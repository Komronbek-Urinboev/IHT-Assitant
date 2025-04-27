#register.py

from bot_instance import bot
from db import user_data, users_db, DB_FILE
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import json
from text import policy
from config import ADMIN_IDS
import time
from ban import blacklist


banned_words = {"плохое", "слово", "пример", "хуй", "член", "пидр", "сука"
,"соси", ".", "west", "niggers", "ебал", "сучка", "дебил", "jnerfnroimeo", "jjjsewd", "assets", "assets154"
}

# Функция проверки запрещенных слов
def contains_banned_word(text):
    text = text.lower()  # Приводим текст к нижнему регистру
    for word in banned_words:
        if word in text:
            return True
    return False
user_timers = {}
# Запрещённые символы для обычных пользователей
PREMIUM_ONLY_SYMBOLS = ["🌟", "👨‍💻"]
def contains_premium_symbols(text):
    return any(symbol in text for symbol in PREMIUM_ONLY_SYMBOLS)


# Функция для запроса имени
def ask_name(message):
    if contains_premium_symbols(message.text):
        bot.send_message(message.chat.id, "Этот символ 🌟 👨‍💻 доступен только премиум-пользователям или администрации. Регистрация отменена.\nДля повторной регистрации введите команду /start")
        return
    if contains_banned_word(message.text):
        bot.send_message(message.chat.id, "Ваше имя содержит запрещенные слова. Регистрация отменена на 10 минут.")

        # Проверяем, является ли чат супергруппой (ID чатов супергрупп < -1000000000000)
        if message.chat.type in ["supergroup", "group"]:
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + 600)
        return
    bot.send_message(message.chat.id, "Введите ваше имя:")
    bot.register_next_step_handler(message, ask_surname)


# Функция запроса фамилии
def ask_surname(message):
    if contains_premium_symbols(message.text):
        bot.send_message(message.chat.id, "Этот символ 🌟👨‍💻 доступен только премиум-пользователям или администрации. Регистрация отменена.\nДля повторной регистрации введите команду /start")
        return
    if contains_banned_word(message.text):
        bot.send_message(message.chat.id, "Ваше имя содержит запрещенные слова. Регистрация отменена на 10 минут.")

        # Проверяем, является ли чат супергруппой (ID чатов супергрупп < -1000000000000)
        if message.chat.type in ["supergroup", "group"]:
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + 600)
        return
    user_data[str(message.chat.id)] = {"name": message.text}
    bot.send_message(message.chat.id, "Введите вашу фамилию:")
    bot.register_next_step_handler(message, ask_group)


# Функция запроса группы
def ask_group(message):
    if contains_premium_symbols(message.text):
        bot.send_message(message.chat.id,
                         "Этот символ 🌟 доступен только премиум-пользователям или администрации. Регистрация отменена.\nДля повторной регистрации введите команду /start")
        return
    user_data[str(message.chat.id)]["surname"] = message.text  # Сохранение фамилии

    groups = ["1-ТН-1", "1-ТН-2", "1-ТН-3", "1-ТН-4", "1-АФ-1", "1-АФ-2", "1-СГ-1", "1-ВТН-1", "2-ТН-1", "2-ТН-2", "2-ТН-3", "2-СГ-1", "2-АФ-1", "2-АФ-2", "2-МТН-1", "2-МСГ-1", "2-ВТН-1","2-ВТН-2","2-ВСГ-3","2-ВСГ-4",]
    group_markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for i in range(0, len(groups), 2):  # Размещение кнопок по 2 в ряд
        group_markup.row(*[KeyboardButton(g) for g in groups[i:i + 2]])

    bot.send_message(message.chat.id, "Выберите свою учебную группу:", reply_markup=group_markup)
    bot.register_next_step_handler(message, lambda msg: validate_group(msg, groups))


def validate_group(message, groups):
    if message.text not in groups:
        bot.send_message(message.chat.id, "Некорректный выбор. Пожалуйста, выберите группу из предложенных вариантов.")
        return ask_group(message)
    user_data[str(message.chat.id)]["group"] = message.text
    ask_in_group(message)


def ask_in_group(message):
    if contains_premium_symbols(message.text):
        bot.send_message(message.chat.id,
                         "Этот символ 🌟👨‍💻 доступен только премиум-пользователям или администрации. Регистрация отменена.\nДля повторной регистрации введите команду /start")
        return

    subgroups = ["А", "В"]
    subgroup_markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    subgroup_markup.add(KeyboardButton("А"), KeyboardButton("В"))

    bot.send_message(message.chat.id, "Выберите свою подгруппу:", reply_markup=subgroup_markup)
    bot.register_next_step_handler(message, lambda msg: validate_subgroup(msg, subgroups))


def validate_subgroup(message, subgroups):
    if message.text not in subgroups:
        bot.send_message(message.chat.id,
                         "Некорректный выбор. Пожалуйста, выберите подгруппу из предложенных вариантов.")
        return ask_in_group(message)
    user_data[str(message.chat.id)]["subgroup"] = message.text

    hide_markup = ReplyKeyboardRemove()
    bot.send_message(message.chat.id, "Ещё чуть-чуть осталось...", reply_markup=hide_markup)
    ask_room(message)


# Функция запроса комнаты
def ask_room(message):
    if contains_premium_symbols(message.text):
        bot.send_message(message.chat.id,
                         "Этот символ 🌟👨‍💻 доступен только премиум-пользователям или администрации. Регистрация отменена.\nДля повторной регистрации введите команду /start")
        return
    if contains_banned_word(message.text):
        bot.send_message(message.chat.id, "Ваше имя содержит запрещенные слова. Регистрация отменена на 10 минут.")

        if message.chat.type in ["supergroup", "group"]:
            bot.restrict_chat_member(message.chat.id, message.from_user.id, until_date=time.time() + 600)
        return

    user_data[str(message.chat.id)]["in_group"] = message.text
    bot.send_message(message.chat.id, "Введите номер вашей комнаты (где проходит у вас кураторский час?):")
    bot.register_next_step_handler(message, save_room)


# Функция сохранения номера комнаты
def save_room(message):
    user_data[str(message.chat.id)]["room"] = message.text
    save_user_data(message)


# Функция сохранения данных
def save_user_data(message):
    telegram_id = str(message.chat.id)
    user_data[telegram_id]["telegram_id"] = telegram_id
    user_data[telegram_id]["username"] = message.chat.username if message.chat.username else "Не указано"

    users_db[telegram_id] = user_data[telegram_id]

    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users_db, f, indent=4, ensure_ascii=False)

    send_data_to_admin(user_data[telegram_id])

    bot.send_message(
        message.chat.id,
        "Регистрация завершена! Для дополнительной информации используйте команду /about.",
        reply_markup=ReplyKeyboardRemove()
    )

    user_data.pop(telegram_id, None)  # Очистка временных данных


def send_data_to_admin(user_info):
    admin_message = (
        f"Новый пользователь зарегистрирован:\n"
        f"Имя: <code>{user_info['name']}</code>\n"
        f"Фамилия: <code>{user_info['surname']}</code>\n"
        f"Группа: <code>{user_info['group']}</code>\n"
        f"Подгруппа: <code>{user_info['subgroup']}</code>\n"  # Исправлено
        f"Комната: <code>{user_info['room']}</code>\n"
        f"Telegram ID: <code>{user_info['telegram_id']}</code>\n"
        f"Username: @{user_info['username']}\n"
    )
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, admin_message, parse_mode="HTML")


def send_existing_data(message, user_info):
    existing_message = (
        f"Вы уже зарегистрированы. Вот ваши данные:\n"
        f"Имя: <code>{user_info.get('name', 'Не указано')}</code>\n"
        f"Фамилия: <code>{user_info.get('surname', 'Не указано')}</code>\n"
        f"Группа: <code>{user_info.get('group', 'Не указано')}</code>\n"
        f"Подгруппа: <code>{user_info.get('subgroup', 'Не указано')}</code>\n"
        f"Комната: <code>{user_info.get('room', 'Не указано')}</code>\n"
        f"Telegram ID: <code>{user_info.get('telegram_id', 'Не указано')}</code>\n"
        f"Username: @{user_info.get('username', 'Не указано')}\n"
    )
    bot.send_message(message.chat.id, existing_message, parse_mode="HTML")
    bot.send_message(message.chat.id, f"Используйте команду /menu - для открытия Главного Меню")
    bot.send_message(message.chat.id, "Сделали ошибку при регистрации? \nСообщите нам /admin")
    bot.send_message(message.chat.id, "Авторизация завершена! Для дополнительной информации используйте команду /about.")


# Команда /start
@bot.message_handler(commands=['start'])
def start_registration(message):
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    telegram_id = str(message.chat.id)

    if telegram_id in users_db:
        send_existing_data(message, users_db[telegram_id])
        return

    user_data[telegram_id] = {
        "telegram_id": telegram_id,
        "name": None,
        "surname": None,
        "group": None,
        "in_group": None,
        "room": None,
        "phone": None,
        "username": message.chat.username if message.chat.username else "Не указано",
    }
    bot.send_message(message.chat.id, f"С момента запуска бота и начала его использования вы автоматически соглашаетесь с <b>Пользовательским соглашением</b> и <b>Политикой конфиденциальности</b>. Ознакомьтесь с ними перед использованием, так как продолжение взаимодействия с ботом означает ваше полное согласие со всеми условиями. \n\n{policy}", parse_mode='HTML')
    bot.send_message(
        message.chat.id,
        f"Привет, <i>{message.chat.first_name}</i>!\n\n"
        f"Давайте проведём регистрацию в бот.",
        parse_mode='HTML'
    )
    ask_name(message)
