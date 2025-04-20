#!/bin/bash
echo "
 -----------------------------------------------------------------------------
 Configuration Script for TikTok-to-Twitter Bot
 -----------------------------------------------------------------------------
 Instructions:
 1. Fill in your actual credentials below.
 2. !! IMPORTANT !! Do NOT commit your env file with your real credentials
    to version control (like Git). Add it to your .gitignore file.
 -----------------------------------------------------------------------------
#
"

# Create and activate virtual environment
#echo "Creating virtual enviroment..."
#pip install virtualenv
#python3 -m venv env
#source env/bin/activate

# Install dependencies from requirements file
# echo "Installing dependencies"
#pip install -r requirements.txt

# Telegram bot credentials
echo "Configuring bot credentials..."
echo "Enter your telegram bot token (get from BotFather):"
read TELEGRAM_TOKEN

# Twitter API credentials
echo "Enter your TWITTER_CONSUMER_KEY:"
read TWITTER_CONSUMER_KEY
echo "Enter your TWITTER_CONSUMER_SECRET:"
read TWITTER_CONSUMER_SECRET
echo "Enter your TWITTER_ACCESS_TOKEN:"
read TWITTER_ACCESS_TOKEN
echo "Enter your TWITTER_ACCESS_TOKEN_SECRET:"
read TWITTER_ACCESS_TOKEN_SECRET

# Directory to store downloaded videos (with default)
echo "Enter directory to store downloaded videos (default: videos):"
VIDEOS_DIR="videos"
read videos_input
if [ ! -z "$videos_input" ]; then
    VIDEOS_DIR="$videos_input"
fi

# Log file path (with default)
echo "Enter log file path (default: download.log):"
LOG_FILE="download.log"
read log_input
if [ ! -z "$log_input" ]; then
    LOG_FILE="$log_input"
fi

# Create a .env file with all credentials
echo "Creating .env file with credentials..."
cat > .env << EOF
TELEGRAM_TOKEN=$TELEGRAM_TOKEN
TWITTER_CONSUMER_KEY=$TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET=$TWITTER_CONSUMER_SECRET
TWITTER_ACCESS_TOKEN=$TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET=$TWITTER_ACCESS_TOKEN_SECRET
VIDEOS_DIR=$VIDEOS_DIR
LOG_FILE=$LOG_FILE
EOF

echo "Configuration complete! .env file created."
echo "Make sure to add .env to your .gitignore file."

# Create videos directory if it doesn't exist
mkdir -p "$VIDEOS_DIR"

echo "Setup completed successfully."


