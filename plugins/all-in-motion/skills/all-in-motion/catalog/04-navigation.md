# Catalog · Navigation — tabs, pages, carousels, pickers

Rule for this whole family: these are *on-screen movements*, so they read as one reversible motion (symmetric timing, no split) and use `--ease-out` for slides / `--ease-in-out` for repositioning. Keyboard-driven tab switching in a tool is high-frequency: consider instant.

---

## 1. Tabs — sliding pill (segmented control)

Tier: tens/day → 250ms, no overshoot. JS writes the active tab's geometry; CSS owns the tween.

```html
<div class="aim-tabs" role="tablist">
  <span class="aim-tabs-pill" aria-hidden="true"></span>
  <button class="aim-tab" role="tab" aria-selected="true">Plan</button>
  <button class="aim-tab" role="tab" aria-selected="false">Build</button>
  <button class="aim-tab" role="tab" aria-selected="false">Ship</button>
</div>
```

```css
.aim-tabs { position: relative; display: inline-flex; gap: 3px; padding: 3px; border-radius: 999px; background: rgb(0 0 0 / 0.06); }
.aim-tab { position: relative; z-index: 1; border: 0; background: transparent; height: 30px; padding: 0 12px; border-radius: 999px; cursor: pointer; color: rgb(0 0 0 / 0.65); font-weight: 500;
  transition: color var(--motion-fast) var(--ease-out); }
.aim-tab[aria-selected="true"], .aim-tab:hover { color: #111; }
.aim-tabs-pill { position: absolute; top: 3px; left: 0; height: 30px; width: 0; border-radius: 999px; background: #fff; box-shadow: var(--shadow-rest); z-index: 0; pointer-events: none;
  /* motion-ok: the pill is measured from the active tab; width is the honest property */
  transform: translateX(0); transition: transform var(--motion-fast) var(--ease-out), width var(--motion-fast) var(--ease-out); will-change: transform, width; }
@media (prefers-reduced-motion: reduce) { .aim-tabs-pill, .aim-tab { transition: none; } }
```

```js
function wireTabs(bar, { animateKeyboard = false } = {}) {
  const pill = bar.querySelector(".aim-tabs-pill"), tabs = [...bar.querySelectorAll(".aim-tab")];
  const moveTo = (tab, animate) => {
    if (!animate) { const p = pill.style.transition; pill.style.transition = "none"; }
    pill.style.transform = `translateX(${tab.offsetLeft}px)`; pill.style.width = `${tab.offsetWidth}px`;
    if (!animate) { void pill.offsetWidth; pill.style.transition = ""; }   // first paint / resize: snap, never animate in from 0
  };
  const active = () => tabs.find((t) => t.getAttribute("aria-selected") === "true") || tabs[0];
  tabs.forEach((tab) => tab.addEventListener("click", (e) => {
    tabs.forEach((t) => t.setAttribute("aria-selected", String(t === tab)));
    moveTo(tab, animateKeyboard || e.detail !== 0);   // e.detail === 0 → keyboard activation → instant
  }));
  requestAnimationFrame(() => moveTo(active(), false));
  addEventListener("resize", () => moveTo(active(), false));
}
```

Spring version: `--spring-tab-select-*` on the pill. The pill's `width` transition is a deliberate exception (small element, occasional); a `scaleX` version avoids layout if the tabs are equal width.

---

## 2. Tabs — clip-path (colour and highlight in perfect sync)

When the highlight bar and the text colour keep drifting out of sync in slow motion: duplicate the tab list, style the copy as the active state, clip it to the active tab, animate the clip. Text and background are one element being revealed.

```html
<div class="aim-cliptabs">
  <div class="aim-cliptabs-row"><button>Plan</button><button>Build</button><button>Ship</button></div>
  <div class="aim-cliptabs-row aim-cliptabs-active" aria-hidden="true"><button tabindex="-1">Plan</button><button tabindex="-1">Build</button><button tabindex="-1">Ship</button></div>
</div>
```

```css
.aim-cliptabs { position: relative; display: inline-block; }
.aim-cliptabs-row { display: flex; gap: 0; }
.aim-cliptabs-row button { border: 0; background: transparent; padding: 6px 14px; color: rgb(0 0 0 / 0.6); cursor: pointer; }
.aim-cliptabs-active { position: absolute; inset: 0; background: #111; border-radius: 999px; pointer-events: none;
  clip-path: inset(0 var(--r, 66.6%) 0 var(--l, 0%) round 999px);
  transition: clip-path var(--motion-fast) var(--ease-in-out); }
.aim-cliptabs-active button { color: #fff; }
@media (prefers-reduced-motion: reduce) { .aim-cliptabs-active { transition: none; } }
```

```js
row.querySelectorAll("button").forEach((b, i, all) => b.addEventListener("click", () => {
  const w = row.offsetWidth; const l = b.offsetLeft / w * 100, r = 100 - (b.offsetLeft + b.offsetWidth) / w * 100;
  active.style.setProperty("--l", l + "%"); active.style.setProperty("--r", r + "%");
}));
```

---

## 3. Page side-by-side (list ↔ detail, wizard steps)

Tier: occasional. Symmetric 250ms. Page 1 exits left, page 2 exits right; 8px travel + 3px blur so the slide is felt, not watched.

```html
<div class="aim-pages" data-page="1">
  <section class="aim-page" data-id="1">…list…</section>
  <section class="aim-page" data-id="2">…detail…</section>
</div>
```

```css
.aim-pages { position: relative; }
.aim-page { position: absolute; inset: 0; opacity: 0; pointer-events: none;
  transform: translateX(calc(var(--from, 0px) * var(--exit, 1)));
  filter: blur(calc(var(--blur-medium) * var(--motion-blur-scale) * var(--exit, 1)));
  transition: opacity var(--motion-fast) var(--ease-out), transform var(--motion-fast) var(--ease-out), filter var(--motion-fast) var(--ease-out);
  will-change: opacity, transform, filter; }
.aim-page[data-id="1"] { --from: calc(var(--move-base) * -1); }
.aim-page[data-id="2"] { --from: var(--move-base); }
.aim-pages[data-page="1"] .aim-page[data-id="1"], .aim-pages[data-page="2"] .aim-page[data-id="2"] { opacity: 1; pointer-events: auto; transform: translateX(0); filter: blur(0); }
@media (prefers-reduced-motion: reduce) { .aim-page { transform: none; filter: none; } }
```

`--exit: 0` on the container disables the outgoing slide (useful on first paint). For a real router use the View Transitions API with the same values (`09-frameworks.md`). Direction should follow information architecture: forward slides left, back slides right.

---

## 4. Paged carousel with edge fades

Tier: occasional. Pages snap one at a time; while moving, both edges fade so what leaves goes into shadow instead of being cut; at rest the fade lingers then eases away.

```html
<div class="aim-carousel"><div class="aim-carousel-track"><article>1</article><article>2</article><article>3</article></div></div>
```

```css
@property --edge { syntax: "<number>"; inherits: false; initial-value: 1; }
.aim-carousel-track {
  display: flex; gap: 12px; overflow-x: auto; scroll-snap-type: x mandatory; scrollbar-width: none;
  --edge: 1;
  mask-image: linear-gradient(to right, rgb(0 0 0 / var(--edge)) 0, #000 32px, #000 calc(100% - 32px), rgb(0 0 0 / var(--edge)) 100%);
  transition: --edge 450ms var(--ease-swap) 250ms;            /* rest: fade lingers, then eases away */
}
.aim-carousel-track > * { flex: 0 0 100%; scroll-snap-align: start; }
.aim-carousel-track.is-moving { --edge: 0; transition: --edge 120ms var(--ease-out); }
.aim-carousel-track.is-moving * { pointer-events: none; }     /* no hover scrubbing while paging */
@media (prefers-reduced-motion: reduce) { .aim-carousel-track { scroll-behavior: auto; } }
```

```js
let idle;
track.addEventListener("scroll", () => { track.classList.add("is-moving"); clearTimeout(idle); idle = setTimeout(() => track.classList.remove("is-moving"), 220); }, { passive: true });
```

Dots under the pages switch on the `state` spring. Scroll snapping gives the physics for free; do not re-implement it in JS.

---

## 5. Edge fade on scrolling rows (only the edge with more content)

```css
@property --fade-start { syntax: "<length>"; inherits: false; initial-value: 0px; }
@property --fade-end   { syntax: "<length>"; inherits: false; initial-value: 0px; }
.aim-edge-fade { --fade: 28px; overflow-x: auto; scrollbar-width: none;
  mask-image: linear-gradient(var(--fade-dir, to right), transparent 0, #000 var(--fade-start), #000 calc(100% - var(--fade-end)), transparent 100%);
  transition: --fade-start var(--spring-state-duration) var(--spring-state-easing), --fade-end var(--spring-state-duration) var(--spring-state-easing); }
.aim-edge-fade.aim-vertical { --fade-dir: to bottom; --fade: 18px; }
.aim-edge-fade.fade-start { --fade-start: var(--fade); }
.aim-edge-fade.fade-end   { --fade-end: var(--fade); }
```

`edgeFade(scroller, "x" | "y")` in `motion.ts` toggles the classes from `scrollLeft` / `scrollWidth` and a `ResizeObserver`; returns a cleanup.

---

## 6. Endless wheel picker

Tier: occasional. Items placed by distance from centre (scale falls off, opacity −0.3 per step to a 0.2 floor, gap squeezes outward), continuous position, snaps on the `emphasis` spring.

```html
<div class="aim-wheel" tabindex="0" role="listbox" aria-label="Pick an icon"><div class="aim-wheel-ring"></div></div>
```

```css
.aim-wheel { position: relative; height: 72px; overflow: hidden; outline: none; touch-action: pan-y; user-select: none;
  mask-image: linear-gradient(to right, transparent, #000 96px, #000 calc(100% - 96px), transparent); }
.aim-wheel-ring { position: absolute; inset: 0; }
.aim-wheel-item { position: absolute; left: 50%; top: 50%; width: 44px; height: 44px; margin: -22px 0 0 -22px; display: grid; place-items: center; border-radius: 12px; background: #fff; box-shadow: var(--shadow-rest);
  transition: transform var(--spring-emphasis-duration) var(--spring-emphasis-easing), opacity var(--spring-emphasis-duration) var(--spring-emphasis-easing); }
.aim-wheel.is-scrubbing .aim-wheel-item { transition: none; }    /* wheel / drag: no animation, follow the hand */
@media (prefers-reduced-motion: reduce) { .aim-wheel-item { transition: opacity var(--motion-quick) var(--ease-out); } }
```

```js
function createWheel(root, items, { pitch = 56, onChange } = {}) {
  const ring = root.querySelector(".aim-wheel-ring");
  const n = items.length, VISIBLE = 4;
  let position = 0, snapTimer, lastReported = null;
  const layout = (t) => {                                 // signed distance from centre, in items
    const d = Math.abs(t), scale = 0.42 + 0.58 * Math.exp(-d), squeeze = d <= 3 ? 1 - 0.1 * d : 0.7;
    return { x: pitch * t * squeeze, scale, opacity: Math.max(0.2, 1 - 0.3 * d), z: Math.round(100 - d * 10) };
  };
  const nodes = new Map();
  function render() {
    const c = Math.round(position);
    const keep = new Set();
    for (let i = c - VISIBLE; i <= c + VISIBLE; i++) {
      keep.add(i);
      let el = nodes.get(i);
      if (!el) { el = document.createElement("div"); el.className = "aim-wheel-item"; el.textContent = items[((i % n) + n) % n]; el.addEventListener("click", () => go(i)); ring.appendChild(el); nodes.set(i, el); }
      const L = layout(i - position);
      el.style.transform = `translate(${L.x}px, 0) scale(${L.scale})`; el.style.opacity = L.opacity; el.style.zIndex = L.z;
    }
    for (const [i, el] of nodes) if (!keep.has(i)) { el.remove(); nodes.delete(i); }
    if (c !== lastReported) { lastReported = c; onChange?.(items[((c % n) + n) % n]); }   // report as it crosses centre
  }
  const snap = () => { root.classList.remove("is-scrubbing"); position = Math.round(position); render(); };
  const go = (i) => { position = i; snap(); };
  root.addEventListener("wheel", (e) => {                 // trackpad/wheel: move without animation, snap 90ms after the last event
    e.preventDefault(); root.classList.add("is-scrubbing");
    position += (e.deltaMode === 1 ? Math.sign(e.deltaX || e.deltaY) * pitch : (e.deltaX || e.deltaY)) / pitch;
    render(); clearTimeout(snapTimer); snapTimer = setTimeout(snap, 90);
  }, { passive: false });
  let drag = null;
  root.addEventListener("pointerdown", (e) => { if (drag) return; drag = { id: e.pointerId, x0: e.clientX, p0: position, t0: performance.now(), x: e.clientX }; root.setPointerCapture(e.pointerId); root.classList.add("is-scrubbing"); });
  root.addEventListener("pointermove", (e) => { if (!drag || e.pointerId !== drag.id) return; drag.x = e.clientX; position = drag.p0 - (e.clientX - drag.x0) / pitch; render(); });
  const end = (e) => { if (!drag || e.pointerId !== drag.id) return; const v = (drag.x - drag.x0) / Math.max(performance.now() - drag.t0, 1); position = drag.p0 - ((drag.x - drag.x0) + v * 200) / pitch; drag = null; snap(); };
  root.addEventListener("pointerup", end); root.addEventListener("pointercancel", end);
  root.addEventListener("keydown", (e) => { if (e.key === "ArrowLeft") go(Math.round(position) - 1); if (e.key === "ArrowRight") go(Math.round(position) + 1); });
  render();
  return { go, get value() { const c = Math.round(position); return items[((c % n) + n) % n]; } };
}
```

---

## 7. Shared element / hero transition

Tier: occasional. **Purpose**: continuity. Web: View Transitions API with `view-transition-name` on the shared element; the shared element moves 300–400ms on `--ease-out`, everything else cross-fades at 200ms. In a motion library: `layoutId` on both renderings (outside `AnimatePresence`). Vanilla FLIP for one element:

```js
function flip(el, mutate) {
  const first = el.getBoundingClientRect();
  mutate();                                              // change layout (class, parent, size)
  const last = el.getBoundingClientRect();
  const dx = first.left - last.left, dy = first.top - last.top, sx = first.width / last.width, sy = first.height / last.height;
  el.animate([{ transform: `translate(${dx}px, ${dy}px) scale(${sx}, ${sy})` }, { transform: "none" }],
             { duration: 300, easing: "cubic-bezier(0.22, 1, 0.36, 1)" });
}
```

Set `transform-origin: top left` on the element for the FLIP math. Reduced motion: cross-fade only.
