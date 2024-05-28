from dataclasses import field

from pytractions.base import Base, TList


class SnapshotComponent(Base):
    """Snapshot component data structure."""

    name: str = ""
    containerImage: str = ""
    repository: str = ""


class Snapshot(Base):
    """Data structure to hold container reference parts."""

    application: str = ""
    components: TList[SnapshotComponent] = field(default_factory=TList[SnapshotComponent])
