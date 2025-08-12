import dataclasses
import logging
import subprocess

from pytractions.base import Base, TList

LOG = logging.getLogger("signtractions.resources.cosign")


class VerifitcationFailed(Exception):
    """Verification failed exception."""

    pass


class CosignClient(Base):
    """Class for performing Docker HTTP API operations with the Quay registry."""

    def verify(self, key_file, reference) -> None:
        """Verify the signature of the image."""
        p = subprocess.Popen(
            ["cosign", "verify", "--key", key_file, reference],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            raise VerifitcationFailed("Verification failed")


class FakeCosignClient(Base):
    """Class simulating cosign client."""

    verify_calls: TList[TList[str]] = dataclasses.field(default_factory=TList[TList[str]])

    def verify(self, key_file, reference) -> None:
        """Verify the signature of the image."""
        self.verify_calls.append(TList[str]([key_file, reference]))
