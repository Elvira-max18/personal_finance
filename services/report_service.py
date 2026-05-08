# Бизнес-логика для формирования отчётов

from models.report import Report
from models.category import Category
from datetime import datetime
from utils.validators import get_date_input, confirm_action

def get_date_range():
    """Запрашивает у пользователя диапазон дат (Модификация 3: с валидацией)"""
    print("\n--- ВЫБОР ПЕРИОДА ---")
    date_from = get_date_input("Начальная дата (ГГГГ-ММ-ДД, Enter - начало месяца): ", allow_empty=True)
    date_to = get_date_input("Конечная дата (ГГГГ-ММ-ДД, Enter - сегодня): ", allow_empty=True)
    
    if not date_from:
        date_from = datetime.now().strftime("%Y-%m-01")
    if not date_to:
        date_to = datetime.now().strftime("%Y-%m-%d")
    
    return date_from, date_to

def get_category_filter(user_id, type_filter="expense"):
    """
    МОДИФИКАЦИЯ 3: Запрашивает у пользователя фильтр по категории
    Возвращает category_id или None (если фильтр не нужен)
    """
    # Спрашиваем, нужен ли фильтр
    print("\n--- ФИЛЬТР ПО КАТЕГОРИИ ---")
    filter_choice = input("Фильтровать по конкретной категории? (да/нет, Enter - нет): ").strip().lower()
    
    if filter_choice not in ["да", "yes", "y", "д", "1"]:
        return None
    
    # Получаем категории пользователя
    categories = Category.get_by_type(user_id, type_filter)
    
    if not categories:
        print(f"✗ У вас нет категорий для {'расходов' if type_filter == 'expense' else 'доходов'}")
        return None
    
    print(f"\nДоступные категории ({'расходы' if type_filter == 'expense' else 'доходы'}):")
    print("0. Все категории (отмена фильтра)")
    for cat in categories:
        cat_id, name = cat
        print(f"  {cat_id}. {name}")
    
    try:
        cat_id = int(input("\nВыберите категорию по ID: ").strip())
        if cat_id == 0:
            return None
        
        # Проверяем, существует ли такая категория
        valid = False
        for cat in categories:
            if cat[0] == cat_id:
                valid = True
                break
        if not valid:
            print("✗ Неверная категория! Фильтр не применяется")
            return None
        
        return cat_id
    except ValueError:
        print("✗ Неверный ввод! Фильтр не применяется")
        return None

def report_income_expense(user_id):
    """Отчёт: Доходы и расходы за период"""
    date_from, date_to = get_date_range()
    
    total_income, income_count, total_expense, expense_count = Report.get_income_expense(
        user_id, date_from, date_to
    )
    
    balance = total_income - total_expense
    
    print("\n" + "=" * 50)
    print("        ДОХОДЫ И РАСХОДЫ")
    print(f"        Период: {date_from} — {date_to}")
    print("=" * 50)
    print(f"Доходы:     {total_income:>12.2f} ₽  ({income_count} операций)")
    print(f"Расходы:    {total_expense:>12.2f} ₽  ({expense_count} операций)")
    print("-" * 50)
    
    if balance >= 0:
        print(f"Экономия:   {balance:>12.2f} ₽")
    else:
        print(f"Перерасход: {balance:>12.2f} ₽")
    print("=" * 50)

def report_expense_by_category(user_id):
    """
    Отчёт: Расходы по категориям за период
    МОДИФИКАЦИЯ 3: Добавлена фильтрация по категории
    """
    date_from, date_to = get_date_range()
    
    # МОДИФИКАЦИЯ 3: Запрашиваем фильтр по категории
    category_filter = get_category_filter(user_id, "expense")
    
    # Если выбран фильтр по категории, показываем детальный отчёт
    if category_filter:
        report_expense_by_single_category(user_id, date_from, date_to, category_filter)
        return
    
    # Иначе показываем обычный отчёт по всем категориям
    results = Report.get_expense_by_category(user_id, date_from, date_to)
    
    print("\n" + "=" * 50)
    print("        РАСХОДЫ ПО КАТЕГОРИЯМ")
    print(f"        Период: {date_from} — {date_to}")
    print("=" * 50)
    
    if not results:
        print("Расходов за выбранный период нет")
    else:
        print(f"{'Категория':<25} {'Сумма':>12} {'Операций':>8}")
        print("-" * 50)
        total = 0
        for name, amount, count in results:
            print(f"{name:<25} {amount:>12.2f} ₽ {count:>8}")
            total += amount
        print("-" * 50)
        print(f"{'ИТОГО:':<25} {total:>12.2f} ₽")
    print("=" * 50)


def report_expense_by_single_category(user_id, date_from, date_to, category_id):
    """
    МОДИФИКАЦИЯ 3: Детальный отчёт по одной категории расходов
    """
    # Получаем название категории
    categories = Category.get_by_type(user_id, "expense")
    category_name = "Неизвестно"
    for cat in categories:
        if cat[0] == category_id:
            category_name = cat[1]
            break
    
    # Получаем детальные операции по этой категории
    from models.operation import Operation
    operations = Operation.get_all(user_id, date_from, date_to, category_id)
    
    print("\n" + "=" * 60)
    print(f"  РАСХОДЫ ПО КАТЕГОРИИ: {category_name}")
    print(f"  Период: {date_from} — {date_to}")
    print("=" * 60)
    
    if not operations:
        print("✗ Нет операций за выбранный период")
        return
    
    print(f"{'ID':<5} {'Дата':<12} {'Сумма':<12} {'Счёт':<15} {'Комментарий':<20}")
    print("-" * 70)
    
    total = 0
    for op in operations:
        op_id, date, amount, description, cat_name, cat_type, acc_name = op
        print(f"{op_id:<5} {str(date):<12} {amount:>10.2f} ₽ {acc_name:<15} {(description or '-'):<20}")
        total += amount
    
    print("-" * 70)
    print(f"{'ИТОГО:':<30} {total:>10.2f} ₽")
    print("=" * 60)


def report_income_by_category(user_id):
    """
    Отчёт: Доходы по категориям за период
    МОДИФИКАЦИЯ 3: Добавлена фильтрация по категории
    """
    date_from, date_to = get_date_range()
    
    # МОДИФИКАЦИЯ 3: Запрашиваем фильтр по категории
    category_filter = get_category_filter(user_id, "income")
    
    # Если выбран фильтр по категории, показываем детальный отчёт
    if category_filter:
        report_income_by_single_category(user_id, date_from, date_to, category_filter)
        return
    
    # Иначе показываем обычный отчёт по всем категориям
    results = Report.get_income_by_category(user_id, date_from, date_to)
    
    print("\n" + "=" * 50)
    print("        ДОХОДЫ ПО КАТЕГОРИЯМ")
    print(f"        Период: {date_from} — {date_to}")
    print("=" * 50)
    
    if not results:
        print("Доходов за выбранный период нет")
    else:
        print(f"{'Категория':<25} {'Сумма':>12} {'Операций':>8}")
        print("-" * 50)
        total = 0
        for name, amount, count in results:
            print(f"{name:<25} {amount:>12.2f} ₽ {count:>8}")
            total += amount
        print("-" * 50)
        print(f"{'ИТОГО:':<25} {total:>12.2f} ₽")
    print("=" * 50)


def report_income_by_single_category(user_id, date_from, date_to, category_id):
    """
    МОДИФИКАЦИЯ 3: Детальный отчёт по одной категории доходов
    """
    # Получаем название категории
    categories = Category.get_by_type(user_id, "income")
    category_name = "Неизвестно"
    for cat in categories:
        if cat[0] == category_id:
            category_name = cat[1]
            break
    
    # Получаем детальные операции по этой категории
    from models.operation import Operation
    operations = Operation.get_all(user_id, date_from, date_to, category_id)
    
    print("\n" + "=" * 60)
    print(f"  ДОХОДЫ ПО КАТЕГОРИИ: {category_name}")
    print(f"  Период: {date_from} — {date_to}")
    print("=" * 60)
    
    if not operations:
        print("✗ Нет операций за выбранный период")
        return
    
    print(f"{'ID':<5} {'Дата':<12} {'Сумма':<12} {'Счёт':<15} {'Комментарий':<20}")
    print("-" * 70)
    
    total = 0
    for op in operations:
        op_id, date, amount, description, cat_name, cat_type, acc_name = op
        print(f"{op_id:<5} {str(date):<12} {amount:>10.2f} ₽ {acc_name:<15} {(description or '-'):<20}")
        total += amount
    
    print("-" * 70)
    print(f"{'ИТОГО:':<30} {total:>10.2f} ₽")
    print("=" * 60)


def report_account_balances(user_id):
    """Отчёт: Остатки по счетам"""
    accounts = Report.get_account_balances(user_id)
    
    if not accounts:
        print("\n✗ У вас нет счетов")
        return
    
    print("\n" + "=" * 55)
    print("            ОСТАТКИ ПО СЧЕТАМ")
    print("=" * 55)
    print(f"{'ID':<5} {'Название':<25} {'Баланс':>15} {'Валюта':<8}")
    print("-" * 55)
    
    total = 0
    for acc_id, name, balance, currency_code, symbol in accounts:
        print(f"{acc_id:<5} {name:<25} {balance:>15.2f} {symbol:<7}")
        total += balance
    
    print("-" * 55)
    print(f"{'ИТОГО:':<31} {total:>15.2f} ₽")
    print("=" * 55)

def report_budget_execution(user_id):
    """Отчёт: Выполнение бюджета"""
    date_from, date_to = get_date_range()
    month_date = date_from[:7] + "-01"
    
    results = Report.get_budget_execution(user_id, month_date, date_from, date_to)
    
    print("\n" + "=" * 65)
    print("            ВЫПОЛНЕНИЕ БЮДЖЕТА")
    print(f"            Месяц: {date_from[:7]}")
    print("=" * 65)
    
    if not results:
        print("Нет данных о бюджете за выбранный период")
    else:
        print(f"{'Категория':<20} {'Бюджет':>10} {'Потрачено':>10} {'Остаток':>10} {'%':>8}")
        print("-" * 65)
        total_budget = 0
        total_spent = 0
        for name, budget, spent, remaining in results:
            percent = (spent / budget * 100) if budget > 0 else 0
            warning = " ⚠ ПЕРЕРАСХОД" if percent > 100 else ""
            print(f"{name:<20} {budget:>10.2f} {spent:>10.2f} {remaining:>10.2f} {percent:>7.1f}%{warning}")
            total_budget += budget
            total_spent += spent
        
        print("-" * 65)
        total_remaining = total_budget - total_spent
        print(f"{'ИТОГО:':<20} {total_budget:>10.2f} {total_spent:>10.2f} {total_remaining:>10.2f}")
        
        if total_spent > total_budget:
            print("\n⚠ ВНИМАНИЕ! Общий перерасход бюджета!")
    
    print("=" * 65)

def run_reports_menu(user_id):
    """Запуск меню отчётов"""
    while True:
        print("\n" + "=" * 50)
        print("              ОТЧЁТЫ")
        print("=" * 50)
        print("1. Доходы и расходы за период")
        print("2. Расходы по категориям")
        print("3. Доходы по категориям")
        print("4. Остатки по счетам")
        print("5. Выполнение бюджета")
        print("6. Назад")
        print("-" * 50)
        
        choice = input("Выберите действие (1-6): ").strip()
        
        if choice == "1":
            report_income_expense(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "2":
            report_expense_by_category(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "3":
            report_income_by_category(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "4":
            report_account_balances(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "5":
            report_budget_execution(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "6":
            break
        else:
            print("✗ Неверный выбор!")