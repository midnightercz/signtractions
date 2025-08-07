from typing import Union

from .signing_wrapper import HVaultSignerWrapper, CosignSignerWrapper, MsgSignerWrapper
from .fake_signing_wrapper import FakeCosignSignerWrapper


SIGNING_WRAPPERS = Union[
    HVaultSignerWrapper, CosignSignerWrapper, MsgSignerWrapper, FakeCosignSignerWrapper
]
