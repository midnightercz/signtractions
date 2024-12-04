import json
from typing import Union

import pytest
from pytractions.base import Port, TDict, TList
from pytractions.executor import LoopExecutor

from signtractions.tractors.t_sign_snapshot import SignSnapshot
from signtractions.resources.signing_wrapper import CosignSignerSettings
from signtractions.models.signing import SignEntry
from signtractions.models.quay import QuayRepo, QuayTag

from signtractions.resources.fake_signing_wrapper import FakeCosignSignerWrapper, FakeEPRunArgs
from signtractions.resources.fake_quay_client import FakeQuayClient


@pytest.fixture
def fake_cosign_wrapper():
    return FakeCosignSignerWrapper(
        config_file="test",
        settings=CosignSignerSettings(),
        fake_entry_point_requests=TList[FakeEPRunArgs]([]),
        fake_entry_point_returns=TList[TDict[str, TDict[str, str]]]([]),
        fake_entry_point_runs=TList[FakeEPRunArgs]([]),
    )


@pytest.fixture
def fake_quay_client():
    return FakeQuayClient(
        username="user",
        password="pass",
        host="quay.io",
        fake_manifests=TDict[str, TDict[str, str]].content_from_json({}),
        fake_repositories=TDict[str, TDict[str, QuayRepo]].content_from_json({}),
        fake_tags=TDict[str, TDict[str, TList[QuayTag]]].content_from_json({}),
    )


def test_sign_snapshot(fix_manifest_v2s2, fix_snapshot_str, fake_cosign_wrapper, fake_quay_client):
    fake_quay_client.populate_manifest(
        "quay.io/containers/podman:latest",
        "application/vnd.docker.distribution.manifest.v2+json",
        False,
        json.dumps(fix_manifest_v2s2),
    )
    fake_quay_client.populate_manifest(
        "quay.io/containers/podman:1.0",
        "application/vnd.docker.distribution.manifest.v2+json",
        False,
        json.dumps(fix_manifest_v2s2),
    )
    fake_cosign_wrapper.fake_entry_point_requests.append(
        FakeEPRunArgs(
            args=TList[str]([]),
            kwargs=TDict[str, Union[str, TList[str]]].content_from_json(
                {
                    "config_file": "test",
                    "digest": [
                        "sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
                        "sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
                    ],
                    "reference": [
                        "quay.io/containers/podman:latest",
                        "quay.io/containers/podman:1.0",
                    ],
                    "identity": [
                        "quay.io/containers/podman:latest",
                        "quay.io/containers/podman:1.0",
                    ],
                    "signing_key": "signing_key",
                }
            ),
        )
    )
    fake_cosign_wrapper.fake_entry_point_returns.append(
        TDict[str, TDict[str, str]].content_from_json({"signer_result": {"status": "ok"}})
    )
    t = SignSnapshot(
        uid="test",
        a_executor=Port[LoopExecutor](data=LoopExecutor()),
        r_dst_quay_client=fake_quay_client,
        r_signer_wrapper_cosign=fake_cosign_wrapper,
        i_task_id=Port[int](data=1),
        i_snapshot_str=Port[str](data=fix_snapshot_str),
        i_signing_key=Port[str](data="signing_key"),
    )
    t.run()
    assert len(t.o_sign_entries) == 2
    assert t.o_sign_entries[0] == SignEntry(
        reference="quay.io/containers/podman:latest",
        identity="quay.io/containers/podman:latest",
        repo="containers/podman",
        digest="sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
        arch="",
        signing_key="signing_key",
    )
    assert t.o_sign_entries[0] == SignEntry(
        reference="quay.io/containers/podman:latest",
        identity="quay.io/containers/podman:latest",
        repo="containers/podman",
        digest="sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
        arch="",
        signing_key="signing_key",
    )


def test_sign_snapshot_file(
    fix_manifest_v2s2, fix_snapshot_file, fake_cosign_wrapper, fake_quay_client
):
    fake_quay_client.populate_manifest(
        "quay.io/containers/podman:latest",
        "application/vnd.docker.distribution.manifest.v2+json",
        False,
        json.dumps(fix_manifest_v2s2),
    )
    fake_quay_client.populate_manifest(
        "quay.io/containers/podman:1.0",
        "application/vnd.docker.distribution.manifest.v2+json",
        False,
        json.dumps(fix_manifest_v2s2),
    )
    fake_cosign_wrapper.fake_entry_point_requests.append(
        FakeEPRunArgs(
            args=TList[str]([]),
            kwargs=TDict[str, Union[str, TList[str]]].content_from_json(
                {
                    "config_file": "test",
                    "digest": [
                        "sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
                        "sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
                    ],
                    "reference": [
                        "quay.io/containers/podman:latest",
                        "quay.io/containers/podman:1.0",
                    ],
                    "identity": [
                        "quay.io/containers/podman:latest",
                        "quay.io/containers/podman:1.0",
                    ],
                    "signing_key": "signing_key",
                }
            ),
        )
    )
    fake_cosign_wrapper.fake_entry_point_returns.append(
        TDict[str, TDict[str, str]].content_from_json({"signer_result": {"status": "ok"}})
    )

    t = SignSnapshot(
        uid="test",
        a_executor=Port[LoopExecutor](data=LoopExecutor()),
        r_dst_quay_client=fake_quay_client,
        r_signer_wrapper_cosign=fake_cosign_wrapper,
        i_task_id=Port[int](data=1),
        i_snapshot_file=Port[str](data=fix_snapshot_file),
        i_signing_key=Port[str](data="signing_key"),
    )
    t.run()
    assert len(t.o_sign_entries) == 2
    assert t.o_sign_entries[0] == SignEntry(
        reference="quay.io/containers/podman:latest",
        identity="quay.io/containers/podman:latest",
        repo="containers/podman",
        digest="sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
        arch="",
        signing_key="signing_key",
    )
    assert t.o_sign_entries[0] == SignEntry(
        reference="quay.io/containers/podman:latest",
        identity="quay.io/containers/podman:latest",
        repo="containers/podman",
        digest="sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
        arch="",
        signing_key="signing_key",
    )
