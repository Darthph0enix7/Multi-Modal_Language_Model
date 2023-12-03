import os
import requests
import llama_cpp
import mimetypes
from PIL import Image
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from transformers.tools.agent_types import AgentText, AgentAudio
from pydub import AudioSegment
from moviepy.editor import VideoFileClip
from transformers.tools import HfAgent

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
            Provide concise and on point answers mostly.
            if the user wants something other than a normal conversation, use fallowing tools, you dont have to say anything except the command to use the tools.

            you have access to these fallowing tools:
            'document_qa': PreTool(task='document-question-answering', description='This is a tool that answers a question about an document (pdf). It takes an input named `document` which should be the document containing the information, as well as a `question` that is the question about the document. It returns a text that contains the answer to the question.'),
            'image_captioner': PreTool(task='image-captioning', description='This is a tool that generates a description of an image. It takes an input named `image` which should be the image to caption, and returns a text that contains the description in English.'),
            'image_qa': PreTool(task='image-question-answering', description='This is a tool that answers a question about an image. It takes an input named `image` which should be the image containing the information, as well as a `question` which should be the question in English. It returns a text that is the answer to the question.'),
            'image_segmenter': PreTool(task='image-segmentation', description='This is a tool that creates a segmentation mask of an image according to a label. It cannot create an image.It takes two arguments named `image` which should be the original image, and `label` which should be a text describing the elements what should be identified in the segmentation mask. The tool returns the mask.' ),
            'transcriber': PreTool(task='speech-to-text', description='This is a tool that transcribes an audio into text. It takes an input named `audio` and returns the transcribed text.'),
            'summarizer': PreTool(task='summarization', description='This is a tool that summarizes an English text. It takes an input `text` containing the text to summarize, and returns a summary of the text.'),
            'text_classifier': PreTool(task='text-classification', description='This is a tool that classifies an English text using provided labels. It takes two inputs: `text`, which should be the text to classify, and `labels`, which should be the list of labels to use for classification. It returns the most likely label in the list of provided `labels` for the input text.'),
            'text_qa': PreTool(task='text-question-answering', description='This is a tool that answers questions related to a text. It takes two arguments named `text`, which is the text where to find the answer, and `question`, which is the question, and returns the answer to the question.'),
            'text_reader': PreTool(task='text-to-speech', description='This is a tool that reads an English text out loud. It takes an input named `text` which should contain the text to read (in English) and returns a waveform object containing the sound.'),
            'translator': PreTool(task='translation', description="This is a tool that translates text from a language to another. It takes three inputs: `text`, which should be the text to translate, `src_lang`, which should be the language of the text to translate and `tgt_lang`, which should be the language for the desired ouput language. Both `src_lang` and `tgt_lang` are written in plain English, such as 'Romanian', or 'Albanian'. It returns the text translated in `tgt_lang`."),
            'image_transformer': PreTool(task='image-transformation', description='This is a tool that transforms an image according to a prompt. It takes two inputs: `image`, which should be the image to transform, and `prompt`, which should be the prompt to use to change it. The prompt should only contain descriptive adjectives, as if completing the prompt of the original image. It returns the modified image.'),
            'text_downloader': PreTool(task='text-download', description='This is a tool that downloads a file from a `url`. It takes the `url` as input, and returns the text contained in the file.'),
            'image_generator': PreTool(task='text-to-image', description='This is a tool that creates an image according to a prompt, which is a text description. It takes an input named `prompt` which contains the image description and outputs an image.'),
            'video_generator': PreTool(task='text-to-video', description='This is a tool that creates a video according to a text description. It takes an input named `prompt` which contains the image description, as well as an optional input `seconds` which will be the duration of the video. The default is of two seconds. The tool outputs a video object.')

            to use these tools you you must only response in this format, if the user wants to use tools:
            Action: 'tool_task'
            Action Input: 'Description of what the user wants'
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
                                                             max_tokens=250,
                                                             stop=["Q:"]
                                                            )

        # Extract only the assistant's response
        assistant_response = completion['choices'][0]['message']['content']
        self.add_message("assistant", assistant_response)
        keywords = ['action', 'Action Input']
        contains_keyword = any(keyword in assistant_response for keyword in keywords)

        # Return only the assistant's response
        return assistant_response.strip(), contains_keyword  # .strip() removes any leading/trailing whitespace

    def clear_memory(self):
        self.history = []

omnibot = OmniBot(model_path="/home/adam/Multi-Modal_Language_Model/mistral-7b-instruct-v0.1.Q4_0.gguf")
agent = HfAgent("https://api-inference.huggingface.co/models/bigcode/starcoder")
print("StarCoder is initialized 💪")

# Start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! I\'m your bot.')

# Help command
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Send me a message and I\'ll respond!')


def determine_response_type(response):
    if isinstance(response, Image.Image):
        return "image"
    elif isinstance(response, AgentAudio):
        return "audio"
    elif isinstance(response, AgentText):
        return "text"
    elif isinstance(response, str):
        # Check for file path and determine type based on extension or MIME type
        if os.path.exists(response):
            mime_type, _ = mimetypes.guess_type(response)
            if mime_type:
                if 'image' in mime_type:
                    return "image"
                elif 'audio' in mime_type:
                    return "audio"
                elif 'video' in mime_type:
                    return "video"
            return "file"
        return "text"
    return "unknown"

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
    user_id = str(update.message.from_user.id)
    print(f'user: {user_id} Received message text: "{text}"')

    if not text:
        await update.message.reply_text("Your message is empty. Please enter a valid message.")
        return

    llm_response, contains_keyword  = omnibot.generate_response(text)
    if contains_keyword:
        await update.message.reply_text("Tools are been used a moment please")
        agent_response = agent.chat(text)
        response_type = determine_response_type(agent_response)

        if response_type == "image":
            with open(agent_response, 'rb') as image_file:
                await context.bot.send_photo(chat_id=user_id, photo=image_file)

        elif response_type == "audio":
            with open(agent_response, 'rb') as audio_file:
                await context.bot.send_audio(chat_id=user_id, audio=audio_file)

        elif response_type == "video":
            with open(agent_response, 'rb') as video_file:
                await context.bot.send_video(chat_id=user_id, video=video_file)

        elif response_type == "text":
            await context.bot.send_message(chat_id=user_id, text=agent_response)

        elif response_type == "file":
            mime_type, _ = mimetypes.guess_type(agent_response)
            if 'video' in mime_type:
                with open(agent_response, 'rb') as video_file:
                    await context.bot.send_video(chat_id=user_id, video=video_file)
            elif 'audio' in mime_type:
                with open(agent_response, 'rb') as audio_file:
                    await context.bot.send_audio(chat_id=user_id, audio=audio_file)
            else:
                # Default to sending as a document
                with open(agent_response, 'rb') as file:
                    await context.bot.send_document(chat_id=user_id, document=file)
        else:
            print("Unknown response type or unable to handle the response.")
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
