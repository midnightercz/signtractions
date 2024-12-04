import logging
from typing import Type, Union

from pytractions.base import (
    Traction,
    OnUpdateCallable,
    TList,
)
from pytractions.stmd import STMD, STMDSingleIn

from ..resources.signing_wrapper import SignerWrapper
from ..resources.cosign import CosignClient, FakeCosignClient
from ..models.signing import SignEntry
from ..models.containers import ContainerParts

LOG = logging.getLogger()
logging.basicConfig()
LOG.setLevel(logging.INFO)


class SignSignEntries(Traction):
    """Sign SignEntries."""

    r_signer_wrapper: SignerWrapper
    i_task_id: int
    i_sign_entries: TList[SignEntry]
    a_dry_run: bool = False

    d_: str = "Sign provided SignEntries with signer wrapper."
    d_i_sign_entries: str = "List of SignEntry objects to sign."
    d_i_task_id: str = "Task id used to identify signing requests."

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        if not self.a_dry_run:
            self.r_signer_wrapper.sign_containers(
                [x for x in self.i_sign_entries],
                task_id=self.i_task_id,
            )
        else:
            for x in self.i_sign_entries:
                LOG.info(f"[DRY] Signing {x}")


class STMDSignSignEntries(STMD):
    """Sign SignEntries.

    STMD version
    """

    _traction: Type[Traction] = SignSignEntries
    r_signer_wrapper: SignerWrapper
    i_task_id: STMDSingleIn[int]
    i_sign_entries: TList[TList[SignEntry]]
    a_dry_run: bool = False

    d_: str = "Sign provided SignEntries with signer wrapper. STMD version."
    d_i_sign_entries: str = "List of List of SignEntry objects to sign."
    d_i_task_id: str = "Task id used to identify signing requests."


class SignEntriesFromContainerParts(Traction):
    """Create sign entries from container parts."""

    i_container_parts: ContainerParts
    i_container_identity: str
    i_signing_key: str
    o_sign_entries: TList[SignEntry]

    d_: str = """Create sign entries from container parts.
    For each pair of digest and arch in container parts, create a SignEntry object.
    """
    d_i_signing_key: str = "Signing key to use for signing."
    d_i_container_parts: str = "Container parts to create sign entries from."
    d_o_sign_entries: str = "List of SignEntry objects"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        for digest, arch in zip(self.i_container_parts.digests, self.i_container_parts.arches):
            self.o_sign_entries.append(
                SignEntry(
                    digest=digest,
                    arch=arch,
                    reference=(
                        self.i_container_parts.make_reference()
                        if self.i_container_parts.tag
                        else None
                    ),
                    repo=self.i_container_parts.image,
                    signing_key=self.i_signing_key,
                    identity=self.i_container_identity,
                )
            )


class STMDSignEntriesFromContainerParts(STMD):
    """Create sign entries from container parts.

    STMD version
    """

    _traction: Type[Traction] = SignEntriesFromContainerParts
    i_signing_key: TList[str]
    i_container_parts: TList[ContainerParts]
    i_container_identity: TList[str]
    o_sign_entries: TList[TList[SignEntry]]

    d_: str = """Create sign entries from container parts.
    For each pair of digest and arch in container parts, create a SignEntry object.
    STMD version
    """
    d_i_signing_key: str = "List of signing key to use for signing."
    d_i_container_parts: str = "List of container parts to create sign entries from."
    d_o_sign_entries: str = "List of List of SignEntry objects"


class VerifyEntries(Traction):
    """Sign SignEntries."""

    i_sign_entries: TList[SignEntry]
    i_public_key_file: str
    r_cosign_client: Union[CosignClient, FakeCosignClient]

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        deduplicated_sign_entries = []
        references = []
        for entry in self.i_sign_entries:
            if entry.reference not in references:
                references.append(entry.reference)
                deduplicated_sign_entries.append(entry)

        for entry in deduplicated_sign_entries:
            print(
                "verifying",
                entry.reference,
                ["cosign", "verify", "--key", self.i_public_key_file, entry.reference],
            )
            self.r_cosign_client.verify(entry.reference, self.i_public_key_file)
