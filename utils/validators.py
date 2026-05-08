# Утилиты для валидации пользовательского ввода

def get_positive_float(prompt, allow_empty=False):
    """
    Запрашивает у пользователя положительное число.
    
    Аргументы:
        prompt (str): Текст запроса
        allow_empty (bool): Если True, пустой ввод возвращает None
    
    Возвращает:
        float: Положительное число
        None: Если allow_empty=True и пользователь ничего не ввёл
    
    Примеры:
        >>> get_positive_float("Введите сумму: ")
        Введите сумму: 500
        500.0
        
        >>> get_positive_float("Введите сумму: ")
        Введите сумму: -10
        ✗ Сумма должна быть больше 0!
        Введите сумму: сто
        ✗ Ошибка! Введите число (например, 500 или 1250.50)
        Введите сумму: 100
        100.0
    """
    while True:
        user_input = input(prompt).strip()
        
        # Пустой ввод
        if allow_empty and user_input == "":
            return None
        
        try:
            value = float(user_input)
            if value > 0:
                return value
            else:
                print("✗ Сумма должна быть больше 0!")
        except ValueError:
            print("✗ Ошибка! Введите число (например, 500 или 1250.50)")


def get_positive_int(prompt, allow_empty=False):
    """
    Запрашивает у пользователя положительное целое число.
    
    Аргументы:
        prompt (str): Текст запроса
        allow_empty (bool): Если True, пустой ввод возвращает None
    
    Возвращает:
        int: Положительное целое число
        None: Если allow_empty=True и пользователь ничего не ввёл
    """
    while True:
        user_input = input(prompt).strip()
        
        if allow_empty and user_input == "":
            return None
        
        try:
            value = int(user_input)
            if value > 0:
                return value
            else:
                print("✗ Число должно быть больше 0!")
        except ValueError:
            print("✗ Ошибка! Введите целое число.")


def get_date_input(prompt, allow_empty=False):
    """
    Запрашивает у пользователя дату в формате ГГГГ-ММ-ДД.
    
    Аргументы:
        prompt (str): Текст запроса
        allow_empty (bool): Если True, пустой ввод возвращает None
    
    Возвращает:
        str: Дата в формате ГГГГ-ММ-ДД
        None: Если allow_empty=True и пользователь ничего не ввёл
    """
    from datetime import datetime
    
    while True:
        user_input = input(prompt).strip()
        
        if allow_empty and user_input == "":
            return None
        
        # Проверяем формат даты
        try:
            datetime.strptime(user_input, "%Y-%m-%d")
            return user_input
        except ValueError:
            print("✗ Неверный формат даты! Используйте ГГГГ-ММ-ДД (например, 2025-12-31)")


def confirm_action(prompt):
    """
    Запрашивает подтверждение действия.
    
    Аргументы:
        prompt (str): Текст запроса (например, "Вы уверены? (да/нет): ")
    
    Возвращает:
        bool: True если пользователь ввёл "да", False если "нет"
    """
    result = input(prompt).strip().lower()
    return result == "да" or result == "yes" or result == "y" or result == "д"