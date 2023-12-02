import os
import requests
import llama_cpp
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pydub import AudioSegment
from moviepy.editor import VideoFileClip

print('Starting up bot...')

TOKEN: Final = '6339894997:AAFr8fEKOYLPhhsJoBg-zwFCu9TmIT2uNZQ'
BOT_USERNAME: Final = '@Enpoi_Omni_Bot'

class OmniBot:
    def __init__(self, model_path, n_ctx=4096, n_gpu_layers=35):
        self.llama_model = llama_cpp.Llama(model_path=model_path, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers, verbose=True)
        self.history = []

    def system_message(self, user_name=None, user_mutter_tongue=None, user_german_proficiency=None):
        # Check if all necessary user information is available:
        return f"""
            You are OmniBot, developed by enpoi.com and Eren Kalinsazlioglu. Your job is to be a respectfull assistant and comunicate with the user.

            you have access to these fallowing tools:
            - image generating
            - image classification
            - audio generation
            - video analysis

            to you these tools you must write 'needtools' for example:

            user: Read the following text out loud
            response: needtools

            user Draw me a picture of rivers and lakes.
            response: needtools
            
            user: Generate a picture of rivers and lakes.
            response: needtools
            """

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

    def generate_response(self, user_input):
        # Format the prompt consistently
        formatted_input = f"Q: {user_input} A: "
        self.add_message("user", formatted_input)

        # Prepare messages for the model
        system_msg= self.system_message()
        messages = [{"role": "system", "content": system_msg}] + self.history

        # Call the model
        completion = self.llama_model.create_chat_completion(messages=messages,
                                                             max_tokens=300,
                                                             stop=["Q:"]
                                                            )

        # Extract only the assistant's response
        assistant_response = completion['choices'][0]['message']['content']
        self.add_message("assistant", assistant_response)

        # Return only the assistant's response
        return assistant_response.strip()  # .strip() removes any leading/trailing whitespace

    def clear_memory(self):
        self.history = []

omnibot = OmniBot(model_path='/home/adam/Telegram_Bot/mistral-7b-instruct-v0.1.Q4_0.gguf')

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
    text = update.message.text.strip()
    print(f'Received message text: "{text}"')

    if not text:
        await update.message.reply_text("Your message is empty. Please enter a valid message.")
        return

    llm_response = omnibot.generate_response(text)
    if "needtools" in llm_response:
        print("Needed_tools")
    else:
        await update.message.reply_text(llm_response)

    print(f'User said: "{text}"')
    print(f'Bot replied with: "{llm_response}"')

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
