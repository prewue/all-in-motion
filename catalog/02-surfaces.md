# Catalog · Surfaces — things that open and close

Decision rules: trigger + surface that grows from it → **dropdown/popover** (anchored, origin-aware). Surface on top of the page, not anchored → **modal** (centered). Surface sliding from a screen edge → **drawer/sheet**. Surface sliding into a region of the page → **panel reveal**. The trigger *becomes* the surface → **morph** (or the gooey menu). Header with a collapsible body → **accordion**. Prefer the lighter surface when two fit.

Shared rule: opens 250ms, closes 150ms, `--ease-out` both ways; overshoot never on a close. A `.is-closing` class needs cleanup after the close duration or the next open starts from the closing scale.

---

## 1. Dropdown / popover / menu (origin-aware)

Tier: occasional. **Purpose**: spatial consistency — it grows out of the thing you clicked.

```html
<div class="aim-anchor">
  <button class="aim-press" aria-expanded="false" aria-haspopup="menu">Options ▾</button>
  <div class="aim-dropdown" role="menu" data-origin="top-left">
    <button role="menuitem">Rename</button><button role="menuitem">Duplicate</button><button role="menuitem">Delete</button>
  </div>
</div>
```

```css
.aim-anchor { position: relative; display: inline-block; }
.aim-dropdown {
  position: absolute; top: calc(100% + 6px); left: 0; min-width: 160px;
  transform-origin: top left;
  transform: scale(var(--scale-dropdown)) translateY(-2px);
  opacity: 0; pointer-events: none;
  transition: transform var(--motion-fast) var(--ease-out), opacity var(--motion-fast) var(--ease-out);
  will-change: transform, opacity;
}
.aim-dropdown[data-origin="top-right"]    { transform-origin: top right; left: auto; right: 0; }
.aim-dropdown[data-origin="top-center"]   { transform-origin: top center; }
.aim-dropdown[data-origin="bottom-left"]  { transform-origin: bottom left; top: auto; bottom: calc(100% + 6px); }
.aim-dropdown[data-origin="bottom-right"] { transform-origin: bottom right; top: auto; bottom: calc(100% + 6px); left: auto; right: 0; }
.aim-dropdown.is-open { transform: scale(1) translateY(0); opacity: 1; pointer-events: auto; }
.aim-dropdown.is-closing {
  transform: scale(var(--scale-closing)); opacity: 0; pointer-events: none;
  transition: transform var(--motion-quick) var(--ease-out), opacity var(--motion-quick) var(--ease-out);
}
@media (prefers-reduced-motion: reduce) {
  .aim-dropdown, .aim-dropdown.is-closing { transform: none; transition: opacity var(--motion-quick) var(--ease-out); }
}
```

```js
function wireDropdown(trigger, menu) {
  const closeMs = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--motion-quick")) || 150;
  const open = () => { menu.classList.remove("is-closing"); menu.classList.add("is-open"); trigger.setAttribute("aria-expanded", "true"); };
  const close = () => {
    if (!menu.classList.contains("is-open")) return;
    menu.classList.remove("is-open"); menu.classList.add("is-closing"); trigger.setAttribute("aria-expanded", "false");
    setTimeout(() => menu.classList.remove("is-closing"), closeMs);   // cleanup, or the next open starts at 0.99
  };
  trigger.addEventListener("click", (e) => { e.stopPropagation(); menu.classList.contains("is-open") ? close() : open(); });
  document.addEventListener("click", (e) => { if (!menu.contains(e.target)) close(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") close(); });
}
```

Library variants: Base UI `transform-origin: var(--transform-origin)` with `[data-starting-style]` / `[data-ending-style]`; Radix `var(--radix-dropdown-menu-content-transform-origin)`. Spring version: `--spring-open-*` to open, `--spring-close-*` to close. Items may stagger 30ms on open (`translateY(-4px)` → 0); never on close. Keyboard-opened menus (⌘K, arrow keys): no animation.

**Fold-reveal variant** (a popover growing from its top anchor with a slight 3D fold, exact per-frame driver in `motion.ts → playReveal`):

```css
@keyframes aim-reveal {
  0%   { opacity: 0; filter: blur(calc(9px * var(--motion-blur-scale))); transform: perspective(500px) rotateX(-6deg) scale(0.4, 0.2); }
  70%  { filter: blur(0); }
  100% { opacity: 1; filter: blur(0); transform: perspective(500px) rotateX(0) scale(1, 1); }
}
.aim-reveal-in  { transform-origin: 50% 0; animation: aim-reveal var(--spring-open-duration) var(--spring-open-easing) both; }
.aim-reveal-out { transform-origin: 50% 0; animation: aim-reveal var(--spring-close-duration) var(--spring-close-easing) reverse both; }
@media (prefers-reduced-motion: reduce) { .aim-reveal-in, .aim-reveal-out { animation-name: aim-fade; } }
@keyframes aim-fade { from { opacity: 0; } to { opacity: 1; } }
```

---

## 2. Tooltip (delay in, instant out, travels between triggers)

Tier: tens/day → 150ms in, 50ms out, 80ms intent delay. **Purpose**: state indication. One bubble per group.

```html
<span class="aim-tt-group">
  <button class="aim-tt-trigger" data-tooltip="Copy link" aria-describedby="tt1">⧉</button>
  <button class="aim-tt-trigger" data-tooltip="Share" aria-describedby="tt1">↗</button>
  <button class="aim-tt-trigger" data-tooltip="More options" aria-describedby="tt1">…</button>
  <span class="aim-tt" id="tt1" role="tooltip" aria-hidden="true" data-show="false"><span class="aim-tt-text"></span></span>
</span>
```

```css
.aim-tt-group { position: relative; display: inline-flex; gap: 4px; }
.aim-tt {
  position: absolute; bottom: calc(100% + 8px); left: 0; width: 0; overflow: hidden; box-sizing: border-box;
  display: inline-flex; justify-content: center; padding: 6px 10px; border-radius: 8px; white-space: nowrap;
  background: var(--tt-bg, #111); color: var(--tt-fg, #fff); font-size: 12px; pointer-events: none;
  translate: var(--tt-x, 0px) 0; scale: var(--scale-tooltip); transform-origin: 50% 100%; opacity: 0;
  /* rest rule = LEAVE: no delay, 50ms. The move lanes are always live.
     motion-ok: the single bubble tweens its width as it travels between triggers. */
  transition: opacity 50ms var(--ease-out), scale 50ms var(--ease-out),
              translate var(--motion-quick) var(--ease-out), width var(--motion-quick) var(--ease-out);
}
.aim-tt[data-show="true"] {
  opacity: 1; scale: 1;
  /* the intent delay belongs only to the show rule; motion-ok: same width lane */
  transition: opacity var(--motion-quick) var(--ease-out) var(--motion-micro), scale var(--motion-quick) var(--ease-out) var(--motion-micro),
              translate var(--motion-quick) var(--ease-out), width var(--motion-quick) var(--ease-out);
}
@media (prefers-reduced-motion: reduce) { .aim-tt { scale: 1; transition: opacity var(--motion-quick) var(--ease-out); } }
```

```js
function wireTooltips(group) {
  const tip = group.querySelector(".aim-tt"), text = tip.querySelector(".aim-tt-text");
  const hide = () => { tip.dataset.show = "false"; tip.setAttribute("aria-hidden", "true"); };
  const place = (t) => {
    const showing = tip.dataset.show === "true";
    text.textContent = t.dataset.tooltip || "";
    const cs = getComputedStyle(tip);
    const w = Math.ceil(text.scrollWidth + parseFloat(cs.paddingLeft) + parseFloat(cs.paddingRight));
    const g = group.getBoundingClientRect(), r = t.getBoundingClientRect();
    const x = r.left - g.left + r.width / 2 - w / 2;
    if (!showing) { tip.style.transition = "none"; tip.style.width = w + "px"; tip.style.setProperty("--tt-x", x + "px"); void tip.offsetWidth; tip.style.transition = ""; }
    else { tip.style.width = w + "px"; tip.style.setProperty("--tt-x", x + "px"); }   // travels
    tip.dataset.show = "true"; tip.setAttribute("aria-hidden", "false");
  };
  group.querySelectorAll(".aim-tt-trigger").forEach((t) => { t.addEventListener("pointerenter", () => place(t)); t.addEventListener("focus", () => place(t)); t.addEventListener("blur", hide); });
  group.addEventListener("pointerleave", hide);
}
```

Snap the geometry while hidden (so only the appear plays); tween it while showing (so the bubble travels). Library pattern: `[data-instant] { transition-duration: 0ms; transition-delay: 0ms; }` once any tooltip in the group is open.

---

## 3. Modal / dialog (centered)

Tier: occasional. **Purpose**: preventing a jarring change. The one surface that keeps `transform-origin: center`. Backdrop and content read as one surface: same clock.

```html
<div class="aim-scrim" data-open="false"></div>
<div class="aim-modal" role="dialog" aria-modal="true" aria-labelledby="m-title" data-open="false">
  <h2 id="m-title">Rename project</h2> … <button class="aim-press" data-close>Cancel</button>
</div>
```

```css
.aim-scrim { position: fixed; inset: 0; background: rgb(0 0 0 / 0.4); opacity: 0; pointer-events: none; transition: opacity var(--motion-fast) var(--ease-out); }
.aim-scrim[data-open="true"] { opacity: 1; pointer-events: auto; }
.aim-modal {
  position: fixed; inset: 0; margin: auto; width: min(420px, 90vw); height: fit-content;
  transform-origin: center; transform: scale(var(--scale-modal)); opacity: 0; pointer-events: none;
  transition: transform var(--motion-quick) var(--ease-out), opacity var(--motion-quick) var(--ease-out);   /* rest = close: 150ms */
  will-change: transform, opacity;
}
.aim-modal[data-open="true"] {
  transform: scale(1); opacity: 1; pointer-events: auto;
  transition: transform var(--motion-fast) var(--ease-out), opacity var(--motion-fast) var(--ease-out);         /* open: 250ms */
}
@media (prefers-reduced-motion: reduce) { .aim-modal { transform: none; } }
```

One attribute gives the asymmetry: the rest rule carries the close clock, the open rule the open clock. Native `<dialog>`: use `@starting-style` + `transition-behavior: allow-discrete` on `display` and `overlay`. Focus: trap inside, first focusable on open, return to trigger on close; Escape and scrim click close. Polished enter (consumer apps): add `filter: blur(4px)` → 0 and `translateY(8px)`; keep the exit subtler (opacity + scale only).

---

## 4. Drawer / bottom sheet (iOS curve + drag)

Tier: occasional. **Purpose**: spatial consistency. 500ms is the exception to the 300ms rule: the curve makes it feel faster.

```html
<div class="aim-scrim" data-open="false"></div>
<div class="aim-sheet" role="dialog" aria-modal="true" data-open="false">
  <div class="aim-sheet-handle" aria-hidden="true"></div>
  <div class="aim-sheet-body">…scrollable content…</div>
</div>
```

```css
.aim-sheet {
  position: fixed; left: 0; right: 0; bottom: 0; max-height: 85vh; border-radius: 16px 16px 0 0; background: #fff;
  transform: translateY(100%);   /* own height: any content */
  transition: transform var(--motion-deliberate) var(--ease-drawer);
  will-change: transform; touch-action: none;
}
.aim-sheet[data-open="true"] { transform: translateY(0); }
.aim-sheet.is-dragging { transition: none; }             /* 1:1 with the finger */
.aim-sheet-body { overflow: auto; overscroll-behavior: contain; touch-action: pan-y; }
@media (prefers-reduced-motion: reduce) {
  .aim-sheet { transition: opacity var(--motion-quick) var(--ease-out); transform: none; opacity: 0; pointer-events: none; }
  .aim-sheet[data-open="true"] { opacity: 1; pointer-events: auto; }
}
```

```js
function wireSheet(sheet, scrim, { snapPoints = [1] } = {}) {   // snapPoints as fractions of height, e.g. [0.4, 1]
  let dragging = false, id = null, startY = 0, y = 0, t0 = 0, samples = [];
  const h = () => sheet.getBoundingClientRect().height;
  const set = (v) => { y = v; sheet.style.transform = `translateY(${v}px)`; };
  const body = sheet.querySelector(".aim-sheet-body");
  let canDrag = true, topTimer;
  body.addEventListener("scroll", () => {                 // scroll vs drag: pause at the top before a drag may start
    clearTimeout(topTimer);
    if (body.scrollTop <= 0) topTimer = setTimeout(() => (canDrag = true), 100); else canDrag = false;
  }, { passive: true });
  sheet.addEventListener("pointerdown", (e) => {
    if (dragging || !canDrag) return;                     // multi-touch guard + scroll guard
    dragging = true; id = e.pointerId; startY = e.clientY - y; t0 = performance.now(); samples = [];
    sheet.setPointerCapture(id); sheet.classList.add("is-dragging");
  });
  sheet.addEventListener("pointermove", (e) => {
    if (!dragging || e.pointerId !== id) return;
    let v = e.clientY - startY;
    if (v < 0) v = v * 0.3;                               // rubber band above the top
    set(v);
    samples.push({ t: performance.now(), y: v }); while (samples.length > 1 && performance.now() - samples[0].t > 100) samples.shift();
  });
  const release = (e) => {
    if (!dragging || e.pointerId !== id) return;
    dragging = false; sheet.classList.remove("is-dragging");
    const a = samples[0], b = samples[samples.length - 1];
    const vel = a && b ? (b.y - a.y) / Math.max(b.t - a.t, 1) : 0;   // px/ms
    const H = h();
    if (vel > 0.5 || y > H * 0.5) { close(); return; }               // flick down or past half: dismiss
    // velocity-aware snap: fast flicks skip intermediate points
    const targets = snapPoints.map((p) => H * (1 - p));
    let target = vel < -0.5 ? Math.min(...targets) : targets.reduce((best, t) => (Math.abs(t - y) < Math.abs(best - y) ? t : best), targets[0]);
    set(target);
  };
  sheet.addEventListener("pointerup", release); sheet.addEventListener("pointercancel", release);
  const open = () => { sheet.dataset.open = "true"; scrim.dataset.open = "true"; set(0); sheet.style.transform = ""; };
  const close = () => { sheet.dataset.open = "false"; scrim.dataset.open = "false"; sheet.style.transform = ""; y = 0; };
  scrim.addEventListener("click", close);
  return { open, close };
}
```

Every rule from `05-interaction-patterns.md §4` is in there: pointer capture, multi-touch guard, damping above the top, momentum dismissal, velocity-aware snaps, scroll/drag conflict. Consumer apps may scale the page behind to 0.95; tools should not.

---

## 5. Panel reveal (slide into a region)

Tier: occasional. **Purpose**: preventing a jarring change. Translate + opacity + 2px cross-blur on one clock, so a short travel still reads as a full open.

```css
.aim-panel {
  transform: translateY(var(--panel-travel, 40px)); opacity: 0; pointer-events: none;
  filter: blur(calc(var(--blur-small) * var(--motion-blur-scale)));
  transition: transform var(--motion-medium) var(--ease-out), opacity var(--motion-medium) var(--ease-out), filter var(--motion-medium) var(--ease-out);   /* close 350 */
  will-change: transform, opacity, filter;
}
.aim-panel[data-open="true"] {
  transform: translateY(0); opacity: 1; filter: blur(0); pointer-events: auto;
  transition: transform var(--motion-slow) var(--ease-out), opacity var(--motion-slow) var(--ease-out), filter var(--motion-slow) var(--ease-out);   /* open 400 */
}
@media (prefers-reduced-motion: reduce) { .aim-panel { transform: none; filter: none; transition: opacity var(--motion-quick) var(--ease-out); } }
```

Wrap in `overflow: hidden` if the closed state must be clipped; set the travel to ~half the panel's height. A sidebar sliding in uses the `panelSlide` spring on `transform: translateX(-100%)`.

---

## 6. Plus → menu morph (the trigger becomes the surface)

Tier: occasional. **Purpose**: continuity. Use over a dropdown when the button *is* the panel.

```html
<div class="aim-morphmenu" data-open="false">
  <div class="aim-morphmenu-menu"><button>New file</button><button>New folder</button><button>Upload</button></div>
  <button class="aim-morphmenu-plus" aria-expanded="false" aria-label="Create"><svg viewBox="0 0 20 20" width="20" height="20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"><path d="M10 4v12M4 10h12"/></svg></button>
</div>
```

```css
.aim-morphmenu {
  position: relative; width: 40px; height: 40px; border-radius: 40px; overflow: hidden; background: #fff; box-shadow: var(--shadow-float);
  /* motion-ok: the trigger IS the panel; one small occasional surface (see the note below) */
  transition: width var(--motion-fast) var(--ease-out), height var(--motion-fast) var(--ease-out), border-radius var(--motion-fast) var(--ease-out);
}
.aim-morphmenu[data-open="true"] {
  width: 180px; height: 150px; border-radius: 20px;
  /* motion-ok: same morph, open phase */
  transition: width var(--motion-medium) cubic-bezier(0.34, 1.25, 0.64, 1), height var(--motion-medium) cubic-bezier(0.34, 1.25, 0.64, 1), border-radius var(--motion-medium) var(--ease-out);
}
.aim-morphmenu-plus {
  position: absolute; inset: auto 0 0 auto; width: 40px; height: 40px; display: grid; place-items: center; border: 0; background: transparent; cursor: pointer;
  transition: opacity 200ms var(--ease-out), transform var(--motion-medium) var(--ease-out), filter 200ms var(--ease-out);
}
.aim-morphmenu-plus svg { transition: transform var(--motion-medium) var(--ease-out); }
.aim-morphmenu[data-open="true"] .aim-morphmenu-plus { opacity: 0; transform: translateX(-40px); filter: blur(var(--blur-small)); pointer-events: none; }
.aim-morphmenu[data-open="true"] .aim-morphmenu-plus svg { transform: scale(0.97) rotate(45deg); }
.aim-morphmenu-menu {
  position: absolute; inset: 0; padding: 12px; display: flex; flex-direction: column; gap: 4px;
  opacity: 0; transform: translateX(40px) scale(0.97); filter: blur(var(--blur-small)); pointer-events: none;
  transition: opacity 200ms var(--ease-out), transform var(--motion-medium) var(--ease-out), filter 200ms var(--ease-out);
}
.aim-morphmenu[data-open="true"] .aim-morphmenu-menu { opacity: 1; transform: none; filter: blur(0); pointer-events: auto; }
@media (prefers-reduced-motion: reduce) { .aim-morphmenu, .aim-morphmenu-plus, .aim-morphmenu-menu { transition: opacity var(--motion-quick) var(--ease-out); transform: none; filter: none; } }
```

```js
plus.addEventListener("click", (e) => { e.stopPropagation(); setOpen(root.dataset.open !== "true"); });
document.addEventListener("click", (e) => { if (!root.contains(e.target)) setOpen(false); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });
function setOpen(o) { root.dataset.open = String(o); plus.setAttribute("aria-expanded", String(o)); }
```

This one animates `width`/`height` on purpose: a single small surface, occasional, with the bouncy ease only on open. Pin the plus to a corner so it stays put while the box grows out of it; `overflow: hidden` clips the menu during the morph. Open size is hardcoded to the real panel, not derived.

---

## 7. Gooey plus menu (liquid split)

Tier: occasional/rare. **Purpose**: continuity + delight. A plus button liquid-splits into 3 satellites on an arc and merges back. The goo is an SVG filter on a blob layer that mirrors the button geometry 1:1; the real buttons sit unfiltered above so icons stay crisp. Filter on **SVG content**, never CSS `filter: url()` on HTML (WebKit). Classic `transform` on the circles (individual `translate:` breaks on SVG in Safari). Longhand `animation-*` for the close nudge.

```html
<div class="aim-goo" data-open="false">
  <svg class="aim-goo-layer" viewBox="0 0 200 140" aria-hidden="true" focusable="false">
    <defs>
      <filter id="aim-goo-f" x="-60%" y="-60%" width="220%" height="220%" color-interpolation-filters="sRGB">
        <feGaussianBlur in="SourceGraphic" stdDeviation="6" result="blur"/>
        <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="goo"/>
        <feComposite in="SourceGraphic" in2="goo" operator="atop" result="shape"/>
        <!-- shadow built from the merged silhouette, merged BEHIND it (never chain feDropShadow) -->
        <feColorMatrix in="shape" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 60 -29.5" result="solid"/>
        <feMorphology in="solid" operator="dilate" radius="1" result="ring-a"/>
        <feFlood flood-color="#000" flood-opacity="0.06" result="ring-c"/><feComposite in="ring-c" in2="ring-a" operator="in" result="ring"/>
        <feGaussianBlur in="shape" stdDeviation="3" result="s2b"/><feOffset in="s2b" dy="2" result="s2o"/>
        <feFlood flood-color="#000" flood-opacity="0.05" result="s2c"/><feComposite in="s2c" in2="s2o" operator="in" result="s2"/>
        <feGaussianBlur in="shape" stdDeviation="21" result="s3b"/><feOffset in="s3b" dy="4" result="s3o"/>
        <feFlood flood-color="#000" flood-opacity="0.06" result="s3c"/><feComposite in="s3c" in2="s3o" operator="in" result="s3"/>
        <feMerge><feMergeNode in="s3"/><feMergeNode in="s2"/><feMergeNode in="ring"/><feMergeNode in="shape"/></feMerge>
      </filter>
    </defs>
    <g filter="url(#aim-goo-f)">
      <circle class="aim-goo-blob" cx="100" cy="100" r="20" style="--fx:-54px;--fy:-34px;--i:0"/>
      <circle class="aim-goo-blob" cx="100" cy="100" r="20" style="--fx:0px;--fy:-64px;--i:1"/>
      <circle class="aim-goo-blob" cx="100" cy="100" r="20" style="--fx:54px;--fy:-34px;--i:2"/>
      <circle class="aim-goo-blob" cx="100" cy="100" r="20"/>
    </g>
  </svg>
  <button class="aim-goo-item" style="--fx:-54px;--fy:-34px;--i:0" aria-label="New file" tabindex="-1">📄</button>
  <button class="aim-goo-item" style="--fx:0px;--fy:-64px;--i:1" aria-label="Add image" tabindex="-1">🖼</button>
  <button class="aim-goo-item" style="--fx:54px;--fy:-34px;--i:2" aria-label="New folder" tabindex="-1">📁</button>
  <button class="aim-goo-main" aria-expanded="false" aria-label="Open menu"><span class="aim-goo-swap">＋</span></button>
</div>
```

```css
.aim-goo { position: relative; width: 200px; height: 140px; }
.aim-goo-layer { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; pointer-events: none; will-change: filter, transform; }
.aim-goo-blob { fill: var(--goo-surface, #fff); transform: translate(0, 0); transform-box: fill-box; transition: transform var(--motion-fast) var(--ease-out); will-change: transform; }
.aim-goo[data-open="true"] .aim-goo-blob {
  transform: translate(calc(var(--fx, 0px) * var(--goo-spread, 1)), calc(var(--fy, 0px) * var(--goo-spread, 1)));
  transition: transform var(--motion-medium) var(--ease-overshoot); transition-delay: calc(var(--i, 0) * var(--stagger-base));
}
.aim-goo-item, .aim-goo-main {
  position: absolute; left: 80px; top: 80px; width: 40px; height: 40px; border: 0; padding: 0; border-radius: 50%; background: transparent;
  display: grid; place-items: center; cursor: pointer; color: #17181c; transform: translate(0, 0);
  transition: transform var(--motion-fast) var(--ease-out); will-change: transform;
}
.aim-goo-item { pointer-events: none; }
.aim-goo[data-open="true"] .aim-goo-item {
  pointer-events: auto; transform: translate(calc(var(--fx, 0px) * var(--goo-spread, 1)), calc(var(--fy, 0px) * var(--goo-spread, 1)));
  transition: transform var(--motion-medium) var(--ease-overshoot); transition-delay: calc(var(--i, 0) * var(--stagger-base));
}
/* icons hold back while the blob is still merged, then cross-blur in */
.aim-goo-item > * { opacity: 0; filter: blur(2px); transition: opacity 120ms ease, filter 120ms ease; }
.aim-goo[data-open="true"] .aim-goo-item > * { opacity: 1; filter: blur(0); transition: opacity 180ms ease, filter 180ms ease; transition-delay: calc(var(--i, 0) * var(--stagger-base) + 120ms); }
@keyframes aim-goo-anticipate { 0% { transform: translateY(0); } 30% { transform: translateY(5px); } 100% { transform: translateY(0); } }
.aim-goo.is-anticipating .aim-goo-layer, .aim-goo.is-anticipating .aim-goo-main {
  animation-name: aim-goo-anticipate; animation-duration: 700ms; animation-timing-function: var(--ease-out); animation-fill-mode: both;
}
.aim-goo-swap { display: inline-grid; place-items: center; font-size: 22px; line-height: 1; transform: rotate(0); transition: transform var(--motion-fast) var(--ease-swap); }
.aim-goo[data-open="true"] .aim-goo-swap { transform: rotate(45deg); }   /* the plus spun 45° IS the ×  */
@media (prefers-reduced-motion: reduce) {
  .aim-goo-blob, .aim-goo-item, .aim-goo-item > *, .aim-goo-swap { transition: none !important; }
  .aim-goo.is-anticipating .aim-goo-layer, .aim-goo.is-anticipating .aim-goo-main { animation: none !important; }
}
```

```js
function wireGoo(root) {
  const main = root.querySelector(".aim-goo-main");
  let t;
  const setOpen = (o) => {
    if ((root.dataset.open === "true") === o) return;
    root.dataset.open = String(o); main.setAttribute("aria-expanded", String(o));
    clearTimeout(t);
    if (!o) { root.classList.add("is-anticipating"); t = setTimeout(() => root.classList.remove("is-anticipating"), 750); }
    else root.classList.remove("is-anticipating");
  };
  main.addEventListener("click", (e) => { e.stopPropagation(); setOpen(root.dataset.open !== "true"); });
  root.querySelectorAll(".aim-goo-item").forEach((i) => i.addEventListener("click", () => setOpen(false)));
  document.addEventListener("click", (e) => { if (!root.contains(e.target)) setOpen(false); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setOpen(false); });
}
```

Give each instance a unique filter id when rendering more than one. Keep `--fx/--fy/--i` paired on the circle and its button.

---

## 8. Accordion / disclosure (grid rows, chevron flip)

Tier: tens/day → 250ms symmetric. **Purpose**: preventing a jarring change. No JS height measuring; any content size.

```html
<div class="aim-acc" data-open="false">
  <button class="aim-acc-head" aria-expanded="false">Shipping details
    <span class="aim-acc-chevron"><svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M4 6.5L8 10.5L12 6.5"/></svg></span>
  </button>
  <div class="aim-acc-panel"><div class="aim-acc-inner">…</div></div>
</div>
```

```css
.aim-acc-panel { display: grid; grid-template-rows: 0fr; transition: grid-template-rows var(--motion-fast) var(--ease-out); }
.aim-acc[data-open="true"] .aim-acc-panel { grid-template-rows: 1fr; }
.aim-acc-inner { overflow: hidden; opacity: 0; filter: blur(calc(var(--blur-small) * var(--motion-blur-scale)));
  transition: opacity var(--motion-fast) var(--ease-out), filter var(--motion-fast) var(--ease-out); }   /* padding goes HERE, never on the track */
.aim-acc[data-open="true"] .aim-acc-inner { opacity: 1; filter: blur(0); }
.aim-acc-chevron { display: inline-flex; transform: scaleY(1); transform-origin: center; transition: transform var(--motion-fast) var(--ease-out); }
.aim-acc-chevron path { vector-effect: non-scaling-stroke; }
.aim-acc[data-open="true"] .aim-acc-chevron { transform: scaleY(-1); }   /* passes through a flat line like a path morph, works everywhere */
@media (prefers-reduced-motion: reduce) { .aim-acc-panel, .aim-acc-inner, .aim-acc-chevron { transition: none; } }
```

```js
head.addEventListener("click", () => { const o = acc.dataset.open !== "true"; acc.dataset.open = String(o); head.setAttribute("aria-expanded", String(o)); });
```

---

## 9. Card resize (compact ↔ expanded)

Tier: occasional. A container tweening its own width/height when its layout state changes. Costs layout — keep it to one small surface at a time, 300ms.

```css
/* motion-ok: the documented layout-cost exception — one small surface, occasional */
.aim-resize { transition: width 300ms var(--ease-out), height 300ms var(--ease-out); will-change: width, height; }
@media (prefers-reduced-motion: reduce) { .aim-resize { transition: none; } }
```

Prefer a `scale`-based zoom (image open tilt, `08-gestures.md`) when the content can be laid out at full size and shrunk, or the FLIP/`layout` animation of a motion library, when the resize is frequent or large.

---

## 10. Command palette — no animation (teaching example)

Tier: 100+/day, keyboard-initiated → **instant**. Overlay appears at once, input focused, results filter with no layout jump, arrow navigation moves the highlight instantly, Enter closes instantly. If a product insists on motion, cap it at a 100ms opacity fade for the scrim only. This entry exists so that "animate the palette" gets the correct answer: don't.
