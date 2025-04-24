import tweepy
import os
import logging
import sys
from yt_dlp import YoutubeDL
import re
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes
)
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
VIDEOS_DIR = "videos"
LOG_FILE = "download.log"
os.makedirs(VIDEOS_DIR, exist_ok=True)

# --- Load Credentials from Environment Variables ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CONSUMER_KEY = os.environ.get("CONSUMER_KEY")
CONSUMER_SECRET = os.environ.get("CONSUMER_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")

# --- Validate Credentials ---
# Basic check to ensure variables are loaded. Exit if any are missing.
missing_creds = []
if not TELEGRAM_TOKEN: missing_creds.append("TELEGRAM_TOKEN")
#if not CONSUMER_KEY: missing_creds.append("CONSUMER_KEY")
#if not CONSUMER_SECRET: missing_creds.append("CONSUMER_SECRET")
#if not ACCESS_TOKEN: missing_creds.append("ACCESS_TOKEN")
#if not ACCESS_TOKEN_SECRET: missing_creds.append("ACCESS_TOKEN_SECRET")

if missing_creds:
    print(f"ERROR: Missing required environment variables: {', '.join(missing_creds)}")
    print("Please ensure you have sourced the 'set_credentials.sh' file correctly.")
    sys.exit(1) # Exit the script if credentials are missing

# --- Set Up Logging ---
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s\t%(levelname)s\t%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.info("Bot starting...") # Log bot start
"""
# --- Twitter API Setup ---
try:
    auth = tweepy.OAuth1UserHandler(
        CONSUMER_KEY,
        CONSUMER_SECRET,
        ACCESS_TOKEN,
        ACCESS_TOKEN_SECRET
    )
    api = tweepy.API(auth)
    # Verify credentials
    api.verify_credentials()
    logging.info("Successfully connected to Twitter API.")
except Exception as e:
    logging.error(f"Failed to authenticate with Twitter API: {e}")
    print(f"ERROR: Failed to authenticate with Twitter API: {e}")
    print("Please check your Twitter API credentials in 'set_credentials.sh' and ensure they are correct and have the necessary permissions.")
    sys.exit(1) # Exit if Twitter auth fails
"""

# --- Conversation states ---
URL, CAPTION = range(2)

def sanitize_filename(name: str) -> str:
    """Removes or replaces characters unsafe for filenames."""
    name = name.replace(' ', '_')
    # Keep alphanumeric, underscore, hyphen. Remove others.
    name = re.sub(r"[^\w\-]", "", name)
    # Limit length to avoid issues with long filenames
    return name[:100] # Limit to 100 characters

def download_tiktok_video(url: str) -> str | None:
    """Downloads a TikTok video using yt-dlp."""
    # Ensure VIDEOS_DIR exists right before download
    os.makedirs(VIDEOS_DIR, exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # Prefer mp4
        'outtmpl': os.path.join(VIDEOS_DIR, '%(title)s.%(ext)s'), # Save directly to videos dir
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{ # Ensure the final file is mp4 if possible
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }],
        'sanitize_filename': True # Use yt-dlp's sanitization
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # yt-dlp >= 2023.06.22 uses 'filepath' after download/postprocessing
            downloaded_path = info.get('filepath')
            if not downloaded_path:
                # Fallback for older versions or if 'filepath' isn't populated
                filename = ydl.prepare_filename(info)
                # Ensure the file exists at the prepared path
                if os.path.exists(filename):
                     downloaded_path = filename
                else:
                     # Try to find the downloaded file based on title/ext if needed
                     title = info.get('title', 'tiktok_video')
                     ext = info.get('ext', 'mp4')
                     # Note: This fallback is less reliable if sanitization differs
                     potential_path = os.path.join(VIDEOS_DIR, f"{title}.{ext}")
                     if os.path.exists(potential_path):
                         downloaded_path = potential_path
                     else:
                         # Last resort based on sanitized name (less reliable)
                         safe_title = sanitize_filename(title)
                         potential_path_sanitized = os.path.join(VIDEOS_DIR, f"{safe_title}.{ext}")
                         if os.path.exists(potential_path_sanitized):
                              downloaded_path = potential_path_sanitized

            if downloaded_path and os.path.exists(downloaded_path):
                logging.info(f"Video downloaded successfully to: {downloaded_path}")
                return downloaded_path
            else:
                 logging.error(f"Download finished but couldn't locate file for URL: {url}")
                 return None

    except Exception as e:
        logging.error(f"Error downloading video from {url}: {e}")
        return None


def post_to_twitter(video_path: str, caption: str) -> bool:
    """Uploads video and posts tweet."""
    try:
        # Check file size (Twitter limits: 512MB for video)
        if os.path.getsize(video_path) > 512 * 1024 * 1024:
             logging.error(f"Video file {video_path} is too large for Twitter.")
             return False

        media = api.media_upload(filename=video_path, media_category="tweet_video", chunked=True)
        logging.info(f"Media uploaded to Twitter: ID {media.media_id_string}")
        # Ensure media processing is complete (optional but safer for large videos)
        # while media.processing_info and media.processing_info['state'] == 'pending':
        #    time.sleep(media.processing_info['check_after_secs'])
        #    media = api.get_media_metadata(media.media_id_string)
        # if media.processing_info and media.processing_info['state'] == 'failed':
        #    logging.error(f"Twitter media processing failed: {media.processing_info['error']}")
        #    return False

        api.update_status(status=caption, media_ids=[media.media_id_string])
        logging.info("Tweet posted successfully.")
        return True
    except tweepy.errors.TweepyException as e:
        logging.error(f"Twitter API error posting tweet for {video_path}: {e}")
        # Consider specific error handling (e.g., duplicate tweet)
        if "duplicate content" in str(e).lower():
            logging.warning("Duplicate tweet detected.")
            # Optionally, inform the user it was a duplicate
        return False
    except Exception as e:
        logging.error(f"Generic error posting tweet for {video_path}: {e}")
        return False

# --- Telegram Bot Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks for the URL."""
    user = update.effective_user
    logging.info(f"User {user.id} ({user.username}) started interaction.")
    await update.message.reply_text(
        "Hi! Send me a TikTok video URL to download and tweet.\n\n"
        "You can use /cancel to stop at any time.\n"
        "Use /logs to see your past activity (if any)."
    )
    return URL

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message when /help command is issued."""
    await update.message.reply_text(
        "🤖 *TikTok to Twitter Bot Help* 🤖\n\n"
        "*Commands:*\n"
        "/start - Begin downloading and tweeting a TikTok video\n"
        "/cancel - Cancel the current operation\n"
        "/logs - View your activity logs\n"
        "/help - Show this help message\n\n"
        "*How to use:*\n"
        "1. Start with /start command\n"
        "2. Send a TikTok video URL\n"
        "3. Provide a caption for your tweet (max 280 characters)\n"
        "4. Wait for confirmation of successful tweeting\n\n"
        "The bot will download the video, post it to Twitter with your caption, "
        "and then clean up the file.",
        parse_mode='Markdown'
    )

async def received_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the URL and asks for the caption."""
    url = update.message.text.strip()
    # Basic URL validation (can be improved)
    if not re.match(r'https?://.*tiktok\.com/.*', url):
        await update.message.reply_text(
            "That doesn't look like a valid TikTok URL. Please send a valid link, or use /cancel."
        )
        return URL # Stay in the same state

    context.user_data['url'] = url
    user = update.effective_user
    logging.info(f"User {user.id} provided URL: {url}")
    await update.message.reply_text(
        "Great! Now send me the caption you want for your tweet (max 280 characters)."
    )
    return CAPTION

async def received_caption(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receives caption, downloads video, posts to Twitter, and cleans up."""
    caption = update.message.text.strip()
    url = context.user_data.get('url')
    user = update.effective_user

    if not url:
         logging.warning(f"User {user.id} reached caption state without URL in context.")
         await update.message.reply_text("Something went wrong, URL not found. Please /start again.")
         return ConversationHandler.END

    # Optional: Caption length check (Twitter limit is 280)
    if len(caption) > 280:
        await update.message.reply_text(
            f"Caption is too long ({len(caption)}/280 characters). Please send a shorter caption, or /cancel."
        )
        return CAPTION # Stay in caption state

    logging.info(f"User {user.id} provided caption: {caption}")
    await update.message.reply_text("⬇️ Downloading video...")

    # For potentially long operations, consider using context.application.create_task()
    video_path = download_tiktok_video(url)

    if not video_path:
        await update.message.reply_text("❌ Failed to download the video. Please check the link or try again later.")
        logging.info(f"USER={user.id}\tDOWNLOAD_FAILED\tURL={url}")
        # Clean up user data
        context.user_data.clear()
        return ConversationHandler.END

    await update.message.reply_text("⬆️ Uploading to Twitter...")
    success = post_to_twitter(video_path, caption)

    if success:
        await update.message.reply_text("✅ Video downloaded and tweeted successfully!")
        logging.info(f"USER={user.id}\tDOWNLOADED\tURL={url}\tFILE={video_path}")
        logging.info(f"USER={user.id}\tTWEETED\tFILE={video_path}\tCAPTION={caption}")
        # Clean up the downloaded video file
        try:
            os.remove(video_path)
            logging.info(f"USER={user.id}\tREMOVED\tFILE={video_path}")
        except OSError as e:
            logging.warning(f"USER={user.id}\tREMOVE_FAILED\tFILE={video_path}\tERROR={e}")
    else:
        await update.message.reply_text("❌ Failed to post the tweet. It might be a duplicate or a Twitter API issue. Check the logs for details.")
        logging.info(f"USER={user.id}\tTWEET_FAILED\tFILE={video_path}")
        # Keep the file in case user wants to retry or debug? Or delete? Let's delete for now.
        try:
            if os.path.exists(video_path): # Check if it exists before removing
                 os.remove(video_path)
                 logging.info(f"USER={user.id}\tREMOVED_AFTER_TWEET_FAIL\tFILE={video_path}")
        except OSError as e:
            logging.warning(f"USER={user.id}\tREMOVE_FAILED_AFTER_TWEET_FAIL\tFILE={video_path}\tERROR={e}")


    # Clean up user data
    context.user_data.clear()
    return ConversationHandler.END

async def send_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the user their relevant log entries."""
    user = update.effective_user
    logging.info(f"User {user.id} requested logs.")
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
        # Filter logs for this specific user ID
        user_log_identifier = f"USER={user.id}\t"
        user_lines = [line for line in lines if user_log_identifier in line] # More robust check

        if not user_lines:
            await update.message.reply_text("No activity logs found for your account yet.")
            return

        # Send logs in chunks to avoid hitting Telegram message limits
        log_output = "```\n--- Your Activity Log ---\n" # Use Markdown code block
        char_count = len(log_output)
        MAX_MSG_LENGTH = 4000 # Telegram's approx limit is 4096, leave buffer

        for line in reversed(user_lines): # Show newest logs first
            if char_count + len(line) + 4 > MAX_MSG_LENGTH: # +4 for ```\n
                log_output += "```"
                try:
                    await update.message.reply_text(log_output, parse_mode='MarkdownV2')
                except Exception as e:
                     logging.warning(f"Failed to send log chunk to user {user.id}: {e}. Trying plain text.")
                     # Fallback for Markdown issues (less likely with simple logs)
                     try:
                         # Remove Markdown formatting for plain text fallback
                         await update.message.reply_text(log_output.replace('```\n','').replace('```',''))
                     except Exception as fallback_e:
                         logging.error(f"Failed to send plain text log chunk either: {fallback_e}")

                log_output = "```\n" # Start new chunk
                char_count = len(log_output)

            log_output += line # Add line to current chunk
            char_count += len(line)

        # Send the last chunk
        if log_output != "```\n": # Check if there's anything in the last chunk
            log_output += "```"
            try:
                await update.message.reply_text(log_output, parse_mode='MarkdownV2')
            except Exception as e:
                logging.warning(f"Failed to send final log chunk to user {user.id}: {e}. Trying plain text.")
                try:
                    await update.message.reply_text(log_output.replace('```\n','').replace('```',''))
                except Exception as fallback_e:
                    logging.error(f"Failed to send final plain text log chunk either: {fallback_e}")


    except FileNotFoundError:
        logging.warning("Log file not found when user requested logs.")
        await update.message.reply_text("Log file not found on the server.")
    except Exception as e:
        logging.error(f"Error reading or sending logs for user {user.id}: {e}")
        await update.message.reply_text("An error occurred while retrieving your logs.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels the current operation."""
    user = update.effective_user
    logging.info(f"User {user.id} cancelled operation. Current data: {context.user_data}")
    await update.message.reply_text("Operation cancelled.")
    # Clean up user data
    context.user_data.clear()
    return ConversationHandler.END

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log Errors caused by Updates."""
    logging.error(f'Update caused error: {context.error}')
    # Optionally inform user about generic error
    # if update and hasattr(update, 'message') and update.message:
    #    await update.message.reply_text("An unexpected error occurred. Please try again later.")



async def main_async() -> None:
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Conversation handler setup
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'https?://.*tiktok\.com/.*'), received_url),
                MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: u.message.reply_text("Please send a valid TikTok URL or /cancel.") or URL)
            ],
            CAPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_caption)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('logs', send_logs))
    application.add_handler(CommandHandler('help', help_command))
    application.add_error_handler(error_handler)

    logging.info("Starting Telegram bot polling...")
    print("Bot is running. Press Ctrl+C to stop.")

    # Start polling (this call manages its own event loop internally)
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logging.info("Bot stopped.")

if __name__ == '__main__':
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Conversation handler setup
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            URL: [
                MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(r'https?://.*tiktok\.com/.*'), received_url),
                MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: u.message.reply_text("Please send a valid TikTok URL or /cancel.") or URL)
            ],
            CAPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, received_caption)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('logs', send_logs))
    application.add_handler(CommandHandler('help', help_command))
    application.add_error_handler(error_handler)

    logging.info("Starting Telegram bot polling...")
    print("Bot is running. Press Ctrl+C to stop.")

    # Start polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logging.info("Bot stopped.")
