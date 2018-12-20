from compbaseball import baseball

def test_BaseballParams():
    params = baseball.BaseballParams()
    assert params

def test_update_params():
    params = baseball.BaseballParams()
    params.adjust({"batter": [{"value": ["Alex Rodriguez"]}]})
    params.post_validate_batter()
    assert params.get("batter") == [{"value": ["Alex Rodriguez"]}]

def test_parse_inputs():
    adj = {"matchup": {"batter": [{"value": ["Alex Rodriguez"]}]}}
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    r = baseball.parse_inputs(adj, "", ew, True)

def test_parse_bad_inputs():
    adj = {"matchup": {"batter": [{"value": [1, "Alex Rodriguez", "fake batter"]}]}}
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    res = baseball.parse_inputs(adj, "", ew, True)

