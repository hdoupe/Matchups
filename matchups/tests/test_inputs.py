import matchups


def test_MatchupsParams():
    params = matchups.MatchupsParams()
    assert params


def test_update_params():
    params = matchups.MatchupsParams()
    adj = {"batter": [{"use_full_sample": False, "value": ["Alex Rodriguez"]}]}
    params.adjust(adj)
    params.set_state(use_full_sample=False)
    assert params.batter == adj["batter"]


def test_parse_inputs():
    meta_params = {"use_full_sample": True}
    adj = {"matchup": {"batter": ["Alex Rodriguez"]}}
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    assert matchups.validate_inputs(meta_params, adj, ew)


def test_parse_bad_inputs():
    meta_params = {"use_full_sample": True}
    adj = {"matchup": {"batter": [1], "pitcher": 1234,}}
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    ew = matchups.validate_inputs(meta_params, adj, ew)
    ew = ew["errors_warnings"]
    assert ew["matchup"]["errors"]["batter"] == ["Not a valid string."]
    assert ew["matchup"]["errors"]["pitcher"] == ["Not a valid string."]

    adj = {"matchup": {"batter": ["fake batter"],}}
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    ew = matchups.validate_inputs(meta_params, adj, ew)
    ew = ew["errors_warnings"]
    exp = ['batter "fake batter" must be in list of choices.']
    assert ew["matchup"]["errors"]["batter"] == exp
