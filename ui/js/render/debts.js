import { fmt } from "./layout.js";

export function renderDebtsTable(debts) {
  const target = document.getElementById("debtsTable");
  if (!debts.length) {
    target.textContent = "No debts recorded.";
    return;
  }

  target.innerHTML = `
    <table>
      <thead><tr><th>Kind</th><th>Counterparty</th><th>Amount</th><th>Paid</th><th>Status</th></tr></thead>
      <tbody>
        ${debts
          .map(
            (item) =>
              `<tr><td>${item.kind}</td><td>${item.counterparty}</td><td>${fmt(item.amount)}</td><td>${fmt(item.paid_amount)}</td><td>${item.status}</td></tr>`,
          )
          .join("")}
      </tbody>
    </table>
  `;
}
