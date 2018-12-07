import json
import os

from pybaseball import playerid_lookup, statcast_pitcher

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

def get_choices():
    with open(os.path.join(CURRENT_PATH, "playerchoices.json")) as f:
        return json.loads(f.read())

def get_data(pitcher, start_date, end_date):
    first_name, last_name = pitcher.split(" ")
    info = playerid_lookup(last_name, first_name)
    results = {'outputs': [], 'aggr_outputs': [], 'meta': {"task_times": [0]}}
    if len(info) == 0:
        return results
    mlbid = info.key_mlbam.values[0]
    data = statcast_pitcher(start_date, end_date, 477132)
    mean_stat = data.groupby(by="pitch_type")["release_speed", "launch_speed"].mean()
    std_stat = data.groupby(by="pitch_type")["release_speed", "launch_speed"].mean()

    results['aggr_outputs'].append({
        'tags': {'statistic': 'mean'},
        'title': 'StatCast Means',
        'downloadable': [{'filename': 'mean' + '.csv',
                          'text': mean_stat.to_csv()}],
        'renderable': mean_stat.to_html()})
    results['aggr_outputs'].append({
        'tags': {'statistic': 'std'},
        'title': 'StatCast Standard Dev.',
        'downloadable': [{'filename': 'std' + '.csv',
                          'text': std_stat.to_csv()}],
        'renderable': std_stat.to_html()})
    return results


def validate_inputs(inputs):
    # date parameters alredy evaluated by webapp.
    ew = {'errors': {}, 'warnings': {}}
    pitcher = inputs["pitcher"]
    choices = get_choices()
    if pitcher not in choices["choices"]:
        ew["errors"] = {"pitcher": f"pitcher {pitcher} not allowed"}
    return ew

def parse_inputs(inputs):
    ew = validate_inputs(inputs)
    return {"params": inputs, "jsonstrs": {"inputs": json.dumps(inputs)},
            "errors_warnings": ew}


def get_inputs():
    with open(os.path.join(CURRENT_PATH, "inputs.json")) as f:
        return {"inputs": json.loads(f.read())}
