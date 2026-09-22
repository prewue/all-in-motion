# Catalog · Data, tables and disclosure

Tables are the hardest surface to animate well: rows are dense, frequently scanned, and the user is reading data rather than watching it. The rule for this whole family is that **the data never moves for style**. Motion here only ever does three things: keep a row's identity while the order changes, show that a row has more inside it, and reveal a control the user asked for.

Everything below animates `transform`, `opacity` and `grid-template-rows` only. Nothing reflows the table while the user reads it.

---

## 1. Data table — sort, insert, remove

Tier: tens/day. **Purpose**: continuity. When the sort changes, each row keeps its identity by travelling to its new position instead of teleporting. That is a FLIP: measure, reorder, invert, play.

Rows never fade in place during a sort. A fade says "different data"; a travel says "same data, new order."

```html
<table class="aim-table">
  <thead>
    <tr>
      <th><button class="aim-th" data-sort="name" aria-sort="ascending">Name <span class="aim-th-caret"></span></button></th>
      <th><button class="aim-th" data-sort="role">Role <span class="aim-th-caret"></span></button></th>
      <th class="num"><button class="aim-th" data-sort="commits">Commits <span class="aim-th-caret"></span></button></th>
    </tr>
  </thead>
  <tbody><!-- rows --></tbody>
</table>
```

```css
.aim-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.aim-table th, .aim-table td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--s-line); }
.aim-table .num, .aim-table td.num { text-align: right; font-variant-numeric: tabular-nums; }

/* Header cell: the caret is the only thing that moves, and only on the active column. */
.aim-th { display: inline-flex; align-items: center; gap: 6px; border: 0; background: transparent; color: var(--s-muted);
  font: inherit; font-weight: 500; padding: 0; cursor: pointer;
  transition: color var(--motion-quick) var(--ease-out); }
.aim-th:hover, .aim-th[aria-sort] { color: var(--s-fg); }
.aim-th-caret { width: 8px; height: 8px; opacity: 0;
  background: currentColor; clip-path: polygon(50% 0, 100% 100%, 0 100%);
  transition: opacity var(--motion-quick) var(--ease-out), transform var(--motion-fast) var(--ease-out); }
.aim-th[aria-sort] .aim-th-caret { opacity: 1; }
.aim-th[aria-sort="descending"] .aim-th-caret { transform: rotate(180deg); }

/* Rows: the travel is applied by JS as a FLIP; CSS only owns the resting state
   and the enter/leave of rows that genuinely arrive or depart. */
.aim-table tbody tr { transition: background-color var(--spring-hover-duration) var(--spring-hover-easing); }
@media (hover: hover) and (pointer: fine) { .aim-table tbody tr:hover { background: var(--s-bg2); } }
.aim-table tbody tr.is-entering { animation: aim-row-in var(--motion-fast) var(--ease-out) both; }
.aim-table tbody tr.is-leaving { animation: aim-row-out var(--motion-quick) var(--ease-out) both; pointer-events: none; }
@keyframes aim-row-in  { from { opacity: 0; transform: translateY(var(--move-small)); } }
@keyframes aim-row-out { to   { opacity: 0; transform: translateY(calc(var(--move-micro) * -1)); } }

@media (prefers-reduced-motion: reduce) {
  .aim-table tbody tr.is-entering, .aim-table tbody tr.is-leaving { animation: none; }
  .aim-th-caret { transition: opacity var(--motion-quick) var(--ease-out); }
}
```

```js
// FLIP over the rows: measure before the DOM changes, invert after, then release.
// Only rows whose position actually changed get an animation.
function flipRows(tbody, mutate) {
  const rows = [...tbody.rows];
  const first = new Map(rows.map((r) => [r, r.getBoundingClientRect().top]));
  mutate();
  if (AIM.reduced) return;
  for (const r of tbody.rows) {
    const before = first.get(r);
    if (before === undefined) continue;                 // a newly inserted row: it enters instead
    const delta = before - r.getBoundingClientRect().top;
    if (!delta) continue;                                // unchanged position: no animation at all
    r.animate(
      [{ transform: `translateY(${delta}px)` }, { transform: "none" }],
      { duration: 250, easing: "cubic-bezier(0.22, 1, 0.36, 1)" }
    );
  }
}

function sortBy(tbody, key, dir) {
  flipRows(tbody, () => {
    [...tbody.rows]
      .sort((a, b) => {
        const x = a.dataset[key], y = b.dataset[key];
        const n = Number(x) - Number(y);
        return (Number.isNaN(n) ? String(x).localeCompare(String(y)) : n) * dir;
      })
      .forEach((r) => tbody.appendChild(r));
  });
}

function removeRow(tbody, row) {
  row.classList.add("is-leaving");
  row.addEventListener("animationend", () => flipRows(tbody, () => row.remove()), { once: true });
}
```

Notes:
- Cap the FLIP at what is on screen. Animating 500 offscreen rows costs layout for nothing; check `getBoundingClientRect()` against the viewport first, or only animate rows inside a virtualised window.
- `aria-sort` on the active header is what a screen reader announces. The caret is decoration on top of it.
- Do not stagger the rows. A sort is one event, not a sequence; staggering it makes a 250ms reorder read as a second of churn.

---

## 2. Expandable table row

Tier: tens/day. **Purpose**: state indication plus preventing a jarring change. The detail opens *inside* the table, so nothing below it jumps by more than the panel's own height.

The row that expands is a real `<tr>` carrying a full-width cell. The height animates through `grid-template-rows: 0fr ↔ 1fr`, so there is no JS measurement and content of any size works. Padding lives on the inner element, never on the `0fr` track, or the panel keeps a residual strip and never closes.

```html
<tbody>
  <tr class="aim-trow" data-open="false">
    <td><button class="aim-trow-toggle" aria-expanded="false" aria-controls="d-1">
      <span class="aim-trow-chevron" aria-hidden="true">
        <svg viewBox="0 0 16 16" width="12" height="12" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6.5L8 10.5L12 6.5"/></svg>
      </span>Ostrovska</button></td>
    <td>Design engineer</td>
    <td class="num">412</td>
  </tr>
  <tr class="aim-trow-detail" id="d-1">
    <td colspan="3"><div class="aim-trow-panel"><div class="aim-trow-inner">
      Joined March 2024 · last active 2 hours ago · 12 open reviews
    </div></div></td>
  </tr>
</tbody>
```

```css
/* The detail row's cell has no padding of its own: the grid track must be able
   to collapse to zero. All padding sits on .aim-trow-inner. */
.aim-trow-detail > td { padding: 0; border-bottom: 0; }
.aim-trow-panel { display: grid; grid-template-rows: 0fr; transition: grid-template-rows var(--motion-fast) var(--ease-out); }
.aim-trow[data-open="true"] + .aim-trow-detail .aim-trow-panel { grid-template-rows: 1fr; }
.aim-trow-inner { overflow: hidden; opacity: 0; font-size: 12px; color: var(--s-muted);
  transition: opacity var(--motion-fast) var(--ease-out); }
.aim-trow-inner > * { padding: 0 12px 11px 30px; margin: 0; }
.aim-trow[data-open="true"] + .aim-trow-detail .aim-trow-inner { opacity: 1; }
/* The open row loses its bottom rule so the row and its detail read as one block. */
.aim-trow[data-open="true"] > td { border-bottom-color: transparent; }

.aim-trow-toggle { display: inline-flex; align-items: center; gap: 6px; border: 0; background: transparent; color: inherit; font: inherit; font-weight: 500; padding: 0; cursor: pointer; }
.aim-trow-chevron { display: inline-flex; color: var(--s-muted); transform: rotate(-90deg); transform-origin: center;
  transition: transform var(--motion-fast) var(--ease-out); }
.aim-trow[data-open="true"] .aim-trow-chevron { transform: rotate(0deg); }

@media (prefers-reduced-motion: reduce) {
  .aim-trow-panel, .aim-trow-inner, .aim-trow-chevron { transition: none; }
}
```

```js
function wireExpandableRows(tbody) {
  tbody.querySelectorAll(".aim-trow-toggle").forEach((btn) => {
    const row = btn.closest(".aim-trow");
    btn.addEventListener("click", () => {
      const open = row.dataset.open !== "true";
      row.dataset.open = String(open);
      btn.setAttribute("aria-expanded", String(open));
    });
  });
}
```

Notes:
- One row open at a time is a product decision, not a motion one. If you enforce it, close the previous row in the same frame so the two height changes share a clock and the page settles once.
- Chevron rotates rather than swapping glyphs: a rotation is one interpolated property, a glyph swap is two elements cross-fading.
- `aria-expanded` on the button and `aria-controls` pointing at the detail row are what make this navigable without sight. The chevron is decoration.

---

## 3. Expanding title with a search field

Tier: tens/day. **Purpose**: state indication. A section heading that reveals a search or filter field underneath it when asked, instead of permanently spending a row of vertical space on a control most visits never use.

The field is the only thing that animates. The heading does not move, because the heading is what the user is reading.

```html
<div class="aim-titlebar" data-open="false">
  <div class="aim-titlebar-head">
    <h4 class="aim-titlebar-title">Team members <span class="aim-titlebar-count">24</span></h4>
    <button class="aim-titlebar-btn" aria-expanded="false" aria-controls="tb-search" aria-label="Search members">
      <span class="aim-iconswap" data-state="a">
        <span class="aim-icon" data-icon="a">⌕</span>
        <span class="aim-icon" data-icon="b">✕</span>
      </span>
    </button>
  </div>
  <div class="aim-titlebar-reveal" id="tb-search">
    <div class="aim-titlebar-inner">
      <input type="search" class="aim-titlebar-input" placeholder="Filter by name or role">
    </div>
  </div>
</div>
```

```css
.aim-titlebar-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.aim-titlebar-title { margin: 0; font-size: 14px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.aim-titlebar-count { font-size: 12px; font-weight: 500; color: var(--s-muted); font-variant-numeric: tabular-nums; }
.aim-titlebar-btn { width: 28px; height: 28px; display: grid; place-items: center; border: 1px solid transparent; border-radius: 7px;
  background: transparent; color: var(--s-muted); font-size: 15px; cursor: pointer;
  transition: background-color var(--spring-hover-duration) var(--spring-hover-easing), color var(--spring-hover-duration) var(--spring-hover-easing); }
.aim-titlebar-btn:hover, .aim-titlebar[data-open="true"] .aim-titlebar-btn { background: var(--s-bg2); color: var(--s-fg); }

/* Same 0fr↔1fr disclosure as the table row: no height measurement, any content size. */
.aim-titlebar-reveal { display: grid; grid-template-rows: 0fr; transition: grid-template-rows var(--motion-fast) var(--ease-out); }
.aim-titlebar[data-open="true"] .aim-titlebar-reveal { grid-template-rows: 1fr; }
.aim-titlebar-inner { overflow: hidden; }
.aim-titlebar-input { width: 100%; margin-top: 10px; padding: 7px 10px; border: 1px solid var(--s-line); border-radius: 8px;
  background: var(--s-bg); color: var(--s-fg); font: inherit; font-size: 13px; outline: none;
  /* The field itself arrives with the panel: a short lift plus fade, so it reads
     as one surface opening rather than a box growing around a static input. */
  opacity: 0; transform: translateY(calc(var(--move-micro) * -1));
  transition: opacity var(--motion-fast) var(--ease-out), transform var(--motion-fast) var(--ease-out),
              border-color var(--motion-quick) var(--ease-out); }
.aim-titlebar[data-open="true"] .aim-titlebar-input { opacity: 1; transform: none; }
.aim-titlebar-input:focus { border-color: var(--s-fg); }

@media (prefers-reduced-motion: reduce) {
  .aim-titlebar-reveal, .aim-titlebar-input { transition: opacity var(--motion-quick) var(--ease-out); }
  .aim-titlebar-input { transform: none; }
}
```

```js
function wireTitleSearch(bar, { onQuery } = {}) {
  const btn = bar.querySelector(".aim-titlebar-btn");
  const input = bar.querySelector(".aim-titlebar-input");
  const swap = bar.querySelector(".aim-iconswap");

  const setOpen = (open) => {
    bar.dataset.open = String(open);
    btn.setAttribute("aria-expanded", String(open));
    swap.dataset.state = open ? "b" : "a";
    if (open) input.focus();
    else { input.value = ""; onQuery?.(""); }
  };

  btn.addEventListener("click", () => setOpen(bar.dataset.open !== "true"));
  input.addEventListener("input", () => onQuery?.(input.value));
  // Escape closes and hands focus back to the button, the same contract as a popover.
  input.addEventListener("keydown", (e) => { if (e.key === "Escape") { setOpen(false); btn.focus(); } });
}
```

Notes:
- Focus moves into the field on open. A search control that appears but does not accept typing is a control the user has to click twice.
- Clearing on close is deliberate: leaving a stale filter applied behind a collapsed field hides rows for reasons the user can no longer see.
- The icon swap between the magnifier and the close glyph is the standard icon swap recipe; it costs one attribute.
- Pair this with the data table above: filtering rows should go through the same FLIP, so rows that survive the filter travel rather than blink.
