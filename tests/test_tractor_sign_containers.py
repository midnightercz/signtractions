import json
from typing import Union

import pytest
from pytractions.base import TList, TDict, Res, Arg, In

from signtractions.tractors.t_sign_containers import SignContainers
from signtractions.resources.signing_wrapper import SignerWrapperSettings
from signtractions.models.containers import ContainerParts
from signtractions.models.signing import SignEntry

from signtractions.resources.fake_signing_wrapper import FakeCosignSignerWrapper, FakeEPRunArgs
from signtractions.resources.fake_quay_client import FakeQuayClient


@pytest.fixture
def fake_cosign_wrapper():
    return FakeCosignSignerWrapper(
        config_file="test",
        settings=SignerWrapperSettings(),
        entry_point_requests=TList[FakeEPRunArgs]([]),
        entry_point_returns=TList[TDict[str, TDict[str, str]]]([]),
        entry_point_runs=TList[FakeEPRunArgs]([]),
    )


@pytest.fixture
def fake_quay_client():
    return FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        manifests=TDict[str, TDict[str, str]].content_from_json({}),
    )


def test_sign_containers_tags(fix_manifest_v2s2, fake_cosign_wrapper, fake_quay_client):
    fake_quay_client.populate_manifest(
        "quay.io/namespace/image:1",
        "application/vnd.docker.distribution.manifest.v2+json",
        False,
        json.dumps(fix_manifest_v2s2),
    )
    fake_cosign_wrapper.entry_point_requests.append(
        FakeEPRunArgs(
            args=TList[str]([]),
            kwargs=TDict[str, Union[str, TList[str]]].content_from_json(
                {
                    "config_file": "test",
                    "digest": TList[str](
                        ["sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d"]
                    ),
                    "reference": TList[str](["quay.io/namespace/image:1"]),
                    "signing_key": "signing_key",
                },
            ),
        )
    )
    fake_cosign_wrapper.entry_point_returns.append(
        TDict[str, TDict[str, str]].content_from_json({"signer_result": {"status": "ok"}})
    )

    t = SignContainers(
        uid="test",
        r_signer_wrapper_cosign=Res[FakeCosignSignerWrapper](r=fake_cosign_wrapper),
        a_pool_size=Arg[int](a=1),
        r_dst_quay_client=Res[FakeQuayClient](r=fake_quay_client),
        i_task_id=In[int](data=1),
        i_signing_keys=In[TList[str]](data=TList[str](["signing_key"])),
        i_container_image_references=In[TList[str]](data=TList[str](["quay.io/namespace/image:1"])),
    )
    t.run()
    assert len(t.tractions["t_parse_container_references"].o_container_parts.data) == 1
    assert t.tractions["t_parse_container_references"].o_container_parts.data[0] == ContainerParts(
        registry="quay.io",
        image="namespace/image",
        tag="1",
        digests=TList[str](),
        arches=TList[str](),
    )
    assert len(t.tractions["t_populate_digests"].o_container_parts.data) == 1
    assert t.tractions["t_populate_digests"].o_container_parts.data[0] == ContainerParts(
        registry="quay.io",
        image="namespace/image",
        tag="1",
        digests=TList[str](
            ["sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d"]
        ),
        arches=TList[str]([""]),
    )
    assert t.tractions["t_sign_entries_from_push_item"].o_sign_entries.data[0][0] == SignEntry(
        reference="quay.io/namespace/image:1",
        repo="namespace/image",
        digest="sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
        arch="",
        signing_key="signing_key",
    )
    assert t.o_sign_entries.data[0] == SignEntry(
        reference="quay.io/namespace/image:1",
        repo="namespace/image",
        digest="sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
        arch="",
        signing_key="signing_key",
    )


def test_sign_containers_tags_ml(fix_manifest_list, fake_cosign_wrapper, fake_quay_client):
    fake_quay_client.populate_manifest(
        "quay.io/namespace/image:1",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        False,
        json.dumps(fix_manifest_list),
    )
    fake_cosign_wrapper.entry_point_requests.append(
        FakeEPRunArgs(
            args=TList[str]([]),
            kwargs=TDict[str, Union[str, TList[str]]].content_from_json(
                {
                    "config_file": "test",
                    "digest": [
                        "sha256:2e8f38a0a8d2a450598430fa70c7f0b53aeec991e76c3e29c63add599b4ef7ee",
                        "sha256:b3f9218fb5839763e62e52ee6567fe331aa1f3c644f9b6f232ff23959257acf9",
                        "sha256:496fb0ff2057c79254c9dc6ba999608a98219c5c93142569a547277c679e532c",
                        "sha256:146ab6fa7ba3ab4d154b09c1c5522e4966ecd071bf23d1ba3df6c8b9fc33f8cb",
                        "sha256:bbef1f46572d1f33a92b53b0ba0ed5a1d09dab7ffe64be1ae3ae66e76275eabd",
                        "sha256:d07476154b88059d730e260eba282b3c7a0b5e7feb620638d49070b71dcdcaf3",
                    ],
                    "reference": [
                        "quay.io/namespace/image:1",
                        "quay.io/namespace/image:1",
                        "quay.io/namespace/image:1",
                        "quay.io/namespace/image:1",
                        "quay.io/namespace/image:1",
                        "quay.io/namespace/image:1",
                    ],
                    "signing_key": "signing_key",
                }
            ),
        )
    )
    fake_cosign_wrapper.entry_point_returns.append(
        TDict[str, TDict[str, str]].content_from_json({"signer_result": {"status": "ok"}})
    )

    t = SignContainers(
        uid="test",
        r_signer_wrapper_cosign=Res[FakeCosignSignerWrapper](r=fake_cosign_wrapper),
        r_dst_quay_client=Res[FakeQuayClient](r=fake_quay_client),
        i_task_id=In[int](data=1),
        a_pool_size=Arg[int](a=1),
        i_signing_keys=In[TList[str]](data=TList[str](["signing_key"])),
        i_container_image_references=In[TList[str]](data=TList[str](["quay.io/namespace/image:1"])),
    )
    t.run()
    assert len(t.tractions["t_parse_container_references"].o_container_parts.data) == 1
    assert t.tractions["t_parse_container_references"].o_container_parts.data[0] == ContainerParts(
        registry="quay.io",
        image="namespace/image",
        tag="1",
        digests=TList[str](),
        arches=TList[str](),
    )
    assert len(t.tractions["t_populate_digests"].o_container_parts.data) == 1
    assert t.tractions["t_populate_digests"].o_container_parts.data[0] == ContainerParts(
        registry="quay.io",
        image="namespace/image",
        tag="1",
        digests=TList[str](
            [
                "sha256:2e8f38a0a8d2a450598430fa70c7f0b53aeec991e76c3e29c63add599b4ef7ee",
                "sha256:b3f9218fb5839763e62e52ee6567fe331aa1f3c644f9b6f232ff23959257acf9",
                "sha256:496fb0ff2057c79254c9dc6ba999608a98219c5c93142569a547277c679e532c",
                "sha256:146ab6fa7ba3ab4d154b09c1c5522e4966ecd071bf23d1ba3df6c8b9fc33f8cb",
                "sha256:bbef1f46572d1f33a92b53b0ba0ed5a1d09dab7ffe64be1ae3ae66e76275eabd",
                "sha256:d07476154b88059d730e260eba282b3c7a0b5e7feb620638d49070b71dcdcaf3",
            ]
        ),
        arches=TList[str](["amd64", "arm64", "arm", "ppc64le", "s390x", "multiarch"]),
    )
    assert len(t.tractions["t_sign_entries_from_push_item"].o_sign_entries.data[0]) == 6
    assert t.tractions["t_sign_entries_from_push_item"].o_sign_entries.data[0] == TList[SignEntry](
        [
            SignEntry(
                reference="quay.io/namespace/image:1",
                repo="namespace/image",
                digest="sha256:2e8f38a0a8d2a450598430fa70c7f0b53a" "eec991e76c3e29c63add599b4ef7ee",
                arch="amd64",
                signing_key="signing_key",
            ),
            SignEntry(
                reference="quay.io/namespace/image:1",
                repo="namespace/image",
                digest="sha256:b3f9218fb5839763e62e52ee6567fe331a" "a1f3c644f9b6f232ff23959257acf9",
                arch="arm64",
                signing_key="signing_key",
            ),
            SignEntry(
                reference="quay.io/namespace/image:1",
                repo="namespace/image",
                digest="sha256:496fb0ff2057c79254c9dc6ba999608a982" "19c5c93142569a547277c679e532c",
                arch="arm",
                signing_key="signing_key",
            ),
            SignEntry(
                reference="quay.io/namespace/image:1",
                repo="namespace/image",
                digest="sha256:146ab6fa7ba3ab4d154b09c1c5522e4966e" "cd071bf23d1ba3df6c8b9fc33f8cb",
                arch="ppc64le",
                signing_key="signing_key",
            ),
            SignEntry(
                reference="quay.io/namespace/image:1",
                repo="namespace/image",
                digest="sha256:bbef1f46572d1f33a92b53b0ba0ed5a1d09d" "ab7ffe64be1ae3ae66e76275eabd",
                arch="s390x",
                signing_key="signing_key",
            ),
            SignEntry(
                reference="quay.io/namespace/image:1",
                repo="namespace/image",
                digest="sha256:d07476154b88059d730e260eba282b3c7a0b" "5e7feb620638d49070b71dcdcaf3",
                arch="multiarch",
                signing_key="signing_key",
            ),
        ]
    )


def test_sign_containers_digests(fix_manifest_v2s2, fake_cosign_wrapper, fake_quay_client):
    fake_quay_client.populate_manifest(
        "quay.io/namespace/image@sha256:6ef06d8c90c863ba4eb4297f10"
        "73ba8cb28c1f6570e2206cdaad2084e2a4715d",
        "application/vnd.docker.distribution.manifest.v2+json",
        False,
        json.dumps(fix_manifest_v2s2),
    )
    fake_cosign_wrapper.entry_point_requests.append(
        FakeEPRunArgs(
            args=TList[str]([]),
            kwargs=TDict[str, Union[str, TList[str]]].content_from_json(
                {
                    "config_file": "test",
                    "digest": [
                        "sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d"
                    ],
                    "reference": [None],
                    "signing_key": "signing_key",
                }
            ),
        )
    )
    fake_cosign_wrapper.entry_point_returns.append(
        TDict[str, TDict[str, str]].content_from_json({"signer_result": {"status": "ok"}})
    )

    t = SignContainers(
        uid="test",
        r_signer_wrapper_cosign=Res[FakeCosignSignerWrapper](r=fake_cosign_wrapper),
        a_pool_size=Arg[int](a=1),
        r_dst_quay_client=Res[FakeQuayClient](r=fake_quay_client),
        i_task_id=In[int](data=1),
        i_signing_keys=In[TList[str]](data=TList[str](["signing_key"])),
        i_container_image_references=In[TList[str]](
            data=TList[str](
                [
                    "quay.io/namespace/image@sha256:6ef06d8c90c863ba4eb4297f1073ba8c"
                    "b28c1f6570e2206cdaad2084e2a4715d"
                ]
            )
        ),
    )
    t.run()
    assert len(t.tractions["t_parse_container_references"].o_container_parts.data) == 1
    assert t.tractions["t_parse_container_references"].o_container_parts.data[0] == ContainerParts(
        registry="quay.io",
        image="namespace/image",
        tag=None,
        digests=TList[str](
            ["sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d"]
        ),
        arches=TList[str]([""]),
    )
    assert len(t.tractions["t_populate_digests"].o_container_parts.data) == 1
    assert t.tractions["t_populate_digests"].o_container_parts.data[0] == ContainerParts(
        registry="quay.io",
        image="namespace/image",
        tag=None,
        digests=TList[str](
            ["sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d"]
        ),
        arches=TList[str]([""]),
    )
    assert t.tractions["t_sign_entries_from_push_item"].o_sign_entries.data[0][0] == SignEntry(
        reference=None,
        repo="namespace/image",
        digest="sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
        arch="",
        signing_key="signing_key",
    )
    assert t.o_sign_entries.data[0] == SignEntry(
        reference=None,
        repo="namespace/image",
        digest="sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
        arch="",
        signing_key="signing_key",
    )


def test_sign_containers_digests_ml(fix_manifest_list, fake_cosign_wrapper, fake_quay_client):
    fake_quay_client.populate_manifest(
        "quay.io/namespace/image@sha256:d07476154b88059d730e260eba282b3c"
        "7a0b5e7feb620638d49070b71dcdcaf3",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        False,
        json.dumps(fix_manifest_list),
    )
    fake_cosign_wrapper.entry_point_requests.append(
        FakeEPRunArgs(
            args=TList[str]([]),
            kwargs=TDict[str, Union[str, TList[str]]].content_from_json(
                {
                    "config_file": "test",
                    "digest": [
                        "sha256:2e8f38a0a8d2a450598430fa70c7f0b53aeec991e76c3e29c63add599b4ef7ee",
                        "sha256:b3f9218fb5839763e62e52ee6567fe331aa1f3c644f9b6f232ff23959257acf9",
                        "sha256:496fb0ff2057c79254c9dc6ba999608a98219c5c93142569a547277c679e532c",
                        "sha256:146ab6fa7ba3ab4d154b09c1c5522e4966ecd071bf23d1ba3df6c8b9fc33f8cb",
                        "sha256:bbef1f46572d1f33a92b53b0ba0ed5a1d09dab7ffe64be1ae3ae66e76275eabd",
                        "sha256:d07476154b88059d730e260eba282b3c7a0b5e7feb620638d49070b71dcdcaf3",
                    ],
                    "reference": [None, None, None, None, None, None],
                    "signing_key": "signing_key",
                }
            ),
        )
    )
    fake_cosign_wrapper.entry_point_returns.append(
        TDict[str, TDict[str, str]]({"signer_result": TDict[str, str]({"status": "ok"})})
    )

    t = SignContainers(
        uid="test",
        r_signer_wrapper_cosign=Res[FakeCosignSignerWrapper](r=fake_cosign_wrapper),
        r_dst_quay_client=Res[FakeQuayClient](r=fake_quay_client),
        i_task_id=In[int](data=1),
        a_pool_size=Arg[int](a=1),
        i_signing_keys=In[TList[str]](data=TList[str](["signing_key"])),
        i_container_image_references=In[TList[str]](
            data=TList[str](
                [
                    "quay.io/namespace/image@sha256:d07476154b88059d730e260eba"
                    "282b3c7a0b5e7feb620638d49070b71dcdcaf3"
                ]
            )
        ),
    )
    t.run()
    assert len(t.tractions["t_parse_container_references"].o_container_parts.data) == 1
    assert t.tractions["t_parse_container_references"].o_container_parts.data[0] == ContainerParts(
        registry="quay.io",
        image="namespace/image",
        tag=None,
        digests=TList[str](
            ["sha256:d07476154b88059d730e260eba282b3c7a0b5e7feb620638d49070b71dcdcaf3"]
        ),
        arches=TList[str]([""]),
    )
    assert len(t.tractions["t_populate_digests"].o_container_parts.data) == 1
    assert t.tractions["t_populate_digests"].o_container_parts.data[0] == ContainerParts(
        registry="quay.io",
        image="namespace/image",
        tag=None,
        digests=TList[str](
            [
                "sha256:2e8f38a0a8d2a450598430fa70c7f0b53aeec991e76c3e29c63add599b4ef7ee",
                "sha256:b3f9218fb5839763e62e52ee6567fe331aa1f3c644f9b6f232ff23959257acf9",
                "sha256:496fb0ff2057c79254c9dc6ba999608a98219c5c93142569a547277c679e532c",
                "sha256:146ab6fa7ba3ab4d154b09c1c5522e4966ecd071bf23d1ba3df6c8b9fc33f8cb",
                "sha256:bbef1f46572d1f33a92b53b0ba0ed5a1d09dab7ffe64be1ae3ae66e76275eabd",
                "sha256:d07476154b88059d730e260eba282b3c7a0b5e7feb620638d49070b71dcdcaf3",
            ]
        ),
        arches=TList[str](["amd64", "arm64", "arm", "ppc64le", "s390x", "multiarch"]),
    )
    assert len(t.tractions["t_sign_entries_from_push_item"].o_sign_entries.data[0]) == 6
    assert t.tractions["t_sign_entries_from_push_item"].o_sign_entries.data[0] == TList[SignEntry](
        [
            SignEntry(
                reference=None,
                repo="namespace/image",
                digest="sha256:2e8f38a0a8d2a450598430fa70c7f0b53aeec99" "1e76c3e29c63add599b4ef7ee",
                arch="amd64",
                signing_key="signing_key",
            ),
            SignEntry(
                reference=None,
                repo="namespace/image",
                digest="sha256:b3f9218fb5839763e62e52ee6567fe331aa1f3c644" "f9b6f232ff23959257acf9",
                arch="arm64",
                signing_key="signing_key",
            ),
            SignEntry(
                reference=None,
                repo="namespace/image",
                digest="sha256:496fb0ff2057c79254c9dc6ba999608a98219c5c93" "142569a547277c679e532c",
                arch="arm",
                signing_key="signing_key",
            ),
            SignEntry(
                reference=None,
                repo="namespace/image",
                digest="sha256:146ab6fa7ba3ab4d154b09c1c5522e4966ecd071bf" "23d1ba3df6c8b9fc33f8cb",
                arch="ppc64le",
                signing_key="signing_key",
            ),
            SignEntry(
                reference=None,
                repo="namespace/image",
                digest="sha256:bbef1f46572d1f33a92b53b0ba0ed5a1d09dab7ffe6" "4be1ae3ae66e76275eabd",
                arch="s390x",
                signing_key="signing_key",
            ),
            SignEntry(
                reference=None,
                repo="namespace/image",
                digest="sha256:d07476154b88059d730e260eba282" "b3c7a0b5e7feb620638d49070b71dcdcaf3",
                arch="multiarch",
                signing_key="signing_key",
            ),
        ]
    )
