import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import validate_resources


def test_rejects_question_mark_placeholder_values():
    data = {
        "good": "Avatar",
        "bad": "??",
        "also_bad": "??????...",
    }

    with pytest.raises(SystemExit) as exc:
        validate_resources.validate_no_placeholder_values(
            data, Path("locales/ion-zh-CN.json")
        )

    message = str(exc.value)
    assert "bad" in message
    assert "also_bad" in message


def test_allows_literal_question_marks_in_real_sentences():
    data = {
        "question": "What should Claude call you?",
        "icu": "{count, plural, one {# question?} other {# questions?}}",
    }

    validate_resources.validate_no_placeholder_values(data, Path("locales/ion-zh-CN.json"))
