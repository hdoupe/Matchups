import matchups


def test_get_matchup():
    adj = {
        "matchup": {
            "batter": [{"value": ["Freddie Freeman"], "use_full_sample": False}]
        }
    }
    assert matchups.get_matchup({"use_full_sample": False}, adj)


def test_get_matchup_empty():
    adj = {
        "matchup": {"pitcher": [{"value": "Freddie Freeman", "use_full_sample": False}]}
    }
    assert matchups.get_matchup({"use_full_sample": False}, adj)
