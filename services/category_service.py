# Бизнес-логика для работы с категориями

from models.category import Category

def show_categories(user_id):
    """Показать все категории пользователя в виде таблицы"""
    categories = Category.get_all(user_id)
    
    if not categories:
        print("\n--- КАТЕГОРИИ ---")
        print("У вас пока нет категорий. Добавьте первую!")
        return
    
    print("\n" + "=" * 50)
    print("        ВАШИ КАТЕГОРИИ")
    print("=" * 50)
    print(f"{'ID':<5} {'Название':<25} {'Тип':<15}")
    print("-" * 50)
    
    for cat in categories:
        cat_id, name, cat_type = cat
        type_rus = "Доход" if cat_type == "income" else "Расход"
        print(f"{cat_id:<5} {name:<25} {type_rus:<15}")
    
    print("-" * 50)

def add_category_flow(user_id):
    """Поток добавления категории"""
    print("\n--- ДОБАВЛЕНИЕ КАТЕГОРИИ ---")
    
    name = input("Название категории: ").strip()
    if not name:
        print("✗ Название не может быть пустым!")
        return
    
    print("Тип категории:")
    print("1. Доход")
    print("2. Расход")
    
    type_choice = input("Выберите (1-2): ").strip()
    
    if type_choice == "1":
        category_type = "income"
        type_name = "Доход"
    elif type_choice == "2":
        category_type = "expense"
        type_name = "Расход"
    else:
        print("✗ Неверный выбор!")
        return
    
    success, message = Category.add(user_id, name, category_type)
    print(f"{'✓' if success else '✗'} {message}")

def edit_category_flow(user_id):
    """Поток редактирования категории"""
    show_categories(user_id)
    
    try:
        cat_id = int(input("\nВведите ID категории для редактирования: ").strip())
    except ValueError:
        print("✗ Неверный ID!")
        return
    
    new_name = input("Новое название категории: ").strip()
    if not new_name:
        print("✗ Название не может быть пустым!")
        return
    
    success, message = Category.update(cat_id, user_id, new_name)
    print(f"{'✓' if success else '✗'} {message}")

def delete_category_flow(user_id):
    """Поток удаления категории"""
    show_categories(user_id)
    
    try:
        cat_id = int(input("\nВведите ID категории для удаления: ").strip())
    except ValueError:
        print("✗ Неверный ID!")
        return
    
    success, message = Category.delete(cat_id, user_id)
    print(f"{'✓' if success else '✗'} {message}")

def run_category_menu(user_id):
    """Запуск меню управления категориями"""
    while True:
        print("\n" + "=" * 50)
        print("        УПРАВЛЕНИЕ КАТЕГОРИЯМИ")
        print("=" * 50)
        print("1. Показать все категории")
        print("2. Добавить категорию")
        print("3. Редактировать категорию")
        print("4. Удалить категорию")
        print("5. Назад")
        print("-" * 50)
        
        choice = input("Выберите действие (1-5): ").strip()
        
        if choice == "1":
            show_categories(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "2":
            add_category_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "3":
            edit_category_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "4":
            delete_category_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "5":
            break
        else:
            print("✗ Неверный выбор! Пожалуйста, выберите 1-5.")