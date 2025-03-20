#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: ./play_round.sh <round_number>"
    exit 1
fi

ROUND=$1

echo "Running predictor.py for round $ROUND..."
python3 predictor.py $ROUND

echo "Running generate_r2.py for round $ROUND..."
NEXT=$((ROUND + 1))
python3 generate_rr.py $NEXT

echo "Running generate_matchup_data.py for round $NEXT..."
NEXT=$((ROUND + 1))
cd ../data || EXIT
python3 generate_matchup_data.py $NEXT
cd ../src || EXIT

echo "Round $ROUND processing complete!"
