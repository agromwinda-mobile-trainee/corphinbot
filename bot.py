import requests
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# 🔑 Clés (à remplacer par les tiennes)
TELEGRAM_TOKEN = "7787262605:AAGsNYBu2SeZH9L17On5lXFgyxBlqQ9LlRM"
CHAT_ID = "1936421270"
ODDS_API_KEY = "44ca244602313bf7e424168cc37e7e63"

bot = Bot(token=TELEGRAM_TOKEN)

def check_surebets(update, context):
    url = f"https://api.the-odds-api.com/v4/sports/soccer/odds/"
    params = {
        "apiKey": ODDS_API_KEY,
        "regions": "eu",
        "markets": "h2h"
    }
    response = requests.get(url, params=params)
    data = response.json()

    surebets = []
    for match in data:
        odds = []
        for bookmaker in match["bookmakers"]:
            markets = bookmaker.get("markets", [])
            if markets:
                for outcome in markets[0]["outcomes"]:
                    odds.append(outcome["price"])

        if len(odds) >= 2:
            best_home = max([o for i,o in enumerate(odds) if i%2==0], default=0)
            best_away = max([o for i,o in enumerate(odds) if i%2==1], default=0)

            if best_home > 0 and best_away > 0:
                arbitrage = (1/best_home) + (1/best_away)
                if arbitrage < 1:
                    surebets.append(f"{match['home_team']} vs {match['away_team']} → Surebet !")

    if surebets:
        message = "\n".join(surebets)
    else:
        message = "Pas de surebets trouvés pour l’instant ⚽"

    bot.send_message(chat_id=CHAT_ID, text=message)

def start(update, context):
    update.message.reply_text("Bienvenue ! Utilise /corphinbot pour chercher des opportunités ⚡")

updater = Updater(TELEGRAM_TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("surebets", check_surebets))

updater.start_polling()
updater.idle()