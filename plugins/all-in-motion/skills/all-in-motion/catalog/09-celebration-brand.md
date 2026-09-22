# Catalog · Celebration & brand moments

Rare-tier motion: first-time success, upgrades, achievements, one hero word. These are allowed to be noticed. They are still gated: reduced motion skips particles and smoke entirely, nothing here belongs on a control used daily, and each plays once per event.

---

## 1. Confetti burst that lands on the button

Paper flakes fall with real physics and **collide with the trigger**, modelled as a true pill: flat top between the cap centres, circular caps at the ends. Flakes rest on the flat top; on the caps the slope is steep so they slide off and keep falling. Once every flake settles the pile holds, then fades. Canvas; skipped entirely under reduced motion.

```html
<div class="aim-confetti-stage"><canvas class="aim-confetti-canvas" aria-hidden="true"></canvas><button class="aim-press aim-confetti-btn">Celebrate</button></div>
```

```css
.aim-confetti-stage { position: relative; overflow: hidden; }
.aim-confetti-stage button { position: relative; z-index: 1; }
.aim-confetti-canvas { position: absolute; inset: 0; width: 100%; height: 100%; z-index: 2; pointer-events: none; }
```

```js
function createConfetti(stage, canvas, btn, { count = 120, gravity = 1300, size = 8, sway = 16, bounce = 0.3, hold = 1600, fade = 600 } = {}) {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return { burst() {} };
  const ctx = canvas.getContext("2d"), COLORS = ["#ff4d67", "#ffb020", "#3b82f6", "#22c55e", "#a855f7", "#f97316", "#06b6d4", "#f43f5e"];
  let parts = [], running = false, lastT = 0, burstEnd = 0, fadeStart = null, W = 0, H = 0;
  function size_() { const r = stage.getBoundingClientRect(), dpr = devicePixelRatio || 1; W = r.width; H = r.height; canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
  const rect = () => { const s = stage.getBoundingClientRect(), b = btn.getBoundingClientRect(); return { left: b.left - s.left, top: b.top - s.top, right: b.right - s.left, bottom: b.bottom - s.top }; };
  function surface(x, b) {                                         // top of the pill at x: y + local slope (0 flat, steep on caps)
    if (x < b.left || x > b.right) return null;
    const r = (b.bottom - b.top) / 2, lc = b.left + r, rc = b.right - r;
    if (x >= lc && x <= rc) return { y: b.top, slope: 0 };
    const cx = x < lc ? lc : rc, dx = x - cx, root = Math.sqrt(Math.max(r * r - dx * dx, 0));
    return { y: b.top + (r - root), slope: dx / Math.max(root, 0.001) };
  }
  function burst() {
    size_(); const now = performance.now(); parts = []; fadeStart = null;
    for (let i = 0; i < count; i++) parts.push({ start: now + Math.random() * 500, x: Math.random() * W, y: -12 - Math.random() * 30, py: -12, vx: (Math.random() - 0.5) * 60, vy: 40 + Math.random() * 120,
      w: size * (0.7 + Math.random() * 0.6), h: size * (0.5 + Math.random() * 0.5), maxFall: 420 + Math.random() * 280, rot: Math.random() * Math.PI, vr: (Math.random() - 0.5) * 7,
      tumble: Math.random() * Math.PI * 2, tumbleSpeed: 4 + Math.random() * 8, squish: 1, phase: Math.random() * Math.PI * 2, swayFreq: 2 + Math.random() * 3, swayScale: 0.5 + Math.random(),
      color: COLORS[(Math.random() * COLORS.length) | 0], bounces: 0, resting: false, dead: false });
    burstEnd = now + 600;
    if (!running) { running = true; lastT = now; requestAnimationFrame(frame); }
  }
  function step(dt, now) {
    const b = rect();
    for (const p of parts) {
      if (p.resting || p.dead || now < p.start) continue;
      p.py = p.y; p.vy = Math.min(p.vy + gravity * dt, p.maxFall); p.phase += p.swayFreq * dt;
      p.x += (p.vx + Math.cos(p.phase) * sway * p.swayScale) * dt; p.y += p.vy * dt; p.rot += p.vr * dt; p.tumble += p.tumbleSpeed * dt; p.squish = 0.25 + 0.75 * Math.abs(Math.cos(p.tumble));
      const half = p.h / 2;
      if (p.vy > 0) { const s = surface(p.x, b);
        if (s && p.y + half >= s.y && p.py + half <= s.y + 2) {
          if (Math.abs(s.slope) > 0.85) { const dir = p.x < (b.left + b.right) / 2 ? -1 : 1; p.vx = dir * Math.max(Math.abs(p.vx), 50 + Math.random() * 50); p.vy *= 0.35; p.y = s.y - half; }   // steep cap: slide off
          else if (p.vy > 150 && p.bounces < 2) { p.bounces++; p.vy = -p.vy * bounce * (0.6 + Math.random() * 0.5); p.vx = p.vx * 0.7 + s.slope * 40 + (Math.random() - 0.5) * 40; p.y = s.y - half; }
          else { p.resting = true; p.y = s.y - half - 0.5; p.vx = 0; p.vy = 0; } } }
      if (!p.resting && p.y + half >= H - 1) { if (p.vy > 170 && p.bounces < 2) { p.bounces++; p.vy = -p.vy * bounce * (0.5 + Math.random() * 0.4); p.vx *= 0.7; p.y = H - 1 - half; } else { p.resting = true; p.y = H - 1 - half; p.vx = 0; p.vy = 0; } }
      if (p.x < -30 || p.x > W + 30 || p.y > H + 30) p.dead = true;
    }
  }
  function draw(alpha) { ctx.clearRect(0, 0, W, H); ctx.globalAlpha = alpha; const now = performance.now();
    for (const p of parts) { if (p.dead || now < p.start) continue; ctx.save(); ctx.translate(p.x, p.y); ctx.rotate(p.rot); ctx.scale(1, p.squish); ctx.fillStyle = p.color; ctx.fillRect(-p.w / 2, -p.h / 2, p.w, p.h); ctx.restore(); }
    ctx.globalAlpha = 1; }
  function frame(now) {
    if (!running) return;
    let rem = Math.min((now - lastT) / 1000, 0.25); lastT = now;                 // substep so a throttled tab never explodes the sim
    while (rem > 0) { const dt = Math.min(rem, 1 / 60); step(dt, now); rem -= dt; }
    if (now > burstEnd && parts.every((p) => p.resting || p.dead) && fadeStart === null) fadeStart = now + hold;
    let alpha = 1;
    if (fadeStart !== null && now >= fadeStart) { alpha = 1 - (now - fadeStart) / Math.max(fade, 1); if (alpha <= 0) { running = false; parts = []; ctx.clearRect(0, 0, W, H); return; } }
    draw(alpha); requestAnimationFrame(frame);
  }
  btn.addEventListener("click", burst); addEventListener("resize", () => running && size_());
  return { burst };
}
```

---

## 2. Delete with smoky dissolve

The element shreds into smoke and sinks under gravity instead of blinking out: snapshot to a canvas overlay, tear the edges through a scrolling noise field, blur and widen like smoke, fall with a light sway and spin, opacity going last. Everything is `drawImage` + typed-array work — no SVG filter, which is why it stays smooth in Safari. Reduced motion: remove immediately.

The full software pipeline (premultiplied snapshot, coarse noise lattice, bilinear remap, separable box-blur passes at half resolution) is long; the version below keeps the same architecture at readable size and is what the demo page runs. For production, tune `warp`, `blur`, `gravity` and `dur`, and stop after `onComplete` instead of respawning.

```html
<div class="aim-smoky-stage"><div class="aim-smoky-card"><img src="photo.jpg" alt=""><button class="aim-smoky-delete" aria-label="Delete">✕</button></div><canvas class="aim-smoky-canvas" aria-hidden="true"></canvas></div>
```

```css
.aim-smoky-stage { position: relative; overflow: hidden; border-radius: 16px; }
.aim-smoky-card { position: relative; width: 120px; height: 120px; border-radius: 16px; overflow: hidden; background: #e9e9ec; box-shadow: 0 1px 3px rgb(0 0 0 / 0.12); will-change: transform, opacity; }
.aim-smoky-card img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; pointer-events: none; }
.aim-smoky-card.is-hidden { visibility: hidden; }
.aim-smoky-card.is-respawning { animation: aim-smoky-respawn 250ms var(--ease-out); }
@keyframes aim-smoky-respawn { from { opacity: 0; transform: scale(0.96); } to { opacity: 1; transform: scale(1); } }
.aim-smoky-canvas { position: absolute; z-index: 3; pointer-events: none; will-change: transform, opacity; }
.aim-smoky-delete { position: absolute; top: 8px; right: 8px; z-index: 2; width: 24px; height: 24px; border: 0; border-radius: 50%; background: rgb(255 255 255 / 0.92); cursor: pointer; display: grid; place-items: center; }
```

```js
function createSmokyDissolve({ stage, card, canvas, dur = 550, gravity = 150, warp = 30, blur = 12, spin = 3, respawn = 800, onComplete, drawSnapshot }) {
  const ctx = canvas.getContext("2d"); const dpr = Math.min(devicePixelRatio || 1, 2); let running = false;
  const N = 64, nz = new Float32Array(N * N * 2);                  // deterministic value noise standing in for turbulence
  (function seed() { let s = 4; for (let i = 0; i < nz.length; i++) { s = (s * 1664525 + 1013904223) >>> 0; nz[i] = s / 2147483648 - 1; } })();
  const g = (o, x, y) => { const xi = Math.floor(x), yi = Math.floor(y); let fx = x - xi, fy = y - yi; fx = fx * fx * (3 - 2 * fx); fy = fy * fy * (3 - 2 * fy);
    const x0 = ((xi % N) + N) % N, x1 = (x0 + 1) % N, y0 = ((yi % N) + N) % N, y1 = (y0 + 1) % N, b = o * N * N;
    const t = nz[b + y0 * N + x0] + (nz[b + y0 * N + x1] - nz[b + y0 * N + x0]) * fx, u = nz[b + y1 * N + x0] + (nz[b + y1 * N + x1] - nz[b + y1 * N + x0]) * fx; return t + (u - t) * fy; };
  const noise = (o, px, py) => (g(o, px / 28, py / 28) + 0.5 * g(o, px / 14 + 37.7, py / 14 + 11.3)) / 1.5;
  const ease = (r) => { const kw = { linear: [0,0,1,1], ease: [0.25,0.1,0.25,1], "ease-in": [0.42,0,1,1], "ease-out": [0,0,0.58,1], "ease-in-out": [0.42,0,0.58,1] }; const c = kw[r] || [0.25,0.1,0.25,1];
    const [x1,y1,x2,y2] = c, cx = 3*x1, bx = 3*(x2-x1)-cx, ax = 1-cx-bx, cy = 3*y1, by = 3*(y2-y1)-cy, ay = 1-cy-by;
    return (x) => { let t = x; for (let i = 0; i < 6; i++) { const e = ((ax*t+bx)*t+cx)*t - x; const d = (3*ax*t+2*bx)*t+cx; if (Math.abs(e) < 1e-4 || !d) break; t -= e/d; } return ((ay*t+by)*t+cy)*t; }; };
  const eIn = ease("ease-in"), eOut = ease("ease-out");
  function dissolve() {
    if (running) return; running = true;
    const sr = stage.getBoundingClientRect(), cr = card.getBoundingClientRect(); const cw = cr.width, ch = cr.height, cx0 = cr.left - sr.left, cy0 = cr.top - sr.top;
    const pad = Math.min(Math.ceil(warp + blur) + 6, 80);
    const snap = document.createElement("canvas"); snap.width = Math.round(cw * dpr); snap.height = Math.round(ch * dpr);
    const sc = snap.getContext("2d"); sc.setTransform(dpr, 0, 0, dpr, 0, 0);
    sc.beginPath(); sc.roundRect(0, 0, cw, ch, 16); sc.clip();
    if (drawSnapshot) drawSnapshot(sc, cw, ch); else { const img = card.querySelector("img"); if (img?.naturalWidth) { const s = Math.max(cw / img.naturalWidth, ch / img.naturalHeight); sc.drawImage(img, (cw - img.naturalWidth * s) / 2, (ch - img.naturalHeight * s) / 2, img.naturalWidth * s, img.naturalHeight * s); } else { sc.fillStyle = "#e9e9ec"; sc.fillRect(0, 0, cw, ch); } }
    const TILE = 6, cols = Math.ceil(cw / TILE), rows = Math.ceil(ch / TILE);
    canvas.width = Math.round((cw + pad * 2) * dpr); canvas.height = Math.round((ch + pad * 2) * dpr);
    canvas.style.cssText = `left:${cx0 - pad}px;top:${cy0 - pad}px;width:${cw + pad * 2}px;height:${ch + pad * 2}px;opacity:1;transform:none`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    card.classList.add("is-hidden");
    const t0 = performance.now();
    (function tick(now) {
      const p = Math.min((now - t0) / dur, 1), pe = eOut(p);
      const w = warp * eOut(Math.min(1, p * 1.2)), bl = blur * eIn(pe), churn = now / 1000 * 30;
      ctx.clearRect(0, 0, cw + pad * 2, ch + pad * 2);
      ctx.filter = bl > 0.3 && "filter" in ctx ? `blur(${bl}px)` : "none";
      for (let r = 0; r < rows; r++) for (let c = 0; c < cols; c++) {                         // tile displacement through the scrolling noise field
        const px = c * TILE, py = r * TILE;
        const dx = w * noise(0, px + churn, py), dy = w * noise(1, px, py + churn);
        ctx.drawImage(snap, px * dpr, py * dpr, TILE * dpr, TILE * dpr, pad + px + dx, pad + py + dy, TILE + 0.5, TILE + 0.5);
      }
      ctx.filter = "none";
      const fall = 0.5 * gravity * (p * dur / 1000) ** 2 * eIn(p);                            // ½·g·t² on the element itself (compositor)
      canvas.style.transform = `translateY(${fall}px) rotate(${spin * pe}deg) scale(${1 + 0.15 * pe})`;
      canvas.style.opacity = String(1 - Math.pow(p, 1.6));                                     // opacity goes last
      if (p < 1) requestAnimationFrame(tick);
      else { ctx.clearRect(0, 0, canvas.width, canvas.height); onComplete?.();
        if (respawn > 0) setTimeout(() => { card.classList.remove("is-hidden"); card.classList.add("is-respawning"); setTimeout(() => card.classList.remove("is-respawning"), 260); running = false; }, respawn);
        else running = false; }
    })(t0);
  }
  return { dissolve };
}
```

Wire: `card.querySelector(".aim-smoky-delete").addEventListener("click", () => reduced ? removeNow() : ctl.dissolve())`. `ctx.filter` is unsupported in older Safari; the tile shred + fall still reads without the blur, which is acceptable for a rare effect.

---

## 3. Living gradient text (one word)

A headline word filled with seven rotated radial colour washes drifting around the glyph box over a grey base ramp, while a full hue rotation cycles the palette. Compositor-only (`background-position` + `filter`). Keep it to a word or two; pauses under reduced motion.

```html
<h1>Upgrade to <span class="aim-gradtext">Pro</span></h1>
```

```css
.aim-gradtext {
  background-image:
    radial-gradient(ellipse 40% 60% at 50% 50%, rgb(0 110 245 / 0.88), transparent 70%),
    radial-gradient(ellipse 70% 40% at 50% 50%, rgb(204 0 167 / 0.5), transparent 70%),
    radial-gradient(ellipse 45% 75% at 50% 50%, rgb(255 173 85 / 0.9), transparent 70%),
    radial-gradient(ellipse 60% 45% at 50% 50%, rgb(0 204 68 / 0.9), rgb(0 170 204 / 0) 70%),
    radial-gradient(ellipse 55% 55% at 50% 50%, rgb(0 170 204 / 0.9), transparent 70%),
    linear-gradient(rgb(108 108 108) 0%, rgb(216 216 216) 100%);
  background-size: 180% 180%, 180% 180%, 180% 180%, 180% 180%, 180% 180%, 100% 100%;
  background-repeat: no-repeat;
  -webkit-background-clip: text; background-clip: text; color: transparent;
  animation: aim-grad-hue 4s linear infinite, aim-grad-drift 5s ease-in-out infinite;
}
@keyframes aim-grad-hue { from { filter: hue-rotate(0deg) saturate(1.3); } to { filter: hue-rotate(-360deg) saturate(1.3); } }
/* each blob orbits the ring of edge stops; the grey ramp (last layer) never moves */
@keyframes aim-grad-drift {
  0%, 100% { background-position: 100% 0%, 0% 50%, 100% 50%, 0% 100%, 0% 0%, 0 0; }
  25%      { background-position: 100% 100%, 50% 0%, 50% 100%, 0% 0%, 100% 0%, 0 0; }
  50%      { background-position: 0% 100%, 100% 50%, 0% 50%, 100% 0%, 100% 100%, 0 0; }
  75%      { background-position: 0% 0%, 50% 100%, 50% 0%, 100% 100%, 0% 100%, 0 0; } }
@media (prefers-reduced-motion: reduce) { .aim-gradtext { animation: none; } }
```

The premium version keeps the exact design-tool ellipses as data-URI SVG layers (CSS `radial-gradient` cannot rotate an ellipse); the CSS-only layers above are the portable approximation.

---

## 4. Rim-glow upgrade button

A plain white pill whose rim glows with the same living colour system; a radial mask clears the middle so the label sits on clean white and the colour reads as atmosphere creeping in from the edges. No JS.

```html
<button class="aim-probtn"><span class="aim-probtn-label">Get Pro</span></button>
```

```css
.aim-probtn { --strength: 0.7; --core: 50%; --core-blur: 150%; --blur: 6px;
  position: relative; display: inline-flex; align-items: center; height: 40px; padding: 0 18px; border: 0; border-radius: 50px; overflow: hidden; background: #fff; color: #0f0f0f; font-weight: 500; cursor: pointer;
  box-shadow: 0 1px 3px rgb(0 0 0 / 0.04), inset 0 0 0 1px rgb(0 0 0 / 0.06), inset 0 -1px 0 rgb(0 0 0 / 0.1); }
.aim-probtn::before { content: ""; position: absolute; inset: 0; border-radius: inherit; pointer-events: none;
  background-image:
    radial-gradient(ellipse 40% 60% at 50% 50%, rgb(0 110 245 / 0.88), transparent 70%),
    radial-gradient(ellipse 70% 40% at 50% 50%, rgb(204 0 167 / 0.5), transparent 70%),
    radial-gradient(ellipse 45% 75% at 50% 50%, rgb(255 173 85 / 0.9), transparent 70%),
    radial-gradient(ellipse 60% 45% at 50% 50%, rgb(0 204 68 / 0.9), transparent 70%),
    radial-gradient(ellipse 55% 55% at 50% 50%, rgb(0 170 204 / 0.9), transparent 70%);
  background-size: 180% 180%; background-repeat: no-repeat;
  mask-image: radial-gradient(ellipse 46% 46% at 50% 50%, transparent var(--core), #000 calc(var(--core) + var(--core-blur)));   /* rim only */
  opacity: var(--strength);
  animation: aim-probtn-hue 4s linear infinite, aim-probtn-drift 5s ease-in-out infinite; }
.aim-probtn-label { position: relative; z-index: 1; }
@keyframes aim-probtn-hue { from { filter: hue-rotate(0deg) saturate(1.3) blur(var(--blur)); } to { filter: hue-rotate(-360deg) saturate(1.3) blur(var(--blur)); } }
@keyframes aim-probtn-drift {
  0%, 100% { background-position: 100% 0%, 0% 50%, 100% 50%, 0% 100%, 0% 0%; }
  25%      { background-position: 100% 100%, 50% 0%, 50% 100%, 0% 0%, 100% 0%; }
  50%      { background-position: 0% 100%, 100% 0%, 0% 100%, 100% 0%, 100% 100%; }
  75%      { background-position: 0% 0%, 100% 100%, 0% 0%, 100% 100%, 50% 100%; } }
@media (prefers-reduced-motion: reduce) { .aim-probtn::before { animation: none; } }   /* freezes on a colourful first frame */
```

---

## 5. Dark-mode toggle (icon morph + radial reveal)

Tier: occasional. Icon: sun ↔ moon via rotation + scale + crossfade (icon swap). Theme: custom properties transition 300ms; optionally a circular `clip-path` reveal from the toggle's position using the View Transitions API. Persist and apply before paint to avoid a flash.

```css
:root { transition: background-color var(--motion-medium) ease, color var(--motion-medium) ease; }
::view-transition-old(root), ::view-transition-new(root) { animation: none; mix-blend-mode: normal; }
::view-transition-new(root) { animation: aim-theme-reveal 500ms var(--ease-in-out); }
@keyframes aim-theme-reveal { from { clip-path: circle(0 at var(--tx, 50%) var(--ty, 50%)); } to { clip-path: circle(150% at var(--tx, 50%) var(--ty, 50%)); } }
@media (prefers-reduced-motion: reduce) { ::view-transition-new(root) { animation: none; } }
```

```js
toggle.addEventListener("click", (e) => {
  document.documentElement.style.setProperty("--tx", e.clientX + "px"); document.documentElement.style.setProperty("--ty", e.clientY + "px");
  const flip = () => { document.documentElement.dataset.theme = document.documentElement.dataset.theme === "dark" ? "light" : "dark"; localStorage.theme = document.documentElement.dataset.theme; };
  document.startViewTransition ? document.startViewTransition(flip) : flip();
});
```

---

## 6. Add to cart (fly along an arc)

Click → label fades to spinner (150ms) → success → a thumbnail clone flies to the cart icon along an arc (500ms, `offset-path`) → the cart icon bounces → the badge count rolls → label returns after 2s.

```js
function flyToCart(thumb, cart) {
  const a = thumb.getBoundingClientRect(), b = cart.getBoundingClientRect();
  const ghost = thumb.cloneNode(true); Object.assign(ghost.style, { position: "fixed", left: a.left + "px", top: a.top + "px", width: a.width + "px", height: a.height + "px", margin: 0, pointerEvents: "none", zIndex: 1000 });
  document.body.appendChild(ghost);
  const dx = b.left + b.width / 2 - (a.left + a.width / 2), dy = b.top + b.height / 2 - (a.top + a.height / 2);
  const anim = ghost.animate(
    { offsetPath: [`path('M 0 0 Q ${dx / 2} ${Math.min(dy, 0) - 120} ${dx} ${dy}')`], offsetDistance: ["0%", "100%"], transform: ["scale(1)", "scale(0.25)"], opacity: [1, 0.9] },
    { duration: 500, easing: "cubic-bezier(0.77, 0, 0.175, 1)", fill: "forwards" });
  anim.finished.then(() => { ghost.remove(); cart.animate([{ transform: "scale(1)" }, { transform: "scale(1.3)" }, { transform: "scale(1)" }], { duration: 360, easing: "cubic-bezier(0.34, 1.56, 0.64, 1)" }); });
}
```

Reduced motion: skip the flight, bounce the cart at most, roll the badge.

---

## 7. Chart bars with hover

Bars are capsules with equal gaps; a day with no data is a dim circle as wide as a bar, never a missing slot. Pointer over the chart: the bar under it stays full, the rest dim to 30% on the `hover` spring, the header swaps the total for that day's value (text swap). Changing datasets animates heights on the `state` spring (a `scaleY` transform with `transform-origin: bottom`, not `height`) and figures roll.

```css
.aim-bars { display: flex; align-items: flex-end; gap: 6px; height: 80px; }
.aim-bar { flex: 1; height: 100%; border-radius: 999px; background: var(--accent, #2563eb); transform-origin: bottom; transform: scaleY(var(--v, 0.5));
  transition: transform var(--spring-state-duration) var(--spring-state-easing), opacity var(--spring-hover-duration) var(--spring-hover-easing); }
.aim-bar.is-empty { height: auto; aspect-ratio: 1; transform: none; opacity: 0.25; align-self: flex-end; }
@media (hover: hover) { .aim-bars:hover .aim-bar:not(:hover) { opacity: 0.3; } }
```
