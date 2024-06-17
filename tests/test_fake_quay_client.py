import json
import pytest

from pytractions.base import TDict

from signtractions.resources import fake_quay_client
from signtractions.resources import exceptions


def test_get_manifest_list_success():
    ml = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribuytion.manifest.list.v2+json",
        "manifests": [
            {
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "size": 429,
                "digest": "sha256:6d5f4d65fg4d6f54g",
                "platform": {"architecture": "arm64", "os": "linux"},
            }
        ],
    }
    client = fake_quay_client.FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json(
            {
                "quay.io/namespace/image:1": {
                    "application/vnd.docker.distribution.manifest.list.v2+json": json.dumps(ml)
                }
            }
        ),
    )
    ret_ml = client.get_manifest(
        "quay.io/namespace/image:1",
        media_type="application/vnd.docker.distribution.manifest.list.v2+json",
    )
    assert ml == ret_ml


def test_get_manifest_list_raw_success():
    ml = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
        "manifests": [
            {
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "size": 429,
                "digest": "sha256:6d5f4d65fg4d6f54g",
                "platform": {"architecture": "arm64", "os": "linux"},
            }
        ],
    }
    client = fake_quay_client.FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
    )
    client.populate_manifest(
        "quay.io/namespace/image:1",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        True,
        json.dumps(ml),
    )
    ret_ml = client.get_manifest(
        "quay.io/namespace/image:1",
        raw=True,
        media_type="application/vnd.docker.distribution.manifest.list.v2+json",
    )
    assert json.dumps(ml) == ret_ml


def test_get_manifest_list_raw_return_headers_success():
    ml = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
        "manifests": [
            {
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "size": 429,
                "digest": "sha256:6d5f4d65fg4d6f54g",
                "platform": {"architecture": "arm64", "os": "linux"},
            }
        ],
    }
    client = fake_quay_client.FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
    )
    client.populate_manifest(
        "quay.io/namespace/image:1",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        {"some": "value"},
        json.dumps(ml, sort_keys=True),
    )
    ret_ml, headers = client.get_manifest(
        "quay.io/namespace/image:1",
        raw=True,
        return_headers=True,
        media_type="application/vnd.docker.distribution.manifest.list.v2+json",
    )
    assert json.dumps(ml, sort_keys=True) == ret_ml
    assert headers == {"return": "headers"}


def test_get_manifest_list_wrong_type():
    manifest = {
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "size": 429,
        "digest": "sha256:6d5f4d65fg4d6f54g",
        "platform": {"architecture": "arm64", "os": "linux"},
    }
    client = fake_quay_client.FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
    )
    client.populate_manifest(
        "quay.io/namespace/image:1",
        "application/vnd.docker.distribution.manifest.v2+json",
        False,
        json.dumps(manifest),
    )

    with pytest.raises(exceptions.ManifestTypeError, match=".*doesn't have a .* manifest"):
        client.get_manifest(
            "quay.io/namespace/image:1",
            media_type="application/vnd.docker.distribution.manifest.list.v2+json",
        )


def test_get_manifest_list_not_found():
    client = fake_quay_client.FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
    )
    with pytest.raises(exceptions.ManifestNotFoundError):
        client.get_manifest(
            "quay.io/namespace/image:1",
            media_type="application/vnd.docker.distribution.manifest.list.v2+json",
        )


def test_get_manifest_accept_any():
    v2s1_manifest = {
        "name": "hello-world",
        "tag": "latest",
        "architecture": "amd64",
        "fsLayers": [],
        "history": [],
        "schemaVersion": 1,
        "signatures": [],
    }

    client = fake_quay_client.FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
    )
    client.populate_manifest(
        "quay.io/namespace/image:1",
        "application/vnd.docker.distribution.manifest.v1+json",
        False,
        json.dumps(v2s1_manifest),
    )
    ret_manifest = client.get_manifest("quay.io/namespace/image:1")
    assert v2s1_manifest == ret_manifest


def test_get_manifest_raw_accept_any_return_headers():
    v2s1_manifest = {
        "name": "hello-world",
        "tag": "latest",
        "architecture": "amd64",
        "fsLayers": [],
        "history": [],
        "schemaVersion": 1,
        "signatures": [],
    }

    client = fake_quay_client.FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
    )
    client.populate_manifest(
        "quay.io/namespace/image:1",
        "application/vnd.docker.distribution.manifest.v1+json",
        False,
        json.dumps(v2s1_manifest),
    )
    ret_manifest, ret_headers = client.get_manifest(
        "quay.io/namespace/image:1", return_headers=True, raw=True
    )
    assert json.dumps(v2s1_manifest) == ret_manifest
    assert ret_headers == {"return": "headers"}


def test_get_v2s1_manifest_wrong_type():
    v2s2_manifest = {
        "mediaType": "application/vnd.docker.distribution.manifest.v1+json",
        "size": 429,
        "digest": "sha256:6d5f4d65fg4d6f54g",
        "platform": {"architecture": "arm64", "os": "linux"},
    }
    client = fake_quay_client.FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
    )
    client.populate_manifest(
        "quay.io/namespace/image:1",
        "application/vnd.docker.distribution.manifest.v1+json",
        False,
        json.dumps(v2s2_manifest, sort_keys=True),
    )
    with pytest.raises(
        exceptions.ManifestTypeError,
        match=r".*doesn't have a application/vnd\."
        r"docker\.distribution\.manifest\.v2\+json manifest",
    ):
        client.get_manifest(
            "quay.io/namespace/image:1",
            media_type="application/vnd.docker.distribution.manifest.v2+json",
        )


def test_upload_manifest_list_success():
    ml = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
        "manifests": [
            {
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "size": 429,
                "digest": "sha256:6d5f4d65fg4d6f54g",
                "platform": {"architecture": "arm64", "os": "linux"},
            }
        ],
    }
    client = fake_quay_client.FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
    )
    client.upload_manifest(json.dumps(ml, sort_keys=True), "quay.io/namespace/image:1", raw=True)
    assert client.fake_manifests["quay.io/namespace/image:1"][
        "application/vnd.docker.distribution.manifest.list.v2+json"
    ] == json.dumps(ml, sort_keys=True)


def test_upload_raw_manifest_success():
    ml = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
        "manifests": [
            {
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "size": 429,
                "digest": "sha256:6d5f4d65fg4d6f54g",
                "platform": {"architecture": "arm64", "os": "linux"},
            }
        ],
    }
    client = fake_quay_client.FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
    )
    client.upload_manifest(json.dumps(ml), "quay.io/namespace/image:1", raw=True)
    assert client.fake_manifests["quay.io/namespace/image:1"][
        "application/vnd.docker.distribution.manifest.list.v2+json"
    ] == json.dumps(ml)
