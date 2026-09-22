# Catalog · Content swap — text, icons, numbers, folds, streaming

Rule: animate what you swap, not the container. Reserve the space so neighbours never shift. Swaps are symmetric (same duration both ways) and use `--ease-swap`; old leaves up, new arrives from below.

---

## 1. Text states swap ("Processing…" → "Done")

Tier: tens/day → 150ms, 4px, 2px blur. Old text exits up, new text enters from below.

```html
<span class="aim-textswap">Processing…</span>
```

```css
.aim-textswap { display: inline-block; transform: translateY(0); filter: blur(0); opacity: 1; will-change: transform, filter, opacity;
  transition: transform var(--motion-quick) var(--ease-swap), filter var(--motion-quick) var(--ease-swap), opacity var(--motion-quick) var(--ease-swap); }
.aim-textswap.is-exit { transform: translateY(calc(var(--move-micro) * -1)); filter: blur(calc(var(--blur-small) * var(--motion-blur-scale))); opacity: 0; }
.aim-textswap.is-enter-start { transform: translateY(var(--move-micro)); filter: blur(calc(var(--blur-small) * var(--motion-blur-scale))); opacity: 0; transition: none; }
@media (prefers-reduced-motion: reduce) { .aim-textswap { transition: opacity var(--motion-quick) var(--ease-out); transform: none !important; filter: none !important; } }
```

```js
function swapText(el, next) {
  const dur = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--motion-quick")) || 150;
  el.classList.add("is-exit");
  setTimeout(() => {
    el.textContent = next; el.classList.remove("is-exit"); el.classList.add("is-enter-start");
    void el.offsetHeight;                                  // reflow, then release → animates back to rest
    el.classList.remove("is-enter-start");
  }, dur);
}
```

Keep the container's width reserved by the longest state (a hidden sizer) so the line does not resize mid-swap.

---

## 2. Icon swap (hamburger ↔ close, copy ↔ check, play ↔ pause)

Tier: tens/day → 250ms symmetric. Both icons stay in the DOM in one grid cell.

```html
<span class="aim-iconswap" data-state="a"><span class="aim-icon" data-icon="a">☰</span><span class="aim-icon" data-icon="b">✕</span></span>
```

```css
.aim-iconswap { display: inline-grid; }
.aim-iconswap .aim-icon { grid-area: 1 / 1; display: grid; place-items: center;
  transition: opacity var(--motion-fast) var(--ease-swap), filter var(--motion-fast) var(--ease-swap), transform var(--motion-fast) var(--ease-swap); will-change: opacity, filter, transform; }
.aim-iconswap[data-state="a"] [data-icon="a"], .aim-iconswap[data-state="b"] [data-icon="b"] { opacity: 1; filter: blur(0); transform: scale(1); }
.aim-iconswap[data-state="a"] [data-icon="b"], .aim-iconswap[data-state="b"] [data-icon="a"] { opacity: 0; filter: blur(calc(var(--blur-small) * var(--motion-blur-scale))); transform: scale(0.25); }
@media (prefers-reduced-motion: reduce) { .aim-iconswap .aim-icon { transform: none !important; filter: none !important; } }
```

Motion-library version: `<AnimatePresence mode="wait">` with `initial/animate/exit` on `{ opacity, scale: 0.8, filter: blur(4px) }`. Instant swaps get missed; the blur + scale makes the state change register.

---

## 3. Number pop-in (each digit re-enters, last two stagger)

Tier: occasional. Counters, prices, balances that update and deserve a small moment.

```html
<span class="aim-digits is-animating"><span class="aim-digit">1</span><span class="aim-digit">2</span><span class="aim-digit" data-stagger="1">.</span><span class="aim-digit" data-stagger="2">3</span></span>
```

```css
.aim-digits { display: inline-flex; align-items: baseline; font-variant-numeric: tabular-nums; }
.aim-digit { display: inline-block; will-change: transform, opacity, filter; }
@keyframes aim-digit-in { 0% { transform: translateY(var(--move-base)); opacity: 0; filter: blur(calc(var(--blur-small) * var(--motion-blur-scale))); } 100% { transform: none; opacity: 1; filter: blur(0); } }
.aim-digits.is-animating .aim-digit { animation: aim-digit-in var(--motion-deliberate) var(--ease-bounce) both; }
.aim-digits.is-animating .aim-digit[data-stagger="1"] { animation-delay: 70ms; }
.aim-digits.is-animating .aim-digit[data-stagger="2"] { animation-delay: 140ms; }
@media (prefers-reduced-motion: reduce) { .aim-digits .aim-digit { animation: none !important; } }
```

```js
function setDigits(group, str) {
  group.classList.remove("is-animating"); group.replaceChildren();
  [...str].forEach((ch, i, a) => { const s = document.createElement("span"); s.className = "aim-digit"; s.textContent = ch; if (i === a.length - 2) s.dataset.stagger = "1"; if (i === a.length - 1) s.dataset.stagger = "2"; group.appendChild(s); });
  void group.offsetHeight; group.classList.add("is-animating");
}
```

---

## 4. Rolling number (only the changed characters move)

Tier: tens/day+ (timers, live prices) → the quiet one: 7px rise through a 3px blur on the `state` spring, one cell per character, tabular figures so nothing else moves.

```css
.aim-roll { display: inline-flex; font-variant-numeric: tabular-nums; }
.aim-digitcell { display: inline-grid; }
.aim-digitcell > * { grid-area: 1 / 1; }
@keyframes aim-roll-in  { from { opacity: 0; filter: blur(3px); transform: translateY(7px); } }
@keyframes aim-roll-out { to   { opacity: 0; filter: blur(3px); transform: translateY(-7px); } }
.aim-roll-in  { animation: aim-roll-in  var(--spring-state-duration) var(--spring-state-easing) both; }
.aim-roll-out { animation: aim-roll-out var(--spring-state-duration) var(--spring-state-easing) both; }
@media (prefers-reduced-motion: reduce) { .aim-roll-in, .aim-roll-out { animation-duration: var(--motion-quick); filter: none; transform: none; } }
```

```js
function rollDigits(el, text) {                          // also in motion.ts (WAAPI version)
  const cells = [...el.children];
  while (cells.length > text.length) cells.pop().remove();
  [...text].forEach((ch, i) => {
    let cell = cells[i];
    if (!cell) { cell = document.createElement("span"); cell.className = "aim-digitcell"; el.appendChild(cell); cells.push(cell); }
    const cur = cell.lastElementChild;
    if (cur?.textContent === ch) return;                  // unchanged: nothing moves
    const next = document.createElement("span"); next.textContent = ch; next.className = "aim-roll-in"; cell.appendChild(next);
    if (cur) { cur.className = "aim-roll-out"; cur.addEventListener("animationend", () => cur.remove(), { once: true }); }
  });
  el.setAttribute("aria-label", text);
}
```

---

## 5. Spinning counter (slot-machine reels)

Tier: rare (jackpot moments: points, KPIs revealed). Each digit is a clipped vertical strip of 0–9; the strip translates up through several full spins before landing, columns stagger 90ms, a vertical-only blur streaks while moving (CSS `blur()` would smear sideways — use an SVG `feGaussianBlur stdDeviation="0 Y"`, decayed to 0 per column as it settles).

```html
<svg width="0" height="0" style="position:absolute" aria-hidden="true"><filter id="aim-vblur"><feGaussianBlur stdDeviation="0 3"/></filter></svg>
<div class="aim-reel" aria-live="polite"></div>
```

```css
.aim-reel { display: inline-flex; height: 30px; font-variant-numeric: tabular-nums; font-size: 22px; font-weight: 600; }
.aim-reel-col { position: relative; height: 30px; overflow: hidden; width: 0.65em;
  mask-image: linear-gradient(to bottom, transparent 0%, #000 22%, #000 78%, transparent 100%); }
.aim-reel-strip { display: flex; flex-direction: column; will-change: transform, filter; }
.aim-reel-digit { height: 30px; display: grid; place-items: center; }
@media (prefers-reduced-motion: reduce) { .aim-reel-strip { transition: none !important; filter: none !important; } }
```

```js
function spinTo(reel, value, { spins = 2, cell = 30, dur = 1400, stagger = 90 } = {}) {
  const digits = String(value).split("");
  reel.replaceChildren();
  digits.forEach((d, col) => {
    const colEl = document.createElement("div"); colEl.className = "aim-reel-col";
    const strip = document.createElement("div"); strip.className = "aim-reel-strip";
    const total = spins * 10 + Number(d);
    for (let i = 0; i <= total; i++) { const c = document.createElement("div"); c.className = "aim-reel-digit"; c.textContent = i % 10; strip.appendChild(c); }
    colEl.appendChild(strip); reel.appendChild(colEl);
    const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) { strip.style.transform = `translateY(-${total * cell}px)`; return; }
    strip.style.filter = "url(#aim-vblur)";
    requestAnimationFrame(() => {
      strip.style.transition = `transform ${dur}ms var(--ease-out-expo) ${col * stagger}ms`;
      strip.style.transform = `translateY(-${total * cell}px)`;
      setTimeout(() => (strip.style.filter = "none"), dur * 0.7 + col * stagger);   // blur decays as the reel settles
    });
  });
  reel.setAttribute("aria-label", String(value));
}
```

Prefer number pop-in for quiet updates and the rolling number for frequent ones; the reel is an event.

---

## 6. Fold transitions: element / unfold / side

Spring-driven swaps for a control, label or status line appearing inside a card, row or toolbar. Blur follows the budget; folds go flat under reduced motion.

```css
/* element: opacity 0→1, blur 14→0, scaleX 0.8→1, rotateX −12°→0 hinged at the top. Enter and leave on `open`. */
@keyframes aim-element {
  from { opacity: 0; filter: blur(calc(var(--blur-max) * var(--motion-blur-scale))); transform: perspective(var(--motion-fold-perspective)) rotateX(var(--fold, -12deg)) scaleX(0.8); }
  to   { opacity: 1; filter: blur(0); transform: perspective(var(--motion-fold-perspective)) rotateX(0) scaleX(1); }
}
.aim-element-in  { transform-origin: 50% 0; animation: aim-element var(--spring-open-duration) var(--spring-open-easing) both; }
.aim-element-out { transform-origin: 50% 0; animation: aim-element var(--spring-open-duration) var(--spring-open-easing) reverse both; }

/* unfold: content swapped at a top edge (a toast's message, a banner, a menu header). In folds; out just fades + blurs in 100ms. */
@keyframes aim-unfold-in  { from { opacity: 0; filter: blur(calc(12px * var(--motion-blur-scale))); transform: perspective(var(--motion-fold-perspective)) rotateX(var(--fold, -12deg)); } to { opacity: 1; filter: blur(0); transform: perspective(var(--motion-fold-perspective)) rotateX(0); } }
@keyframes aim-unfold-out { from { opacity: 1; filter: blur(0); } to { opacity: 0; filter: blur(calc(12px * var(--motion-blur-scale))); } }
.aim-unfold-in  { transform-origin: 50% 0; animation: aim-unfold-in var(--spring-open-duration) var(--spring-open-easing) both; }
.aim-unfold-out { animation: aim-unfold-out 100ms var(--ease-exit) both; }

/* side: collapsing into an edge and growing back out of it (one half of a split toolbar). */
@keyframes aim-side { from { opacity: 0; filter: blur(calc(10px * var(--motion-blur-scale))); transform: scaleX(0); } to { opacity: 1; filter: blur(0); transform: scaleX(1); } }
.aim-side-from-left-in  { transform-origin: 0 50%;   animation: aim-side var(--spring-open-duration) var(--spring-open-easing) both; }
.aim-side-from-right-in { transform-origin: 100% 50%; animation: aim-side var(--spring-open-duration) var(--spring-open-easing) both; }
.aim-side-to-left-out   { transform-origin: 0 50%;   animation: aim-side var(--spring-open-duration) var(--spring-open-easing) reverse both; }
.aim-side-to-right-out  { transform-origin: 100% 50%; animation: aim-side var(--spring-open-duration) var(--spring-open-easing) reverse both; }

@media (prefers-reduced-motion: reduce) { :root { --fold: 0deg; } }
```

Vue: `<Transition enter-active-class="aim-element-in" leave-active-class="aim-element-out" mode="out-in">`. WAAPI: `el.animate(transitions.element(), waapi("open"))`. Motion: `initial/animate/exit` with `{ opacity, filter, scaleX, rotateX }` and `transformPerspective: 600`.

---

## 7. Skeleton → content reveal

Tier: occasional. The skeleton pulses, then both layers cross-fade with a matching cross-blur in the same slot — layout-free.

```html
<div class="aim-skel" data-state="loading">
  <div class="aim-skel-ghost is-pulsing"><i class="aim-skel-avatar"></i><i class="aim-skel-line"></i><i class="aim-skel-line short"></i></div>
  <div class="aim-skel-content">…real row…</div>
</div>
```

```css
.aim-skel { position: relative; }
.aim-skel-ghost, .aim-skel-content { position: absolute; inset: 0; }
.aim-skel-ghost { z-index: 1; opacity: 1; filter: blur(0); transition: opacity var(--motion-slow) var(--ease-swap), filter var(--motion-slow) var(--ease-swap); }
.aim-skel-content { z-index: 2; opacity: 0; filter: blur(calc(var(--blur-small) * var(--motion-blur-scale))); transition: opacity var(--motion-slow) var(--ease-swap), filter var(--motion-slow) var(--ease-swap); }
.aim-skel.is-revealed .aim-skel-ghost { opacity: 0; filter: blur(calc(var(--blur-small) * var(--motion-blur-scale))); }
.aim-skel.is-revealed .aim-skel-content { opacity: 1; filter: blur(0); }
.aim-skel.is-resetting .aim-skel-ghost, .aim-skel.is-resetting .aim-skel-content { transition: none !important; }   /* replay without animating the reverse */
/* pulse on the children, so the ghost's own opacity/filter stay free for the cross-fade */
.aim-skel-ghost.is-pulsing > * { animation: aim-skel-pulse 1s ease-in-out infinite; }
@keyframes aim-skel-pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
.aim-skel-avatar, .aim-skel-line { background: rgb(0 0 0 / 0.08); border-radius: 6px; display: block; }
@media (prefers-reduced-motion: reduce) { .aim-skel-ghost, .aim-skel-content { transition: opacity var(--motion-quick) var(--ease-out); filter: none !important; } .aim-skel-ghost.is-pulsing > * { animation-duration: 2s; } }
```

```js
function reveal(skel) { skel.classList.add("is-revealed"); }
function replay(skel) { skel.classList.add("is-resetting"); skel.classList.remove("is-revealed"); void skel.offsetWidth; skel.classList.remove("is-resetting"); setTimeout(() => skel.classList.add("is-revealed"), 1000); }
```

---

## 8. Image-generation placeholder (breathing dot lattice)

Tier: occasional. Three states on the card: idle (a *frozen frame* of the loader, not a flat grid), `.is-loading` (every dot breathes on its own baked tempo and negative phase, so it wakes up rather than boots up), `.is-revealed` (field blurs away as the image blurs in).

```html
<div class="aim-imgen"><span class="aim-imgen-field" aria-hidden="true"></span><img class="aim-imgen-img" alt="Generated image"></div>
```

```css
.aim-imgen { position: relative; width: 142px; height: 142px; border-radius: 12px; background: #eaeaea; overflow: hidden; isolation: isolate; }
.aim-imgen-field { position: absolute; inset: 0; pointer-events: none; transition: opacity 650ms var(--ease-out), filter 650ms var(--ease-out); }
.aim-imgen-img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; opacity: 0; filter: blur(3px); transition: opacity 650ms var(--ease-out), filter 650ms var(--ease-out); }
.aim-imgen.is-revealed .aim-imgen-field { opacity: 0; filter: blur(3px); }
.aim-imgen.is-revealed .aim-imgen-img { opacity: 1; filter: blur(0); }
.aim-imgen-field i { position: absolute; width: 1.5px; height: 1.5px; margin: -0.75px 0 0 -0.75px; border-radius: 50%; background: rgb(0 0 0 / 0.28);
  opacity: var(--v, 1); transform: scale(var(--v, 1)); }
.aim-imgen.is-loading .aim-imgen-field i { animation: aim-imgen-twinkle calc(1400ms * var(--k, 1)) ease-in-out var(--delay, 0ms) infinite; }
/* motion-ok: a loader dot vanishing and returning, not an element entering */
@keyframes aim-imgen-twinkle { 0%, 100% { opacity: 0; transform: scale(0); } 50% { opacity: 1; transform: scale(1); } }
@media (prefers-reduced-motion: reduce) { .aim-imgen.is-loading .aim-imgen-field i { animation: none !important; } .aim-imgen-field, .aim-imgen-img { filter: none !important; transition: opacity var(--motion-quick) var(--ease-out); } }
```

```js
function createImgen(card, { pitch = 5, spread = 0.1, phase = 6000, cycle = 1400 } = {}) {
  const field = card.querySelector(".aim-imgen-field");
  function build() {
    field.textContent = "";
    const size = field.clientWidth || 142, n = Math.max(1, Math.floor(size / pitch)), off = (size - (n - 1) * pitch) / 2;
    for (let r = 0; r < n; r++) for (let c = 0; c < n; c++) {
      const d = document.createElement("i");
      d.style.left = off + c * pitch + "px"; d.style.top = off + r * pitch + "px";
      const k = 1 - spread + Math.random() * spread * 2, offset = Math.random() * phase;
      d.style.setProperty("--k", k.toFixed(3)); d.style.setProperty("--delay", Math.round(-offset) + "ms");
      const frac = (offset % (cycle * k)) / (cycle * k);
      d.style.setProperty("--v", (0.5 - 0.5 * Math.cos(frac * Math.PI * 2)).toFixed(3));   // frozen frame = where its phase would be
      field.appendChild(d);
    }
  }
  build();
  return { build, load() { card.classList.remove("is-revealed"); card.classList.add("is-loading"); },
           reveal() { card.classList.remove("is-loading"); card.classList.add("is-revealed"); },
           reset() { card.classList.remove("is-loading", "is-revealed"); } };
}
// img.onload = () => ph.reveal(); img.src = url;   // reveal only once the bytes are there
```

---

## 9. Streaming text (words resolve through a soft blur)

Tier: occasional. Model output arriving word by word; each word condenses into place (opacity + 1px blur, 350ms) one every 60ms — reads as resolution, not keystrokes.

```css
.aim-stream-w { opacity: 0; filter: blur(calc(1px * var(--motion-blur-scale))); transition: opacity var(--motion-medium) var(--ease-out), filter var(--motion-medium) var(--ease-out); }
.aim-stream-w.is-in { opacity: 1; filter: blur(0); }
@media (prefers-reduced-motion: reduce) { .aim-stream-w { transition: opacity var(--motion-quick) var(--ease-out); filter: none; } }
```

```js
function streamInto(block, text, gap = 60) {
  block.textContent = "";
  const spans = text.split(/\s+/).map((w, i, a) => { const s = document.createElement("span"); s.className = "aim-stream-w"; s.textContent = w; block.appendChild(s); if (i < a.length - 1) block.appendChild(document.createTextNode(" ")); return s; });
  spans.forEach((s, i) => setTimeout(() => s.classList.add("is-in"), i * gap));
}
// For real streams: append a span per received token and add .is-in on the next frame.
```

---

## 10. Thinking states (shimmer while holding, swap on change)

Tier: occasional. An AI status line ("Setting up a workspace" → "Running a command") that shimmers while a state holds and swaps with the text-swap motion. A hidden sizer holds the longest state so the box never resizes.

```html
<span class="aim-think" role="status"><span class="aim-think-sizer" aria-hidden="true">Setting up a workspace</span><span class="aim-think-text" data-text="Thinking…">Thinking…</span></span>
```

```css
.aim-think { position: relative; display: inline-block; text-align: center; }
.aim-think-sizer { display: block; visibility: hidden; white-space: nowrap; }
.aim-think-text { position: absolute; inset: 0 0 auto 0; display: block; color: var(--shimmer-base, #7c7c7c); white-space: nowrap; transform: translateY(0); filter: blur(0); opacity: 1; will-change: transform, filter, opacity;
  transition: transform var(--motion-quick) var(--ease-swap), filter var(--motion-quick) var(--ease-swap), opacity var(--motion-quick) var(--ease-swap); }
.aim-think-text::before { content: attr(data-text); position: absolute; inset: 0; pointer-events: none;
  background-image: linear-gradient(90deg, transparent 0 40%, var(--shimmer-highlight, #0d0d0d) 50%, transparent 60% 100%);
  background-size: 400% 100%; background-repeat: no-repeat; -webkit-background-clip: text; background-clip: text; color: transparent; -webkit-text-fill-color: transparent;
  animation: aim-shimmer 2s linear infinite; }
@keyframes aim-shimmer { 0% { background-position: 100% 0; } 100% { background-position: 0% 0; } }
.aim-think-text.is-exit { transform: translateY(calc(var(--move-base) * -1)); filter: blur(calc(var(--blur-small) * var(--motion-blur-scale))); opacity: 0; }
.aim-think-text.is-enter-start { transition: none; transform: translateY(var(--move-base)); filter: blur(calc(var(--blur-small) * var(--motion-blur-scale))); opacity: 0; }
@media (prefers-reduced-motion: reduce) { .aim-think-text { transition: opacity var(--motion-quick) var(--ease-out); transform: none !important; filter: none !important; } .aim-think-text::before { display: none; } }
```

```js
function setThinking(box, next, gap = 50) {
  const live = box.querySelector(".aim-think-text:not(.is-exit)");
  live.classList.add("is-exit");
  const n = document.createElement("span"); n.className = "aim-think-text is-enter-start"; n.textContent = next; n.dataset.text = next; box.appendChild(n);
  setTimeout(() => { void n.offsetWidth; n.classList.remove("is-enter-start"); }, gap);
  setTimeout(() => live.remove(), 150 + gap);
}
```

---

## 11. Reasoning stream (transcript stepping up two lines)

Tier: occasional. A card clips a tall transcript; JS steps it up N lines every hold; the transcript is cloned once so the wrap never jumps. Edge fades are a mask on the viewport so the card background can be anything.

```html
<div class="aim-reason"><div class="aim-reason-viewport"><div class="aim-reason-scroll"><div class="aim-reason-text"><p>…</p></div></div></div></div>
```

```css
.aim-reason { position: relative; height: 96px; overflow: hidden; }
.aim-reason-viewport { position: absolute; inset: 0; overflow: hidden; mask-image: linear-gradient(transparent 0, #000 28px, #000 calc(100% - 28px), transparent 100%); }
.aim-reason-scroll { position: absolute; left: 0; right: 0; transform: translateY(0); will-change: transform; }
@media (prefers-reduced-motion: reduce) { .aim-reason-scroll { transition: none !important; } }
```

```js
function startReasoning(root, { hold = 840, step = 500, lines = 2 } = {}) {
  const scroll = root.querySelector(".aim-reason-scroll"), text = scroll.querySelector(".aim-reason-text");
  scroll.appendChild(text.cloneNode(true));
  let offset = 0, alive = true;
  (function tick() {
    if (!alive) return;
    setTimeout(() => {
      const lineH = parseFloat(getComputedStyle(text).lineHeight) || 18;
      offset += lineH * lines;
      scroll.style.transition = `transform ${step}ms var(--ease-out)`; scroll.style.transform = `translateY(${-offset}px)`;
      setTimeout(() => { const h = text.offsetHeight; if (offset >= h) { offset -= h; scroll.style.transition = "none"; scroll.style.transform = `translateY(${-offset}px)`; void scroll.offsetWidth; } tick(); }, step + 30);
    }, hold);
  })();
  return () => (alive = false);
}
```
