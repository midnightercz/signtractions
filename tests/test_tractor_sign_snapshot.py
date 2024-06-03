import json

import pytest
from pytractions.base import Res, Arg, In, STMDExecutorType

from signtractions.tractors.t_sign_snapshot import SignSnapshot
from signtractions.resources.signing_wrapper import SignerWrapperSettings
from signtractions.models.signing import SignEntry

from signtractions.resources.fake_signing_wrapper import FakeCosignSignerWrapper
from signtractions.resources.fake_quay_client import FakeQuayClient


@pytest.fixture
def fake_cosign_wrapper():
    return FakeCosignSignerWrapper(config_file="test", settings=SignerWrapperSettings())


@pytest.fixture
def fake_quay_client():
    return FakeQuayClient(username="user", password="pass", host="quay.io")


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
    fake_cosign_wrapper._entry_point_returns[
        (
            (),
            '{"config_file": "test",'
            ' "digest": ["sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",'
            ' "sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d"],'
            ' "reference": ["quay.io/containers/podman:latest", "quay.io/containers/podman:1.0"],'
            ' "signing_key": "signing_key"}',
        )
    ] = {"signer_result": {"status": "ok"}}

    t = SignSnapshot(
        uid="test",
        a_pool_size=Arg[int](a=1),
        a_executor_type=Arg[STMDExecutorType](a=STMDExecutorType.LOCAL),
        r_dst_quay_client=Res[FakeQuayClient](r=fake_quay_client),
        r_signer_wrapper_cosign=Res[FakeCosignSignerWrapper](r=fake_cosign_wrapper),
        i_task_id=In[int](data=1),
        i_snapshot_str=In[str](data=fix_snapshot_str),
        i_signing_key=In[str](data="signing_key"),
    )
    t.run()
    assert len(t.o_sign_entries.data) == 2
    assert t.o_sign_entries.data[0] == SignEntry(
        reference="quay.io/containers/podman:latest",
        repo="containers/podman",
        digest="sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
        arch="",
        signing_key="signing_key",
    )
    assert t.o_sign_entries.data[0] == SignEntry(
        reference="quay.io/containers/podman:latest",
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
    fake_cosign_wrapper._entry_point_returns[
        (
            (),
            '{"config_file": "test",'
            ' "digest": ["sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",'
            ' "sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d"],'
            ' "reference": ["quay.io/containers/podman:latest", "quay.io/containers/podman:1.0"],'
            ' "signing_key": "signing_key"}',
        )
    ] = {"signer_result": {"status": "ok"}}

    t = SignSnapshot(
        uid="test",
        a_pool_size=Arg[int](a=1),
        a_executor_type=Arg[STMDExecutorType](a=STMDExecutorType.LOCAL),
        r_dst_quay_client=Res[FakeQuayClient](r=fake_quay_client),
        r_signer_wrapper_cosign=Res[FakeCosignSignerWrapper](r=fake_cosign_wrapper),
        i_task_id=In[int](data=1),
        i_snapshot_file=In[str](data=fix_snapshot_file),
        i_signing_key=In[str](data="signing_key"),
    )
    t.run()
    assert len(t.o_sign_entries.data) == 2
    assert t.o_sign_entries.data[0] == SignEntry(
        reference="quay.io/containers/podman:latest",
        repo="containers/podman",
        digest="sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
        arch="",
        signing_key="signing_key",
    )
    assert t.o_sign_entries.data[0] == SignEntry(
        reference="quay.io/containers/podman:latest",
        repo="containers/podman",
        digest="sha256:6ef06d8c90c863ba4eb4297f1073ba8cb28c1f6570e2206cdaad2084e2a4715d",
        arch="",
        signing_key="signing_key",
    )
