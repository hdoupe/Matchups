import matchups


def test_MatchupsParams():
    params = matchups.MatchupsParams()
    assert params

def test_update_params():
    params = matchups.MatchupsParams()
    adj = {"batter": [{'use_2018': False, "value": ["Alex Rodriguez"]}]}
    params.adjust(adj)
    params.post_validate()
    assert params.get("batter", use_2018=False) == adj["batter"]

def test_parse_inputs():
    adj = {"matchup": {"batter": [{"value": ["Alex Rodriguez"]}]}}
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    r = matchups.parse_inputs(adj, "", ew, True)

def test_parse_bad_inputs():
    adj = {
        "matchup": {
            "batter": [{"value": [1, "Alex Rodriguez", "fake batter"]}],
            "pitcher": 1234,
        }
    }
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    params, jsonstr, ew = matchups.parse_inputs(adj, "", ew, True)
    assert ew["matchup"]["errors"]["batter"] == ['Not a valid string.']

    adj = {
        "matchup": {
            "batter": [{"value": ["Alex Rodriguez", "fake batter"]}],
        }
    }
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    params, jsonstr, ew = matchups.parse_inputs(adj, "", ew, True)
    exp = ['ERROR: Batter "fake batter" not allowed.']
    assert ew["matchup"]["errors"]["batter"] == exp
