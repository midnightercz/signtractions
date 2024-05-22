from typing import Optional
from dataclasses import field

from pytractions.base import Base, TList


class ContainerParts(Base):
    """Data structure to hold container reference parts."""

    registry: str = ""
    image: str = ""
    tag: Optional[str] = None
    digests: TList[str] = field(default_factory=TList[str])
    arches: TList[str] = field(default_factory=TList[str])

    def make_reference(self):
        """Convert container parts back to reference."""
        if self.tag:
            return "{}/{}:{}".format(self.registry, self.image, self.tag)
        else:
            return "{}/{}@{}".format(self.registry, self.image, self.digests[0])
