import os

# Configuración de la base de datos
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root", 
    "password": "admin",
    "database": "ventasplus"
}

DATABASE_URL = f"mysql+pymysql://{DATABASE_CONFIG['user']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# Configuración de la aplicación
APP_CONFIG = {
    "title": "VentasPlus API",
    "description": "Sistema de gestión de ventas y vendedores",
    "version": "1.0.0",
    "host": "0.0.0.0",
    "port": 8000,
    "debug": True
}

# Configuración de CORS
CORS_CONFIG = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"]
}