import json
import os

import pandas as pd

from paramtools.parameters import Parameters
from marshmallow import ValidationError

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


class BaseballParams(Parameters):
    schema = os.path.join(CURRENT_PATH, "schema.json")
    defaults = os.path.join(CURRENT_PATH, "defaults.json")

    def post_validate_pitcher(self):
        with open(os.path.join(CURRENT_PATH, "playerchoices.json")) as f:
            choices = json.loads(f.read())
        pitcher = self.get("pitcher")[0]["value"]
        errors = []
        if pitcher not in choices["choices"]:
            errors = [f"ERROR: Pitcher \"{pitcher}\" not allowed."]
            raise ValidationError({"pitcher": errors})

    def post_validate_batter(self):
        with open(os.path.join(CURRENT_PATH, "playerchoices.json")) as f:
            choices = json.loads(f.read())
        batters = self.get("batter")[0]["value"]
        errors = []
        for batter in batters:
            if batter not in choices["choices"]:
                errors.append(f"ERROR: Batter \"{batter}\" not allowed.")
        if errors:
            raise ValidationError({"batter": errors})


def get_inputs(use_2018=True):
    params = BaseballParams()
    return params.specification()


def parse_inputs(inputs, jsonparams, errors_warnings, use_2018=True):
    adjustments = inputs["matchup"]
    params = BaseballParams()
    try:
        params.adjust(adjustments)
    except ValidationError as ve:
        errors_warnings["matchup"]["errors"].update(ve.messages)
    try:
        params.post_validate_batter()
    except ValidationError as ve:
        errors_warnings["matchup"]["errors"].update(ve.messages)
    try:
        params.post_validate_pitcher()
    except ValidationError as ve:
        errors_warnings["matchup"]["errors"].update(ve.messages)

    import pdb; pdb.set_trace()
    return (inputs, {"matchup": json.dumps(inputs)}, errors_warnings)


def pdf_to_clean_html(pdf):
    """Takes a PDF and returns an HTML table without any deprecated tags or
    irrelevant styling"""
    return (pdf.to_html()
            .replace(' border="1"', '')
            .replace(' style="text-align: right;"', ''))


def get_matchup(use_2018, user_mods):
    config = user_mods["matchup"]
    defaults = get_inputs()
    specs = {}
    for param in defaults["matchup"]:
        if config.get(param, None) is not None:
            specs[param] = config[param]
        else:
            specs[param] = defaults["matchup"][param]["value"]
    print("getting data according to: ", use_2018, specs)
    results = {'outputs': [], 'aggr_outputs': [], 'meta': {"task_times": [0]}}
    if use_2018:
        url = "https://s3.amazonaws.com/hank-statcast/statcast2018.parquet"
    else:
        url = "https://s3.amazonaws.com/hank-statcast/statcast.parquet"
    print(f"reading data from {url}")
    scall = pd.read_parquet(url, engine="pyarrow")
    print('data read')
    scall["date"] = pd.to_datetime(scall["game_date"])
    sc = scall.loc[(scall.date >= specs["start_date"]) & (scall.date < specs["end_date"])]
    del scall
    print('filtered by date')

    gb = sc.groupby(
        ["balls", "strikes"])
    agg_pitch_outcome_normalized = pd.DataFrame(gb["type"].value_counts(normalize=True))
    del gb

    gb = sc.groupby(
        ["balls", "strikes"])
    agg_pitch_type_normalized = pd.DataFrame(gb["pitch_type"].value_counts(normalize=True))
    del gb

    results['aggr_outputs'].append({
        'tags': {'attribute': 'pitch-outcome'},
        'title': 'Pitch outcome by count for all players',
        'downloadable': [{'filename': 'pitch_outcome.csv',
                          'text': agg_pitch_outcome_normalized.to_csv()}],
        'renderable': pdf_to_clean_html(agg_pitch_outcome_normalized)})
    results['aggr_outputs'].append({
        'tags': {'attribute': 'pitch-type'},
        'title': 'Pitch type by count for all players',
        'downloadable': [{'filename': 'pitch_type.csv',
                          'text': agg_pitch_type_normalized.to_csv()}],
        'renderable': pdf_to_clean_html(agg_pitch_type_normalized)})


    pitcher, batters = specs["pitcher"], specs["batter"]
    for batter in batters:
        print(pitcher, batter)
        pdf = sc.loc[(sc["player_name"]==pitcher) & (sc["batter_name"]==batter), :]
        if len(pdf) == 0:
            pitch_outcome_normalized = pd.DataFrame()
            pitch_outcome = pd.DataFrame()
            pitch_type_normalized = pd.DataFrame()
            pitch_type = pd.DataFrame()
        else:
            gb = pdf.loc[(pdf["player_name"]==pitcher) & (pdf["batter_name"]==batter), :].groupby(
                ["balls", "strikes"])
            pitch_outcome_normalized = pd.DataFrame(gb["type"].value_counts(normalize=True))
            pitch_outcome = pd.DataFrame(gb["type"].value_counts())
            del gb

            gb = pdf.loc[(pdf["player_name"]==pitcher) & (pdf["batter_name"]==batter), :].groupby(
                ["balls", "strikes"])
            pitch_type_normalized = pd.DataFrame(gb["pitch_type"].value_counts(normalize=True))
            pitch_type = pd.DataFrame(gb["pitch_type"].value_counts())
            del gb
            del pdf

        results["outputs"] += [
            {
                "dimension": batter,
                "tags": {"attribute": "pitch-outcome", "count": "normalized"},
                'title': f'Normalized pitch outcome by count for {pitcher} v. {batter}',
                'downloadable': [{'filename': f"normalized_pitch_outcome_{pitcher}_{batter}.csv",
                                "text": pitch_outcome_normalized.to_csv()}],
                'renderable': pdf_to_clean_html(pitch_outcome_normalized)
            },
            {
                "dimension": batter,
                "tags": {"attribute": "pitch-outcome", "count": "raw-count"},
                'title': f'Pitch outcome by count for {pitcher} v. {batter}',
                'downloadable': [{'filename': f"pitch_outcome_{pitcher}_{batter}.csv",
                                "text": pitch_outcome.to_csv()}],
                'renderable': pdf_to_clean_html(pitch_outcome)
            },
            {
                "dimension": batter,
                "tags": {"attribute": "pitch-type", "count": "normalized"},
                'title': f'Normalized pitch type by count for {pitcher} v. {batter}',
                'downloadable': [{'filename': f"normalized_pitch_type_{pitcher}_{batter}.csv",
                                "text": pitch_type_normalized.to_csv()}],
                'renderable': pdf_to_clean_html(pitch_type_normalized)
            },
            {
                "dimension": batter,
                "tags": {"attribute": "pitch-type", "count": "raw-count"},
                'title': f'Pitch type by count for {pitcher} v. {batter}',
                'downloadable': [{'filename': f"pitch_type{pitcher}_{batter}.csv",
                                "text": pitch_type.to_csv()}],
                'renderable': pdf_to_clean_html(pitch_type)
            },
        ]
    del sc
    return results


# def validate_inputs(inputs):
#     # date parameters alredy evaluated by webapp.
#     inputs = inputs["matchup"]
#     ew = {"matchup": {'errors': {}, 'warnings': {}}}
#     for pos in ["pitcher", "batter"]:
#         players = inputs.get(pos, None)
#         if players is None:
#             continue
#         if not isinstance(players, list):
#             players = [players]
#         for player in players:
#             choices = get_choices()
#             if player not in choices["choices"]:
#                 ew["matchup"]["errors"] = {pos: f"ERROR: player \"{player}\" not allowed"}
#     return ew

