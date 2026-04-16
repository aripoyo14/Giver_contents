from collector.sources import TIER_1_SOURCES, TIER_2_SOURCES, ALL_SOURCES


def test_tier1_sources_have_required_fields():
    for source in TIER_1_SOURCES:
        assert 'name' in source
        assert 'url' in source
        assert source['tier'] == 1
        assert 0 < source['weight'] <= 1.0
        assert source.get('language') in ('en', 'ja')


def test_tier2_sources_have_required_fields():
    for source in TIER_2_SOURCES:
        assert source['tier'] == 2
        assert source.get('language') in ('en', 'ja')


def test_all_sources_contains_both_tiers():
    tiers = {s['tier'] for s in ALL_SOURCES}
    assert 1 in tiers
    assert 2 in tiers


def test_tier1_has_at_least_three_sources():
    assert len(TIER_1_SOURCES) >= 3
