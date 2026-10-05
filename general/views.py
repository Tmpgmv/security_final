from django.http import HttpResponse
from django.views.generic import TemplateView
from general.forms import ModelInputForm


class BaseGeneratorView(TemplateView):
    """
    Базовый генератор кода.
    """
    form_class = ModelInputForm
    repo_task = None
    repo_task_key = None
    model_name = None

    # Абстрактный метод для переопределения
    def get_additional_content(self):
        """Возвращает специфичный для каждого типа генератора контент."""
        raise NotImplementedError

    # Абстрактный метод для переопределения
    def get_template_suffix(self):
        """Возвращает суффикс для имени шаблона."""
        raise NotImplementedError

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class()
        if self.repo_task_key and self.repo_task:
            context[self.repo_task_key] = self.repo_task
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            self.model_name = self._process_model_name(form)
            content = self._generate_full_content()
            return self._create_response(content)
        return super().get(request, *args, **kwargs)

    def _process_model_name(self, form):
        """Обрабатывает имя модели, возвращает словарь с вариантами."""
        model_name_tmp = form.cleaned_data["model_name"].strip()
        return {
            'lower': model_name_tmp.lower(),
            'capitalized': model_name_tmp[0].upper() + model_name_tmp[1:],
            'original': model_name_tmp,
        }

    def _get_model_registration(self):
        """Генерирует код для регистрации модели в административной панели
        (немного различается для классического веб- и REST-приложений)."""
        import_string = "from general.admin import BaseAdmin" if "html" in self.request.path else ""
        parent_class = "BaseAdmin"  if "html" in self.request.path else "admin.ModelAdmin"

        return f"""
------------------------Регистрации модели в админке----------------------------------

from django.contrib import admin
{import_string}


class {self.model_name["capitalized"]}Admin({parent_class}):
    exclude = []

admin.site.register({self.model_name["capitalized"]}, {self.model_name["capitalized"]}Admin)




        
        """

    def _get_model_definition(self):
        """Генерирует определение модели (немного различается для
        классического веб- и REST-приложений)."""

        html_generator = "html" in self.request.path

        result = f"""
------------------------Модель----------------------------------

from django.db import models
"""
        if html_generator:
            result += """from general.model_mixins import TypicalUrlMixin
"""

        result += f"""
        
        
class {self.model_name['capitalized']}("""

        if html_generator:
            result += "TypicalUrlMixin, "
        result += """models.Model):



    def __str__(self):
        
        return f"Id: { self.pk }"
        


    class Meta:
        verbose_name = ""
        verbose_name_plural = ""
        ordering = ["pk"]
"""
        if html_generator:
            result += """            
        # constraints = [
        #     models.CheckConstraint(
        #         condition=Q(time_spent__gt=0),
        #         name="time_spent_gt_0",
        #     )
        # ]"""
        else:
            result += """
        #db_table = "" """
        result += """
        
        
        
        
        """
        

        return result

    def _generate_full_content(self):
        """Генерирует полный контент, комбинируя общую и специфичную части."""
        model_def = self._get_model_definition()
        admin_reg = self._get_model_registration()
        additional = self.get_additional_content()
        return model_def + admin_reg + additional

    def _create_response(self, content):
        """Создает HTTP ответ с контентом."""
        response = HttpResponse(content.encode('utf-8'))
        response['Content-Type'] = 'text/plain; charset=utf-8'
        return response


class HtmlGeneratorView(BaseGeneratorView):
    """
    Генератор кода для классического веб-приложения.

    См. комментарий в general/view_mixins.py/GetVerboseNameMixin
    """
    template_name = "generators/html_generator.html"
    repo_task = "grablevskiy_m_v_5_task1"
    repo_task_key = "repo_task_1"

    def get_additional_content(self):
        """Возвращает специфичный для HTML-генератора контент."""


        return f"""
------------------------Представления----------------------------------

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView, CreateView, DeleteView, ListView
from general.view_mixins import GetVerboseNameMixin


class {self.model_name["capitalized"]}ListView(GetVerboseNameMixin,
                    ListView):
    model = {self.model_name["capitalized"]}

    # Если требуется фильтрация, сортировка и поиск.

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     # Получаем параметры из GET-запроса
    #     search = self.request.GET.get('search')
    #     sort = self.request.GET.get('sort')
    #     filter = self.request.GET.get('filter')
    #
    #     if search:
    #         queryset = queryset.filter(number=search)
    #     if filter:
    #         queryset = queryset.filter(status=filter)
    #     if sort:
    #         queryset = queryset.order_by(sort)
    #     # Если sort не передан, используем сортировку по умолчанию из модели (Meta)
    #     return queryset
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     # Передаём GET-данные в форму, чтобы она отображала текущие значения
    #     context['form'] = SearchSortFilterForm(self.request.GET or None)
    #     return context



class {self.model_name["capitalized"]}DetailView(GetVerboseNameMixin,
                      DetailView):
    model = {self.model_name["capitalized"]}
    template_name = "general/pages/detail.html"


class {self.model_name["capitalized"]}UpdateView(SuccessMessageMixin,
                      GetVerboseNameMixin,
                      UpdateView):
    model = {self.model_name["capitalized"]}
    fields = "__all__"    
    #form_class = {self.model_name["capitalized"]}Form
    success_message = "Сохранено."
    success_url = reverse_lazy("home")
    template_name = "general/pages/form.html"


class {self.model_name["capitalized"]}CreateView(SuccessMessageMixin,
                      GetVerboseNameMixin,
                      CreateView):
    model = {self.model_name["capitalized"]}
    fields = "__all__"
    #form_class = {self.model_name["capitalized"]}Form
    success_message = "Сохранено."
    success_url = reverse_lazy("home")
    template_name = "general/pages/form.html"


class {self.model_name["capitalized"]}DeleteView(SuccessMessageMixin,
                      GetVerboseNameMixin,
                      DeleteView):
    model = {self.model_name["capitalized"]}
    success_message = "Удалено."
    success_url = reverse_lazy("home")
    template_name = "general/pages/confirm_delete.html"




------------------------URL для CRUD----------------------------------

path("{self.model_name["lower"]}/detail/<int:pk>", {self.model_name["capitalized"]}DetailView.as_view(), name="{self.model_name["lower"]}_detail"),
path("{self.model_name["lower"]}/update/<int:pk>", {self.model_name["capitalized"]}UpdateView.as_view(), name="{self.model_name["lower"]}_update"),
path("{self.model_name["lower"]}/delete/<int:pk>", {self.model_name["capitalized"]}DeleteView.as_view(), name="{self.model_name["lower"]}_delete"),
path("{self.model_name["lower"]}/create", {self.model_name["capitalized"]}CreateView.as_view(), name="{self.model_name["lower"]}_create"),
path("{self.model_name["lower"]}/list", {self.model_name["capitalized"]}ListView.as_view(), name="{self.model_name["lower"]}_list"),




------------------------Форма фильтрации, сортировки и поиска ----------------------------------

class SearchSortFilterForm(forms.Form):

    search = forms.IntegerField(required=False,
                                validators=[MinValueValidator(0),],    
                                label="Номер")


    # Как вариант - первым элементом кортежа задавать
    # наименование поля в модели (по которому собрались сортировать). Допустим, модель такая.
    # class Plane(TypicalUrlMixin,
    #            models.Model):
    #    start = models.DateField(verbose_name="Дата ввода в эксплуатацию")
    # Как применять - см. комментарий к HomeView.

    SORT_CHOICES = [
        ('-start', 'Сначала новые ▲'),
        ('start', 'Сначала старые ▼'),
    ]
    sort = forms.ChoiceField(
           choices=SORT_CHOICES,
           initial='-start', # Не должно расходиться с сортировкой по умолчанию в модели (в Meta). 
           required=True,
           label="Дата ввода в эксплуатацию"
    )

    # filter = forms.ModelChoiceField(queryset=Category.objects.all(),
    #                                 empty_label="-- Все категории --", # Изменить по необходимости.
    #                                 required=True
    # )

    filter = forms.ChoiceField(choices=choices(["Все статусы"] + STATUSES),
                               required=False,
                               label="Статус")





------------------------Представление для хомяка----------------------------------

from django.urls import reverse_lazy
from django.views.generic import RedirectView


class HomeView(RedirectView):
    permanent = True
    query_string = True


    def get_redirect_url(self, *args, **kwargs):

        return reverse_lazy("{self.model_name["lower"]}_list")





------------------------Форма----------------------------------

from django.forms import ModelForm
from django import forms


class {self.model_name["capitalized"]}Form(ModelForm):



    class Meta:
        model = {self.model_name["capitalized"]}
        fields = "__all__"

        
        widgets = {{ # Искать в документации по DateInput.
            'start': forms.DateInput(attrs={{"type": "date"}}, format="%Y-%m-%d"),
        }}
        
        

"""


class JsonGeneratorView(BaseGeneratorView):
    """
    Генератор кода для REST-приложения.
    """
    template_name = "generators/json_generator.html"
    repo_task = "grablevskiy_m_v_5_task2"
    repo_task_key = "repo_task_2"

    def _get_serializer(self):
        return f"""        
------------------------Сериализатор----------------------------------
        
from rest_framework import serializers


class {self.model_name["capitalized"]}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {self.model_name["capitalized"]}
        fields = "__all__"        





        """

    def _get_view_set(self):
        """
        Возвращает набор представлений.
        """
    
        return f"""        
------------------------Набор представлений----------------------------------
        
from rest_framework import viewsets, permissions


class {self.model_name["capitalized"]}ViewSet(viewsets.ModelViewSet):
    queryset = {self.model_name["capitalized"]}.objects.all()
    serializer_class = {self.model_name["capitalized"]}Serializer
    permission_classes = [permissions.AllowAny]
      





        """


    def get_additional_content(self):
        """
        Возвращает специфичный для REST-генератора контент.        
        """

        result = self._get_serializer()
        result += self._get_view_set()
        return result
