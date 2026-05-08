import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import extract_missing_locale_ids


def test_classify_message_groups_by_keywords():
    assert extract_missing_locale_ids.classify_message("Continue to checkout") == "billing"
    assert extract_missing_locale_ids.classify_message("Create pull requests automatically") == "claude-code"
    assert extract_missing_locale_ids.classify_message("What Anthropic doesn't see") == "privacy"
    assert extract_missing_locale_ids.classify_message("Install plugin") == "plugins"


def test_build_missing_items_preserves_source_file_and_context():
    messages = {
        "a": {"defaultMessage": "Continue to checkout", "files": ["chunk-a.js"]},
        "b": {"defaultMessage": "Already translated", "files": ["chunk-b.js"]},
    }
    locale = {"b": "已翻译"}

    items = extract_missing_locale_ids.build_missing_items(messages, locale)

    assert items == [
        {
            "id": "a",
            "defaultMessage": "Continue to checkout",
            "suggestedGroup": "billing",
            "files": ["chunk-a.js"],
            "translation": "",
            "status": "todo",
        }
    ]
