# Модель для работы с категориями доходов и расходов

from db.config import get_connection

class Category:
    """Класс для работы с категориями пользователя"""
    
    @staticmethod
    def get_all(user_id):
        """
        Получить все категории пользователя
        Возвращает список кортежей: (id, name, type)
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, type FROM categories 
                WHERE user_id = %s 
                ORDER BY type, name
            """, (user_id,))
            results = cursor.fetchall()
            return results
        except Exception as e:
            print(f"Ошибка получения категорий: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def get_by_type(user_id, type_filter):
        """
        Получить категории по типу ('income' или 'expense')
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name FROM categories 
                WHERE user_id = %s AND type = %s
                ORDER BY name
            """, (user_id, type_filter))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения категорий: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def add(user_id, name, category_type):
        """
        Добавить новую категорию
        category_type: 'income' или 'expense'
        """
        if not name or len(name.strip()) == 0:
            return False, "Название категории не может быть пустым"
        
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, есть ли уже такая категория у пользователя
            cursor.execute("""
                SELECT id FROM categories 
                WHERE user_id = %s AND name = %s AND type = %s
            """, (user_id, name.strip(), category_type))
            
            if cursor.fetchone():
                return False, f"Категория '{name}' уже существует"
            
            # Добавляем новую категорию
            cursor.execute("""
                INSERT INTO categories (user_id, name, type)
                VALUES (%s, %s, %s)
            """, (user_id, name.strip(), category_type))
            
            conn.commit()
            return True, f"Категория '{name}' успешно добавлена"
            
        except Exception as e:
            return False, f"Ошибка при добавлении: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def update(category_id, user_id, new_name):
        """
        Обновить название категории
        """
        if not new_name or len(new_name.strip()) == 0:
            return False, "Название категории не может быть пустым"
        
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, принадлежит ли категория пользователю
            cursor.execute("""
                SELECT id FROM categories 
                WHERE id = %s AND user_id = %s
            """, (category_id, user_id))
            
            if not cursor.fetchone():
                return False, "Категория не найдена"
            
            # Обновляем название
            cursor.execute("""
                UPDATE categories SET name = %s
                WHERE id = %s AND user_id = %s
            """, (new_name.strip(), category_id, user_id))
            
            conn.commit()
            return True, f"Категория переименована в '{new_name}'"
            
        except Exception as e:
            return False, f"Ошибка при обновлении: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def delete(category_id, user_id):
        """
        Удалить категорию (только если нет связанных операций)
        """
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, принадлежит ли категория пользователю
            cursor.execute("""
                SELECT name FROM categories 
                WHERE id = %s AND user_id = %s
            """, (category_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return False, "Категория не найдена"
            
            category_name = result[0]
            
            # Проверяем, есть ли операции с этой категорией
            cursor.execute("""
                SELECT COUNT(*) FROM operations 
                WHERE category_id = %s AND user_id = %s
            """, (category_id, user_id))
            
            count = cursor.fetchone()[0]
            if count > 0:
                return False, f"Нельзя удалить категорию '{category_name}', так как есть {count} операций с ней"
            
            # Удаляем категорию
            cursor.execute("""
                DELETE FROM categories 
                WHERE id = %s AND user_id = %s
            """, (category_id, user_id))
            
            conn.commit()
            return True, f"Категория '{category_name}' удалена"
            
        except Exception as e:
            return False, f"Ошибка при удалении: {e}"
        finally:
            conn.close()