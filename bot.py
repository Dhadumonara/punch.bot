import os
import logging
import json
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, CallbackContext

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# File to store user data
DATA_FILE = 'users.json'
TOTAL_COINS = 3000000000454

# Load user data from JSON file
def load_data():
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save user data to JSON file
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file)

# Start command handler
def start(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = {'coins': 0, 'referrals': 0, 'level': 1, 'badges': [], 'tasks': {}}
        save_data(data)
        update.message.reply_text('Welcome! You have been registered with 0 punch coins.')
    else:
        update.message.reply_text(f'Welcome back! You have {data[user_id]["coins"]} punch coins.')

# Balance command handler
def balance(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id in data:
        update.message.reply_text(f'You have {data[user_id]["coins"]} punch coins.')
    else:
        update.message.reply_text('You need to start the bot first by using /start.')

# Earn command handler
def earn(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    data = load_data()
    if user_id in data:
        data[user_id]['coins'] += 1
        global TOTAL_COINS
        TOTAL_COINS -= 1
        save_data(data)

        # Send the image of the coin
        coin_image_url = "https://drive.google.com/uc?id=1E6UUbJPEauulDfTi_rTsbGLNVPgt1CdG"
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=coin_image_url)

        update.message.reply_text(f'You earned 1 punch coin! You now have {data[user_id]["coins"]} punch coins.')
    else:
        update.message.reply_text('You need to start the bot first by using /start.')

# Referral command handler
def refer(update: Update, context: CallbackContext) -> None:
    referrer_id = str(update.message.from_user.id)
    data = load_data()
    if referrer_id in data:
        if context.args:
            referee_id = context.args[0]
            if referee_id in data:
                data[referee_id]['coins'] += 5000
                data[referrer_id]['coins'] += 5000
                data[referrer_id]['referrals'] += 1
                global TOTAL_COINS
                TOTAL_COINS -= 10000
                update.message.reply_text(f'Referral successful! You and {referee_id} earned 5000 punch coins each.')
                check_level(referrer_id, data)
                save_data(data)
            else:
                update.message.reply_text('Invalid referral code.')
        else:
            update.message.reply_text('Please provide a referral code.')
    else:
        update.message.reply_text('You need to start the bot first by using /start.')

# Check and update user level and badges
def check_level(user_id, data):
    user = data[user_id]
    if user['referrals'] >= 10 and user['level'] < 10:
        user['level'] += 1
        user['badges'].append(f'Level {user["level"]}')
        data[user_id] = user

# Task completion command handler
def task(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    data = load_data()
    task_name = context.args[0] if context.args else None
    tasks = ['Instagram', 'YouTube', 'Telegram']

    if user_id in data:
        if task_name in tasks:
            if task_name not in data[user_id]['tasks']:
                data[user_id]['tasks'][task_name] = True
                data[user_id]['coins'] += 100000
                global TOTAL_COINS
                TOTAL_COINS -= 100000
                update.message.reply_text(f'Task completed! You earned 100000 punch coins for joining {task_name}.')
                save_data(data)
            else:
                update.message.reply_text(f'You have already completed the {task_name} task.')
        else:
            update.message.reply_text(f'Invalid task. Available tasks are: {", ".join(tasks)}')
    else:
        update.message.reply_text('You need to start the bot first by using /start.')

# Total coins command handler
def total_coins(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Total punch coins remaining: {TOTAL_COINS}')

def main() -> None:
    # Load bot token from Replit secrets
    bot_token = os.getenv('BOT_TOKEN')

    if bot_token is None:
        logger.error("Bot token not found. Make sure you have added it to Replit secrets.")
        return

    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Register command handlers
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("balance", balance))
    dispatcher.add_handler(CommandHandler("earn", earn))
    dispatcher.add_handler(CommandHandler("refer", refer))
    dispatcher.add_handler(CommandHandler("task", task))
    dispatcher.add_handler(CommandHandler("total_coins", total_coins))

    # Start the bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT, SIGTERM or SIGABRT
    updater.idle()

if __name__ == '__main__':
    main()