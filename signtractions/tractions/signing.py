from typing import Type

from pytractions.base import (
    Traction,
    STMD,
    In,
    Out,
    Res,
    OnUpdateCallable,
    TList,
    STMDSingleIn,
)
from ..resources.signing_wrapper import SignerWrapper
from ..models.signing import SignEntry
from ..models.containers import ContainerParts


class SignSignEntries(Traction):
    """Sign SignEntries."""

    r_signer_wrapper: Res[SignerWrapper]
    i_task_id: In[int]
    i_sign_entries: In[TList[In[SignEntry]]]

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        self.r_signer_wrapper.r.sign_containers(
            [x.data for x in self.i_sign_entries.data],
            task_id=self.i_task_id.data,
        )


class STMDSignSignEntries(STMD):
    """Sign SignEntries.

    STMD version
    """

    _traction: Type[Traction] = SignSignEntries
    r_signer_wrapper: Res[SignerWrapper]
    i_task_id: STMDSingleIn[int]
    i_sign_entries: In[TList[In[TList[In[SignEntry]]]]]


class SignEntriesFromContainerParts(Traction):
    """Create sign entries from container parts."""

    i_container_parts: In[ContainerParts]
    i_signing_key: In[str]
    o_sign_entries: Out[TList[Out[SignEntry]]]

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        for digest, arch in zip(
            self.i_container_parts.data.digests, self.i_container_parts.data.arches
        ):
            self.o_sign_entries.data.append(
                Out[SignEntry](
                    data=SignEntry(
                        digest=digest,
                        arch=arch,
                        reference=(
                            self.i_container_parts.data.make_reference()
                            if self.i_container_parts.data.tag
                            else None
                        ),
                        repo=self.i_container_parts.data.image,
                        signing_key=self.i_signing_key.data,
                    )
                )
            )


class STMDSignEntriesFromContainerParts(STMD):
    """Create sign entries from container parts.

    STMD version
    """

    _traction: Type[Traction] = SignEntriesFromContainerParts
    i_signing_key: In[TList[In[str]]]
    i_container_parts: In[TList[In[ContainerParts]]]
    o_sign_entries: Out[TList[Out[TList[Out[SignEntry]]]]]
