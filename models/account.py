# Модель для работы со счетами пользователя

from db.config import get_connection

class Account:
    """Класс для работы со счетами"""
    
    @staticmethod
    def get_all(user_id):
        """
        Получить все счета пользователя
        Возвращает список кортежей: (id, name, balance, currency_code)
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT a.id, a.name, a.balance, c.code, c.symbol
                FROM accounts a
                JOIN currency c ON a.currency_id = c.id
                WHERE a.user_id = %s
                ORDER BY a.id
            """, (user_id,))
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Ошибка получения счетов: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def add(user_id, name, currency_id=1):
        """
        Добавить новый счёт
        currency_id: 1 - RUB, 2 - USD, 3 - EUR
        """
        if not name or len(name.strip()) == 0:
            return False, "Название счёта не может быть пустым"
        
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, есть ли уже такой счёт у пользователя
            cursor.execute("""
                SELECT id FROM accounts 
                WHERE user_id = %s AND name = %s
            """, (user_id, name.strip()))
            
            if cursor.fetchone():
                return False, f"Счёт '{name}' уже существует"
            
            # Добавляем новый счёт
            cursor.execute("""
                INSERT INTO accounts (user_id, currency_id, name, balance)
                VALUES (%s, %s, %s, 0)
            """, (user_id, currency_id, name.strip()))
            
            conn.commit()
            return True, f"Счёт '{name}' успешно добавлен"
            
        except Exception as e:
            return False, f"Ошибка при добавлении: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def update(account_id, user_id, new_name):
        """
        Обновить название счёта
        """
        if not new_name or len(new_name.strip()) == 0:
            return False, "Название счёта не может быть пустым"
        
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, принадлежит ли счёт пользователю
            cursor.execute("""
                SELECT name FROM accounts 
                WHERE id = %s AND user_id = %s
            """, (account_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return False, "Счёт не найден"
            
            # Обновляем название
            cursor.execute("""
                UPDATE accounts SET name = %s
                WHERE id = %s AND user_id = %s
            """, (new_name.strip(), account_id, user_id))
            
            conn.commit()
            return True, f"Счёт переименован в '{new_name}'"
            
        except Exception as e:
            return False, f"Ошибка при обновлении: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def delete(account_id, user_id):
        """
        Удалить счёт (только если баланс = 0 и нет операций)
        """
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, принадлежит ли счёт пользователю
            cursor.execute("""
                SELECT name, balance FROM accounts 
                WHERE id = %s AND user_id = %s
            """, (account_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return False, "Счёт не найден"
            
            account_name, balance = result
            
            # Проверяем баланс
            if balance != 0:
                return False, f"Нельзя удалить счёт '{account_name}' с балансом {balance} ₽. Сначала потратьте или переведите деньги."
            
            # Проверяем, есть ли операции со счётом
            cursor.execute("""
                SELECT COUNT(*) FROM operations 
                WHERE account_id = %s AND user_id = %s
            """, (account_id, user_id))
            
            count = cursor.fetchone()[0]
            if count > 0:
                return False, f"Нельзя удалить счёт '{account_name}', так как есть {count} операций с ним"
            
            # Удаляем счёт
            cursor.execute("""
                DELETE FROM accounts 
                WHERE id = %s AND user_id = %s
            """, (account_id, user_id))
            
            conn.commit()
            return True, f"Счёт '{account_name}' удалён"
            
        except Exception as e:
            return False, f"Ошибка при удалении: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def get_balance(account_id, user_id):
        """
        Получить баланс конкретного счёта
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT balance, name FROM accounts 
                WHERE id = %s AND user_id = %s
            """, (account_id, user_id))
            result = cursor.fetchone()
            if result:
                return result[0]
            return None
        except Exception as e:
            print(f"Ошибка получения баланса: {e}")
            return None
        finally:
            conn.close()