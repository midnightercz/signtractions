import json

from pytractions.base import (
    Traction,
    TList,
    OnUpdateCallable,
)
from ..models.snapshot import SnapshotSpec


class ParseSnapshot(Traction):
    """Sign SignEntries."""

    i_snapshot_str: str
    i_snapshot_file: str
    o_snapshot_spec: SnapshotSpec

    d_: str = "Parse snapshot json string into Snapshot object."
    d_i_snapshot_str: str = "Snapshot string"
    d_o_snapshot_spec: str = "Parsed Snapshot object"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        if self.i_snapshot_str:
            self.o_snapshot_spec = SnapshotSpec.content_from_json(json.loads(self.i_snapshot_str))
        else:
            self.o_snapshot_spec = SnapshotSpec.content_from_json(
                json.load(open(self.i_snapshot_file))
            )


class ContainerImagesFromSnapshot(Traction):
    """Extract container image references from snapshot."""

    i_snapshot_spec: SnapshotSpec
    o_container_images: TList[str]
    o_container_identities: TList[str]

    d_: str = """Extract container image references from snapshot."""
    d_i_snapshot_spec: str = "Snapshot object"
    d_o_container_images: str = "List of container image references"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        for component in self.i_snapshot_spec.components:
            self.o_container_images.append(component.containerImage)
            self.o_container_identities.append(component.containerImage)
