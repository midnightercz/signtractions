from typing import Optional

from pytractions.base import Base, TDict


class SignEntry(Base):
    """Data structure to hold signing related information.

    Args:
        signing_key (str): Signing key.
        repo (str): Repo reference in format <registry>/<repo>
        reference (str): Reference in format <registry>/<repo>:<tag>
        digest (str): Digest of the manifest.
        arch (str): Architecture of the manifest.
    """

    repo: str = ""
    reference: Optional[str] = ""
    digest: str = ""
    signing_key: str = ""
    arch: str = ""
    identity: Optional[str] = ""


class _LegacySignatureCriticalImage(Base):
    _SERIALIZE_REPLACE_FIELDS = {"docker_manifest_digest": "docker-manifest-digest"}
    docker_manifest_digest: str


class _LegacySignatureCriticalIdentity(Base):
    _SERIALIZE_REPLACE_FIELDS = {"docker_reference": "docker-reference"}
    docker_reference: str


class _LegacySignatureCritical(Base):
    image: _LegacySignatureCriticalImage
    type: str = "atomic container signature"
    identity: _LegacySignatureCriticalIdentity


class LegacySignature(Base):
    """Data structure to hold legacy signature information."""

    critical: _LegacySignatureCritical
    optional: TDict[str, str] = TDict[str, str]({})
