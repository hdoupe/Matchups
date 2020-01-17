import json
import os
from datetime import datetime, date


from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource
from bokeh.embed import json_item
from bokeh.palettes import d3
from bokeh.models.widgets import Tabs, Panel
import pandas as pd
import numpy as np

import paramtools
from marshmallow import ValidationError

from matchups.utils import (CURRENT_PATH, renamedf, pdf_to_clean_html)
from matchups import __version__

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


def count_plot(df, title):
    p = figure(title=title, match_aspect=True)
    p.grid.visible = False
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
    pitch_types = df.pitch_type.unique()
    palette = d3["Category20"][max(3, pitch_types.shape[0])]
    for ix, (pitch_type, df) in enumerate(df.groupby("pitch_type")):
        p.circle(-df.plate_x, df.plate_z, legend_label=pitch_type,
                 color=palette[ix], size=10, alpha=1,
                 muted_color=palette[ix], muted_alpha=0.2)
    p.legend.click_policy = "hide"
    return p

def count_panels(df, main_title):
    p = count_plot(df, main_title)
    panels = [Panel(child=p, title="All counts")]

    for (balls, strikes), df in df.groupby(["balls", "strikes"]):
        panels.append(
            Panel(
                child=count_plot(df, f"{main_title} (balls={balls}, strikes={strikes})"),
                title=f"{balls}-{strikes}"
            )
        )

    tabs = Tabs(tabs=panels)
    return tabs


def append_output(df, title, renderable, downloadable):
    if len(df) == 0:
        renderable.append(
            {
                "media_type": "table",
                "title": title,
                "data": "<p><b>No matchups found.</b></p>"
            }
        )
    else:
        data = json_item(count_panels(df, title))
        renderable.append(
            {
                "media_type": "bokeh",
                "title": title,
                "data": data
            }
        )
    downloadable.append(
        {
            "media_type": "CSV",
            "title": title,
            "data": df.to_csv()
        }
    )


class MetaParams(paramtools.Parameters):
    array_first = True
    defaults = {
        "use_full_data": {
            "title": "Use Full Data",
            "description": "Flag that determines whether Matchups uses the 10 year data set or the 2018 data set.",
            "type": "bool",
            "value": True,
            "validators": {"choice": {"choices": [True, False]}}
        }
    }


class MatchupsParams(paramtools.Parameters):
    defaults_template = os.path.join(CURRENT_PATH, "defaults.json")

    def __init__(self, *args, **kwargs):
        players = pd.read_parquet(
            os.path.join(CURRENT_PATH, "players.parquet"),
            engine="fastparquet"
        )

        with open(self.defaults_template, "r") as f:
            self.defaults = json.loads(f.read())

        self.defaults["pitcher"]["validators"]["choice"]["choices"] = players.players.tolist()
        self.defaults["batter"]["validators"]["choice"]["choices"] = players.players.tolist()

        super().__init__(*args, **kwargs)

def get_inputs(meta_params_dict):
    meta_params = MetaParams()
    meta_params.adjust(meta_params_dict)
    params = MatchupsParams()
    params.set_state(use_full_data=meta_params.use_full_data.tolist())
    return {
        "meta_parameters": meta_params.dump(),
        "model_parameters": {"matchup": params.dump()}
    }


def validate_inputs(meta_param_dict, adjustment, errors_warnings):
    # matchups doesn't look at meta_param_dict for validating inputs.
    params = MatchupsParams()
    params.adjust(adjustment["matchup"], raise_errors=False)
    errors_warnings["matchup"]["errors"].update(params.errors)
    return {"errors_warnings": errors_warnings}


def get_matchup(meta_param_dict, adjustment):
    meta_params = MetaParams()
    meta_params.adjust(meta_param_dict)
    params = MatchupsParams()
    params.set_state(use_full_data=meta_params.use_full_data.tolist())
    params.adjust(adjustment["matchup"])
    print("getting data according to: ", meta_params.specification(), params.specification())
    if meta_params.use_full_data:
        path = os.path.join(CURRENT_PATH, "statcast.parquet")
    else:
        path = os.path.join(CURRENT_PATH, "statcast2018.parquet")
    scall = pd.read_parquet(path, engine="fastparquet")
    print('data read')
    scall["date"] = pd.to_datetime(scall["game_date"])
    sc = scall.loc[(scall.date >= pd.Timestamp(params.start_date[0]["value"])) &
                   (scall.date < pd.Timestamp(params.end_date[0]["value"]))]
    print('filtered by date')

    pitcher, batter = params.pitcher[0]["value"], params.batter[0]["value"]
    renderable = []
    downloadable = []
    pitcher_df = sc.loc[(scall["player_name"]==pitcher), :]
    append_output(pitcher_df, f"{pitcher} v. All batters", renderable, downloadable)

    batter_df = pitcher_df.loc[(scall["player_name"]==pitcher) & (scall["batter_name"]==batter), :]
    append_output(batter_df, f"{pitcher} v. {batter}", renderable, downloadable)

    return {
        "renderable": renderable,
        "downloadable": downloadable
    }
