import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models")))
import torch
import pandas as pd
import numpy as np
from model import MarchMadnessNN
#from new_model import MarchMadnessNN

r = sys.argv[1]

file_path = f"../data/processed/matchups{r}.csv"
matchups = pd.read_csv(file_path)

# Convert matchups data to tensor (assumes all columns are features)
feature_columns = matchups.columns  # Select all columns (since the last two are missing)
matchup_data = torch.tensor(matchups[feature_columns].values, dtype=torch.float32)
input_size = matchups.shape[1]

model = MarchMadnessNN(input_size)  # Initialize model
model.load_state_dict(torch.load('../models/model.pth'))
model.eval()  

# for game in matchups.csv
    # run model on game
    # store output somewhere

# Run model predictions
with torch.no_grad():
    predictions = model(matchup_data).numpy()  

# Append predictions to the dataframe
matchups["Win_Prob_Team1"] = predictions[:, 0]
matchups["Win_Prob_Team2"] = predictions[:, 1]

# Save updated CSV
#output_path = "matchups_with_predictions.csv"
#matchups.to_csv(output_path, index=False)

#print(f"Predictions saved to {output_path}")

# Load original roundr.csv
round_path = f"../data/processed/round{r}.csv"
round_df = pd.read_csv(round_path)

# Load matchups_with_predictions.csv (output from model)
# predictions_path = "matchups_with_predictions.csv"
# predictions_df = pd.read_csv(predictions_path)

# Extract only the win probabilities
win_probs = matchups[["Win_Prob_Team1", "Win_Prob_Team2"]]

# Append probabilities to round1.csv
round_df = pd.concat([round_df, win_probs], axis=1)
#round1_df.drop(columns=["team1_id","team2_id"], inplace=True)


# Save updated roundr.csv
output_path = f"predictions/round{r}_with_probs.csv"
round_df.to_csv(output_path, index=False)

print(f"Updated round{r}.csv with win probabilities saved as {output_path}")
