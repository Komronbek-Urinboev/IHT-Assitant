#message_bot.py
from bot_instance import *
import db
from config import ADMIN_IDS
from ban import blacklist
import time
user_timers = {}

def get_user_telegram_id(user_id):
    user = db.get_user_by_id(user_id)
    if user:
        return user.get("telegram_id")
    return None

# Команда /say (текст, фото, документ)
@bot.message_handler(commands=['say'])
def send_message(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⛔ У вас нет прав для выполнения этой команды.")
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "⚠ Используйте: /say [ID] [текст]")
        return

    user_id = parts[1]
    text = parts[2]

    telegram_id = get_user_telegram_id(user_id)
    if not telegram_id:
        bot.reply_to(message, f"❌ Пользователь {user_id} не найден в базе.")
        return

    # Проверяем, не заблокировал ли пользователь бота
    try:
        bot.send_chat_action(telegram_id, "typing")
    except telebot.apihelper.ApiException as e:
        if "Forbidden" in str(e):
            bot.reply_to(message, f"🚫 Пользователь {user_id} заблокировал бота.")
        else:
            bot.reply_to(message, f"⚠ Ошибка при отправке сообщения пользователю {user_id}.")
        return

    # Отправляем текст
    bot.send_message(telegram_id, text)
    bot.reply_to(message, f"✅ Сообщение отправлено пользователю {user_id}.")

# Обработчик фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⛔ У вас нет прав на отправку фото.")
        return

    parts = message.caption.split(maxsplit=1) if message.caption else []
    if len(parts) < 2:
        bot.reply_to(message, "⚠ Используйте: отправьте фото + подпись [ID] [текст]")
        return

    user_id = parts[0]
    caption = parts[1]

    telegram_id = get_user_telegram_id(user_id)
    if not telegram_id:
        bot.reply_to(message, f"❌ Пользователь {user_id} не найден в базе.")
        return

    bot.send_photo(telegram_id, message.photo[-1].file_id, caption=caption)
    bot.reply_to(message, f"✅ Фото отправлено пользователю {user_id}.")

# Обработчик документов
@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "⛔ У вас нет прав на отправку документов.")
        return

    parts = message.caption.split(maxsplit=1) if message.caption else []
    if len(parts) < 2:
        bot.reply_to(message, "⚠ Используйте: отправьте документ + подпись [ID] [текст]")
        return

    user_id = parts[0]
    caption = parts[1]

    telegram_id = get_user_telegram_id(user_id)
    if not telegram_id:
        bot.reply_to(message, f"❌ Пользователь {user_id} не найден в базе.")
        return

    bot.send_document(telegram_id, message.document.file_id, caption=caption)
    bot.reply_to(message, f"✅ Документ отправлен пользователю {user_id}.")


print("Модуль message загружен")