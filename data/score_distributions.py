import pandas as pd
import numpy as np

# Load tourney results
tourney_results = pd.read_csv("raw\MNCAATourneyDetailedResults.csv")

# Compute point differentials
tourney_results["PointDelta"] = tourney_results["WScore"] - tourney_results["LScore"]

# Compute mean and std dev of point differentials
mean_delta = tourney_results["PointDelta"].mean()
std_delta = tourney_results["PointDelta"].std()

print(f"Mean Point Differential: {mean_delta:.2f}")
print(f"Standard Deviation of Point Differentials: {std_delta:.2f}")
