import os
import requests
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
from moviepy.editor import VideoFileClip

print('Starting up bot...')

TOKEN: Final = '6339894997:AAFr8fEKOYLPhhsJoBg-zwFCu9TmIT2uNZQ'
BOT_USERNAME: Final = '@Enpoi_Omni_Bot'

# Start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! I\'m your bot.')

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Send me a message and I\'ll respond!')

# Function to convert audio to mp3
def convert_audio_to_mp3(source_path, target_path):
    audio = AudioSegment.from_file(source_path)
    audio.export(target_path, format="mp3")

# Function to convert video to mp4
def convert_video_to_mp4(source_path, target_path):
    clip = VideoFileClip(source_path)
    clip.write_videofile(target_path, codec="libx264")

# Handle photos
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await context.bot.get_file(update.message.photo[-1].file_id)
    file_url = photo_file.file_path
    with open('user_photo.jpg', 'wb') as f:
        f.write(requests.get(file_url).content)
    await update.message.reply_text('Photo received!')

# Handle audio
async def audio_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    audio_file = await context.bot.get_file(update.message.audio.file_id)
    file_url = audio_file.file_path
    temp_file_name = 'temp_audio' + os.path.splitext(file_url)[1]
    with open(temp_file_name, 'wb') as f:
        f.write(requests.get(file_url).content)
    convert_audio_to_mp3(temp_file_name, 'user_audio.mp3')
    os.remove(temp_file_name)
    await update.message.reply_text('Audio received and converted to MP3!')

# Handle videos
async def video_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    video_file = await context.bot.get_file(update.message.video.file_id)
    file_url = video_file.file_path
    temp_file_name = 'temp_video' + os.path.splitext(file_url)[1]
    with open(temp_file_name, 'wb') as f:
        f.write(requests.get(file_url).content)
    convert_video_to_mp4(temp_file_name, 'user_video.mp4')
    os.remove(temp_file_name)
    await update.message.reply_text('Video received and converted to MP4!')

# Handle general files
async def file_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    document = update.message.document
    file_id = document.file_id
    file_name = document.file_name
    file_to_download = await context.bot.get_file(file_id)
    file_url = file_to_download.file_path

    # Downloading the file
    with open(file_name, 'wb') as f:
        f.write(requests.get(file_url).content)
    await update.message.reply_text(f'File {file_name} received!')

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text: str = update.message.text
    chat_id = update.message.chat_id
    
    print(f"Received message from user {chat_id}: '{text}'")

    if text.lower() == 'test':
        for file_name in ['user_photo.jpg', 'user_audio.mp3', 'user_video.mp4']:
            if os.path.exists(file_name):
                await context.bot.send_document(chat_id=chat_id, document=open(file_name, 'rb'))
            else:
                await update.message.reply_text(f'No {file_name} available.')

    else:
        await update.message.reply_text("I'm not sure how to respond to that.")

# Log errors
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message.text:
        # Handle text messages
        await handle_message(update, context)
    elif message.photo:
        # Handle photo messages
        await photo_handler(update, context)
    elif message.audio:
        # Handle audio messages
        await audio_handler(update, context)
    elif message.video:
        # Handle video messages
        await video_handler(update, context)
    elif message.document:
        # Handle document messages
        await file_handler(update, context)

# Run the program
if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    # Use a generic handler for all non-command messages
    app.add_handler(MessageHandler(filters.ALL, handle_all))

    app.add_error_handler(error)

    print('Polling...')
    app.run_polling(poll_interval=5)
