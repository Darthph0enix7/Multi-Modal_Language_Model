import json
import yaml
import os
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import llama_cpp
import nest_asyncio
nest_asyncio.apply()


class ChatBot:
    def __init__(self, model_path, n_ctx=4096, n_gpu_layers=35):
        self.llama_model = llama_cpp.Llama(model_path=model_path, n_ctx=n_ctx, n_gpu_layers=n_gpu_layers, verbose=True)
        self.history = []

    def system_message(self, user_name=None, user_mutter_tongue=None, user_german_proficiency=None):
        # Check if all necessary user information is available:
        return f"""
            Du bist Lingua Guide, entwickelt von enpoi.com und Eren Kalinsazlioglu. Ihre Aufgabe ist es, mit Menschen zu kommunizieren.
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




# Initialize the ChatBot instance
chatbot = ChatBot(model_path='/home/adam/Telegram_Bot/mistral-7b-instruct-v0.1.Q4_0.gguf')

chatbot.clear_memory()

# Load user data from YAML file
def load_user_data(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return yaml.safe_load(file) or {}
    else:
        with open(file_path, 'w') as file:
            yaml.dump({}, file)
        return {}

# Save user data to YAML file
def save_user_data(file_path, data):
    with open(file_path, 'w') as file:
        yaml.dump(data, file)

# Command handlers
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello there! I\'m a bot. What\'s up?')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Try typing anything and I will do my best to respond!')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_data_file = 'user_data.yaml'
    user_data = load_user_data(user_data_file)
    basic_words = {
        "hello", "hi", "hey",
        "ok", "okay", "k",
        "aha", "ah", "hmm",
        "yes", "yep", "yeah",
        "no", "nope", "nah",
        "thanks", "thank", "thank you",
        "please",
        "bye", "goodbye", "see you",
        "sorry", "apologies",
        "well", "oh", "wow",
        "haha", "lol",
        "um", "uh", "uhm",
        "hallo", "hi", "hey",
        "ok", "okay",
        "aha", "ah", "hmm",
        "ja", "doch",
        "nein", "nö",
        "danke", "bitte",
        "tschüss", "auf Wiedersehen",
        "entschuldigung", "tut mir leid",
        "nun", "oh", "wow",
        "haha", "lol",
        "ähm", "äh", "hm"
        "auch"
    }

    # Initialize user data if not present
    if user_id not in user_data:
        user_data[user_id] = {"info_status": "unknown"}

    # Check and request user information
    if user_data[user_id].get("info_status") != "complete":
        if user_data[user_id].get("info_status") != "awaiting_response":
            await update.message.reply_text("Hi! Could you please tell me your name, mother tongue, and your proficiency in German?")
            user_data[user_id]["info_status"] = "awaiting_response"
            save_user_data(user_data_file, user_data)
            return

    # Process the response with user's information
    if user_data[user_id]["info_status"] == "awaiting_response":
        user_response = update.message.text.strip()

        # Constructing the LLM prompt
        llm_prompt = f"""Extrahieren Sie diese Informationen aus diesem Text (Namen können knifflig sein, wählen Sie einfach einen aus, der ein Name sein könnte, und der Benutzer hat wahrscheinlich seinen Namen angegeben): {user_response}
        in der folgenden Vorlage. schreibe nicht NONE (sprache):

        Name:
        Muttersprache:
        Deutsche Profizenz:
        """
        llm_response = chatbot.generate_response(llm_prompt)
        print(llm_response)

        try:
            # Extracting information from the LLM response
            parsed_info = {line.split(":")[0].strip(): line.split(":")[1].strip() for line in llm_response.splitlines() if ":" in line}
            user_data[user_id] = {
                "user_name": parsed_info.get("Name", "Unknown"),
                "mutter_tongue": parsed_info.get("Muttersprache", "Unknown"),
                "german_proficiency": parsed_info.get("Deutsche Profizenz", "Unknown"),
                "info_status": "complete"
            }
            save_user_data(user_data_file, user_data)
            await update.message.reply_text(f"Thanks, {parsed_info.get('Name', 'Unknown')}! How can I assist you with your German learning?")
            chatbot.clear_memory()
        except Exception as e:
            await update.message.reply_text("There was an error processing your information. Please try again.")
            print(f"Error processing user info: {e}")  # For debugging
        return

    # Normal conversation flow for users with complete information
    user_info = user_data.get(user_id, {})
    user_name = user_info.get("user_name", "Unknown")
    user_mutter_tongue = user_info.get("mutter_tongue", "Unknown")
    user_german_proficiency = user_info.get("german_proficiency", "Unknown")

    # Process the user's message and generate a response
    text = update.message.text

    # Print the received message text for debugging
    print(f'Received message text: "{text}"')

    # Check if the message text is empty
    if not text.strip():
        await update.message.reply_text("Deine Nachricht ist leer. Bitte gib eine gültige Nachricht ein.")
        return

    # Handle user commands
    if text.upper() == "MEMORY.CLEAR":
        # Clear chatbot memory
        chatbot.clear_memory()
        await update.message.reply_text("Chatbot memory has been cleared.")
        return

    if text.upper() == "PROMPTTEMPLATE":
        updated_system_message = chatbot.system_message(user_name=user_name, user_mutter_tongue=user_mutter_tongue, user_german_proficiency=user_german_proficiency)
        await update.message.reply_text(updated_system_message)
        return

    text = update.message.text.strip()
    user_info = user_data.get(user_id, {})

    # Handling different cases based on user input
    if len(text) == 1 and text.isalpha():
        print("aaaaaaaa")
        # Append specific instruction for single letter input
        instruction = f"""Stellen Sie drei beliebige deutsche Wörter vor, vergiss die artikeln nicht!, die mit dem Buchstaben '{text}' beginnen. Fügen Sie Bedeutungen und Übersetzungen (auf {user_mutter_tongue}) für diese Wörter in folgendem Format hinzu:
        1.Wort:
        2.Wort:
        3.Wort:
        Beispiele auf deutsch mit {user_mutter_tongue}e übersetzungen:
        a.
        """
        modified_input = f"{text} {instruction}"
        system_msg = chatbot.system_message(user_name=user_name, user_mutter_tongue=user_mutter_tongue, user_german_proficiency=user_german_proficiency)
        llm_response = chatbot.generate_response(modified_input)
        print(instruction)
        await update.message.reply_text(llm_response)

    elif len(text.split()) == 1 and text.lower() not in basic_words:
        print("bbbbbbbbb")
        # Append specific instruction based on the type of the word
        instruction = (f"""
                       'system:' Meldungen sind für Sie und werden bei der Beantwortung ignoriert
                       system: Prüfen Sie, ob das Wort '{text}' ein Substantiv, Adjektiv oder Verb ist. Wenn nicht, fahren Sie mit dem Gespräch fort (antworten Sie nicht und fahren Sie fort)
                       Wenn es sich um ein Substantiv oder Adjektiv handelt, geben Sie die Erklärungen und Übersetzungen an,
                       und nennen Sie drei einfache Beispiele für die Verwendung des Begriffs.
                       Wenn es sich um ein Verb handelt, geben Sie die Vergangenheits- und Präsensformen an,
                       zusammen mit Beispielen mit {user_mutter_tongue} übersetzungen.

                       all dies in diesen Formaten:

                       Analysieren Sie, ob das Wort '{text}' ein Verb ist. Wenn ja, geben Sie detaillierte Informationen in folgendem Format an:
                        Wort:
                        Presäns Form:
                        Perfekt form:
                        Vergangenheitsform:
                        Beispiele:
                        1.
                        2.
                        3.
                        Übersetzungen auf {user_mutter_tongue}:

                       Untersuchen Sie, ob das Wort "{text}" ein Substantiv oder ein Adjektiv ist. Wenn ja, geben Sie detaillierte Informationen in folgendem Format an:
                        Wort:
                        Beispiele:
                        1.
                        2.
                        3.
                        Wenn es sich um ein Adjektiv handelt, geben Sie auch sein Gegenteil an:
                        Gegenteil:
                        Übersetzungen auf {user_mutter_tongue}:
                        Wenn "{text}" weder ein Substantiv noch ein Adjektiv noch ein Verb ist oder für das Gespräch relevant ist wie 'Hallo' oder 'ok', ignorieren Sie nicht alle diese Informationen und setzen Sie das Gespräch normal fort.
                       """)
        system_msg = chatbot.system_message(user_name=user_name, user_mutter_tongue=user_mutter_tongue, user_german_proficiency=user_german_proficiency)
        text = update.message.text.strip()
        llm_response = chatbot.generate_response(instruction)
        await update.message.reply_text(llm_response)
    else:
        # Normal conversation flow
        system_msg = chatbot.system_message(user_name=user_name, user_mutter_tongue=user_mutter_tongue, user_german_proficiency=user_german_proficiency)
        text = update.message.text.strip()
        print(system_msg)
        llm_response = chatbot.generate_response(text)
        await update.message.reply_text(llm_response)
        save_user_data(user_data_file, user_data)

    print(f'User ({user_id}) said: "{text}"')
    print(f'Bot replied with: "{llm_response}"')



# Error handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

# Run the program
if __name__ == '__main__':
    TOKEN: Final = '6362009757:AAGlc1jwcn2WS4LnxjoNwv7MnPngknFjs80'
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    print('Bot is polling...')
    app.run_polling(poll_interval=5)
