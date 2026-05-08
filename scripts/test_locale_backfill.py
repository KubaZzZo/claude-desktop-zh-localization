import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import locale_backfill


def test_extract_default_messages_supports_both_property_orders():
    text = 'defaultMessage:"Continue to checkout",id:"abc";id:"def",defaultMessage:"Save image"'

    assert locale_backfill.extract_default_messages(text) == {
        "abc": "Continue to checkout",
        "def": "Save image",
    }


def test_translate_preserves_placeholders_and_tags():
    message = "We'll email {name}'s gift to {toEmail}. <link>Learn more</link>."

    translated = locale_backfill.translate_default_message(message)

    assert "{name}" in translated
    assert "{toEmail}" in translated
    assert "<link>" in translated
    assert "</link>" in translated
    assert "Learn more" not in translated


def test_translate_returns_none_for_unknown_messages_instead_of_generic_text():
    assert locale_backfill.translate_default_message("A previously unseen product sentence.") is None


def test_backfill_locale_adds_missing_keys_without_overwriting_existing():
    locale = {"existing": "已有"}
    messages = {
        "existing": "Existing",
        "checkout": "Continue to checkout",
        "save": "Save image",
        "unknown": "A previously unseen product sentence.",
    }

    added = locale_backfill.backfill_locale(locale, messages)

    assert added == 2
    assert locale["existing"] == "已有"
    assert locale["checkout"] == "继续结账"
    assert locale["save"] == "保存图片"
    assert "unknown" not in locale


def test_fix_common_mixed_translations():
    data = {
        "a": "继续Claude",
        "b": "安装Git",
        "c": "Token 总数",
        "d": "Load all{serverTotal, number}invites",
    }

    changed = locale_backfill.fix_common_mixed_values(data)

    assert changed == 4
    assert data["a"] == "继续使用 Claude"
    assert data["b"] == "安装 Git"
    assert data["c"] == "Token 总量"
    assert data["d"] == "加载全部 {serverTotal, number} 个邀请"
