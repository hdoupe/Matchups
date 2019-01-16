from compbaseball import baseball

def test_get_matchup():
    data = {
        'matchup': {
            'batter': [{'value': ['David Ortiz', 'Chipper Jones'],
                        'use_2018': False}]
        }
    }
    assert baseball.get_matchup(False, data)