import pytest
from typing import Union

from pytractions.base import In, TList, TDict, Res

from signtractions.resources.signing_wrapper import CosignSignerSettings
from signtractions.resources.fake_signing_wrapper import FakeCosignSignerWrapper, FakeEPRunArgs
from signtractions.tractions.signing import (
    SignEntriesFromContainerParts,
    SignEntry,
    ContainerParts,
    SignSignEntries,
)
from signtractions.resources.signing_wrapper import SigningError


def test_sign_entries_from_container_parts():
    t = SignEntriesFromContainerParts(
        uid="test",
        i_container_parts=In[ContainerParts](
            data=ContainerParts(
                registry="quay.io",
                image="containers/podman",
                tag="latest",
                digests=TList[str](["sha256:123456", "sha256:123457"]),
                arches=TList[str](["amd64", "arm64"]),
            )
        ),
        i_signing_key=In[str](data="signing_key"),
    )
    t.run()
    assert t.o_sign_entries.data[0] == SignEntry(
        repo="containers/podman",
        reference="quay.io/containers/podman:latest",
        digest="sha256:123456",
        arch="amd64",
        signing_key="signing_key",
    )
    assert t.o_sign_entries.data[1] == SignEntry(
        repo="containers/podman",
        reference="quay.io/containers/podman:latest",
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
        r_signer_wrapper=Res[FakeCosignSignerWrapper](r=fsw),
        i_task_id=In[int](data=1),
        i_sign_entries=In[TList[SignEntry]](
            data=TList[SignEntry](
                [
                    SignEntry(
                        repo="containers/podman",
                        reference="quay.io/containers/podman:latest",
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
        r_signer_wrapper=Res[FakeCosignSignerWrapper](r=fsw),
        i_task_id=In[int](data=1),
        i_sign_entries=In[TList[SignEntry]](
            data=TList[SignEntry](
                [
                    SignEntry(
                        repo="containers/podman",
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
