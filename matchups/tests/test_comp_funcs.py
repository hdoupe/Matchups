from compdevkit import TestAPI

import matchups

def test_get_parameters():
    ta = TestAPI(
        model_parameters=matchups.get_inputs,
        validate_inputs=matchups.validate_inputs,
        run_model=matchups.get_matchup,
    )
    ta.test()