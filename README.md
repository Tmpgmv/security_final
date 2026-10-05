# Федеральное государственное автономное образовательное учреждение высшего образования «Национальный исследовательский ядерный университет «МИФИ»

## Специальность

09.02.11 Разработка и управление программным обеспечением

Наименование квалификации: Программист

Наименование направленности: Разработка информационных систем

## Экзаменационная работа `ООО \"Мастер Пол\"`
Выполнил: Граблевский Михаил Владимирович

Дата: 2026-10-04

Описание проекта: Итоговый проект (сессионное задание). Сетевая информационная безопасность.


## Создание виртуального окружения
```bash 
python -m venv .venv
```

## Активация виртуального окружения
```bash 
.venv\Scripts\activate  # Windows

source .venv/bin/activate # Linux/MacOS
```

## Установка зависимостей
```bash 
pip install --no-index --find-links=D:\dependencies -r requirements.txt
```

## Применение миграций
```bash
python manage.py migrate
```

## Создать суперпользователя (по необходимости)
```bash
python manage.py createsuperuser
```

## Создать пользователей
```bash
python manage.py createusers
```


## Запуск сервера
```bash
python manage.py runserver
```

## Выполнение тестов
```bash
python manage.py test
```


## Подготовка документации

```bash
python manage.py modelinfo -v 3 --markdown >> temp_modelinfo.md
```

```bash
cat temp_modelinfo.md >> README.md
```

```bash
rm temp_modelinfo.md
```

## Скрипт создания базы данных

```bash
pg_dump --schema-only --dbname=grablevskiy_m_v_master_pol --username=avia --password --host=localhost > schema.sql
```


## Скрипт создания базы данных

```bash
pg_dump --data-only --dbname=grablevskiy_m_v_master_pol --username=avia --password --host=localhost > schema.sql
```
