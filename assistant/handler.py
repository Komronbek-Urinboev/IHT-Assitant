#handler.py

from bot_instance import bot
from config import ADMIN_IDS
from db import users_db
import time
from text import about, policy, help, admin, SU_about_text, SU_about_text_ru, commands, ai, devs, schedule
from ban import blacklist
user_timers = {}
@bot.message_handler(commands=['list_users'])
def list_users(message):
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    # Проверяем, является ли пользователь администратором
    if message.from_user.id not in ADMIN_IDS:  # Используем from_user.id, а не chat.id
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return

    if not users_db:
        bot.send_message(message.chat.id, "Пока никто не зарегистрировался.")
        return

    # Формируем список пользователей
    user_list = "📋 *Список зарегистрированных пользователей:*\n\n"
    messages = []

    for idx, user in enumerate(users_db.values(), start=1):
        user_info = (
            f"{idx}. Имя: <code>{user.get('name', 'Не указано')}</code>\n"
            f"   Фамилия: <code>{user.get('surname', 'Не указано')}</code>\n"
            f"   Группа: <code>{user.get('group', 'Не указано')}</code>\n"
            f"   Подгруппа: <code>{user.get('in_group', 'Не указано')}</code>\n"
            f"   Кабинет: <code>{user.get('room', 'Не указано')}</code>\n"
            f"   Telegram ID: <code>{user.get('telegram_id', 'Не указано')}</code>\n"
            f"   Username: @{user.get('username', 'Не указано')}\n\n"
        )

        if len(user_list) + len(user_info) >= 4000:
            messages.append(user_list)
            user_list = ""

        user_list += user_info

    if user_list:
        messages.append(user_list)

    # Отправляем сообщения всем администраторам
    for admin_id in ADMIN_IDS:
        for msg in messages:
            bot.send_message(admin_id, msg, parse_mode="HTML")


# Словарь для хранения времени последнего использования команды
user_last_command_time = {}


@bot.message_handler(commands=["about"])
def about_command(mess):
    if mess.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = mess.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 15:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    user_id = str(mess.chat.id)

    # Проверяем, зарегистрирован ли пользователь
    if user_id not in users_db:
        bot.send_message(user_id,
                         "Вы не зарегистрированы! Пожалуйста, сначала пройдите регистрацию с помощью команды /start.")
        return

    # Проверяем, не использовал ли пользователь команду слишком часто
    last_time = user_last_command_time.get(user_id, 0)
    if time.time() - last_time < 5:  # 5 секунд задержка
        return  # Игнорируем команду

    # Обновляем время последнего использования команды
    user_last_command_time[user_id] = time.time()

    bot.send_message(user_id, about, parse_mode="HTML")

@bot.message_handler(commands=["policy"])
def about_command(mess):
    if mess.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = mess.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    if str(mess.chat.id) not in users_db:
        bot.send_message(mess.chat.id,
                         "Вы не зарегистрированы! Пожалуйста, сначала пройдите регистрацию с помощью команды /start.")
    else:
        bot.send_message(mess.chat.id, policy)

@bot.message_handler(commands=["help"])
def help_command(mess):  # Изменил название функции
    if mess.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = mess.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    if str(mess.chat.id) not in users_db:
        bot.send_message(mess.chat.id,
                         "Вы не зарегистрированы! Пожалуйста, сначала пройдите регистрацию с помощью команды /start.")
    else:
        bot.send_message(mess.chat.id, help, parse_mode="HTML")

@bot.message_handler(commands=["admin"])
def admin_command(mess):  # Изменил название функции
    if mess.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = mess.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 15:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    if str(mess.chat.id) not in users_db:
        bot.send_message(mess.chat.id,
                         "Вы не зарегистрированы! Пожалуйста, сначала пройдите регистрацию с помощью команды /start.")
    else:
        bot.send_message(mess.chat.id, admin, parse_mode="HTML")

#######
@bot.message_handler(commands=["root1"])
def root(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    if str(message.chat.id) not in users_db:
        bot.send_message(message.chat.id,
                         "Вы не зарегистрированы! Пожалуйста, сначала пройдите регистрацию с помощью команды /start.")
    else:
        bot.send_message(message.chat.id, f"Авторизация успешно выполнена\nВы вошли в корневую папку системы сервера!"
                                          f"\nУвы, тут пусто, но зато вы успещно устоновили себе майнер")


@bot.message_handler(commands=['antispam'])
def antispam_command(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    bot.send_message(message.chat.id, "✅ Команда выполнена!")  # Ответ при первом вызове




@bot.message_handler(commands=['su'])
def antispam_command(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 15:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    bot.send_message(message.chat.id, f"{SU_about_text}\n\n{SU_about_text_ru}")  # Ответ при первом вызове


@bot.message_handler(commands=['COO_Commands'])
def antispam_command(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 15:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    bot.send_message(message.chat.id, commands)  # Ответ при первом вызове

@bot.message_handler(commands=['ai'])
def ai_command(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 15:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    bot.send_message(message.chat.id, ai)  # Ответ при первом вызове


@bot.message_handler(commands=['devs'])
def devs_command(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 15:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    bot.send_message(message.chat.id, devs, parse_mode="HTML")  # Ответ при первом вызове

@bot.message_handler(commands=['schedule'])
def devs_command(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 15:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    bot.send_message(message.chat.id, schedule, parse_mode="HTML")  # Ответ при первом вызове

print("Модуль handler загружен")