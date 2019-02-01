import matchups


def test_get_matchup():
    data = {
        'matchup': {
            'batter': [{'value': ['Freddie Freeman', 'Yasiel Puig'],
                        'use_full_data': False}]
        }
    }
    assert matchups.get_matchup(False, data)

def test_get_matchup_empty():
    data = {
        'matchup': {
            'batter': [{'value': ['Ty Cobb'],
                        'use_full_data': False}]
        }
    }
    assert matchups.get_matchup(False, data)