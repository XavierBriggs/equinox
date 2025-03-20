import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from scipy.special import erf


def generate_training_data(tourney_results_csv, team_feature_matrix_csv, train_csv, test_csv, test_size=0.2, random_seed=3627):
    # Load the March Madness tournament results
    tourney_results = pd.read_csv(tourney_results_csv)
    
    # Load the team feature matrix (now includes QuarterID)
    team_features = pd.read_csv(team_feature_matrix_csv)
    
    # Ensure QuarterID is present in both datasets
    if "QuarterID" not in team_features.columns:
        team_features["QuarterID"] = 4  # Default all rows to QuarterID = 4

    tourney_results["QuarterID"] = pd.cut(
        tourney_results["DayNum"], 
        bins=[-1, 33, 66, 99, 132], 
        labels=[1, 2, 3, 4]  # Quarter 1, 2, 3, or 4
    ).astype(int)


    # Create a mapping (Season, QuarterID, TeamID) -> Team Stats
    team_map = {}
    for _, row in team_features.iterrows():
        key = (row["Season"], row["QuarterID"], row["TeamID"])  # Now includes QuarterID
        team_map[key] = row.drop(["Season", "QuarterID", "TeamID"]).values  # Store only feature values
    
    # Prepare training data
    X = []
    Y = []
    
    for _, row in tourney_results.iterrows():
        season = row["Season"]
        quarter = row["QuarterID"]  # Now match using QuarterID too
        team_w = row["WTeamID"]  # Winning Team
        team_l = row["LTeamID"]  # Losing Team
        score_w = row["WScore"]
        score_l = row["LScore"]
        delta = score_w - score_l  # Margin of victory
        
        # Get team vectors from mapping using (Season, QuarterID, TeamID)
        if (season, quarter, team_w) in team_map and (season, quarter, team_l) in team_map:
            team_w_vector = team_map[(season, quarter, team_w)]
            team_l_vector = team_map[(season, quarter, team_l)]

            sigma = 10  # Adjusted probability scaling
            p = lambda delta: 0.5 + 0.5 * erf(delta / sigma)
            
            # Randomly shuffle order of teams
            if np.random.rand() > 0.5:
                matchup_vector = list(team_w_vector) + list(team_l_vector)
                y_label = [p(delta), 1 - p(delta)]  # Team 1 wins
            else:
                matchup_vector = list(team_l_vector) + list(team_w_vector)
                y_label = [1 - p(delta), p(delta)]  # Team 2 wins
            
            X.append(matchup_vector)
            Y.append(y_label)
    
    # Convert to DataFrame
    feature_columns = list(team_features.columns[3:])  # Skip Season, QuarterID, and TeamID
    columns = [f"Team1_{col}" for col in feature_columns] + [f"Team2_{col}" for col in feature_columns]
    X_df = pd.DataFrame(X, columns=columns)
    Y_df = pd.DataFrame(Y, columns=["Win_Prob_Team1", "Win_Prob_Team2"])
    
    # Combine X and Y into a single DataFrame
    data = pd.concat([X_df, Y_df], axis=1)
    
    # Train-test split
    train_data, test_data = train_test_split(data, test_size=test_size, random_state=random_seed)
    
    # Save training and testing data
    train_data.to_csv(train_csv, index=False)
    test_data.to_csv(test_csv, index=False)
    
    print(f"Training data saved as {train_csv}")
    print(f"Testing data saved as {test_csv}")

# Example usage
generate_training_data(
    "raw\MRegularSeasonDetailedResults_with_poss.csv",
    "processed/teams.csv",
    "../models/data/training_data.csv",
    "../models/data/testing_data.csv"
)

