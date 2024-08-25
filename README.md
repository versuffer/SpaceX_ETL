# SpaceX ETL
### Основная информация о сервисе

**Python**: 3.11.9 и выше

**Зависимости**: 
   - FastAPI;
   - Pydantic 2;
   - asyncpg;
   - SQLAlchemy;
   - alembic;
   - httpx;
   - APScheduler

**Краткое описание**: 

SpaceX ETL - сервис, собирающий данные о полётах, миссиях и ракетах компании SpaceX
и сохраняющий их локально в PostgreSQL.

Источник данных (GraphQL): https://spacex-production.up.railway.app/

У сервиса есть локальный API, к которому можно обратиться по адресу http://localhost:8000/
и посмотреть статистику по собранным данным.

### Схема БД
https://dbdiagram.io/d/SpaceX-ETL-DB-Schema-66ca2b3ea346f9518cfabbf4

### Какие задачи решает сервис
1) Раз в минуту собирает данные для объектов launch, mission и rocket;
2) Сохраняет данные в PostgreSQL;
3) При обращении по адресу http://localhost:8000/data_mart/object_url_count
выводит количество публикаций для объектов launch, mission и rocket (количество URL).

### Как запустить сервис
1) Склонировать проект
```bash
git clone https://github.com/versuffer/SpaceX_ETL.git
```
2) Запустить проект из корневой директории с помощью Docker Compose
```bash
docker compose up -d
```

### Как пользоваться сервисом
1) Посмотреть логи всех сервисов
```bash
docker compose logs -f
```
2) Посмотреть логи ETL-планировщика
```bash
docker compose logs -f etl_scheduler
```
3) Получить статистику по собранным данным
```bash
curl -X GET http://localhost:8000/data_mart/object_url_count
```

### Что можно добавить / улучшить
1) Добавить авторизацию на JWT-токенах либо делегировать её стороннему сервису;
2) Прикрутить nginx:
   - Rate Limit;
   - X-Request-Id (трассировка запросов);
   - X-Forwarded-For (определение ip пользователей сервиса);
3) Прикрутить интеграцию с Sentry через Middleware;
4) Прикрутить JSON-логи (добавить кастомный хендлер для логов);
5) Добавить трассировку через Jaeger;
6) Заменить View на Materialized View, если оно станет слишком тяжёлыми;
7) Добавить партиции для таблиц, если данных будет много;
8) Добавить пагинацию при для GraphQL-запросов через limit и offset;
9) Добавить обработку ошибок с помощью кастомных исключений в ETL;
10) Добавить unit-тесты для ETL и API;
11) **ДОБАВИТЬ .env В .gitignore!!!
(.env добавлен в репозиторий для корректной работы Docker Compose)**;
