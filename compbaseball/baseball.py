import json
import os

import pandas as pd

from compbaseball.utils import (CURRENT_PATH, renamedf,
                                validate_inputs, pdf_to_clean_html)


def get_inputs(use_2018=True):
    with open(os.path.join(CURRENT_PATH, "inputs.json")) as f:
        return {"matchup": json.loads(f.read())}


def parse_inputs(inputs, jsonparams, errors_warnings, use_2018=True):
    ew = validate_inputs(inputs)
    return (inputs, {"matchup": json.dumps(inputs, indent=4)}, ew)


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
    agg_pitch_outcome_normalized = renamedf(
        pd.DataFrame(gb["type"].value_counts(normalize=True)),
        normalized=True
    )
    del gb

    gb = sc.groupby(
        ["balls", "strikes"])
    agg_pitch_type_normalized = renamedf(
        pd.DataFrame(gb["pitch_type"].value_counts(normalize=True)),
        normalized=True
    )
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
            pitch_outcome_normalized = renamedf(
                pd.DataFrame(gb["type"].value_counts(normalize=True)),
                normalized=True
            )
            pitch_outcome = renamedf(
                pd.DataFrame(gb["type"].value_counts()),
                normalized=False
            )
            del gb

            gb = pdf.loc[(pdf["player_name"]==pitcher) & (pdf["batter_name"]==batter), :].groupby(
                ["balls", "strikes"])
            pitch_type_normalized = renamedf(
                pd.DataFrame(gb["pitch_type"].value_counts(normalize=True)),
                normalized=True
            )
            pitch_type = renamedf(
                pd.DataFrame(gb["pitch_type"].value_counts()),
                normalized=False
            )
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
