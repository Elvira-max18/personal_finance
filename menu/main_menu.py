# Главное меню приложения

import sys
from models.user import User

def print_main_menu():
    """Выводит главное меню (до входа)"""
    print("\n" + "=" * 50)
    print("        ЛИЧНЫЙ ФИНАНСОВЫЙ УЧЁТ")
    print("=" * 50)
    print("1. Вход в систему")
    print("2. Регистрация")
    print("3. Выход")
    print("-" * 50)

def print_user_menu(full_name):
    """Выводит меню пользователя (после входа)"""
    print("\n" + "=" * 50)
    print(f"   Добро пожаловать, {full_name}!")
    print("=" * 50)
    print("1. Мои операции")
    print("2. Управление категориями")
    print("3. Управление счетами")
    print("4. Управление метками (тегами)")
    print("5. Бюджет")
    print("6. Отчёты")
    print("7. Выйти из аккаунта")
    print("-" * 50)

def login():
    """Функция входа в систему"""
    print("\n--- ВХОД В СИСТЕМУ ---")
    username = input("Введите логин: ").strip()
    password = input("Введите пароль: ").strip()
    
    if not username or not password:
        print("✗ Логин и пароль не могут быть пустыми!")
        return None, None
    
    success, user_id, full_name = User.authenticate(username, password)
    
    if success:
        print(f"✓ Добро пожаловать, {full_name}!")
        return user_id, full_name
    else:
        print("✗ Неверный логин или пароль!")
        return None, None

def register():
    """Функция регистрации нового пользователя"""
    print("\n--- РЕГИСТРАЦИЯ ---")
    username = input("Введите логин: ").strip()
    password = input("Введите пароль: ").strip()
    full_name = input("Введите ваше имя (можно пропустить Enter): ").strip()
    email = input("Введите email (можно пропустить Enter): ").strip()
    
    if not username or not password:
        print("✗ Логин и пароль обязательны для заполнения!")
        return
    
    success, message, user_id = User.create_user(username, password, full_name, email)
    print(f"{'✓' if success else '✗'} {message}")
    
    if success:
        print("Теперь вы можете войти в систему (пункт 1)")

def run_main_menu():
    """Запуск главного меню (до входа)"""
    while True:
        print_main_menu()
        choice = input("Выберите действие (1-3): ").strip()
        
        if choice == "1":
            user_id, full_name = login()
            if user_id:
                run_user_menu(user_id, full_name)
        elif choice == "2":
            register()
        elif choice == "3":
            print("\n✓ До свидания! Спасибо за использование программы.")
            sys.exit(0)
        else:
            print("✗ Неверный выбор! Пожалуйста, выберите 1, 2 или 3.")

def run_user_menu(user_id, full_name):
    """Запуск меню пользователя (после входа)"""
    while True:
        print_user_menu(full_name)
        choice = input("Выберите действие (1-7): ").strip()
        
        if choice == "1":
            # МОИ ОПЕРАЦИИ
            from services.operation_service import run_operations_menu
            run_operations_menu(user_id)
        elif choice == "2":
            # УПРАВЛЕНИЕ КАТЕГОРИЯМИ
            from services.category_service import run_category_menu
            run_category_menu(user_id)
        elif choice == "3":
            # УПРАВЛЕНИЕ СЧЕТАМИ
            from services.account_service import run_account_menu
            run_account_menu(user_id)
        elif choice == "4":
         from services.tag_service import run_tags_menu
         run_tags_menu(user_id)
        elif choice == "5":
         from services.budget_service import run_budget_menu
         run_budget_menu(user_id)
        elif choice == "6":
         from services.report_service import run_reports_menu
         run_reports_menu(user_id)
        elif choice == "7":
            print("\n✓ Вы вышли из аккаунта.")
            break
        else:
            print("✗ Неверный выбор! Пожалуйста, выберите 1-7.")