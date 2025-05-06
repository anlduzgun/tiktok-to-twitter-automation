# TikTok-to-Twitter Automation Bot v1

A Telegram bot that downloads TikTok videos and automatically posts them to Twitter. Perfect for content creators who want to maintain a presence across platforms with minimal effort.

## 🌟 Features

- **Easy to Use**: Simple conversation flow through Telegram
- **Automatic Video Download**: Handles TikTok video downloads with optimal quality
- **Twitter Integration**: Posts videos directly to your Twitter account
- **Activity Logging**: Track your download and posting history
- **Secure**: Environment-based credential management
- **Automatic Cleanup**: Videos are deleted after successful posting

## 📋 Prerequisites

- Python 3.10+
- Telegram Bot Token (from [BotFather](https://t.me/botfather))
- Twitter Developer API credentials

## 🚀 Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/tiktok-twitter-bot.git
cd tiktok-twitter-bot
```

2. **Run set_credentials script**

- Script automatically sets virtual enviroment and .env file for credential

```bash
bash set_credentials.sh
```



## 💻 Usage

1. **Start the bot**

```bash
python tiktok-to-twitter-automation-telegram-bot.py
```

2. **Interact with the bot on Telegram**
   - Start a conversation with `/start`
   - Send a TikTok video URL
   - Add your desired tweet caption
   - The bot will handle the rest!

## 📱 Telegram Bot Commands

- `/start` - Begin a new download and tweet process
- `/cancel` - Cancel the current operation
- `/logs` - View your past activity
- `/help` - Display available commands and usage instructions

## 📂 Project Structure

```
tiktok-twitter-bot/
├── tiktok-to-twitter-automation-telegram-bot.py  # Main bot script
├── set_credentials.sh                            # Setup script
├── requirements.txt                              # Python dependencies
├── .env                                          # Environment variables (created during setup)
├── videos/                                       # Temporary video storage directory
└── download.log                                  # Activity log file
```

## ⚙️ Configuration Options

You can customize the following options in your `.env` file:

- `VIDEOS_DIR`: Directory for temporary video storage (default: "videos")
- `LOG_FILE`: Path to the log file (default: "download.log")

## 🔍 Troubleshooting

- **"Failed to download the video"**: Ensure the TikTok URL is valid and publicly accessible
- **"Failed to post the tweet"**: Check that your Twitter API credentials have proper permissions
- **Twitter API errors**: Make sure your account has proper API access and hasn't reached daily limits

## 🛠️ Development

This bot uses the following technologies:

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) for Telegram integration
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for video downloading
- [tweepy](https://github.com/tweepy/tweepy) for Twitter API integration

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.


## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) team
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) project
- [tweepy](https://github.com/tweepy/tweepy) developers

---

⭐ Star this repository if you find it useful! ⭐
