from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=200, verbose_name="Наименование")

    def __str__(self):
        return self.name


    class Meta:
        verbose_name_plural = "Товары"
        verbose_name = "Товар"
