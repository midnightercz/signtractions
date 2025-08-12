from typing import Union, Optional
import os

from pytractions.base import TList, Port, NullPort
from pytractions.traction import Traction, TractionFailedError
from pytractions.stmd import STMD
from pytractions.executor import ThreadPoolExecutor, LoopExecutor, ProcessPoolExecutor
from pytractions.transformations import ListMultiplier, Flatten
from pytractions.tractor import Tractor

from ..tractions.containers import STMDGetContainerImageTags

from ..resources.quay_client import QuayClient
from ..resources.fake_quay_client import FakeQuayClient
from signtractions.resources.cosign import CosignClient, FakeCosignClient

from ..resources import SIGNING_WRAPPERS

from ..models.signing import SignEntry, ContainerSignInput

from .t_sign_containers import SignContainers


class DecideRepos(Traction):
    """Decide source of the repositories to sign."""

    i_container_image_repos: Port[TList[str]]
    i_container_image_repo_file: Port[Optional[str]]
    o_container_image_repos: Port[TList[str]]

    def _run(self, on_update=None) -> None:
        if self.i_container_image_repo_file and os.path.exists(self.i_container_image_repo_file):
            with open(self.i_container_image_repo_file, "r") as f:
                self.o_container_image_repos = TList[str](f.read().splitlines())
        elif self.i_container_image_repos is not None:
            self.o_container_image_repos = self.i_container_image_repos
        else:
            self.log.error("No container image repos provided.")
            raise TractionFailedError("No container image repos provided.")


class MakeContainerSignInput(Traction):
    """Create a ContainerSignInput from provided parameters."""

    i_signing_key: Port[str]
    i_container_image_reference: Port[str]
    i_container_image_identity: Port[str]
    o_container_sign_input: Port[ContainerSignInput]

    def _run(self):
        self.o_container_sign_input = ContainerSignInput(
            reference=self.i_container_image_reference,
            identity=self.i_container_image_identity,
            signing_key=self.i_signing_key,
        )


STMDMakeContainerSignInputs = STMD.wrap(MakeContainerSignInput)


class SignRepos(Tractor):
    """Sign a repository."""

    r_signer_wrapper: Port[SIGNING_WRAPPERS] = NullPort[SIGNING_WRAPPERS]()
    r_dst_quay_client: Port[Union[QuayClient, FakeQuayClient]] = NullPort[
        Union[QuayClient, FakeQuayClient]
    ]()
    r_cosign_client: Port[Union[CosignClient, FakeCosignClient]] = NullPort[
        Union[CosignClient, FakeCosignClient]
    ]()

    i_container_image_repos: Port[TList[str]] = NullPort[TList[str]]()
    i_container_image_repos_file: Port[Optional[str]] = NullPort[Optional[str]]()
    i_container_image_repo_identities: Port[TList[str]] = NullPort[TList[str]]()
    i_signing_key: Port[str] = NullPort[str]()
    i_task_id: Port[int] = NullPort[int]()
    a_executor_2: Port[Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor]] = Port[
        Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor]
    ](data=ThreadPoolExecutor(pool_size=5, executor_type="thread_pool_executor"))
    a_sign_executor: Port[Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor]] = Port[
        Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor]
    ](data=ThreadPoolExecutor(pool_size=5, executor_type="thread_pool_executor"))
    a_dry_run: Port[bool] = Port[bool](data=False)

    t_decide_repos: DecideRepos = DecideRepos(
        uid="decide_repos",
        i_container_image_repos=i_container_image_repos,
        i_container_image_repo_file=i_container_image_repos_file,
    )

    t_get_container_image_tags: STMDGetContainerImageTags = STMDGetContainerImageTags(
        uid="get_container_image_tags",
        r_quay_client=r_dst_quay_client,
        i_container_image_repo=t_decide_repos.o_container_image_repos,
        i_container_image_repo_identities=i_container_image_repo_identities,
        a_executor=a_executor_2,
    )

    t_flatten_container_references: Flatten[str] = Flatten[str](
        uid="flatten_container_references",
        i_complex=t_get_container_image_tags.o_container_references,
    )

    t_flatten_container_image_identities: Flatten[str] = Flatten[str](
        uid="flatten_container_identities",
        i_complex=t_get_container_image_tags.o_container_identities,
    )

    t_populate_signing_keys: ListMultiplier[str, str] = ListMultiplier[str, str](
        uid="populate_signing_keys",
        i_scalar=i_signing_key,
        i_list=t_flatten_container_references.o_flat,
    )
    t_make_container_sign_inputs: STMDMakeContainerSignInputs = STMDMakeContainerSignInputs(
        uid="make_container_sign_inputs",
        i_container_image_reference=t_flatten_container_references.o_flat,
        i_container_image_identity=t_flatten_container_image_identities.o_flat,
        i_signing_key=t_populate_signing_keys.o_list,
    )

    i_chunk_size: Port[int] = Port[int](data=50)
    t_sign_containers: SignContainers = SignContainers(
        uid="sign_containers",
        r_signer_wrapper=r_signer_wrapper,
        r_dst_quay_client=r_dst_quay_client,
        i_containers_to_sign=t_make_container_sign_inputs.o_container_sign_input,
        i_task_id=i_task_id,
        a_executor=a_executor_2,
        a_sign_executor=a_sign_executor,
        a_dry_run=a_dry_run,
        i_chunk_size=i_chunk_size,
    )
    o_sign_entries: Port[TList[SignEntry]] = t_sign_containers.o_sign_entries

    d_: str = """
    # Sign all tags and digets for given repositories.

This traction takes list of repositories (provided explicitly as list or as
file with one repository per line). Repositories are expected to be in form
of <registry>/<repository>


"""
    d_i_task_id: str = "Task ID to identify signing request. Must be number"
    d_i_signing_key: str = "Signing key used to sign containers"
    d_i_chunk_size: str = (
        "Size of each chunk used to split sign entries to chunks for parallel signing."
    )
    d_i_container_image_repos: str = "List of repositories to sign"
    d_i_container_image_repos_file: str = (
        "List of repositories to sign stored in a file. One repo per line"
    )
    d_i_container_image_repo_identities: str = (
        "List of indentities used for signing containers."
        + " Use only base hosts, e.g. `registry.redhat.io`,"
        + "full identities are constructed in to process."
    )

    d_r_signer_wrapper: str = "Signer wrapper used to sign container images."
    d_a_sign_executor: str = "Executor used for signing."
    d_a_executor_2: str = "Executor used for parallel preprocessing of the input."
    d_a_dry_run: str = "Dry run flag to simulate signing without actual signing."
    d_r_dst_quay_client: str = (
        "Quay client used for fetching container images when populating digests in SignEntries."
    )
