import matchups


def test_get_matchup():
    data = {
        'matchup': {
            'batter': [{'value': ['Freddie Freeman', 'Yasiel Puig'],
                        'use_full_data': True}]
        }
    }
    assert matchups.get_matchup(True, data)