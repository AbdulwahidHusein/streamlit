# Telegram Bot with OpenAI Integration

A simple Telegram bot that forwards messages to OpenAI and replies with the AI's response.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file:
- Copy `.env.example` to `.env`
- Fill in your Telegram Bot Token (get it from @BotFather)
- Add your OpenAI API key
- Set your webhook URL (needs to be HTTPS)

3. Run the bot:
```bash
python main.py
```

## Features

- Responds to all text messages in groups or direct messages
- Forwards messages to OpenAI's GPT-3.5-turbo
- Uses webhooks for better performance
- Built with FastAPI for reliable webhook handling

## Requirements

- Python 3.7+
- HTTPS domain for webhook
- Telegram Bot Token
- OpenAI API Key 