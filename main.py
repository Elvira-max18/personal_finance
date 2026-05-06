# Главный файл для запуска программы

from menu.main_menu import run_main_menu

def main():
    """Запуск приложения"""
    print("\n" + "=" * 50)
    print("   ЗАПУСК ПРОГРАММЫ 'ЛИЧНЫЙ ФИНАНСОВЫЙ УЧЁТ'")
    print("=" * 50)
    
    # Запускаем главное меню
    run_main_menu()

if __name__ == "__main__":
    main()