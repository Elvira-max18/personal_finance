# Бизнес-логика для работы с метками

from models.tag import Tag
from models.operation import Operation

def show_tags(user_id):
    """Показать все метки пользователя"""
    tags = Tag.get_all(user_id)
    
    if not tags:
        print("\n--- МЕТКИ ---")
        print("У вас пока нет меток. Добавьте первую!")
        return
    
    print("\n" + "=" * 40)
    print("        ВАШИ МЕТКИ")
    print("=" * 40)
    print(f"{'ID':<5} {'Название':<25}")
    print("-" * 40)
    
    for tag in tags:
        tag_id, name = tag
        print(f"{tag_id:<5} {name:<25}")
    
    print("-" * 40)

def add_tag_flow(user_id):
    """Поток добавления метки"""
    print("\n--- ДОБАВЛЕНИЕ МЕТКИ ---")
    
    name = input("Название метки: ").strip()
    if not name:
        print("✗ Название не может быть пустым!")
        return
    
    success, message = Tag.add(user_id, name)
    print(f"{'✓' if success else '✗'} {message}")

def edit_tag_flow(user_id):
    """Поток редактирования метки"""
    show_tags(user_id)
    
    try:
        tag_id = int(input("\nВведите ID метки для редактирования: ").strip())
    except ValueError:
        print("✗ Неверный ID!")
        return
    
    new_name = input("Новое название метки: ").strip()
    if not new_name:
        print("✗ Название не может быть пустым!")
        return
    
    success, message = Tag.update(tag_id, user_id, new_name)
    print(f"{'✓' if success else '✗'} {message}")

def delete_tag_flow(user_id):
    """Поток удаления метки"""
    show_tags(user_id)
    
    try:
        tag_id = int(input("\nВведите ID метки для удаления: ").strip())
    except ValueError:
        print("✗ Неверный ID!")
        return
    
    confirm = input("Вы уверены? Метка будет удалена из всех операций. (да/нет): ").strip().lower()
    if confirm == "да":
        success, message = Tag.delete(tag_id, user_id)
        print(f"{'✓' if success else '✗'} {message}")
    else:
        print("✗ Удаление отменено")

def manage_operation_tags_flow(user_id):
    """Управление метками для конкретной операции"""
    # Показываем последние операции
    operations = Operation.get_all(user_id, None, None, None)
    
    if not operations:
        print("\n✗ Нет операций для работы с метками")
        return
    
    print("\n" + "=" * 70)
    print("        ПОСЛЕДНИЕ ОПЕРАЦИИ (для выбора)")
    print("=" * 70)
    print(f"{'ID':<5} {'Дата':<12} {'Сумма':<12} {'Категория':<20}")
    print("-" * 70)
    
    for op in operations[:10]:
        op_id, date, amount, description, cat_name, cat_type, acc_name = op
        print(f"{op_id:<5} {str(date):<12} {amount:>10.2f} ₽ {cat_name:<20}")
    
    print("-" * 70)
    
    try:
        op_id = int(input("\nВведите ID операции: ").strip())
        
        # Проверяем, существует ли операция
        op_exists = False
        for op in operations:
            if op[0] == op_id:
                op_exists = True
                break
        
        if not op_exists:
            print("✗ Операция не найдена!")
            return
        
        while True:
            # Показываем текущие метки операции
            current_tags = Tag.get_tags_for_operation(op_id, user_id)
            
            print(f"\n--- МЕТКИ ДЛЯ ОПЕРАЦИИ ID={op_id} ---")
            if current_tags:
                print("Текущие метки:")
                for tag in current_tags:
                    tag_id, name = tag
                    print(f"  - {name} (ID: {tag_id})")
            else:
                print("У этой операции пока нет меток")
            
            print("\n1. Добавить метку к операции")
            print("2. Удалить метку из операции")
            print("3. Назад")
            
            choice = input("Выберите действие (1-3): ").strip()
            
            if choice == "1":
                # Показываем все метки пользователя
                all_tags = Tag.get_all(user_id)
                if not all_tags:
                    print("✗ У вас нет меток. Сначала создайте метку в пункте 'Управление метками'")
                    continue
                
                print("\nДоступные метки:")
                for tag in all_tags:
                    tag_id, name = tag
                    print(f"  {tag_id}. {name}")
                
                try:
                    tag_id = int(input("Выберите ID метки: ").strip())
                    success, message = Tag.add_tag_to_operation(op_id, tag_id, user_id)
                    print(f"{'✓' if success else '✗'} {message}")
                except ValueError:
                    print("✗ Неверный ID!")
                    
            elif choice == "2":
                if not current_tags:
                    print("✗ У этой операции нет меток для удаления")
                    continue
                
                print("\nВыберите метку для удаления:")
                for tag in current_tags:
                    tag_id, name = tag
                    print(f"  {tag_id}. {name}")
                
                try:
                    tag_id = int(input("Введите ID метки: ").strip())
                    success, message = Tag.remove_tag_from_operation(op_id, tag_id, user_id)
                    print(f"{'✓' if success else '✗'} {message}")
                except ValueError:
                    print("✗ Неверный ID!")
                    
            elif choice == "3":
                break
            else:
                print("✗ Неверный выбор!")
                
    except ValueError:
        print("✗ Неверный ID!")

def run_tags_menu(user_id):
    """Запуск меню управления метками"""
    while True:
        print("\n" + "=" * 50)
        print("        УПРАВЛЕНИЕ МЕТКАМИ (ТЕГАМИ)")
        print("=" * 50)
        print("1. Показать все метки")
        print("2. Добавить метку")
        print("3. Редактировать метку")
        print("4. Удалить метку")
        print("5. Управление метками операций")
        print("6. Назад")
        print("-" * 50)
        
        choice = input("Выберите действие (1-6): ").strip()
        
        if choice == "1":
            show_tags(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "2":
            add_tag_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "3":
            edit_tag_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "4":
            delete_tag_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "5":
            manage_operation_tags_flow(user_id)
            input("\nНажмите Enter, чтобы продолжить...")
        elif choice == "6":
            break
        else:
            print("✗ Неверный выбор!")