import requests
import json
from geopy.geocoders import Nominatim
import logging
import asyncio
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters


tokens = {}
with open("config.json", "r") as f:
    tokens = json.load(f)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


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
    await update.message.reply_text(f"Ваш ID: {update.message.from_user.id}")


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


    '''req = request.get_json(force=True)

    action = req.get('queryResult').get('action')

    result = req.get("queryResult")
    parameters = result.get("parameters")

    if parameters.get('location').get('city'):
        geolocator = Nominatim(user_agent='weather-bot')
        location = geolocator.geocode(parameters.get('location').get('city'))
        lat = location.latitude
        long = location.longitude
        weather_req = requests.get('https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&appid={}'.format(lat, long, tokens["openweather-api-token"]))
        current_weather = json.loads(weather_req.text)['current']
        temp = round(current_weather['temp'] - 273.15)
        feels_like = round(current_weather['feels_like'] - 273.15)
        clouds = current_weather['clouds']
        wind_speed = current_weather['wind_speed']

    return {'fulfillmentText': 'Сейчас температура воздуха - {} градусов, ощущается как {} градусов, облачность - {}%, скорость ветра - {}м/с'.format(str(temp), str(feels_like), str(clouds), str(wind_speed))}'''

