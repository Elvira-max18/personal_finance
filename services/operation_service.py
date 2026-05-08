# Бизнес-логика для работы с операциями

from models.operation import Operation
from models.category import Category
from models.account import Account
from datetime import datetime
from utils.validators import get_positive_float, get_date_input, confirm_action

def get_category_type_name(cat_type):
    """Преобразует тип категории в русское название"""
    return "Доход" if cat_type == "income" else "Расход"

def show_operations(user_id, categories, accounts):
    """Показать все операции пользователя"""
    print("\n--- ФИЛЬТРАЦИЯ ОПЕРАЦИЙ ---")
    
    date_from = input("Дата от (ГГГГ-ММ-ДД, Enter - без ограничения): ").strip()
    date_to = input("Дата до (ГГГГ-ММ-ДД, Enter - без ограничения): ").strip()
    
    # Показываем категории для фильтра
    print("\nДоступные категории:")
    print("0. Все категории")
    for cat in categories:
        cat_id, name, cat_type = cat
        print(f"{cat_id}. {name} ({get_category_type_name(cat_type)})")
    
    try:
        cat_filter = int(input("\nВыберите категорию для фильтра (0 - все): ").strip())
        if cat_filter == 0:
            cat_filter = None
    except ValueError:
        cat_filter = None
    
    operations = Operation.get_all(user_id, date_from if date_from else None, 
                                   date_to if date_to else None, cat_filter)
    
    if not operations:
        print("\n✗ Операции не найдены за выбранный период")
        return
    
    print("\n" + "=" * 80)
    print("                     ВАШИ ОПЕРАЦИИ")
    print("=" * 80)
    print(f"{'ID':<5} {'Дата':<12} {'Тип':<8} {'Сумма':<12} {'Категория':<20} {'Счёт':<15}")
    print("-" * 80)
    
    total_income = 0
    total_expense = 0
    
    for op in operations:
        op_id, date, amount, description, cat_name, cat_type, acc_name = op
        type_rus = get_category_type_name(cat_type)
        amount_str = f"{amount:>10.2f} ₽"
        
        if cat_type == 'income':
            total_income += amount
        else:
            total_expense += amount
        
        print(f"{op_id:<5} {str(date):<12} {type_rus:<8} {amount_str:<12} {cat_name:<20} {acc_name:<15}")
    
    print("-" * 80)
    print(f"{'ИТОГО ДОХОДЫ:':<30} {total_income:>15.2f} ₽")
    print(f"{'ИТОГО РАСХОДЫ:':<30} {total_expense:>15.2f} ₽")
    print(f"{'БАЛАНС:':<30} {total_income - total_expense:>15.2f} ₽")
    print("=" * 80)

def add_operation_flow(user_id):
    """Поток добавления операции (Модификация 2: улучшенная проверка ввода)"""
    print("\n--- ДОБАВЛЕНИЕ ОПЕРАЦИИ ---")
    
    # Выбор типа операции
    print("\nТип операции:")
    print("1. Доход")
    print("2. Расход")
    op_type = input("Выберите (1-2): ").strip()
    
    if op_type == "1":
        category_type_filter = "income"
        type_rus = "доход"
    elif op_type == "2":
        category_type_filter = "expense"
        type_rus = "расход"
    else:
        print("✗ Неверный выбор!")
        return
    
    # Сумма (Модификация 2: защита от дурака)
    amount = get_positive_float(f"\nСумма {type_rus}а: ")
    if amount is None:
        return
    
    # Дата (Модификация 2: проверка формата)
    date = get_date_input("Дата (ГГГГ-ММ-ДД, Enter - сегодня): ", allow_empty=True)
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Категория
    categories = Category.get_by_type(user_id, category_type_filter)
    if not categories:
        print(f"\n✗ У вас нет категорий для {type_rus}а. Сначала создайте категорию в пункте 2.")
        return
    
    print(f"\nДоступные категории для {type_rus}а:")
    for cat in categories:
        cat_id, name = cat
        print(f"  {cat_id}. {name}")
    
    try:
        cat_id = int(input("Выберите категорию по ID: ").strip())
        # Проверяем, что категория существует
        valid = False
        for cat in categories:
            if cat[0] == cat_id:
                valid = True
                break
        if not valid:
            print("✗ Неверная категория!")
            return
    except ValueError:
        print("✗ Неверный ID!")
        return
    
    # Счёт
    accounts = Account.get_all(user_id)
    if not accounts:
        print("\n✗ У вас нет счетов. Сначала создайте счёт в пункте 3.")
        return
    
    print("\nДоступные счета:")
    for acc in accounts:
        acc_id, name, balance, currency_code, symbol = acc
        print(f"  {acc_id}. {name} (баланс: {balance:.2f} {symbol})")
    
    try:
        acc_id = int(input("Выберите счёт по ID: ").strip())
        valid = False
        for acc in accounts:
            if acc[0] == acc_id:
                valid = True
                break
        if not valid:
            print("✗ Неверный счёт!")
            return
    except ValueError:
        print("✗ Неверный ID!")
        return
    
    # Комментарий
    description = input("Комментарий (можно пропустить Enter): ").strip()
    
    # =============================================
    # ПРОВЕРКА БЮДЖЕТА (только для расходов)
    # =============================================
    if op_type == "2":  # Расход
        from models.budget import Budget
        budget_ok, budget_msg, is_over, remaining = Budget.check_budget(user_id, cat_id, amount, date)
        
        if is_over:
            print(f"\n⚠ {budget_msg}")
            # Модификация 2: используем функцию confirm_action
            if not confirm_action("Вы всё равно хотите добавить операцию? (да/нет): "):
                print("✗ Операция отменена")
                return
        else:
            if budget_ok and "В рамках бюджета" in budget_msg:
                print(f"\n✓ {budget_msg}")
    
    # Сохраняем операцию
    success, message = Operation.add(user_id, acc_id, cat_id, amount, date, description)
    print(f"\n{'✓' if success else '✗'} {message}")

def delete_operation_flow(user_id):
    """Поток удаления операции"""
    # Сначала показываем последние операции
    operations = Operation.get_all(user_id, None, None, None)
    
    if not operations:
        print("\n✗ Нет операций для удаления")
        return
    
    print("\n" + "=" * 70)
    print("                   ПОСЛЕДНИЕ ОПЕРАЦИИ")
    print("=" * 70)
    print(f"{'ID':<5} {'Дата':<12} {'Сумма':<12} {'Категория':<20}")
    print("-" * 70)
    
    for op in operations[:10]:  # Показываем последние 10
        op_id, date, amount, description, cat_name, cat_type, acc_name = op
        print(f"{op_id:<5} {str(date):<12} {amount:>10.2f} ₽ {cat_name:<20}")
    
    print("-" * 70)
    
    try:
        op_id = int(input("\nВведите ID операции для удаления: ").strip())
        confirm = input(f"Вы уверены, что хотите удалить операцию {op_id}? (да/нет): ").strip().lower()
        
        if confirm == "да":
            success, message = Operation.delete(op_id, user_id)
            print(f"{'✓' if success else '✗'} {message}")
        else:
            print("✗ Удаление отменено")
    except ValueError:
        print("✗ Неверный ID!")


# =============================================
# МОДИФИКАЦИЯ 1: РЕДАКТИРОВАНИЕ ОПЕРАЦИИ
# =============================================

def edit_operation_flow(user_id):
    """Поток редактирования операции (Модификация 2: улучшенная проверка ввода)"""
    print("\n--- РЕДАКТИРОВАНИЕ ОПЕРАЦИИ ---")
    
    # Сначала показываем последние операции
    operations = Operation.get_all(user_id, None, None, None)
    
    if not operations:
        print("\n✗ Нет операций для редактирования")
        return
    
    print("\n" + "=" * 70)
    print("                   ВАШИ ОПЕРАЦИИ")
    print("=" * 70)
    print(f"{'ID':<5} {'Дата':<12} {'Сумма':<12} {'Категория':<20} {'Счёт':<15}")
    print("-" * 70)
    
    for op in operations[:10]:  # Показываем последние 10
        op_id, date, amount, description, cat_name, cat_type, acc_name = op
        print(f"{op_id:<5} {str(date):<12} {amount:>10.2f} ₽ {cat_name:<20} {acc_name:<15}")
    
    print("-" * 70)
    
    # Выбираем операцию
    try:
        op_id = int(input("\nВведите ID операции для редактирования: ").strip())
    except ValueError:
        print("✗ Неверный ID!")
        return
    
    # Находим выбранную операцию
    selected_op = None
    for op in operations:
        if op[0] == op_id:
            selected_op = op
            break
    
    if not selected_op:
        print("✗ Операция не найдена!")
        return
    
    op_id, old_date, old_amount, old_description, old_cat_name, old_cat_type, old_acc_name = selected_op
    
    print(f"\nТекущая операция:")
    print(f"  Сумма: {old_amount:.2f} ₽")
    print(f"  Категория: {old_cat_name}")
    print(f"  Счёт: {old_acc_name}")
    print(f"  Дата: {old_date}")
    
    # Что будем менять?
    print("\nЧто вы хотите изменить?")
    print("1. Сумму")
    print("2. Категорию")
    print("3. Всё (сумму и категорию)")
    print("4. Отмена")
    
    change_choice = input("Выберите (1-4): ").strip()
    
    if change_choice == "4":
        print("✗ Редактирование отменено")
        return
    
    new_amount = old_amount
    new_cat_id = None
    
    # Определяем ID старой категории
    old_cat_id = None
    categories = Category.get_by_type(user_id, old_cat_type)
    for cat in categories:
        if cat[1] == old_cat_name:
            old_cat_id = cat[0]
            break
    
    # Меняем сумму (Модификация 2: с валидацией)
    if change_choice in ["1", "3"]:
        new_amount_result = get_positive_float(f"Введите новую сумму (Enter - {old_amount:.2f}): ", allow_empty=True)
        if new_amount_result is None:
            new_amount = old_amount
        else:
            new_amount = new_amount_result
    
    # Меняем категорию
    if change_choice in ["2", "3"]:
        # Показываем категории того же типа
        categories = Category.get_by_type(user_id, old_cat_type)
        if not categories:
            print(f"\n✗ Нет доступных категорий для этого типа операций")
            new_cat_id = old_cat_id
        else:
            print(f"\nДоступные категории ({'доход' if old_cat_type == 'income' else 'расход'}):")
            for cat in categories:
                cat_id, name = cat
                print(f"  {cat_id}. {name}")
            
            try:
                new_cat_id = int(input("Выберите новую категорию по ID: ").strip())
                valid = False
                for cat in categories:
                    if cat[0] == new_cat_id:
                        valid = True
                        break
                if not valid:
                    print("✗ Неверная категория! Оставляем старую.")
                    new_cat_id = old_cat_id
            except ValueError:
                print("✗ Неверный ID! Оставляем старую категорию.")
                new_cat_id = old_cat_id
    else:
        new_cat_id = old_cat_id
    
    # Подтверждение
    print("\n--- ПОДТВЕРДИТЕ ИЗМЕНЕНИЯ ---")
    print(f"Новая сумма: {new_amount:.2f} ₽ (было: {old_amount:.2f})")
    if new_cat_id != old_cat_id:
        # Получаем имя новой категории
        new_cat_name = "неизвестно"
        for cat in categories:
            if cat[0] == new_cat_id:
                new_cat_name = cat[1]
                break
        print(f"Новая категория: {new_cat_name} (было: {old_cat_name})")
    
    if not confirm_action("\nСохранить изменения? (да/нет): "):
        print("✗ Редактирование отменено")
        return
    
    # Сохраняем изменения
    success, message = Operation.update_operation(op_id, new_amount, new_cat_id)
    print(f"\n{'✓' if success else '✗'} {message}")


def run_operations_menu(user_id):
    """Запуск меню операций"""
    # Получаем списки для фильтров
    categories = Category.get_all(user_id)
    accounts = Account.get_all(user_id)
    
    while True:
        print("\n" + "=" * 50)
        print("             МОИ ОПЕРАЦИИ")
        print("=" * 50)
        print("1. Показать все операции")
        print("2. Добавить операцию")
        print("3. Удалить операцию")
        print("4. Редактировать операцию")
        print("5. Назад")
        print("-" * 50)
        
        choice = input("Выберите действие (1-5): ").strip()
        
        if choice == "1":
            show_operations(user_id, categories, accounts)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "2":
            add_operation_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "3":
            delete_operation_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "4":
            edit_operation_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "5":
            break
        else:
            print("✗ Неверный выбор!")