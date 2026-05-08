import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import auto_localize


def test_build_script_command_adds_auto_detect_by_default():
    command = auto_localize.build_script_command("apply_localization.py", auto_detect=True, app_dir=None)

    assert Path(command[-2]).name == "apply_localization.py"
    assert command[-1] == "--auto-detect"


def test_build_script_command_uses_app_dir_when_provided():
    command = auto_localize.build_script_command("verify_localization.py", auto_detect=True, app_dir="D:/Claude/app")

    assert Path(command[-3]).name == "verify_localization.py"
    assert command[-2:] == ["--app-dir", "D:/Claude/app"]
    assert "--auto-detect" not in command


def test_summarize_missing_locale_ids_limits_samples():
    messages = {f"id-{i}": f"Message {i}" for i in range(20)}
    locale = {"id-0": "已有"}

    summary = auto_localize.summarize_missing_locale_ids(messages, locale, sample_limit=3)

    assert summary["count"] == 19
    assert summary["samples"] == [
        {"id": "id-1", "defaultMessage": "Message 1"},
        {"id": "id-2", "defaultMessage": "Message 2"},
        {"id": "id-3", "defaultMessage": "Message 3"},
    ]


def test_report_status_is_failed_when_any_required_step_fails():
    steps = [
        {"name": "apply", "required": True, "exitCode": 0},
        {"name": "verify", "required": True, "exitCode": 1},
        {"name": "scan", "required": False, "exitCode": 1},
    ]

    assert auto_localize.report_status(steps) == "failed"


def test_report_status_is_ok_when_only_optional_steps_fail():
    steps = [
        {"name": "apply", "required": True, "exitCode": 0},
        {"name": "scan", "required": False, "exitCode": 1},
    ]

    assert auto_localize.report_status(steps) == "ok"
