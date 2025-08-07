import os
import logging
from typing import Union

from pytractions.base import TList, TDict
from pytractions.stmd import STMD
from pytractions.traction import Traction

import subprocess

from ..models.signing import SignEntry
from ..resources.sigstore import Sigstore
from ..resources.fake_sigstore import FakeSigstore


LOG = logging.getLogger()
logging.basicConfig()
LOG.setLevel(logging.INFO)


class VerifyEntriesLegacy(Traction):
    """Sign SignEntries."""

    i_sign_entries: TList[SignEntry]
    r_sigstore: Union[Sigstore, FakeSigstore]
    o_verified: TDict[SignEntry, bool]

    d_: str = """Verify SignEntries have signatures in the legacy sigstore."""
    d_i_sign_entries: str = "List of SignEntries to verify"
    d_r_sigstore: str = "Sigstore resource"
    d_o_verified: str = "Dictionary of SignEntry to verification status"

    def _run(self) -> None:
        for entry in self.i_sign_entries:
            if entry.arch != "amd64":
                continue
            image_tag = entry.identity.split("/", 1)[-1]
            image = image_tag.split(":")[0]

            self.log.info(f"Legacy: Verifying {entry.reference}")

            signatures = self.r_sigstore.get_signatures(image, entry.digest)
            found = False
            for signature in signatures:
                if signature.critical.identity.docker_reference == entry.identity:
                    found = True
                    break
            self.o_verified[entry] = found


class VerifyEntriesCosign(Traction):
    """Sign SignEntries."""

    i_sign_entries: TList[SignEntry]
    i_public_key_file: str
    i_rekor_public_key_file: str
    o_verified: TDict[SignEntry, bool]

    d_: str = """Verify SignEntries have signatures in the cosign sigstore."""
    d_i_sign_entries: str = "List of SignEntries to verify"
    d_i_public_key_file: str = "Public key file"
    d_o_verified: str = "Dictionary of SignEntry to verification status"

    def _run(self) -> None:
        pk_backup = os.environ.get("SIGSTORE_REKOR_PUBLIC_KEY")
        os.environ["SIGSTORE_REKOR_PUBLIC_KEY"] = self.i_rekor_public_key_file
        try:
            for entry in self.i_sign_entries:
                self.log.info(f"Cosign: Verifying {entry.reference} {entry.digest}")
                p = subprocess.Popen(
                    ["cosign", "verify", "--key", self.i_public_key_file, entry.reference],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = p.communicate()
                if p.returncode != 0:
                    self.log.error(f"Error verifying {entry.reference} {entry.digest}")
                    self.o_verified[entry] = False
                    self.log.error("Verificaiton failed")
                    self.log.error("STDOUT:")
                    self.log.error(stdout)
                    self.log.error("STDERR:")
                    self.log.error(stderr)
                else:
                    self.o_verified[entry] = True
        finally:
            if pk_backup:
                os.environ["SIGSTORE_REKOR_PUBLIC_KEY"]


class VerifyEntryCosign(Traction):
    """Sign SignEntries."""

    i_sign_entry: SignEntry
    i_public_key_file: str
    i_rekor_public_key_file: str
    o_verified: bool

    d_: str = """SignEntry have signatures in the cosign sigstore."""
    d_i_sign_entry: str = "SignEntry to verify"
    d_i_public_key_file: str = "Public key file"
    d_o_verified: str = "Dictionary of SignEntry to verification status"

    def _run(self) -> None:
        pk_backup = os.environ.get("SIGSTORE_REKOR_PUBLIC_KEY")
        os.environ["SIGSTORE_REKOR_PUBLIC_KEY"] = self.i_rekor_public_key_file
        try:
            entry = self.i_sign_entry
            self.log.info(f"Cosign: Verifying {entry.reference} {entry.digest}")
            p = subprocess.Popen(
                ["cosign", "verify", "--key", self.i_public_key_file, entry.reference],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                self.log.error(f"Error verifying {entry.reference} {entry.digest}")
                self.o_verified = False
                self.log.error("Verificaiton failed")
                self.log.error("STDOUT:")
                self.log.error(stdout)
                self.log.error("STDERR:")
                self.log.error(stderr)
            else:
                self.o_verified = True
        finally:
            if pk_backup:
                os.environ["SIGSTORE_REKOR_PUBLIC_KEY"]


STMDVerifyEntryCosign = STMD.wrap(
    VerifyEntryCosign, single_inputs=("i_public_key_file", "i_rekor_public_key_file")
)
