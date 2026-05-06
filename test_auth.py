# test_auth.py - временный файл для тестирования регистрации

from models.user import User

# Тест регистрации
print("=== ТЕСТ РЕГИСТРАЦИИ ===")

# Регистрируем нового пользователя
success, message, user_id = User.create_user(
    username="test_user",
    password="12345",
    full_name="Тестовый Пользователь",
    email="test@mail.ru"
)

print(f"Результат: {success}")
print(f"Сообщение: {message}")
print(f"ID пользователя: {user_id}")

# Проверяем, что пользователь создался
if success:
    print(f"\n=== ПРОВЕРКА ВХОДА ===")
    success_auth, user_id_auth, full_name = User.authenticate("test_user", "12345")
    print(f"Вход выполнен: {success_auth}")
    print(f"ID: {user_id_auth}")
    print(f"Имя: {full_name}")