import os
import sys
from datetime import datetime
from loguru import logger

# Конфигурация
BACKUP_DIR = "backups"
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB", "images_db")
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")

# Настройка логирования
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logger.add(
    os.path.join(LOG_DIR, "backup.log"),
    format="[{time:YYYY-MM-DD HH:mm:ss}] {level}: {message}",
    level="INFO"
)

def create_backup():
    """Создание резервной копии базы данных"""
    try:
        # Создаем директорию для бэкапов если её нет
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Формируем имя файла бэкапа
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        backup_file = os.path.join(BACKUP_DIR, f'backup_{timestamp}.sql')
        
        # Формируем команду для pg_dump
        command = f'PGPASSWORD="{DB_PASSWORD}" pg_dump -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} -F p > {backup_file}'
        
        # Выполняем команду
        result = os.system(command)
        
        if result == 0:
            logger.info(f"Резервная копия успешно создана: {backup_file}")
            return backup_file
        else:
            raise Exception(f"Ошибка при создании резервной копии. Код ошибки: {result}")
            
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {str(e)}")
        raise

def restore_backup(backup_file):
    """Восстановление базы данных из резервной копии"""
    try:
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Файл резервной копии не найден: {backup_file}")
        
        # Формируем команду для восстановления
        command = f'PGPASSWORD="{DB_PASSWORD}" psql -h {DB_HOST} -p {DB_PORT} -U {DB_USER} -d {DB_NAME} < {backup_file}'
        
        # Выполняем команду
        result = os.system(command)
        
        if result == 0:
            logger.info(f"База данных успешно восстановлена из файла: {backup_file}")
        else:
            raise Exception(f"Ошибка при восстановлении базы данных. Код ошибки: {result}")
            
    except Exception as e:
        logger.error(f"Неожиданная ошибка при восстановлении: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        if len(sys.argv) == 1:
            # Создание резервной копии
            create_backup()
        elif len(sys.argv) == 3 and sys.argv[1] == "restore":
            # Восстановление из резервной копии
            restore_backup(sys.argv[2])
        else:
            print("Использование:")
            print("  Создание резервной копии: python backup.py")
            print("  Восстановление из копии: python backup.py restore <путь_к_файлу_копии>")
    except Exception as e:
        logger.error(f"Ошибка: {str(e)}")
        sys.exit(1) 