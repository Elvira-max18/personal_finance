# Модель для работы с бюджетными лимитами

from db.config import get_connection
from datetime import datetime
from calendar import monthrange

class Budget:
    """Класс для работы с бюджетными лимитами"""
    
    @staticmethod
    def get_all(user_id, month=None):
        """
        Получить все бюджетные лимиты пользователя за месяц
        month: дата в формате 'ГГГГ-ММ-01' (если None - текущий месяц)
        """
        if month is None:
            month = datetime.now().strftime("%Y-%m-01")
        
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT bl.id, c.name, c.id, bl.limit_amount, bl.month
                FROM budget_limits bl
                JOIN categories c ON bl.category_id = c.id
                WHERE bl.user_id = %s AND bl.month = %s
                ORDER BY c.name
            """, (user_id, month))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения бюджетов: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_by_category(user_id, category_id, month):
        """
        Получить бюджетный лимит по конкретной категории за месяц
        Возвращает float
        """
        conn = get_connection()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT limit_amount FROM budget_limits
                WHERE user_id = %s AND category_id = %s AND month = %s
            """, (user_id, category_id, month))
            result = cursor.fetchone()
            return float(result[0]) if result else None
        except Exception as e:
            print(f"Ошибка получения бюджета: {e}")
            return None
        finally:
            conn.close()
    
    @staticmethod
    def set_limit(user_id, category_id, amount, month=None):
        """
        Установить бюджетный лимит на категорию за месяц
        Если запись существует - обновляет, если нет - создаёт
        """
        if amount <= 0:
            return False, "Сумма бюджета должна быть больше 0"
        
        if month is None:
            month = datetime.now().strftime("%Y-%m-01")
        
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, существует ли уже лимит
            cursor.execute("""
                SELECT id FROM budget_limits
                WHERE user_id = %s AND category_id = %s AND month = %s
            """, (user_id, category_id, month))
            
            existing = cursor.fetchone()
            
            if existing:
                # Обновляем
                cursor.execute("""
                    UPDATE budget_limits SET limit_amount = %s
                    WHERE user_id = %s AND category_id = %s AND month = %s
                """, (amount, user_id, category_id, month))
                action = "обновлён"
            else:
                # Создаём новый
                cursor.execute("""
                    INSERT INTO budget_limits (user_id, category_id, month, limit_amount)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, category_id, month, amount))
                action = "установлен"
            
            conn.commit()
            return True, f"Бюджет {action} на сумму {amount:.2f} ₽"
            
        except Exception as e:
            return False, f"Ошибка при установке бюджета: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def delete_limit(user_id, category_id, month=None):
        """
        Удалить бюджетный лимит
        """
        if month is None:
            month = datetime.now().strftime("%Y-%m-01")
        
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM budget_limits
                WHERE user_id = %s AND category_id = %s AND month = %s
            """, (user_id, category_id, month))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Бюджет удалён"
            else:
                return False, "Бюджет для этой категории не найден"
            
        except Exception as e:
            return False, f"Ошибка при удалении: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def check_budget(user_id, category_id, amount, date):
        """
        Проверить, не превышает ли операция бюджет
        Возвращает: (success, message, is_over_budget, remaining)
        """
        # Определяем месяц из даты операции
        month = date[:7] + "-01"
        
        # Получаем лимит бюджета
        limit = Budget.get_by_category(user_id, category_id, month)
        
        if limit is None:
            # Лимит не установлен - всё ок
            return True, "Бюджет не установлен", False, None
        
        # Преобразуем лимит в float
        limit = float(limit)
        
        # Считаем уже потраченное за месяц
        conn = get_connection()
        if not conn:
            return True, "Ошибка проверки бюджета", False, None
        
        try:
            cursor = conn.cursor()
            
            # Вычисляем последний день месяца для корректного диапазона
            year = int(month[:4])
            month_num = int(month[5:7])
            last_day = monthrange(year, month_num)[1]
            month_start = month
            month_end = f"{month[:7]}-{last_day}"
            
            cursor.execute("""
                SELECT SUM(o.amount)
                FROM operations o
                WHERE o.user_id = %s AND o.category_id = %s 
                AND o.date BETWEEN %s AND %s
            """, (user_id, category_id, month_start, month_end))
            
            result = cursor.fetchone()[0]
            spent = float(result) if result else 0.0
            remaining = limit - spent
            
            if remaining < amount:
                return False, f"Превышение бюджета! Остаток: {remaining:.2f} ₽", True, remaining
            else:
                return True, f"В рамках бюджета. Остаток: {remaining - amount:.2f} ₽", False, remaining
                
        except Exception as e:
            print(f"Ошибка проверки бюджета: {e}")
            return True, "Ошибка проверки", False, None
        finally:
            conn.close()
    
    @staticmethod
    def get_spent_by_category(user_id, category_id, month):
        """
        Получить сумму потраченных средств по категории за месяц
        Возвращает float
        """
        conn = get_connection()
        if not conn:
            return 0.0
        
        try:
            cursor = conn.cursor()
            # Вычисляем последний день месяца
            year = int(month[:4])
            month_num = int(month[5:7])
            last_day = monthrange(year, month_num)[1]
            month_end = f"{month[:7]}-{last_day}"
            
            cursor.execute("""
                SELECT SUM(o.amount)
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                WHERE o.user_id = %s AND o.category_id = %s 
                AND o.date BETWEEN %s AND %s
                AND c.type = 'expense'
            """, (user_id, category_id, month, month_end))
            
            result = cursor.fetchone()[0]
            return float(result) if result else 0.0
        except Exception as e:
            print(f"Ошибка получения расходов: {e}")
            return 0.0
        finally:
            conn.close()