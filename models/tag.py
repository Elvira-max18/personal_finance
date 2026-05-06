# Модель для работы с метками (тегами)

from db.config import get_connection

class Tag:
    """Класс для работы с метками пользователя"""
    
    @staticmethod
    def get_all(user_id):
        """
        Получить все метки пользователя
        Возвращает список кортежей: (id, name)
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name FROM tags 
                WHERE user_id = %s 
                ORDER BY name
            """, (user_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения меток: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def add(user_id, name):
        """
        Добавить новую метку
        """
        if not name or len(name.strip()) == 0:
            return False, "Название метки не может быть пустым"
        
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, есть ли уже такая метка у пользователя
            cursor.execute("""
                SELECT id FROM tags 
                WHERE user_id = %s AND name = %s
            """, (user_id, name.strip()))
            
            if cursor.fetchone():
                return False, f"Метка '{name}' уже существует"
            
            # Добавляем новую метку
            cursor.execute("""
                INSERT INTO tags (user_id, name)
                VALUES (%s, %s)
            """, (user_id, name.strip()))
            
            conn.commit()
            return True, f"Метка '{name}' успешно добавлена"
            
        except Exception as e:
            return False, f"Ошибка при добавлении: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def update(tag_id, user_id, new_name):
        """
        Обновить название метки
        """
        if not new_name or len(new_name.strip()) == 0:
            return False, "Название метки не может быть пустым"
        
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, принадлежит ли метка пользователю
            cursor.execute("""
                SELECT name FROM tags 
                WHERE id = %s AND user_id = %s
            """, (tag_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return False, "Метка не найдена"
            
            # Обновляем название
            cursor.execute("""
                UPDATE tags SET name = %s
                WHERE id = %s AND user_id = %s
            """, (new_name.strip(), tag_id, user_id))
            
            conn.commit()
            return True, f"Метка переименована в '{new_name}'"
            
        except Exception as e:
            return False, f"Ошибка при обновлении: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def delete(tag_id, user_id):
        """
        Удалить метку (автоматически удаляются связи в operation_tags)
        """
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, принадлежит ли метка пользователю
            cursor.execute("""
                SELECT name FROM tags 
                WHERE id = %s AND user_id = %s
            """, (tag_id, user_id))
            
            result = cursor.fetchone()
            if not result:
                return False, "Метка не найдена"
            
            tag_name = result[0]
            
            # Удаляем метку (связи удалятся автоматически из-за ON DELETE CASCADE)
            cursor.execute("""
                DELETE FROM tags 
                WHERE id = %s AND user_id = %s
            """, (tag_id, user_id))
            
            conn.commit()
            return True, f"Метка '{tag_name}' удалена"
            
        except Exception as e:
            return False, f"Ошибка при удалении: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def get_tags_for_operation(operation_id, user_id):
        """
        Получить все метки, привязанные к операции
        """
        conn = get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.name
                FROM tags t
                JOIN operation_tags ot ON t.id = ot.tag_id
                WHERE ot.operation_id = %s AND t.user_id = %s
            """, (operation_id, user_id))
            return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка получения меток операции: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def add_tag_to_operation(operation_id, tag_id, user_id):
        """
        Привязать метку к операции
        """
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, принадлежит ли операция пользователю
            cursor.execute("""
                SELECT id FROM operations 
                WHERE id = %s AND user_id = %s
            """, (operation_id, user_id))
            if not cursor.fetchone():
                return False, "Операция не найдена"
            
            # Проверяем, принадлежит ли метка пользователю
            cursor.execute("""
                SELECT id FROM tags 
                WHERE id = %s AND user_id = %s
            """, (tag_id, user_id))
            if not cursor.fetchone():
                return False, "Метка не найдена"
            
            # Проверяем, не привязана ли уже метка
            cursor.execute("""
                SELECT * FROM operation_tags 
                WHERE operation_id = %s AND tag_id = %s
            """, (operation_id, tag_id))
            if cursor.fetchone():
                return False, "Эта метка уже привязана к операции"
            
            # Привязываем метку
            cursor.execute("""
                INSERT INTO operation_tags (operation_id, tag_id)
                VALUES (%s, %s)
            """, (operation_id, tag_id))
            
            conn.commit()
            return True, "Метка привязана к операции"
            
        except Exception as e:
            return False, f"Ошибка при привязке метки: {e}"
        finally:
            conn.close()
    
    @staticmethod
    def remove_tag_from_operation(operation_id, tag_id, user_id):
        """
        Отвязать метку от операции
        """
        conn = get_connection()
        if not conn:
            return False, "Ошибка подключения к базе данных"
        
        try:
            cursor = conn.cursor()
            
            # Проверяем, принадлежит ли операция пользователю
            cursor.execute("""
                SELECT id FROM operations 
                WHERE id = %s AND user_id = %s
            """, (operation_id, user_id))
            if not cursor.fetchone():
                return False, "Операция не найдена"
            
            # Удаляем связь
            cursor.execute("""
                DELETE FROM operation_tags 
                WHERE operation_id = %s AND tag_id = %s
            """, (operation_id, tag_id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                return True, "Метка отвязана от операции"
            else:
                return False, "Эта метка не была привязана к операции"
            
        except Exception as e:
            return False, f"Ошибка при отвязке метки: {e}"
        finally:
            conn.close()