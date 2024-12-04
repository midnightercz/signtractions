from typing import Union

from pytractions.base import TList, Port, NullPort
from pytractions.executor import ThreadPoolExecutor, LoopExecutor, ProcessPoolExecutor
from pytractions.transformations import ListMultiplier
from pytractions.tractor import Tractor

from ..tractions.snapshot import ParseSnapshot, ContainerImagesFromSnapshot

from ..resources.quay_client import QuayClient
from ..resources.fake_quay_client import FakeQuayClient

from ..resources.signing_wrapper import MsgSignerWrapper, CosignSignerWrapper
from ..resources.fake_signing_wrapper import FakeCosignSignerWrapper

from ..models.signing import SignEntry

from .t_sign_containers import SignContainers


class SignSnapshot(Tractor):
    """Sign release snapshot."""

    r_signer_wrapper_cosign: Port[
        Union[FakeCosignSignerWrapper, MsgSignerWrapper, CosignSignerWrapper]
    ] = NullPort[Union[FakeCosignSignerWrapper, MsgSignerWrapper, CosignSignerWrapper]]()
    r_dst_quay_client: Port[Union[QuayClient, FakeQuayClient]] = NullPort[
        Union[QuayClient, FakeQuayClient]
    ]()
    i_snapshot_str: Port[str] = NullPort[str]()
    i_snapshot_file: Port[str] = NullPort[str]()
    i_signing_key: Port[str] = NullPort[str]()
    i_chunk_size: Port[int] = Port[int](data=10)
    i_task_id: Port[int] = NullPort[int]()
    a_executor: Port[Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor]] = Port[
        Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor]
    ](data=LoopExecutor())

    t_parse_snapshot: ParseSnapshot = ParseSnapshot(
        uid="parse_snapshot",
        i_snapshot_str=i_snapshot_str,
        i_snapshot_file=i_snapshot_file,
    )
    t_container_images_from_snapshot: ContainerImagesFromSnapshot = ContainerImagesFromSnapshot(
        uid="container_images_from_snapshot", i_snapshot_spec=t_parse_snapshot._raw_o_snapshot_spec
    )
    t_populate_signing_keys: ListMultiplier[str, str] = ListMultiplier[str, str](
        uid="populate_signing_keys",
        i_scalar=i_signing_key,
        i_list=t_container_images_from_snapshot._raw_o_container_images,
    )
    t_sign_containers: SignContainers = SignContainers(
        uid="sign_containers",
        r_signer_wrapper_cosign=r_signer_wrapper_cosign,
        r_dst_quay_client=r_dst_quay_client,
        i_container_image_references=t_container_images_from_snapshot._raw_o_container_images,
        i_container_image_identities=t_container_images_from_snapshot._raw_o_container_identities,
        i_signing_keys=t_populate_signing_keys._raw_o_list,
        i_task_id=i_task_id,
        i_chunk_size=i_chunk_size,
        a_executor=a_executor,
    )

    o_sign_entries: Port[TList[SignEntry]] = t_sign_containers._raw_o_sign_entries

    d_: str = """
    Sign containers in release snapshot.
"""
    d_i_task_id: str = "Task ID to identify signing request."
    d_i_snapshot_str: str = "Json representation of release snapshot."
    d_i_snapshot_file: str = "Path to a file containing snapshot in json format."
    d_a_executor: str = "Executor used for parallel processing."
    d_i_signing_key: str = "Signing key used to sign containers. One key per container."
    d_r_signer_wrapper_cosign: str = "Signer wrapper used to sign container images."
    d_r_dst_quay_client: str = (
        "Quay client used for fetching container images when populating " "digests in SignEntries."
    )
    d_t_container_images_from_snapshot: str = "Extract container images from snapshot."
    d_t_populate_signing_keys: str = "Populate signing keys for each container image."
    d_t_sign_containers: str = "Sign containers in release snapshot."
