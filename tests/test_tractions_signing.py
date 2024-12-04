import pytest
from typing import Union

from pytractions.base import Port, TList, TDict

from signtractions.resources.signing_wrapper import CosignSignerSettings
from signtractions.resources.cosign import FakeCosignClient
from signtractions.resources.fake_signing_wrapper import FakeCosignSignerWrapper, FakeEPRunArgs
from signtractions.tractions.signing import (
    SignEntriesFromContainerParts,
    SignEntry,
    ContainerParts,
    SignSignEntries,
    VerifyEntries,
)
from signtractions.resources.signing_wrapper import SigningError


def test_sign_entries_from_container_parts():
    t = SignEntriesFromContainerParts(
        uid="test",
        i_container_parts=Port[ContainerParts](
            data=ContainerParts(
                registry="quay.io",
                image="containers/podman",
                tag="latest",
                digests=TList[str](["sha256:123456", "sha256:123457"]),
                arches=TList[str](["amd64", "arm64"]),
            )
        ),
        i_signing_key=Port[str](data="signing_key"),
        i_container_identity=Port[str](data="quay.io/containers/podman:latest"),
    )
    t.run()
    assert t.o_sign_entries[0] == SignEntry(
        repo="containers/podman",
        reference="quay.io/containers/podman:latest",
        identity="quay.io/containers/podman:latest",
        digest="sha256:123456",
        arch="amd64",
        signing_key="signing_key",
    )
    assert t.o_sign_entries[1] == SignEntry(
        repo="containers/podman",
        reference="quay.io/containers/podman:latest",
        identity="quay.io/containers/podman:latest",
        digest="sha256:123457",
        arch="arm64",
        signing_key="signing_key",
    )


def test_sign_sign_entries():
    fsw = FakeCosignSignerWrapper(
        config_file="test",
        settings=CosignSignerSettings(),
        fake_entry_point_requests=TList[FakeEPRunArgs]([]),
        fake_entry_point_returns=TList[TDict[str, TDict[str, str]]]([]),
        fake_entry_point_runs=TList[FakeEPRunArgs]([]),
    )
    fsw.fake_entry_point_requests.append(
        FakeEPRunArgs(
            args=TList[str]([]),
            kwargs=TDict[str, Union[str, TList[str]]](
                {
                    "config_file": "test",
                    "signing_key": "signing_key",
                    "digest": TList[str](["sha256:123456"]),
                    "identity": TList[str](["quay.io/containers/podman:latest"]),
                    "reference": TList[str](["quay.io/containers/podman:latest"]),
                }
            ),
        )
    )
    fsw.fake_entry_point_returns.append(
        TDict[str, TDict[str, str]]({"signer_result": TDict[str, str]({"status": "ok"})})
    )
    t = SignSignEntries(
        uid="test",
        r_signer_wrapper=fsw,
        i_task_id=1,
        i_sign_entries=Port[TList[SignEntry]](
            data=TList[SignEntry](
                [
                    SignEntry(
                        repo="containers/podman",
                        reference="quay.io/containers/podman:latest",
                        identity="quay.io/containers/podman:latest",
                        digest="sha256:123456",
                        arch="amd64",
                        signing_key="signing_key",
                    )
                ]
            )
        ),
    )
    t.run()


def test_sign_sign_entries_dry_run():
    fsw = FakeCosignSignerWrapper(
        config_file="test",
        settings=CosignSignerSettings(),
        fake_entry_point_requests=TList[FakeEPRunArgs]([]),
        fake_entry_point_returns=TList[TDict[str, TDict[str, str]]]([]),
        fake_entry_point_runs=TList[FakeEPRunArgs]([]),
    )
    fsw.fake_entry_point_requests.append(
        FakeEPRunArgs(
            args=TList[str]([]),
            kwargs=TDict[str, Union[str, TList[str]]](
                {
                    "config_file": "test",
                    "signing_key": "signing_key",
                    "digest": TList[str](["sha256:123456"]),
                    "identity": TList[str](["quay.io/containers/podman:latest"]),
                    "reference": TList[str](["quay.io/containers/podman:latest"]),
                }
            ),
        )
    )
    fsw.fake_entry_point_returns.append(
        TDict[str, TDict[str, str]]({"signer_result": TDict[str, str]({"status": "ok"})})
    )
    t = SignSignEntries(
        uid="test",
        a_dry_run=True,
        r_signer_wrapper=fsw,
        i_task_id=1,
        i_sign_entries=Port[TList[SignEntry]](
            data=TList[SignEntry](
                [
                    SignEntry(
                        repo="containers/podman",
                        reference="quay.io/containers/podman:latest",
                        identity="quay.io/containers/podman:latest",
                        digest="sha256:123456",
                        arch="amd64",
                        signing_key="signing_key",
                    )
                ]
            )
        ),
    )
    t.run()


def test_sign_sign_entries_fail():
    fsw = FakeCosignSignerWrapper(
        config_file="test",
        settings=CosignSignerSettings(),
        fake_entry_point_requests=TList[FakeEPRunArgs]([]),
        fake_entry_point_returns=TList[TDict[str, TDict[str, str]]]([]),
        fake_entry_point_runs=TList[FakeEPRunArgs]([]),
    )
    fsw.fake_entry_point_requests.append(
        FakeEPRunArgs(
            args=TList[str]([]),
            kwargs=TDict[str, Union[str, TList[str]]].content_from_json(
                {
                    "config_file": "test",
                    "digest": TList[str](["sha256:123456"]),
                    "reference": TList[str](["quay.io/containers/podman:latest"]),
                    "identity": TList[str](["quay.io/containers/podman:latest"]),
                    "signing_key": "signing_key",
                }
            ),
        )
    )
    fsw.fake_entry_point_returns.append(
        TDict[str, TDict[str, str]].content_from_json(
            {"signer_result": {"status": "error", "error_message": "test error"}}
        )
    )
    t = SignSignEntries(
        uid="test",
        r_signer_wrapper=fsw,
        i_task_id=1,
        i_sign_entries=Port[TList[SignEntry]](
            data=TList[SignEntry](
                [
                    SignEntry(
                        repo="containers/podman",
                        identity="quay.io/containers/podman:latest",
                        reference="quay.io/containers/podman:latest",
                        digest="sha256:123456",
                        arch="amd64",
                        signing_key="signing_key",
                    )
                ]
            )
        ),
    )
    with pytest.raises(SigningError):
        t.run()


def test_verify_signature(fake_cosign_wrapper):
    fake_cosign_wrapper.fake_entry_point_returns.append(
        TDict[str, TDict[str, str]]({"signer_result": TDict[str, str]({"status": "ok"})})
    )
    fake_cosign_client = FakeCosignClient()

    t = VerifyEntries(
        uid="test",
        r_cosign_client=fake_cosign_client,
        i_sign_entries=Port[TList[SignEntry]](
            data=TList[SignEntry](
                [
                    SignEntry(
                        repo="containers/podman",
                        reference="quay.io/containers/podman:latest",
                        identity="quay.io/containers/podman:latest",
                        digest="sha256:123456",
                        arch="amd64",
                        signing_key="signing_key",
                    )
                ]
            )
        ),
        i_public_key_file="test_public_key_file",
    )
    t.run()
