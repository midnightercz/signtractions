import datetime
from typing import Union, Optional

from pytractions.base import TList, NullPort, Port, TDict
from pytractions.traction import Traction
from pytractions.transformations import Flatten, ListMultiplier

from pytractions.tractor import Tractor
from pytractions.executor import LoopExecutor, ThreadPoolExecutor, ProcessPoolExecutor

from ..tractions.containers import (
    STMDPopulateContainerDigest,
    STMDParseContainerImageReference,
    STMDGetContainerImageTags,
)
from ..tractions.signing import STMDSignEntriesFromContainerParts
from ..tractions.verify import VerifyEntriesCosign, VerifyEntriesLegacy, STMDVerifyEntryCosign

from ..tractors.t_sign_repos import DecideRepos

from ..resources.quay_client import QuayClient
from ..resources.signing_wrapper import MsgSignerWrapper, CosignSignerWrapper
from ..resources.fake_signing_wrapper import FakeCosignSignerWrapper
from ..resources.fake_quay_client import FakeQuayClient
from ..resources.sigstore import Sigstore
from ..resources.fake_sigstore import FakeSigstore
from ..resources.gsheets import GSheets
from ..resources.fake_gsheets import FakeGSheets

from ..models.signing import SignEntry


class Evaluate(Traction):
    """Evaluate entries."""

    i_sign_entries: TList[SignEntry]
    i_found_signatures_legacy: TDict[SignEntry, bool]
    i_found_signatures_cosign: TDict[SignEntry, bool]
    r_gsheets: Port[GSheets]

    d_: str = """Evaluate availability of found signatures.
Results are stored in Google Sheets where each column represent a container image
identity and sigstore (cosign or legacy) and ever row represent a timestamp of the evaluation.
Values of each availability cells are either positive integers (found)
or negative integers (not found).


"""
    d_i_sign_entries: str = "Sign entries which ever verified."
    d_i_found_signatures_legacy: str = "Signatures found in legacy sigstore."
    d_i_found_signatures_cosign: str = "Signatures found in cosign."
    d_r_gsheets: str = "Google Sheets resource."

    def _run(self) -> None:
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

        self.r_gsheets.append_values("Data!A3", values)


class Verifier(Tractor):
    """Sign container images."""

    r_signer_wrapper_cosign: Port[
        Union[FakeCosignSignerWrapper, MsgSignerWrapper, CosignSignerWrapper]
    ] = NullPort[Union[FakeCosignSignerWrapper, MsgSignerWrapper, CosignSignerWrapper]]()
    r_dst_quay_client: Union[QuayClient, FakeQuayClient] = NullPort[
        Union[QuayClient, FakeQuayClient]
    ]()
    r_sigstore: Port[Union[Sigstore, FakeSigstore]] = NullPort[Union[Sigstore, FakeSigstore]]()
    r_gsheets: Port[Union[GSheets, FakeGSheets]] = NullPort[Union[GSheets, FakeGSheets]]()

    i_container_image_references: Port[TList[str]] = Port[TList[str]]()
    i_container_image_identities: Port[TList[str]] = Port[TList[str]]()
    i_public_key_file: Port[str] = NullPort[str]()
    i_rekor_public_key_file: Port[str] = NullPort[str]()
    i_signing_keys: Port[TList[str]] = NullPort[TList[str]]()

    a_executor: Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor] = ThreadPoolExecutor(
        pool_size=1, executor_type="thread_pool_executor"
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
    t_make_sign_entries: STMDSignEntriesFromContainerParts = STMDSignEntriesFromContainerParts(
        uid="sign_entries_from_container_parts",
        i_container_parts=t_populate_digests._raw_o_container_parts,
        i_container_identity=i_container_image_identities,
        i_signing_key=i_signing_keys,
        a_executor=a_executor,
    )
    t_flatten_sign_entries: Flatten[SignEntry] = Flatten[SignEntry](
        uid="flatten_sign_entries",
        i_complex=t_make_sign_entries._raw_o_sign_entries,
    )
    t_verify_entries_cosign: VerifyEntriesCosign = VerifyEntriesCosign(
        uid="verify_entries_cosign",
        i_sign_entries=t_flatten_sign_entries._raw_o_flat,
        i_rekor_public_key_file=i_rekor_public_key_file,
        i_public_key_file=i_public_key_file,
    )
    t_verify_entries_legacy: VerifyEntriesLegacy = VerifyEntriesLegacy(
        uid="verify_entries_legacy",
        i_sign_entries=t_flatten_sign_entries._raw_o_flat,
        r_sigstore=r_sigstore,
    )
    t_evaluate: Evaluate = Evaluate(
        uid="evaluate_entries",
        i_sign_entries=t_flatten_sign_entries._raw_o_flat,
        i_found_signatures_legacy=t_verify_entries_legacy._raw_o_verified,
        i_found_signatures_cosign=t_verify_entries_cosign._raw_o_verified,
        r_gsheets=r_gsheets,
    )

    d_i_container_image_references: str = "Container image references to verify."
    d_i_container_image_references: str = "Container image identities to verify."
    d_i_public_key_file: str = "Public key file to verify cosign signatures."
    d_i_signing_keys: str = """Signing keys used to populate SignEntry models.
For this tractor they do no need to make sense."""
    d_r_signer_wrapper_cosign: str = "Cosign signer wrapper."
    d_r_dst_quay_client: str = "Destination Quay client."
    d_r_sigstore: str = "Sigstore client."
    d_r_gsheets: str = "Google Sheets client."
    d_a_executor: str = "Executor to use."
    d_a_dry_run: str = "Dry run mode."


class VerifyRepos(Tractor):
    """Sign container images."""

    r_dst_quay_client: Union[QuayClient, FakeQuayClient] = NullPort[
        Union[QuayClient, FakeQuayClient]
    ]()
    r_sigstore: Port[Union[Sigstore, FakeSigstore]] = NullPort[Union[Sigstore, FakeSigstore]]()

    i_container_image_repos: Port[TList[str]] = NullPort[TList[str]]()
    i_container_image_repos_file: Port[Optional[str]] = NullPort[Optional[str]]()
    i_container_image_repo_identities: Port[TList[str]] = NullPort[TList[str]]()
    i_rekor_public_key_file: Port[str] = NullPort[str]()
    i_public_key_file: Port[str] = NullPort[str]()
    i_signing_key: Port[str] = NullPort[str]()

    a_executor: Union[ProcessPoolExecutor, ThreadPoolExecutor, LoopExecutor] = ThreadPoolExecutor(
        pool_size=10, executor_type="thread_pool_executor"
    )
    a_dry_run: bool = False

    t_decide_repos: DecideRepos = DecideRepos(
        uid="decide_repos",
        i_container_image_repos=i_container_image_repos,
        i_container_image_repo_file=i_container_image_repos_file,
    )

    t_get_container_image_tags: STMDGetContainerImageTags = STMDGetContainerImageTags(
        uid="get_container_image_tags",
        r_quay_client=r_dst_quay_client,
        i_container_image_repo=t_decide_repos.o_container_image_repos,
        i_container_image_repo_identities=i_container_image_repo_identities,
        a_executor=a_executor,
    )

    t_flatten_container_references: Flatten[str] = Flatten[str](
        uid="flatten_container_references",
        i_complex=t_get_container_image_tags.o_container_references,
    )

    t_flatten_container_image_identities: Flatten[str] = Flatten[str](
        uid="flatten_container_identities",
        i_complex=t_get_container_image_tags.o_container_identities,
    )

    t_populate_signing_keys: ListMultiplier[str, str] = ListMultiplier[str, str](
        uid="populate_signing_keys",
        i_scalar=i_signing_key,
        i_list=t_flatten_container_references.o_flat,
    )

    t_parse_container_references: STMDParseContainerImageReference = (
        STMDParseContainerImageReference(
            uid="parse_container_references",
            i_container_image_reference=t_flatten_container_references._raw_o_flat,
            a_executor=a_executor,
        )
    )

    t_populate_digests: STMDPopulateContainerDigest = STMDPopulateContainerDigest(
        uid="populate_digests",
        r_quay_client=r_dst_quay_client,
        i_container_parts=t_parse_container_references._raw_o_container_parts,
        a_executor=a_executor,
    )

    t_make_sign_entries: STMDSignEntriesFromContainerParts = STMDSignEntriesFromContainerParts(
        uid="sign_entries_from_container_parts",
        i_container_parts=t_populate_digests._raw_o_container_parts,
        i_container_identity=t_flatten_container_image_identities._raw_o_flat,
        i_signing_key=t_populate_signing_keys._raw_o_list,
        a_executor=a_executor,
    )

    t_flatten_sign_entries: Flatten[SignEntry] = Flatten[SignEntry](
        uid="flatten_sign_entries",
        i_complex=t_make_sign_entries._raw_o_sign_entries,
    )
    t_verify_entries_cosign: STMDVerifyEntryCosign = STMDVerifyEntryCosign(
        uid="verify_entries_cosign",
        i_sign_entry=t_flatten_sign_entries._raw_o_flat,
        i_rekor_public_key_file=i_rekor_public_key_file,
        i_public_key_file=i_public_key_file,
    )
    t_verify_entries_legacy: VerifyEntriesLegacy = VerifyEntriesLegacy(
        uid="verify_entries_legacy",
        i_sign_entries=t_flatten_sign_entries._raw_o_flat,
        r_sigstore=r_sigstore,
    )

    d_i_public_key_file: str = "Public key file to verify cosign signatures."
    d_i_signing_key: str = """Signing key used to populate SignEntry models.
For this tractor they do no need to make sense."""
    d_i_rekor_public_key_file: str = "Public key to validate against rekor instance"
    d_r_dst_quay_client: str = "Destination Quay client."
    d_r_sigstore: str = "Sigstore client."
    d_a_executor: str = "Executor to use."
    d_a_dry_run: str = "Dry run mode."
