import json
import hashlib
import logging
from typing import Type, Union
from pytractions.base import Traction, TList, OnUpdateCallable, Port
from pytractions.stmd import STMD

from ..models.containers import ContainerParts
from ..models.quay import QuayTag, QuayRepo

from ..resources.quay_client import QuayClient
from ..resources.fake_quay_client import FakeQuayClient

LOG = logging.getLogger()
logging.basicConfig()
LOG.setLevel(logging.INFO)


class GetQuayRepositories(Traction):
    """Get list of repositories from Quay for given namespace."""

    i_namespace: str
    r_quay_client: Port[Union[QuayClient, FakeQuayClient]]
    o_repositories: TList[QuayRepo]

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        for repo in self.r_quay_client.get_repositories(self.i_namespace):
            self.o_repositories.append(repo)


class GetQuayTags(Traction):
    """Get repository tags."""

    i_repository: str
    r_quay_client: Port[Union[QuayClient, FakeQuayClient]]
    o_tags: TList[QuayTag]

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        for tag in self.r_quay_client.get_quay_repository_tags(self.i_repository):
            self.o_tags.append(tag)


class GetContainerImageTags(Traction):
    """Parser container image reference into parts."""

    i_container_image_repo: str
    i_container_image_repo_identities: TList[str]
    o_container_references: TList[str]
    o_container_identities: TList[str]
    r_quay_client: Port[Union[QuayClient, FakeQuayClient]]

    def _run(self, on_update: OnUpdateCallable = None) -> None:

        registry, repo_ns = self.i_container_image_repo.split("/", 1)
        ns, repo = repo_ns.split("/", 1)

        for tag in self.r_quay_client.get_repository_tags(repo_ns)["tags"]:
            if tag.endswith(".sig") or tag.endswith(".att") or tag.endswith(".sbom"):
                continue
            for identity in self.i_container_image_repo_identities:
                self.o_container_references.append(f"{self.i_container_image_repo}:{tag}")
                full_identity = f"{identity}/{repo.replace('----', '/')}:{tag}"
                self.o_container_identities.append(f"{full_identity}")


class ParseCotainerImageReference(Traction):
    """Parser container image reference into parts."""

    i_container_image_reference: str
    o_container_parts: ContainerParts

    d_: str = """Parser container image reference into ContainerParts model"""
    d_i_container_image_reference: str = "Container image reference to parse"
    d_o_container_parts: str = "Parsed container parts"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        registry, rest = self.i_container_image_reference.split("/", 1)
        if "@" in rest:
            image, digest = rest.split("@", 1)
            tag = None
        else:
            image, tag = rest.split(":", 1)
            digest = None
        self.o_container_parts = ContainerParts(
            registry=registry,
            image=image,
            tag=tag,
            digests=TList[str]([digest]) if digest else TList[str](),
            arches=TList[str]([""]) if digest else TList[str](),
        )
        self.add_details("parsed container parts" + str(self.o_container_parts))


class STMDParseContainerImageReference(STMD):
    """Parser container image references into list of parts."""

    _traction: Type[Traction] = ParseCotainerImageReference
    i_container_image_reference: TList[str]
    o_container_parts: TList[ContainerParts]

    d_: str = """Parser container image reference into ContainerParts model. STMD version."""
    d_i_container_image_reference: str = "List of container image references to parse"
    d_o_container_parts: str = "List of Parsed container parts"


class PopulateContainerDigest(Traction):
    """Fetch digest(s) for ContainerParts if there isn't any."""

    i_container_parts: ContainerParts
    o_container_parts: ContainerParts
    r_quay_client: QuayClient

    d_: str = """Fetch digest(s) for ContainerParts if there aren't any

    If fetched manifest by tag is manifest lists, populate also digests for manifests in the
    manifest list + digest of the list itself.
    """
    d_i_container_parts: str = "Container parts to fetch digest for"
    d_o_container_parts: str = "Container parts with digests populated (or unchanged)"
    d_r_quay_client: str = "Quay client to fetch manifest"

    def _run(self, on_update: OnUpdateCallable = None) -> None:
        self.o_container_parts = self.i_container_parts
        if self.i_container_parts.tag:
            LOG.info(
                "Fetching {}/{}:{}".format(
                    self.i_container_parts.registry,
                    self.i_container_parts.image,
                    self.i_container_parts.tag,
                )
            )
            manifest_str = self.r_quay_client.get_manifest(
                "{}/{}:{}".format(
                    self.i_container_parts.registry,
                    self.i_container_parts.image,
                    self.i_container_parts.tag,
                ),
                raw=True,
            )
        else:
            LOG.info(
                "Fetching {}/{}@{}".format(
                    self.i_container_parts.registry,
                    self.i_container_parts.image,
                    self.i_container_parts.digests[0],
                )
            )
            manifest_str = self.r_quay_client.get_manifest(
                "{}/{}@{}".format(
                    self.i_container_parts.registry,
                    self.i_container_parts.image,
                    self.i_container_parts.digests[0],
                ),
                raw=True,
            )

        manifest = json.loads(manifest_str)
        self.o_container_parts = ContainerParts(
            registry=self.i_container_parts.registry,
            image=self.i_container_parts.image,
            tag=self.i_container_parts.tag,
        )
        if manifest["mediaType"] in (
            QuayClient._MANIFEST_LIST_TYPE,
            QuayClient._MANIFEST_OCI_LIST_TYPE,
        ):
            for _manifest in manifest["manifests"]:
                self.o_container_parts.digests.append(_manifest["digest"])
                self.o_container_parts.arches.append(_manifest["platform"]["architecture"])

            hasher = hashlib.sha256()
            hasher.update(manifest_str.encode("utf-8"))
            digest = hasher.hexdigest()
            self.o_container_parts.digests.append("sha256:" + digest)
            self.o_container_parts.arches.append("multiarch")

        else:
            hasher = hashlib.sha256()
            hasher.update(manifest_str.encode("utf-8"))
            digest = hasher.hexdigest()
            self.o_container_parts.digests.append("sha256:" + digest)
            self.o_container_parts.arches.append("")


class STMDPopulateContainerDigest(STMD):
    """Fetch digest(s) for ContainerParts if there isn't any. STMD version."""

    _traction: Type[Traction] = PopulateContainerDigest
    i_container_parts: TList[ContainerParts]
    o_container_parts: TList[ContainerParts]
    r_quay_client: QuayClient

    d_: str = """Fetch digest(s) for ContainerParts if there aren't any

    If fetched manifest by tag is manifest lists, populate also digests for manifests in the
    manifest list + digest of the list itself.
    """
    d_i_container_parts: str = "Container parts to fetch digest for"
    d_o_container_parts: str = "Container parts with digests populated (or unchanged)"
    d_r_quay_client: str = "Quay client to fetch manifest"
