# 🖼️ Image Hoster

**Image Hoster** – это веб-приложение для загрузки, хранения и раздачи изображений.  
Позволяет загружать изображения, получать на них прямые ссылки и использовать в соцсетях, блогах или на сайтах.

---

## 📂 Структура проекта

- `app.py` – Основной Python-бэкенд
- `requirements.txt` – Зависимости Python
- `Dockerfile` – Dockerfile для бэкенда
- `docker-compose.yml` – Конфигурация Docker Compose
- `nginx.conf` – Конфигурация Nginx
- `images/` – Папка для загруженных изображений (Docker volume)
- `logs/` – Папка для логов (Docker volume)

---

## 🚀 Функционал

- **Загрузка изображений** – `.jpg`, `.png`, `.gif`, размером до **5MB**
- **Получение прямых ссылок** – после загрузки пользователь получает URL изображения
- **Раздача файлов через Nginx** – изображения доступны через прямые ссылки

---

## 🛠️ Запуск сервиса

Для работы потребуется **Docker** и **Docker Compose**.  
Запуск сервиса выполняется командой:

```bash
cd app
docker-compose up --build
```

## 📄 Отчет о производительности

![Вот он](/iScreen_Shoter_Google_Chrome_250217175811.jpg)




## ✅ Чек-лист тестирования

### 🔍 Проверка доступности
- ✅ [http://localhost:8080/](http://localhost:8080/) – главная страница отображается корректно

### 📤 Проверка загрузки изображений
- ✅ **Загрузка `.jpg` (1MB)** – файл успешно загружен, код `201`, получен JSON с URL
- ✅ **Загрузка `.png` (4MB)** – файл успешно загружен, код `201`, получен JSON с URL
- ✅ **Загрузка `.gif` (5MB)** – файл успешно загружен, код `201`, получен JSON с URL
- ✅ **Попытка загрузить файл > 5MB** – сервер вернул `413 Payload Too Large`
- ✅ **Попытка загрузить неподдерживаемый формат (`.exe`, `.txt`)** – сервер вернул `415 Unsupported Media Type`
- ✅ **Попытка загрузки без файла** – сервер вернул `400 Bad Request`

### 🖼️ Проверка получения изображений
- ✅ **Запрос загруженного изображения** – [http://localhost:8080/images/<имя_файла>](http://localhost:8080/images/<имя_файла>) – изображение отображается
- ✅ **Запрос несуществующего файла** – [http://localhost:8080/images/файл_не_существует.jpg](http://localhost:8080/images/файл_не_существует.jpg) – сервер вернул `404 Not Found`

### 📜 Проверка логирования
- ✅ **Логирование успешной загрузки** – в `logs/app.log` появилась запись о загрузке
- ✅ **Логирование ошибки (`415 Unsupported Media Type`)** – в `logs/app.log` зафиксирован неподдерживаемый формат
- ✅ **Логирование ошибки (`413 Payload Too Large`)** – в `logs/app.log` зафиксирована попытка загрузки большого файла


