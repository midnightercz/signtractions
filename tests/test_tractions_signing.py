import pytest

from pytractions.base import In, TList, Res

from signtractions.resources.signing_wrapper import SignerWrapperSettings
from signtractions.resources.fake_signing_wrapper import FakeCosignSignerWrapper
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
    assert t.o_sign_entries.data[0].data == SignEntry(
        repo="containers/podman",
        reference="quay.io/containers/podman:latest",
        digest="sha256:123456",
        arch="amd64",
        signing_key="signing_key",
    )
    assert t.o_sign_entries.data[1].data == SignEntry(
        repo="containers/podman",
        reference="quay.io/containers/podman:latest",
        digest="sha256:123457",
        arch="arm64",
        signing_key="signing_key",
    )


def test_sign_sign_entries():
    fsw = FakeCosignSignerWrapper(
        config_file="test",
        settings=SignerWrapperSettings(),
    )
    fsw._entry_point_returns[
        (
            (),
            '{"config_file": "test", "digest": ["sha256:123456"], '
            '"reference": ["quay.io/containers/podman:latest"], "signing_key": "signing_key"}',
        )
    ] = {"signer_result": {"status": "ok"}}
    t = SignSignEntries(
        uid="test",
        r_signer_wrapper=Res[FakeCosignSignerWrapper](r=fsw),
        i_task_id=In[int](data=1),
        i_sign_entries=In[TList[In[SignEntry]]](
            data=TList[In[SignEntry]](
                [
                    In[SignEntry](
                        data=SignEntry(
                            repo="containers/podman",
                            reference="quay.io/containers/podman:latest",
                            digest="sha256:123456",
                            arch="amd64",
                            signing_key="signing_key",
                        )
                    )
                ]
            )
        ),
    )
    t.run()


def test_sign_sign_entries_fail():
    fsw = FakeCosignSignerWrapper(
        config_file="test",
        settings=SignerWrapperSettings(),
    )
    fsw._entry_point_returns[
        (
            (),
            '{"config_file": "test", "digest": ["sha256:123456"], "reference": '
            '["quay.io/containers/podman:latest"], "signing_key": "signing_key"}',
        )
    ] = {"signer_result": {"status": "error", "error_message": "test error"}}
    t = SignSignEntries(
        uid="test",
        r_signer_wrapper=Res[FakeCosignSignerWrapper](r=fsw),
        i_task_id=In[int](data=1),
        i_sign_entries=In[TList[In[SignEntry]]](
            data=TList[In[SignEntry]](
                [
                    In[SignEntry](
                        data=SignEntry(
                            repo="containers/podman",
                            reference="quay.io/containers/podman:latest",
                            digest="sha256:123456",
                            arch="amd64",
                            signing_key="signing_key",
                        )
                    )
                ]
            )
        ),
    )
    with pytest.raises(SigningError):
        t.run()
