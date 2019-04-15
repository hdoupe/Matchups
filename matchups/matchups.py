import json
import os

from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource
from bokeh.transform import linear_cmap
from bokeh.util.hex import hexbin
from bokeh.embed import components
import pandas as pd

from paramtools.parameters import Parameters
from marshmallow import ValidationError

from matchups.utils import (CURRENT_PATH, renamedf, pdf_to_clean_html)

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


def plot(df):
    bins = hexbin(-df.plate_x.values, df.plate_z.values, 0.1)
    p = figure(title="Matchups Plot", tools="wheel_zoom,pan,reset",
               match_aspect=True, background_fill_color='#440154')
    p.grid.visible = False
    p.hex_tile(q="q", r="r", size=0.1, line_color=None, source=bins,
            fill_color=linear_cmap('counts', 'Viridis256', 0, max(bins.counts)))
    strike_zone_cds = ColumnDataSource({'x': [-8.5 / 12, 8.5 / 12],
                                        'x_side1': [-8.5 / 12, -8.5 / 12],
                                        'x_side2': [8.5 / 12, 8.5 / 12],
                                        'top': [3.0, 3.0],
                                        'bottom': [1.2, 1.2],
                                        'side1': [3.0, 1.2],
                                        'side2': [1.2, 3.0]})
    p.line(x='x', y='top', line_width=3, color='red', source=strike_zone_cds)
    p.line(x='x', y='bottom', line_width=3, color='red',
            source=strike_zone_cds)
    p.line(x='x_side1', y='side1', line_width=3, color='red',
            source=strike_zone_cds)
    p.line(x='x_side2', y='side2', line_width=3, color='red',
    source=strike_zone_cds)

    js, div = components(p)
    return js, div

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
    scall = pd.read_parquet(path, engine="fastparquet")
    print('data read')
    scall["date"] = pd.to_datetime(scall["game_date"])
    sc = scall.loc[(scall.date >= pd.Timestamp(params.start_date[0]["value"])) &
                   (scall.date < pd.Timestamp(params.end_date[0]["value"]))]
    print('filtered by date')

    pitcher, batters = params.pitcher[0]["value"], params.batter[0]["value"]
    renderable = []
    downloadable = []
    for batter in batters:
        pdf = sc.loc[(scall["player_name"]==pitcher) & (scall["batter_name"]==batter), :]
        if len(pdf) == 0:
            js = ""
            div = "<p><b>No matchups found for date range.</b></p>"
        else:
            js, div = plot(pdf)
        renderable.append(
            {
                "media_type": "bokeh",
                "title": f"{pitcher} v. {batter}",
                "data": {
                    "javascript": js,
                    "html": div
                }
            }
        )
        downloadable.append(
            {
                "media_type": "CSV",
                "title": f"{pitcher} v. {batter}",
                "data": {
                    "CSV": pdf.to_csv()
                }
            }
        )
        del pdf
    return {
        "renderable": renderable,
        "downloadable": downloadable
    }
