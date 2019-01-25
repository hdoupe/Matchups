import matchups


def test_get_matchup():
    data = {
        'matchup': {
            'batter': [{'value': ['David Ortiz', 'Chipper Jones'],
                        'use_2018': False}]
        }
    }
    assert matchups.get_matchup(False, data)