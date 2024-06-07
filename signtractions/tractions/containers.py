import json
import hashlib
import logging
from typing import Type
from pytractions.base import Traction, TList, In, Out, Res, STMD, OnUpdateCallable

from ..models.containers import ContainerParts

from ..resources.quay_client import QuayClient

LOG = logging.getLogger()
logging.basicConfig()
LOG.setLevel(logging.INFO)


class ParseCotainerImageReference(Traction):
    """Parser container image reference into parts."""

    i_container_image_reference: In[str]
    o_container_parts: Out[ContainerParts]

    d_: str = """Parser container image reference into ContainerParts model"""
    d_i_container_image_reference: str = "Container image reference to parse"
    d_o_container_parts: str = "Parsed container parts"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        registry, rest = self.i_container_image_reference.data.split("/", 1)
        if "@" in rest:
            image, digest = rest.split("@", 1)
            tag = None
        else:
            image, tag = rest.split(":", 1)
            digest = None
        self.o_container_parts.data = ContainerParts(
            registry=registry,
            image=image,
            tag=tag,
            digests=TList[str]([digest]) if digest else TList[str](),
            arches=TList[str]([""]) if digest else TList[str](),
        )
        self.add_details("parsed container parts" + str(self.o_container_parts.data))


class STMDParseContainerImageReference(STMD):
    """Parser container image references into list of parts."""

    _traction: Type[Traction] = ParseCotainerImageReference
    i_container_image_reference: In[TList[str]]
    o_container_parts: Out[TList[ContainerParts]]

    d_: str = """Parser container image reference into ContainerParts model. STMD version."""
    d_i_container_image_reference: str = "List of container image references to parse"
    d_o_container_parts: str = "List of Parsed container parts"


class PopulateContainerDigest(Traction):
    """Fetch digest(s) for ContainerParts if there isn't any."""

    i_container_parts: In[ContainerParts]
    o_container_parts: Out[ContainerParts]
    r_quay_client: Res[QuayClient]

    d_: str = """Fetch digest(s) for ContainerParts if there aren't any

    If fetched manifest by tag is manifest lists, populate also digests for manifests in the
    manifest list + digest of the list itself.
    """
    d_i_container_parts: str = "Container parts to fetch digest for"
    d_o_container_parts: str = "Container parts with digests populated (or unchanged)"
    d_r_quay_client: str = "Quay client to fetch manifest"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        self.o_container_parts.data = self.i_container_parts.data
        if self.i_container_parts.data.tag:
            LOG.info(
                "Fetching {}/{}:{}".format(
                    self.i_container_parts.data.registry,
                    self.i_container_parts.data.image,
                    self.i_container_parts.data.tag,
                )
            )
            manifest_str = self.r_quay_client.r.get_manifest(
                "{}/{}:{}".format(
                    self.i_container_parts.data.registry,
                    self.i_container_parts.data.image,
                    self.i_container_parts.data.tag,
                ),
                raw=True,
            )
        else:
            LOG.info(
                "Fetching {}/{}@{}".format(
                    self.i_container_parts.data.registry,
                    self.i_container_parts.data.image,
                    self.i_container_parts.data.digests[0],
                )
            )
            manifest_str = self.r_quay_client.r.get_manifest(
                "{}/{}@{}".format(
                    self.i_container_parts.data.registry,
                    self.i_container_parts.data.image,
                    self.i_container_parts.data.digests[0],
                ),
                raw=True,
            )

        manifest = json.loads(manifest_str)
        self.o_container_parts.data = ContainerParts(
            registry=self.i_container_parts.data.registry,
            image=self.i_container_parts.data.image,
            tag=self.i_container_parts.data.tag,
        )
        if manifest["mediaType"] in (
            QuayClient._MANIFEST_LIST_TYPE,
            QuayClient._MANIFEST_OCI_LIST_TYPE,
        ):
            for _manifest in manifest["manifests"]:
                self.o_container_parts.data.digests.append(_manifest["digest"])
                self.o_container_parts.data.arches.append(_manifest["platform"]["architecture"])

            hasher = hashlib.sha256()
            hasher.update(manifest_str.encode("utf-8"))
            digest = hasher.hexdigest()
            self.o_container_parts.data.digests.append("sha256:" + digest)
            self.o_container_parts.data.arches.append("multiarch")

        else:
            hasher = hashlib.sha256()
            hasher.update(manifest_str.encode("utf-8"))
            digest = hasher.hexdigest()
            self.o_container_parts.data.digests.append("sha256:" + digest)
            self.o_container_parts.data.arches.append("")


class STMDPopulateContainerDigest(STMD):
    """Fetch digest(s) for ContainerParts if there isn't any. STMD version."""

    _traction: Type[Traction] = PopulateContainerDigest
    i_container_parts: In[TList[ContainerParts]]
    o_container_parts: Out[TList[ContainerParts]]
    r_quay_client: Res[QuayClient]

    d_: str = """Fetch digest(s) for ContainerParts if there aren't any

    If fetched manifest by tag is manifest lists, populate also digests for manifests in the
    manifest list + digest of the list itself.
    """
    d_i_container_parts: str = "Container parts to fetch digest for"
    d_o_container_parts: str = "Container parts with digests populated (or unchanged)"
    d_r_quay_client: str = "Quay client to fetch manifest"
