import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "price_tracker.settings")

from django.contrib.auth import get_user_model


# Данные суперпользователя из переменных окружения
username = os.getenv("DJANGO_SUPERUSER_USERNAME")
email = os.getenv("DJANGO_SUPERUSER_EMAIL")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

User = get_user_model()

# Проверить, существует ли суперпользователь
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"Суперпользователь {username} создан.")
else:
    print(f"Суперпользователь {username} уже существует.")
