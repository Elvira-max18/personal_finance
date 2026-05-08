# Модель для работы с финансовыми операциями (доходы/расходы)

from db.config import get_connection
from datetime import datetime

class Operation:
    """Класс для работы с операциями"""
    
    @staticmethod
    def add(user_id, account_id, category_id, amount, date, description=""):
        """
        Добавить новую операцию (доход или расход)
        """
        if amount <= 0:
            return False, "Сумма должна быть больше 0"
        
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Добавляем операцию
            cursor.execute("""
                INSERT INTO operations (user_id, account_id, category_id, amount, date, description)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (user_id, account_id, category_id, amount, date, description))
            
            # Обновляем баланс счёта
            # Для дохода - прибавляем, для расхода - вычитаем
            # Сначала узнаем тип категории
            cursor.execute("""
                SELECT type FROM categories WHERE id = %s AND user_id = %s
            """, (category_id, user_id))
            cat_result = cursor.fetchone()
            
            if cat_result:
                cat_type = cat_result[0]
                if cat_type == 'income':
                    # Доход: увеличиваем баланс
                    cursor.execute("""
                        UPDATE accounts SET balance = balance + %s
                        WHERE id = %s AND user_id = %s
                    """, (amount, account_id, user_id))
                else:
                    # Расход: уменьшаем баланс
                    cursor.execute("""
                        UPDATE accounts SET balance = balance - %s
                        WHERE id = %s AND user_id = %s
                    """, (amount, account_id, user_id))
            
            conn.commit()
            return True, "Операция успешно добавлена"
            
        except Exception as e:
            conn.rollback()
            return False, f"Ошибка при добавлении: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def get_all(user_id, date_from=None, date_to=None, category_id=None):
        """
        Получить все операции пользователя с фильтрацией
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT o.id, o.date, o.amount, o.description,
                       c.name as category_name, c.type as category_type,
                       a.name as account_name
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                JOIN accounts a ON o.account_id = a.id
                WHERE o.user_id = %s
            """
            params = [user_id]
            
            if date_from:
                query += " AND o.date >= %s"
                params.append(date_from)
            if date_to:
                query += " AND o.date <= %s"
                params.append(date_to)
            if category_id:
                query += " AND o.category_id = %s"
                params.append(category_id)
            
            query += " ORDER BY o.date DESC, o.id DESC"
            
            cursor.execute(query, params)
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Ошибка получения операций: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def delete(operation_id, user_id):
        """
        Удалить операцию и восстановить баланс счёта
        """
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Сначала получаем информацию об операции
            cursor.execute("""
                SELECT o.account_id, o.amount, c.type
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                WHERE o.id = %s AND o.user_id = %s
            """, (operation_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return False, "Операция не найдена"
            
            account_id, amount, cat_type = result
            
            # Восстанавливаем баланс счёта
            if cat_type == 'income':
                # Доход был: вычитаем обратно
                cursor.execute("""
                    UPDATE accounts SET balance = balance - %s
                    WHERE id = %s AND user_id = %s
                """, (amount, account_id, user_id))
            else:
                # Расход был: прибавляем обратно
                cursor.execute("""
                    UPDATE accounts SET balance = balance + %s
                    WHERE id = %s AND user_id = %s
                """, (amount, account_id, user_id))
            
            # Удаляем операцию
            cursor.execute("DELETE FROM operations WHERE id = %s AND user_id = %s", (operation_id, user_id))
            
            conn.commit()
            return True, "Операция удалена"
            
        except Exception as e:
            conn.rollback()
            return False, f"Ошибка при удалении: {e}"
        finally:
            conn.close()
    
    # =============================================
    # МОДИФИКАЦИЯ 1: ОБНОВЛЕНИЕ ОПЕРАЦИИ
    # =============================================
    
    @staticmethod
    def update_operation(operation_id, new_amount, new_category_id):
        """
        Обновить сумму и категорию операции с корректировкой баланса счёта
        """
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # 1. Получаем текущую информацию об операции
            cursor.execute("""
                SELECT o.account_id, o.amount, c.type, o.user_id
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                WHERE o.id = %s
            """, (operation_id,))
            
            result = cursor.fetchone()
            if not result:
                return False, "Операция не найдена"
            
            account_id, old_amount, old_cat_type, user_id = result
            
            # 2. Получаем тип новой категории
            cursor.execute("""
                SELECT type FROM categories WHERE id = %s AND user_id = %s
            """, (new_category_id, user_id))
            
            cat_result = cursor.fetchone()
            if not cat_result:
                return False, "Новая категория не найдена"
            
            new_cat_type = cat_result[0]
            
            # 3. Корректируем баланс счёта
            # Отменяем влияние старой операции
            if old_cat_type == 'income':
                # Старый доход: вычитаем из баланса
                cursor.execute("""
                    UPDATE accounts SET balance = balance - %s
                    WHERE id = %s AND user_id = %s
                """, (old_amount, account_id, user_id))
            else:
                # Старый расход: прибавляем к балансу
                cursor.execute("""
                    UPDATE accounts SET balance = balance + %s
                    WHERE id = %s AND user_id = %s
                """, (old_amount, account_id, user_id))
            
            # 4. Применяем влияние новой операции
            if new_cat_type == 'income':
                # Новый доход: прибавляем к балансу
                cursor.execute("""
                    UPDATE accounts SET balance = balance + %s
                    WHERE id = %s AND user_id = %s
                """, (new_amount, account_id, user_id))
            else:
                # Новый расход: вычитаем из баланса
                cursor.execute("""
                    UPDATE accounts SET balance = balance - %s
                    WHERE id = %s AND user_id = %s
                """, (new_amount, account_id, user_id))
            
            # 5. Обновляем операцию
            cursor.execute("""
                UPDATE operations 
                SET amount = %s, category_id = %s
                WHERE id = %s AND user_id = %s
            """, (new_amount, new_category_id, operation_id, user_id))
            
            conn.commit()
            return True, "Операция успешно обновлена"
            
        except Exception as e:
            conn.rollback()
            return False, f"Ошибка при обновлении: {e}"
        finally:
            conn.close()