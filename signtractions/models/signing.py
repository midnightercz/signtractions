from typing import Optional

from pytractions.base import Base


class SignEntry(Base):
    """Data structure to hold signing related information.

    Args:
        signing_key (str): Signing key.
        repo (str): Repo reference in format <registry>/<repo>
        reference (str): Reference in format <registry>/<repo>:<tag>
        digest (str): Digest of the manifest.
        arch (str): Architecture of the manifest.
    """

    repo: str
    reference: Optional[str]
    digest: str
    signing_key: str
    arch: str
