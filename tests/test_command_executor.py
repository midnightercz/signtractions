from unittest import mock
import pytest
import logging

from signtractions.resources import command_executor
from .utils.misc import compare_logs


def test_local_executor_init():
    executor = command_executor.LocalExecutor({"some_param": "value"})

    assert executor.params["some_param"] == "value"
    assert executor.params["universal_newlines"] is True
    assert executor.params["stderr"] == -1
    assert executor.params["stdout"] == -1
    assert executor.params["stdin"] == -1


@mock.patch("signtractions.resources.command_executor.subprocess.Popen")
def test_local_executor_run(mock_popen):
    executor = command_executor.LocalExecutor({"some_param": "value"})

    mock_communicate = mock.MagicMock()
    mock_communicate.return_value = ("outlog", "errlog")
    mock_popen.return_value.communicate = mock_communicate
    mock_popen.return_value.returncode = 0

    out, err = executor._run_cmd("pwd", stdin="input")
    assert out == "outlog"
    assert err == "errlog"
    mock_popen.assert_called_once_with(
        ["pwd"],
        some_param="value",
        universal_newlines=True,
        stderr=-1,
        stdout=-1,
        stdin=-1,
    )
    mock_communicate.assert_called_once_with(input="input")


@mock.patch("signtractions.resources.command_executor.subprocess.Popen")
def test_local_executor_context_manager(mock_popen):
    mock_communicate = mock.MagicMock()
    mock_communicate.return_value = ("outlog", "errlog")
    mock_popen.return_value.communicate = mock_communicate
    mock_popen.return_value.returncode = 0

    with command_executor.LocalExecutor({"some_param": "value"}) as executor:
        out, err = executor._run_cmd("pwd", stdin="input")
    assert out == "outlog"
    assert err == "errlog"
    mock_popen.assert_called_once_with(
        ["pwd"],
        some_param="value",
        universal_newlines=True,
        stderr=-1,
        stdout=-1,
        stdin=-1,
    )
    mock_communicate.assert_called_once_with(input="input")


@mock.patch("signtractions.resources.command_executor.subprocess.Popen")
def test_local_executor_run_error(mock_popen):
    executor = command_executor.LocalExecutor({"some_param": "value"})

    mock_communicate = mock.MagicMock()
    mock_communicate.return_value = ("outlog", "errlog")
    mock_popen.return_value.communicate = mock_communicate
    mock_popen.return_value.returncode = -1

    with pytest.raises(RuntimeError, match="An error has occured when executing.*"):
        executor._run_cmd("pwd", stdin="input")


@mock.patch("signtractions.resources.command_executor.subprocess.Popen")
def test_local_executor_run_long_error(mock_popen, caplog):
    caplog.set_level(logging.ERROR)
    executor = command_executor.LocalExecutor({"some_param": "value"})

    err_msg = " ".join(["Very long error message."] * 40)

    mock_communicate = mock.MagicMock()
    mock_communicate.return_value = ("outlog", err_msg)
    mock_popen.return_value.communicate = mock_communicate
    mock_popen.return_value.returncode = -1

    expected_logs = [
        ".*failed with the following error:",
        "    Very long error message. Very long error message. Very long error message. "
        "Very long error message. Very long error message. Very long error message. "
        "Very long error message. Very long error message.",
        "    Very long error message. Very long error message. Very long error message. "
        "Very long error message. Very long error message. Very long error message. "
        "Very long error message. Very long error message.",
        "    Very long error message. Very long error message. Very long error message. "
        "Very long error message. Very long error message. Very long error message. "
        "Very long error message. Very long error message.",
        "    Very long error message. Very long error message. Very long error message. "
        "Very long error message. Very long error message. Very long error message. "
        "Very long error message. Very long error message.",
        "    Very long error message. Very long error message. Very long error message. "
        "Very long error message. Very long error message. Very long error message. "
        "Very long error message. Very long error message.",
    ]

    with pytest.raises(RuntimeError, match="An error has occured when executing.*"):
        executor._run_cmd("pwd", stdin="input")

    compare_logs(caplog, expected_logs)


@mock.patch("signtractions.resources.command_executor.subprocess.Popen")
def test_local_executor_run_error_custom_message(mock_popen):
    executor = command_executor.LocalExecutor({"some_param": "value"})

    mock_communicate = mock.MagicMock()
    mock_communicate.return_value = ("outlog", "errlog")
    mock_popen.return_value.communicate = mock_communicate
    mock_popen.return_value.returncode = -1

    with pytest.raises(RuntimeError, match="Custom error"):
        executor._run_cmd("pwd", stdin="input", err_msg="Custom error")


@mock.patch("signtractions.resources.command_executor.subprocess.Popen")
def test_local_executor_run_tolerate_err(mock_popen):
    executor = command_executor.LocalExecutor({"some_param": "value"})

    mock_communicate = mock.MagicMock()
    mock_communicate.return_value = ("outlog", "errlog")
    mock_popen.return_value.communicate = mock_communicate
    mock_popen.return_value.returncode = -1

    out, err = executor._run_cmd("pwd", stdin="input", tolerate_err=True)
    assert out == "outlog"
    assert err == "errlog"
    mock_popen.assert_called_once_with(
        ["pwd"],
        some_param="value",
        universal_newlines=True,
        stderr=-1,
        stdout=-1,
        stdin=-1,
    )
    mock_communicate.assert_called_once_with(input="input")


@mock.patch("signtractions.resources.command_executor.LocalExecutor._run_cmd")
def test_skopeo_login_already_logged(mock_run_cmd):
    executor = command_executor.LocalExecutor()

    mock_run_cmd.return_value = ("quay_user", "")
    executor.skopeo_login("quay_host", "quay_user", "quay_token")
    mock_run_cmd.assert_called_once_with("skopeo login --get-login quay_host", tolerate_err=True)


@mock.patch("signtractions.resources.command_executor.LocalExecutor._run_cmd")
def test_skopeo_login_missing_credentials(mock_run_cmd):
    executor = command_executor.LocalExecutor()

    mock_run_cmd.return_value = ("not logged into quay", "")
    with pytest.raises(ValueError, match=".*login credentials are not present.*"):
        executor.skopeo_login("some-host")


@mock.patch("signtractions.resources.command_executor.LocalExecutor._run_cmd")
def test_skopeo_login_success(mock_run_cmd):
    executor = command_executor.LocalExecutor()

    mock_run_cmd.side_effect = [("not logged into quay", ""), ("Login Succeeded", "")]
    executor.skopeo_login("quay_host", "quay_user", "quay_token")
    assert mock_run_cmd.call_args_list == [
        mock.call("skopeo login --get-login quay_host", tolerate_err=True),
        mock.call(
            "skopeo login -u quay_user --password-stdin quay_host",
            stdin="quay_token",
        ),
    ]


@mock.patch("signtractions.resources.command_executor.LocalExecutor._run_cmd")
def test_skopeo_login_failed(mock_run_cmd):
    executor = command_executor.LocalExecutor()

    mock_run_cmd.side_effect = [("not logged into quay", ""), ("", "Login failed")]
    with pytest.raises(RuntimeError, match="Login command didn't generate.*"):
        executor.skopeo_login("quay_host", "quay_user", "quay_token")


@mock.patch("signtractions.resources.command_executor.LocalExecutor._run_cmd")
def test_skopeo_tag_images(mock_run_cmd):
    executor = command_executor.LocalExecutor()

    executor.tag_images("quay.io/repo/image:1", ["quay.io/repo/dest:1", "quay.io/repo/dest:2"])
    assert mock_run_cmd.call_args_list == [
        mock.call(
            "skopeo copy docker://quay.io/repo/image:1 docker://quay.io/repo/dest:1 --format v2s2"
        ),
        mock.call(
            "skopeo copy docker://quay.io/repo/image:1 docker://quay.io/repo/dest:2 --format v2s2"
        ),
    ]


@mock.patch("signtractions.resources.command_executor.LocalExecutor._run_cmd")
def test_skopeo_tag_images_all_arch(mock_run_cmd):
    executor = command_executor.LocalExecutor()

    executor.tag_images(
        "quay.io/repo/image:1", ["quay.io/repo/dest:1", "quay.io/repo/dest:2"], True
    )
    assert mock_run_cmd.call_args_list == [
        mock.call(
            "skopeo copy --all docker://quay.io/repo/image:1 docker://quay.io/repo/dest:1"
            " --format v2s2"
        ),
        mock.call(
            "skopeo copy --all docker://quay.io/repo/image:1 docker://quay.io/repo/dest:2"
            " --format v2s2"
        ),
    ]


@mock.patch("signtractions.resources.command_executor.LocalExecutor._run_cmd")
def test_skopeo_inspect(mock_run_cmd):
    mock_run_cmd.return_value = ('{"aaa":"bbb"}', "")
    executor = command_executor.LocalExecutor()

    ret = executor.skopeo_inspect("quay.io/repo/image:1")
    mock_run_cmd.assert_called_once_with("skopeo inspect docker://quay.io/repo/image:1")
    assert ret == {"aaa": "bbb"}

    ret = executor.skopeo_inspect("quay.io/repo/image:1", raw=True)
    assert ret == '{"aaa":"bbb"}'
