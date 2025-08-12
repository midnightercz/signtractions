from typing import Optional
from pytractions.base import Base, TDict


class QuayTag(Base):
    """Quay Tag model."""

    name: str
    reversion: bool
    start_ts: int
    manifest_digest: str
    is_manifest_list: bool
    size: Optional[int]
    last_modified: str
    end_ts: Optional[int] = 0
    expiration: Optional[str] = None


class QuayRepo(Base):
    """Quay Repository model."""

    namespace: str
    name: str
    description: Optional[str]
    is_public: bool
    kind: str
    state: str
    is_starred: bool
    quota_report: TDict[str, Optional[int]]
