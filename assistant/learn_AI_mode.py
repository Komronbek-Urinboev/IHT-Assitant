from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, Message
from bot_instance import *
from db import users_db
from config import ADMIN_IDS
import time
from ban import blacklist

user_timers = {}
IDEA_RECEIVER_IDS = [-4786549537]  # ID человека, которому отправляются идеи
pending_users = {}  # Словарь для хранения ожидающих подтверждения пользователей

@bot.message_handler(commands=['learn_ai'])
def request_ai_learn(message: Message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане

    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Игнорируем частые сообщения

    user_timers[user_id] = current_time
    pending_users[user_id] = True  # Отмечаем, что пользователь ожидает ввода идеи

    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("🚫 Отменить"))

    bot.send_message(
        message.chat.id,
        "Отправьте чему хотите обучить ИИ. На какой вопрос он будет отвечать, и какой ответ он выдаст. (Опишите всё чётко и ясно\nВопрос❓ - Ответ\nЧто это за группа ТН-3? - Ответ: Это самая лучшая группа)\nЕсли передумали, нажмите '🚫 Отменить'.",
        reply_markup=markup
    )
    bot.register_next_step_handler(message, process_ai_learn)


def process_ai_learn(message: Message):
    user_id = message.from_user.id

    if message.text == "🚫 Отменить":
        pending_users.pop(user_id, None)  # Убираем пользователя из списка ожидающих
        bot.send_message(message.chat.id, "❌ Процесс обучение отменена.", reply_markup=ReplyKeyboardRemove())
        return

    if user_id not in pending_users:
        return  # Если пользователь не ожидал ввода, игнорируем

    user_info = users_db.get(str(user_id), {})
    user_name = user_info.get("name", "Не указано")
    user_surname = user_info.get("surname", "Не указано")
    user_group = user_info.get("group", "Не указано")
    user_subgroup = user_info.get("in_group", "Не указано")

    learn_ai_info = (f"💡 Запрос на обучение ИИ:")
    learn_ai_info += f"\n👤 Имя: <code>{user_name}</code>"
    learn_ai_info += f"\n🔤 Фамилия: <code>{user_surname}</code>"
    learn_ai_info += f"\n📚 Группа: <code>{user_group}</code>"

    caption_text = message.caption if message.caption else ""

    # Функция отправки сообщения нескольким получателям
    def send_to_receivers(func, *args, **kwargs):
        for receiver_id in IDEA_RECEIVER_IDS:
            func(receiver_id, *args, **kwargs)

    if message.text and not message.photo and not message.video and not message.document and not message.audio:
        learn_ai_info += f"\n💡 Идея: <code>{message.text}</code>"
        send_to_receivers(bot.send_message, learn_ai_info, parse_mode="HTML")

    if message.photo:
        learn_ai_info += "\n📸 Отправлено фото"
        send_to_receivers(bot.send_message, learn_ai_info, parse_mode="HTML")
        send_to_receivers(bot.send_photo, message.photo[-1].file_id, caption=f"📸 Фото: {caption_text}")

    if message.video:
        learn_ai_info += "\n🎥 Отправлено видео"
        send_to_receivers(bot.send_message, learn_ai_info, parse_mode="HTML")
        send_to_receivers(bot.send_video, message.video.file_id, caption=f"🎥 Видео: {caption_text}")

    if message.document:
        learn_ai_info += "\n📂 Отправлен документ"
        send_to_receivers(bot.send_message, learn_ai_info, parse_mode="HTML")
        send_to_receivers(bot.send_document, message.document.file_id, caption=f"📂 Документ: {caption_text}")

    if message.audio:
        learn_ai_info += "\n🎵 Отправлен аудиофайл"
        send_to_receivers(bot.send_message, learn_ai_info, parse_mode="HTML")
        send_to_receivers(bot.send_audio, message.audio.file_id, caption=f"🎵 Аудиофайл: {caption_text}")

    if not message.text and not message.photo and not message.video and not message.document and not message.audio:
        bot.send_message(message.chat.id,
                         "❌ Неподдерживаемый формат. Пожалуйста, отправьте текст, фото, видео, документ или аудиофайл.")
        return

    admin_message = (
        f"🔔 <b>Для администрации</b>\n"
        f"👤 {user_name} {user_surname}\n"
        f"📚 Группа: {user_group}, Подгруппа: {user_subgroup}\n"
        f"💡 Отправил свои данные для ИИ: {learn_ai_info}"
    )
    for admin_id in ADMIN_IDS:
        bot.send_message(admin_id, admin_message, parse_mode="HTML")

    bot.send_message(message.chat.id, "✅ Ваш труд успешно отправлен на рассмотрение!", reply_markup=ReplyKeyboardRemove())
    pending_users.pop(user_id, None)

print("Модуль learn_AI_mode загружен")