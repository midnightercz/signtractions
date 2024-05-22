import json

from typing import Any

from signtractions.resources.signing_wrapper import (
    CosignSignerWrapper,
)


class FakeCosignSignerWrapper(CosignSignerWrapper):
    """Fake cosign signer wrapper for testing."""

    def __post_init__(self):
        """Fake cosign signer wrapper post init."""
        self._entry_point_runs = []
        self._entry_point_returns = {}

    def _fake_ep(self, *args, **kwargs):
        self._entry_point_runs.append((args, kwargs))
        return self._entry_point_returns[(args, json.dumps(kwargs, sort_keys=True))]

    @property
    def entry_point(self) -> Any:
        """Load and return entry point for pubtools-sign project."""
        return self._fake_ep
