import json
from bot_instance import *

# Функция для загрузки данных пользователей из JSON
def load_data():
    with open('biggest_project.json', 'r', encoding='utf-8') as file:
        return json.load(file)


# Функция для сохранения данных пользователей в JSON
def save_data(users_data):
    with open('biggest_project.json', 'w', encoding='utf-8') as file:
        json.dump(users_data, file, indent=4, ensure_ascii=False)


# ID администратора
ADMIN_ID = 7393504121  # Убедитесь, что это ваш правильный ID


# Функция для обработки команды /verify
@bot.message_handler(commands=['verify'])
def verify_user(message):
    if message.from_user.id == ADMIN_ID:  # Используем прямое сравнение чисел
        try:
            user_id = message.text.split()[1]  # Получаем ID пользователя
            users_data = load_data()  # Загружаем данные пользователей

            if user_id in users_data:
                # Добавляем звездочку к имени пользователя
                users_data[user_id]["name"] += " 🌟"

                # Сохраняем обновленные данные в JSON
                save_data(users_data)

                # Уведомляем пользователя
                bot.send_message(user_id, "Вы стали премиум пользователем 🌟")
                bot.reply_to(message, f"Пользователь {user_id} стал премиум 🌟")
            else:
                bot.reply_to(message, "Пользователь с таким ID не найден.")
        except IndexError:
            bot.reply_to(message, "Пожалуйста, укажите ID пользователя для верификации.")
    else:
        bot.reply_to(message, "Вы не имеете прав на выполнение этой команды.")

@bot.message_handler(commands=['/'])
def ver_prog_user(message):
    if message.from_user.id == ADMIN_ID:  # Используем прямое сравнение чисел
        try:
            user_id = message.text.split()[1]  # Получаем ID пользователя
            users_data = load_data()  # Загружаем данные пользователей

            if user_id in users_data:
                # Добавляем звездочку к имени пользователя
                users_data[user_id]["name"] += "👨‍💻"

                # Сохраняем обновленные данные в JSON
                save_data(users_data)

                # Уведомляем пользователя
                bot.send_message(user_id, "Вам дали значок разработчика 👨‍💻")
                bot.reply_to(message, f"Пользователь {user_id} получил значок разработчика 👨‍💻")
            else:
                bot.reply_to(message, "Пользователь с таким ID не найден.")
        except IndexError:
            bot.reply_to(message, "Пожалуйста, укажите ID пользователя для верификации.")
    else:
        bot.reply_to(message, "Вы не имеете прав на выполнение этой команды.")

print("Модуль verify загружен")