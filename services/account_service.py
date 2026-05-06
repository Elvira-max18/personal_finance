# Бизнес-логика для работы со счетами

from models.account import Account

def show_accounts(user_id):
    """Показать все счета пользователя в виде таблицы"""
    accounts = Account.get_all(user_id)
    
    if not accounts:
        print("\n--- СЧЕТА ---")
        print("У вас пока нет счетов. Добавьте первый!")
        return
    
    print("\n" + "=" * 55)
    print("            ВАШИ СЧЕТА")
    print("=" * 55)
    print(f"{'ID':<5} {'Название':<25} {'Баланс':<15} {'Валюта':<8}")
    print("-" * 55)
    
    total_balance = 0
    for acc in accounts:
        acc_id, name, balance, currency_code, symbol = acc
        print(f"{acc_id:<5} {name:<25} {balance:>10.2f} {symbol:<7} {currency_code}")
        total_balance += balance
    
    print("-" * 55)
    print(f"{'ИТОГО:':<31} {total_balance:>10.2f} ₽")
    print("=" * 55)

def add_account_flow(user_id):
    """Поток добавления счёта"""
    print("\n--- ДОБАВЛЕНИЕ СЧЁТА ---")
    
    name = input("Название счёта: ").strip()
    if not name:
        print("✗ Название не может быть пустым!")
        return
    
    print("\nВыберите валюту:")
    print("1. Российский рубль (₽)")
    print("2. Доллар США ($)")
    print("3. Евро (€)")
    
    currency_choice = input("Выберите (1-3): ").strip()
    
    if currency_choice == "1":
        currency_id = 1
    elif currency_choice == "2":
        currency_id = 2
    elif currency_choice == "3":
        currency_id = 3
    else:
        print("✗ Неверный выбор! Будет установлен рубль по умолчанию.")
        currency_id = 1
    
    success, message = Account.add(user_id, name, currency_id)
    print(f"{'✓' if success else '✗'} {message}")

def edit_account_flow(user_id):
    """Поток редактирования счёта"""
    show_accounts(user_id)
    
    try:
        acc_id = int(input("\nВведите ID счёта для редактирования: ").strip())
    except ValueError:
        print("✗ Неверный ID!")
        return
    
    new_name = input("Новое название счёта: ").strip()
    if not new_name:
        print("✗ Название не может быть пустым!")
        return
    
    success, message = Account.update(acc_id, user_id, new_name)
    print(f"{'✓' if success else '✗'} {message}")

def delete_account_flow(user_id):
    """Поток удаления счёта"""
    show_accounts(user_id)
    
    try:
        acc_id = int(input("\nВведите ID счёта для удаления: ").strip())
    except ValueError:
        print("✗ Неверный ID!")
        return
    
    success, message = Account.delete(acc_id, user_id)
    print(f"{'✓' if success else '✗'} {message}")

def run_account_menu(user_id):
    """Запуск меню управления счетами"""
    while True:
        print("\n" + "=" * 50)
        print("           УПРАВЛЕНИЕ СЧЕТАМИ")
        print("=" * 50)
        print("1. Показать все счета")
        print("2. Добавить счёт")
        print("3. Редактировать счёт")
        print("4. Удалить счёт")
        print("5. Назад")
        print("-" * 50)
        
        choice = input("Выберите действие (1-5): ").strip()
        
        if choice == "1":
            show_accounts(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "2":
            add_account_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "3":
            edit_account_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "4":
            delete_account_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "5":
            break
        else:
            print("✗ Неверный выбор! Пожалуйста, выберите 1-5.")