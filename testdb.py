# test_connection.py - Script para probar la conexión
import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def test_mysql_connection():
    """Probar conexión a MySQL"""
    try:
        # Conexión directa con pymysql
        connection = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            password='admin',
            database='ventasplusdb',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"Conexión exitosa a MySQL: {version[0]}")
            
            # Mostrar tablas existentes
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print(f"Tablas encontradas: {[table[0] for table in tables]}")
            
            # Mostrar estructura de tabla vendedores si existe
            try:
                cursor.execute("DESCRIBE vendedores")
                columns = cursor.fetchall()
                print(f"Estructura tabla vendedores:")
                for col in columns:
                    print(f"   - {col[0]}: {col[1]}")
            except:
                print("Tabla vendedores no encontrada")
            
            # Mostrar estructura de tabla operaciones si existe
            try:
                cursor.execute("DESCRIBE operaciones")
                columns = cursor.fetchall()
                print(f"Estructura tabla operaciones:")
                for col in columns:
                    print(f"   - {col[0]}: {col[1]}")
            except:
                print("⚠️ Tabla operaciones no encontrada")
                
        connection.close()
        
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False
    
    return True

def test_sqlalchemy_connection():
    """Probar conexión con SQLAlchemy"""
    try:
        DATABASE_URL = "mysql+pymysql://root:admin@localhost:3306/ventasplusdb"
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT VERSION()"))
            version = result.fetchone()
            print(f"✅ SQLAlchemy conexión exitosa: {version[0]}")
            
        return True
    except Exception as e:
        print(f"Error SQLAlchemy: {e}")
        return False

if __name__ == "__main__":
    print("Probando conexión a MySQL...")
    print("=" * 50)
    
    if test_mysql_connection():
        print("\n" + "=" * 50)
        print("Probando SQLAlchemy...")
        test_sqlalchemy_connection()
    
    print("\nPruebas completadas!")