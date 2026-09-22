# Catalog · Feedback & controls

Every recipe: `aim-*` classes, semantic tokens from `assets/motion-tokens.css` (+ `motion-springs.css`), a `prefers-reduced-motion` path, and the hooks to wire. Paste the CSS verbatim, wire the documented attributes, keep the reduced-motion block. Tier = frequency tier from `01-principles.md`.

---

## 1. Button press

**When**: any pressable element. Tier: every tier — press feedback is the one animation that belongs on 100+/day controls because it is ≤160ms and confirms the input. **Purpose**: feedback.

```html
<button class="aim-press">Save</button>
```

```css
.aim-press {
  transition: transform var(--motion-quick) var(--ease-out), background-color var(--motion-quick) var(--ease-hover);
}
.aim-press:active { transform: scale(var(--scale-press)); }   /* 0.97; 0.95–0.98 range */

@media (prefers-reduced-motion: reduce) {
  .aim-press { transition: background-color var(--motion-quick) var(--ease-hover); }
  .aim-press:active { transform: none; }
}
```

Spring version (pointer down follows the hand, release springs back):

```css
.aim-press--spring { transition: transform var(--spring-release-duration) var(--spring-release-easing); }
.aim-press--spring:active { transform: scale(var(--scale-press)); transition-duration: var(--spring-press-duration); transition-timing-function: var(--spring-press-easing); }
```

Notes: `:active` fires on touch; hover does not — never make hover the only feedback. `scale()` carries the label and icon along. Tailwind v4: `transition-transform duration-150 ease-out active:scale-[0.97]`.

---

## 2. Press bounce (confirmed primary action)

**When**: add / start / confirm — a click that deserves a small "got it". Tier: occasional. **Purpose**: feedback.

```html
<button class="aim-bounce-btn"><span class="aim-bounce-icon">＋</span> Add</button>
```

```css
.aim-bounce-icon { display: inline-block; transition: transform var(--spring-release-duration) var(--spring-release-easing); }
.aim-bounce-btn.is-bouncing .aim-bounce-icon { transform: scale(var(--scale-pop)); transition: transform var(--spring-bounce-duration) var(--spring-bounce-easing); }
@media (prefers-reduced-motion: reduce) { .aim-bounce-icon { transition: none; } .aim-bounce-btn.is-bouncing .aim-bounce-icon { transform: none; } }
```

```js
btn.addEventListener("click", () => {
  btn.classList.add("is-bouncing");
  setTimeout(() => btn.classList.remove("is-bouncing"), 180);   // 1.15 on `bounce`, back on `release`
});
```

Swap a play/pause glyph in the same click with the icon swap (`05-content-swap.md`).

---

## 3. Hover: fill, grow, lift

**When**: mouse hover on interactive elements. Tier: tens/day → subtle. **Purpose**: state indication (this is interactive). Gate everything behind a real pointer.

```css
/* Fill change only: cards, rows, buttons. Size never changes. */
.aim-hover-fill { transition: background-color var(--spring-hover-duration) var(--spring-hover-easing), border-color var(--spring-hover-duration) var(--spring-hover-easing); }
@media (hover: hover) and (pointer: fine) { .aim-hover-fill:hover { background-color: var(--surface-hover, rgb(0 0 0 / 0.04)); } }

/* Grow: only clickable pills / badges. The grow means "you can press this". */
.aim-hover-grow { transition: transform var(--spring-hover-scale-duration) var(--spring-hover-scale-easing); }
@media (hover: hover) and (pointer: fine) {
  .aim-hover-grow:hover { transform: scale(var(--scale-hover-grow)); }         /* 1.08 */
  .aim-hover-grow.aim-small:hover { transform: scale(1.06); }
}

/* Lift: product cards, tiles. Shadow expands; image inside may zoom 1.05. */
.aim-hover-lift {
  box-shadow: var(--shadow-rest);
  transition: transform var(--motion-fast) var(--ease-out), box-shadow var(--motion-fast) var(--ease-out);
}
.aim-hover-lift img { transition: transform var(--motion-medium) var(--ease-out); }
@media (hover: hover) and (pointer: fine) {
  .aim-hover-lift:hover { transform: translateY(-3px); box-shadow: var(--shadow-hover); }
  .aim-hover-lift:hover img { transform: scale(1.05); }
}
.aim-hover-lift:active { transform: translateY(-1px) scale(0.99); transition-duration: var(--motion-quick); }

@media (prefers-reduced-motion: reduce) {
  .aim-hover-grow:hover, .aim-hover-lift:hover, .aim-hover-lift:hover img { transform: none; }
}
```

Controls that appear on hover (edit/delete) sit `position: absolute` on top of the row and fade in on the `hover` spring so content never shifts. Do not put a hover scale on every card in a grid (anti-pattern §2).

---

## 4. Like button (heart pop + particle burst)

**When**: like / favourite / heart — a single tap that flips a boolean and deserves a tiny celebration. Tier: occasional. **Purpose**: feedback + delight. The burst plays on the way in only.

```html
<button class="aim-like" data-liked="false" aria-pressed="false">
  <span class="aim-like-icon">
    <svg class="aim-like-heart" viewBox="0 0 24 24" width="20" height="20"><path d="M12 21s-7-4.6-9.3-9.2C.9 8 3 4 6.8 4c2 0 3.5 1 4.2 2.3C11.7 5 13.2 4 15.2 4 19 4 21.1 8 19.3 11.8 17 16.4 12 21 12 21z"/></svg>
  </span>
  <span class="aim-like-particles" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span>
  <span class="aim-like-count">128</span>
</button>
```

```css
.aim-like { position: relative; display: inline-flex; align-items: center; gap: 6px; }
.aim-like-heart { color: currentColor; transition: color var(--motion-quick) var(--ease-out); }
.aim-like-heart path { fill: transparent; stroke: currentColor; stroke-width: 1.6; transition: fill var(--motion-quick) var(--ease-out), stroke var(--motion-quick) var(--ease-out); }
.aim-like[data-liked="true"] .aim-like-heart { color: var(--like-color, #f40051); }
.aim-like[data-liked="true"] .aim-like-heart path { fill: currentColor; }
/* Pop lives on the HTML wrapper, never the <svg>: transforming inline SVG rasterises it at 1× in Chromium. */
.aim-like-icon { display: inline-flex; }
.aim-like[data-liked="true"] .aim-like-icon { animation: aim-like-pop var(--motion-medium) var(--ease-overshoot); }
@keyframes aim-like-pop { 0% { transform: scale(1); } 30% { transform: scale(0.82); } 100% { transform: scale(1); } }

.aim-like-particles { position: absolute; left: 10px; top: 50%; width: 0; height: 0; pointer-events: none; color: var(--like-color, #f40051); }
.aim-like-particles i {
  position: absolute;
  width: calc(2.5px * var(--psize, 1)); height: calc(2.5px * var(--psize, 1));
  left: calc(2.5px * var(--psize, 1) / -2); top: calc(2.5px * var(--psize, 1) / -2);
  border-radius: 50%; background: currentColor; opacity: 0;
}
@keyframes aim-like-burst {
  0%   { opacity: 0; transform: translate(0, 0) scale(0.4); }
  20%  { opacity: 1; transform: translate(calc(var(--px) * 0.25), calc(var(--py) * 0.25)) scale(1); }
  100% { opacity: 0; transform: translate(var(--px), var(--py)) scale(var(--p-end, 0.6)); }
}
.aim-like.is-bursting .aim-like-particles i { animation: aim-like-burst var(--pdur, 600ms) ease-out var(--pdelay, 0ms) forwards; }

@media (prefers-reduced-motion: reduce) { .aim-like-icon, .aim-like-particles i { animation: none !important; } }
```

```js
function wireLike(btn) {
  const dots = btn.querySelectorAll(".aim-like-particles i");
  btn.addEventListener("click", () => {
    const liked = btn.getAttribute("data-liked") !== "true";
    btn.setAttribute("data-liked", String(liked));
    btn.setAttribute("aria-pressed", String(liked));
    if (!liked) return;                                    // unlike: fill reverses, no particles
    dots.forEach((d, i) => {                               // organic spray: per-dot vector, size, timing
      const a = (i / dots.length) * Math.PI * 2 + (Math.random() - 0.5) * 0.6;
      const dist = 16 + Math.random() * 10;
      d.style.setProperty("--px", `${Math.cos(a) * dist}px`);
      d.style.setProperty("--py", `${Math.sin(a) * dist}px`);
      d.style.setProperty("--psize", (0.7 + Math.random() * 0.8).toFixed(2));
      d.style.setProperty("--pdur", `${480 + Math.random() * 240}ms`);
      d.style.setProperty("--pdelay", `${Math.random() * 60}ms`);
    });
    btn.classList.remove("is-bursting"); void btn.offsetWidth; btn.classList.add("is-bursting");
    setTimeout(() => btn.classList.remove("is-bursting"), 800);
  });
}
```

---

## 5. Checkbox check (fill, then draw)

**When**: any boolean control whose checked state should feel earned. Tier: tens/day → keep it ≤500ms total and calm. **Purpose**: state indication.

```html
<button class="aim-check" role="checkbox" aria-checked="false">
  <svg viewBox="0 0 12 12" width="12" height="12"><path d="M2 6.3L4.8 9.2L10 3"/></svg>
</button>
```

```css
.aim-check {
  width: 20px; height: 20px; border-radius: 6px; border: 0; padding: 0; display: grid; place-items: center; cursor: pointer;
  background: var(--check-bg, rgb(0 0 0 / 0.08));
  box-shadow: inset 0 0 0 1px rgb(0 0 0 / 0.12);
  transition: background var(--motion-quick) var(--ease-out), box-shadow var(--motion-quick) var(--ease-out);
}
.aim-check svg path {
  fill: none; stroke: #fff; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round;
  stroke-dasharray: var(--check-len, 13); stroke-dashoffset: var(--check-len, 13);
  transition: stroke-dashoffset var(--motion-quick) var(--ease-out);          /* uncheck: quick, no draw */
}
.aim-check[aria-checked="true"] { background: var(--accent, #2563eb); box-shadow: inset 0 0 0 1px transparent; }
.aim-check[aria-checked="true"] svg path {
  stroke-dashoffset: 0;
  transition: stroke-dashoffset var(--motion-medium) var(--ease-out) var(--motion-micro, 0ms);  /* draw after the fill */
}
@media (prefers-reduced-motion: reduce) { .aim-check, .aim-check svg path { transition: none !important; } }
```

```js
// Calibrate the dash to the real path length once (round up by 1) — otherwise it pre-reveals or over-draws.
const path = box.querySelector("path");
box.style.setProperty("--check-len", String(Math.ceil(path.getTotalLength()) + 1));
box.addEventListener("click", () => box.setAttribute("aria-checked", String(box.getAttribute("aria-checked") !== "true")));
```

Transitioning `stroke-dashoffset` (not keyframes) lets a mid-draw uncheck reverse cleanly.

---

## 6. Toggle switch (double-overshoot travel)

**When**: settings rows, feature flags. Tier: tens/day → the overshoot is 1px, invisible unless you look. **Purpose**: state indication.

```html
<button class="aim-toggle" role="switch" aria-checked="false" data-on="false"><span class="aim-toggle-thumb"></span></button>
```

```css
.aim-toggle {
  --travel: 16px;
  position: relative; width: 36px; height: 20px; border-radius: 999px; border: 0; padding: 2px; cursor: pointer;
  background: rgb(0 0 0 / 0.16);
  transition: background-color var(--motion-fast) var(--ease-out);
}
.aim-toggle[data-on="true"] { background: var(--accent, #2563eb); }
.aim-toggle-thumb {
  display: block; width: 16px; height: 16px; border-radius: 50%; background: #fff;
  box-shadow: 0 1px 2px rgb(0 0 0 / 0.25);
  translate: 0 0; will-change: translate;
}
.aim-toggle[data-on="true"] .aim-toggle-thumb { translate: var(--travel) 0; }
/* Only after first interaction (.is-init) so switches don't bounce on page load. */
.aim-toggle.is-init[data-on="true"]  .aim-toggle-thumb { animation: aim-toggle-on  var(--motion-medium) var(--ease-bounce) both; }
.aim-toggle.is-init[data-on="false"] .aim-toggle-thumb { animation: aim-toggle-off var(--motion-medium) var(--ease-bounce) both; }
@keyframes aim-toggle-on  { 0% { translate: 0 0; } 55% { translate: calc(var(--travel) + 1px) 0; } 80% { translate: var(--travel) 0; } 100% { translate: var(--travel) 0; } }
@keyframes aim-toggle-off { 0% { translate: var(--travel) 0; } 55% { translate: -1px 0; } 80% { translate: 0 0; } 100% { translate: 0 0; } }
@media (prefers-reduced-motion: reduce) { .aim-toggle-thumb { animation: none !important; transition: translate var(--motion-quick) var(--ease-out); } }
```

```js
sw.addEventListener("click", () => {
  const on = sw.getAttribute("data-on") !== "true";
  sw.classList.add("is-init");
  sw.setAttribute("data-on", String(on)); sw.setAttribute("aria-checked", String(on));
});
```

Spring alternative for the thumb: `transition: translate var(--spring-segmented-duration) var(--spring-segmented-easing)` with no keyframes — smoother under rapid toggling. Optional haptic tick on mobile at completion.

---

## 7. Selected pill / segmented option

**When**: a chip or tab that becomes selected; the chosen tile in a picker. Tier: tens/day. **Purpose**: state indication.

```css
.aim-pill {
  transition: background-color var(--spring-segmented-duration) var(--spring-segmented-easing),
              color var(--spring-segmented-duration) var(--spring-segmented-easing);
  font-weight: 500;   /* keep weight identical in both states so width never changes */
}
.aim-pill[aria-selected="true"] { background: var(--accent, #2563eb); color: #fff; }
```

A sliding indicator under tabs is in `04-navigation.md`. A choice that should feel *decided* (favourite, primary selection) snaps on the `emphasis` spring instead.

---

## 8. Success check (fade + rotate + bob + path draw)

**When**: a status turns from pending to success — payment done, upload complete, message sent — and the moment should feel earned. Tier: occasional/rare. **Purpose**: feedback. Appear only; hide by unmounting or a plain fade.

```html
<span class="aim-success" data-state="out" aria-hidden="true">
  <svg viewBox="0 0 48 48" width="48" height="48" fill="none">
    <circle cx="24" cy="24" r="21" stroke="currentColor" stroke-width="2.5"/>
    <path d="M15 24.5l6.5 6.5L33 18" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  </svg>
</span>
```

```css
.aim-success { display: inline-block; transform-origin: center; opacity: 0; color: var(--success, #16a34a); will-change: transform, opacity, filter; }
.aim-success svg { display: block; overflow: visible; }
.aim-success svg path { stroke-dasharray: var(--check-len, 26); stroke-dashoffset: var(--check-len, 26); }
.aim-success[data-state="in"] {
  animation:
    aim-succ-fade   var(--motion-deliberate) var(--ease-out) forwards,
    aim-succ-rotate var(--motion-deliberate) var(--ease-out) forwards,
    aim-succ-blur   var(--motion-deliberate) var(--ease-out) forwards,
    aim-succ-bob    var(--motion-deliberate) var(--ease-bounce) forwards;
}
.aim-success[data-state="in"] svg path { animation: aim-succ-draw var(--motion-deliberate) var(--ease-out) var(--motion-micro) forwards; }
@keyframes aim-succ-fade   { from { opacity: 0; } to { opacity: 1; } }
@keyframes aim-succ-rotate { from { transform: rotate(80deg); } to { transform: rotate(0); } }
@keyframes aim-succ-blur   { from { filter: blur(10px); } to { filter: blur(0); } }
@keyframes aim-succ-bob    { from { translate: 0 40px; } to { translate: 0 0; } }
@keyframes aim-succ-draw   { to { stroke-dashoffset: 0; } }
@media (prefers-reduced-motion: reduce) {
  .aim-success { animation: none !important; opacity: 1; }
  .aim-success svg path { animation: none !important; stroke-dashoffset: 0 !important; }
}
```

```js
function showSuccess(el) {
  const p = el.querySelector("path");
  el.style.setProperty("--check-len", String(Math.ceil(p.getTotalLength()) + 1));
  el.setAttribute("data-state", "out"); void el.offsetWidth;   // replay from zero
  el.setAttribute("data-state", "in");
}
```

Pair with the icon swap when a spinner must give way to the check; or use the spinner→check morph below for a row-level badge.

---

## 9. Spinner → check morph (row-level status badge)

**When**: task lists, checklists, upload rows, save indicators — a spinner that needs an ending. Tier: occasional. **Purpose**: state indication. One attribute is the whole API: `data-state="spinning" | "done"`.

```html
<span class="aim-morph-wrap"><!-- carries the cross-blur; must be a separate element -->
  <span class="aim-morph" data-state="spinning" role="img" aria-label="In progress">
    <span class="aim-morph-ring" aria-hidden="true"></span>
    <span class="aim-morph-arc" aria-hidden="true"></span>
    <span class="aim-morph-fill" aria-hidden="true"></span>
    <span class="aim-morph-disc" aria-hidden="true"><svg viewBox="0 0 24 24"><path class="aim-morph-mark" d="M8 12.5L10.8 15.5L16.4 9.5"/></svg></span>
  </span>
</span>
```

```css
.aim-morph-wrap { display: inline-flex; filter: blur(0); transition: filter var(--motion-fast) var(--ease-out); will-change: filter; }
.aim-morph-wrap.is-crossing { filter: blur(0.5px); transition: filter calc(var(--motion-medium) * 0.45) var(--ease-bounce); }
.aim-morph { position: relative; width: 22px; height: 22px; scale: 1; transition: scale var(--motion-fast) var(--ease-out); will-change: scale, transform; }
.aim-morph[data-state="done"] {
  scale: 1.09; transition: scale var(--motion-medium) var(--ease-overshoot);
  /* two-phase hop: up, then down (delayed by the up duration). fill-mode forwards, NOT both,
     or the delayed phase yanks the badge to its `from` immediately. Longhands for WebKit. */
  animation-name: aim-morph-up, aim-morph-down;
  animation-duration: var(--motion-fast), 300ms;
  animation-timing-function: var(--ease-bounce), cubic-bezier(0.14, 2.56, 0.94, 1);
  animation-delay: 0ms, var(--motion-fast);
  animation-fill-mode: forwards, forwards;
}
@keyframes aim-morph-up   { from { transform: translateY(0); } to { transform: translateY(-3px); } }
@keyframes aim-morph-down { from { transform: translateY(-3px); } to { transform: translateY(0); } }
.aim-morph-ring { position: absolute; inset: 0; border-radius: 50%; border: 2.5px solid rgb(0 0 0 / 0.1); transition: opacity var(--motion-fast) ease; }
.aim-morph[data-state="done"] .aim-morph-ring { opacity: 0; transition: opacity calc(var(--motion-medium) * 0.7) ease; }
.aim-morph-arc {
  position: absolute; inset: 0; border-radius: 50%; border: 2.5px solid transparent; border-top-color: #7a7a7a;
  animation: aim-morph-spin 900ms linear infinite; transition: opacity var(--motion-fast) var(--ease-out); will-change: transform;
}
@keyframes aim-morph-spin { to { transform: rotate(360deg); } }
.aim-morph[data-state="done"] .aim-morph-arc { opacity: 0; animation-play-state: paused; transition: opacity calc(var(--motion-medium) * 0.5) ease; }
.aim-morph-fill { position: absolute; inset: -1px; border-radius: 50%; background: var(--success, #35ba00); opacity: 0; transition: opacity var(--motion-fast) var(--ease-out); }
.aim-morph[data-state="done"] .aim-morph-fill { opacity: 1; transition: opacity var(--motion-medium) var(--ease-bounce); }
.aim-morph-disc { position: absolute; inset: 0; display: grid; place-items: center; }
.aim-morph-disc svg { width: 100%; height: 100%; display: block; }
.aim-morph-mark {
  fill: none; stroke: #fff; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round;
  stroke-dasharray: var(--mark-len, 20); stroke-dashoffset: var(--mark-len, 20);
  transition: stroke-dashoffset var(--motion-fast) var(--ease-out);
}
.aim-morph[data-state="done"] .aim-morph-mark {
  stroke-dashoffset: 0;
  /* sequenced, not queued: the draw starts 200ms BEFORE the fill completes */
  transition: stroke-dashoffset 600ms var(--ease-out) calc(var(--motion-medium) + var(--motion-micro) - 200ms);
}
@media (prefers-reduced-motion: reduce) {
  .aim-morph-arc { animation: none !important; }
  .aim-morph-wrap, .aim-morph-wrap.is-crossing { filter: none !important; transition: none !important; }
  .aim-morph, .aim-morph-ring, .aim-morph-arc, .aim-morph-fill, .aim-morph-mark { transition: none !important; animation: none !important; }
  .aim-morph[data-state="done"] .aim-morph-mark { stroke-dashoffset: 0; }
}
```

```js
function createMorph(badge, wrap) {
  const mark = badge.querySelector(".aim-morph-mark");
  badge.style.setProperty("--mark-len", String(Math.ceil(mark.getTotalLength())));
  let t;
  const cross = () => { clearTimeout(t); wrap.classList.add("is-crossing"); t = setTimeout(() => wrap.classList.remove("is-crossing"), 350 * 0.45); };
  return {
    done() { if (badge.dataset.state === "done") { badge.dataset.state = "spinning"; void badge.offsetWidth; } badge.dataset.state = "done"; badge.setAttribute("aria-label", "Done"); cross(); },
    spin() { badge.dataset.state = "spinning"; badge.setAttribute("aria-label", "In progress"); cross(); },
  };
}
// saveTask().then(() => morph.done());   // reverting is just morph.spin(): every layer has a reverse transition
```

React: the state is a prop (`<StatusBadge state="loading|done">`); calibrate the dash in `useLayoutEffect` (before first paint), pulse the crossing class in an effect on state change, skipping mount.

---

## 10. Error shake (form validation)

**When**: invalid field, wrong PIN, duplicate name — "this is wrong, try again" without an alert. Tier: occasional. **Purpose**: feedback. Shake **once**.

```html
<div class="aim-field">
  <div class="aim-input"><input type="email" placeholder="you@example.com"></div>
  <p class="aim-error-msg">Please enter a valid email.</p>
</div>
```

```css
.aim-input { transition: border-color var(--motion-quick) var(--ease-out); will-change: transform; border: 1px solid rgb(0 0 0 / 0.14); border-radius: 8px; }
.aim-input.is-error { border-color: var(--danger, #e5484d); transition: border-color 280ms var(--ease-out); }
.aim-error-msg { opacity: 0; visibility: hidden; color: var(--danger, #e5484d); transition: opacity 280ms var(--ease-out), visibility 0s linear 280ms; }
.aim-field.is-error .aim-error-msg { opacity: 1; visibility: visible; transition: opacity 280ms var(--ease-out), visibility 0s linear 0s; }
/* legs: A A B B = 80 80 60 60 = 280ms → stops at 28.57 / 57.14 / 78.57 %. Recompute if you change the legs. */
.aim-input.is-shaking { animation: aim-shake 280ms linear; }
@keyframes aim-shake {
  0%     { transform: translateX(0);    animation-timing-function: var(--ease-out); }
  28.57% { transform: translateX(6px);  animation-timing-function: var(--ease-out); }
  57.14% { transform: translateX(-6px); animation-timing-function: var(--ease-out); }
  78.57% { transform: translateX(4px);  animation-timing-function: var(--ease-out); }
  100%   { transform: translateX(0); }
}
@media (prefers-reduced-motion: reduce) { .aim-input { animation: none !important; transform: none !important; } }
```

```js
function showError(field) {
  const input = field.querySelector(".aim-input");
  field.classList.add("is-error"); input.classList.add("is-error");
  input.classList.remove("is-shaking"); void input.offsetWidth; input.classList.add("is-shaking");   // replay
  setTimeout(() => input.classList.remove("is-shaking"), 300);
  clearTimeout(field._revert);
  field._revert = setTimeout(() => { field.classList.remove("is-error"); input.classList.remove("is-error"); }, 3300);
  field.querySelector("input").addEventListener("input", () => { clearTimeout(field._revert); field.classList.remove("is-error"); input.classList.remove("is-error"); }, { once: true });
}
```

Keep `.is-error` (treatment) and `.is-shaking` (one-shot) separate so the shake can replay without flickering the border. Validate on blur, never while typing. Reduced motion: colour pulse instead of shake.

---

## 11. Hold to confirm (asymmetric fill)

**When**: destructive actions where a plain click is too easy. Tier: rare. **Purpose**: feedback + preventing accidents. Linear fill = honest progress.

```html
<button class="aim-hold"><span class="aim-hold-fill" aria-hidden="true"></span><span>Hold to delete</span></button>
```

```css
.aim-hold { position: relative; overflow: hidden; isolation: isolate; transition: transform var(--motion-quick) var(--ease-out); }
.aim-hold > span:last-child { position: relative; }
.aim-hold-fill {
  position: absolute; inset: 0; background: var(--danger, #e5484d); opacity: 0.25;
  clip-path: inset(0 100% 0 0);
  transition: clip-path var(--motion-fast) var(--ease-out);        /* release: snappy */
}
.aim-hold:active { transform: scale(var(--scale-press)); }
.aim-hold:active .aim-hold-fill { clip-path: inset(0 0 0 0); transition: clip-path 2s linear; }   /* press: slow, deliberate */
@media (prefers-reduced-motion: reduce) { .aim-hold:active { transform: none; } }
```

```js
let timer;
btn.addEventListener("pointerdown", () => { timer = setTimeout(confirm, 2000); });
["pointerup", "pointerleave", "pointercancel"].forEach((e) => btn.addEventListener(e, () => clearTimeout(timer)));
```

Tailwind: `transition-[clip-path] ease-out duration-200 active:duration-[2000ms]`.

---

## 12. Inline confirmation (swap controls in place)

**When**: a destructive row action that should ask inline instead of opening a modal. Tier: occasional. **Purpose**: preventing a jarring change.

```html
<div class="aim-row">
  <span class="aim-row-meta">2 h 14 min · yesterday</span>
  <div class="aim-row-actions" data-mode="idle">
    <div class="aim-row-set" data-set="idle"><button>Edit</button><button class="danger">Delete</button></div>
    <div class="aim-row-set" data-set="confirm"><span>Delete?</span><button>Cancel</button><button class="danger">Delete</button></div>
  </div>
</div>
```

```css
.aim-row-actions { display: inline-grid; }
.aim-row-set { grid-area: 1 / 1; display: inline-flex; gap: 6px; align-items: center; transform-origin: 50% 0;
  transition: opacity var(--spring-open-duration) var(--spring-open-easing), filter var(--spring-open-duration) var(--spring-open-easing), transform var(--spring-open-duration) var(--spring-open-easing); }
.aim-row-actions[data-mode="idle"] [data-set="confirm"],
.aim-row-actions[data-mode="confirm"] [data-set="idle"] {
  opacity: 0; pointer-events: none;
  filter: blur(calc(var(--blur-max) * var(--motion-blur-scale)));
  transform: perspective(var(--motion-fold-perspective)) rotateX(-12deg) scaleX(0.8);
}
/* Hide secondary details at the same moment so the question takes their room and nothing jumps. */
.aim-row-meta { transition: opacity var(--spring-open-duration) var(--spring-open-easing); }
.aim-row:has([data-mode="confirm"]) .aim-row-meta { opacity: 0; }
@media (prefers-reduced-motion: reduce) { .aim-row-set { filter: none; transform: none; transition: opacity var(--motion-quick) var(--ease-out); } }
```

Same "element" fold as the content-swap catalog; reverse on Cancel by flipping `data-mode`.

---

## 13. Success line (status text swap)

**When**: after an action completes, replace the status line with "✓ Saved" and swap back after ~2.4s. Tier: occasional. Uses the element transition above on a single line: set `data-mode`, `setTimeout(back, 2400)`. Colour the success copy with the accent, keep the width reserved by the longest state.

---

## 14. "Learn more" chevron → arrow

**When**: inline links/buttons with a trailing chevron. Tier: tens/day → a 2px shift and 8° spread is the whole effect. Hover-only; keyboard and touch lose nothing.

```html
<a class="aim-learn" href="#">Learn more
  <span class="aim-learn-chevron"><svg viewBox="0 0 16 16" width="16" height="16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round">
    <path class="aim-arm aim-arm-top" d="M6 4L10 8"/><path class="aim-arm aim-arm-bot" d="M10 8L6 12"/></svg></span>
</a>
```

```css
.aim-learn { display: inline-flex; align-items: center; gap: 4px; }
.aim-learn-chevron { display: inline-flex; transition: transform var(--motion-medium) var(--ease-out); }
.aim-arm { transform-box: view-box; transform-origin: 10px 8px; vector-effect: non-scaling-stroke; transition: transform var(--motion-medium) var(--ease-out); }
@media (hover: hover) and (pointer: fine) {
  .aim-learn:hover .aim-learn-chevron { transform: translateX(2px); }
  .aim-learn:hover .aim-arm-top { transform: rotate(8deg); }
  .aim-learn:hover .aim-arm-bot { transform: rotate(-8deg); }
}
@media (prefers-reduced-motion: reduce) { .aim-learn-chevron, .aim-arm { transition: none; } }
```

---

## 15. Button loading state

**When**: any async submit. Tier: occasional. **Purpose**: immediate feedback. Label fades to a spinner (150ms), `aria-busy`, pointer events off; success morphs the spinner into a check (icon swap); label returns after ~2s.

```html
<button class="aim-async" data-state="idle" aria-busy="false">
  <span class="aim-async-slot"><span data-s="idle">Save</span><span data-s="loading"><i class="aim-spinner"></i></span><span data-s="done">✓ Saved</span></span>
</button>
```

```css
.aim-async { position: relative; }
.aim-async[data-state="loading"] { pointer-events: none; }
.aim-async-slot { display: inline-grid; }
.aim-async-slot > span { grid-area: 1 / 1; display: inline-flex; justify-content: center; align-items: center; gap: 6px;
  transition: opacity var(--motion-quick) var(--ease-swap), filter var(--motion-quick) var(--ease-swap), transform var(--motion-quick) var(--ease-swap); }
.aim-async:not([data-state="idle"]) [data-s="idle"], .aim-async:not([data-state="loading"]) [data-s="loading"], .aim-async:not([data-state="done"]) [data-s="done"] {
  opacity: 0; filter: blur(var(--blur-small)); transform: scale(0.9); }
.aim-spinner { width: 14px; height: 14px; border-radius: 50%; border: 2px solid rgb(0 0 0 / 0.15); border-top-color: currentColor; animation: aim-spin 800ms linear infinite; }
@keyframes aim-spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .aim-async-slot > span { filter: none; transform: none; } .aim-spinner { animation-duration: 1.6s; } }
```

```js
btn.dataset.state = "loading"; btn.setAttribute("aria-busy", "true");
await save();
btn.dataset.state = "done"; btn.setAttribute("aria-busy", "false");
setTimeout(() => (btn.dataset.state = "idle"), 2000);
```

---

## 16. Focus ring — do not animate

`:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }` appears instantly. Keyboard users move fast; a ring that fades in lags behind them.
