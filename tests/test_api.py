from __future__ import annotations

from datetime import date


def today_str() -> str:
    return date.today().isoformat()


def this_month() -> str:
    return today_str()[:7]


def create_account(client, name: str, account_type: str, currency: str = "USD", balance: float = 0) -> dict:
    response = client.post(
        "/accounts",
        json={
            "name": name,
            "type": account_type,
            "currency": currency,
            "initial_balance": balance,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_meta_endpoint(client):
    response = client.get("/meta")

    assert response.status_code == 200
    body = response.json()
    assert body["group"]
    assert body["app_name"]
    assert body["version"]


def test_accounts_create_and_list_endpoints(client):
    created = create_account(client, "Main Card", "CARD", "usd", 1200)

    listed = client.get("/accounts")
    assert listed.status_code == 200
    items = listed.json()
    assert len(items) == 1
    assert items[0]["id"] == created["id"]
    assert items[0]["currency"] == "USD"
    assert items[0]["balance"] == 1200.0


def test_expenses_create_list_update_delete_endpoints(client):
    acc_a = create_account(client, "Main", "CARD", balance=1000)
    acc_b = create_account(client, "Cash", "CASH", balance=500)

    created = client.post(
        "/expenses",
        json={
            "account_id": acc_a["id"],
            "amount": 100,
            "date": today_str(),
            "description": "groceries",
            "category": "FOOD",
        },
    )
    assert created.status_code == 200
    expense_id = created.json()["id"]

    listed = client.get("/expenses")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.put(
        f"/expenses/{expense_id}",
        json={
            "account_id": acc_b["id"],
            "amount": 50,
            "date": today_str(),
            "description": "taxi",
            "category": "TRANSPORT",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["account_id"] == acc_b["id"]
    assert updated.json()["amount"] == 50.0

    deleted = client.delete(f"/expenses/{expense_id}")
    assert deleted.status_code == 200
    assert deleted.json()["message"] == "Expense deleted"

    final_list = client.get("/expenses")
    assert final_list.status_code == 200
    assert final_list.json() == []


def test_expenses_insufficient_funds_error(client):
    acc = create_account(client, "Low Balance", "CARD", balance=10)

    response = client.post(
        "/expenses",
        json={
            "account_id": acc["id"],
            "amount": 50,
            "date": today_str(),
            "description": "big expense",
            "category": "OTHER",
        },
    )

    assert response.status_code == 400
    assert "Insufficient funds" in response.json()["detail"]


def test_incomes_create_list_update_delete_endpoints(client):
    acc_a = create_account(client, "Income A", "CARD", balance=200)
    acc_b = create_account(client, "Income B", "BANK_ACCOUNT", balance=100)

    created = client.post(
        "/incomes",
        json={
            "account_id": acc_a["id"],
            "amount": 150,
            "date": today_str(),
            "source": "salary",
            "category": "SALARY",
        },
    )
    assert created.status_code == 200
    income_id = created.json()["id"]

    listed = client.get("/incomes")
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.put(
        f"/incomes/{income_id}",
        json={
            "account_id": acc_b["id"],
            "amount": 90,
            "date": today_str(),
            "source": "freelance",
            "category": "FREELANCE",
        },
    )
    assert updated.status_code == 200
    assert updated.json()["account_id"] == acc_b["id"]
    assert updated.json()["amount"] == 90.0

    deleted = client.delete(f"/incomes/{income_id}")
    assert deleted.status_code == 200
    assert deleted.json()["message"] == "Income deleted"

    final_list = client.get("/incomes")
    assert final_list.status_code == 200
    assert final_list.json() == []


def test_delete_income_insufficient_funds_error(client):
    acc = create_account(client, "Income Spend", "CARD", balance=0)

    income = client.post(
        "/incomes",
        json={
            "account_id": acc["id"],
            "amount": 100,
            "date": today_str(),
            "source": "gift",
            "category": "OTHER",
        },
    )
    assert income.status_code == 200
    income_id = income.json()["id"]

    spend = client.post(
        "/expenses",
        json={
            "account_id": acc["id"],
            "amount": 100,
            "date": today_str(),
            "description": "spent all",
            "category": "OTHER",
        },
    )
    assert spend.status_code == 200

    delete_income = client.delete(f"/incomes/{income_id}")
    assert delete_income.status_code == 400
    assert "Insufficient funds" in delete_income.json()["detail"]


def test_transfers_create_and_list_same_currency_endpoints(client):
    source = create_account(client, "Source", "CARD", balance=500)
    target = create_account(client, "Target", "CASH", balance=10)

    created = client.post(
        "/transfers",
        json={
            "from_account_id": source["id"],
            "to_account_id": target["id"],
            "amount": 75,
            "date": today_str(),
            "description": "wallet top up",
        },
    )
    assert created.status_code == 200
    body = created.json()
    assert body["amount"] == 75.0
    assert body["converted_amount"] == 75.0

    listed = client.get("/transfers")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_transfers_different_currency_requires_exchange_rate(client):
    source = create_account(client, "USD", "CARD", "USD", 100)
    target = create_account(client, "EUR", "CASH", "EUR", 0)

    fail = client.post(
        "/transfers",
        json={
            "from_account_id": source["id"],
            "to_account_id": target["id"],
            "amount": 10,
            "date": today_str(),
            "description": "fx",
        },
    )

    assert fail.status_code == 400
    assert "exchange_rate" in fail.json()["detail"]


def test_transfers_different_currency_with_exchange_rate(client):
    source = create_account(client, "USD", "CARD", "USD", 100)
    target = create_account(client, "EUR", "CASH", "EUR", 0)

    ok = client.post(
        "/transfers",
        json={
            "from_account_id": source["id"],
            "to_account_id": target["id"],
            "amount": 10,
            "exchange_rate": 0.5,
            "date": today_str(),
            "description": "fx",
        },
    )

    assert ok.status_code == 200
    assert ok.json()["converted_amount"] == 5.0


def test_transfers_same_account_error(client):
    account = create_account(client, "Self", "CARD", balance=100)

    response = client.post(
        "/transfers",
        json={
            "from_account_id": account["id"],
            "to_account_id": account["id"],
            "amount": 10,
            "date": today_str(),
            "description": "invalid",
        },
    )

    assert response.status_code == 400
    assert "must be different" in response.json()["detail"]


def test_debts_create_list_payment_close_endpoints(client):
    created = client.post(
        "/debts",
        json={
            "kind": "RECEIVABLE",
            "counterparty": "Ali",
            "amount": 200,
            "date": today_str(),
            "note": "loan",
        },
    )
    assert created.status_code == 200
    debt_id = created.json()["id"]

    listed_open = client.get("/debts?status=OPEN")
    assert listed_open.status_code == 200
    assert len(listed_open.json()) == 1

    payment = client.post(f"/debts/{debt_id}/payments", json={"amount": 50})
    assert payment.status_code == 200
    assert payment.json()["paid_amount"] == 50.0
    assert payment.json()["status"] == "OPEN"

    closed = client.put(f"/debts/{debt_id}/close")
    assert closed.status_code == 200
    assert closed.json()["status"] == "CLOSED"

    listed_closed = client.get("/debts?status=CLOSED")
    assert listed_closed.status_code == 200
    assert len(listed_closed.json()) == 1


def test_debts_overpayment_and_closed_payment_errors(client):
    created = client.post(
        "/debts",
        json={
            "kind": "DEBT",
            "counterparty": "Vendor",
            "amount": 100,
            "date": today_str(),
            "note": "invoice",
        },
    )
    debt_id = created.json()["id"]

    overpay = client.post(f"/debts/{debt_id}/payments", json={"amount": 101})
    assert overpay.status_code == 400
    assert "exceeds" in overpay.json()["detail"]

    client.put(f"/debts/{debt_id}/close")
    closed_payment = client.post(f"/debts/{debt_id}/payments", json={"amount": 1})
    assert closed_payment.status_code == 400
    assert "already closed" in closed_payment.json()["detail"]


def test_budget_endpoints_and_monthly_comparison(client):
    account = create_account(client, "Budget", "CARD", balance=1000)

    month = this_month()
    client.post(
        "/incomes",
        json={
            "account_id": account["id"],
            "amount": 300,
            "date": today_str(),
            "source": "salary",
            "category": "SALARY",
        },
    )
    client.post(
        "/expenses",
        json={
            "account_id": account["id"],
            "amount": 120,
            "date": today_str(),
            "description": "food",
            "category": "FOOD",
        },
    )

    budget_set = client.post("/budgets/monthly-income", json={"month": month, "income_target": 500})
    assert budget_set.status_code == 200
    assert budget_set.json()["income_target"] == 500

    limit_set = client.post(
        "/budgets/category-limits",
        json={"month": month, "category": "FOOD", "limit": 100},
    )
    assert limit_set.status_code == 200
    assert limit_set.json()["limit"] == 100

    comparison = client.get(f"/budgets/monthly/{month}/comparison")
    assert comparison.status_code == 200
    body = comparison.json()
    assert body["month"] == month
    assert body["actual_income"] == 300.0
    assert body["actual_expense"] == 120.0
    assert body["net_result"] == 180.0
    assert body["category_comparison"][0]["category"] == "FOOD"
    assert body["category_comparison"][0]["is_over_limit"] is True


def test_analytics_summary_and_by_category_endpoints(client):
    account = create_account(client, "Analytics", "CARD", balance=0)
    today = today_str()

    client.post(
        "/incomes",
        json={
            "account_id": account["id"],
            "amount": 200,
            "date": today,
            "source": "salary",
            "category": "SALARY",
        },
    )
    client.post(
        "/expenses",
        json={
            "account_id": account["id"],
            "amount": 80,
            "date": today,
            "description": "transport",
            "category": "TRANSPORT",
        },
    )

    summary = client.get(f"/analytics/summary?period=day&anchor_date={today}")
    assert summary.status_code == 200
    assert summary.json()["net"] == 120.0

    by_category = client.get(f"/analytics/by-category?period=day&anchor_date={today}")
    assert by_category.status_code == 200
    rows = by_category.json()["rows"]
    categories = {row["category"] for row in rows}
    assert "SALARY" in categories
    assert "TRANSPORT" in categories


def test_analytics_summary_empty_dataset_returns_zeroes(client):
    today = today_str()
    response = client.get(f"/analytics/summary?period=month&anchor_date={today}")

    assert response.status_code == 200
    body = response.json()
    assert body["total_income"] == 0.0
    assert body["total_expense"] == 0.0
    assert body["net"] == 0.0


def test_analytics_by_category_empty_dataset_returns_empty_rows(client):
    today = today_str()
    response = client.get(f"/analytics/by-category?period=month&anchor_date={today}")

    assert response.status_code == 200
    assert response.json()["rows"] == []


def test_analytics_calendar_endpoint_and_invalid_range(client):
    account = create_account(client, "Calendar", "CARD", balance=0)
    today = today_str()

    client.post(
        "/incomes",
        json={
            "account_id": account["id"],
            "amount": 100,
            "date": today,
            "source": "gift",
            "category": "OTHER",
        },
    )
    client.post(
        "/expenses",
        json={
            "account_id": account["id"],
            "amount": 20,
            "date": today,
            "description": "coffee",
            "category": "FOOD",
        },
    )

    calendar = client.get(f"/analytics/calendar?from_date={today}&to_date={today}")
    assert calendar.status_code == 200
    days = calendar.json()["days"]
    assert len(days) == 1
    assert days[0]["income_count"] == 1
    assert days[0]["expense_count"] == 1

    invalid = client.get(f"/analytics/calendar?from_date={today}&to_date=2000-01-01")
    assert invalid.status_code == 400
    assert "to_date" in invalid.json()["detail"]


def test_analytics_calendar_empty_range_returns_empty_days(client):
    today = today_str()
    response = client.get(f"/analytics/calendar?from_date={today}&to_date={today}")

    assert response.status_code == 200
    assert response.json()["days"] == []


def test_analytics_invalid_period_error(client):
    response = client.get(f"/analytics/summary?period=invalid&anchor_date={today_str()}")
    assert response.status_code == 400
    assert "period must be" in response.json()["detail"]


def test_ai_suggest_category_endpoint(client):
    response = client.post("/ai/suggest-category", json={"description": "paid electricity bill"})

    assert response.status_code == 200
    body = response.json()
    assert body["method"] == "rule-based"
    assert body["suggested_category"] == "UTILITIES"


def test_ai_alerts_endpoint(client):
    account = create_account(client, "AI Alerts", "CARD", balance=500)
    month = this_month()

    client.post("/budgets/category-limits", json={"month": month, "category": "FOOD", "limit": 50})
    client.post(
        "/expenses",
        json={
            "account_id": account["id"],
            "amount": 80,
            "date": today_str(),
            "description": "restaurant",
            "category": "FOOD",
        },
    )

    response = client.get(f"/ai/alerts/{month}")
    assert response.status_code == 200
    alerts = response.json()["alerts"]
    assert len(alerts) == 1
    assert alerts[0]["type"] == "CATEGORY_OVERSPEND"
    assert alerts[0]["category"] == "FOOD"


def test_budget_monthly_comparison_empty_dataset_returns_zeroes(client):
    month = this_month()
    response = client.get(f"/budgets/monthly/{month}/comparison")

    assert response.status_code == 200
    body = response.json()
    assert body["actual_income"] == 0.0
    assert body["actual_expense"] == 0.0
    assert body["net_result"] == 0.0
    assert body["category_comparison"] == []
