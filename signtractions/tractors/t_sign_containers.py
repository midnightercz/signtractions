from typing import Union

from pytractions.base import TList, NullPort, Port, Traction
from pytractions.transformations import Flatten
from pytractions.tractor import Tractor
from pytractions.executor import LoopExecutor, ThreadPoolExecutor, ProcessPoolExecutor

from ..tractions.containers import STMDPopulateContainerDigest, STMDParseContainerImageReference
from ..tractions.signing import STMDSignSignEntries
from ..tractions.signing import STMDSignEntriesFromContainerParts

from ..resources.quay_client import QuayClient
from ..resources.signing_wrapper import MsgSignerWrapper, CosignSignerWrapper
from ..resources.fake_signing_wrapper import FakeCosignSignerWrapper
from ..resources.fake_quay_client import FakeQuayClient

from ..models.signing import SignEntry


class ChunkSignEntries(Traction):
    """Chunk SignEntries."""

    i_sign_entries: TList[SignEntry]
    i_chunk_size: int
    o_chunked_sign_entries: TList[TList[SignEntry]]

    d_: str = "Chunk provided SignEntries into chunks."
    d_i_sign_entries: str = "List of SignEntry objects to chunk."
    d_i_chunk_size: str = "Size of each chunk."

    def _run(self, on_update=None) -> None:
        for i in range(0, len(self.i_sign_entries), self.i_chunk_size):
            chunk = TList[SignEntry](self.i_sign_entries[i : i + self.i_chunk_size])  # noqa: E203
            self.o_chunked_sign_entries.append(chunk)

        # self.o_chunked_sign_entries = TList[TList[SignEntry]](
        #     [
        #         TList[SignEntry](chunk)
        #         for i in range(0, len(self.i_sign_entries), self.i_chunk_size)
        #     ]
        # )


class SignContainers(Tractor):
    """Sign container images."""

    r_signer_wrapper_cosign: Port[
        Union[FakeCosignSignerWrapper, MsgSignerWrapper, CosignSignerWrapper]
    ] = NullPort[Union[FakeCosignSignerWrapper, MsgSignerWrapper, CosignSignerWrapper]]()
    r_dst_quay_client: Union[QuayClient, FakeQuayClient] = NullPort[
        Union[QuayClient, FakeQuayClient]
    ]()
    i_container_image_references: Port[TList[str]] = Port[TList[str]]()
    i_container_image_identities: Port[TList[str]] = Port[TList[str]]()
    i_task_id: Port[int] = Port[int](data=1)
    i_signing_keys: Port[TList[str]] = Port[TList[str]]([])
    a_executor: Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor] = ThreadPoolExecutor(
        pool_size=5
    )
    a_dry_run: bool = False

    t_parse_container_references: STMDParseContainerImageReference = (
        STMDParseContainerImageReference(
            uid="parse_container_references",
            i_container_image_reference=i_container_image_references,
            a_executor=a_executor,
        )
    )
    t_populate_digests: STMDPopulateContainerDigest = STMDPopulateContainerDigest(
        uid="populate_digests",
        r_quay_client=r_dst_quay_client,
        i_container_parts=t_parse_container_references._raw_o_container_parts,
        a_executor=a_executor,
    )
    t_sign_entries_from_push_item: STMDSignEntriesFromContainerParts = (
        STMDSignEntriesFromContainerParts(
            uid="sign_entries_from_container_parts",
            i_container_parts=t_populate_digests._raw_o_container_parts,
            i_container_identity=i_container_image_identities,
            i_signing_key=i_signing_keys,
            a_executor=a_executor,
        )
    )
    t_flatten_sign_entries: Flatten[SignEntry] = Flatten[SignEntry](
        uid="flatten_sign_entries",
        i_complex=t_sign_entries_from_push_item._raw_o_sign_entries,
    )
    i_chunk_size: Port[int] = Port[int](data=10)

    t_chunk_sign_entries: ChunkSignEntries = ChunkSignEntries(
        uid="chunk_sign_entries",
        i_sign_entries=t_flatten_sign_entries._raw_o_flat,
        i_chunk_size=i_chunk_size,
    )

    t_sign_push_item_after_push: STMDSignSignEntries = STMDSignSignEntries(
        uid="sign_push_item_after_push",
        i_sign_entries=t_chunk_sign_entries._raw_o_chunked_sign_entries,
        i_task_id=i_task_id,
        r_signer_wrapper=r_signer_wrapper_cosign,
        a_dry_run=a_dry_run,
        a_executor=a_executor,
    )
    o_sign_entries: Port[TList[SignEntry]] = t_flatten_sign_entries._raw_o_flat

    d_: str = """
    Sign container images provided as input in cosign wrapper with signing keys provided as input.
"""
    d_i_task_id: str = "Task ID to identify signing request."
    d_i_container_image_references: str = "List of container image references to sign."
    d_i_container_image_identities: str = "List of container image identities."
    d_i_signing_keys: str = "List of signing keys used to sign containers. One key per container."
    d_a_executor: str = "Executor used for parallel processing."
