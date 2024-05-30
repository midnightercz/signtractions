from typing import Optional

from dataclasses import field

from pytractions.base import Base, TList


class ComponentSourceGit(Base):
    """Component source data structure."""

    context: str = ""
    dockerfileUrl: str = ""
    revision: str = ""
    url: str = ""


class ComponentSource(Base):
    """Component source data structure."""

    git: Optional[ComponentSourceGit]


class SnapshotComponent(Base):
    """Snapshot component data structure."""

    name: str = ""
    containerImage: str = ""
    repository: str = ""
    source: Optional[ComponentSource] = None


class Snapshot(Base):
    """Data structure to hold container reference parts."""

    application: str = ""
    components: TList[SnapshotComponent] = field(default_factory=TList[SnapshotComponent])
