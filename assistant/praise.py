#praise.py
from bot_instance import bot
import random
import re
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import time
from ban import blacklist

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

user_timers = {}

def escape_markdown(text):
    """Экранирует специальные символы для MarkdownV2"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


# Функция для получения случайной похвалы
def get_random_praise(exclude=None):
    try:
        with open("praise.txt", "r", encoding="utf-8") as file:
            praises = [line.strip() for line in file.readlines() if line.strip()]

        if not praises:
            logging.warning("Файл praise.txt пуст!")
            return "Ты замечательный!"

        # Исключаем текущую похвалу
        exclude = exclude.strip() if exclude else None
        if exclude and exclude in praises:
            praises.remove(exclude)

        return random.choice(praises) if praises else "Ты великолепен!"
    except Exception as e:
        logging.error(f"Ошибка при загрузке похвал: {e}")
        return "Ты крутой!"


# Команда /praise
@bot.message_handler(commands=['praise'])
def send_praise(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    praise_text = get_random_praise()
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Похвали меня", callback_data="new_praise"))
    bot.send_message(message.chat.id, escape_markdown(praise_text), reply_markup=markup, parse_mode="MarkdownV2")


# Обработчик inline-кнопки "Похвали меня"
@bot.callback_query_handler(func=lambda call: call.data == "new_praise")
def update_praise(call):
    bot.answer_callback_query(call.id)  # Убираем "⌛ Ожидание..."

    current_text = call.message.text.strip()
    new_praise = get_random_praise(exclude=current_text)

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Похвали меня", callback_data="new_praise"))

    # Проверяем, изменился ли текст
    if new_praise != current_text:
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=escape_markdown(new_praise), reply_markup=markup, parse_mode="MarkdownV2")
        except Exception as e:
            logging.error(f"Ошибка при обновлении похвалы: {e}")
            bot.answer_callback_query(call.id, "Ошибка обновления сообщения. Попробуй снова!")

print("Модуль praise загружен")
