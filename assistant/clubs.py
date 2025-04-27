#clubs.py

from text import infoIHT_BotLab, info_Speaking_Club_IHT, info_Media_and_Design, IHT_Talk_Club, Chess_Club, SU_Frontend_Development_UI_UX_Design, Debate_Club, FC_Club
from bot_instance import bot
from db import users_db
from config import ADMIN_IDS
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from ban import blacklist
import time

user_timers = {}
# Список клубов и их владельцев
CLUBS = {
    "IHT BotLab": 7393504121,
    "Speaking Club IHT": 7393504121,
    "Media & Design": 7393504121,
    "IHT Talk Club": 7393504121,
    "Chess Club": 7393504121,
    "SU по Frontend Development и UI/UX Design": 7393504121,
    "Debate Club": 7393504121,
    "Football Club": 7393504121
}

# Информация о клубах
club_info = {
    "IHT BotLab": infoIHT_BotLab,
    "Speaking Club IHT": info_Speaking_Club_IHT,
    "Media & Design": info_Media_and_Design,
    "IHT Talk Club":IHT_Talk_Club,
    "Chess Club": Chess_Club,
    "SU по Frontend Development и UI/UX Design": SU_Frontend_Development_UI_UX_Design,
    "Debate Club": Debate_Club,
    "Football Club": FC_Club
}

@bot.message_handler(commands=['choose_club'])
def choose_club(message):
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    """Команда для выбора клуба"""
    if str(message.chat.id) not in users_db:
        bot.send_message(
            message.chat.id,
            "Вы не зарегистрированы! Пожалуйста, сначала пройдите регистрацию с помощью команды /start."
        )
        return

    show_club_options(message)

def show_club_options(message):
    """Отправляет пользователю список клубов в виде Inline-кнопок"""
    markup = InlineKeyboardMarkup()
    for club_name in CLUBS.keys():
        markup.add(InlineKeyboardButton(text=club_name, callback_data=f"club_{club_name}"))

    bot.send_message(
        message.chat.id,
        "Выберите клуб, в который хотите подать заявку:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("club_"))
def show_club_info(call):
    """Отправляет информацию о выбранном клубе с Inline-кнопками"""
    selected_club = call.data.replace("club_", "")

    # Inline-кнопки
    markup = InlineKeyboardMarkup()
    apply_button = InlineKeyboardButton("✅ Подать заявку", callback_data=f"apply_{selected_club}")
    back_button = InlineKeyboardButton("🔙 Вернуться назад", callback_data="back_to_clubs")
    markup.add(apply_button, back_button)

    # Отправляем информацию о клубе
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"<b>Информация о клубе {selected_club}:</b>\n\n{club_info[selected_club]}",
        parse_mode="HTML",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "back_to_clubs")
def back_to_club_selection(call):
    """Обрабатывает кнопку 'Вернуться назад' и удаляет предыдущее сообщение"""
    bot.delete_message(call.message.chat.id, call.message.message_id)  # Удаляем предыдущее сообщение
    show_club_options(call.message)  # Отправляем список клубов


@bot.callback_query_handler(func=lambda call: call.data.startswith("apply_"))
def process_club_application(call):
    """Обрабатывает нажатие на кнопку 'Подать заявку'"""
    selected_club = call.data.replace("apply_", "")

    user_info = users_db.get(str(call.message.chat.id), {})
    club_owner_id = CLUBS[selected_club]

    club_message = (
        f"Новая заявка в клуб {selected_club}:\n"
        f"Имя: {user_info.get('name', 'Не указано')}\n"
        f"Фамилия: {user_info.get('surname', 'Не указано')}\n"
        f"Группа: {user_info.get('group', 'Не указано')}\n"
        f"Подгруппа: {user_info.get('in_group', 'Не указано')}\n"
        f"Telegram ID: {user_info.get('telegram_id', 'Не указано')}\n"
        f"Username: @{user_info.get('username', 'Не указано')}\n"
    )

    bot.send_message(club_owner_id, club_message, parse_mode="HTML")

    # Уведомляем администратора
    for admin_id in ADMIN_IDS:
        bot.send_message(
            admin_id,
            f"<b>Для администрации</b>\n\nПользователь {user_info.get('name')}\n"
            f"Юзернейм: @{user_info.get('username')}\n"
            f"Группа: {user_info.get('group')}\n"
            f"Успешно подал заявку в клуб {selected_club}.",
            parse_mode="HTML"
        )

    # Уведомляем пользователя
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"Вы успешно подали заявку в клуб <b>{selected_club}</b>. Ожидайте обратной связи!",
        #text=f"Вы успешно подали заявку в клуб <b>{selected_club}</b> в тестовом режиме бота, если бот среагрировал, значит тут все работает!",
        parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda call: call.data == "back_to_clubs")
def back_to_club_selection(call):
    """Обрабатывает кнопку 'Вернуться назад'"""
    show_club_options(call.message)

print("Модуль clubs загружен")