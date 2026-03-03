import { getApiBase, request, setApiBase } from "./api.js";
import { bindStaticForms, bindTransactionForms, formDataAsJson } from "./forms/binders.js";
import { renderAccountsTable, mountCategoryLimitOptions, mountTransactionForms } from "./render/accounts.js";
import { renderAnalytics, renderKpis } from "./render/analytics.js";
import { renderDebtsTable } from "./render/debts.js";
import { bindSettingsPanel, log, today, toast } from "./render/layout.js";
import { state } from "./state.js";

const THEME_KEY = "newecon_theme";

function updateThemeButtons(theme) {
  const darkButton = document.getElementById("themeDarkBtn");
  const lightButton = document.getElementById("themeLightBtn");
  const isLight = theme === "light";

  darkButton.classList.toggle("active", !isLight);
  lightButton.classList.toggle("active", isLight);
  darkButton.setAttribute("aria-pressed", String(!isLight));
  lightButton.setAttribute("aria-pressed", String(isLight));
}

function applyTheme(theme) {
  document.body.setAttribute("data-theme", theme);
  updateThemeButtons(theme);
}

function setTheme(theme) {
  applyTheme(theme);
  localStorage.setItem(THEME_KEY, theme);
}

function initTheme() {
  const storedTheme = localStorage.getItem(THEME_KEY);
  const initialTheme = storedTheme === "light" ? "light" : "dark";
  applyTheme(initialTheme);
}

function bindThemeButtons() {
  const darkButton = document.getElementById("themeDarkBtn");
  const lightButton = document.getElementById("themeLightBtn");

  darkButton.addEventListener("click", () => setTheme("dark"));
  lightButton.addEventListener("click", () => setTheme("light"));
}

async function refreshAccounts() {
  const accounts = await request("/accounts");
  state.accounts = accounts;
  renderAccountsTable(accounts);
  mountTransactionForms(accounts);
  bindTransactionForms({ onExpenseSubmit, onIncomeSubmit, onTransferSubmit });
}

async function refreshDebts() {
  const debts = await request("/debts");
  renderDebtsTable(debts);
}

async function refreshAnalytics() {
  const anchorDate = today();
  const summary = await request(`/analytics/summary?period=month&anchor_date=${anchorDate}`);
  const byCategory = await request(`/analytics/by-category?period=month&anchor_date=${anchorDate}`);
  const budget = await request(`/budgets/monthly/${state.month}/comparison`);

  renderAnalytics(summary, byCategory, budget);
  renderKpis(state.accounts, summary);
}

async function refreshAll() {
  await refreshAccounts();
  await refreshDebts();
  await refreshAnalytics();
}

async function refreshCoreData() {
  await refreshAccounts();
  await refreshDebts();
}

async function onAccountSubmit(event) {
  event.preventDefault();
  try {
    const payload = formDataAsJson(event.target);
    payload.initial_balance = Number(payload.initial_balance);
    await request("/accounts", { method: "POST", body: JSON.stringify(payload) });
    event.target.reset();
    toast("Account created");
    log("Account created", payload);
    await refreshAll();
  } catch (error) {
    toast(`Account error: ${error.message}`, "error");
    log(`Account error: ${error.message}`);
  }
}

async function onExpenseSubmit(event) {
  event.preventDefault();
  try {
    const payload = formDataAsJson(event.target);
    payload.amount = Number(payload.amount);
    await request("/expenses", { method: "POST", body: JSON.stringify(payload) });
    toast("Expense added");
    log("Expense added", payload);
    await refreshAll();
  } catch (error) {
    toast(`Expense error: ${error.message}`, "error");
    log(`Expense error: ${error.message}`);
  }
}

async function onIncomeSubmit(event) {
  event.preventDefault();
  try {
    const payload = formDataAsJson(event.target);
    payload.amount = Number(payload.amount);
    await request("/incomes", { method: "POST", body: JSON.stringify(payload) });
    toast("Income added");
    log("Income added", payload);
    await refreshAll();
  } catch (error) {
    toast(`Income error: ${error.message}`, "error");
    log(`Income error: ${error.message}`);
  }
}

async function onTransferSubmit(event) {
  event.preventDefault();
  try {
    const payload = formDataAsJson(event.target);
    payload.amount = Number(payload.amount);
    if (payload.exchange_rate) {
      payload.exchange_rate = Number(payload.exchange_rate);
    }
    await request("/transfers", { method: "POST", body: JSON.stringify(payload) });
    toast("Transfer completed");
    log("Transfer completed", payload);
    await refreshAll();
  } catch (error) {
    toast(`Transfer error: ${error.message}`, "error");
    log(`Transfer error: ${error.message}`);
  }
}

async function onDebtSubmit(event) {
  event.preventDefault();
  try {
    const payload = formDataAsJson(event.target);
    payload.amount = Number(payload.amount);
    await request("/debts", { method: "POST", body: JSON.stringify(payload) });
    event.target.reset();
    toast("Debt record created");
    log("Debt created", payload);
    await refreshDebts();
  } catch (error) {
    toast(`Debt error: ${error.message}`, "error");
    log(`Debt error: ${error.message}`);
  }
}

async function onBudgetSubmit(event) {
  event.preventDefault();
  try {
    const payload = formDataAsJson(event.target);
    payload.income_target = Number(payload.income_target);
    state.month = payload.month;
    await request("/budgets/monthly-income", { method: "POST", body: JSON.stringify(payload) });
    toast("Monthly budget saved");
    log("Monthly budget saved", payload);
    await refreshAnalytics();
  } catch (error) {
    toast(`Budget error: ${error.message}`, "error");
    log(`Budget error: ${error.message}`);
  }
}

async function onCategoryLimitSubmit(event) {
  event.preventDefault();
  try {
    const payload = formDataAsJson(event.target);
    payload.limit = Number(payload.limit);
    state.month = payload.month;
    await request("/budgets/category-limits", { method: "POST", body: JSON.stringify(payload) });
    toast("Category limit saved");
    log("Category limit saved", payload);
    await refreshAnalytics();
  } catch (error) {
    toast(`Category limit error: ${error.message}`, "error");
    log(`Category limit error: ${error.message}`);
  }
}

async function onRefreshAnalytics() {
  try {
    await refreshAnalytics();
    toast("Insights refreshed");
    log("Insights refreshed");
  } catch (error) {
    document.getElementById("summaryBox").textContent = "Insights are temporarily unavailable.";
    document.getElementById("categoryBox").textContent = "Insights are temporarily unavailable.";
    document.getElementById("budgetBox").textContent = "Insights are temporarily unavailable.";
    toast(`Insights error: ${error.message}`, "error");
    log(`Insights error: ${error.message}`);
  }
}

async function onApplyApiUrl() {
  const input = document.getElementById("apiBaseUrl");
  setApiBase(input.value.trim());
  try {
    await refreshAll();
    toast("API endpoint applied");
    log(`API endpoint set: ${getApiBase()}`);
  } catch (error) {
    toast(`Connection failed: ${error.message}`, "error");
    log(`Connection failed: ${error.message}`);
  }
}

async function connectApiWithFallback(initialValue) {
  const hostPort8000 = `${window.location.protocol}//${window.location.hostname}:8000`;
  const candidates = [...new Set([initialValue, "", hostPort8000].map((value) => (value || "").trim()))];

  let lastError = null;
  const maxAttempts = 10;
  for (let attempt = 1; attempt <= maxAttempts; attempt += 1) {
    for (const candidate of candidates) {
      setApiBase(candidate);
      try {
        await refreshCoreData();
        return candidate;
      } catch (error) {
        lastError = error;
      }
    }
    await new Promise((resolve) => setTimeout(resolve, 800));
  }

  throw lastError || new Error("Unable to connect to API");
}

async function loadAnalyticsSafely() {
  try {
    await refreshAnalytics();
  } catch (error) {
    document.getElementById("summaryBox").textContent = "Insights are temporarily unavailable.";
    document.getElementById("categoryBox").textContent = "Insights are temporarily unavailable.";
    document.getElementById("budgetBox").textContent = "Insights are temporarily unavailable.";
    toast(`Insights unavailable: ${error.message}`, "error");
    log(`Insights unavailable on startup: ${error.message}`);
  }
}

async function loadBrandingMetadata() {
  try {
    const meta = await request("/meta");
    const brandName = document.getElementById("brandName");
    const brandChip = document.getElementById("brandChip");
    const heroSubtitle = document.getElementById("heroSubtitle");

    if (brandName && meta.group) {
      brandName.textContent = meta.group;
    }
    if (brandChip && meta.group) {
      brandChip.textContent = `Group: ${meta.group}`;
    }
    if (heroSubtitle && meta.app_name) {
      heroSubtitle.textContent = `${meta.app_name} powers your day-to-day financial operations.`;
    }
    if (meta.group) {
      document.title = `${meta.group} Finance Control Room`;
    }
  } catch (error) {
    log(`Brand metadata unavailable: ${error.message}`);
  }
}

async function bootstrap() {
  const input = document.getElementById("apiBaseUrl");
  const monthA = document.querySelector("#budgetForm [name='month']");
  const monthB = document.querySelector("#categoryLimitForm [name='month']");
  monthA.value = state.month;
  monthB.value = state.month;

  mountCategoryLimitOptions();
  initTheme();
  bindThemeButtons();
  bindSettingsPanel();

  bindStaticForms({
    onAccountSubmit,
    onDebtSubmit,
    onBudgetSubmit,
    onCategoryLimitSubmit,
    onRefreshAnalytics,
    onApplyApiUrl,
  });

  const selectedApi = await connectApiWithFallback(input.value.trim());
  input.value = selectedApi;
  if (!selectedApi) {
    log("API endpoint selected: same-origin proxy");
  } else {
    log(`API endpoint selected: ${selectedApi}`);
  }
  await loadAnalyticsSafely();
  await loadBrandingMetadata();
}

bootstrap().catch((error) => {
  toast(`Initialization failed: ${error.message}`, "error");
  log(`Initialization failed: ${error.message}`);
});
