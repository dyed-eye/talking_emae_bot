import requests
import json
from geopy.geocoders import Nominatim
import logging
import asyncio
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import spacy
from datetime import datetime
import random
from bs4 import BeautifulSoup
import collections

collections.Callable = collections.abc.Callable
# that's essential for correct work of BeautifulSoup.find_all() method

tokens = {}
with open("config.json", "r") as f:
    tokens = json.load(f)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

nlp = spacy.load("ru_core_news_lg")
ruler = nlp.add_pipe("entity_ruler").from_disk("./patterns.jsonl")


def get_weather(location):
    geolocator = Nominatim(user_agent='weather-bot')
    location = geolocator.geocode(location)
    lat = location.latitude
    long = location.longitude
    weather_req = requests.get('https://api.openweathermap.org/data/2.5/weather?lat={}&lon={}&appid={}'.format(lat, long, tokens["openweather-api-token"]))
    weather = json.loads(weather_req.text)
    if weather['cod'] < 299:
        temp = round(weather['main']['temp'] - 273.15)
        feels_like = round(weather['main']['feels_like'] - 273.15)
        clouds = weather['clouds']['all']
        wind_speed = weather['wind']['speed']

        return 'Сейчас температура воздуха - {} градусов, ощущается как {} градусов, облачность - {}%, скорость ветра - {}м/с'.format(str(temp), str(feels_like), str(clouds), str(wind_speed))
    else:
        return 'Извините, сервис погоды временно умер...'
      
def tell_a_joke():
    date = datetime.now().strftime("%Y-%m-%d")
    jokes_json = {}
    with open("jokes.json", "r") as f:
        jokes_json = json.load(f)
    if jokes_json['date'] != date:
        page = requests.get('http://anekdotov.net/anekdot/day/').text
        soup = BeautifulSoup(page, 'lxml')
        divs = soup.body.find_all('div', class_='anekdot')
        jokes_parsed = []
        for div in divs:
            jokes_parsed.append(div.text)
        jokes_json['date'] = date
        jokes_json['jokes'] = jokes_parsed
        with open("jokes.json", "w") as f:
            json.dump(jokes_json, f)
        return random.choice(jokes_parsed)
    else:
        return random.choice(jokes_json['jokes'])
    

# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет, {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    doc = nlp(update.message.text)
    q_weather = False
    q_loc = []
    q_joy = False
    for ent in doc.ents:
        if ent.label_ == "WEATHER":
            q_weather = True
        elif ent.label_ == "JOY":
            q_joy = True
        elif ent.label_ == "LOC":
            q_loc.append(ent.text)
        
    if q_weather & (len(q_loc) > 0):
        await update.message.reply_text(get_weather(q_loc[0]))
    elif q_joy:
        await update.message.reply_text(tell_a_joke())
    else:
        await update.message.reply_text("Я не понимаю, что вы от меня хотите :(")
        return


def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(tokens["telegram-api-token"]).build()
    
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
