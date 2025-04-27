#health_diagnose
from recomendation import *
from bot_instance import *
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

def calculate_calories_from_steps(steps):
    return steps * 0.04

def calculate_water_intake(weight, gender):
    if gender == "male":
        base_water_intake = 35
    else:
        base_water_intake = 31
    water_intake = base_water_intake * weight
    return water_intake / 1000  # Литры

def activity_level(steps):
    if steps < 5000:
        return "low"
    elif steps < 10000:
        return "medium"
    else:
        return "high"

def calculate_excess_weight(weight, height):
    """Вычисляет избыточный вес и цель для нормального веса."""
    height_m = height / 100  # Рост в метрах
    max_normal_weight = 24.9 * (height_m ** 2)  # Верхний предел нормального веса
    excess_weight = max(0, weight - max_normal_weight)
    return excess_weight, max_normal_weight

def provide_recommendations(bmi_category, water_intake, activity_level_str):
    recommendations = []

    # Рекомендации по ИМТ
    recommendations.extend(Recommendations.bmi_recommendations(bmi_category))

    # Рекомендации по воде
    recommendations.extend(Recommendations.water_intake_recommendations(water_intake))

    # Рекомендации по активности
    recommendations.extend(Recommendations.activity_level_recommendations(activity_level_str))

    return "\n".join(recommendations)

@bot.message_handler(commands=['diagnose123123hacked'])
def start_diagnose(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(KeyboardButton("Male"), KeyboardButton("Female"))
    msg = bot.send_message(message.chat.id, "Выберите ваш пол:", reply_markup=markup)
    bot.register_next_step_handler(msg, get_gender)

def get_gender(message):
    gender = message.text.lower()
    if gender not in ["male", "female"]:
        msg = bot.send_message(message.chat.id, "Некорректный ввод. Выберите пол, нажав на кнопку:")
        bot.register_next_step_handler(msg, get_gender)
        return
    bot.user_data = {"gender": gender}
    msg = bot.send_message(message.chat.id, "Введите ваш возраст:", reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, get_age)

def get_age(message):
    if not message.text.isdigit() or int(message.text) == 0:
        msg = bot.send_message(message.chat.id, "Ошибка! Введите корректный возраст (число больше 0):")
        bot.register_next_step_handler(msg, get_age)
        return
    bot.user_data["age"] = int(message.text)
    msg = bot.send_message(message.chat.id, "Введите ваш рост (см):")
    bot.register_next_step_handler(msg, get_height)

def get_height(message):
    if not message.text.isdigit() or int(message.text) == 0:
        msg = bot.send_message(message.chat.id, "Ошибка! Введите корректный рост (число больше 0):")
        bot.register_next_step_handler(msg, get_height)
        return
    bot.user_data["height"] = int(message.text)
    msg = bot.send_message(message.chat.id, "Введите ваш вес (кг):")
    bot.register_next_step_handler(msg, get_weight)

def get_weight(message):
    if not message.text.isdigit() or int(message.text) == 0:
        msg = bot.send_message(message.chat.id, "Ошибка! Введите корректный вес (число больше 0):")
        bot.register_next_step_handler(msg, get_weight)
        return
    bot.user_data["weight"] = int(message.text)
    msg = bot.send_message(message.chat.id, "Введите количество шагов в день (можно пропустить):")
    bot.register_next_step_handler(msg, get_steps)

def get_steps(message):
    steps = message.text.strip()
    bot.user_data["steps"] = int(steps) if steps.isdigit() else 0
    calculate_and_send_results(message.chat.id)

def calculate_and_send_results(chat_id):
    data = bot.user_data
    gender = data["gender"]
    age = data["age"]
    height = data["height"]
    weight = data["weight"]
    steps = data["steps"]

    # Проверка на ошибки
    if age == 0 or height == 0 or weight == 0:
        bot.send_message(chat_id, "⚠ Ошибка при расчетах: введены некорректные данные. Пожалуйста, попробуйте снова.")
        return

    calories_burned = calculate_calories_from_steps(steps)
    water_intake = calculate_water_intake(weight, gender)

    bmi = weight / (height / 100) ** 2
    if bmi < 18.5:
        bmi_category = "Недовес"
    elif 18.5 <= bmi < 24.9:
        bmi_category = "Нормальная масса тела"
    elif 25 <= bmi < 29.9:
        bmi_category = "Избыточный вес"
    else:
        bmi_category = "Ожирение"

    activity_level_str = activity_level(steps)
    excess_weight, max_normal_weight = calculate_excess_weight(weight, height)

    results = [
        f"📊 Ваш индекс массы тела (ИМТ): {bmi:.2f} ({bmi_category})",
        f"💧 Ваша норма воды: {water_intake:.2f} литра в день.",
        f"🏃 Уровень активности: {activity_level_str.capitalize()}",
        f"🔥 Калории, потраченные на шаги: {calories_burned:.2f} калорий."
    ]

    if bmi_category in ["Избыточный вес", "Ожирение"]:
        results.append(
            f"⚖ Ваш вес: {weight} кг. Максимальный нормальный вес: {max_normal_weight:.2f} кг.\n"
            f"📉 Избыточный вес: {excess_weight:.2f} кг. Рекомендуется достичь нормального ИМТ."
        )

    bot.send_message(chat_id, "\n".join(results))

    recommendations = provide_recommendations(bmi_category, water_intake, activity_level_str)
    bot.send_message(chat_id, "🏅 Ваши персональные рекомендации:\n" + recommendations)
