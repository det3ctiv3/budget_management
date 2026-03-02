#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
TODAY="$(date +%F)"
MONTH="$(date +%Y-%m)"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

need_cmd curl
need_cmd python3

json_get() {
  local key="$1"
  python3 -c 'import json,sys; print(json.load(sys.stdin)[sys.argv[1]])' "$key"
}

echo "== Health =="
curl -sS "$BASE_URL/health"
echo
echo

echo "== 1) Create accounts =="
CARD_JSON="$(curl -sS -X POST "$BASE_URL/accounts" \
  -H 'Content-Type: application/json' \
  -d "{\"name\":\"Main Card\",\"type\":\"CARD\",\"currency\":\"USD\",\"initial_balance\":1000}")"
echo "$CARD_JSON"
CARD_ID="$(echo "$CARD_JSON" | json_get id)"

CASH_JSON="$(curl -sS -X POST "$BASE_URL/accounts" \
  -H 'Content-Type: application/json' \
  -d "{\"name\":\"Cash Wallet\",\"type\":\"CASH\",\"currency\":\"USD\",\"initial_balance\":150}")"
echo "$CASH_JSON"
CASH_ID="$(echo "$CASH_JSON" | json_get id)"
echo

echo "== 2) Add expense (balance decreases) =="
curl -sS -X POST "$BASE_URL/expenses" \
  -H 'Content-Type: application/json' \
  -d "{\"account_id\":\"$CARD_ID\",\"amount\":120,\"date\":\"$TODAY\",\"description\":\"grocery store\",\"category\":\"FOOD\"}"
echo
echo

echo "== 3) Add income (balance increases) =="
curl -sS -X POST "$BASE_URL/incomes" \
  -H 'Content-Type: application/json' \
  -d "{\"account_id\":\"$CARD_ID\",\"amount\":300,\"date\":\"$TODAY\",\"source\":\"salary\",\"category\":\"SALARY\"}"
echo
echo

echo "== 4) Transfer from card to cash =="
curl -sS -X POST "$BASE_URL/transfers" \
  -H 'Content-Type: application/json' \
  -d "{\"from_account_id\":\"$CARD_ID\",\"to_account_id\":\"$CASH_ID\",\"amount\":50,\"date\":\"$TODAY\",\"description\":\"ATM withdraw\"}"
echo
echo

echo "== 5) Create debt and partial payment =="
DEBT_JSON="$(curl -sS -X POST "$BASE_URL/debts" \
  -H 'Content-Type: application/json' \
  -d "{\"kind\":\"RECEIVABLE\",\"counterparty\":\"Ali\",\"amount\":200,\"date\":\"$TODAY\",\"note\":\"Lend to friend\"}")"
echo "$DEBT_JSON"
DEBT_ID="$(echo "$DEBT_JSON" | json_get id)"

curl -sS -X POST "$BASE_URL/debts/$DEBT_ID/payments" \
  -H 'Content-Type: application/json' \
  -d '{"amount":80}'
echo
echo

echo "== 6) Set budget and category limit =="
curl -sS -X POST "$BASE_URL/budgets/monthly-income" \
  -H 'Content-Type: application/json' \
  -d "{\"month\":\"$MONTH\",\"income_target\":2500}"
echo
curl -sS -X POST "$BASE_URL/budgets/category-limits" \
  -H 'Content-Type: application/json' \
  -d "{\"month\":\"$MONTH\",\"category\":\"FOOD\",\"limit\":100}"
echo
echo

echo "== 7) Budget comparison =="
curl -sS "$BASE_URL/budgets/monthly/$MONTH/comparison"
echo
echo

echo "== 8) Analytics summary/by-category/calendar =="
curl -sS "$BASE_URL/analytics/summary?period=month&anchor_date=$TODAY"
echo
curl -sS "$BASE_URL/analytics/by-category?period=month&anchor_date=$TODAY"
echo
curl -sS "$BASE_URL/analytics/calendar?from_date=$TODAY&to_date=$TODAY"
echo
echo

echo "== 9) AI category + alerts =="
curl -sS -X POST "$BASE_URL/ai/suggest-category" \
  -H 'Content-Type: application/json' \
  -d '{"description":"paid electricity bill"}'
echo
curl -sS "$BASE_URL/ai/alerts/$MONTH"
echo
