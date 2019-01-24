from matchups import get_inputs, parse_inputs, get_matchup

def test_get_inputs():
    assert get_inputs()

def test_parse_inputs():
    adj = {"matchup": {"batter": ["Alex Rodriguez"]}}
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    r = parse_inputs(adj, "", ew, True)
    assert r

def test_get_matchup():
    use_2018 = True
    user_mods = {
        "matchup": {
            "start_date": "2018-05-01",
            "pitcher": "Max Scherzer",
            "batter": ["Freddie Freeman", "David Wright"]
        }
    }
    assert get_matchup(use_2018, user_mods)
