#!/bin/bash

# =================CONFIGURATION=================
PROJECT_DIR="/Volumes/MOVESPEED/下载/AIcode/KunlunGrowth"
VENV_PYTHON="$PROJECT_DIR/tools/KGCRM/venv/bin/python3"
SCRIPT_PATH="$PROJECT_DIR/tools/seo/auto_seo.py"
LOG_FILE="$PROJECT_DIR/logs/seo_cron.log"

# =================EXECUTION=================
echo "Starting Daily SEO Job: $(date)" >> "$LOG_FILE"

# Change to project dir to ensure relative paths work if needed
cd "$PROJECT_DIR"

# Load environment variables if .env exists
if [ -f ".env" ]; then
    export $(cat .env | xargs)
fi

# Run the python script
"$VENV_PYTHON" "$SCRIPT_PATH" >> "$LOG_FILE" 2>&1

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Success: SEO Automation completed at $(date)" >> "$LOG_FILE"
else
    echo "Error: SEO Automation failed with code $EXIT_CODE at $(date)" >> "$LOG_FILE"
fi

echo "----------------------------------------" >> "$LOG_FILE"
