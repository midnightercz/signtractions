import json

from pytractions.base import (
    Traction,
    In,
    Out,
    TList,
    OnUpdateCallable,
)
from ..models.snapshot import Snapshot


class ParseSnapshot(Traction):
    """Sign SignEntries."""

    i_snapshot_str: In[str]
    o_snapshot: Out[Snapshot]

    d_: str = "Parse snapshot json string into Snapshot object."
    d_i_snapshot_str: str = "Snapshot string"
    d_o_snapshot: str = "Parsed Snapshot object"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        self.o_snapshot.data = Snapshot.content_from_json(json.loads(self.i_snapshot_str.data))


class ContainerImagesFromSnapshot(Traction):
    """Extract container image references from snapshot."""

    i_snapshot: In[Snapshot]
    o_container_images: Out[TList[str]]

    d_: str = """Extract container image references from snapshot."""
    d_i_snapshot: str = "Snapshot object"
    d_o_container_images: str = "List of container image references"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        for component in self.i_snapshot.data.components:
            self.o_container_images.data.append(component.containerImage)
