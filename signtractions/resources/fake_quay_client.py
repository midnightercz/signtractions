from typing import cast
import json
import logging

from pytractions.base import TDict, TList, doc

from .quay_client import QuayClient, ManifestTypeError, ManifestNotFoundError
from .types import ManifestList, Manifest
from ..models.quay import QuayRepo, QuayTag


LOG = logging.getLogger()
logging.basicConfig()
LOG.setLevel(logging.INFO)


class FakeQuayClient(QuayClient):
    """Class for performing Docker HTTP API operations with the Quay registry."""

    fake_manifests: TDict[str, TDict[str, str]]
    fake_repositories: TDict[str, TDict[str, QuayRepo]]
    fake_tags: TDict[str, TDict[str, TList[QuayTag]]]

    d_fake_manifests: str = doc("Fake manifests for testing.")

    def __post_init__(self):
        """Fake quay client post init."""
        LOG.info("Populate fake manifests:")
        for image, media_types in self.fake_manifests.items():
            LOG.info("Image: {}".format(image))
            for mtype in media_types:
                LOG.info("\tMedia Type {}".format(mtype))

    def populate_manifest(self, image, media_type, return_headers, manifest):
        """Populate fake quay client with manifest for given media_type."""
        self.fake_manifests.setdefault(image, TDict[str, str]({}))
        self.fake_manifests[image][media_type] = manifest

    def populate_repository(self, namespace: str, repository: str, repo_data: QuayRepo):
        """Populate fake quay client with repository."""
        self.fake_repositories.setdefault(namespace, TDict[str, QuayRepo]({}))[
            repository
        ] = repo_data

    def populate_tags(self, namespace: str, repository: str, tags: TList[QuayTag]):
        """Populate fake quay client with tag."""
        self.fake_tags.setdefault(namespace, TDict[str, TList[QuayTag]]({})).setdefault(
            repository, TList[QuayTag]([])
        ).extend(tags)

    def get_repositories(self, namespace: str) -> TList[QuayRepo]:
        """Get list of repositories for given namespace."""
        return TList[QuayRepo](
            [repo for repo in self.fake_repositories.get(namespace, {}).values()]
        )

    def get_manifest(
        self,
        image: str,
        raw: bool = False,
        media_type: str | None = None,
        return_headers: bool = False,
    ) -> ManifestList | Manifest | str:
        """
        Get manifest of given media type.

        Args:
            image (str):
                Image for which to get the manifest list.
            raw (bool):
                Whether to return the manifest as raw JSON.
            manifest_list (bool):
                Whether to only return a manifest list and raise an exception otherwise.
            media_type (str):
                Can be application/vnd.docker.distribution.manifest.list.v2+json,
                application/vnd.docker.distribution.manifest.v2+json,
                application/vnd.docker.distribution.manifest.v1+json,
                application/vnd.oci.image.manifest.v1+json, application/vnd.oci.image.index.v1+json
                or None indicating which manifest type is requested. If it's None,
                manifest list is prefered, but if v2s2 is returned instead, v2s2
                is returned as final result. If neither is found, same order is attempted with
                OCI type images.
        Returns (dict|str):
            Image manifest
        Raises:
            ManifestTypeError:
                When the image doesn't return the requested manifest type.
            ValueError:
                If Manifest list and V2S1 manifest are requested at the same time.
        """
        if media_type is not None:
            if image in self.fake_manifests and media_type in self.fake_manifests[image]:
                if raw:
                    if return_headers:
                        return (self.fake_manifests[image][media_type], {"return": "headers"})
                    else:
                        return self.fake_manifests[image][media_type]
                else:
                    return json.loads(self.fake_manifests[image][media_type])
            elif image in self.fake_manifests and media_type not in self.fake_manifests[image]:
                raise ManifestTypeError(
                    "Image {0} doesn't have a {1} manifest".format(image, media_type)
                )
            else:
                raise ManifestNotFoundError()
        else:
            for manifest_type in (
                QuayClient._MANIFEST_LIST_TYPE,
                QuayClient._MANIFEST_V2S2_TYPE,
                QuayClient._MANIFEST_OCI_LIST_TYPE,
                QuayClient._MANIFEST_OCI_V2S2_TYPE,
                QuayClient._MANIFEST_V2S1_TYPE,
            ):
                if image in self.fake_manifests and manifest_type in self.fake_manifests[image]:
                    if raw:
                        if return_headers:
                            return (
                                self.fake_manifests[image][manifest_type],
                                {"return": "headers"},
                            )
                        else:
                            return self.fake_manifests[image][manifest_type]
                    else:
                        return json.loads(self.fake_manifests[image][manifest_type])
            else:
                raise ManifestNotFoundError(image)

    def upload_manifest(self, manifest: ManifestList | str, image: str, raw: bool = False) -> None:
        """
        Upload manifest to a specified image.

        All manifest types are supported (manifest, manifest list).

        Args:
            manifest (dict):
                Manifest to be uploaded.
            image (str):
                Image address to upload the manifest to.
            raw (bool):
                Whether the given manifest is a string (raw) or a Python dictionary
        """
        if raw:
            manifest_type = json.loads(cast(str, manifest)).get(
                "mediaType", self._MANIFEST_V2S1_TYPE
            )
            self.fake_manifests.setdefault(image, TDict[str, str]({}))[manifest_type] = manifest
        else:
            manifest_type = cast(ManifestList, manifest).get("mediaType", self._MANIFEST_V2S1_TYPE)
            self.fake_manifests.setdefault(image, TDict[str, str]({}))[manifest_type] = json.dumps(
                manifest, sort_keys=True
            )

    def get_repository_tags(self, repository: str):
        """Get list of tags for given repository."""
        namespace, repository = repository.split("/")
        return {"tags": [tag.name for tag in self.fake_tags.get(namespace, {}).get(repository, [])]}

    def get_quay_repository_tags(self, repository: str) -> TList[QuayTag]:
        """Get list of tags for given repository."""
        namespace, repository = repository.split("/")
        return TList[QuayTag](self.fake_tags.get(namespace, {}).get(repository, []))
