import os
import telebot
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hola, soy HerramientaUtilBot. Envíame un comando.")

@bot.message_handler(commands=['precio'])
def precio(message):
    try:
        r = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json")
        data = r.json()
        usd = data["bpi"]["USD"]["rate"]
        bot.reply_to(message, f"El precio actual es: {usd} USD")
    except:
        bot.reply_to(message, "Error obteniendo el precio.")

@bot.message_handler(func=lambda m: True)
def echo(message):
    bot.reply_to(message, "No entiendo ese comando. Usa /precio o /start.")

bot.polling()