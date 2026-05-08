import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import repair_mojibake_assets


def test_repair_mojibake_text_repairs_utf8_chinese_written_as_latin1():
    text = 'label:"å\x8d\x8fä½\x9c",code:"ä»£ç\xa0\x81",keep:"ASCII"'

    fixed, repairs = repair_mojibake_assets.repair_mojibake_text(text)

    assert repairs == 2
    assert 'label:"协作"' in fixed
    assert 'code:"代码"' in fixed
    assert 'keep:"ASCII"' in fixed


def test_repair_mojibake_text_does_not_change_non_cjk_latin1():
    text = 'name:"Café", unit:"µs"'

    fixed, repairs = repair_mojibake_assets.repair_mojibake_text(text)

    assert repairs == 0
    assert fixed == text
