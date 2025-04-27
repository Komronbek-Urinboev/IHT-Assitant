#logger.py
import logging
from bot_instance import bot
from config import ADMIN_IDS


class TelegramLogHandler(logging.Handler):
    def emit(self, record):
        log_entry = self.format(record)  # Форматируем лог

        # Экранируем специальные символы для HTML
        log_entry = (
            log_entry.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, f"📜 <b>Новый лог:</b>\n<pre>{log_entry}</pre>", parse_mode="HTML")
            except Exception as e:
                print(f"Ошибка отправки лога: {e}")


# Настройка логирования
logger = logging.getLogger("TelegramLogger")
logger.setLevel(logging.INFO)  # Можно изменить уровень логирования

# Добавляем наш обработчик
telegram_handler = TelegramLogHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")  # Формат логов
telegram_handler.setFormatter(formatter)
logger.addHandler(telegram_handler)
