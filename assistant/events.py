#event.py

from text import gazeta_ly, day_6_eco, Business_Terminology_Classes
from bot_instance import bot
from db import users_db
from config import ADMIN_IDS
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import logging
import time
from ban import blacklist

user_timers = {}
# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Список клубов и их владельцев
EVENTS = {
    "Газета лицея": 7393504121,
    "6 ДНЕЙ ЗАГРЯЗНЕНИЯ МИРА": 7393504121,
    "Business Terminology Classes": 7393504121
}

event_info = {
    "Газета лицея": gazeta_ly,
    "6 ДНЕЙ ЗАГРЯЗНЕНИЯ МИРА": day_6_eco,
    "Business Terminology Classes":Business_Terminology_Classes
}


def ask_event(message):
    """Запрашиваем выбор мероприятия"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)

    # Добавляем кнопку "Отменить" в самое начало
    markup.add(KeyboardButton("❌ Отменить"))

    for event_name in EVENTS.keys():
        markup.add(KeyboardButton(text=event_name))

    bot.send_message(
        message.chat.id,
        "Выберите мероприятие, на которое хотите подать заявку:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_event_selection)


def process_event_selection(message):
    """Обрабатываем выбор мероприятия"""
    selected_event = message.text

    if selected_event == "❌ Отменить":
        bot.send_message(message.chat.id, "Вы отменили подачу заявки.", reply_markup=ReplyKeyboardRemove())
        return  # Завершаем процесс

    if selected_event not in EVENTS:
        bot.send_message(
            message.chat.id,
            "Неверный выбор. Пожалуйста, выберите мероприятие из списка."
        )
        ask_event(message)  # Повторно показываем список мероприятий
        return

    # Отправляем информацию о мероприятии и кнопки
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Подать заявку"))
    markup.add(KeyboardButton("🔙 Вернуться назад"))

    bot.send_message(message.chat.id, event_info[selected_event], reply_markup=markup)
    bot.register_next_step_handler(message, handle_event_action, selected_event)

    """Запрашиваем выбор мероприятия"""
    markup = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    for event_name in EVENTS.keys():
        markup.add(KeyboardButton(text=event_name))
    bot.send_message(
        message.chat.id,
        "Выберите мероприятие, на которое хотите подать заявку:",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_event_selection)


def process_event_selection(message):
    if message.text == "❌ Отменить":
        bot.send_message(message.chat.id, "Вы отменили отправку резюме.", reply_markup=ReplyKeyboardRemove())
        return
    """Обрабатываем выбор мероприятия"""
    selected_event = message.text

    if selected_event not in EVENTS:
        bot.send_message(
            message.chat.id,
            "Неверный выбор. Пожалуйста, выберите мероприятие из списка."
        )
        ask_event(message)  # Повторно показываем список мероприятий
        return

    # Отправляем информацию о мероприятии и кнопки
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("✅ Подать заявку"))
    markup.add(KeyboardButton("🔙 Вернуться назад"))
    bot.send_message(message.chat.id, event_info[selected_event], reply_markup=markup)
    bot.register_next_step_handler(message, handle_event_action, selected_event)


def handle_event_action(message, selected_event):
    """Обрабатываем выбор пользователя после просмотра информации о мероприятии"""
    if message.text == "✅ Подать заявку":
        bot.send_message(message.chat.id,
                         "Теперь отправьте то, что от вас требуют: (текст, файл, фото, видео, голосовое сообщение или стикер).\nЕсли мероприятие дополнительно ничего не требует просто отправьте '.' ",
                         reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(message, handle_resume, selected_event)
    elif message.text == "🔙 Вернуться назад":
        if message.text == "❌ Отменить":
            bot.send_message(message.chat.id, "Вы остановили процесс.", reply_markup=ReplyKeyboardRemove())
            return
        ask_event(message)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, выберите один из доступных вариантов.")
        bot.register_next_step_handler(message, handle_event_action, selected_event)


def handle_resume(message, selected_event):
    if message.text == "❌ Отменить":
        bot.send_message(message.chat.id, "Вы отменили отправку заявки.", reply_markup=ReplyKeyboardRemove())
        return
    """Обрабатываем резюме пользователя"""
    user_info = users_db.get(str(message.chat.id), {})
    event_owner_id = EVENTS[selected_event]

    logging.info(f"Отправка резюме в чат ID: {event_owner_id}")

    if message.text:
        resume = message.text
        resume_type = "текст"
    elif message.photo:
        resume_type = "фото"
        file_id = message.photo[-1].file_id
        bot.send_photo(event_owner_id, file_id)
        resume = "Фото отправлено"
    elif message.video:
        resume_type = "видео"
        file_id = message.video.file_id
        bot.send_video(event_owner_id, file_id)
        resume = "Видео отправлено"
    elif message.document:
        resume_type = "файл"
        file_id = message.document.file_id
        bot.send_document(event_owner_id, file_id)
        resume = "Файл отправлен"
    elif message.voice:
        resume_type = "голосовое сообщение"
        file_id = message.voice.file_id
        bot.send_voice(event_owner_id, file_id)
        resume = "Голосовое сообщение отправлено"
    elif message.sticker:
        resume_type = "стикер"
        file_id = message.sticker.file_id
        bot.send_sticker(event_owner_id, file_id)
        resume = "Стикер отправлен"
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте ваше резюме.")
        return

    event_message = (
        f"Новая заявка на мероприятие {selected_event}:\n"
        f"Имя: {user_info.get('name', 'Не указано')}\n"
        f"Фамилия: {user_info.get('surname', 'Не указано')}\n"
        f"Группа: {user_info.get('group', 'Не указано')}\n"
        f"Telegram ID: {user_info.get('telegram_id', 'Не указано')}\n"
        f"Username: @{user_info.get('username', 'Не указано')}\n\n"
        f"Резюме ({resume_type}): {resume}"
    )

    try:
        bot.send_message(event_owner_id, event_message, parse_mode="HTML")
    except Exception as e:
        logging.error(f"Ошибка отправки резюме: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка при отправке резюме. Пожалуйста, попробуйте позже.")
        return

    bot.send_message(message.chat.id,
                     f"Вы успешно подали заявку на мероприятие <b>{selected_event}</b>. Ожидайте обратной связи!",
                     parse_mode="HTML")
    #bot.send_message(message.chat.id, f"Вы успешно подали заявку на мероприятие <b>{selected_event}</b> в тестовом режиме бота, если бот среагировал, значить функция подачи заявок работает!")

    for admin_id in ADMIN_IDS:
        bot.send_message(
            admin_id,
            f"<b>Для администрации</b>\n\nПользователь {user_info.get('name')}\n"
            f"Юзернейм: @{user_info.get('username')}\n"
            f"Группа: {user_info.get('group')}\n"
            f"Успешно подал заявку в ивент(событие) {selected_event}. \n\n"
            f"Резюме ({resume_type}): {resume} ",
            parse_mode="HTML")


@bot.message_handler(commands=['apply_event'])
def apply_event(message):
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    """Команда для подачи заявки на мероприятие"""
    if str(message.chat.id) not in users_db:
        bot.send_message(message.chat.id,
                         "Вы не зарегистрированы! Пожалуйста, сначала пройдите регистрацию с помощью команды /start.")
        return
    ask_event(message)

print("Модуль events загружен")