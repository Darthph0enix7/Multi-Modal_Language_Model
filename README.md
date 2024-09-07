# OmniBot Telegram Bot

OmniBot is a multi-functional Telegram bot built using a powerful LLM (Llama-based model) that interacts with users, processes various file types (images, audio, video), and integrates tools for multimedia processing and language understanding. The bot also uses HuggingFace agents for advanced tasks such as image transformation and document Q&A.

## Features

- **LLM Integration:** OmniBot utilizes the Llama model for natural language conversation and tool invocation.
- **Multimedia Handling:** Processes images, audio, and video files, including conversion to common formats (e.g., MP3, MP4).
- **Tool Integration:** Includes several tools for image captioning, document analysis, text-to-speech, translation, and more via HuggingFace agents.
- **Task Automation:** Automatically selects and invokes the right tool based on user input.

## Installation

### Prerequisites

- Python 3.8+
- Telegram Bot Token (Get one from [BotFather](https://core.telegram.org/bots#botfather))
- Required libraries:

```bash
pip install telegram python-telegram-bot transformers pydub moviepy pillow requests
```

### Clone the Repository

```bash
git clone https://github.com/your-repo/omnibot.git
cd omnibot
```

### Environment Setup

1. Add your Telegram bot token in the code:
   ```python
   TOKEN: Final = 'YOUR_BOT_TOKEN'
   BOT_USERNAME: Final = '@YourBotUsername'
   ```

2. Provide the correct path to the Llama model when initializing `OmniBot`:
   ```python
   omnibot = OmniBot(model_path="path/to/llama/model")
   ```

## Usage

### Start the Bot

Run the bot script:

```bash
python omnibot.py
```

### Telegram Commands

- **Start:** `/start` - Initiates the bot and sends a greeting message.
- **Help:** `/help` - Provides a short guide on how to interact with the bot.

### File Processing

- **Images:** Send an image file to the bot, and it will process or transform it based on the input.
- **Audio:** The bot converts received audio files to MP3 format.
- **Video:** The bot converts received video files to MP4 format.

### Text Interaction

Send any text message to the bot for a response. The bot will either engage in conversation or use integrated tools based on the input.

### Tool Automation

If the user's request requires advanced processing (e.g., document Q&A, image captioning), the bot automatically detects and invokes the correct tool. Tools available include:

- **Document Q&A**
- **Image Captioner**
- **Speech-to-Text (Audio Transcription)**
- **Translation**
- **Text-to-Speech**
- **Text Summarization**

## Multimedia Conversion

- **Audio to MP3:** Converts uploaded audio files to MP3 format.
- **Video to MP4:** Converts uploaded video files to MP4 format using MoviePy.

### Example Usage

1. **Sending Text**: 
   ```
   User: Can you describe this document?
   Bot: Action: 'document_qa' | Action Input: 'Describe the attached document.'
   ```

2. **Sending an Image**: 
   - The bot will respond with a processed image or a caption.

3. **Sending Audio or Video**:
   - The bot converts and responds with the media in the appropriate format.

## Project Structure

- `OmniBot`: Main class that handles conversation, multimedia, and tool management.
- `HfAgent`: Interface to HuggingFace models for handling specific tasks such as image transformation and document Q&A.
- `Media Handlers`: Functions to process audio, video, and images received by the bot.

## License

This project is licensed under the MIT License.

## Acknowledgements

- [Llama CPP](https://github.com/ggerganov/llama.cpp) for efficient language model inference.
- [HuggingFace](https://huggingface.co/) for advanced models and agents.
- [Python Telegram Bot](https://python-telegram-bot.readthedocs.io/) for seamless Telegram integration.
