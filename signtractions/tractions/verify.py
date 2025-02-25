import logging

from pytractions.base import (
    Traction,
    OnUpdateCallable,
    TList,
    TDict
)

import subprocess

from ..models.signing import SignEntry
from ..resources.quay_client import QuayClient
from ..resources.sigstore import Sigstore


LOG = logging.getLogger()
logging.basicConfig()
LOG.setLevel(logging.INFO)


class VerifyEntriesLegacy(Traction):
    """Sign SignEntries."""
    i_sign_entries: TList[SignEntry]
    r_sigstore: Sigstore
    o_verified: TDict[SignEntry, bool]

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        for entry in self.i_sign_entries:
            if entry.arch != "amd64":
                continue
            image_tag = entry.identity.split("/", 1)[-1]
            image = image_tag.split(":")[0]

            LOG.info(f"Legacy: Verifying {entry.reference}")

            signatures = self.r_sigstore.get_signatures(image, entry.digest)
            found = False
            for signature in signatures:
                if signature["critical"]['identity']['docker-reference'] == entry.identity:
                    found = True
                    break
            self.o_verified[entry] = found


class VerifyEntriesCosign(Traction):
    """Sign SignEntries."""
    i_sign_entries: TList[SignEntry]
    i_public_key_file: str
    r_dst_quay_client: QuayClient
    o_verified: TDict[SignEntry, bool]

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        deduplicated_sign_entries = []
        references = []
        # for entry in self.i_sign_entries:
        #     if entry.reference not in references:
        #         references.append(entry.reference)
        #         deduplicated_sign_entries.append(entry)

        username = self.r_dst_quay_client.username
        password = self.r_dst_quay_client.password

        for entry in self.i_sign_entries:
            LOG.info(f"Cosign: Verifying {entry.reference} {entry.digest}")
            p = subprocess.Popen(
                ["cosign", "verify", "--key", self.i_public_key_file, entry.reference],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            stdout, stderr = p.communicate()
            if p.returncode != 0:
                print(f"Error verifying {entry.reference} {entry.digest}", stdout, stderr)
                self.o_verified[entry] = False
                print("Verificaiton failed")
                print(stdout)
                print(stderr)
            else:
                self.o_verified[entry] = True
        print("Cosign verification done")
        for entry, verified in self.o_verified.items():
            print(f"{entry.reference} verified: {verified}")
