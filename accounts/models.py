from django.db import models


# PREP {
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """
    Расширенная модель пользователя системы.
    Добавлено отчество и методы, в частности, для работы с ролями.
    """
    
    patronymic = models.CharField(max_length=300,
                                  verbose_name="Отчество")

    def get_full_name(self):
        """
        Получить полное ФИО.
        :return: str
        """
        return super().first_name + " " + self.patronymic + " " + super().last_name

    def is_admin(self):
        """
        Проверяет, является ли текущий пользователь администратором.

        :return: bool
        """        
        result = self.groups.filter(name='Администратор').exists() or self.is_superuser
        return result

    def is_manager(self):
        """
        Проверяет, является ли текущий пользователь менеджером.

        :return: bool
        """        
        return self.groups.filter(name='Менеджер').exists()

    def is_client(self):
        """
        Проверяет, является ли текущий пользователь авторизованным клиентом.

        :return: bool
        """        
        return self.groups.filter(name__icontains='авторизированный').exists()        

    def __str__(self):
        return self.get_full_name()

    def role(self):
        """
        Получить роль пользователя.
        Пользователь может иметь множество ролей.
        Но в интерфейсе надо отобразить одну - основную - 
        роль пользователя. Поэтому метод 
        возвращает одну роль.
         
        :return: Group или ""
        """        
        return self.groups.first() or ""

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

# } PREP


