from typing import Final
import requests
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

print('Starting up bot1...')

TOKEN: Final = '6339894997:AAFr8fEKOYLPhhsJoBg-zwFCu9TmIT2uNZQ'
BOT_USERNAME: Final = '@Enpoi_Omni_Bot'

# Start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! I\'m a bot. What\'s up?')

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Try typing anything and I will do my best to respond!')

# Custom command
async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('This is a custom command, you can add whatever text you want here.')

# Handle text responses
def handle_response(text: str) -> str:
    processed: str = text.lower()

    if 'hello' in processed:
        return 'Hey there!'

    if 'how are you' in processed:
        return 'I\'m good!'

    if 'i love python' in processed:
        return 'Remember to subscribe!'

    return 'I don\'t understand'

# Handle text messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    print(f'User ({update.message.chat.id}) in {message_type}: "{text}"')

    if message_type == 'group' and BOT_USERNAME in text:
        new_text: str = text.replace(BOT_USERNAME, '').strip()
        response: str = handle_response(new_text)
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)


# Handle photos
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
    file_url = photo_file.file_path
    response = requests.get(file_url)
    if response.status_code == 200:
        with open('user_photo.jpg', 'wb') as f:
            f.write(response.content)
        await update.message.reply_text('Photo received!')

# Handle audio
async def audio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file = await context.bot.get_file(update.message.audio.file_id)
    file_url = audio_file.file_path
    response = requests.get(file_url)
    if response.status_code == 200:
        with open('user_audio.mp3', 'wb') as f:
            f.write(response.content)
        await update.message.reply_text('Audio received!')

# Send image
async def send_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await context.bot.send_photo(chat_id=chat_id, photo=open('path_to_image.jpg', 'rb'))

# Send audio
async def send_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await context.bot.send_audio(chat_id=chat_id, audio=open('path_to_audio.mp3', 'rb'))

# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('sendimage', send_image))
    app.add_handler(CommandHandler('sendaudio', send_audio))

    # Add message handlers
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.AUDIO, audio_handler))

    # Log all errors
    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=5)
