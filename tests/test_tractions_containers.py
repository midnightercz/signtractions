import json
from typing import Optional

import pytest

from pytractions.base import Port, TList, TDict
from pytractions.executor import LoopExecutor

from signtractions.resources.fake_quay_client import (
    FakeQuayClient,
    ManifestNotFoundError,
)
from signtractions.models.quay import QuayRepo, QuayTag

from signtractions.tractions.containers import (
    ParseCotainerImageReference,
    PopulateContainerDigest,
    STMDParseContainerImageReference,
    ContainerParts,
    GetQuayRepositories,
    GetQuayTags,
    GetContainerImageTags,
)


def test_parse_container_image_reference_tag():
    t = ParseCotainerImageReference(
        uid="test",
        i_container_image_reference="quay.io/containers/podman:latest",
    )
    t.run()
    assert t.o_container_parts.registry == "quay.io"
    assert t.o_container_parts.image == "containers/podman"
    assert t.o_container_parts.tag == "latest"
    assert t.o_container_parts.digests == TList[str]([])
    assert t.o_container_parts.arches == TList[str]([])


def test_parse_container_image_reference_digest():
    t = ParseCotainerImageReference(
        uid="test",
        i_container_image_reference=Port[str](data="quay.io/containers/podman@sha256:123456"),
    )
    t.run()
    assert t.o_container_parts.registry == "quay.io"
    assert t.o_container_parts.image == "containers/podman"
    assert t.o_container_parts.tag is None
    assert t.o_container_parts.digests == TList[str](["sha256:123456"])
    assert t.o_container_parts.arches == TList[str]([""])


def test_parse_container_image_reference_stmd_tag():
    t = STMDParseContainerImageReference(
        uid="test",
        i_container_image_reference=Port[TList[str]](
            data=TList[str](
                [
                    "quay.io/containers/podman:latest",
                    "quay.io/containers/podman:greatest",
                ]
            )
        ),
        a_executor=Port[LoopExecutor](data=LoopExecutor()),
    )
    t.run()
    assert t.o_container_parts == TList[ContainerParts](
        [
            ContainerParts(
                registry="quay.io",
                image="containers/podman",
                tag="latest",
                digests=TList[str]([]),
                arches=TList[str]([]),
            ),
            ContainerParts(
                registry="quay.io",
                image="containers/podman",
                tag="greatest",
                digests=TList[str]([]),
                arches=TList[str]([]),
            ),
        ]
    )


def test_populate_container_digest_manifest_not_found():
    fqc = FakeQuayClient(
        username="test",
        password="test",
        host="test",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
        fake_repositories=TDict[str, TDict[str, QuayRepo]].content_from_json({}),
        fake_tags=TDict[str, TDict[str, TList[QuayTag]]].content_from_json({}),
    )
    t = PopulateContainerDigest(
        uid="test",
        i_container_parts=Port[ContainerParts](
            data=ContainerParts(
                registry="quay.io",
                image="containers/podman",
                tag="latest",
                digests=TList[str]([]),
                arches=TList[str]([]),
            )
        ),
        r_quay_client=fqc,
    )
    with pytest.raises(ManifestNotFoundError):
        t.run()


def test_populate_container_digest_manifest(fix_manifest_v2s2):
    fqc = FakeQuayClient(
        username="test",
        password="test",
        host="test",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
        fake_repositories=TDict[str, TDict[str, QuayRepo]].content_from_json({}),
        fake_tags=TDict[str, TDict[str, TList[QuayTag]]].content_from_json({}),
    )
    fqc.populate_manifest(
        "quay.io/containers/podman:latest",
        "application/vnd.docker.distribution.manifest.v2+json",
        {},
        json.dumps(fix_manifest_v2s2),
    )

    t = PopulateContainerDigest(
        uid="test",
        i_container_parts=Port[ContainerParts](
            data=ContainerParts(
                registry="quay.io",
                image="containers/podman",
                tag="latest",
                digests=TList[str]([]),
                arches=TList[str]([]),
            )
        ),
        r_quay_client=fqc,
    )
    t.run()
    assert t.o_container_parts.registry == "quay.io"
    assert t.o_container_parts.image == "containers/podman"
    assert t.o_container_parts.tag == "latest"
    assert t.o_container_parts.digests == TList[str](
        ["sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d"]
    )


def test_populate_container_digest_manifest_list(fix_manifest_list):
    fqc = FakeQuayClient(
        username="test",
        password="test",
        host="test",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
        fake_repositories=TDict[str, TDict[str, QuayRepo]].content_from_json({}),
        fake_tags=TDict[str, TDict[str, TList[QuayTag]]].content_from_json({}),
    )
    fqc.populate_manifest(
        "quay.io/containers/podman:latest",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        {},
        json.dumps(fix_manifest_list),
    )

    t = PopulateContainerDigest(
        uid="test",
        i_container_parts=Port[ContainerParts](
            data=ContainerParts(
                registry="quay.io",
                image="containers/podman",
                tag="latest",
                digests=TList[str]([]),
                arches=TList[str]([]),
            )
        ),
        r_quay_client=fqc,
    )
    t.run()
    assert t.o_container_parts.registry == "quay.io"
    assert t.o_container_parts.image == "containers/podman"
    assert t.o_container_parts.tag == "latest"
    assert t.o_container_parts.digests == TList[str](
        [
            "sha256:2e8f38a0a8d2a450598430fa70c7f0b53aeec991e76c3e29c63add599b4ef7ee",
            "sha256:b3f9218fb5839763e62e52ee6567fe331aa1f3c644f9b6f232ff23959257acf9",
            "sha256:496fb0ff2057c79254c9dc6ba999608a98219c5c93142569a547277c679e532c",
            "sha256:146ab6fa7ba3ab4d154b09c1c5522e4966ecd071bf23d1ba3df6c8b9fc33f8cb",
            "sha256:bbef1f46572d1f33a92b53b0ba0ed5a1d09dab7ffe64be1ae3ae66e76275eabd",
            "sha256:d07476154b88059d730e260eba282b3c7a0b5e7feb620638d49070b71dcdcaf3",
        ]
    )


def test_populate_container_digest_manifest_list_by_digest(fix_manifest_list):
    fqc = FakeQuayClient(
        username="test",
        password="test",
        host="test",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
        fake_repositories=TDict[str, TDict[str, QuayRepo]].content_from_json({}),
        fake_tags=TDict[str, TDict[str, TList[QuayTag]]].content_from_json({}),
    )
    fqc.populate_manifest(
        "quay.io/containers/podman@sha256:2e8f38a0a8d2a450598430fa"
        "70c7f0b53aeec991e76c3e29c63add599b4ef7ee",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        {},
        json.dumps(fix_manifest_list),
    )

    t = PopulateContainerDigest(
        uid="test",
        i_container_parts=Port[ContainerParts](
            data=ContainerParts(
                registry="quay.io",
                image="containers/podman",
                tag="",
                digests=TList[str](
                    ["sha256:2e8f38a0a8d2a450598430fa70c7f0b53aeec991e76c3e29c63add599b4ef7ee"]
                ),
                arches=TList[str]([]),
            )
        ),
        r_quay_client=fqc,
    )
    t.run()
    assert t.o_container_parts.registry == "quay.io"
    assert t.o_container_parts.image == "containers/podman"
    assert t.o_container_parts.tag == ""
    assert t.o_container_parts.digests == TList[str](
        [
            "sha256:2e8f38a0a8d2a450598430fa70c7f0b53aeec991e76c3e29c63add599b4ef7ee",
            "sha256:b3f9218fb5839763e62e52ee6567fe331aa1f3c644f9b6f232ff23959257acf9",
            "sha256:496fb0ff2057c79254c9dc6ba999608a98219c5c93142569a547277c679e532c",
            "sha256:146ab6fa7ba3ab4d154b09c1c5522e4966ecd071bf23d1ba3df6c8b9fc33f8cb",
            "sha256:bbef1f46572d1f33a92b53b0ba0ed5a1d09dab7ffe64be1ae3ae66e76275eabd",
            "sha256:d07476154b88059d730e260eba282b3c7a0b5e7feb620638d49070b71dcdcaf3",
        ]
    )


def test_get_quay_repositories(fix_manifest_list):
    fqc = FakeQuayClient(
        username="test",
        password="test",
        host="test",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
        fake_repositories=TDict[str, TDict[str, QuayRepo]].content_from_json({}),
        fake_tags=TDict[str, TDict[str, TList[QuayTag]]].content_from_json({}),
    )
    test_repo = QuayRepo(
        namespace="test_namespace",
        name="test_repository",
        description=None,
        is_public=False,
        kind="image",
        state="NORMAL",
        is_starred=False,
        quota_report=TDict[str, Optional[int]]({"quota_bytes": 0, "configured_quota": None}),
    )
    fqc.populate_repository("test_namespace", "test_repository", test_repo)

    t = GetQuayRepositories(
        uid="test",
        i_namespace="test_namespace",
        r_quay_client=fqc,
    )
    t.run()
    assert t.o_repositories == TList[QuayRepo]([test_repo])


def test_get_quay_tags(fix_manifest_list):
    fqc = FakeQuayClient(
        username="test",
        password="test",
        host="test",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
        fake_repositories=TDict[str, TDict[str, QuayRepo]].content_from_json({}),
        fake_tags=TDict[str, TDict[str, TList[QuayTag]]].content_from_json({}),
    )
    tag = QuayTag(
        name="t1",
        reversion=False,
        start_ts=0,
        manifest_digest="sha256:123456",
        is_manifest_list=False,
        size=None,
        last_modified="",
        end_ts=0,
        expiration=None,
    )
    fqc.populate_tags("test_namespace", "test_repository", TList[QuayTag]([tag]))

    t = GetQuayTags(
        uid="test",
        i_repository="test_namespace/test_repository",
        r_quay_client=fqc,
    )
    t.run()
    assert t.o_tags == TList[QuayTag]([tag])


def test_get_container_image_tags(fix_manifest_list):
    fqc = FakeQuayClient(
        username="test",
        password="test",
        host="test",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
        fake_repositories=TDict[str, TDict[str, QuayRepo]].content_from_json({}),
        fake_tags=TDict[str, TDict[str, TList[QuayTag]]].content_from_json({}),
    )
    tag = QuayTag(
        name="t1",
        reversion=False,
        start_ts=0,
        manifest_digest="sha256:123456",
        is_manifest_list=False,
        size=None,
        last_modified="",
        end_ts=0,
        expiration=None,
    )
    fqc.populate_tags("test_namespace", "test_repository", TList[QuayTag]([tag]))
    t = GetContainerImageTags(
        uid="test",
        i_container_image_repo="registry.com/test_namespace/test_repository",
        i_container_image_repo_identities=TList[str](["identity-registry.com"]),
        r_quay_client=fqc,
    )
    t.run()
    assert t.o_container_references == TList[str](
        ["registry.com/test_namespace/test_repository:t1"]
    )
    assert t.o_container_identities == TList[str](["identity-registry.com/test_repository:t1"])
