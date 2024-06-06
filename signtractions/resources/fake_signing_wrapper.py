from dataclasses import field

from typing import Any, Union

from pytractions.base import TDict, TList, Base
from signtractions.resources.signing_wrapper import (
    CosignSignerWrapper,
)


class FakeEPRunArgs(Base):
    """Fake entry point run args for testing."""

    args: TList[str]
    kwargs: TDict[str, Union[str, TList[str]]]


class FakeCosignSignerWrapper(CosignSignerWrapper):
    """Fake cosign signer wrapper for testing."""

    entry_point_requests: TList[FakeEPRunArgs] = field(default_factory=TList[FakeEPRunArgs])
    entry_point_returns: TList[TDict[str, TDict[str, str]]] = field(
        default_factory=TList[TDict[str, TDict[str, str]]]
    )
    entry_point_runs: TList[FakeEPRunArgs] = field(default_factory=TList[FakeEPRunArgs])

    def _fake_ep(self, *args, **kwargs):
        self.entry_point_runs.append(
            FakeEPRunArgs(
                args=TList[str](args),
                kwargs=TDict[str, Union[str, TList[str]]].content_from_json(kwargs),
            )
        )

        i = self.entry_point_requests.index(
            FakeEPRunArgs(
                args=TList[str](args),
                kwargs=TDict[str, Union[str, TList[str]]].content_from_json(kwargs),
            )
        )
        return self.entry_point_returns[i]

    @property
    def entry_point(self) -> Any:
        """Load and return entry point for pubtools-sign project."""
        return self._fake_ep
