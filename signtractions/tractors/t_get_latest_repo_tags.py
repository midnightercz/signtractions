from typing import Union, Optional

from pytractions.base import TList, NullPort, Port, Traction
from pytractions.stmd import STMD

from pytractions.tractor import Tractor
from pytractions.executor import LoopExecutor, ThreadPoolExecutor, ProcessPoolExecutor

from ..tractions.quay import GetQuayRepositories, STMDGetQuayTags


from ..resources.quay_client import QuayClient
from ..resources.fake_quay_client import FakeQuayClient

from ..models.quay import QuayTag


class FilterTags(Traction):
    """Filter tags."""

    i_tags: TList[QuayTag]
    i_repository: str
    o_filtered_tags: TList[QuayTag]
    a_skip_sigs: bool = True
    a_not_after: Optional[str] = None
    a_not_before: Optional[str] = None

    def _run(self, on_update=None) -> None:
        print(f"Processing {len(self.i_tags)} tags")
        for tag in self.i_tags:
            if self.a_skip_sigs and (
                tag.name.endswith(".sig") or tag.name.endswith(".att") or tag.name.endswith(".sbom")
            ):
                continue
            if self.a_not_after and tag.last_modified > self.a_not_after:
                continue
            if self.a_not_before and tag.last_modified < self.a_not_before:
                continue
            self.o_filtered_tags.append(tag)
        print(f"Filtered to {len(self.i_tags)} tags")


STMDFilterTags = STMD.wrap(FilterTags)


class PrintOutput(Traction):
    """Print output."""

    i_tags: TList[TList[QuayTag]]
    i_repositories: TList[str]
    o_repo_tags: TList[str]

    def _run(self, on_update=None) -> None:
        for repo, tags in zip(self.i_repositories, self.i_tags):
            for tag in tags:
                print(f"{repo}:{tag.name}")
                self.o_repo_tags.append(f"{repo}:{tag.name}")
        print(f"Total tags {len(self.o_repo_tags)}")


STMDPrintOutput = STMD.wrap(PrintOutput)


class GetLastRepoTags(Tractor):
    """Sign container images."""

    i_namespace: Port[str] = Port[str](data="")
    r_dst_quay_client: Union[QuayClient, FakeQuayClient] = NullPort[
        Union[QuayClient, FakeQuayClient]
    ]()
    a_executor: Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor] = ThreadPoolExecutor(
        pool_size=5
    )
    a_not_after: Port[Optional[str]] = Port[Optional[str]](data="")
    a_not_before: Port[Optional[str]] = Port[Optional[str]](data="")

    t_get_repositories: GetQuayRepositories = GetQuayRepositories(
        uid="get_repositories",
        i_namespace=i_namespace,
        r_quay_client=r_dst_quay_client,
    )
    t_get_tags: STMDGetQuayTags = STMDGetQuayTags(
        uid="get_tags",
        r_quay_client=r_dst_quay_client,
        i_repository=t_get_repositories.o_repositories,
        a_executor=a_executor,
    )
    t_filter_tags: STMDFilterTags = STMDFilterTags(
        uid="filter_tags",
        i_tags=t_get_tags.o_tags,
        i_repository=t_get_repositories.o_repositories,
        a_not_after=a_not_after,
        a_not_before=a_not_before,
        a_skip_sigs=True,
    )
    t_print_output: PrintOutput = PrintOutput(
        uid="print_output",
        i_tags=t_get_tags.o_tags,
        i_repositories=t_get_repositories.o_repositories,
    )

    o_repo_tags: Port[TList[str]] = t_print_output.o_repo_tags
