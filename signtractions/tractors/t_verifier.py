import datetime
from typing import Union, Optional

from pytractions.base import TList, NullPort, Port, Traction, TDict
from pytractions.stmd import STMD
from pytractions.transformations import Flatten

from pytractions.stmd import ThreadPoolExecutor
from pytractions.tractor import Tractor
from pytractions.executor import LoopExecutor, ThreadPoolExecutor, ProcessPoolExecutor

from ..tractions.quay import GetQuayRepositories, STMDGetQuayTags
from ..tractions.containers import STMDPopulateContainerDigest, STMDParseContainerImageReference
from ..tractions.signing import STMDSignEntriesFromContainerParts
from ..tractions.verify import VerifyEntriesCosign, VerifyEntriesLegacy

from ..resources.quay_client import QuayClient
from ..resources.signing_wrapper import MsgSignerWrapper, CosignSignerWrapper
from ..resources.fake_signing_wrapper import FakeCosignSignerWrapper
from ..resources.fake_quay_client import FakeQuayClient
from ..resources.sigstore import Sigstore
from ..resources.gsheets import GSheets

from ..models.signing import SignEntry
from ..models.quay import QuayTag


class Evaluate(Traction):
    """Evaluate entries."""
    i_sign_entries: TList[SignEntry]
    i_found_signatures_legacy: TDict[SignEntry, bool]
    i_found_signatures_cosign: TDict[SignEntry, bool]
    r_gsheets: Port[GSheets]

    def _run(self, on_update=None) -> None:
        date = datetime.datetime.utcnow().isoformat()
        groupped_entries = {}

        for entry in sorted(self.i_sign_entries, key=lambda x: x.identity):
            groupped_entries.setdefault(entry.identity, []).append(entry)

        values = [date]
        i = 1
        for identity, entries in groupped_entries.items():
            found_legacy = False
            found_cosign = False
            for entry in entries:
                if entry in self.i_found_signatures_legacy and not found_legacy:
                    found_legacy = i if self.i_found_signatures_legacy[entry] else -i
                if entry in self.i_found_signatures_cosign and not found_cosign:
                    found_cosign = i if self.i_found_signatures_cosign[entry] else -i
            values.append(found_legacy)
            values.append(found_cosign)

            i += 1

        self.r_gsheets.append_values(
            "Data!A3",
            values
        )

class Verifier(Tractor):
    """Sign container images."""

    r_signer_wrapper_cosign: Port[
        Union[FakeCosignSignerWrapper, MsgSignerWrapper, CosignSignerWrapper]
    ] = NullPort[Union[FakeCosignSignerWrapper, MsgSignerWrapper, CosignSignerWrapper]]()
    r_dst_quay_client: Union[QuayClient, FakeQuayClient] = NullPort[Union[QuayClient, FakeQuayClient]]()
    r_sigstore: Port[Sigstore] = NullPort[Sigstore]()
    r_gsheets: Port[GSheets] = NullPort[GSheets]()

    i_container_image_references: Port[TList[str]] = Port[TList[str]]()
    i_container_image_identities: Port[TList[str]] = Port[TList[str]]()
    i_public_key_file: Port[str] = NullPort[str]()
    i_signing_keys: Port[TList[str]] = NullPort[TList[str]]()

    a_executor: Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor] = ThreadPoolExecutor(pool_size=1)
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
    t_make_sign_entries: STMDSignEntriesFromContainerParts = (
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
        i_complex=t_make_sign_entries._raw_o_sign_entries,
    )
    t_verify_entries_cosign: VerifyEntriesCosign = VerifyEntriesCosign(
        uid="verify_entries_cosign",
        i_sign_entries=t_flatten_sign_entries._raw_o_flat,
        i_public_key_file=i_public_key_file,
        r_dst_quay_client=r_dst_quay_client
    )
    t_verify_entries_legacy: VerifyEntriesLegacy = VerifyEntriesLegacy(
        uid="verify_entries_legacy",
        i_sign_entries=t_flatten_sign_entries._raw_o_flat,
        r_sigstore=r_sigstore
    )
    t_evaluate: Evaluate = Evaluate(
        uid="evaluate_entries",
        i_sign_entries=t_flatten_sign_entries._raw_o_flat,
        i_found_signatures_legacy=t_verify_entries_legacy._raw_o_verified,
        i_found_signatures_cosign=t_verify_entries_cosign._raw_o_verified,
        r_gsheets=r_gsheets
    )

