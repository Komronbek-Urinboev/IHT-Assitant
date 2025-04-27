#schedule.py
from bot_instance import bot
from db import users_db
import json
from ban import blacklist
import time
# Загрузка расписания из schedule.json
def load_schedule():
    with open("schedule.json", "r", encoding="utf-8") as f:
        return json.load(f)
user_timers = {}
@bot.message_handler(commands=['schedulebeta_03_03_2025_test'])
def send_schedule(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    telegram_id = str(message.chat.id)
    if telegram_id not in users_db:
        bot.send_message(message.chat.id, "Вы не зарегистрированы! Пожалуйста, зарегистрируйтесь.")
        return


    user_info = users_db[telegram_id]
    group = user_info["group"].replace("-", "_")  # Приводим формат группы к правильному
    in_group = user_info["in_group"]

    # Составляем ключ для поиска расписания
    schedule_key = f"{group}_{in_group}"

    schedule = load_schedule()

    if schedule_key in schedule:
        weekly_schedule = schedule[schedule_key]

        # Формируем сообщение с расписанием
        schedule_message = "Ваше расписание на неделю:\n"
        for day, classes in weekly_schedule.items():
            schedule_message += f"\n{day}:\n{classes}\n"

        bot.send_message(message.chat.id, schedule_message, parse_mode="HTML")
        bot.send_message(message.chat.id, f"Нашли ошибку? Напишите тех.поддержке /admin")
    else:
        bot.send_message(message.chat.id, "Мы работаем над этим 🏗👨‍💻\nНо пока что, для вашей группы и подгруппы нет расписания.")

print("Модуль schedule загружен")