const categories = [
  "FOOD",
  "TRANSPORT",
  "UTILITIES",
  "SHOPPING",
  "HEALTH",
  "EDUCATION",
  "SALARY",
  "FREELANCE",
  "INVESTMENT",
  "OTHER",
];

const logEl = document.getElementById("log");
const apiBaseInput = document.getElementById("apiBaseUrl");

const state = {
  accounts: [],
  month: new Date().toISOString().slice(0, 7),
};

function apiBase() {
  return apiBaseInput.value.replace(/\/$/, "");
}

function log(message, payload) {
  const row = `[${new Date().toLocaleTimeString()}] ${message}`;
  logEl.textContent = `${row}${payload ? `\n${JSON.stringify(payload, null, 2)}` : ""}\n\n${logEl.textContent}`;
}

async function request(path, options = {}) {
  const res = await fetch(`${apiBase()}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

function optionRows(items) {
  return items
    .map((a) => `<option value="${a.id}">${a.name} (${a.currency})</option>`)
    .join("");
}

function categoryOptions() {
  return categories.map((c) => `<option value="${c}">${c}</option>`).join("");
}

function fmt(n) {
  return Number(n).toFixed(2);
}

function today() {
  return new Date().toISOString().slice(0, 10);
}

function renderAccountsTable(accounts) {
  const html = `
    <table>
      <thead><tr><th>Название</th><th>Тип</th><th>Валюта</th><th>Баланс</th></tr></thead>
      <tbody>
        ${accounts
          .map(
            (a) =>
              `<tr><td>${a.name}</td><td>${a.type}</td><td>${a.currency}</td><td>${fmt(a.balance)}</td></tr>`,
          )
          .join("")}
      </tbody>
    </table>`;
  document.getElementById("accountsTable").innerHTML = accounts.length ? html : "Нет счетов";
}

function renderDebtsTable(debts) {
  const html = `
    <table>
      <thead><tr><th>Тип</th><th>Контрагент</th><th>Сумма</th><th>Оплачено</th><th>Статус</th></tr></thead>
      <tbody>
        ${debts
          .map(
            (d) =>
              `<tr><td>${d.kind}</td><td>${d.counterparty}</td><td>${fmt(d.amount)}</td><td>${fmt(d.paid_amount)}</td><td>${d.status}</td></tr>`,
          )
          .join("")}
      </tbody>
    </table>`;
  document.getElementById("debtsTable").innerHTML = debts.length ? html : "Нет долгов";
}

function mountTransactionForms(accounts) {
  const accountOptions = optionRows(accounts);
  document.getElementById("expenseForm").innerHTML = `
    <select name="account_id" required>${accountOptions}</select>
    <input name="amount" type="number" step="0.01" placeholder="Сумма" required />
    <input name="date" type="date" value="${today()}" required />
    <select name="category">${categoryOptions()}</select>
    <input name="description" placeholder="Описание" />
    <button type="submit">Добавить расход</button>
  `;

  document.getElementById("incomeForm").innerHTML = `
    <select name="account_id" required>${accountOptions}</select>
    <input name="amount" type="number" step="0.01" placeholder="Сумма" required />
    <input name="date" type="date" value="${today()}" required />
    <select name="category">${categoryOptions()}</select>
    <input name="source" placeholder="Источник" />
    <button type="submit">Добавить доход</button>
  `;

  document.getElementById("transferForm").innerHTML = `
    <select name="from_account_id" required>${accountOptions}</select>
    <select name="to_account_id" required>${accountOptions}</select>
    <input name="amount" type="number" step="0.01" placeholder="Сумма" required />
    <input name="date" type="date" value="${today()}" required />
    <input name="exchange_rate" type="number" step="0.0001" placeholder="Курс (если валюты разные)" />
    <input name="description" placeholder="Описание" />
    <button type="submit">Перевести</button>
  `;
}

async function refreshAccounts() {
  const accounts = await request("/accounts");
  state.accounts = accounts;
  renderAccountsTable(accounts);
  mountTransactionForms(accounts);
}

async function refreshDebts() {
  const debts = await request("/debts");
  renderDebtsTable(debts);
}

async function refreshAnalytics() {
  const anchorDate = today();
  const month = state.month;
  const summary = await request(`/analytics/summary?period=month&anchor_date=${anchorDate}`);
  const byCategory = await request(`/analytics/by-category?period=month&anchor_date=${anchorDate}`);
  const budget = await request(`/budgets/monthly/${month}/comparison`);

  document.getElementById("summaryBox").innerHTML = `
    Доход: <b>${fmt(summary.total_income)}</b><br>
    Расход: <b>${fmt(summary.total_expense)}</b><br>
    Net: <b>${fmt(summary.net)}</b>
  `;

  document.getElementById("categoryBox").innerHTML = byCategory.rows.length
    ? byCategory.rows
        .map((r) => `${r.category}: доход ${fmt(r.income)} / расход ${fmt(r.expense)} / net ${fmt(r.net)}`)
        .join("<br>")
    : "Нет данных";

  document.getElementById("budgetBox").innerHTML = `
    Месяц: <b>${budget.month}</b><br>
    План дохода: <b>${budget.income_target ?? "-"}</b><br>
    Факт дохода: <b>${fmt(budget.actual_income)}</b><br>
    Факт расхода: <b>${fmt(budget.actual_expense)}</b><br>
    Итог: <b>${fmt(budget.net_result)}</b>
  `;
}

function formDataAsJson(form) {
  const data = Object.fromEntries(new FormData(form).entries());
  for (const [k, v] of Object.entries(data)) {
    if (v === "") delete data[k];
  }
  return data;
}

function monthValueToApi(value) {
  return value;
}

function bindForms() {
  document.getElementById("accountForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const payload = formDataAsJson(e.target);
      payload.initial_balance = Number(payload.initial_balance);
      await request("/accounts", { method: "POST", body: JSON.stringify(payload) });
      e.target.reset();
      log("Счет создан");
      await refreshAccounts();
      await refreshAnalytics();
    } catch (err) {
      log(`Ошибка создания счета: ${err.message}`);
    }
  });

  document.getElementById("expenseForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const payload = formDataAsJson(e.target);
      payload.amount = Number(payload.amount);
      await request("/expenses", { method: "POST", body: JSON.stringify(payload) });
      log("Расход добавлен", payload);
      await refreshAccounts();
      await refreshAnalytics();
    } catch (err) {
      log(`Ошибка добавления расхода: ${err.message}`);
    }
  });

  document.getElementById("incomeForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const payload = formDataAsJson(e.target);
      payload.amount = Number(payload.amount);
      await request("/incomes", { method: "POST", body: JSON.stringify(payload) });
      log("Доход добавлен", payload);
      await refreshAccounts();
      await refreshAnalytics();
    } catch (err) {
      log(`Ошибка добавления дохода: ${err.message}`);
    }
  });

  document.getElementById("transferForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const payload = formDataAsJson(e.target);
      payload.amount = Number(payload.amount);
      if (payload.exchange_rate) {
        payload.exchange_rate = Number(payload.exchange_rate);
      }
      await request("/transfers", { method: "POST", body: JSON.stringify(payload) });
      log("Перевод выполнен", payload);
      await refreshAccounts();
      await refreshAnalytics();
    } catch (err) {
      log(`Ошибка перевода: ${err.message}`);
    }
  });

  document.getElementById("debtForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const payload = formDataAsJson(e.target);
      payload.amount = Number(payload.amount);
      await request("/debts", { method: "POST", body: JSON.stringify(payload) });
      log("Долг добавлен", payload);
      e.target.reset();
      await refreshDebts();
    } catch (err) {
      log(`Ошибка добавления долга: ${err.message}`);
    }
  });

  document.getElementById("budgetForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const payload = formDataAsJson(e.target);
      payload.month = monthValueToApi(payload.month);
      payload.income_target = Number(payload.income_target);
      state.month = payload.month;
      await request("/budgets/monthly-income", { method: "POST", body: JSON.stringify(payload) });
      log("Месячный бюджет сохранен", payload);
      await refreshAnalytics();
    } catch (err) {
      log(`Ошибка сохранения бюджета: ${err.message}`);
    }
  });

  document.getElementById("categoryLimitForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    try {
      const payload = formDataAsJson(e.target);
      payload.month = monthValueToApi(payload.month);
      payload.limit = Number(payload.limit);
      state.month = payload.month;
      await request("/budgets/category-limits", { method: "POST", body: JSON.stringify(payload) });
      log("Лимит категории сохранен", payload);
      await refreshAnalytics();
    } catch (err) {
      log(`Ошибка сохранения лимита: ${err.message}`);
    }
  });

  document.getElementById("refreshAnalytics").addEventListener("click", async () => {
    try {
      await refreshAnalytics();
      log("Аналитика обновлена");
    } catch (err) {
      log(`Ошибка аналитики: ${err.message}`);
    }
  });

  apiBaseInput.addEventListener("change", async () => {
    try {
      await bootstrap();
      log(`API URL изменен: ${apiBase()}`);
    } catch (err) {
      log(`Не удалось подключиться к API: ${err.message}`);
    }
  });
}

async function bootstrap() {
  const monthInputA = document.querySelector("#budgetForm [name='month']");
  const monthInputB = document.querySelector("#categoryLimitForm [name='month']");
  monthInputA.value = state.month;
  monthInputB.value = state.month;

  document.getElementById("categoryLimitCategory").innerHTML = categoryOptions();

  await refreshAccounts();
  await refreshDebts();
  await refreshAnalytics();
}

bindForms();
bootstrap().catch((err) => log(`Ошибка инициализации: ${err.message}`));
