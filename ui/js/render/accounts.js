import { categories } from "../state.js";
import { fmt, today } from "./layout.js";

function options(items) {
  return items.map((item) => `<option value="${item.id}">${item.name} (${item.currency})</option>`).join("");
}

function categoryOptions() {
  return categories.map((category) => `<option value="${category}">${category}</option>`).join("");
}

export function renderAccountsTable(accounts) {
  const target = document.getElementById("accountsTable");
  if (!accounts.length) {
    target.textContent = "No accounts yet.";
    return;
  }

  target.innerHTML = `
    <table>
      <thead><tr><th>Name</th><th>Type</th><th>Currency</th><th>Balance</th></tr></thead>
      <tbody>
        ${accounts
          .map((item) => `<tr><td>${item.name}</td><td>${item.type}</td><td>${item.currency}</td><td>${fmt(item.balance)}</td></tr>`)
          .join("")}
      </tbody>
    </table>
  `;
}

export function mountTransactionForms(accounts) {
  const accountOptions = options(accounts);

  document.getElementById("expenseForm").innerHTML = `
    <label>Account<select name="account_id" required>${accountOptions}</select></label>
    <label>Amount<input name="amount" type="number" step="0.01" required /></label>
    <label>Date<input name="date" type="date" value="${today()}" required /></label>
    <label>Category<select name="category">${categoryOptions()}</select></label>
    <label>Description<input name="description" /></label>
    <button type="submit">Add Expense</button>
  `;

  document.getElementById("incomeForm").innerHTML = `
    <label>Account<select name="account_id" required>${accountOptions}</select></label>
    <label>Amount<input name="amount" type="number" step="0.01" required /></label>
    <label>Date<input name="date" type="date" value="${today()}" required /></label>
    <label>Category<select name="category">${categoryOptions()}</select></label>
    <label>Source<input name="source" /></label>
    <button type="submit">Add Income</button>
  `;

  document.getElementById("transferForm").innerHTML = `
    <label>From<select name="from_account_id" required>${accountOptions}</select></label>
    <label>To<select name="to_account_id" required>${accountOptions}</select></label>
    <label>Amount<input name="amount" type="number" step="0.01" required /></label>
    <label>Date<input name="date" type="date" value="${today()}" required /></label>
    <label>Exchange Rate<input name="exchange_rate" type="number" step="0.0001" /></label>
    <label>Description<input name="description" /></label>
    <button type="submit">Transfer</button>
  `;
}

export function mountCategoryLimitOptions() {
  document.getElementById("categoryLimitCategory").innerHTML = categoryOptions();
}
