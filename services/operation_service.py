# Бизнес-логика для работы с операциями

from models.operation import Operation
from models.category import Category
from models.account import Account
from datetime import datetime

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
    """Поток добавления операции"""
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
    
    # Сумма
    try:
        amount = float(input(f"\nСумма {type_rus}а: ").strip())
        if amount <= 0:
            print("✗ Сумма должна быть больше 0!")
            return
    except ValueError:
        print("✗ Введите число!")
        return
    
    # Дата
    date = input("Дата (ГГГГ-ММ-ДД, Enter - сегодня): ").strip()
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
            confirm = input("Вы всё равно хотите добавить операцию? (да/нет): ").strip().lower()
            if confirm != "да":
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
        print("4. Назад")
        print("-" * 50)
        
        choice = input("Выберите действие (1-4): ").strip()
        
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
            break
        else:
            print("✗ Неверный выбор!")