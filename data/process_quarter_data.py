#!/usr/bin/env python3
import pandas as pd

def compute_team_per_quarter_matrix(csv_file):
    # Load the CSV file
    df = pd.read_csv(csv_file)
    
    # Define quarters based on DayNum
    df["QuarterID"] = pd.cut(df["DayNum"], bins=[-1, 33, 66, 99, 132], labels=[1, 2, 3, 4]).astype(int)
    
    # Estimate possessions for winning and losing teams
    df["WPoss"] = df["WFGA"] - (df["WOR"] / (df["WOR"] + df["LDR"])) * (df["WFGA"] - df["WFGM"]) * 1.07 + df["WTO"] + (0.44 * df["WFTA"])
    df["LPoss"] = df["LFGA"] - (df["LOR"] / (df["LOR"] + df["WDR"])) * (df["LFGA"] - df["LFGM"]) * 1.07 + df["LTO"] + (0.44 * df["LFTA"])
    
    # Compute per-possession stats for both winning and losing teams
    for prefix in ["W", "L"]:
        df[f"{prefix}TS%"] = 0.5 * df[f"{prefix}Score"] / (df[f"{prefix}FGA"] + 0.44 * df[f"{prefix}FTA"])
        df[f"{prefix}eFG%"] = (df[f"{prefix}FGM"] + 0.5 * df[f"{prefix}FGM3"]) / df[f"{prefix}FGA"]
        df[f"{prefix}TO%"] = df[f"{prefix}TO"] / df[f"{prefix}Poss"]
        df[f"{prefix}OREB%"] = df[f"{prefix}OR"] / (df[f"{prefix}OR"] + df[f"{'L' if prefix == 'W' else 'W'}DR"])
        df[f"{prefix}DREB%"] = df[f"{prefix}DR"] / (df[f"{prefix}DR"] + df[f"{'L' if prefix == 'W' else 'W'}OR"])
        df[f"{prefix}FTR"] = df[f"{prefix}FTA"] / df[f"{prefix}FGA"]
        df[f"{prefix}3PAr"] = df[f"{prefix}FGA3"] / df[f"{prefix}FGA"]
        df[f"{prefix}AST/TO"] = df[f"{prefix}Ast"] / (df[f"{prefix}TO"] + 1e-6)
        df[f"{prefix}STL%"] = df[f"{prefix}Stl"] / df[f"{prefix}Poss"]
        df[f"{prefix}BLK%"] = df[f"{prefix}Blk"] / df[f"{prefix}FGA"]
    
    # Aggregate per team per quarter
    team_stats = {}
    for _, row in df.iterrows():
        for prefix, team, score, poss in [("W", row["WTeamID"], row["WScore"], row["WPoss"]),
                                          ("L", row["LTeamID"], row["LScore"], row["LPoss"])]:
            key = (row["Season"], row["QuarterID"], team)
            if key not in team_stats:
                team_stats[key] = {
                    "TeamID": team,
                    "Games": 0, "TotalPoss": 0, "TS%": 0, 
                    "eFG%": 0, "TO%": 0, "OREB%": 0, "DREB%": 0, "FTR": 0,
                    "3PAr": 0, "AST/TO": 0, "STL%": 0, "BLK%": 0,
                    "PointsPerPoss": 0, "AdjO": 0, "AdjD": 0
                }
            
            team_stats[key]["Games"] += 1
            team_stats[key]["TotalPoss"] += poss
            team_stats[key]["TS%"] += row[f"{prefix}TS%"] * poss
            team_stats[key]["eFG%"] += row[f"{prefix}eFG%"] * poss
            team_stats[key]["TO%"] += row[f"{prefix}TO%"] * poss
            team_stats[key]["OREB%"] += row[f"{prefix}OREB%"] * poss
            team_stats[key]["DREB%"] += row[f"{prefix}DREB%"] * poss
            team_stats[key]["FTR"] += row[f"{prefix}FTR"] * poss
            team_stats[key]["3PAr"] += row[f"{prefix}3PAr"] * poss
            team_stats[key]["AST/TO"] += row[f"{prefix}AST/TO"] * poss
            team_stats[key]["STL%"] += row[f"{prefix}STL%"] * poss
            team_stats[key]["BLK%"] += row[f"{prefix}BLK%"] * poss
            team_stats[key]["PointsPerPoss"] += score * poss

    # Compute Adjusted Offensive and Defensive Ratings
    season_avg_ppp = {
    season: sum(team_stats[(s, q, t)]["PointsPerPoss"] / team_stats[(s, q, t)]["TotalPoss"]
                for (s, q, t) in team_stats.keys() if s == season) /
            len([t for (s, q, t) in team_stats.keys() if s == season])
    for season in set(s for s, q, t in team_stats.keys())
}


    for (season, quarter, team), stats in team_stats.items():
        opponents = [opponent for (s, q, opponent) in team_stats.keys() if s == season and opponent != team]
        if opponents:
            avg_opponent_def = sum(team_stats[(season, quarter, opp)]["PointsPerPoss"] / team_stats[(season, quarter, opp)]["TotalPoss"]
                                   for opp in opponents) / len(opponents)
            avg_opponent_off = sum(team_stats[(season, quarter, opp)]["PointsPerPoss"] / team_stats[(season, quarter, opp)]["TotalPoss"]
                                   for opp in opponents) / len(opponents)

            stats["AdjO"] = (stats["PointsPerPoss"] / stats["TotalPoss"]) * (avg_opponent_def / season_avg_ppp[season])
            stats["AdjD"] = (stats["PointsPerPoss"] / stats["TotalPoss"]) * (avg_opponent_off / season_avg_ppp[season])

    # Normalize per possession
    team_features = []
    for (season, quarter, team), stats in team_stats.items():
        row = [season, quarter, team]
        row.extend([
            stats["TS%"] / stats["TotalPoss"],
            stats["eFG%"] / stats["TotalPoss"],
            stats["TO%"] / stats["TotalPoss"],
            stats["OREB%"] / stats["TotalPoss"],
            stats["DREB%"] / stats["TotalPoss"],
            stats["FTR"] / stats["TotalPoss"],
            stats["3PAr"] / stats["TotalPoss"],
            stats["AST/TO"] / stats["TotalPoss"],
            stats["STL%"] / stats["TotalPoss"],
            stats["BLK%"] / stats["TotalPoss"],
            stats["PointsPerPoss"] / stats["TotalPoss"],
            stats["AdjO"],
            stats["AdjD"]
        ])
        team_features.append(row)
    
    # Convert to DataFrame
    feature_columns = ["Season", "QuarterID", "TeamID", "TS%", "eFG%", "TO%", "OREB%", "DREB%", "FTR", "3PAr", "AST/TO", "STL%", "BLK%", "PointsPerPoss", "AdjO", "AdjD"]
    team_matrix = pd.DataFrame(team_features, columns=feature_columns)
    return team_matrix

# Usage example:
team_matrix = compute_team_per_quarter_matrix("raw/MRegularSeasonDetailedResults_with_poss.csv")
team_matrix.to_csv("processed/teams.csv", index=False)
print("Done")
