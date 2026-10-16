from prdiq.evaluation import SAMPLE_DIR, evaluate
from prdiq.rules import review_prd


def test_good_sample_passes_every_applicable_check():
    prd = (SAMPLE_DIR / "prd_good.md").read_text(encoding="utf-8")
    assert review_prd(prd).score == (24, 24)


def test_evaluation_finds_planted_flaws_without_false_alarms():
    result = evaluate()[0]
    assert result["found"] == result["planted"] == 7
    assert result["missed"] == []
    assert result["false_alarms"] == []