# this will be made obsolete by monte carlo sims 

import pandas as pd
import sys


r = int(sys.argv[1])  # r > 1
t = r - 1  # previous round number

preds_t = f"../src/predictions/round{t}_with_probs.csv"
round_data = pd.read_csv(preds_t)

required_columns = ["team", "away_team", "team1_id", "team2_id", "Win_Prob_Team1", "Win_Prob_Team2"]
for col in required_columns:
    if col not in round_data.columns:
        print(f"Error: Column '{col}' not found in {preds_t}")
        sys.exit(1)

winners = []
for i in range(0, len(round_data), 2):
    game1 = round_data.iloc[i]
    game2 = round_data.iloc[i + 1]

    if game1["Win_Prob_Team1"] > game1["Win_Prob_Team2"]:
        winner1 = (game1["team"], game1["team1_id"])
    else:
        winner1 = (game1["away_team"], game1["team2_id"])

    if game2["Win_Prob_Team1"] > game2["Win_Prob_Team2"]:
        winner2 = (game2["team"], game2["team1_id"])
    else:
        winner2 = (game2["away_team"], game2["team2_id"])

    winners.append([winner1[0], winner2[0], winner1[1], winner2[1]])

round_next = pd.DataFrame(winners, columns=["team", "away_team", "team1_id", "team2_id"])

round_next_file = f"../data/processed/round{r}.csv"
round_next.to_csv(round_next_file, index=False)

print(f"Round {r} matchups saved to {round_next_file}")