BOT_TOKEN = "7741936950:AAHODs1t0U66CSSLViJj8jfiQTzfimfxrAw"
PEXELS_API_KEY = "3QzGz2xy7n7N90Vfl6ouPK0NGIIYPJBmKYKKLnL6XIGv9oyC8F7frbnR"

from bot_instance import *
import requests

PEXELS_URL = "https://api.pexels.com/v1/search"


@bot.message_handler(commands=["image"])
def search_photos(message):
    query = message.text.replace("/image", "").strip()

    if not query:
        bot.send_message(message.chat.id, "Пожалуйста, укажи запрос после /image. Например: /image sunset")
        return

    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 4}

    response = requests.get(PEXELS_URL, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        photos = data.get("photos", [])

        if not photos:
            bot.send_message(message.chat.id, "Извините, но я не нашел подходящих фото 😢")
            return

        media_group = [telebot.types.InputMediaPhoto(photo["src"]["large2x"]) for photo in photos]
        bot.send_media_group(message.chat.id, media_group)

    else:
        bot.send_message(message.chat.id, "Ошибка при получении данных 😕")

print("Модуль image_ai загружен")