import json
import logging
import shlex
import subprocess
import textwrap
from types import TracebackType
from typing import Any, Optional, Type
from typing_extensions import Self


from shlex import quote

LOG = logging.getLogger()


class Executor(object):
    """
    Base executor class.

    Implementation of command execution should be done in
    descendant classes. Common pre- and post-processing should be
    implemented in this class.
    """

    def __enter__(self) -> Self:
        """Use the class as context manager. Returns instance upon invocation."""
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        """Cleanup when used as context manager. No-op by default."""
        pass

    def _run_cmd(
        self,
        cmd: str,
        err_msg: str | None = None,
        tolerate_err: bool = False,
        stdin: str | None = None,
    ) -> tuple[str, str]:
        """Run a bash command."""
        raise NotImplementedError  # pragma: no cover"

    def skopeo_login(
        self, host: str = "quay.io", username: str | None = None, password: str | None = None
    ) -> None:
        """
        Attempt to login to Quay if no login credentials are present.

        Args:
            host (str):
                docker registry host (quay.io as default)
            username (str):
                Username for login.
            password (str):
                Password for login.
        """
        cmd_check = "skopeo login --get-login %s" % host
        out, err = self._run_cmd(cmd_check, tolerate_err=True)
        if username and username in out:
            LOG.info("Already logged in to Quay.io")
            return

        if not username or not password:
            raise ValueError(
                "Skopeo login credentials are not present. Quay user and token must be provided."
            )
        LOG.info(f"Logging in to Quay with provided credentials {username} {password}")

        cmd_login = ("skopeo login -u {0} --password-stdin %s" % host).format(quote(username))
        out, err = self._run_cmd(cmd_login, stdin=password)

        if "Login Succeeded" in out:
            LOG.info("Login successful")
        else:
            raise RuntimeError(
                "Login command didn't generate expected output. "
                "STDOUT: '{0}', STDERR: '{1}'".format(out, err)
            )

    def tag_images(self, source_ref: str, dest_refs: list[str], all_arch: bool = False) -> None:
        """
        Copy image from source to destination(s) using skopeo.

        Args:
            source_ref (str):
                Reference of the source image.
            dest_refs ([str]):
                List of target references to copy the image to.
            all_arch (bool):
                Whether to copy all architectures (if multiarch image)
        """
        if all_arch:
            cmd = "skopeo copy --all docker://{0} docker://{1} --format v2s2"
        else:
            cmd = "skopeo copy docker://{0} docker://{1} --format v2s2"

        for dest_ref in dest_refs:
            LOG.info("Tagging source '{0}' to destination '{1}'".format(source_ref, dest_ref))
            self._run_cmd(cmd.format(quote(source_ref), quote(dest_ref)))
            LOG.info("Destination image {0} has been tagged.".format(dest_ref))

        LOG.info("Tagging complete.")

    def skopeo_inspect(self, image_ref: str, raw: bool = False) -> Any:
        """
        Run skopeo inspect and return the result.

        NOTE: inspect command will not be run with the --raw argument. This option only returns an
        image manifest, which can be gathered by QuayClient. 'raw' argument in this function
        denotes if the result should be parsed or returned raw.

        Args:
            image_ref (str):
                Image reference to inspect.
            raw (bool):
                Whether to parse the returned JSON, or return raw.
        Returns (dict|str):
            Result of skopeo inspect.
        """
        cmd = "skopeo inspect docker://{0}".format(image_ref)
        out, _ = self._run_cmd(cmd)

        if raw:
            return out
        else:
            return json.loads(out)


class LocalExecutor(Executor):
    """Run commands locally."""

    def __init__(self, params: dict[str, Any] = {}) -> None:
        """
        Initialize.

        Args:
            params (dict):
                Custom parameters to be applied when running the shell commands.
        """
        self.params = params
        self.params.setdefault("universal_newlines", True)
        self.params.setdefault("stderr", subprocess.PIPE)
        self.params.setdefault("stdout", subprocess.PIPE)
        self.params.setdefault("stdin", subprocess.PIPE)

    # @tw.instrument_func(args_to_attr=True)
    def _run_cmd(
        self,
        cmd: str,
        err_msg: str | None = None,
        tolerate_err: bool = False,
        stdin: str | None = None,
    ) -> tuple[str, str]:
        """
        Run a command locally.

        Args:
            cmd (str):
                Shell command to be executed.
            error_msg (str):
                Error message written when the command fails.
            tolerate_err (bool):
                Whether to tolerate a failed command.
            stdin (str):
                String to send to standard input for a command.

        Returns (str, str):
            Tuple of stdout and stderr generated by the command.
        """
        err_msg = err_msg or "An error has occured when executing a command."

        p = subprocess.Popen(shlex.split(cmd), **self.params)
        out, err = p.communicate(input=stdin)

        if p.returncode != 0 and not tolerate_err:
            LOG.error("Command {0} failed with the following error:".format(cmd))
            for line in textwrap.wrap(err, 200):
                LOG.error(f"    {line}")
            raise RuntimeError(err_msg)

        return out, err
