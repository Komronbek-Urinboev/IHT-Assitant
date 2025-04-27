import difflib
import google.generativeai as genai
from bot_instance import *
import time
import random

from ban import blacklist
user_timers = {}

# Укажи свой API-ключ Gemini
GEMINI_API_KEY = "AIzaSyBQO89TC_kEQwSt7lqQJIwy7m5yaCw3y2g"
genai.configure(api_key=GEMINI_API_KEY)


# Локальная база вопросов и ответов
FAQ = {
    "что это за бот": "Это многофункциональный Telegram-бот, созданный командой разработчиков из клуба IHT BotLab.",
    "кто создал этот бот": "Бот разработан командой из клуба IHT BotLab, а также другими участниками проекта.",
    "кто создатель этого бота": "Бот разработан командой из клуба IHT BotLab, а также другими участниками проекта.",
    "на каком языке написан бот": "Бот написан на языке Python с использованием библиотеки telebot.",
    "как связаться с разработчиками бота": "Вы можете написать в чат поддержки или обратиться к администратору: @LenovoFlex14 @Komronbek_Urinboev",
    "как удалить данные": "Для удаления данных свяжитесь с @Komronbek_Urinboev.",
    "как подать идею": "Используйте команду /su_ideas и следуйте инструкции.",
    "кто принимает решения": "Все решения принимает СЮ.",
    "iht botlab": "IHT BotLab — это клуб, созданный для учащихся, желающих изучать программирование и разрабатывать Telegram-ботов.\nЛаборатория, где участники осваивают основы Python и работу с Telegram API.\n\n🔹 Чему обучают в клубе?\nОсновы Python — переменные, циклы, функции.\nРабота с Telegram API — создание и управление ботами.\nХранение данных — JSON и работа с пользователями.\nСоздание UI — inline-кнопки, клавиатуры.\nРабота с медиа — фото, видео, документы в Telegram.\nХостинг — запуск ботов на серверах.",
    "клуб iht botlab": "IHT BotLab — это клуб, созданный для учащихся, желающих изучать программирование и разрабатывать Telegram-ботов.\nЛаборатория, где участники осваивают основы Python и работу с Telegram API.\n\n🔹 Чему обучают в клубе?\nОсновы Python — переменные, циклы, функции.\nРабота с Telegram API — создание и управление ботами.\nХранение данных — JSON и работа с пользователями.\nСоздание UI — inline-кнопки, клавиатуры.\nРабота с медиа — фото, видео, документы в Telegram.\nХостинг — запуск ботов на серверах.",
    "что такое iht botlab": "IHT BotLab — это клуб, созданный для учащихся, желающих изучать программирование и разрабатывать Telegram-ботов.\nЛаборатория, где участники осваивают основы Python и работу с Telegram API.\n\n🔹 Чему обучают в клубе?\nОсновы Python — переменные, циклы, функции.\nРабота с Telegram API — создание и управление ботами.\nХранение данных — JSON и работа с пользователями.\nСоздание UI — inline-кнопки, клавиатуры.\nРабота с медиа — фото, видео, документы в Telegram.\nХостинг — запуск ботов на серверах.",
    "информация о клубе iht botlab": "IHT BotLab — это клуб, созданный для учащихся, желающих изучать программирование и разрабатывать Telegram-ботов.\nЛаборатория, где участники осваивают основы Python и работу с Telegram API.\n\n🔹 Чему обучают в клубе?\nОсновы Python — переменные, циклы, функции.\nРабота с Telegram API — создание и управление ботами.\nХранение данных — JSON и работа с пользователями.\nСоздание UI — inline-кнопки, клавиатуры.\nРабота с медиа — фото, видео, документы в Telegram.\nХостинг — запуск ботов на серверах.",
#    "кто такой уринбоев комронбек": "Уринбоев Комронбек - 1 из разработчиков этого бота\nЯ целеустремленный человек, который с детства увлекается программированием и разрабатывает собственные проекты. Сейчас я учусь в INTERNATIONAL HOUSE-TASHKENT ACADEMIC LYCEUM в группе 1-ТН-3 и возглавляю клуб IHT BotLab. Я активно создаю Telegram-ботов, работаю с базами данных и внедряю искусственный интеллект в свои проекты.",
#    "уринбоев комронбек": "Уринбоев Комронбек - 1 из разработчиков этого бота\nЯ целеустремленный человек, который с детства увлекается программированием и разрабатывает собственные проекты. Сейчас я учусь в INTERNATIONAL HOUSE-TASHKENT ACADEMIC LYCEUM в группе 1-ТН-3 и возглавляю клуб IHT BotLab. Я активно создаю Telegram-ботов, работаю с базами данных и внедряю искусственный интеллект в свои проекты.",
    "сидиков хабибулло": "Сидиков Хабибулло - 1 из разработчиков этого бота\nЯ упорный человек, который с детства увлекается программированием,  графическому дизайну и  разработки собственных проектов. Сейчас я учусь в INTERNATIONAL HOUSE-TASHKENT ACADEMIC LYCEUM в группе 1-ТН-3 и возглавляю клуб IHT BotLab. Я активно принимаю участия в создаю Telegram-ботов, работаю с базами данных и отвечаю за медиа часть в клубе IHT BotLab",
    "кто такой сидиков хабибулло": "Сидиков Хабибулло - 1 из разработчиков этого бота\nЯ упорный человек, который с детства увлекается программированием,  графическому дизайну и  разработки собственных проектов. Сейчас я учусь в INTERNATIONAL HOUSE-TASHKENT ACADEMIC LYCEUM в группе 1-ТН-3 и возглавляю клуб IHT BotLab. Я активно принимаю участия в создаю Telegram-ботов, работаю с базами данных и отвечаю за медиа часть в клубе IHT BotLab"

}

# Функция поиска наиболее похожего вопроса
def find_best_match(user_question: str):
    questions = list(FAQ.keys())
    matches = difflib.get_close_matches(user_question, questions, n=1, cutoff=0.7)
    return matches[0] if matches else None



# Функция разбиения длинного сообщения на части
def split_message(text, max_length=4000):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Обработчик команды /ask
@bot.message_handler(commands=['ask'])
def ask_ai(message):
    if message.from_user.id in blacklist:
        return  # Игнорируем команду, если пользователь в бане
    user_id = message.from_user.id
    current_time = time.time()

    if user_id in user_timers and current_time - user_timers[user_id] < 10:
        return  # Просто игнорируем сообщение

    user_timers[user_id] = current_time
    user_text = message.text.replace("/ask", "").strip().lower()
    if not user_text:
        bot.reply_to(message, "Вы не ввели вопрос. Используйте: `/ask ваш вопрос`")
        return

    # Показываем progress bar
    progress_msg = bot.send_message(message.chat.id, "⌛ Генерация ответа: [0%]")
    progress_steps = [
        "▱▱▱▱▱▱▱▱▱▱▱ 0%",
        "▰▱▱▱▱▱▱▱▱▱▱ 5%",
        "▰▰▱▱▱▱▱▱▱▱▱ 14%",
        "▰▰▰▱▱▱▱▱▱▱▱ 16%",
        "▰▰▰▰▱▱▱▱▱▱▱ 22%",
        "▰▰▰▰▱▱▱▱▱▱▱ 28%",
        "▰▰▰▰▱▱▱▱▱▱▱ 37%",
        "▰▰▰▰▰▱▱▱▱▱▱ 39%",
        "▰▰▰▰▰▱▱▱▱▱▱ 43%",
        "▰▰▰▰▰▰▱▱▱▱▱ 48%",
        "▰▰▰▰▰▰▰▰▱▱▱ 55%",
        "▰▰▰▰▰▰▰▰▱▱▱ 63%",
        "▰▰▰▰▰▰▰▰▱▱▱ 69%",
        "▰▰▰▰▰▰▰▰▱▱▱ 75%",
        "▰▰▰▰▰▰▰▰▰▱▱ 79%",
        "▰▰▰▰▰▰▰▰▰▱▱ 80%",
        "▰▰▰▰▰▰▰▰▰▰▱▱ 85%",
        "▰▰▰▰▰▰▰▰▰▰▰▱ 92%",
        "▰▰▰▰▰▰▰▰▰▰▰▰▱ 94%",
        "▰▰▰▰▰▰▰▰▰▰▰▰▱ 99%",
        "▰▰▰▰▰▰▰▰▰▰▰▰▰▰ 100%"
    ]


    for step in progress_steps:
        time.sleep(random.uniform(0.1, 0.3))  # Случайная задержка от 0.1 до 1 секунды
        bot.edit_message_text(f"⌛ Генерация ответа: {step}", chat_id=message.chat.id,
                              message_id=progress_msg.message_id)

    # Ищем ответ в FAQ
    best_match = find_best_match(user_text)
    if best_match:
        bot.edit_message_text(f"✅ Ответ найден:\n {FAQ[best_match]}", chat_id=message.chat.id,
                              message_id=progress_msg.message_id)
        return

    # Если вопрос не найден — отправляем в ИИ
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(user_text)
        response_text = response.text

        # Если ответ длиннее 4000 символов, разбиваем его на части и отправляем поочередно
        parts = split_message(response_text)
        bot.edit_message_text(f"✅ Ответ: {parts[0]}", chat_id=message.chat.id,
                              message_id=progress_msg.message_id)
        for part in parts[1:]:
            bot.send_message(message.chat.id, part)

    except Exception as e:
        bot.edit_message_text("❌ Ошибка при обработке запроса. Попробуйте позже.", chat_id=message.chat.id,
                              message_id=progress_msg.message_id)
        print(f"Ошибка: {e}")
print("Модуль ai_feature загружен")