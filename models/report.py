# Модель для формирования отчётов (запросы к базе данных)

from db.config import get_connection

class Report:
    """Класс для получения данных для отчётов"""
    
    @staticmethod
    def get_income_expense(user_id, date_from, date_to):
        """
        Получить сумму доходов и расходов за период
        Возвращает: (total_income, income_count, total_expense, expense_count)
        """
        conn = get_connection()
        if not conn:
            return 0, 0, 0, 0
        
        try:
            cursor = conn.cursor()
            
            # Доходы
            cursor.execute("""
                SELECT SUM(o.amount), COUNT(*)
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                WHERE o.user_id = %s AND c.type = 'income'
                AND o.date BETWEEN %s AND %s
            """, (user_id, date_from, date_to))
            income_result = cursor.fetchone()
            total_income = income_result[0] or 0
            income_count = income_result[1] or 0
            
            # Расходы
            cursor.execute("""
                SELECT SUM(o.amount), COUNT(*)
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                WHERE o.user_id = %s AND c.type = 'expense'
                AND o.date BETWEEN %s AND %s
            """, (user_id, date_from, date_to))
            expense_result = cursor.fetchone()
            total_expense = expense_result[0] or 0
            expense_count = expense_result[1] or 0
            
            return total_income, income_count, total_expense, expense_count
            
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return 0, 0, 0, 0
        finally:
            conn.close()
    
    @staticmethod
    def get_expense_by_category(user_id, date_from, date_to):
        """
        Получить расходы по категориям за период
        Возвращает: список (название_категории, сумма, количество_операций)
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.name, SUM(o.amount), COUNT(o.id)
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                WHERE o.user_id = %s AND c.type = 'expense'
                AND o.date BETWEEN %s AND %s
                GROUP BY c.id, c.name
                ORDER BY SUM(o.amount) DESC
            """, (user_id, date_from, date_to))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_income_by_category(user_id, date_from, date_to):
        """
        Получить доходы по категориям за период
        Возвращает: список (название_категории, сумма, количество_операций)
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT c.name, SUM(o.amount), COUNT(o.id)
                FROM operations o
                JOIN categories c ON o.category_id = c.id
                WHERE o.user_id = %s AND c.type = 'income'
                AND o.date BETWEEN %s AND %s
                GROUP BY c.id, c.name
                ORDER BY SUM(o.amount) DESC
            """, (user_id, date_from, date_to))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_account_balances(user_id):
        """
        Получить балансы по счетам пользователя
        Возвращает: список (id, название, баланс, код_валюты, символ)
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
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_budget_execution(user_id, month_date, date_from, date_to):
        """
        Получить данные о выполнении бюджета
        month_date: дата месяца для бюджетных лимитов (например, '2025-02-01')
        date_from, date_to: период для операций
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.name,
                    COALESCE(bl.limit_amount, 0) as budget_limit,
                    COALESCE(SUM(o.amount), 0) as actual_spent,
                    COALESCE(bl.limit_amount, 0) - COALESCE(SUM(o.amount), 0) as remaining
                FROM categories c
                LEFT JOIN budget_limits bl ON c.id = bl.category_id AND bl.user_id = %s AND bl.month = %s
                LEFT JOIN operations o ON c.id = o.category_id AND o.user_id = %s 
                    AND o.date BETWEEN %s AND %s AND c.type = 'expense'
                WHERE c.user_id = %s AND c.type = 'expense'
                GROUP BY c.id, c.name, bl.limit_amount
                HAVING budget_limit > 0 OR actual_spent > 0
                ORDER BY actual_spent DESC
            """, (user_id, month_date, user_id, date_from, date_to, user_id))
            
            return cursor.fetchall()
            
        except Exception as e:
            print(f"Ошибка получения данных: {e}")
            return []
        finally:
            conn.close()