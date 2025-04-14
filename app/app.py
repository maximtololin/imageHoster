import os
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from loguru import logger
import shutil
import sys

# Конфигурация
UPLOAD_DIR = "images"
LOG_DIR = "logs"
BACKUP_DIR = "backups"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}

# Создание директорий
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# Настройка логирования
LOG_FILE = os.path.join(LOG_DIR, "app.log")
logger.remove()  # Удаляем все существующие обработчики
logger.add(
    LOG_FILE,
    format="[{time:YYYY-MM-DD HH:mm:ss}] {level}: {message}",
    level="INFO",
    rotation="10 MB",  # Ротация логов при достижении 10MB
    retention="1 week"  # Хранение логов в течение недели
)
logger.add(
    sys.stderr,  # Также выводим логи в консоль
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# Модели Pydantic
class ImageResponse(BaseModel):
    id: int
    filename: str
    original_name: str
    size: int
    upload_time: datetime
    file_type: str

class ImageListResponse(BaseModel):
    images: List[ImageResponse]
    total: int
    page: int
    per_page: int

# Инициализация FastAPI
app = FastAPI(title="Image Hosting Service")

# Инициализация шаблонов
templates = Jinja2Templates(directory="templates")

# Подключение к базе данных
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "images_db"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            host=os.getenv("POSTGRES_HOST", "db"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        raise HTTPException(status_code=500, detail="Ошибка подключения к базе данных")

def init_db():
    """Инициализация базы данных"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS images (
                    id SERIAL PRIMARY KEY,
                    filename TEXT NOT NULL,
                    original_name TEXT NOT NULL,
                    size INTEGER NOT NULL,
                    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    file_type TEXT NOT NULL
                );
            """)
            conn.commit()
            logger.info("Таблица images успешно создана или уже существует")
    except Exception as e:
        error_msg = f"Ошибка при инициализации базы данных: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    finally:
        if 'conn' in locals():
            conn.close()

# Инициализация базы данных при старте приложения
@app.on_event("startup")
async def startup_event():
    logger.info("Инициализация приложения...")
    init_db()
    logger.info("Приложение успешно инициализировано")

# Маршруты
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Проверка размера файла
        if file.size > MAX_FILE_SIZE:
            error_msg = f"Файл слишком большой: {file.size} байт (максимум {MAX_FILE_SIZE} байт)"
            logger.error(error_msg)
            raise HTTPException(status_code=413, detail=error_msg)

        # Проверка расширения файла
        _, ext = os.path.splitext(file.filename)
        ext = ext.lower()
        if ext not in ALLOWED_EXTENSIONS:
            error_msg = f"Неподдерживаемый формат файла: {ext}"
            logger.error(error_msg)
            raise HTTPException(status_code=415, detail=error_msg)

        # Генерация уникального имени файла
        image_id = str(uuid.uuid4())
        filename = f"{image_id}{ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        # Сохранение файла
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            logger.info(f"Файл успешно сохранен: {filename}")
        except Exception as e:
            error_msg = f"Ошибка сохранения файла {filename}: {str(e)}"
            logger.error(error_msg)
            raise HTTPException(status_code=500, detail=error_msg)

        # Сохранение метаданных в базу данных
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO images (filename, original_name, size, file_type)
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (filename, file.filename, file.size, ext[1:])
                )
                image_id = cursor.fetchone()["id"]
                conn.commit()
                logger.info(f"Метаданные файла {filename} успешно сохранены в базу данных")
        except Exception as e:
            error_msg = f"Ошибка сохранения метаданных файла {filename}: {str(e)}"
            logger.error(error_msg)
            os.remove(file_path)
            raise HTTPException(status_code=500, detail=error_msg)
        finally:
            if 'conn' in locals():
                conn.close()

        return JSONResponse(
            status_code=201,
            content={
                "status": "success",
                "id": image_id,
                "file_url": f"/images/{filename}"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        error_msg = f"Неожиданная ошибка при загрузке файла: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/images-list", response_class=HTMLResponse)
async def get_images_list(
    request: Request,
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100)
):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Получение общего количества изображений
            cursor.execute("SELECT COUNT(*) FROM images")
            total = cursor.fetchone()["count"]

            # Получение изображений для текущей страницы
            offset = (page - 1) * per_page
            cursor.execute(
                """
                SELECT * FROM images
                ORDER BY upload_time DESC
                LIMIT %s OFFSET %s
                """,
                (per_page, offset)
            )
            images = cursor.fetchall()
    except Exception as e:
        logger.error(f"Ошибка получения списка изображений: {e}")
        raise HTTPException(status_code=500, detail="Ошибка получения списка изображений")
    finally:
        conn.close()

    return templates.TemplateResponse(
        "images_list.html",
        {
            "request": request,
            "images": images,
            "total": total,
            "page": page,
            "per_page": per_page
        }
    )

@app.delete("/delete/{image_id}")
async def delete_image(image_id: int):
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Получение информации о файле
            cursor.execute(
                "SELECT filename FROM images WHERE id = %s",
                (image_id,)
            )
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Изображение не найдено")

            filename = result["filename"]
            file_path = os.path.join(UPLOAD_DIR, filename)

            # Удаление записи из базы данных
            cursor.execute(
                "DELETE FROM images WHERE id = %s",
                (image_id,)
            )
            conn.commit()

            # Удаление файла
            if os.path.exists(file_path):
                os.remove(file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка удаления изображения: {e}")
        raise HTTPException(status_code=500, detail="Ошибка удаления изображения")
    finally:
        conn.close()

    return JSONResponse(
        status_code=200,
        content={"status": "success", "message": "Изображение успешно удалено"}
    )

# Монтирование статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/images", StaticFiles(directory=UPLOAD_DIR), name="images")