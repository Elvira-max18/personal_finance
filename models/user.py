# Модель для работы с пользователями

import hashlib
from db.config import get_connection

class User:
    """Класс для работы с пользователями"""
    
    @staticmethod
    def hash_password(password):
        """
        Преобразует пароль в хэш (для безопасного хранения в БД)
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def create_user(username, password, full_name="", email=""):
        """
        Создаёт нового пользователя в базе данных
        Возвращает: (success, message, user_id)
        """
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных", None
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, существует ли пользователь с таким логином
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                return False, "Пользователь с таким логином уже существует", None
            
            # Хэшируем пароль
            password_hash = User.hash_password(password)
            
            # Добавляем нового пользователя
            cursor.execute("""
                INSERT INTO users (username, password_hash, full_name, email)
                VALUES (%s, %s, %s, %s)
            """, (username, password_hash, full_name, email))
            
            conn.commit()
            user_id = cursor.lastrowid
            
            return True, "Регистрация успешно завершена", user_id
            
        except Exception as e:
            return False, f"Ошибка при регистрации: {e}", None
        finally:
            conn.close()
    
    @staticmethod
    def authenticate(username, password):
        """
        Проверяет логин и пароль пользователя
        Возвращает: (success, user_id, full_name) или (False, None, None)
        """
        conn = get_connection()
        if not conn:
            return False, None, None
        
        try:
            cursor = conn.cursor()
            
            # Хэшируем введённый пароль
            password_hash = User.hash_password(password)
            
            # Ищем пользователя с таким логином и хэшем пароля
            cursor.execute("""
                SELECT id, full_name FROM users 
                WHERE username = %s AND password_hash = %s
            """, (username, password_hash))
            
            result = cursor.fetchone()
            
            if result:
                return True, result[0], result[1]
            else:
                return False, None, None
                
        except Exception as e:
            print(f"Ошибка при входе: {e}")
            return False, None, None
        finally:
            conn.close()
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Получает информацию о пользователе по ID
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, full_name, email, created_at
                FROM users WHERE id = %s
            """, (user_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'username': result[1],
                    'full_name': result[2],
                    'email': result[3],
                    'created_at': result[4]
                }
            return None
        except Exception as e:
            print(f"Ошибка получения пользователя: {e}")
            return None
        finally:
            conn.close()