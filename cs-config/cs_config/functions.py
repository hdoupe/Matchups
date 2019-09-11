import matchups


def get_version():
    return matchups.__version__


def get_inputs(meta_param_dict):
    return matchups.get_inputs(meta_param_dict)


def validate_inputs(meta_param_dict, adjustment, errors_warnings):
    return matchups.validate_inputs(meta_param_dict, adjustment, errors_warnings)


def run_model(meta_param_dict, adjustment):
    return matchups.get_matchup(meta_param_dict, adjustment)
