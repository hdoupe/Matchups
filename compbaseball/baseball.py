import json
import os

import pandas as pd

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))

def get_choices():
    with open(os.path.join(CURRENT_PATH, "playerchoices.json")) as f:
        return json.loads(f.read())


def get_inputs():
    with open(os.path.join(CURRENT_PATH, "inputs.json")) as f:
        return {"matchup": json.loads(f.read())}


def pdf_to_clean_html(pdf):
    """Takes a PDF and returns an HTML table without any deprecated tags or
    irrelevant styling"""
    return (pdf.to_html()
            .replace(' border="1"', '')
            .replace(' style="text-align: right;"', ''))


def get_matchup(**kwargs):
    defaults = get_inputs()
    specs = {}
    for param in defaults["matchup"]:
        if kwargs.get(param, None) is not None:
            specs[param] = kwargs[param][0] # comp params are lists right now.
        else:
            specs[param] = defaults["matchup"][param]["value"]
    print("getting data according to: ", specs)
    results = {'outputs': [], 'aggr_outputs': [], 'meta': {"task_times": [0]}}
    use_2018 = kwargs["use_2018"]
    if use_2018:
        url = "https://s3.amazonaws.com/hank-statcast/statcast2018.parquet"
    else:
        url = "https://s3.amazonaws.com/hank-statcast/statcast.parquet"
    print(f"reading data from {url}")
    scallcols = pd.read_parquet(url, engine="pyarrow")
    cols2keep = ["player_name", "batter_name", "pitch_type",
                "game_date", "release_speed", "events",
                "launch_speed", "woba_value", "bb_type",
                "balls", "strikes", "outs_when_up",
                "at_bat_number", "type"]
    scall = scallcols.loc[:, cols2keep]
    scall["date"] = pd.to_datetime(scall["game_date"])
    sc = scall.loc[(scall.date >= specs["start_date"]) & (scall.date < specs["end_date"])]

    pitcher, batter = specs["pitcher"], specs["batter"]
    gb = sc.loc[(sc["player_name"]==pitcher) & (sc["batter_name"]==batter), :].groupby(
        ["balls", "strikes"])
    pitch_outcome_normalized = pd.DataFrame(gb["type"].value_counts(normalize=True))
    pitch_outcome = pd.DataFrame(gb["type"].value_counts())

    gb = sc.loc[(sc["player_name"]==pitcher) & (sc["batter_name"]==batter), :].groupby(
        ["balls", "strikes"])
    pitch_type_normalized = pd.DataFrame(gb["pitch_type"].value_counts(normalize=True))
    pitch_type = pd.DataFrame(gb["pitch_type"].value_counts())

    agg_gb = sc.groupby(
        ["balls", "strikes"])
    agg_pitch_outcome_normalized = pd.DataFrame(gb["type"].value_counts(normalize=True))

    agg_gb = sc.groupby(
        ["balls", "strikes"])
    agg_pitch_type_normalized = pd.DataFrame(gb["pitch_type"].value_counts(normalize=True))


    results['aggr_outputs'].append({
        'tags': {'attribute': 'pitch outcome'},
        'title': 'Pitch outcome by count for all players',
        'downloadable': [{'filename': 'pitch_outcome.csv',
                          'text': agg_pitch_outcome_normalized.to_csv()}],
        'renderable': pdf_to_clean_html(agg_pitch_outcome_normalized)})
    results['aggr_outputs'].append({
        'tags': {'attribute': 'pitch type'},
        'title': 'Pitch type by count for all players',
        'downloadable': [{'filename': 'pitch_type.csv',
                          'text': agg_pitch_type_normalized.to_csv()}],
        'renderable': pdf_to_clean_html(agg_pitch_type_normalized)})

    results["outputs"] = [
        {
            "dimension": "",
            "tags": {"attribute": "pitch outcome", "count": "normalized"},
            'title': f'Normalized pitch outcome by count for {pitcher} v. {batter}',
            'downloadable': [{'filename': f"normalized_pitch_outcome_{pitcher}_{batter}.csv",
                              "text": pitch_outcome_normalized.to_csv()}],
            'renderable': pdf_to_clean_html(pitch_outcome_normalized)
        },
        {
            "dimension": "",
            "tags": {"attribute": "pitch outcome", "count": "raw count"},
            'title': f'Pitch outcome by count for {pitcher} v. {batter}',
            'downloadable': [{'filename': f"pitch_outcome_{pitcher}_{batter}.csv",
                              "text": pitch_outcome.to_csv()}],
            'renderable': pdf_to_clean_html(pitch_outcome)
        },
        {
            "dimension": "",
            "tags": {"attribute": "pitch type", "count": "normalized"},
            'title': f'Normalized pitch type by count for {pitcher} v. {batter}',
            'downloadable': [{'filename': f"normalized_pitch_type_{pitcher}_{batter}.csv",
                              "text": pitch_type_normalized.to_csv()}],
            'renderable': pdf_to_clean_html(pitch_type_normalized)
        },
        {
            "dimension": "",
            "tags": {"attribute": "pitch type", "count": "raw count"},
            'title': f'Pitch type by count for {pitcher} v. {batter}',
            'downloadable': [{'filename': f"pitch_type{pitcher}_{batter}.csv",
                            "text": pitch_type.to_csv()}],
            'renderable': pdf_to_clean_html(pitch_type)
        },
    ]

    return results


def validate_inputs(inputs):
    # date parameters alredy evaluated by webapp.
    inputs = inputs["matchup"]
    ew = {"matchup": {'errors': {}, 'warnings': {}}}
    for pos in ["pitcher", "batter"]:
        player = inputs[pos]
        if not player:
            continue
        player = player[0]
        choices = get_choices()
        if player not in choices["choices"]:
            ew["matchup"]["errors"] = {pos: f"player \"{player}\" not allowed"}
    return ew

def parse_inputs(use_2018, inputs):
    ew = validate_inputs(inputs)
    return (inputs, {"matchup": json.dumps(inputs)}, ew)
