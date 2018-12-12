import json
import os

from pybaseball import playerid_lookup, statcast_pitcher

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

def get_choices():
    with open(os.path.join(CURRENT_PATH, "playerchoices.json")) as f:
        return json.loads(f.read())


def get_inputs():
    with open(os.path.join(CURRENT_PATH, "inputs.json")) as f:
        return {"pitching": json.loads(f.read())}


def pdf_to_clean_html(pdf):
    """Takes a PDF and returns an HTML table without any deprecated tags or
    irrelevant styling"""
    return (pdf.to_html()
            .replace(' border="1"', '')
            .replace(' style="text-align: right;"', ''))


def get_data(**kwargs):
    defaults = get_inputs()
    specs = {}
    for param in defaults["pitching"]:
        if kwargs.get(param, None) is not None:
            specs[param] = kwargs[param][0] # comp params are lists right now.
        else:
            specs[param] = defaults["pitching"][param]["value"]
    print("getting data according to: ", specs)
    first_name, last_name = specs["pitcher"].split(" ")
    info = playerid_lookup(last_name, first_name)
    results = {'outputs': [], 'aggr_outputs': [], 'meta': {"task_times": [0]}}
    if len(info) == 0:
        return results
    mlbid = info.key_mlbam.values[0]
    data = statcast_pitcher(specs["start_date"], specs["end_date"], mlbid)
    mean_stat = data.groupby(by="pitch_type")["release_speed", "launch_speed"].mean()
    std_stat = data.groupby(by="pitch_type")["release_speed", "launch_speed"].std()

    results['aggr_outputs'].append({
        'tags': {'statistic': 'mean'},
        'title': 'StatCast Means',
        'downloadable': [{'filename': 'mean' + '.csv',
                          'text': mean_stat.to_csv()}],
        'renderable': pdf_to_clean_html(mean_stat)})
    results['aggr_outputs'].append({
        'tags': {'statistic': 'std'},
        'title': 'StatCast Standard Dev.',
        'downloadable': [{'filename': 'std' + '.csv',
                          'text': std_stat.to_csv()}],
        'renderable': pdf_to_clean_html(std_stat)})
    return results


def validate_inputs(inputs):
    # date parameters alredy evaluated by webapp.
    inputs = inputs["pitching"]
    ew = {"pitching": {'errors': {}, 'warnings': {}}}
    pitcher = inputs["pitcher"]
    if not pitcher:
        return ew
    pitcher = pitcher[0]
    choices = get_choices()
    if pitcher not in choices["choices"]:
        ew["pitching"]["errors"] = {"pitcher": f"pitcher {pitcher} not allowed"}
    return ew

def parse_inputs(inputs):
    ew = validate_inputs(inputs)
    return (inputs, {"pitching": json.dumps(inputs)}, ew)
