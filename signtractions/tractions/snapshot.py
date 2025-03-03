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

    d_: str = """Parse snapshot json string into SnapshotSpec 
object (https://pkg.go.dev/github.com/redhat-appstudio/rhtap-cli/api/v1alpha1#SnapshotSpec)"""
    d_i_snapshot_str: str = "Snapshot string in json format"
    d_i_snapshot_file: str = "Snapshot file path"
    d_o_snapshot_spec: str = "Parsed Snapshot object (json format)"

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

    d_: str = """Extract container image references from SnapshotSpec object."""
    d_i_snapshot_spec: str = "SnapshotSpec object"
    d_o_container_images: str = "List of container image references"
    d_o_container_identities: str = "List of container identities"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        for component in self.i_snapshot_spec.components:
            self.o_container_images.append(component.containerImage)
            self.o_container_identities.append(component.containerImage)
