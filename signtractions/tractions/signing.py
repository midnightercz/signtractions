from typing import Type, Union
import json

from pytractions.base import TList, NullPort, Port, STMDSingleIn
from pytractions.traction import Traction
from pytractions.tractor import Tractor

from pytractions.stmd import STMD

from ..resources import SIGNING_WRAPPERS
from ..resources.cosign import CosignClient, FakeCosignClient
from ..models.signing import SignEntry
from ..models.containers import ContainerParts


class FilterToSignEntries(Traction):
    """Filter SignEntries."""

    r_signer_wrapper: Port[SIGNING_WRAPPERS]

    i_sign_entries: TList[SignEntry]
    o_sign_entries: TList[SignEntry]

    d_: str = "Remove SignEntries that already exists in the sigstore."
    d_i_sign_entries: str = "List of SignEntry objects to filter."
    d_o_sign_entries: str = "List of filtered SignEntry objects."

    def _run(self) -> None:
        # self.o_sign_entries = self.i_sign_entries
        filtered_sign_entries = self.r_signer_wrapper._filter_to_sign(self.i_sign_entries)
        for entry in filtered_sign_entries:
            self.o_sign_entries.append(entry)


class SignEntries(Traction):
    """Sign entries."""

    i_sign_entries: TList[SignEntry]
    i_task_id: int
    r_signer_wrapper: Port[SIGNING_WRAPPERS]
    o_signed: str
    a_dry_run: Port[bool] = Port[bool](data=False)

    def _run(self):
        if not self.a_dry_run:
            self.log.info(f"Signing {len(self.i_sign_entries)} entries")
            signed = self.r_signer_wrapper._sign_entries(self.i_sign_entries, self.i_task_id)
            self.o_signed = json.dumps(signed)
        else:
            self.log.info(f"[DRY RUN] Signing {len(self.i_sign_entries)} entries")
            self.o_signed = "{}"


class StoreSigned(Traction):
    """Store signed entries to sigstore."""

    i_signed: str
    r_signer_wrapper: Port[SIGNING_WRAPPERS]
    a_dry_run: bool = False

    def _run(self):
        if not self.a_dry_run:
            try:
                self.r_signer_wrapper._store_signed(json.loads(self.i_signed))
            except Exception:
                self.log.error("Exception when storing signatures:", exc_info=True)
                raise
        else:
            self.log.info(f"DRY RUN: {self.uid}")


class SignSignEntries(Tractor):
    """Sign SignEntries."""

    r_signer_wrapper: Port[SIGNING_WRAPPERS] = NullPort[SIGNING_WRAPPERS]()
    i_task_id: int = NullPort[int]()
    i_sign_entries: Port[TList[SignEntry]] = NullPort[TList[SignEntry]]()
    a_dry_run: Port[bool] = Port[bool](data=False)

    t_filter_to_sign: FilterToSignEntries = FilterToSignEntries(
        uid="filter_to_sign",
        r_signer_wrapper=r_signer_wrapper,
        i_sign_entries=i_sign_entries,
    )
    t_sign_entries: SignEntries = SignEntries(
        uid="sign_entries",
        i_sign_entries=t_filter_to_sign.o_sign_entries,
        i_task_id=i_task_id,
        r_signer_wrapper=r_signer_wrapper,
        a_dry_run=a_dry_run,
    )
    t_store_signed: StoreSigned = StoreSigned(
        uid="store_signed",
        i_signed=t_sign_entries.o_signed,
        r_signer_wrapper=r_signer_wrapper,
    )

    d_: str = "Sign provided SignEntries with signer wrapper."
    d_i_sign_entries: str = "List of SignEntry objects to sign."
    d_i_task_id: str = "Task id used to identify signing requests."


class STMDSignSignEntries(STMD):
    """Sign SignEntries.

    STMD version
    """

    _traction: Type[Traction] = SignSignEntries
    r_signer_wrapper: Port[SIGNING_WRAPPERS]
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

    def _run(self) -> None:
        for digest, arch in zip(self.i_container_parts.digests, self.i_container_parts.arches):
            # print("Sign entry", self.i_container_parts.make_reference(), digest, arch)
            if arch == "multiarch":
                continue
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

    def _run(self) -> None:
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
