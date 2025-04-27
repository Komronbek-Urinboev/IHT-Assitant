#main.py
import logging
import time
import telebot
import requests
from bot_instance import bot
#from clubs import *
from register import *
#from events import *
from schedule import send_schedule
from handler import list_users
from health_diagnose import *
from library import *
import praise
import verify
import quiz
#import send_music
import faq
import ban
#import SU_EVENTS
import ai_feature
import image_ai
import learn_AI_mode
import message_bot
import test
# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
if __name__ == "__main__":
    print("Бот запущен и работает...")
    time.sleep(1)  # <-- Даем секунду на регистрацию обработчиков
    try:
        bot.polling(none_stop=True, interval=0, timeout=10000000)
    except Exception as e:
        logging.error(f"Ошибка в работе бота: {e}")
        time.sleep(5)  # Перезапуск через 5 сек
