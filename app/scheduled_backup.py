import schedule
import time
from datetime import datetime
from backup import create_backup
from loguru import logger
import os

# Настройка логирования
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logger.add(
    os.path.join(LOG_DIR, "scheduled_backup.log"),
    format="[{time:YYYY-MM-DD HH:mm:ss}] {level}: {message}",
    level="INFO",
    rotation="1 week"
)

def scheduled_backup():
    """Функция для создания резервной копии по расписанию"""
    try:
        logger.info("Запуск планового резервного копирования")
        backup_file = create_backup()
        logger.info(f"Плановое резервное копирование успешно завершено: {backup_file}")
    except Exception as e:
        logger.error(f"Ошибка при плановом резервном копировании: {str(e)}")

def main():
    # Настройка расписания
    # Каждый день в 00:00
    schedule.every().day.at("00:00").do(scheduled_backup)
    # Каждую неделю в воскресенье в 12:00
    schedule.every().sunday.at("12:00").do(scheduled_backup)
    # Каждый месяц 1-го числа в 03:00
    schedule.every().month_start.at("03:00").do(scheduled_backup)

    logger.info("Планировщик резервного копирования запущен")
    
    # Создаем первую копию при запуске
    scheduled_backup()
    
    # Бесконечный цикл для выполнения задач по расписанию
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверяем расписание каждую минуту

if __name__ == "__main__":
    main() 