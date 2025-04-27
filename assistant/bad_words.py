from bot_instance import *
import time
import json
import re

BANNED_WORDS = {"плохое", "слово", "ругательство"}  # Запрещённые слова
users_file = "users.json"

def load_users():
    try:
        with open(users_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    with open(users_file, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

def contains_banned_words(text):
    text = text.lower()
    text = re.sub(r"[^а-яёa-z0-9 ]", "", text)  # Убираем знаки препинания
    words = text.split()
    return any(word in BANNED_WORDS for word in words)

def is_blocked(user_id):
    users = load_users()
    if str(user_id) in users and "blocked_until" in users[str(user_id)]:
        if time.time() < users[str(user_id)]["blocked_until"]:
            return True
        else:
            del users[str(user_id)]["blocked_until"]
            save_users(users)
    return False

def block_user(user_id):
    users = load_users()
    users[str(user_id)] = users.get(str(user_id), {})
    users[str(user_id)]["blocked_until"] = time.time() + 600  # 10 минут
    save_users(users)

@bot.message_handler(func=lambda message: is_blocked(message.chat.id))
def blocked_message(message):
    bot.send_message(message.chat.id, "Вы заблокированы на 10 минут за использование запрещённых слов.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if contains_banned_words(message.text):
        block_user(message.chat.id)
        bot.send_message(message.chat.id, "Вы заблокированы на 10 минут за использование запрещённых слов.")
print("Модуль bad_words загружен")