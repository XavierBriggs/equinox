#!/bin/bash

echo "Processing game data..."
python3 process_quarter_data.py

echo "Generating training data..."
python3 generate_training_data.py

echo "Generating round 1 matchups..."
ROUND=1
python3 generate_matchup_data.py $ROUND

echo "Complete"