from prdiq.checklist import CHECKS, applicable_checks


def test_checklist_has_24_checks_in_six_groups():
    assert len(CHECKS) == 24
    assert len({check.group for check in CHECKS}) == 6
    assert len({check.id for check in CHECKS}) == 24


def test_non_ai_review_omits_only_ai_checks():
    assert len(applicable_checks(is_ai_feature=False)) == 18
    assert all(not check.ai_only for check in applicable_checks(is_ai_feature=False))
    assert len(applicable_checks(is_ai_feature=True)) == 24