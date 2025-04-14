# 🖼️ Image Hoster

Сервис для загрузки и хранения изображений с веб-интерфейсом.

## 🚀 Возможности

- Загрузка изображений (JPG, PNG, GIF до 5MB)
- Просмотр списка загруженных файлов
- Получение прямых ссылок на изображения
- Автоматическое резервное копирование
- Пагинация и сортировка списка
- Удаление изображений

## 📦 Требования

- Docker
- Docker Compose

## 🛠️ Установка и запуск

```bash
# Клонирование репозитория
git clone <repository-url>
cd imageHoster

# Запуск сервиса
docker compose up --build -d
```

Сервис будет доступен по адресу: http://localhost:8080

## 📝 Основные команды

### Управление сервисом

```bash
# Запуск
docker compose up -d

# Остановка
docker compose down

# Просмотр логов
docker compose logs -f
```

### Резервное копирование

```bash
# Создать бэкап вручную
docker compose exec app python backup.py

# Просмотр списка бэкапов
docker compose exec app ls -l /app/backups

# Восстановление из бэкапа
docker compose exec app python backup.py restore /app/backups/backup_YYYY-MM-DD_HHMMSS.sql
```

### Мониторинг

```bash
# Проверка статуса базы данных
docker compose exec db pg_isready -U postgres

# Просмотр логов приложения
docker compose exec app cat /app/logs/app.log

# Просмотр логов бэкапов
docker compose exec app cat /app/logs/backup.log
```

## 📁 Структура проекта

```
imageHoster/
├── app/
│   ├── static/          # CSS и JavaScript
│   ├── templates/       # HTML шаблоны
│   ├── app.py          # Основной код приложения
│   ├── backup.py       # Скрипты резервного копирования
│   └── init.sql        # Инициализация базы данных
├── images/             # Загруженные изображения
├── logs/              # Логи приложения
└── backups/           # Резервные копии
```

## 🔄 Автоматическое резервное копирование

Система автоматически создает резервные копии:
- Ежедневно в 00:00
- Еженедельно (воскресенье, 12:00)
- Ежемесячно (1-е число, 03:00)

## 🌐 API Endpoints

- `GET /` - Главная страница
- `POST /upload` - Загрузка изображения
- `GET /images-list` - Список загруженных изображений
- `GET /images/<filename>` - Просмотр изображения
- `DELETE /delete/<id>` - Удаление изображения

## 📊 Технические детали

- Backend: FastAPI
- База данных: PostgreSQL
- Веб-сервер: Nginx
- Логирование: loguru
- Контейнеризация: Docker

## 🔒 Безопасность

- Ограничение размера файлов: 5MB
- Поддерживаемые форматы: JPG, PNG, GIF
- Валидация типов файлов
- Автоматическое резервное копирование

