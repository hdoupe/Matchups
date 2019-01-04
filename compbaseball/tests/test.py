from compbaseball import baseball

def test_get_inputs():
    assert baseball.get_inputs()

def test_parse_inputs():
    adj = {"matchup": {"batter": ["Alex Rodriguez"]}}
    ew = {"matchup": {"errors": {}, "warnings": {}}}
    r = baseball.parse_inputs(adj, "", ew, True)
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
    baseball.get_matchup(use_2018, user_mods)
