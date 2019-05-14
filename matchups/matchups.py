import os
import pandas as pd


CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))


def get_matchup(pitcher, batter, begin_date, end_date, df=None):
    if not df:
        path = os.path.join(CURRENT_PATH, "statcast.parquet")
        df = pd.read_parquet(path, engine="fastparquet")
    print('data read')
    df["date"] = pd.to_datetime(df["game_date"])
    bydate = df.loc[(df.date >= pd.Timestamp(start_date)) &
                    (df.date < pd.Timestamp(end_date))]
    print('filtered by date')

    pitcher = bydate.loc[(bydate["player_name"] == pitcher), :]
    batter = bydate.loc[(bydate["batter"] == batter), :]
    matchups = batter.loc[(batter["player_name"] == pitcher), :]

    return pitcher, batter, matchups