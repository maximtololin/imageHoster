# Резервное копирование

## Автоматическое

Расписание:
- Ежедневно: 00:00
- Еженедельно: воскресенье 12:00
- Ежемесячно: 1-е число 03:00

## Команды

### Основные операции
```bash
# Создать бэкап
docker compose exec app python backup.py

# Список бэкапов
docker compose exec app ls -l /app/backups

# Восстановить из бэкапа
docker compose exec app python backup.py restore /app/backups/backup_YYYY-MM-DD_HHMMSS.sql
```

### Мониторинг
```bash
# Логи ручных операций
docker compose exec app cat /app/logs/backup.log

# Логи автоматических операций
docker compose exec app cat /app/logs/scheduled_backup.log

# Проверка размера бэкапов
docker compose exec app du -h /app/backups
```

### Обслуживание
```bash
# Удалить старые копии (>30 дней)
docker compose exec app find /app/backups -name "backup_*.sql" -type f -mtime +30 -delete

# Скопировать бэкап локально
docker compose cp app:/app/backups/backup_YYYY-MM-DD_HHMMSS.sql ./local_backup.sql
``` 