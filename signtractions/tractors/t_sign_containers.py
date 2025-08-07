from typing import Union

from pytractions.base import TList, NullPort, Port
from pytractions.traction import Traction
from pytractions.transformations import Flatten
from pytractions.tractor import Tractor
from pytractions.executor import LoopExecutor, ThreadPoolExecutor, ProcessPoolExecutor
from pytractions.transformations import Extractor
from pytractions.stmd import STMD

from ..tractions.containers import STMDPopulateContainerDigest, STMDParseContainerImageReference
from ..tractions.signing import STMDSignSignEntries
from ..tractions.signing import STMDSignEntriesFromContainerParts

from ..resources.quay_client import QuayClient
from ..resources import SIGNING_WRAPPERS
from ..resources.fake_quay_client import FakeQuayClient

from ..models.signing import ContainerSignInput, SignEntry


class ChunkSignEntries(Traction):
    """Chunk SignEntries."""

    i_sign_entries: TList[SignEntry]
    i_chunk_size: int
    o_chunked_sign_entries: TList[TList[SignEntry]]

    d_: str = "Chunk provided SignEntries into chunks."
    d_i_sign_entries: str = "List of SignEntry objects to chunk."
    d_i_chunk_size: str = "Size of each chunk."
    d_o_chunked_sign_entries: str = "List of chunked SignEntry objects."

    def _run(self, on_update=None) -> None:
        self.log.info(
            f"Chunking {len(self.i_sign_entries)} "
            f"SignEntries into chunks of size {self.i_chunk_size}."
        )
        for i in range(0, len(self.i_sign_entries), self.i_chunk_size):
            chunk = TList[SignEntry](self.i_sign_entries[i : i + self.i_chunk_size])  # noqa: E203
            self.o_chunked_sign_entries.append(chunk)


STMDExtractContainerSignInput = STMD.wrap(Extractor[ContainerSignInput, str])


class SignContainers(Tractor):
    """Sign container images."""

    r_signer_wrapper: Port[SIGNING_WRAPPERS] = NullPort[SIGNING_WRAPPERS]()
    r_dst_quay_client: Union[QuayClient, FakeQuayClient] = NullPort[
        Union[QuayClient, FakeQuayClient]
    ]()
    i_task_id: Port[int] = Port[int](data=1)
    i_containers_to_sign: Port[TList[ContainerSignInput]] = NullPort[TList[ContainerSignInput]]()

    a_executor: Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor] = ThreadPoolExecutor(
        pool_size=5, executor_type="thread_pool_executor"
    )
    a_sign_executor: Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor] = (
        ThreadPoolExecutor(pool_size=5, executor_type="thread_pool_executor")
    )
    a_dry_run: Port[bool] = Port[bool](data=False)

    t_extract_references: STMDExtractContainerSignInput = STMDExtractContainerSignInput(
        uid="extract_references", i_model=i_containers_to_sign, a_field="reference"
    )
    t_parse_container_references: STMDParseContainerImageReference = (
        STMDParseContainerImageReference(
            uid="parse_container_references",
            i_container_image_reference=t_extract_references._raw_o_model,
            a_executor=a_executor,
        )
    )
    t_populate_digests: STMDPopulateContainerDigest = STMDPopulateContainerDigest(
        uid="populate_digests",
        r_quay_client=r_dst_quay_client,
        i_container_parts=t_parse_container_references._raw_o_container_parts,
        a_executor=a_executor,
    )
    t_extract_identities: STMDExtractContainerSignInput = STMDExtractContainerSignInput(
        uid="extract_identities", i_model=i_containers_to_sign, a_field="identity"
    )
    t_extract_signing_key: STMDExtractContainerSignInput = STMDExtractContainerSignInput(
        uid="extract_signing_keys", i_model=i_containers_to_sign, a_field="signing_key"
    )
    t_make_sign_entries_from_push_item: STMDSignEntriesFromContainerParts = (
        STMDSignEntriesFromContainerParts(
            uid="sign_entries_from_container_parts",
            i_container_parts=t_populate_digests._raw_o_container_parts,
            i_container_identity=t_extract_identities._raw_o_model,
            i_signing_key=t_extract_signing_key._raw_o_model,
            a_executor=a_executor,
        )
    )
    t_flatten_entries: Flatten[SignEntry] = Flatten[SignEntry](
        uid="flatten_entries",
        i_complex=t_make_sign_entries_from_push_item._raw_o_sign_entries,
    )
    i_chunk_size: Port[int] = Port[int](data=1000)

    t_chunk_entries: ChunkSignEntries = ChunkSignEntries(
        uid="chunk_entries",
        i_sign_entries=t_flatten_entries._raw_o_flat,
        i_chunk_size=i_chunk_size,
    )

    t_sign_entries: STMDSignSignEntries = STMDSignSignEntries(
        uid="sign_entries",
        i_sign_entries=t_chunk_entries._raw_o_chunked_sign_entries,
        i_task_id=i_task_id,
        r_signer_wrapper=r_signer_wrapper,
        a_dry_run=a_dry_run,
        a_executor=a_sign_executor,
    )
    o_sign_entries: Port[TList[SignEntry]] = t_flatten_entries._raw_o_flat

    d_: str = """markdown
# Sign container images with selected signer.

This traction takes a list of container sign inputs. Container sign input is
composed object consisting of three fields:

- `reference`:  reference of container to sign, e.i. from where container can be pulled
- `signing_key`: signing key which will be used to sign the container
- `identity`: identity of the container image, e.i. reference which will be stored in the signature.

Signing consists of these steps:

- Convert containers to signing entries.
  This includes populating manifests digests for given references. For that `r_dst_quay_client`
  is used. This steps also runs in parallel using `a_executor`.
- Split populated signing entries into chunks. This is important for next step as
  if anything happens during signing process, provided references could be at least partially
  signed (before the error)
- Filter already signed references. This stes prevents sending containers which were
  already signed to be signed again. Therefore chunked input (step before) can be partially
  signed and in next run process will sign only unsigned containers.
- Sign filtered references
- Store signatures to sigstore

"""
    d_i_task_id: str = "Task ID to identify signing request."
    d_i_containers_to_sign: str = "List of ContainerSignInput models to sign."
    d_a_executor: str = "Executor used for parallel processing."
    d_i_chunk_size: str = (
        "Size of each chunk used to split sign entries to chunks for parallel signing."
    )
    d_o_sign_entries: str = "List of SignEntry objects signed."
    d_r_signer_wrapper: str = "Signer wrapper used to sign container images with cosign."
    d_a_dry_run: str = "Dry run flag to simulate signing without actual signing."
