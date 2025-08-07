import contextlib
import functools
from dataclasses import dataclass, field
from io import StringIO
import logging
import os

# import pkg_resources
import importlib
import importlib.metadata
import textwrap
from typing import Iterable, Any, Dict, Generator, Tuple, Optional, List, Callable
import sys

LOG = logging.getLogger("pubtools.quay")

INTERNAL_DELIMITER = "----"
MAX_RETRY_WAIT = 120
# from pubtools.pluggy import pm


@dataclass
class FData:
    """Dataclass for holding data for a function execution.

    Args:
        args (Iterable[Any]): Arguments for the function.
        kwargs (Dict[str, Any]): Keyword arguments for the function.
    """

    args: Iterable[Any]
    kwargs: Dict[str, Any] = field(default_factory=dict)


@contextlib.contextmanager
def capture_stdout() -> Generator[StringIO, None, None]:
    """Capture sys.stdout to stream buffer."""
    old_stdout = sys.stdout
    sys.stdout = new_stdout = StringIO()

    try:
        yield new_stdout
    finally:
        sys.stdout = old_stdout


@contextlib.contextmanager
def setup_entry_point_cli(
    entry_tuple: Tuple[str, str, str],
    name: Optional[str],
    args: List[str],
    environ_vars: Dict[str, Any],
) -> Generator[Callable[[], Any], None, None]:
    """
    Set up an entrypoint as a context manager.

    Args:
        entry_tuple ((str, str, str)):
            Tuple consisting of dependency, category, and entrypoint.
        name: (str):
            Entrypoint name.
        args ([str]):
            Entrypoint arguments.
        environ_vars (dict):
            Env variable names and values to set for the entrypoint.
    """
    orig_environ = os.environ.copy()

    try:
        # First argv element is always the entry point name.
        # For a console_scripts entry point, this will be the same value
        # as if the script was invoked directly. For any other kind of entry point,
        # this value is probably meaningless.
        for key in environ_vars:
            os.environ[key] = environ_vars[key]
        entry_point_func = list(
            importlib.metadata.entry_points(group=entry_tuple[1], name=entry_tuple[2])
        )[0].load()

        if args:
            func_args = [name]
            func_args.extend(args)
            yield functools.partial(entry_point_func, func_args)
        else:
            yield entry_point_func
    finally:
        os.environ.update(orig_environ)

        to_delete = [key for key in os.environ if key not in orig_environ]
        for key in to_delete:
            del os.environ[key]


def run_entrypoint(
    entry_tuple: tuple[str, str, str], name: str, args: list[str], environ_vars: dict[str, Any]
) -> Any:
    """
    Run an entrypoint function and return its return value.

    Args:
        entry_tuple ((str, str, str)):
            Tuple consisting of dependency, category, and entrypoint.
        name: (str):
            Entrypoint name.
        args ([str]):
            Entrypoint arguments.
        environ_vars (dict):
            Env variable names and values to set for the entrypoint.

    Returns (str):
        Data returned by the entrypoint.
    """
    raw_args = " ".join([entry_tuple[2]] + args)
    wrapped_lines = textwrap.wrap(
        raw_args, 100, subsequent_indent="  ", break_on_hyphens=False, break_long_words=False
    )

    LOG.info("Running task with arguments:")
    for idx, line in enumerate(wrapped_lines):
        suffix = ""
        if idx != len(wrapped_lines) - 1:
            # shell-style backslash to indicate continuation
            suffix = " \\"
        LOG.info("%s%s", line, suffix)

    with setup_entry_point_cli(entry_tuple, name, args, environ_vars) as entry_func:
        with capture_stdout():
            pyret = entry_func()

    return pyret


def run_entrypoint_mod(entry_tuple: tuple[str, str, str], name: str, args: list[str]) -> Any:
    """Run entrypoint as python module function."""
    entry_point_func = list(
        importlib.metadata.entry_points(group=entry_tuple[1], name=entry_tuple[2])
    )[0].load()
    print("RUN ENTRYPOINT MOD", entry_point_func, args)
    pyret = entry_point_func(*args)

    return pyret
