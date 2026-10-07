const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];

let plan = null;
let recipes = [];

// ---------- helpers ----------
async function api(path, opts = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined,
  });
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error(data?.detail?.[0]?.msg || data?.detail || `Request failed (${res.status})`);
  return data;
}

function toast(msg) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => t.classList.remove("show"), 3200);
}

function store(key, value) {
  try {
    if (value === undefined) return JSON.parse(localStorage.getItem(key));
    localStorage.setItem(key, JSON.stringify(value));
  } catch { return null; }
}

function busy(btn, label) {
  btn.disabled = true;
  btn.dataset.label = btn.textContent;
  btn.innerHTML = `<span class="spinner"></span>${label}`;
  return () => { btn.disabled = false; btn.textContent = btn.dataset.label; };
}

const fmtQty = (q) => {
  if (q == null) return "";
  const whole = Math.floor(q), frac = q - whole;
  const fracs = [[0.25, "¼"], [0.33, "⅓"], [0.5, "½"], [0.67, "⅔"], [0.75, "¾"]];
  const f = fracs.find(([v]) => Math.abs(frac - v) < 0.04);
  if (frac < 0.04) return String(whole);
  return f ? `${whole || ""}${f[1]}` : q.toFixed(2).replace(/0+$/, "");
};

function recipeDetails(r, scaleTo) {
  const scale = scaleTo && r.servings ? scaleTo / r.servings : 1;
  const el = document.createElement("div");
  const ings = r.ingredients.map((i) => {
    const q = i.qty == null ? "" : fmtQty(i.qty * scale);
    const li = document.createElement("li");
    li.textContent = [q, i.unit, i.item].filter(Boolean).join(" ") + (i.note ? `, ${i.note}` : "");
    return li.outerHTML;
  }).join("");
  const steps = r.steps.map((s) => { const li = document.createElement("li"); li.textContent = s; return li.outerHTML; }).join("");
  el.innerHTML = `
    ${r.description ? `<p></p>` : ""}
    <h4>Ingredients${scaleTo ? ` (for ${scaleTo})` : ` (serves ${r.servings})`}</h4><ul>${ings}</ul>
    <h4>Steps</h4><ol>${steps}</ol>`;
  if (r.description) el.querySelector("p").textContent = r.description;
  if (r.source_url) {
    const a = document.createElement("a");
    a.href = r.source_url; a.target = "_blank"; a.rel = "noopener"; a.textContent = "Original recipe ↗";
    const p = document.createElement("p"); p.append(a); el.append(p);
  }
  return el.innerHTML;
}

const metaLine = (r) => [`${r.total_minutes} min`, r.cuisine, r.protein].filter(Boolean).join(" · ");

// ---------- tabs ----------
$$(".tabs button").forEach((b) => b.addEventListener("click", () => {
  $$(".tabs button").forEach((x) => x.classList.toggle("active", x === b));
  $("#tab-week").hidden = b.dataset.tab !== "week";
  $("#tab-recipes").hidden = b.dataset.tab !== "recipes";
  if (b.dataset.tab === "recipes") loadRecipes();
}));

// ---------- plan form ----------
const savedDays = store("menubot.days") || ["Monday", "Tuesday", "Thursday", "Friday"];
$("#day-chips").innerHTML = DAYS.map((d) =>
  `<button type="button" data-day="${d}" class="${savedDays.includes(d) ? "on" : ""}">${d.slice(0, 3)}</button>`).join("");
$$("#day-chips button").forEach((b) => b.addEventListener("click", () => b.classList.toggle("on")));
$("#servings").value = store("menubot.servings") || 2;
$$(".stepper button").forEach((b) => b.addEventListener("click", () => {
  const input = $("#servings");
  input.value = Math.min(12, Math.max(1, Number(input.value) + Number(b.dataset.step)));
}));

$("#plan-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const days = $$("#day-chips button.on").map((b) => b.dataset.day);
  if (!days.length) return toast("Pick at least one night.");
  const servings = Number($("#servings").value) || 2;
  store("menubot.days", days);
  store("menubot.servings", servings);
  const done = busy(e.submitter || $("#plan-form .primary"), "Thinking about dinner…");
  try {
    plan = await api("/api/plans", { method: "POST", body: { days, servings, prompt: $("#prompt").value } });
    showPlan();
  } catch (err) {
    toast(err.message);
  } finally { done(); }
});

$("#new-plan").addEventListener("click", () => {
  $("#prompt").value = plan?.prompt || "";
  $("#plan-view").hidden = true;
  $("#plan-form").hidden = false;
  $("#cancel-new").hidden = !plan;
});
$("#cancel-new").addEventListener("click", showPlan);

// ---------- plan view ----------
function showPlan() {
  $("#plan-form").hidden = true;
  $("#shopping-view").hidden = true;
  $("#plan-view").hidden = false;
  renderPlan();
}

function renderPlan() {
  $("#plan-prompt").textContent = plan.prompt;
  $("#plan-prompt").hidden = !plan.prompt;
  const approved = plan.meals.filter((m) => m.approved).length;
  $("#plan-progress").textContent = `${approved} of ${plan.meals.length} approved · ${plan.servings} servings each`;
  const allDone = approved === plan.meals.length;
  $("#to-shopping").disabled = !allDone;
  $("#shopping-hint").hidden = allDone;

  const container = $("#meals");
  const openDetails = new Set($$(".meal", container).filter((c) => !$(".details", c).hidden).map((c) => c.dataset.day));
  container.innerHTML = "";
  for (const meal of plan.meals) container.append(mealCard(meal, openDetails.has(meal.day)));
}

function mealCard(meal, detailsOpen) {
  const node = $("#meal-tpl").content.firstElementChild.cloneNode(true);
  const r = meal.recipe;
  node.dataset.day = meal.day;
  node.classList.toggle("approved", meal.approved);
  $(".day", node).textContent = meal.day;
  $(".title", node).textContent = r.title;
  $(".meta", node).textContent = metaLine(r);
  $(".reason", node).textContent = meal.reason;
  $(".approve", node).textContent = meal.approved ? "Approved" : "Looks good";

  const details = $(".details", node);
  details.innerHTML = recipeDetails(r, plan.servings);
  details.hidden = !detailsOpen;
  $(".details-btn", node).textContent = detailsOpen ? "Hide" : "Recipe";
  $(".details-btn", node).addEventListener("click", (e) => {
    details.hidden = !details.hidden;
    e.target.textContent = details.hidden ? "Recipe" : "Hide";
  });

  $(".approve", node).addEventListener("click", async () => {
    try {
      plan = await api(`/api/plans/${plan.id}/meals/${meal.day}/approve`, { method: "POST", body: { approved: !meal.approved } });
      renderPlan();
    } catch (err) { toast(err.message); }
  });

  const swapForm = $(".swap-form", node);
  $(".swap", node).addEventListener("click", () => {
    swapForm.hidden = !swapForm.hidden;
    if (!swapForm.hidden) $("input", swapForm).focus();
  });
  swapForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    node.classList.add("loading");
    const done = busy($("button", swapForm), "Finding…");
    try {
      plan = await api(`/api/plans/${plan.id}/meals/${meal.day}/swap`, {
        method: "POST", body: { feedback: $("input", swapForm).value },
      });
      renderPlan();
      toast(`New pick for ${meal.day}`);
    } catch (err) {
      toast(err.message);
      node.classList.remove("loading");
      done();
    }
  });
  return node;
}

// ---------- shopping list ----------
$("#to-shopping").addEventListener("click", showShopping);
$("#back-to-plan").addEventListener("click", showPlan);

let shoppingText = "";
async function showShopping() {
  const list = await api(`/api/plans/${plan.id}/shopping-list`).catch((e) => toast(e.message));
  if (!list) return;
  shoppingText = list.text;
  $("#plan-view").hidden = true;
  $("#shopping-view").hidden = false;
  $("#share-list").hidden = !navigator.share;

  const key = `menubot.checked.${plan.id}`;
  const checked = new Set(store(key) || []);
  const groups = [...list.aisles.map((g) => [g.aisle, g.items])];
  if (list.staples.length) groups.push(["Check the pantry", list.staples]);

  const root = $("#shopping");
  root.innerHTML = "";
  for (const [name, items] of groups) {
    const card = document.createElement("div");
    card.className = "card aisle";
    const h = document.createElement("h3");
    h.textContent = name;
    card.append(h);
    for (const it of items) {
      const row = document.createElement("label");
      row.className = "item";
      row.title = `For: ${it.recipes.join(", ")}`;
      row.innerHTML = `<input type="checkbox"><div><div class="name"></div><div class="amt"></div></div>`;
      $(".name", row).textContent = it.item;
      $(".amt", row).textContent = name === "Check the pantry" ? it.recipes.join(", ") : it.amount;
      const box = $("input", row);
      box.checked = checked.has(it.item);
      row.classList.toggle("done", box.checked);
      box.addEventListener("change", () => {
        box.checked ? checked.add(it.item) : checked.delete(it.item);
        row.classList.toggle("done", box.checked);
        store(key, [...checked]);
      });
      card.append(row);
    }
    root.append(card);
  }
}

$("#copy-list").addEventListener("click", async () => {
  try { await navigator.clipboard.writeText(shoppingText); toast("Copied!"); }
  catch { toast("Couldn't copy. Long-press to select instead."); }
});
$("#share-list").addEventListener("click", () => navigator.share({ title: "Grocery list", text: shoppingText }).catch(() => {}));

// ---------- recipes tab ----------
let importMode = "url";
$$(".seg button").forEach((b) => b.addEventListener("click", () => {
  importMode = b.dataset.mode;
  $$(".seg button").forEach((x) => x.classList.toggle("active", x === b));
  $("#import-url").hidden = importMode !== "url";
  $("#import-text").hidden = importMode !== "text";
}));

$("#import-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = importMode === "url" ? { url: $("#import-url").value } : { text: $("#import-text").value };
  if (!(body.url || body.text || "").trim()) return toast("Add a link or paste a recipe first.");
  const done = busy(e.submitter || $("#import-form .primary"), "Reading recipe…");
  try {
    const r = await api("/api/recipes/import", { method: "POST", body });
    $("#import-url").value = ""; $("#import-text").value = "";
    toast(`Added “${r.title}”`);
    await loadRecipes(true);
  } catch (err) { toast(err.message); }
  finally { done(); }
});

async function loadRecipes(force) {
  if (!recipes.length || force) recipes = await api("/api/recipes");
  renderRecipes();
}

$("#search").addEventListener("input", renderRecipes);

function renderRecipes() {
  const q = $("#search").value.trim().toLowerCase();
  const match = (r) => !q || [r.title, r.cuisine, r.protein, ...r.tags, ...r.ingredients.map((i) => i.item)]
    .some((s) => s.toLowerCase().includes(q));
  const shown = recipes.filter(match);
  $("#recipe-count").textContent = `${shown.length} of ${recipes.length} recipes`;
  const list = $("#recipe-list");
  list.innerHTML = "";
  for (const r of shown) {
    const card = document.createElement("article");
    card.className = "card recipe";
    card.innerHTML = `<div class="head"><h3></h3><span class="badge"></span></div><p class="muted"></p><div class="details" hidden></div>`;
    $("h3", card).textContent = r.title;
    $(".badge", card).textContent = r.source;
    $("p", card).textContent = metaLine(r) + (r.tags.length ? ` · ${r.tags.join(", ")}` : "");
    const details = $(".details", card);
    card.addEventListener("click", (e) => {
      if (e.target.closest("a, button")) return;
      if (!details.innerHTML) {
        details.innerHTML = recipeDetails(r);
        if (r.source !== "seed") {
          const del = document.createElement("button");
          del.className = "link danger"; del.textContent = "Delete recipe";
          del.addEventListener("click", async () => {
            if (!confirm(`Delete “${r.title}”?`)) return;
            try { await api(`/api/recipes/${r.id}`, { method: "DELETE" }); await loadRecipes(true); }
            catch (err) { toast(err.message); }
          });
          details.append(del);
        }
      }
      details.hidden = !details.hidden;
    });
    list.append(card);
  }
}

// ---------- boot ----------
(async function init() {
  api("/api/status").then((s) => {
    const pill = $("#status");
    pill.textContent = s.claude ? "Claude on" : "Offline mode";
    pill.classList.toggle("on", s.claude);
    pill.title = s.claude ? `Using ${s.model}` : "No API key set: picks are random within your filters";
  }).catch(() => {});
  plan = await api("/api/plans/latest").catch(() => null);
  if (plan) showPlan();
  else $("#plan-form").hidden = false;
})();
