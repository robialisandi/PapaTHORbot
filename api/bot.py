import os
import logging
import requests
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.constants import ParseMode, ChatAction
from dotenv import load_dotenv
from flask import Flask, request

load_dotenv()

# Inisialisasi logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Variabel global untuk Application
application = None

async def start(update: Update, context: CallbackContext) -> None:
    chat = update.effective_chat
    if chat.type == 'private':
        name = chat.first_name
        pesan = f'''
        Halo {name}.\nPanggil aku Papa ya!!!\nSenang kamu chat papa.\nKetik /help untuk melihat daftar perintah yang tersedia.
        '''
    else:
        group_name = chat.title
        pesan = f'''
        Halo anak-anak {group_name}.\nPanggil aku Papa ya!!!\nSenang Papa bisa ada disini.\nKetik /help untuk melihat daftar perintah yang tersedia.
        '''

    await update.effective_chat.send_message(pesan, parse_mode=ParseMode.HTML)

async def help(update: Update, context: CallbackContext) -> None:
    help_message = '''
    Daftar perintah yang tersedia:
    - /start: Memulai bot
    - /help: Menampilkan daftar perintah
    - /meme [text]: Generate meme kocak
    '''
    await update.effective_chat.send_message(help_message, parse_mode=ParseMode.HTML)

async def meme(update: Update, context: CallbackContext) -> None:
    try:
        chat_id = update.effective_chat.id
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        url_meme = 'https://api.imgflip.com/caption_image'
        input_text = ' '.join(context.args)
        response_template = requests.get('https://api.imgflip.com/get_memes').json()
        templates = response_template['data']['memes']
        random_index = random.randint(0, len(templates) - 1)
        template_id = templates[random_index]['id']

        formData = {
            'template_id': template_id,
            'username': 'NgodingDewa',
            'password': 'Heloword0987#',
            'text0': input_text
        }

        response = requests.post(url_meme, data=formData)
        if response.status_code == 200:
            data = response.json()
            meme_url = data['data']['url']
            await context.bot.send_photo(chat_id=chat_id, photo=meme_url)
        else:
            await update.message.reply_text('Terjadi kesalahan dalam mengambil meme.')
    except Exception as e:
        logger.error(f"Error in meme function: {str(e)}")
        await update.message.reply_text(f'Maaf, terjadi kesalahan: {str(e)}', parse_mode=ParseMode.HTML)

@app.route('/api/bot', methods=['POST'])
def webhook():
    if application is None:
        logger.error("Application is not initialized")
        return 'Internal Server Error', 500

    try:
        data = request.get_json()
        logger.info(f"Received update: {data}")
        update = Update.de_json(data, application.bot)
        application.update_queue.put(update)
        return 'OK'
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return 'Internal Server Error', 500

def init_application():
    global application
    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logger.error("BOT_TOKEN is not set in environment variables")
        return

    application = Application.builder().token(bot_token).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('meme', meme))

    # Set webhook URL
    webhook_url = os.getenv('WEBHOOK_URL') + '/api/bot'
    logger.info(f"Setting webhook to: {webhook_url}")
    try:
        application.bot.set_webhook(webhook_url)
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")

def main():
    init_application()
    # Ensure that application is initialized before starting Flask server
    if application is None:
        logger.error("Failed to initialize the application.")
        return
    # Run the Flask app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == '__main__':
    main()
