import pandas as pd

# people from: https://raw.githubusercontent.com/chadwickbureau/register/master/data/people.csv
# sc from:
# from pybaseball import statcast
# data = statcast(start_dt='2008-01-01', end_dt='2018-11-30')
# full statcast.csv.gzip file available upon request.

people = pd.read_csv("people.csv")
sc = pd.read_csv("statcast.csv.gzip", compression="gzip")
people["batter_name"] = people.name_first + " " + people.name_last
merged = pd.merge(
    sc,
    people.loc[:, ["key_mlbam", "batter_name"]],
    how="left",
    left_on="batter",
    right_on="key_mlbam",
)
cols2keep = [
    "player_name",
    "batter_name",
    "pitch_type",
    "game_date",
    "release_speed",
    "events",
    "launch_speed",
    "woba_value",
    "bb_type",
    "balls",
    "strikes",
    "outs_when_up",
    "at_bat_number",
    "type",
]
sc = merged.loc[:, cols2keep]
sc.to_parquet("statcast.parquet", engine="pyarrow")
sc.to_parquet(
    "https://s3.amazonaws.com/hank-statcast/statcast.parquet", engine="pyarrow"
)

sc["date"] = pd.to_datetime(merged["game_date"])
recent = sc.loc[sc.date > "2018-01-01", :]
recent.drop(columns=["date"], inplace=True)
recent.to_parquet("statcast2018.parquet", engine="pyarrow")
recent.to_parquet(
    "https://s3.amazonaws.com/hank-statcast/statcast2018.parquet", engine="pyarrow"
)
