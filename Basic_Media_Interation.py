from typing import Final
from pydub import AudioSegment
import os
import requests
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


# Function to convert audio to mp3
def convert_audio_to_mp3(source_path, target_path):
    audio = AudioSegment.from_file(source_path)
    audio.export(target_path, format="mp3")

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
    text: str = update.message.text
    chat_id = update.message.chat_id

    if text.lower() == 'test':
        # Check if the photo file exists and send it
        if os.path.exists('user_photo.jpg'):
            await context.bot.send_photo(chat_id=chat_id, photo=open('user_photo.jpg', 'rb'))
        else:
            await update.message.reply_text('No photo available.')

        # Check if the audio file exists and send it
        if os.path.exists('user_audio.mp3'):
            await context.bot.send_audio(chat_id=chat_id, audio=open('user_audio.mp3', 'rb'))
        else:
            await update.message.reply_text('No audio available.')
    else:
        # Existing message handling logic
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
    file_extension = os.path.splitext(file_url)[1]

    temp_file_name = f'temp_audio{file_extension}'
    mp3_file_name = 'user_audio.mp3'

    # Download the original audio file
    response = requests.get(file_url)
    if response.status_code == 200:
        with open(temp_file_name, 'wb') as f:
            f.write(response.content)
        
        # Convert to mp3 and save
        convert_audio_to_mp3(temp_file_name, mp3_file_name)
        os.remove(temp_file_name)  # Remove the temporary file

        await update.message.reply_text('Audio received and converted to MP3!')

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
