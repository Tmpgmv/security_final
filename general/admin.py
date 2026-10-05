from django.contrib import admin, messages
from django.db import transaction
import re


class BaseAdmin(admin.ModelAdmin):
    """
    Универсальный базовый класс для обработки ошибок сохранения.

    Причина создания: задание для 09.02.11 может предусматривать разработку триггеров.
    Триггер будет содержать что-то вроде RAISE EXCEPTION,
    а административная панель Django к такому не готова совершенно.

    Применять в admin.py. Пример:

    from django.contrib import admin

    from general.admin import BaseAdmin
    from maintenance_procedures.models import MaintenanceProcedure
    
    
    
    class MaintenanceProcedureAdmin(BaseAdmin):
        exclude = []
    
    admin.site.register(MaintenanceProcedure, MaintenanceProcedureAdmin)

    """

    def save_model(self, request, obj, form, change):
        try:
            with transaction.atomic():
                super().save_model(request, obj, form, change)
        except Exception as e:
            self._handle_save_error(request, form, e)

    def _handle_save_error(self, request, form, error):
        """Обработка ошибок сохранения."""
        errors = self._extract_errors(error)

        for field, error_list in errors.items():
            if field and field in form.fields:
                for err in error_list:
                    form.add_error(field, err)
                    field_label = form.fields[field].label or field
                    messages.error(request, f'❌ {field_label}: {err}')
            else:
                for err in error_list:
                    form.add_error(None, err)
                    messages.error(request, f'❌ {err}')

    def _extract_errors(self, error):
        """Извлекает ошибки из исключения."""
        result = {}

        if hasattr(error, 'message_dict'):
            for field, errors in error.message_dict.items():
                result[field] = errors if isinstance(errors, list) else [errors]
        elif hasattr(error, 'messages') and error.messages:
            result[None] = list(error.messages)
        else:
            error_msg = self._clean_error_message(str(error))
            result[None] = [error_msg]

        return result

    def _clean_error_message(self, error_msg):
        """Очищает сообщение от технической информации."""
        if 'CONTEXT:' in error_msg:
            error_msg = error_msg.split('CONTEXT:')[0].strip()
        error_msg = re.sub(r'line \d+ at', '', error_msg)
        error_msg = re.sub(r'\s+', ' ', error_msg).strip()
        return error_msg

    def message_user(self, request, message, level=messages.INFO, extra_tags='', fail_silently=False):
        """
        Переопределяем отправку сообщений пользователю.
        Убираем все SUCCESS сообщения.
        """
        if level == messages.SUCCESS:
            # Не показываем сообщения об успехе
            return
        super().message_user(request, message, level, extra_tags, fail_silently)
