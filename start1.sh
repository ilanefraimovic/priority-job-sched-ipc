#!/bin/bash

# Absolute path to your project directory
PROJECT_DIR="$HOME/Desktop/OS-proj/OS-Proj"

# Start background tails with window titles via Terminal tabs
osascript <<EOF
tell application "Terminal"
    activate
    do script "cd \"$PROJECT_DIR\"; echo 'TAIL_TERMINAL'; tail -f shared_terminal.txt"
    delay 1
    do script "cd \"$PROJECT_DIR\"; echo 'TAIL_LOG'; tail -f log.txt"
end tell
EOF

# Give the tails a moment to launch
sleep 2

# Run the main Python program from the project directory
cd "$PROJECT_DIR"
python3 main.py

# Kill the tail processes after main.py finishes
pkill -f "tail -f shared_terminal.txt"
pkill -f "tail -f log.txt"

read -p "Press enter to continue..."