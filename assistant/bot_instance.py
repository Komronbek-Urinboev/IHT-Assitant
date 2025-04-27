# bot_instance.py
import telebot
from config import TOKEN2


API_TOKEN = TOKEN2
bot = telebot.TeleBot(API_TOKEN)

print("Модуль bot_instance загружен")