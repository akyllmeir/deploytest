# Medical Clinic Django App

Готовое веб-приложение для дипломного проекта.

## Что реализовано
- SQLite по умолчанию, с подготовкой к будущему переходу на PostgreSQL
- Кастомный пользователь с ролями: admin / doctor / patient
- Саморегистрация отключена: пользователей создаёт администратор
- Профили врача и пациента
- Слоты записи: занятый слот недоступен для пациента
- Подтверждение/отклонение записи врачом
- Итог приёма: MedicalRecord + несколько Prescription
- Русский / Қазақша переключение без перезапуска
- Нормальные Bootstrap-страницы
- Улучшенная Django admin panel

## Быстрый запуск
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Открыть:
- Сайт: http://127.0.0.1:8000/
- Админка: http://127.0.0.1:8000/admin/

## Демо пользователи
После `python manage.py seed_demo`:
- admin@clinic.local / Admin123!
- doctor@clinic.local / Doctor123!
- patient@clinic.local / Patient123!

## SQLite сейчас, PostgreSQL потом
По умолчанию используется SQLite. Для перехода на PostgreSQL:
1. Создай `.env`
2. Поставь `USE_POSTGRES=True`
3. Укажи `DB_*`
4. Выполни миграции на новой БД

Модели написаны без SQLite/PostgreSQL-специфичных полей, поэтому миграции останутся совместимыми.
