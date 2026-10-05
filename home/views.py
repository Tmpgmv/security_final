from django.views.generic import TemplateView  # PREP


class HomeView(TemplateView):  # PREP
    """
    PREP
    Редактировать данный файл по необходимости.
    При подготовке заготовки проекта надо
    было вывести на экран какой-то шаблон.
    Реальная задача может сильно отличаться.
    """

    template_name = "home/home.html"  # PREP


