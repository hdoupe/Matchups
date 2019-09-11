from cs_kit import CoreTestFunctions

from cs_config import functions


class TestFunctions1(CoreTestFunctions):
    get_version = functions.get_version
    get_inputs = functions.get_inputs
    validate_inputs = functions.validate_inputs
    run_model = functions.run_model
    ok_adjustment={"matchup": {"pitcher": [{"value": "Max Scherzer"}]}}
    bad_adjustment={"matchup": {"pitcher": [{"value": "Not a pitcher"}]}}
