#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Script version
VERSION="1.0.0"

# Default values
DEFAULT_VIDEOS_DIR="videos"
DEFAULT_LOG_FILE="bot.log"
ENV_FILE=".env"
REQUIREMENTS_FILE="requirements.txt"

# Banner function
print_banner() {
    clear
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║              TikTok-to-Twitter Bot Configuration               ║"
    echo "║                        Version ${VERSION}                           ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo "This script will set up the necessary environment for your bot."
    echo "You'll need your Telegram and Twitter API credentials ready."
    echo ""
}

# Error handling function
handle_error() {
    echo -e "${RED}ERROR: $1${NC}"
    exit 1
}

# Success message function
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Warning message function
print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

# Check if directory exists, create if not
ensure_directory() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1" || handle_error "Failed to create directory: $1"
        print_success "Created directory: $1"
    else
        print_success "Directory already exists: $1"
    fi
}

# Check if .gitignore exists and contains .env
update_gitignore() {
    if [ -f ".gitignore" ]; then
        if grep -q "^${ENV_FILE}$" .gitignore; then
            print_success ".env already in .gitignore"
        else
            echo "${ENV_FILE}" >> .gitignore
            print_success "Added .env to .gitignore"
        fi
    else
        echo "${ENV_FILE}" > .gitignore
        print_success "Created .gitignore with .env entry"
    fi
}

# Setup virtual environment
setup_venv() {
    echo -e "${BLUE}Setting up virtual environment...${NC}"
    
    if [ ! -d "env" ]; then
        echo "Creating virtual environment..."
        python3 -m venv env || handle_error "Failed to create virtual environment"
        print_success "Virtual environment created"
    else
        print_success "Virtual environment already exists"
    fi
    
    echo "Activating virtual environment..."
    source env/bin/activate || handle_error "Failed to activate virtual environment"
    print_success "Virtual environment activated"
    
    if [ -f "${REQUIREMENTS_FILE}" ]; then
        echo "Installing dependencies from requirements.txt..."
        pip install -r "${REQUIREMENTS_FILE}" || handle_error "Failed to install dependencies"
        print_success "Dependencies installed"
    else
        print_warning "No requirements.txt found. Skipping dependency installation."
    fi
}

# Get credentials from user
get_credentials() {
    echo -e "${BLUE}Please enter your API credentials:${NC}"
    echo ""
    
    # Check if .env already exists
    if [ -f "${ENV_FILE}" ]; then
        echo -e "${YELLOW}An .env file already exists. Do you want to overwrite it? (y/n)${NC}"
        read -r overwrite
        if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
            echo "Configuration cancelled. Existing .env file preserved."
            exit 0
        fi
    fi
    
    # Telegram credentials
    echo -e "${BLUE}Telegram Bot Configuration:${NC}"
    echo "Enter your Telegram bot token (from BotFather):"
    read -r TELEGRAM_TOKEN
    
    # Twitter API credentials
    echo -e "${BLUE}Twitter API Configuration:${NC}"
    echo "Enter your Twitter Consumer Key:"
    read -r TWITTER_CONSUMER_KEY
    echo "Enter your Twitter Consumer Secret:"
    read -r TWITTER_CONSUMER_SECRET
    echo "Enter your Twitter Access Token:"
    read -r TWITTER_ACCESS_TOKEN
    echo "Enter your Twitter Access Token Secret:"
    read -r TWITTER_ACCESS_TOKEN_SECRET
    
    # Additional configuration
    echo -e "${BLUE}Additional Configuration:${NC}"
    echo "Enter directory to store downloaded videos (default: ${DEFAULT_VIDEOS_DIR}):"
    read -r videos_input
    VIDEOS_DIR=${videos_input:-$DEFAULT_VIDEOS_DIR}
    
    echo "Enter log file path (default: ${DEFAULT_LOG_FILE}):"
    read -r log_input
    LOG_FILE=${log_input:-$DEFAULT_LOG_FILE}
}

# Create configuration file
create_env_file() {
    echo -e "${BLUE}Creating .env file...${NC}"
    
    # Create a .env file with all credentials
    cat > "${ENV_FILE}" << EOF
# Telegram Bot Configuration
TELEGRAM_TOKEN=$TELEGRAM_TOKEN

# Twitter API Credentials
TWITTER_CONSUMER_KEY=$TWITTER_CONSUMER_KEY
TWITTER_CONSUMER_SECRET=$TWITTER_CONSUMER_SECRET
TWITTER_ACCESS_TOKEN=$TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET=$TWITTER_ACCESS_TOKEN_SECRET

# App Configuration
VIDEOS_DIR=$VIDEOS_DIR
LOG_FILE=$LOG_FILE

# Configuration created on $(date)
EOF
    
    # Check if .env was created successfully
    if [ -f "${ENV_FILE}" ]; then
        print_success ".env file created successfully"
    else
        handle_error "Failed to create .env file"
    fi
}

# Main function to run the script
main() {
    print_banner
    
    # Uncomment these lines if you want to set up virtual environment by default
     setup_venv
    
    get_credentials
    create_env_file
    ensure_directory "${VIDEOS_DIR}"
    update_gitignore
    
    echo ""
    echo -e "${GREEN}══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ Configuration completed successfully!${NC}"
    echo -e "${GREEN}══════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Run 'source env/bin/activate' to activate the virtual environment"
    echo "2. Run your bot with 'python bot.py' or the appropriate command"
    echo ""
    print_warning "Remember: Never commit your .env file to version control!"
}

# Run the main function
main
