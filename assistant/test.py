from bot_instance import bot
from telebot import types
import time
import json
import random
import re
import logging
from text import about, ai, help, policy, devs, commands

# Если необходимо, задайте список заблокированных пользователей
blacklist = []  # Например: [123456789, 987654321]

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Общие словари для ограничения скорости (rate limiting)
user_timers = {}
user_timers_top = {}

BOOKS = [
    {"title": "Январьский выпуск газеты - 2025", "message_id": 46},
    {"title": "Алгебра 10 класс. РУ", "message_id": 9},
    {"title": "Биология 10 класс. РУ", "message_id": 10},
    {"title": "ОГП 10 класс. РУ", "message_id": 11},
    {"title": "География 10 класс. РУ", "message_id": 13},
    {"title": "Геометрия 10 класс. РУ", "message_id": 14},
    {"title": "Информатика 10 класс. РУ", "message_id": 15},
    {"title": "Всемирная история 10 класс. РУ", "message_id": 16},
    {"title": "Химия 10 класс. РУ", "message_id": 17},
    {"title": "Узбекский язык 10 класс. РУ", "message_id": 18},
    {"title": "История Узбекистана 10 класс. РУ", "message_id": 19},
    {"title": "Русский язык 10 класс. РУ", "message_id": 20},
    {"title": "Математика часть 1 - 11 Класс. РУ", "message_id": 22},
    {"title": "Математика часть 2 - 11 Класс. РУ", "message_id": 23},
    {"title": "Астрономия - 11 Класс. РУ", "message_id": 24},
    {"title": "Биология - 11 Класс. РУ", "message_id": 26},
    {"title": "ОГП - 11 Класс. РУ", "message_id": 27},
    {"title": "Физика - 11 Класс. РУ", "message_id": 28},
    {"title": "Всемирная история - 11 Класс. РУ", "message_id": 29},
    {"title": "Литература часть 1 - 11 Класс. РУ", "message_id": 30},
    {"title": "Литература часть 2 - 11 Класс. РУ", "message_id": 31},
    {"title": "Узбекский язык - 11 Класс. РУ", "message_id": 32},
    {"title": "История Узбекистана - 11 Класс. РУ", "message_id": 33},
    {"title": "Русский язык - 11 Класс. РУ", "message_id": 34},
    {"title": "Основы предпринимательства - 11 Класс. РУ", "message_id": 35},
    {"title": "Самаркандский вестник", "message_id": 37},
    {"title": "Вестник 📕 часть 1", "message_id": 38},
    {"title": "Вестник 📕 часть 2", "message_id": 39},
    {"title": "Информатика - 11 класс. РУ", "message_id": 44},
]
CHANNEL_ID = -1002302327144  # Укажите ID канала, откуда пересылаются книги


def get_books_markup(page=0, per_page=9):
    """
    Генерирует инлайн-клавиатуру с книгами.
    Кнопки добавляются по одной в строке.
    В конце клавиатуры добавлена кнопка «Назад», которая возвращает пользователя в главное меню.
    """
    markup = types.InlineKeyboardMarkup(row_width=1)
    start = page * per_page
    end = start + per_page
    books_on_page = BOOKS[start:end]
    for book in books_on_page:
        markup.add(types.InlineKeyboardButton(book["title"], callback_data=f"book_{book['message_id']}"))

    # Если возможно перемещение между страницами – добавляем кнопки навигации
    if page > 0:
        markup.add(types.InlineKeyboardButton("<<<<<", callback_data=f"prev_{page - 1}"))
    if end < len(BOOKS):
        markup.add(types.InlineKeyboardButton(">>>>>", callback_data=f"next_{page + 1}"))

    # Кнопка возврата в главное меню
    markup.add(types.InlineKeyboardButton("Назад", callback_data="back_to_menu_lib"))
    return markup


@bot.callback_query_handler(func=lambda call: call.data.startswith("book_"))
def send_book(call):
    """Пересылает выбранную книгу (сообщение) из канала пользователю."""
    try:
        message_id = int(call.data.split("_")[1])
        bot.forward_message(call.from_user.id, CHANNEL_ID, message_id)
    except Exception as e:
        bot.send_message(call.from_user.id, f"Ошибка пересылки: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("next_"))
def next_page(call):
    """Листает страницу вперед."""
    page = int(call.data.split("_")[1])
    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=get_books_markup(page))


@bot.callback_query_handler(func=lambda call: call.data.startswith("prev_"))
def prev_page(call):
    """Листает страницу назад."""
    page = int(call.data.split("_")[1])
    bot.edit_message_reply_markup(call.message.chat.id,
                                  call.message.message_id,
                                  reply_markup=get_books_markup(page))


@bot.callback_query_handler(func=lambda call: call.data == "back_to_menu_lib")
def back_to_menu_lib(call):
    """Обрабатывает кнопку 'Назад' из библиотеки и возвращает пользователя в главное меню."""
    try:
        chat_id = call.message.chat.id
        bot.delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_menu())
    except Exception as e:
        logging.error(f"Ошибка возврата в главное меню из библиотеки: {e}")


# ================== МОДУЛЬ "ПОХВАЛИ МЕНЯ" ==================
# Реализовано в точности по вашему исходнику
def escape_markdown(text):
    """Экранирует специальные символы для MarkdownV2."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)


def get_random_praise(exclude=None):
    try:
        with open("praise.txt", "r", encoding="utf-8") as file:
            praises = [line.strip() for line in file.readlines() if line.strip()]
        if not praises:
            logging.warning("Файл praise.txt пуст!")
            return "Ты замечательный!"
        exclude = exclude.strip() if exclude else None
        if exclude and exclude in praises:
            praises.remove(exclude)
        return random.choice(praises) if praises else "Ты великолепен!"
    except Exception as e:
        logging.error(f"Ошибка при загрузке похвал: {e}")
        return "Ты крутой!"


@bot.message_handler(commands=['praise'])
def send_praise(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()
    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Ограничение частоты
    user_timers[user_id] = current_time
    praise_text = get_random_praise()
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Похвали меня", callback_data="new_praise"))
    bot.send_message(message.chat.id, escape_markdown(praise_text), reply_markup=markup, parse_mode="MarkdownV2")


@bot.callback_query_handler(func=lambda call: call.data == "new_praise")
def update_praise(call):
    bot.answer_callback_query(call.id)  # Убираем "⌛ Ожидание..."
    current_text = call.message.text.strip()
    new_praise = get_random_praise(exclude=current_text)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Похвали меня", callback_data="new_praise"))
    if new_praise != current_text:
        try:
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=escape_markdown(new_praise),
                                  reply_markup=markup,
                                  parse_mode="MarkdownV2")
        except Exception as e:
            logging.error(f"Ошибка при обновлении похвалы: {e}")
            bot.answer_callback_query(call.id, "Ошибка обновления сообщения. Попробуй снова!")


print("Модуль praise загружен")

# ================== МОДУЛЬ "ТОП-5 УЧАСТНИКОВ" ==================
USERS_FILE = "biggest_project.json"
try:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    users = {}


def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


def top_players_fn(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    current_time = time.time()
    if user_id in user_timers_top and current_time - user_timers_top[user_id] < 10:
        return
    user_timers_top[user_id] = current_time
    if user_id in blacklist:
        return
    top_list = sorted(users.items(), key=lambda x: x[1].get("score", 0), reverse=True)[:5]
    if not top_list:
        bot.send_message(chat_id, "❌ Пока никто не набрал очков.")
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_menu())
        return
    top_text = "🏆 Топ-5 участников викторины:\n\n"
    for i, (uid, data) in enumerate(top_list, start=1):
        name = data.get("name", "Без имени")
        surname = data.get("surname", "")
        score = data.get("score", 0)
        full_name = f"{name} {surname}".strip()
        top_text += f"{i}. {full_name} — {score} баллов\n"
    bot.send_message(chat_id, top_text)
    bot.send_message(chat_id, "Главное меню:", reply_markup=main_menu())


@bot.message_handler(commands=["top"])
def top_players_message(message):
    user_id = message.from_user.id
    current_time = time.time()
    if user_id in user_timers_top and current_time - user_timers_top[user_id] < 10:
        return
    user_timers_top[user_id] = current_time
    if user_id in blacklist:
        return
    top_list = sorted(users.items(), key=lambda x: x[1].get("score", 0), reverse=True)[:5]
    if not top_list:
        bot.send_message(message.chat.id, "❌ Пока никто не набрал очков.")
        return
    top_text = "🏆 Топ-5 участников викторины:\n\n"
    for i, (uid, data) in enumerate(top_list, start=1):
        name = data.get("name", "Без имени")
        surname = data.get("surname", "")
        score = data.get("score", 0)
        full_name = f"{name} {surname}".strip()
        top_text += f"{i}. {full_name} — {score} баллов\n"
    bot.send_message(message.chat.id, top_text)


# ================== МОДУЛЬ "FAQ" ==================
CHANNELS_ID_FAQ = -1002476745050  # Укажите ID канала для пересылки ответов на FAQ
faqs = [
    {"title": "Что это за бот?", "message_id": 9},
    {"title": "Кто создал этот бот?", "message_id": 10},
    {"title": "На каком языке программирования написан бот?", "message_id": 11},
    {"title": "Как скачать книгу через бота?", "message_id": 12},
    {"title": "Как добавить бота в канал IHT Books свои книги?", "message_id": 13},
    {"title": "Что делать, если бот не отвечает?", "message_id": 15},
    {"title": "Как связаться с разработчиками?", "message_id": 16},
    {"title": "Как удалить свои данные из бота?", "message_id": 17},
    {"title": "Можно ли изменить свои данные?", "message_id": 18},
]


def get_faq_markup(page=0, per_page=7):
    """
    Генерирует инлайн-клавиатуру для FAQ.
    Каждая кнопка располагается в отдельной строке.
    """
    markup = types.InlineKeyboardMarkup(row_width=1)
    start = page * per_page
    end = start + per_page
    faqs_on_page = faqs[start:end]
    for faq in faqs_on_page:
        button = types.InlineKeyboardButton(f"📌 {faq['title']}",
                                            callback_data=f"faqitem_{faq['message_id']}")
        markup.add(button)
    if page > 0:
        markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data=f"faqprev_{page - 1}"))
    if end < len(faqs):
        markup.add(types.InlineKeyboardButton("Вперед ➡", callback_data=f"faqnext_{page + 1}"))
    return markup


@bot.message_handler(commands=['faqs'])
def show_faqs(message):
    user_id = message.from_user.id
    current_time = time.time()
    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return
    user_timers[user_id] = current_time
    if message.from_user.id in blacklist:
        return
    bot.send_message(message.chat.id, "📚 Часто задаваемые вопросы:")
    bot.send_message(message.chat.id, "Выберите вопрос:", reply_markup=get_faq_markup())


@bot.callback_query_handler(func=lambda call: call.data.startswith("faqitem_"))
def send_faq(call):
    """
    При выборе FAQ-вопроса пересылается соответствующее сообщение из канала
    с ответом и добавляется кнопка «Назад», возвращающая в главное меню.
    """
    try:
        _, msg_id = call.data.split("_")
        message_id = int(msg_id)
        back_markup = types.InlineKeyboardMarkup(row_width=1)
        back_markup.add(types.InlineKeyboardButton("Назад", callback_data="faq_back"))
        bot.copy_message(chat_id=call.from_user.id,
                         from_chat_id=CHANNELS_ID_FAQ,
                         message_id=message_id,
                         reply_markup=back_markup)
    except Exception as e:
        logging.error(f"Ошибка при обработке FAQ-item: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("faqnext_"))
def faq_next(call):
    try:
        page = int(call.data.split("_")[1])
        bot.edit_message_reply_markup(call.message.chat.id,
                                      call.message.message_id,
                                      reply_markup=get_faq_markup(page))
    except Exception as e:
        logging.error(f"Ошибка при переключении страницы FAQ: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("faqprev_"))
def faq_prev(call):
    try:
        page = int(call.data.split("_")[1])
        bot.edit_message_reply_markup(call.message.chat.id,
                                      call.message.message_id,
                                      reply_markup=get_faq_markup(page))
    except Exception as e:
        logging.error(f"Ошибка при переключении страницы FAQ: {e}")


@bot.callback_query_handler(func=lambda call: call.data == "faq_back")
def faq_back(call):
    try:
        chat_id = call.message.chat.id
        bot.delete_message(chat_id, call.message.message_id)
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_menu())
    except Exception as e:
        logging.error(f"Ошибка при возврате в главное меню: {e}")


# ================== ГЛАВНОЕ МЕНЮ ==================
def main_menu():
    """
    Возвращает инлайн-клавиатуру главного меню с кнопками, расположенными вертикально.
    """
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("ИИ", callback_data="ai"))
    markup.add(types.InlineKeyboardButton("Библиотека", callback_data="library"))
    markup.add(types.InlineKeyboardButton("Похвали меня", callback_data="praise"))
    markup.add(types.InlineKeyboardButton("Топ-5 участников викторины", callback_data="top_players"))
    markup.add(types.InlineKeyboardButton("Информация о боте", callback_data="bot_info"))
    markup.add(types.InlineKeyboardButton("FAQ", callback_data="faq"))
    markup.add(types.InlineKeyboardButton("Help me", callback_data="commands"))
    markup.add(types.InlineKeyboardButton("Политика использования", callback_data="usage_policy"))
    markup.add(types.InlineKeyboardButton("Разработчики бота", callback_data="developers"))
    return markup


@bot.message_handler(commands=['menu'])
def start(message):
    bot.send_message(message.chat.id, "Добро пожаловать! Выберите нужное из меню ниже:")
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=main_menu())


@bot.callback_query_handler(func=lambda call: call.data in [
    "ai", "library", "praise", "top_players", "bot_info",
    "faq", "commands", "usage_policy", "developers"
])
def main_menu_callback(call):
    """
    Обрабатывает нажатия по главному меню: удаляет предыдущее сообщение
    и отправляет текстовый ответ в новом сообщении, а затем – главное меню.
    """
    chat_id = call.message.chat.id
    bot.delete_message(chat_id, call.message.message_id)
    if call.data == "ai":
        bot.send_message(chat_id,
                         ai, parse_mode="HTML")
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_menu())
    elif call.data == "library":
        bot.send_message(chat_id, "📚 Библиотека:")
        bot.send_message(chat_id, "Выберите книгу:", reply_markup=get_books_markup())
    elif call.data == "praise":
        praise_text = get_random_praise()
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Похвали меня", callback_data="new_praise"))
        bot.send_message(chat_id, escape_markdown(praise_text), reply_markup=markup, parse_mode="MarkdownV2")
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_menu())
    elif call.data == "top_players":
        top_players_fn(call)
    elif call.data == "bot_info":
        bot.send_message(chat_id, about, parse_mode="HTML")
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_menu())
    elif call.data == "faq":
        bot.send_message(chat_id, "📚 Часто задаваемые вопросы:")
        bot.send_message(chat_id, "Выберите вопрос:", reply_markup=get_faq_markup())
    elif call.data == "commands":
        bot.send_message(chat_id, help, parse_mode="HTML")
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_menu())
    elif call.data == "usage_policy":
        bot.send_message(chat_id,
                         policy, parse_mode="HTML")
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_menu())
    elif call.data == "developers":
        bot.send_message(chat_id,
                         devs, parse_mode="HTML")
        bot.send_message(chat_id, "Главное меню:", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id)
