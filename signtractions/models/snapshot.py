from typing import Optional

from dataclasses import field

from pytractions.base import Base, TList, TDict


class ComponentSourceGit(Base):
    """Component source data structure."""

    context: str = ""
    dockerfileUrl: str = ""
    revision: str = ""
    url: str = ""


class ComponentSource(Base):
    """Component source data structure."""

    git: Optional[ComponentSourceGit]


class SnapshotSpecComponent(Base):
    """Snapshot component data structure."""

    name: str = ""
    containerImage: str = ""
    repository: str = ""
    source: Optional[ComponentSource] = None


class SnapshotSpec(Base):
    """Data structure to hold container reference parts."""

    application: str = ""
    components: TList[SnapshotSpecComponent] = field(default_factory=TList[SnapshotSpecComponent])
    artifacts: TDict[str, str] = field(default_factory=TDict[str, str])
