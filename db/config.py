# Конфигурация подключения к базе данных MySQL

import mysql.connector
from mysql.connector import Error

# Параметры подключения 
DB_CONFIG = {
    'host': 'localhost',         
    'user': 'root',             
    'password': '88131398486852292007',            
    'database': 'finance_db',   
    'charset': 'utf8mb4'        
}

def get_connection():
    """
    Создаёт и возвращает соединение с базой данных.
    Если подключение не удалось - выводит ошибку и возвращает None
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("✓ Подключение к базе данных успешно установлено!")
        return connection
    except Error as e:
        print(f"✗ Ошибка подключения к БД: {e}")
        return None

def test_connection():
    """
    Тестовая функция для проверки подключения
    """
    conn = get_connection()
    if conn:
        print("Подключение работает!")
        conn.close()
        return True
    else:
        print("Подключение не удалось. Проверьте параметры в DB_CONFIG.")
        return False

# Если запускаем этот файл напрямую - выполняем тест
if __name__ == "__main__":
    test_connection()