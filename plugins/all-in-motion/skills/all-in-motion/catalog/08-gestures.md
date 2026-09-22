# Catalog · Gestures — drag, swipe, tilt, physics

All gesture code follows `05-interaction-patterns.md §4`: pointer capture, multi-touch guard, direct style writes while dragging (no transition), damping past edges, momentum dismissal by velocity, springs on release, `touch-action: none` on the dragged element only. The `press` / `release` / `drag` springs stay under reduced motion (they follow the hand); decorative extras (smoke, tilt, particles) do not.

---

## 1. Drag to dismiss (toast / card)

```html
<div class="aim-dismiss" role="status">Message archived <button>Undo</button></div>
```

```css
.aim-dismiss { touch-action: pan-x; user-select: none; will-change: transform;
  transition: transform var(--spring-release-duration) var(--spring-release-easing), opacity var(--motion-fast) var(--ease-out); }
.aim-dismiss.is-dragging { transition: none; }
.aim-dismiss.is-gone { opacity: 0; transition: transform var(--motion-fast) var(--ease-out), opacity var(--motion-fast) var(--ease-out); }
@media (prefers-reduced-motion: reduce) { .aim-dismiss.is-gone { transform: none !important; } }
```

```js
function dragToDismiss(el, { axis = "y", threshold = 80, velocity = 0.11, onDismiss } = {}) {
  let id = null, start = 0, d = 0, t0 = 0, samples = [];
  const prop = axis === "y" ? "clientY" : "clientX";
  const write = (v) => (el.style.transform = axis === "y" ? `translateY(${v}px)` : `translateX(${v}px)`);
  el.addEventListener("pointerdown", (e) => {
    if (id !== null) return;                                        // a second finger must not restart the drag
    id = e.pointerId; start = e[prop]; t0 = performance.now(); samples = [];
    el.setPointerCapture(id); el.classList.add("is-dragging");
  });
  el.addEventListener("pointermove", (e) => {
    if (e.pointerId !== id) return;
    d = e[prop] - start;
    if (d < 0) d = d * 0.3;                                         // "wrong" direction: friction, not a wall
    write(d);
    samples.push({ t: performance.now(), d }); while (samples.length > 1 && performance.now() - samples[0].t > 100) samples.shift();
  });
  const end = (e) => {
    if (e.pointerId !== id) return;
    id = null; el.classList.remove("is-dragging");
    const a = samples[0], b = samples[samples.length - 1];
    const v = a && b ? (b.d - a.d) / Math.max(b.t - a.t, 1) : 0;    // px/ms
    if (d >= threshold || v > velocity) {                           // distance OR a flick
      write(d + 200); el.classList.add("is-gone");                  // exit the way it moved
      setTimeout(() => onDismiss?.(), 260);
    } else write(0);                                                // spring home on `release`
  };
  el.addEventListener("pointerup", end); el.addEventListener("pointercancel", end);
}
```

---

## 2. Swipe actions on a list row

Reveal an action area behind a row as it is dragged; thresholds tick (haptic on mobile); release past the threshold commits, before it springs back.

```html
<div class="aim-swipe"><div class="aim-swipe-actions"><button>Archive</button></div><div class="aim-swipe-row">Inbox message</div></div>
```

```css
.aim-swipe { position: relative; overflow: hidden; }
.aim-swipe-actions { position: absolute; inset: 0 0 0 auto; display: flex; align-items: center; padding: 0 12px; background: var(--accent, #2563eb); color: #fff;
  opacity: 0; transition: opacity var(--motion-quick) var(--ease-out); }
.aim-swipe.is-revealed .aim-swipe-actions { opacity: 1; }
.aim-swipe-actions button { transform: scale(0.8); opacity: 0; transition: transform var(--spring-emphasis-duration) var(--spring-emphasis-easing), opacity var(--motion-quick) var(--ease-out); }
.aim-swipe.is-armed .aim-swipe-actions button { transform: scale(1); opacity: 1; }     /* threshold crossed */
.aim-swipe-row { position: relative; background: #fff; touch-action: pan-y; user-select: none; will-change: transform;
  transition: transform var(--spring-release-duration) var(--spring-release-easing); }
.aim-swipe.is-dragging .aim-swipe-row { transition: none; }
.aim-swipe.is-committed .aim-swipe-row { transform: translateX(-100%); transition: transform var(--motion-fast) var(--ease-out); }
```

```js
function wireSwipe(root, { armAt = 72, onCommit } = {}) {
  const row = root.querySelector(".aim-swipe-row"); let id = null, x0 = 0, dx = 0, t0 = 0, x1 = 0;
  row.addEventListener("pointerdown", (e) => { if (id !== null) return; id = e.pointerId; x0 = e.clientX; t0 = performance.now(); row.setPointerCapture(id); root.classList.add("is-dragging", "is-revealed"); });
  row.addEventListener("pointermove", (e) => {
    if (e.pointerId !== id) return;
    dx = Math.min(0, e.clientX - x0); x1 = e.clientX;
    if (dx < -armAt) dx = -armAt - (-dx - armAt) * 0.35;           // damp past the arm point
    row.style.transform = `translateX(${dx}px)`;
    root.classList.toggle("is-armed", dx <= -armAt);
  });
  const end = (e) => {
    if (e.pointerId !== id) return; id = null; root.classList.remove("is-dragging");
    const v = (x0 - x1) / Math.max(performance.now() - t0, 1);
    if (dx <= -armAt || v > 0.5) { root.classList.add("is-committed"); setTimeout(() => onCommit?.(), 260); }
    else { row.style.transform = ""; root.classList.remove("is-revealed", "is-armed"); }
  };
  row.addEventListener("pointerup", end); row.addEventListener("pointercancel", end);
}
```

---

## 3. Drag & drop with weight (velocity tilt, squash landing, smoke)

Tier: occasional/rare (upload targets, canvas slots). The chip follows the finger 1:1, lifts 5% on grab and tilts from horizontal velocity. On a hit the chip does **not** fly or resize: it dissolves where it was let go while the **zone** morphs into the image and plays a squash-and-spring anticipation; a ring of turbulence-warped smoke squeezes out under it. Dropping outside springs the chip home. Reduced motion keeps drag and drop, skips the smoke.

```html
<div class="aim-drop">
  <div class="aim-drop-chip"><img alt="" src="photo.jpg" draggable="false"></div>
  <div class="aim-drop-zone">
    <span class="aim-drop-label">Drag &amp; drop<br>it here</span>
    <img class="aim-drop-dropped" alt="" src="photo.jpg">
    <svg class="aim-drop-puffs" viewBox="0 0 204 204" aria-hidden="true"><g class="aim-drop-puffgroup" filter="url(#aim-drop-smoke)"></g></svg>
  </div>
</div>
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <filter id="aim-drop-smoke" x="-150%" y="-150%" width="400%" height="400%">
    <feTurbulence type="fractalNoise" baseFrequency="0.046 0.046" numOctaves="2" seed="4" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="30" xChannelSelector="R" yChannelSelector="G" result="w"/>
    <feGaussianBlur in="w" stdDeviation="5"/>
  </filter>
</svg>
```

```css
.aim-drop { position: relative; width: 213px; height: 192px; }
.aim-drop-chip { position: absolute; left: 141px; top: 0; width: 72px; height: 72px; border-radius: 12px; overflow: hidden; box-shadow: var(--shadow-float); cursor: grab; z-index: 5;
  touch-action: none; user-select: none;
  translate: var(--dx, 0px) var(--dy, 0px); rotate: var(--tilt, 0deg); scale: var(--lift, 1);   /* three independent clocks */
  transition: scale 200ms var(--ease-out), rotate 150ms ease-out;   /* NO translate transition while dragging */
  will-change: translate, rotate, scale; }
.aim-drop-chip img { width: 100%; height: 100%; object-fit: cover; display: block; pointer-events: none; }
.aim-drop-chip.is-dragging { cursor: grabbing; z-index: 30; }
.aim-drop-chip.is-returning { transition: translate 500ms var(--ease-overshoot), rotate 500ms var(--ease-overshoot), scale 500ms var(--ease-overshoot); }
.aim-drop-chip.is-fading { opacity: 0; filter: blur(2px); transition: opacity 450ms var(--ease-bounce), filter 450ms var(--ease-bounce); pointer-events: none; }
.aim-drop-chip.is-respawning { animation-name: aim-drop-respawn; animation-duration: 250ms; animation-timing-function: var(--ease-out); }
@keyframes aim-drop-respawn { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }
.aim-drop-zone { position: absolute; left: 0; top: 88px; width: 104px; height: 104px; border-radius: 12px; border: 2px dashed rgb(0 0 0 / 0.1); background: rgb(234 234 234 / 0.2);
  transition: border-color 150ms ease, background-color 150ms ease, box-shadow 400ms var(--ease-swap); }
.aim-drop-zone.is-over { border-color: rgb(0 0 0 / 0.28); background: rgb(234 234 234 / 0.55); }
.aim-drop-label { position: absolute; left: 50%; top: 38px; transform: translateX(-50%); width: 76px; font-size: 11px; line-height: 15px; text-align: center; color: #767676; transition: opacity 150ms ease; pointer-events: none; }
.aim-drop-zone.is-over .aim-drop-label { opacity: 0.5; }
.aim-drop-zone.is-filled { border-color: transparent; box-shadow: var(--shadow-float); }
.aim-drop-zone.is-filled .aim-drop-label { opacity: 0; }
.aim-drop-dropped { position: absolute; inset: -2px; width: calc(100% + 4px); height: calc(100% + 4px); object-fit: cover; border-radius: 12px; display: block; opacity: 0; pointer-events: none; transition: opacity 400ms var(--ease-swap); }
.aim-drop-zone.is-filled .aim-drop-dropped { opacity: 1; }
/* squash then spring: two phases, own duration + easing each, second delayed by the first, fill forwards */
@keyframes aim-drop-down { from { transform: scale(1); } to { transform: scale(0.97); } }
@keyframes aim-drop-up   { from { transform: scale(0.97); } to { transform: scale(1); } }
.aim-drop-zone.is-landing { animation-name: aim-drop-down, aim-drop-up; animation-duration: 250ms, 450ms; animation-timing-function: var(--ease-out), var(--ease-out); animation-delay: 0ms, 250ms; animation-fill-mode: forwards, forwards; will-change: transform; }
.aim-drop-zone.is-emptying .aim-drop-dropped { opacity: 0; filter: blur(4px); transition: opacity 400ms var(--ease-out), filter 400ms var(--ease-out); }
.aim-drop-zone.is-emptying { border-color: rgb(0 0 0 / 0.1); box-shadow: 0 0 0 1px transparent; transition: box-shadow 400ms var(--ease-out), border-color 400ms var(--ease-out); }
.aim-drop-puffs { position: absolute; inset: -50px; width: calc(100% + 100px); height: calc(100% + 100px); overflow: visible; pointer-events: none; }
.aim-drop-wave { fill: none; stroke: rgb(122 122 122 / 0.42); opacity: 0; transform: translate(0, 0) scale(0.96); transform-box: fill-box; transform-origin: center; }
@keyframes aim-drop-wave { 0% { opacity: 0; transform: translate(0, 0) scale(0.96); } 16% { opacity: 0.9; } 100% { opacity: 0; transform: translate(0, 10px) scale(var(--wscale, 1.5)); } }
.aim-drop-zone.is-bursting .aim-drop-wave { animation-name: aim-drop-wave; animation-duration: var(--wdur, 1500ms); animation-timing-function: ease-out; animation-delay: var(--wdelay, 0ms); animation-fill-mode: forwards; }
@media (prefers-reduced-motion: reduce) {
  .aim-drop-chip.is-respawning, .aim-drop-zone.is-bursting .aim-drop-wave, .aim-drop-zone.is-landing { animation: none !important; }
  .aim-drop-chip.is-fading, .aim-drop-dropped { transition: none !important; }
}
```

```js
function createDragDrop({ chip, zone, puffs, onDrop, demoRevert = true }) {
  const reduced = matchMedia("(prefers-reduced-motion: reduce)");
  let dragging = false, settling = false, id = null, sx = 0, sy = 0, dx = 0, dy = 0, lastX = 0, lastT = 0;
  const timers = new Set(); const after = (ms, fn) => { const t = setTimeout(() => { timers.delete(t); fn(); }, ms); timers.add(t); };
  const setVars = (x, y, tilt, lift) => { chip.style.setProperty("--dx", x.toFixed(1) + "px"); chip.style.setProperty("--dy", y.toFixed(1) + "px"); if (tilt !== null) chip.style.setProperty("--tilt", tilt.toFixed(2) + "deg"); if (lift !== null) chip.style.setProperty("--lift", String(lift)); };
  const overZone = () => { const c = chip.getBoundingClientRect(), z = zone.getBoundingClientRect(); const cx = c.left + c.width / 2, cy = c.top + c.height / 2; return cx >= z.left && cx <= z.right && cy >= z.top && cy <= z.bottom; };   // centre hit-test
  function buildPuffs() {                                            // ring shells hugging the image outline; the group filter fuses them into one smoke front
    puffs.replaceChildren();
    const count = 1, baseW = 50, dist = 30, travel = 1 + (dist * 2) / zone.offsetWidth;
    for (let w = 0; w < count; w++) {
      const r = document.createElementNS("http://www.w3.org/2000/svg", "rect");
      const sw = Math.max(2, baseW - w * 20), hw = sw / 2;            // SVG stroke straddles its path: inset by half, shrink by a full stroke
      r.setAttribute("class", "aim-drop-wave"); r.setAttribute("x", String(52 + hw)); r.setAttribute("y", String(52 + hw));
      r.setAttribute("width", String(Math.max(1, 100 - sw))); r.setAttribute("height", String(Math.max(1, 100 - sw))); r.setAttribute("rx", String(Math.max(2, 14 - hw))); r.setAttribute("stroke-width", String(sw));
      r.style.setProperty("--wdur", Math.round(1500 * (0.85 + w * 0.28)) + "ms"); r.style.setProperty("--wdelay", w * 150 + "ms"); r.style.setProperty("--wscale", (travel + w * 0.07).toFixed(3));
      puffs.appendChild(r);
    }
  }
  function land() {
    zone.classList.add("is-filled", "is-landing");
    if (!reduced.matches) { buildPuffs(); after(250, () => zone.classList.add("is-bursting")); }   // smoke squeezes out at the bottom of the squash
    onDrop?.();
    if (!demoRevert) return;
    after(1800, () => { zone.classList.add("is-emptying"); after(450, () => {
      zone.classList.remove("is-filled", "is-emptying", "is-bursting", "is-landing");
      dx = 0; dy = 0; setVars(0, 0, 0, 1);                             // reset JS offsets WITH the CSS vars, or the next drag teleports
      chip.offsetWidth; chip.classList.remove("is-fading"); chip.classList.add("is-respawning");
      after(300, () => { chip.classList.remove("is-respawning"); settling = false; });
    }); });
  }
  chip.addEventListener("pointerdown", (e) => {
    if (dragging || settling) return;
    dragging = true; id = e.pointerId; try { chip.setPointerCapture(id); } catch {}
    sx = e.clientX - dx; sy = e.clientY - dy; lastX = e.clientX; lastT = performance.now();
    chip.classList.remove("is-returning", "is-respawning"); chip.classList.add("is-dragging"); chip.style.setProperty("--lift", "1.05");
  });
  chip.addEventListener("pointermove", (e) => {
    if (!dragging || e.pointerId !== id) return;
    dx = e.clientX - sx; dy = e.clientY - sy;
    const now = performance.now(), vx = (e.clientX - lastX) / Math.max(now - lastT, 1); lastX = e.clientX; lastT = now;
    setVars(dx, dy, Math.max(-10, Math.min(10, vx * 28)), null);     // tilt from horizontal velocity only
    zone.classList.toggle("is-over", !zone.classList.contains("is-filled") && overZone());
  });
  const release = (e) => {
    if (!dragging || e.pointerId !== id) return;
    dragging = false; chip.classList.remove("is-dragging");
    const hit = zone.classList.contains("is-over"); zone.classList.remove("is-over"); settling = true;
    if (hit) { setVars(dx, dy, 0, null); chip.classList.add("is-fading"); land(); }
    else { chip.classList.add("is-returning"); dx = 0; dy = 0; setVars(0, 0, 0, 1); after(550, () => { chip.classList.remove("is-returning"); settling = false; }); }
  };
  chip.addEventListener("pointerup", release); chip.addEventListener("pointercancel", release);
  return { destroy() { timers.forEach(clearTimeout); } };
}
```

The smoke filter lives on SVG content (`<g filter>`), never as CSS `filter: url()` on HTML — WebKit renders that as a grey slab. Low turbulence frequency + strong displacement keeps the ring one continuous wavy front instead of granules.

---

## 4. Card hover tilt (3D toward the pointer + cursor glare)

Tier: occasional (product cards, cover art, membership cards). Pointer-only; touch tap-hold-drag also works via pointer events. Track the pointer on a **flat outer wrapper** so the rotating card's edges never slip from under the cursor.

```html
<div class="aim-tilt"><div class="aim-tilt-card">…card content…<div class="aim-tilt-glare"></div></div></div>
```

```css
.aim-tilt { touch-action: none; }
.aim-tilt-card { position: relative; border-radius: 12px; overflow: hidden; transform-style: preserve-3d; will-change: transform;
  transform: perspective(1000px) rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg));
  transition: transform 1000ms var(--ease-out); }                     /* return: slow settle */
.aim-tilt-card.is-tilting { transition: transform 400ms var(--ease-out); }   /* follow: short */
.aim-tilt-glare { position: absolute; inset: 0; pointer-events: none; opacity: 0; mix-blend-mode: screen; transition: opacity 300ms var(--ease-out);
  background:
    radial-gradient(circle 95px at var(--gx, 50%) var(--gy, 50%), rgb(255 255 255 / 0.48), rgb(255 255 255 / 0.06) 52%, transparent 84%),
    radial-gradient(circle 200px at var(--gx, 50%) var(--gy, 50%), rgb(255 255 255 / 0.22), rgb(255 255 255 / 0.04) 58%, transparent 78%),
    radial-gradient(circle 360px at var(--gx, 50%) var(--gy, 50%), rgb(255 255 255 / 0.10), transparent 88%); }
.aim-tilt.is-hover .aim-tilt-glare { opacity: 0.32; }
@media (prefers-reduced-motion: reduce) { .aim-tilt-card { transform: none !important; transition: none !important; } }
```

```js
function wireTilt(tilt, { max = 14 } = {}) {
  const card = tilt.querySelector(".aim-tilt-card"), reduce = matchMedia("(prefers-reduced-motion: reduce)");
  const reset = () => { tilt.classList.remove("is-hover"); card.classList.remove("is-tilting"); card.style.setProperty("--rx", "0deg"); card.style.setProperty("--ry", "0deg"); };
  tilt.addEventListener("pointermove", (e) => {
    if (reduce.matches) return;
    const r = tilt.getBoundingClientRect(), px = Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)), py = Math.min(1, Math.max(0, (e.clientY - r.top) / r.height));
    tilt.classList.add("is-hover"); card.classList.add("is-tilting");
    card.style.setProperty("--ry", ((px - 0.5) * max).toFixed(2) + "deg"); card.style.setProperty("--rx", ((0.5 - py) * max).toFixed(2) + "deg");
    card.style.setProperty("--gx", (px * 100).toFixed(1) + "%"); card.style.setProperty("--gy", (py * 100).toFixed(1) + "%");
  });
  tilt.addEventListener("pointerdown", (e) => { if (e.pointerType !== "mouse") { try { tilt.setPointerCapture(e.pointerId); } catch {} } });
  tilt.addEventListener("pointerup", reset); tilt.addEventListener("pointercancel", reset);
  tilt.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") reset(); });
}
```

10–16° reads as subtle. Not for cards in a scrolling feed (hover fires while scrolling under a resting pointer).

---

## 5. Image open tilt (zoom open like an app launch)

Tier: occasional. The card is laid out at full size and shrunk with `scale`, so the zoom is one continuous curve from press to landing while a 3D tilt rides on `transform` keyframes, strongest ~40% into the flight and flat by landing. Border radius counter-morphs 32 → 16px. Close dives back with a smaller opposite tilt on a faster clock. (The optional organic canvas bend from the premium version is omitted here — it is a per-pixel software warp; the transform flight alone carries the effect.)

```html
<div class="aim-opentilt-stage"><button class="aim-opentilt" aria-expanded="false" aria-label="Open image"><img src="photo.jpg" alt=""></button></div>
```

```css
.aim-opentilt-stage { perspective: 900px; }
.aim-opentilt { appearance: none; border: 0; padding: 0; position: relative; width: 320px; height: 240px; border-radius: 32px; overflow: visible; cursor: pointer; background: #eee; box-shadow: var(--shadow-float);
  transform-origin: center; scale: 0.3; transform: rotateX(0) rotateY(0) translateZ(0); will-change: scale, transform;
  transition: scale 420ms var(--ease-out), border-radius 420ms var(--ease-out); }
.aim-opentilt img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; pointer-events: none; border-radius: inherit; }   /* clip on the img, not overflow (Safari layer stability) */
.aim-opentilt.is-open { border-radius: 16px; scale: 1; transition: scale 620ms var(--ease-out), border-radius 620ms var(--ease-out); animation: aim-opentilt-open 620ms both; }
.aim-opentilt.is-closing { animation: aim-opentilt-close 420ms both; }
@keyframes aim-opentilt-open {
  0%   { transform: rotateX(0) rotateY(0) translateZ(0); animation-timing-function: cubic-bezier(0.3, 0.7, 0.4, 1); }
  40%  { transform: rotateX(22deg) rotateY(-14deg) translateZ(70px); animation-timing-function: cubic-bezier(0.45, 0, 0.3, 1); }
  100% { transform: rotateX(0) rotateY(0) translateZ(0); } }
@keyframes aim-opentilt-close {
  0%   { transform: rotateX(0) rotateY(0) translateZ(0); animation-timing-function: cubic-bezier(0.4, 0.4, 0.5, 1); }
  45%  { transform: rotateX(-10deg) rotateY(6deg) translateZ(28px); animation-timing-function: cubic-bezier(0.45, 0, 0.3, 1); }
  100% { transform: rotateX(0) rotateY(0) translateZ(0); } }
@media (prefers-reduced-motion: reduce) { .aim-opentilt, .aim-opentilt.is-open, .aim-opentilt.is-closing { animation: none; transition: scale var(--motion-quick) var(--ease-out); } }
```

```js
card.addEventListener("click", () => {
  const open = card.classList.contains("is-open");
  card.classList.toggle("is-open", !open); card.classList.toggle("is-closing", open); card.setAttribute("aria-expanded", String(!open));
});
card.addEventListener("animationend", (e) => { if (e.animationName === "aim-opentilt-close") card.classList.remove("is-closing"); });
```

---

## 6. Bottom sheet with snap points

See `02-surfaces.md §4` — the drawer recipe includes the drag, snap points, velocity and scroll/drag handling.

---

## 7. Pointer-follow decorations (use a spring, never a direct binding)

For a spotlight, a cursor blob or a parallax layer that follows the mouse on a marketing page: interpolate the pointer through a spring (`useSpring(mouseX, { stiffness: 300, damping: 30 })` or a tiny rAF lerp) so the element has momentum; binding it 1:1 reads artificial. Decorative only; never on data the user is reading.

```js
let tx = 0, ty = 0, x = 0, y = 0;
addEventListener("pointermove", (e) => { tx = e.clientX; ty = e.clientY; });
(function loop() { x += (tx - x) * 0.12; y += (ty - y) * 0.12; el.style.transform = `translate(${x}px, ${y}px)`; requestAnimationFrame(loop); })();
```
