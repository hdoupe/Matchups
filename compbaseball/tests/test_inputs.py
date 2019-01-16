from compbaseball import baseball

def test_BaseballParams():
    params = baseball.BaseballParams()
    assert params

def test_update_params():
    params = baseball.BaseballParams()
    adj = {"batter": [{'use_2018': False, "value": ["Alex Rodriguez"]}]}
    params.adjust(adj)
    params.post_validate_batter()
    assert params.get("batter", use_2018=False) == adj["batter"]

def test_parse_inputs():
    adj = {"matchup": {"batter": [{"value": ["Alex Rodriguez"]}]}}
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    r = baseball.parse_inputs(adj, "", ew, True)

def test_parse_bad_inputs():
    adj = {
        "matchup": {
            "batter": [{"value": [1, "Alex Rodriguez", "fake batter"]}],
            "pitcher": 1234,
        }
    }
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    res = baseball.parse_inputs(adj, "", ew, True)