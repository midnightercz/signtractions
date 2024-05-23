from typing import Union

from pytractions.base import TList, Arg, Res, TRes, In, TIn, Out, STMDExecutorType
from pytractions.transformations import Flatten
from pytractions.tractor import Tractor

from ..tractions.containers import STMDPopulateContainerDigest, STMDParseContainerImageReference
from ..tractions.signing import SignSignEntries
from ..tractions.signing import STMDSignEntriesFromContainerParts

from ..resources.quay_client import QuayClient
from ..resources.signing_wrapper import MsgSignerWrapper, CosignSignerWrapper

from ..models.signing import SignEntry


class SignContainers(Tractor):
    """Sign container images."""

    r_signer_wrapper_cosign: Res[Union[MsgSignerWrapper, CosignSignerWrapper]] = TRes[
        Union[MsgSignerWrapper, CosignSignerWrapper]
    ]()
    r_dst_quay_client: Res[QuayClient] = TRes[QuayClient]()
    i_container_image_references: In[TList[In[str]]] = TIn[TList[In[str]]]()
    i_task_id: In[int] = In[int](data=1)
    i_signing_keys: In[TList[In[str]]] = TIn[TList[In[str]]]()
    a_pool_size: Arg[int] = Arg[int](a=10)

    t_parse_container_references: STMDParseContainerImageReference = (
        STMDParseContainerImageReference(
            uid="parse_container_references",
            i_container_image_reference=i_container_image_references,
            a_pool_size=a_pool_size,
            a_executor_type=Arg[STMDExecutorType](a=STMDExecutorType.THREAD),
        )
    )
    t_populate_digests: STMDPopulateContainerDigest = STMDPopulateContainerDigest(
        uid="populate_digests",
        r_quay_client=r_dst_quay_client,
        i_container_parts=t_parse_container_references.o_container_parts,
        a_pool_size=a_pool_size,
        a_executor_type=Arg[STMDExecutorType](a=STMDExecutorType.THREAD),
    )
    t_sign_entries_from_push_item: STMDSignEntriesFromContainerParts = (
        STMDSignEntriesFromContainerParts(
            uid="sign_entries_from_container_parts",
            i_container_parts=t_populate_digests.o_container_parts,
            i_signing_key=i_signing_keys,
            a_pool_size=a_pool_size,
            a_executor_type=Arg[STMDExecutorType](a=STMDExecutorType.THREAD),
        )
    )
    t_flatten_sign_entries: Flatten[SignEntry] = Flatten[SignEntry](
        uid="flatten_sign_entries",
        i_complex=t_sign_entries_from_push_item.o_sign_entries,
    )
    t_sign_push_item_after_push: SignSignEntries = SignSignEntries(
        uid="sign_push_item_after_push",
        i_sign_entries=t_flatten_sign_entries.o_flat,
        i_task_id=i_task_id,
        r_signer_wrapper=r_signer_wrapper_cosign,
    )
    o_sign_entries: Out[TList[Out[SignEntry]]] = t_flatten_sign_entries.o_flat

    d_: str = """
    Sign container images provided as input in cosign wrapper with signing keys provided as input.
"""
    d_i_task_id: str = "Task ID to identify signing request."
    d_i_container_image_references: str = "List of container image references to sign."
    d_a_pool_size: str = "Pool size used for STMD tractions"
    d_i_signing_keys: str = "List of signing keys used to sign containers. One key per container."