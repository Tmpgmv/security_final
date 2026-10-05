import os
import sys
import threading
import time
import webview
from django.core.management import execute_from_command_line


def start_django():
    """
    Запустить веб-приложение на Django в качестве 
    десктопного приложения.

    https://pywebview.flowrl.com/

    Использование: python desktop.py    
    """


    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                          'master_pol.settings')
    
    # Запуск отладочного сервера без перезагрузки.    
    sys.argv = ['manage.py', 'runserver', '127.0.0.1:8000', '--noreload']
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    # 1. Запустить сервер Django в фоновом режиме (демон).
    django_thread = threading.Thread(target=start_django, daemon=True)
    django_thread.start()

    # 2. Подождать, пока сервер Django запустится.
    time.sleep(1)

    # 3. Открыть нативное десктопное окно.
    webview.create_window(
        title="ООО \"Мастер Пол\"",
        url="http://127.0.0.1:8000",
        width=1024,
        height=768,
        resizable=True
    )

    # 4. Запустить цикл GUI loop (закрытие этого окна остановит сервер Django, работающий в фоновом режиме).
    webview.start()
