import pandas as pd

people = pd.read_csv("people.csv")
people = people.loc[people.mlb_played_last > 2009, :]
all_players = pd.DataFrame.from_dict({
    "players": sorted((people.name_first + " " + people.name_last).dropna().unique())
})

all_players.to_parquet("../matchups/players.parquet", engine="fastparquet")
