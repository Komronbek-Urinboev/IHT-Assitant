from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Message
from bot_instance import *
from db import users_db
from config import ADMIN_IDS, MUSIC_RECEIVER_ID
import time
from ban import blacklist

user_timers = {}
MUSIC_RECEIVER_ID = MUSIC_RECEIVER_ID
pending_users = {}

@bot.message_handler(commands=['send_music'])
def request_music(message: Message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане

    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    pending_users[user_id] = True  # Отмечаем, что пользователь ожидает ввода

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("🚫 Отменить"))

    bot.send_message(
        message.chat.id,
        "Отправьте название песни или сам файл музыки, который вы хотите передать. (Любая музыка либо название песни, которую вы сейчас отправите, отправится команде FM). Если случайно нажали на эту опцию, нажмите '🚫 Отменить'.",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_music)

def process_music(message: Message):
    user_id = message.from_user.id

    if message.text == "🚫 Отменить":
        pending_users.pop(user_id, None)  # Убираем пользователя из списка ожидающих
        bot.send_message(message.chat.id, "❌ Отправка музыки отменена.", reply_markup=ReplyKeyboardRemove())
        return

    if user_id not in pending_users:
        return  # Если пользователь не ожидал ввода, игнорируем

    user_info = users_db.get(str(message.chat.id), {})
    user_name = user_info.get("name", "Не указано")
    user_surname = user_info.get("surname", "Не указано")
    user_group = user_info.get("group", "Не указано")
    user_subgroup = user_info.get("in_group", "Не указано")

    music_info = None  # Инициализация переменной перед использованием

    if message.text:
        music_info = (
            f"🎵 Вам пришло новое название песни от:\n"
            f"👤 Имя: <code>{user_name}</code>\n"
            f"🔤 Фамилия: <code>{user_surname}</code>\n"
            f"📚 Группа: <code>{user_group}</code>\n"
            f"🎶 Название песни: <code>{message.text}</code>"
        )
        bot.send_message(MUSIC_RECEIVER_ID, music_info, parse_mode="HTML")

    elif message.audio:
        music_info = (
            f"🎵 Вам пришел музыкальный файл от:\n"
            f"👤 Имя: <code>{user_name}</code>\n"
            f"🔤 Фамилия: <code>{user_surname}</code>\n"
            f"📚 Группа: <code>{user_group}</code>\n"
            f"🎶 Музыкальный файл:"
        )
        bot.send_message(MUSIC_RECEIVER_ID, music_info, parse_mode="HTML")
        bot.send_audio(MUSIC_RECEIVER_ID, message.audio.file_id, caption="🎵:")

    else:
        bot.send_message(message.chat.id, "❌ Неподдерживаемый формат. Пожалуйста, отправьте название песни или музыкальный файл.")
        return

    # Сообщение для админов
    admin_message = (
        f"🔔 <b>Для администрации</b>\n"
        f"👤 {user_name} {user_surname}\n"
        f"📚 Группа: {user_group}, Подгруппа: {user_subgroup}\n"
        f"🎵 Отправил песню/музыку: {music_info}"
    )
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, admin_message, parse_mode="HTML")

    bot.send_message(message.chat.id, "✅ Музыка успешно отправлена!", reply_markup=ReplyKeyboardRemove())
    pending_users.pop(user_id, None)  # Убираем пользователя из списка ожидающих

print("Модуль send_music загружен")
