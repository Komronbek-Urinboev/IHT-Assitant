import json
import random
from bot_instance import *
from telebot import types  # исправлено
import time
from ban import blacklist

USERS_FILE = "biggest_project.json"
user_timers = {}

try:
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    users = {}

from quiz_questions import questions

ADMIN_IDS = [7393504121]
active_question = None
correct_answers_count = 0
answered_users = set()


def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)


@bot.message_handler(commands=["quiz_start"])
def start_quiz(message):
    global active_question, correct_answers_count, answered_users

    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ У вас нет прав для запуска викторины.")
        return

    if not questions:
        bot.send_message(message.chat.id, "❌ Ошибка: Вопросы отсутствуют.")
        return

    active_question = random.choice(questions)
    correct_answers_count = 0
    answered_users.clear()

    question_text = f"{active_question['question']}\n\nВыберите ответ:"
    markup = types.InlineKeyboardMarkup()
    for i, answer in enumerate(active_question["answers"]):
        markup.add(types.InlineKeyboardButton(answer, callback_data=f"quiz_{i}"))

    sent_users = 0
    for user_id in users.keys():
        try:
            bot.send_message(int(user_id), question_text, reply_markup=markup)
            sent_users += 1
        except:
            continue

    bot.send_message(message.chat.id, f"📨 Вопрос был отправлен {sent_users} пользователям!")


@bot.callback_query_handler(func=lambda call: call.data.startswith("quiz_"))
def handle_quiz_answer(call):
    global correct_answers_count, active_question

    if active_question is None:
        bot.answer_callback_query(call.id, "❌ Викторина не активна!")
        return

    user_id = str(call.from_user.id)

    if user_id in answered_users:
        bot.answer_callback_query(call.id, "⚠️ Вы уже отвечали на этот вопрос!")
        return

    answer_idx = int(call.data.split("_")[1])

    if user_id not in users:
        users[user_id] = {"score": 0}

    if answer_idx == active_question.get("correct"):
        users[user_id]["score"] += 1
        correct_answers_count += 1
        answered_users.add(user_id)
        bot.answer_callback_query(call.id, "✅ Правильный ответ!")
        save_users()

        if correct_answers_count >= 8:
            for uid in users.keys():
                try:
                    bot.send_message(int(uid), "🎉 Вопрос закрыт, 8 человек ответили правильно!")
                except:
                    continue
            active_question = None
    else:
        bot.answer_callback_query(call.id, "❌ Неправильно!")
        bot.send_message(call.message.chat.id, active_question.get("explanation", "❌ Ошибка!"))

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass


@bot.message_handler(commands=["top"])
def top_players(message):
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return

    user_timers[user_id] = current_time

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


print("Модуль quiz загружен")
