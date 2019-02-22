import matchups


def test_MatchupsParams():
    params = matchups.MatchupsParams()
    assert params

def test_update_params():
    params = matchups.MatchupsParams()
    adj = {"batter": [{'use_full_data': False, "value": ["Alex Rodriguez"]}]}
    params.adjust(adj)
    params.set_state(use_full_data=False)
    assert params.batter == adj["batter"]

def test_parse_inputs():
    adj = {"matchup": {"batter": [{"value": ["Alex Rodriguez"]}]}}
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    r = matchups.parse_inputs(adj, "", ew, True)

def test_parse_bad_inputs():
    adj = {
        "matchup": {
            "batter": [{"value": [1, "Alex Rodriguez", "fake batter"]}],
            "pitcher": [{"value": 1234}],
        }
    }
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    params, jsonstr, ew = matchups.parse_inputs(adj, "", ew, True)
    assert ew["matchup"]["errors"]["batter"] == ['Not a valid string: 1.']
    assert ew["matchup"]["errors"]["pitcher"] == ["Not a valid string: 1234."]

    adj = {
        "matchup": {
            "batter": [{"value": ["Alex Rodriguez", "fake batter"]}],
        }
    }
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    params, jsonstr, ew = matchups.parse_inputs(adj, "", ew, True)
    exp = ['batter "fake batter" must be in list of choices for dimensions .']
    assert ew["matchup"]["errors"]["batter"] == exp
