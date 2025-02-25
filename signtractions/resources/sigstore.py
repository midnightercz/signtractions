import json
import requests
import subprocess

from pytractions.base import Base


class Sigstore(Base):
    """Container reference constructor."""

    base_url: str = ""

    def get_signatures(self, image, digest):
        digest = digest.replace("sha256:", "")
        i = 1
        signatures = []
        while True:
            #print("Fetching signatures", f"{self.base_url}{image}@sha256={digest}/signature-{i}")
            ret = requests.get(f"{self.base_url}{image}@sha256={digest}/signature-{i}")
            if ret.status_code == 404:
                break
            if ret.status_code != 200:
                ret.raise_for_status()
            stdout, stderr = subprocess.Popen(["gpg", "-d"],
                                 stdin=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 stdout=subprocess.PIPE).communicate(ret.content)
            signatures.append(json.loads(stdout))
            i += 1
        return signatures
