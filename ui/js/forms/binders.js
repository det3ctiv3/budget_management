import { formDataAsJson } from "./helpers.js";

export function bindStaticForms(handlers) {
  document.getElementById("accountForm").addEventListener("submit", handlers.onAccountSubmit);
  document.getElementById("debtForm").addEventListener("submit", handlers.onDebtSubmit);
  document.getElementById("budgetForm").addEventListener("submit", handlers.onBudgetSubmit);
  document.getElementById("categoryLimitForm").addEventListener("submit", handlers.onCategoryLimitSubmit);
  document.getElementById("refreshAnalytics").addEventListener("click", handlers.onRefreshAnalytics);
  document.getElementById("applyApiUrl").addEventListener("click", handlers.onApplyApiUrl);
}

export function bindTransactionForms(handlers) {
  document.getElementById("expenseForm").addEventListener("submit", handlers.onExpenseSubmit);
  document.getElementById("incomeForm").addEventListener("submit", handlers.onIncomeSubmit);
  document.getElementById("transferForm").addEventListener("submit", handlers.onTransferSubmit);
}

export { formDataAsJson };
