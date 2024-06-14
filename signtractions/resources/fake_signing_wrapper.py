from dataclasses import field

from typing import Any, Union

from pytractions.base import TDict, TList, Base, doc
from signtractions.resources.signing_wrapper import (
    CosignSignerWrapper,
)


class FakeEPRunArgs(Base):
    """Fake entry point run args for testing."""

    args: TList[str]
    kwargs: TDict[str, Union[str, TList[str]]]


class FakeCosignSignerWrapper(CosignSignerWrapper):
    """Fake cosign signer wrapper for testing."""

    fake_entry_point_requests: TList[FakeEPRunArgs]
    fake_entry_point_returns: TList[TDict[str, TDict[str, str]]]
    fake_entry_point_runs: TList[FakeEPRunArgs] = field(default_factory=TList[FakeEPRunArgs])

    d_fake_entry_point_requests: str = doc("Fake entry point requests for testing.")
    d_fake_entry_point_returns: str = doc("Fake entry point returns for testing.")
    d_fake_entry_point_runs: str = doc("Records of fake entry point runs.")

    def _fake_ep(self, *args, **kwargs):
        self.fake_entry_point_runs.append(
            FakeEPRunArgs(
                args=TList[str](args),
                kwargs=TDict[str, Union[str, TList[str]]].content_from_json(kwargs),
            )
        )

        i = self.fake_entry_point_requests.index(
            FakeEPRunArgs(
                args=TList[str](args),
                kwargs=TDict[str, Union[str, TList[str]]].content_from_json(kwargs),
            )
        )
        return self.fake_entry_point_returns[i]

    @property
    def entry_point(self) -> Any:
        """Load and return entry point for pubtools-sign project."""
        return self._fake_ep
