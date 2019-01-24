import json
import os


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


def get_choices():
    with open(os.path.join(CURRENT_PATH, "playerchoices.json")) as f:
        return json.loads(f.read())


def pdf_to_clean_html(pdf):
    """Takes a PDF and returns an HTML table without any deprecated tags or
    irrelevant styling"""
    return (pdf.to_html()
            .replace(' border="1"', '')
            .replace(' style="text-align: right;"', ''))


def renamedf(df, normalized=True):
    index_map = {
        "balls": "Balls",
        "strikes": "Strikes",
        "type": "Pitch Outcome",
        "pitch_type": "Pitch Type",
    }

    template_col_map = {
        "type": "{op} of pitch outcome by count",
        "pitch_type": "{op} of pitch type by count",
    }

    if normalized:
        op = "Proportion"
    else:
        op = "Count"

    # rename index
    df.index.names = [index_map[oldname] for oldname in df.index.names]

    col_map = {}
    for oldname, newname in template_col_map.items():
        if oldname in df.columns:
            col_map[oldname] = newname.format(op=op)

    return df.rename(columns=col_map)


def validate_inputs(inputs):
    # date parameters alredy evaluated by webapp.
    inputs = inputs["matchup"]
    ew = {"matchup": {'errors': {}, 'warnings': {}}}
    for pos in ["pitcher", "batter"]:
        players = inputs.get(pos, None)
        if players is None:
            continue
        if not isinstance(players, list):
            players = [players]
        for player in players:
            choices = get_choices()
            if player not in choices["choices"]:
                ew["matchup"]["errors"] = {pos: f"ERROR: player \"{player}\" not allowed"}
    return ew
