#!/bin/bash

# Letterboxd Sync Runner Script
# This script handles log rotation and optimized execution for cron jobs

# Set the project directory
PROJECT_DIR="/Users/larson/Documents/Coding/letterboxd-sync"
cd "$PROJECT_DIR" || exit 1

# Create logs directory if it doesn't exist
mkdir -p logs

# Rotate cron log if it's getting too large (>10MB)
if [ -f "logs/cron.log" ]; then
    LOG_SIZE=$(stat -f%z "logs/cron.log" 2>/dev/null || echo 0)
    if [ "$LOG_SIZE" -gt 10485760 ]; then  # 10MB in bytes
        mv "logs/cron.log" "logs/cron.log.$(date +%Y%m%d_%H%M%S)"
        echo "$(date): Rotated large cron log file" > "logs/cron.log"
    fi
fi

# Run the sync script with production mode enabled
export PRODUCTION=1
export DEBUG=0

# Execute the main script and capture output, filtering out DEBUG messages and TMDB debug logs
/usr/bin/env python3 main.py 2>&1 | grep -v "\[DEBUG\]" | grep -v "Searching for" | grep -v "Found TMDB ID" | grep -v "No results for" | tee -a logs/cron.log

# Clean up old log files (older than 7 days)
find logs -name "*.log*" -mtime +7 -delete 2>/dev/null

# Clean up old cache files (older than 30 days)
find cache -name "*.json" -mtime +30 -delete 2>/dev/null 