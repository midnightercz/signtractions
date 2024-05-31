import json
import pytest

from pytractions.base import Arg, In, TList, STMDExecutorType, Res

from signtractions.resources.fake_quay_client import FakeQuayClient, ManifestNotFoundError

from signtractions.tractions.containers import (
    ParseCotainerImageReference,
    PopulateContainerDigest,
    STMDParseContainerImageReference,
    ContainerParts,
)


def test_parse_container_image_reference_tag():
    t = ParseCotainerImageReference(
        uid="test",
        i_container_image_reference=In[str](data="quay.io/containers/podman:latest"),
    )
    t.run()
    assert t.o_container_parts.data.registry == "quay.io"
    assert t.o_container_parts.data.image == "containers/podman"
    assert t.o_container_parts.data.tag == "latest"
    assert t.o_container_parts.data.digests == TList[str]([])
    assert t.o_container_parts.data.arches == TList[str]([])


def test_parse_container_image_reference_digest():
    t = ParseCotainerImageReference(
        uid="test",
        i_container_image_reference=In[str](data="quay.io/containers/podman@sha256:123456"),
    )
    t.run()
    assert t.o_container_parts.data.registry == "quay.io"
    assert t.o_container_parts.data.image == "containers/podman"
    assert t.o_container_parts.data.tag is None
    assert t.o_container_parts.data.digests == TList[str](["sha256:123456"])
    assert t.o_container_parts.data.arches == TList[str]([""])


def test_parse_container_image_reference_stmd_tag():
    t = STMDParseContainerImageReference(
        uid="test",
        i_container_image_reference=In[TList[str]](
            data=[
                "quay.io/containers/podman:latest",
                "quay.io/containers/podman:greatest",
            ]
        ),
        a_executor_type=Arg[STMDExecutorType](a=STMDExecutorType.LOCAL),
        a_pool_size=Arg[int](a=1),
    )
    t.run()
    assert t.o_container_parts.data == TList[ContainerParts](
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
    fqc = FakeQuayClient(username="test", password="test", host="test")
    t = PopulateContainerDigest(
        uid="test",
        i_container_parts=In[ContainerParts](
            data=ContainerParts(
                registry="quay.io",
                image="containers/podman",
                tag="latest",
                digests=TList[str]([]),
                arches=TList[str]([]),
            )
        ),
        r_quay_client=Res[FakeQuayClient](r=fqc),
    )
    with pytest.raises(ManifestNotFoundError):
        t.run()


def test_populate_container_digest_manifest(fix_manifest_v2s2):
    fqc = FakeQuayClient(username="test", password="test", host="test")
    fqc.populate_manifest(
        "quay.io/containers/podman:latest",
        "application/vnd.docker.distribution.manifest.v2+json",
        {},
        json.dumps(fix_manifest_v2s2),
    )

    t = PopulateContainerDigest(
        uid="test",
        i_container_parts=In[ContainerParts](
            data=ContainerParts(
                registry="quay.io",
                image="containers/podman",
                tag="latest",
                digests=TList[str]([]),
                arches=TList[str]([]),
            )
        ),
        r_quay_client=Res[FakeQuayClient](r=fqc),
    )
    t.run()
    assert t.o_container_parts.data.registry == "quay.io"
    assert t.o_container_parts.data.image == "containers/podman"
    assert t.o_container_parts.data.tag == "latest"
    assert t.o_container_parts.data.digests == TList[str](
        ["sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d"]
    )


def test_populate_container_digest_manifest_list(fix_manifest_list):
    fqc = FakeQuayClient(username="test", password="test", host="test")
    fqc.populate_manifest(
        "quay.io/containers/podman:latest",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        {},
        json.dumps(fix_manifest_list),
    )

    t = PopulateContainerDigest(
        uid="test",
        i_container_parts=In[ContainerParts](
            data=ContainerParts(
                registry="quay.io",
                image="containers/podman",
                tag="latest",
                digests=TList[str]([]),
                arches=TList[str]([]),
            )
        ),
        r_quay_client=Res[FakeQuayClient](r=fqc),
    )
    t.run()
    assert t.o_container_parts.data.registry == "quay.io"
    assert t.o_container_parts.data.image == "containers/podman"
    assert t.o_container_parts.data.tag == "latest"
    assert t.o_container_parts.data.digests == TList[str](
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
    fqc = FakeQuayClient(username="test", password="test", host="test")
    fqc.populate_manifest(
        "quay.io/containers/podman@sha256:2e8f38a0a8d2a450598430fa"
        "70c7f0b53aeec991e76c3e29c63add599b4ef7ee",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        {},
        json.dumps(fix_manifest_list),
    )

    t = PopulateContainerDigest(
        uid="test",
        i_container_parts=In[ContainerParts](
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
        r_quay_client=Res[FakeQuayClient](r=fqc),
    )
    t.run()
    assert t.o_container_parts.data.registry == "quay.io"
    assert t.o_container_parts.data.image == "containers/podman"
    assert t.o_container_parts.data.tag == ""
    assert t.o_container_parts.data.digests == TList[str](
        [
            "sha256:2e8f38a0a8d2a450598430fa70c7f0b53aeec991e76c3e29c63add599b4ef7ee",
            "sha256:b3f9218fb5839763e62e52ee6567fe331aa1f3c644f9b6f232ff23959257acf9",
            "sha256:496fb0ff2057c79254c9dc6ba999608a98219c5c93142569a547277c679e532c",
            "sha256:146ab6fa7ba3ab4d154b09c1c5522e4966ecd071bf23d1ba3df6c8b9fc33f8cb",
            "sha256:bbef1f46572d1f33a92b53b0ba0ed5a1d09dab7ffe64be1ae3ae66e76275eabd",
            "sha256:d07476154b88059d730e260eba282b3c7a0b5e7feb620638d49070b71dcdcaf3",
        ]
    )
