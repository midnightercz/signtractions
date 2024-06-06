from typing import Union

from pytractions.base import TList, Arg, Res, TRes, In, TIn, Out, STMDExecutorType
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

    r_signer_wrapper_cosign: Res[
        Union[FakeCosignSignerWrapper, MsgSignerWrapper, CosignSignerWrapper]
    ] = TRes[Union[FakeCosignSignerWrapper, MsgSignerWrapper, CosignSignerWrapper]]()
    r_dst_quay_client: Res[Union[QuayClient, FakeQuayClient]] = TRes[
        Union[QuayClient, FakeQuayClient]
    ]()
    i_snapshot_str: In[str] = TIn[str]()
    i_snapshot_file: In[str] = TIn[str]()
    i_signing_key: In[str] = TIn[str]()
    i_task_id: In[int] = TIn[int]()
    a_pool_size: Arg[int] = Arg[int](a=10)
    a_executor_type: Arg[STMDExecutorType] = Arg[STMDExecutorType](a=STMDExecutorType.THREAD)

    t_parse_snapshot: ParseSnapshot = ParseSnapshot(
        uid="parse_snapshot",
        i_snapshot_str=i_snapshot_str,
        i_snapshot_file=i_snapshot_file,
    )
    t_container_images_from_snapshot: ContainerImagesFromSnapshot = ContainerImagesFromSnapshot(
        uid="container_images_from_snapshot", i_snapshot=t_parse_snapshot.o_snapshot
    )
    t_populate_signing_keys: ListMultiplier[str, str] = ListMultiplier[str, str](
        uid="populate_signing_keys",
        i_scalar=i_signing_key,
        i_list=t_container_images_from_snapshot.o_container_images,
    )
    t_sign_containers: SignContainers = SignContainers(
        uid="sign_containers",
        r_signer_wrapper_cosign=r_signer_wrapper_cosign,
        r_dst_quay_client=r_dst_quay_client,
        i_container_image_references=t_container_images_from_snapshot.o_container_images,
        i_signing_keys=t_populate_signing_keys.o_list,
        i_task_id=i_task_id,
        a_pool_size=Arg[int](a=10),
        a_executor_type=a_executor_type,
    )

    o_sign_entries: Out[TList[SignEntry]] = t_sign_containers.o_sign_entries

    d_: str = """
    Sign containers in release snapshot.
"""
    d_i_task_id: str = "Task ID to identify signing request."
    d_i_snapshot_str: str = "Json representation of release snapshot."
    d_i_snapshot_file: str = "Path to a file containing snapshot in json format."
    d_a_pool_size: str = "Pool size used for STMD tractions"
    d_i_signing_key: str = "Signing key used to sign containers. One key per container."
