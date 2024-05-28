import pytest


@pytest.fixture
def fix_manifest_v2s2():
    return {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
        "config": {
            "mediaType": "application/vnd.docker.container.image.v1+json",
            "size": 5830,
            "digest": "sha256:5f88c70a8b703ed93f24c24a809f6c7838105642dd6fb0a19d1f873450304627",
        },
        "layers": [
            {
                "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                "size": 76421592,
                "digest": "sha256:eae19a56e9c600eb0a59816d9d0ad7065824a34a13be60469084304fc7170334",
            },
            {
                "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                "size": 1811,
                "digest": "sha256:be73321c79565b4e2fdf9f55ba6333e5d50a1bcf583db3b41be45a9be7d82431",
            },
            {
                "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                "size": 4280307,
                "digest": "sha256:c06d2750af3cc462e5f8e34eccb0fdd350b28d8cd3b72b86bbf4d28e4a40e6ea",
            },
            {
                "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                "size": 9608840,
                "digest": "sha256:457122c845c27bd616c9f80748f1fa19f3d69783957448b3eca30cea7ed9a0a0",
            },
            {
                "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
                "size": 96318592,
                "digest": "sha256:899560bde2837f603312932d5134a4bb3621e328797895233da54e9d5336911f",
            },
        ],
    }


@pytest.fixture
def fix_manifest_list():
    return {
        "schemaVersion": 2,
        "mediaType": "application/vnd.docker.distribution.manifest.list.v2+json",
        "manifests": [
            {
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "size": 949,
                "digest": "sha256:2e8f38a0a8d2a450598430fa70c7f0b53aeec991e76c3e29c63add599b4ef7ee",
                "platform": {"architecture": "amd64", "os": "linux"},
            },
            {
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "size": 949,
                "digest": "sha256:b3f9218fb5839763e62e52ee6567fe331aa1f3c644f9b6f232ff23959257acf9",
                "platform": {"architecture": "arm64", "os": "linux"},
            },
            {
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "size": 949,
                "digest": "sha256:496fb0ff2057c79254c9dc6ba999608a98219c5c93142569a547277c679e532c",
                "platform": {"architecture": "arm", "os": "linux"},
            },
            {
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "size": 949,
                "digest": "sha256:146ab6fa7ba3ab4d154b09c1c5522e4966ecd071bf23d1ba3df6c8b9fc33f8cb",
                "platform": {"architecture": "ppc64le", "os": "linux"},
            },
            {
                "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
                "size": 949,
                "digest": "sha256:bbef1f46572d1f33a92b53b0ba0ed5a1d09dab7ffe64be1ae3ae66e76275eabd",
                "platform": {"architecture": "s390x", "os": "linux"},
            },
        ],
    }


@pytest.fixture
def fix_snapshot_str():
    return """
{
    "application": "testApplication",
    "components": [
        {
            "containerImage": "quay.io/containers/podman:latest",
            "name": "podman",
            "repository": "containers/podman"
        },
        {
            "containerImage": "quay.io/containers/podman:1.0",
            "name": "podman",
            "repository": "containers/podman"
        }
    ]
}
"""
