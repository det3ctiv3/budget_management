# Fintech MVP: Income / Expense / Budget Manager

MVP backend для управления личными финансами в одном сервисе:
- счета и карты с балансами;
- расходы, доходы, переводы (включая конвертацию валют);
- долги и задолженности;
- месячные бюджеты и лимиты по категориям;
- аналитика (общая, по категориям, calendar view);
- бонус: rule-based категоризация и алерты.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn main:app --reload
```

Swagger UI:
- `http://127.0.0.1:8000/docs`

## Пользовательский интерфейс (Web UI)

Запустите UI отдельным простым сервером:

```bash
cd ui
python -m http.server 5500
```

Откройте:
- `http://127.0.0.1:5500`

По умолчанию UI подключается к API `http://127.0.0.1:8000` (можно поменять в поле `API URL` в шапке).

## Быстрая демонстрация (end-to-end)

После запуска API можно прогнать готовый сценарий:

```bash
chmod +x demo.sh
./demo.sh
```

Скрипт автоматически выполняет:
- создание счетов,
- расход, доход, перевод,
- долг + частичное погашение,
- бюджет и лимиты,
- аналитику и AI-алерты.

## Основные API группы

- `POST /accounts`, `GET /accounts`
- `POST /expenses`, `GET /expenses`, `PUT /expenses/{id}`, `DELETE /expenses/{id}`
- `POST /incomes`, `GET /incomes`, `PUT /incomes/{id}`, `DELETE /incomes/{id}`
- `POST /transfers`, `GET /transfers`
- `POST /debts`, `GET /debts`, `POST /debts/{id}/payments`, `PUT /debts/{id}/close`
- `POST /budgets/monthly-income`
- `POST /budgets/category-limits`
- `GET /budgets/monthly/{month}/comparison`
- `GET /analytics/summary?period=month&anchor_date=2026-03-02`
- `GET /analytics/by-category?period=month&anchor_date=2026-03-02`
- `GET /analytics/calendar?from_date=2026-03-01&to_date=2026-03-31`
- `POST /ai/suggest-category`
- `GET /ai/alerts/{month}`

## Примеры use case

1. Создать счёт/карту (`POST /accounts`) с `initial_balance`.
2. Добавить расход (`POST /expenses`) и автоматически уменьшить баланс счёта.
3. Добавить доход (`POST /incomes`) и автоматически увеличить баланс.
4. Выполнить перевод между счетами (`POST /transfers`), при разных валютах передать `exchange_rate`.
5. Зафиксировать долг (`POST /debts`) и гасить по частям (`POST /debts/{id}/payments`).
6. Сравнить план и факт за месяц (`GET /budgets/monthly/{month}/comparison`).
