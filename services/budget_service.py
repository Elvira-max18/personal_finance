# Бизнес-логика для работы с бюджетом

from models.budget import Budget
from models.category import Category
from datetime import datetime

def get_current_month():
    """Возвращает текущий месяц в формате ГГГГ-ММ-01"""
    return datetime.now().strftime("%Y-%m-01")

def show_budgets(user_id):
    """Показать все бюджетные лимиты на текущий месяц"""
    month = get_current_month()
    budgets = Budget.get_all(user_id, month)
    
    if not budgets:
        print(f"\n--- БЮДЖЕТ НА {month[:7]} ---")
        print("У вас пока нет установленных бюджетов на этот месяц.")
        print("Добавьте бюджет для категорий расходов!")
        return
    
    print(f"\n" + "=" * 60)
    print(f"        БЮДЖЕТ НА {month[:7]}")
    print("=" * 60)
    print(f"{'ID':<5} {'Категория':<25} {'Бюджет':>15} {'Потрачено':>15}")
    print("-" * 60)
    
    total_budget = 0.0
    total_spent = 0.0
    
    for b in budgets:
        budget_id, cat_name, cat_id, limit_amount, month_date = b
        # Преобразуем Decimal в float
        limit_amount = float(limit_amount) if limit_amount else 0.0
        spent = float(Budget.get_spent_by_category(user_id, cat_id, month))
        remaining = limit_amount - spent
        
        # Определяем статус
        if spent >= limit_amount:
            status = " ⚠ ПЕРЕРАСХОД"
        elif remaining < (limit_amount * 0.2):
            status = " ⚠ Осталось мало"
        else:
            status = ""
        
        print(f"{budget_id:<5} {cat_name:<25} {limit_amount:>15.2f} ₽ {spent:>15.2f} ₽{status}")
        total_budget += limit_amount
        total_spent += spent
    
    print("-" * 60)
    print(f"{'ИТОГО:':<31} {total_budget:>15.2f} ₽ {total_spent:>15.2f} ₽")
    
    if total_spent > total_budget:
        print(f"\n⚠ ВНИМАНИЕ! Общий перерасход бюджета на {total_spent - total_budget:.2f} ₽")
    elif total_budget - total_spent < (total_budget * 0.1):
        print(f"\n⚠ Остаток бюджета менее 10%!")
    
    print("=" * 60)

def add_budget_flow(user_id):
    """Поток добавления/редактирования бюджета"""
    print("\n--- УСТАНОВКА БЮДЖЕТА ---")
    
    # Показываем только категории расходов
    categories = Category.get_by_type(user_id, "expense")
    
    if not categories:
        print("✗ У вас нет категорий расходов. Сначала создайте категорию (пункт 2).")
        return
    
    print("\nДоступные категории расходов:")
    for cat in categories:
        cat_id, name = cat
        print(f"  {cat_id}. {name}")
    
    try:
        cat_id = int(input("\nВыберите категорию по ID: ").strip())
        
        # Проверяем, что категория существует
        valid = False
        cat_name = ""
        for cat in categories:
            if cat[0] == cat_id:
                valid = True
                cat_name = cat[1]
                break
        
        if not valid:
            print("✗ Неверная категория!")
            return
    except ValueError:
        print("✗ Неверный ID!")
        return
    
    try:
        amount = float(input("Введите бюджет на месяц (в рублях): ").strip())
        if amount <= 0:
            print("✗ Сумма должна быть больше 0!")
            return
    except ValueError:
        print("✗ Введите число!")
        return
    
    # Месяц для бюджета (можно выбрать)
    print("\nМесяц для бюджета:")
    print("1. Текущий месяц")
    print("2. Следующий месяц")
    print("3. Указать вручную")
    
    month_choice = input("Выберите (1-3): ").strip()
    
    if month_choice == "1":
        month = get_current_month()
    elif month_choice == "2":
        from datetime import datetime, timedelta
        next_month = datetime.now() + timedelta(days=30)
        month = next_month.strftime("%Y-%m-01")
    elif month_choice == "3":
        year = input("Год (ГГГГ): ").strip()
        month_num = input("Месяц (1-12): ").strip()
        month = f"{year}-{int(month_num):02d}-01"
    else:
        month = get_current_month()
    
    success, message = Budget.set_limit(user_id, cat_id, amount, month)
    print(f"{'✓' if success else '✗'} {message}")

def delete_budget_flow(user_id):
    """Поток удаления бюджета"""
    month = get_current_month()
    budgets = Budget.get_all(user_id, month)
    
    if not budgets:
        print("\n✗ Нет установленных бюджетов на текущий месяц")
        return
    
    print(f"\nВаши бюджеты на {month[:7]}:")
    for b in budgets:
        budget_id, cat_name, cat_id, limit_amount, month_date = b
        limit_amount = float(limit_amount) if limit_amount else 0.0
        print(f"  ID: {budget_id} - {cat_name}: {limit_amount:.2f} ₽")
    
    try:
        budget_id = int(input("\nВведите ID бюджета для удаления: ").strip())
        
        # Находим category_id по budget_id
        cat_id = None
        for b in budgets:
            if b[0] == budget_id:
                cat_id = b[2]
                break
        
        if cat_id is None:
            print("✗ Бюджет не найден!")
            return
        
        confirm = input(f"Удалить бюджет для категории? (да/нет): ").strip().lower()
        if confirm == "да":
            success, message = Budget.delete_limit(user_id, cat_id, month)
            print(f"{'✓' if success else '✗'} {message}")
        else:
            print("✗ Удаление отменено")
            
    except ValueError:
        print("✗ Неверный ID!")

def run_budget_menu(user_id):
    """Запуск меню бюджета"""
    while True:
        print("\n" + "=" * 50)
        print("              БЮДЖЕТ")
        print("=" * 50)
        print("1. Показать бюджеты на текущий месяц")
        print("2. Установить/изменить бюджет")
        print("3. Удалить бюджет")
        print("4. Назад")
        print("-" * 50)
        
        choice = input("Выберите действие (1-4): ").strip()
        
        if choice == "1":
            show_budgets(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "2":
            add_budget_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "3":
            delete_budget_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "4":
            break
        else:
            print("✗ Неверный выбор!")