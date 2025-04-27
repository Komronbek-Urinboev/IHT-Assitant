from ban import *
import time
from text import steps
import random

def simulate_hack(chat_id):
    message = bot.send_message(chat_id, "<b>>> Подключение к удалённому серверу...</b>", parse_mode='html')


    progress = 0
    for step in steps:
        progress += 100 // len(steps)
        progress_bar = f"[{'█' * (progress // 10)}{' ' * (10 - progress // 10)}] {progress}%"

        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message.message_id,
            text=f"<pre>{'\n'.join(steps[:steps.index(step) + 1])}</pre>\n{progress_bar}",
            parse_mode='html'
        )
        time.sleep(random.uniform(0, 1))

    time.sleep(random.uniform(2, 3))
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message.message_id,
        text="<b>Присоеденяйся к нам, IHT BotLab!</b>",
        parse_mode='html'
    )
@bot.message_handler(commands=['root'])
def start_handler(message):
    bot.send_message(
        message.chat.id,
        f"<b>Здравствуйте, IHT ADMIN!</b>\nГотовы к запуску всех атак?",
        parse_mode='html'
    )
    simulate_hack(message.chat.id)