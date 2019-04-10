import json
import os

import pandas as pd

from paramtools.parameters import Parameters
from marshmallow import ValidationError

from matchups.utils import (CURRENT_PATH, renamedf, pdf_to_clean_html)

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


class MatchupsParams(Parameters):
    schema = os.path.join(CURRENT_PATH, "schema.json")
    defaults = os.path.join(CURRENT_PATH, "defaults.json")


def get_inputs(use_full_data=True):
    params = MatchupsParams()
    spec = params.specification(meta_data=True, use_full_data=use_full_data)
    return {"matchup": spec}


def parse_inputs(inputs, jsonparams, errors_warnings, use_full_data=True):
    adjustments = inputs["matchup"]
    params = MatchupsParams()
    params.adjust(adjustments, raise_errors=False)
    errors_warnings["matchup"]["errors"].update(params.errors)
    return (inputs, {"matchup": json.dumps(inputs, indent=4)}, errors_warnings)


def get_matchup(use_full_data, user_mods):
    adjustment = user_mods["matchup"]
    params = MatchupsParams()
    params.set_state(use_full_data=use_full_data)
    params.adjust(adjustment)
    print("getting data according to: ", use_full_data, params.specification())
    results = {'outputs': [], 'aggr_outputs': [], 'meta': {"task_times": [0]}}
    if use_full_data:
        path = os.path.join(CURRENT_PATH, "statcast.parquet")
    else:
        path = os.path.join(CURRENT_PATH, "statcast2018.parquet")
    scall = pd.read_parquet(path, engine="pyarrow")
    print('data read')
    scall["date"] = pd.to_datetime(scall["game_date"])
    sc = scall.loc[(scall.date >= pd.Timestamp(params.start_date[0]["value"])) &
                   (scall.date < pd.Timestamp(params.end_date[0]["value"]))]
    del scall
    print('filtered by date')

    pitcher, batters = params.pitcher[0]["value"], params.batter[0]["value"]
    pvall = sc.loc[sc["player_name"]==pitcher, :]
    print("pvall", pvall)
    if len(pvall) == 0:
        agg_pitch_outcome_normalized = pd.DataFrame()
    else:
        gb = (pd.DataFrame(pvall.groupby(
            ["balls", "strikes"])["type"]
            .value_counts(normalize=True)
            ))
        agg_pitch_outcome_normalized = renamedf(
            gb,
            normalized=True
        )
        del gb

    if len(pvall) == 0:
        agg_pitch_type_normalized = pd.DataFrame()
    else:
        gb = (pd.DataFrame(pvall.groupby(
            ["balls", "strikes"])["pitch_type"]
            .value_counts(normalize=True)
            ))
        agg_pitch_type_normalized = renamedf(
            gb,
            normalized=True
        )
        del gb
    del pvall

    results['aggr_outputs'].append({
        'tags': {'attribute': 'pitch-outcome'},
        'title': f'Pitch outcome by count for {pitcher} versus all players',
        'downloadable': [{'filename': 'pitch_outcome.csv',
                          'text': agg_pitch_outcome_normalized.to_csv()}],
        'renderable': pdf_to_clean_html(agg_pitch_outcome_normalized)})
    results['aggr_outputs'].append({
        'tags': {'attribute': 'pitch-type'},
        'title': f'Pitch type by count for {pitcher} versus all players',
        'downloadable': [{'filename': 'pitch_type.csv',
                          'text': agg_pitch_type_normalized.to_csv()}],
        'renderable': pdf_to_clean_html(agg_pitch_type_normalized)})


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
