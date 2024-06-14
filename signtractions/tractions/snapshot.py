import json

from pytractions.base import (
    Traction,
    In,
    Out,
    TList,
    OnUpdateCallable,
)
from ..models.snapshot import SnapshotSpec


class ParseSnapshot(Traction):
    """Sign SignEntries."""

    i_snapshot_str: In[str]
    i_snapshot_file: In[str]
    o_snapshot_spec: Out[SnapshotSpec]

    d_: str = "Parse snapshot json string into Snapshot object."
    d_i_snapshot_str: str = "Snapshot string"
    d_o_snapshot_spec: str = "Parsed Snapshot object"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        if self.i_snapshot_str.data:
            self.o_snapshot_spec.data = SnapshotSpec.content_from_json(
                json.loads(self.i_snapshot_str.data)
            )
        else:
            self.o_snapshot_spec.data = SnapshotSpec.content_from_json(
                json.load(open(self.i_snapshot_file.data))
            )


class ContainerImagesFromSnapshot(Traction):
    """Extract container image references from snapshot."""

    i_snapshot_spec: In[SnapshotSpec]
    o_container_images: Out[TList[str]]

    d_: str = """Extract container image references from snapshot."""
    d_i_snapshot_spec: str = "Snapshot object"
    d_o_container_images: str = "List of container image references"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        for component in self.i_snapshot_spec.data.components:
            self.o_container_images.data.append(component.containerImage)
