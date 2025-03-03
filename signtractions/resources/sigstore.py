import json
import requests
import subprocess

from pytractions.base import Base

from ..models.signing import LegacySignature


class VerificationError(Exception):
    """Verification error."""

    pass


class Sigstore(Base):
    """Container reference constructor."""

    base_url: str = ""

    def get_signatures(self, image, digest):
        """Get signatures for an image and digest."""
        digest = digest.replace("sha256:", "")
        i = 1
        signatures = []
        while True:
            ret = requests.get(f"{self.base_url}{image}@sha256={digest}/signature-{i}")
            if ret.status_code == 404:
                break
            if ret.status_code != 200:
                ret.raise_for_status()
            p = subprocess.Popen(
                ["gpg", "-d"], stdin=subprocess.PIPE, stderr=subprocess.PIPE, stdout=subprocess.PIPE
            )
            print("RC", p.returncode)
            stdout, stderr = p.communicate(ret.content)
            if p.returncode != 0:
                raise VerificationError(f"Error verifying {image} {digest}", stdout, stderr)

            signatures.append(LegacySignature.content_from_json(json.loads(stdout)))
            i += 1
        return signatures
