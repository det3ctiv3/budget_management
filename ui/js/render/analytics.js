import { fmt } from "./layout.js";

export function renderKpis(accounts, summary) {
  const totalBalance = accounts.reduce((acc, item) => acc + Number(item.balance), 0);
  document.getElementById("kpiBalance").textContent = fmt(totalBalance);
  document.getElementById("kpiIncome").textContent = fmt(summary.total_income);
  document.getElementById("kpiExpense").textContent = fmt(summary.total_expense);
  document.getElementById("kpiNet").textContent = fmt(summary.net);
}

export function renderAnalytics(summary, byCategory, budget) {
  document.getElementById("summaryBox").innerHTML = `
    Income: <b>${fmt(summary.total_income)}</b><br>
    Expense: <b>${fmt(summary.total_expense)}</b><br>
    Net: <b>${fmt(summary.net)}</b>
  `;

  document.getElementById("categoryBox").innerHTML = byCategory.rows.length
    ? byCategory.rows
        .map((row) => `${row.category}: income ${fmt(row.income)} / expense ${fmt(row.expense)} / net ${fmt(row.net)}`)
        .join("<br>")
    : "No category data";

  document.getElementById("budgetBox").innerHTML = `
    Month: <b>${budget.month}</b><br>
    Target Income: <b>${budget.income_target ?? "-"}</b><br>
    Actual Income: <b>${fmt(budget.actual_income)}</b><br>
    Actual Expense: <b>${fmt(budget.actual_expense)}</b><br>
    Net Result: <b>${fmt(budget.net_result)}</b>
  `;
}
