from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.db import OperationalError, transaction, IntegrityError

User = get_user_model()  # UNIVERSAL: works with any AUTH_USER_MODEL


class Command(BaseCommand):
    help = 'Create users.'

    USER_GROUP = {
        "a": "Администратор",
        "c": "Авторизованный пользователь",
        "m": "Менеджер",
        "g": "Гость",
    }

    def create_auth_groups(self):
        groups = {}

        for code, group_name in self.USER_GROUP.items():
            group, created = Group.objects.get_or_create(name=group_name)
            groups[code] = group

        group_names = ', '.join(group.name for group in groups.values())
        print(f"Созданы группы: {group_names}")

        return groups

    def create_users(self):
        USERS = ["a", "c", "m", "g"]

        for username in USERS:
            # Общие данные для всех пользователей
            user_data = {
                'username': username,
                'email': f'{username}@{username}.ru',
                'password': username,
                'first_name': username,
            }

            # Создаём суперпользователя или обычного пользователя
            if username == "a":
                User.objects.create_superuser(**user_data)
            else:
                User.objects.create_user(**user_data)

            print("Создан пользователь: " + username)

    def assign_groups_to_users(self, groups):
        for username, group in groups.items():
            user = User.objects.get(username=username)
            user.groups.add(group)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Начало создания пользователей и групп!'))

        try:
            with transaction.atomic():
                groups = self.create_auth_groups()
                self.create_users()
                self.assign_groups_to_users(groups)
        except OperationalError as e:
            self.stdout.write(self.style.ERROR("❌ " + str(e)))
            self.stdout.write(self.style.ERROR("========="))
            self.stdout.write(self.style.ERROR("Попробуйте"))
            self.stdout.write(self.style.ERROR("python manage.py makemigrations"))
            self.stdout.write(self.style.ERROR("python manage.py migrate"))
        except IntegrityError as e:
            self.stdout.write(self.style.ERROR("❌ " + str(e)))
            self.stdout.write(self.style.ERROR("Выявлены дубли"))
            self.stdout.write(self.style.ERROR("Вы забыли сбросить последовательность?"))

        self.stdout.write(self.style.SUCCESS('Завершено!'))
