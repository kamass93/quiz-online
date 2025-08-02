from flask import Flask, request
import telegram
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters

TOKEN = "7305825990:AAHQYjZ54g8TqmEgjV26sPEAF3V_W9FKeVc"

app = Flask(__name__)
bot = telegram.Bot(token=TOKEN)

quiz = {
    "Qual è la capitale d'Italia?": "Roma",
    "Quanto fa 5 + 7?": "12",
    "Chi ha scritto 'Divina Commedia'?": "Dante",
}

# Stato utente
user_states = {}

def start(update, context):
    user_id = update.effective_user.id
    user_states[user_id] = {"score": 0, "q": list(quiz.keys())}
    update.message.reply_text("Benvenuto al quiz! Rispondi alle domande.")
    ask_question(update, context)

def ask_question(update, context):
    user_id = update.effective_user.id
    if user_states[user_id]["q"]:
        question = user_states[user_id]["q"].pop(0)
        user_states[user_id]["current_q"] = question
        update.message.reply_text(question)
    else:
        score = user_states[user_id]["score"]
        update.message.reply_text(f"Quiz terminato! Punteggio: {score}")
        user_states.pop(user_id)

def handle_answer(update, context):
    user_id = update.effective_user.id
    if user_id not in user_states:
        update.message.reply_text("Scrivi /start per iniziare il quiz.")
        return

    user_data = user_states[user_id]
    question = user_data.get("current_q")
    correct_answer = quiz[question]
    if update.message.text.strip().lower() == correct_answer.lower():
        user_states[user_id]["score"] += 1
        update.message.reply_text("✅ Corretto!")
    else:
        update.message.reply_text(f"❌ Sbagliato! La risposta corretta era: {correct_answer}")
    ask_question(update, context)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return 'ok'

# Dispatcher per gestire i comandi
dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_answer))

@app.route("/", methods=["GET"])
def index():
    return "Bot attivo!"

if __name__ == "__main__":
    app.run(debug=True)
