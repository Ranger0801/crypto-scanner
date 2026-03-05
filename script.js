// ─────────────────────────────────────────────
// script.js — Crypto Signal Scanner Frontend
// ─────────────────────────────────────────────

const API = "";  // same origin

// ── Utility ──────────────────────────────────

function fmt(val, decimals = 2, prefix = "") {
  if (val == null) return "—";
  return prefix + Number(val).toFixed(decimals);
}

function fmtPrice(price) {
  if (price == null) return "—";
  if (price >= 1000) return "$" + price.toLocaleString("en-US", {maximumFractionDigits: 2});
  if (price >= 1)    return "$" + price.toFixed(4);
  return "$" + price.toFixed(8);
}

function fmtChange(change) {
  if (change == null) return "—";
  const sign = change >= 0 ? "+" : "";
  return sign + change.toFixed(2) + "%";
}

function badge(direction) {
  const cls = {bullish: "badge-bullish", bearish: "badge-bearish", neutral: "badge-neutral"};
  return `<span class="badge ${cls[direction] || 'badge-neutral'}">${direction}</span>`;
}

function scorePill(score) {
  return `<span class="score-pill">${score}</span>`;
}

function ago(ts) {
  const d = new Date(ts + "Z");
  const diff = Math.floor((Date.now() - d) / 1000);
  if (diff < 60)    return `${diff}s ago`;
  if (diff < 3600)  return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

async function apiFetch(path) {
  const r = await fetch(API + path);
  if (!r.ok) throw new Error(`API error ${r.status}`);
  return r.json();
}

// ── Signal Table ──────────────────────────────

function signalTableHTML(signals) {
  if (!signals.length) return `<div class="empty">No signals found.</div>`;
  const rows = signals.map(s => `
    <tr onclick="location.href='/coin/${s.coin}'">
      <td><strong>${s.coin}</strong></td>
      <td>${s.signal_type}</td>
      <td>${badge(s.direction)}</td>
      <td>${s.timeframe}</td>
      <td>${scorePill(s.score)}</td>
      <td>${ago(s.timestamp)}</td>
    </tr>
  `).join("");

  return `
    <table class="signal-table">
      <thead><tr>
        <th>Coin</th><th>Signal</th><th>Direction</th>
        <th>Timeframe</th><th>Score</th><th>Time</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table>`;
}

// ── Dashboard ─────────────────────────────────

async function loadDashboard() {
  try {
    const [overview, strong, signals, gainers, losers] = await Promise.all([
      apiFetch("/api/market_overview"),
      apiFetch("/api/strong_signals"),
      apiFetch("/api/signals?limit=30"),
      apiFetch("/api/top_gainers"),
      apiFetch("/api/top_losers"),
    ]);

    // Stats
    const sc = overview.signal_counts;
    document.querySelector("#stat-total   .stat-number").textContent = sc.total;
    document.querySelector("#stat-bullish .stat-number").textContent = sc.bullish;
    document.querySelector("#stat-bearish .stat-number").textContent = sc.bearish;
    document.querySelector("#stat-strong  .stat-number").textContent = strong.length;

    // Strong signals grid
    document.getElementById("strong-signals").innerHTML = strong.length
      ? strong.map(s => `
          <div class="signal-card ${s.direction}" onclick="location.href='/coin/${s.coin}'">
            <div class="coin-sym">${s.coin} ${scorePill(s.score)}</div>
            <div class="sig-type">${s.signal_type}</div>
            <div>${badge(s.direction)}</div>
            <div class="sig-meta">${s.timeframe} · ${ago(s.timestamp)}</div>
          </div>`).join("")
      : `<div class="empty">No strong signals in the last 24h.</div>`;

    // Latest signals table
    document.getElementById("latest-signals").innerHTML = signalTableHTML(signals);

    // Top gainers & losers
    function moverHTML(coins) {
      return coins.map(c => {
        const cls = (c.change_24h || 0) >= 0 ? "up" : "down";
        return `<div class="mover-row" onclick="location.href='/coin/${c.symbol}'">
          <span class="mover-sym">${c.symbol}</span>
          <span>${fmtPrice(c.price)}</span>
          <span class="mover-change ${cls}">${fmtChange(c.change_24h)}</span>
        </div>`;
      }).join("");
    }
    document.getElementById("top-gainers").innerHTML = moverHTML(gainers);
    document.getElementById("top-losers").innerHTML  = moverHTML(losers);

    // Attach filter handlers
    ["filter-timeframe", "filter-direction"].forEach(id => {
      document.getElementById(id)?.addEventListener("change", loadFilteredSignals);
    });

  } catch (err) {
    console.error(err);
  }
}

async function loadFilteredSignals() {
  const tf  = document.getElementById("filter-timeframe")?.value || "";
  const dir = document.getElementById("filter-direction")?.value || "";
  const params = new URLSearchParams({ limit: 50 });
  if (tf)  params.append("timeframe",  tf);
  if (dir) params.append("direction",  dir);

  try {
    const signals = await apiFetch(`/api/signals?${params}`);
    document.getElementById("latest-signals").innerHTML = signalTableHTML(signals);
  } catch (err) { console.error(err); }
}

// ── Scanner Page ──────────────────────────────

async function loadScanner() {
  const tf    = document.getElementById("filter-timeframe")?.value || "";
  const dir   = document.getElementById("filter-direction")?.value || "";
  const score = document.getElementById("filter-score")?.value || "0";
  const params = new URLSearchParams({ limit: 100, min_score: score });
  if (tf)  params.append("timeframe",  tf);
  if (dir) params.append("direction",  dir);

  try {
    const signals = await apiFetch(`/api/signals?${params}`);
    document.getElementById("scanner-results").innerHTML = signalTableHTML(signals);
  } catch (err) { console.error(err); }
}

// ── Coin Page ─────────────────────────────────

async function loadCoinPage(symbol) {
  try {
    const data = await apiFetch(`/api/coin/${symbol}`);
    const { coin, signals } = data;

    document.querySelector("#coin-price  .stat-number").textContent = fmtPrice(coin.price);
    document.querySelector("#coin-change .stat-number").textContent = fmtChange(coin.change_24h);
    document.querySelector("#coin-volume .stat-number").textContent = coin.volume_24h
      ? "$" + (coin.volume_24h / 1e6).toFixed(1) + "M" : "—";

    const chgEl = document.getElementById("coin-change");
    if ((coin.change_24h || 0) >= 0) chgEl.classList.add("bullish-card");
    else chgEl.classList.add("bearish-card");

    document.getElementById("coin-subtitle").textContent = coin.name;
    document.getElementById("coin-signals").innerHTML = signalTableHTML(signals);

  } catch (err) {
    console.error(err);
    document.getElementById("coin-signals").innerHTML = `<div class="empty">Could not load data.</div>`;
  }
}
