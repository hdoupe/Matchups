import pandas as pd

people = pd.read_csv("people.csv")
all_players = pd.DataFrame.from_dict({
    "players": (people.name_first + " " + people.name_last).dropna().unique()
})

all_players.to_parquet("../matchups/players.parquet", engine="fastparquet")
