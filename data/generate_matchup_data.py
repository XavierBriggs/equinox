# generate matchups.csv 
# use teams.csv to create file simliar to train and test wo/ the probabilities 
# loop through some workflow to figure out matchups (similar to how we go through every game in generate_training_data.py)

# need ex: id1: s1=2025, q1=4, id2: s2=2025, q2=4

import pandas as pd
import sys


# Load raw matchups for round r
r = sys.argv[1]

round_path = f"processed/round{r}.csv"
teams_path = "processed/teams.csv"

round = pd.read_csv(round_path)
teams = pd.read_csv(teams_path)

# Assuming round_1.csv has `id1` and `id2` representing team IDs
# Assuming teams.csv has a `team_id` column and corresponding stats

# Merge team statistics for Team1 and Team2
matchups = round.merge(teams, left_on="team1_id", right_on="TeamID", suffixes=("_Team1", ""))
matchups = matchups.merge(teams, left_on="team2_id", right_on="TeamID", suffixes=("", "_Team2"))

# Filter for Season = 2025 and Quarter = 4
matchups = matchups[
    (matchups["Season"] == 2025) & (matchups["QuarterID"] == 4) 
    # (matchups["Team2_Season"] == 2025) & (matchups["Team2_QuarterID"] == 4)
]

matchups = matchups.drop_duplicates(subset=["team1_id", "team2_id"])

# Rename columns to match requested format
column_rename_map = {}
for col in teams.columns:
    if col != "team_id":  # Exclude the ID column
        column_rename_map[col + "_Team1"] = f"Team1_{col}"
        column_rename_map[col + "_Team2"] = f"Team2_{col}"

matchups.rename(columns=column_rename_map, inplace=True)
matchups.drop(columns=["team","away_team","team1_id","team2_id","Season","QuarterID","TeamID", "Team2_Season","Team2_QuarterID","Team2_TeamID"], inplace=True)
# Save the matchups dataset
output_path = f"processed/matchups{r}.csv"
matchups.to_csv(output_path, index=False)

print(f"Matchups file generated: {output_path}")




