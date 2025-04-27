#library.py
import time
from ban import blacklist
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


from bot_instance import *
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
user_timers = {}

CHANNEL_ID = -1002302327144  # Замени на ID своего канала


# ======= 📚 ОБЫЧНАЯ БИБЛИОТЕКА (по страницам) =======
def get_books_markup(page=0, per_page=9):
    markup = InlineKeyboardMarkup()
    start = page * per_page
    end = start + per_page
    books_on_page = BOOKS[start:end]

    for book in books_on_page:
        markup.add(InlineKeyboardButton(book["title"], callback_data=f"book_{book['message_id']}"))

    if end < len(BOOKS):
        markup.add(InlineKeyboardButton(">>>>>", callback_data=f"next_{page+1}"))

    if page > 0:
        markup.add(InlineKeyboardButton("<<<<<", callback_data=f"prev_{page-1}"))

    return markup

@bot.message_handler(commands=['library'])
def show_library(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    bot.send_message(message.chat.id, "📚 Библиотека:", reply_markup=get_books_markup())

@bot.callback_query_handler(func=lambda call: call.data.startswith("book_"))
def send_book(call):
    """Пересылает книгу пользователю."""
    message_id = int(call.data.split("_")[1])
    bot.forward_message(call.from_user.id, CHANNEL_ID, message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("next_"))
def next_page(call):
    """Перелистывает страницу вперед."""
    page = int(call.data.split("_")[1])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_books_markup(page))

@bot.callback_query_handler(func=lambda call: call.data.startswith("prev_"))
def prev_page(call):
    """Перелистывает страницу назад."""
    page = int(call.data.split("_")[1])
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_books_markup(page))

# ======= 🔍 ИНЛАЙН ПОИСК =======
@bot.inline_handler(lambda query: len(query.query) > 2)
def inline_search(query):
    """Обрабатывает инлайн-запросы и ищет книги по названию."""
    results = []
    search_text = query.query.lower()

    for book in BOOKS:
        if search_text in book["title"].lower():
            result = InlineQueryResultArticle(
                id=str(book["message_id"]),
                title=book["title"],
                input_message_content=InputTextMessageContent(f"📖 {book['title']}"),
                reply_markup=get_inline_book_button(book["message_id"])
            )
            results.append(result)

    if not results:
        results.append(InlineQueryResultArticle(
            id="not_found",
            title="Ничего не найдено",
            input_message_content=InputTextMessageContent("Книга не найдена 📚"),
        ))

    bot.answer_inline_query(query.id, results, cache_time=1)

def get_inline_book_button(message_id):
    """Создает inline-кнопку для пересылки книги."""
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📥 Скачать", callback_data=f"book_{message_id}"))
    return markup

print("Модуль library загружен")