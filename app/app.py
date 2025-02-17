import os
import uuid
import json
import mimetypes
from http.server import HTTPServer, BaseHTTPRequestHandler
from io import BytesIO
from loguru import logger
import cgi

# Настройки
UPLOAD_DIR = "images"
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
LOG_FILE = os.path.join(LOG_DIR, "server.log")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}
SERVER_ADDRESS = ('0.0.0.0', 8000)

# Создаем необходимые директории
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

# Настройка логирования
logger.add(LOG_FILE, format="[{time:YYYY-MM-DD HH:mm:ss}] {level}: {message}", level="INFO")


class ImageHostingHandler(BaseHTTPRequestHandler):
    server_version = 'Image Hosting Server/0.3'

    def __init__(self, request, client_address, server):
        self.routes = {
            '/': self.route_get_index,
            '/index.html': self.route_get_index,
            '/upload': self.route_post_upload,
        }
        super().__init__(request, client_address, server)

    def do_OPTIONS(self):
        """Обрабатывает preflight-запросы для CORS"""
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path in self.routes:
            self.routes[self.path]()
        else:
            logger.error(f'GET 404 {self.path}')
            self.send_response(404, "Not Found")
            self.end_headers()

    def route_get_index(self):
        logger.info(f'GET {self.path}')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(open('index.html', 'rb').read())

    def do_POST(self):
        if self.path == '/upload':
            self.route_post_upload()
        else:
            logger.error(f'POST 404 {self.path}')
            self.send_response(404, "Not Found")
            self.end_headers()

    def route_post_upload(self):
        logger.info(f'POST {self.path}')

        # Проверяем Content-Length
        content_length = self.headers.get('Content-Length')
        if not content_length:
            logger.error("Ошибка 411: нет заголовка Content-Length")
            self.send_response(411, "Length Required")
            self.end_headers()
            return

        content_length = int(content_length)
        if content_length > MAX_FILE_SIZE:
            logger.error("Ошибка 413: файл превышает 5MB")
            self.send_response(413, "Payload Too Large")
            self.end_headers()
            return

        # Проверяем заголовок Content-Type
        content_type = self.headers.get('Content-Type')
        if not content_type or "multipart/form-data" not in content_type:
            logger.error(f"Ошибка 415: неподдерживаемый формат файла - {content_type}")
            self.send_response(415, "Unsupported Media Type")
            self.end_headers()
            return

        # Разбираем multipart/form-data
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD': 'POST'})

        # Проверяем, есть ли файл в запросе
        if "file" not in form:
            logger.error("Ошибка 400: файл не был передан")
            self.send_response(400, "Bad Request")
            self.end_headers()
            return

        file_item = form["file"]

        # Проверяем, был ли загружен файл
        if not file_item.filename:
            logger.error("Ошибка 400: передан пустой файл")
            self.send_response(400, "Bad Request")
            self.end_headers()
            return

        # Определяем расширение файла
        _, ext = os.path.splitext(file_item.filename)
        ext = ext.lower()

        if ext not in ALLOWED_EXTENSIONS:
            logger.error(f"Ошибка 415: неподдерживаемый формат файла - {ext}")
            self.send_response(415, "Unsupported Media Type")
            self.end_headers()
            return

        # Генерируем уникальное имя файла
        image_id = uuid.uuid4()
        file_path = os.path.join(UPLOAD_DIR, f"{image_id}{ext}")

        # Сохраняем файл
        with open(file_path, 'wb') as f:
            f.write(file_item.file.read())

        logger.info(f"Изображение {image_id}{ext} загружено.")

        # Отправляем JSON-ответ с URL загруженного файла
        self.send_response(201)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response = {"status": "success", "file_url": f'http://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}/{file_path}'}
        self.wfile.write(json.dumps(response).encode('utf-8'))


def run():
    httpd = HTTPServer(SERVER_ADDRESS, ImageHostingHandler)
    logger.info(f"Сервер запущен на {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")
    print(f"Server started at http://{SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Остановка сервера по запросу пользователя.")
        print("\nShutting down server...")
        httpd.server_close()


if __name__ == "__main__":
    run()