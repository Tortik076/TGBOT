import os
import telebot

TOKEN = os.getenv("TOKEN") or "API_TOKEN"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я простой эхо-бот. Напиши что-нибудь.")

@bot.message_handler()
def echo(message):
    bot.send_message(message.chat.id, message.text)

print("Бот запущен...")
bot.infinity_polling()

