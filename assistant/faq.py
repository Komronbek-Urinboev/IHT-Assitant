#faq.py
from bot_instance import bot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
from ban import blacklist
import time

user_timers = {}
CHANNELS_ID = -1002476745050  # Укажи ID своего канала

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
    """Генерирует инлайн-клавиатуру для навигации по FAQ."""
    markup = InlineKeyboardMarkup()
    start = page * per_page
    end = start + per_page
    faqs_on_page = faqs[start:end]

    for faq in faqs_on_page:
        markup.add(InlineKeyboardButton(f"📌 {faq['title']}", callback_data=f"faqitem_{faq['message_id']}"))

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅ Назад", callback_data=f"faqprev_{page - 1}"))
    if end < len(faqs):
        nav_buttons.append(InlineKeyboardButton("Вперед ➡", callback_data=f"faqnext_{page + 1}"))

    if nav_buttons:
        markup.add(*nav_buttons)

    return markup


@bot.message_handler(commands=['faqs'])
def show_faqs(message):
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    """Отправляет список часто задаваемых вопросов."""
    bot.send_message(message.chat.id, "📚 Часто задаваемые вопросы:", reply_markup=get_faq_markup())


@bot.callback_query_handler(func=lambda call: call.data.startswith("faqitem_"))
def send_faq(call):
    """Пересылает сообщение с ответом на FAQ."""
    try:
        _, msg_id = call.data.split("_")
        message_id = int(msg_id)
        bot.forward_message(call.from_user.id, CHANNELS_ID, message_id)
    except (ValueError, IndexError) as e:
        logging.error(f"Ошибка при обработке callback_query: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("faqnext_"))
def next_page(call):
    """Листает FAQ вперед."""
    try:
        page = int(call.data.split("_")[1])
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_faq_markup(page))
    except Exception as e:
        logging.error(f"Ошибка при переключении страницы FAQ: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("faqprev_"))
def prev_page(call):
    """Листает FAQ назад."""
    try:
        page = int(call.data.split("_")[1])
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=get_faq_markup(page))
    except Exception as e:
        logging.error(f"Ошибка при переключении страницы FAQ: {e}")

print("Модуль faq загружен")