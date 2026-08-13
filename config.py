import os
from dotenv import load_dotenv
#Cargar las variables de entorno desde el archivo .env
load_dotenv()

class config:
    # Configuración de la base de datos
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT')
    DB_NAME = os.getenv('DB_NAME')

    # Configuración de la clave secreta
    SECRET_KEY = os.getenv('SECRET_KEY')

    #URL de conexión a la base de datos PostgreSQL
    SQLALCHEMY_DATABASE_URI = (
    f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    )
