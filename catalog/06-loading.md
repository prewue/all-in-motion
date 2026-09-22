# Catalog · Loading — shimmers, loaders, progress

Loaders are the sanctioned infinite animations. Rules: `linear` for constant motion, pausable (`data-playing="false"`), a gentler form (not removal) under reduced motion, `role="status"` so the state is announced, and a faster spinner makes the same wait feel shorter.

---

## 1. Shimmer text (pure CSS)

A "thinking / generating" label that feels alive without a spinner. Duplicate the string into `data-text`; a masked gradient sweeps the glyphs.

```html
<span class="aim-shimmer" data-text="Planning next moves" role="status">Planning next moves</span>
```

```css
.aim-shimmer { position: relative; display: inline-block; color: var(--shimmer-base, #7c7c7c); }
.aim-shimmer::before {
  content: attr(data-text); position: absolute; inset: 0; pointer-events: none;
  background-image: linear-gradient(90deg, transparent 0%, transparent 40%, var(--shimmer-highlight, #0d0d0d) 50%, transparent 60%, transparent 100%);
  background-size: 400% 100%; background-repeat: no-repeat;
  -webkit-background-clip: text; background-clip: text; color: transparent; -webkit-text-fill-color: transparent;
  animation: aim-shimmer 2s var(--ease-linear) infinite;
}
@keyframes aim-shimmer { 0% { background-position: 100% 0; } 100% { background-position: 0% 0; } }
@media (prefers-reduced-motion: reduce) { .aim-shimmer::before { animation: none; } }
```

Dark mode: swap `--shimmer-base` / `--shimmer-highlight` (light grey / white).

---

## 2. Skeleton shimmer (surface sweep)

```css
.aim-skeleton { position: relative; overflow: hidden; background: rgb(0 0 0 / 0.07); border-radius: 8px; }
.aim-skeleton::after { content: ""; position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent 0 30%, rgb(255 255 255 / 0.5) 50%, transparent 70% 100%);
  background-size: 200% 100%; animation: aim-sweep 1.5s var(--ease-linear) infinite; }
@keyframes aim-sweep { from { background-position: 100% 0; } to { background-position: -100% 0; } }
@media (prefers-reduced-motion: reduce) { .aim-skeleton::after { animation: aim-skel-fade 2s ease-in-out infinite; background: rgb(255 255 255 / 0.3); } }
@keyframes aim-skel-fade { 50% { opacity: 0; } }
```

Match the skeleton's layout to the real content exactly, then cross-fade to it (`05-content-swap.md §7`), staggering blocks 30ms apart if several load at once.

---

## 3. Organic colour shimmer (premium skeleton / upload target)

Tier: occasional, rare surfaces only (it is expensive: an SVG turbulence warp + blur). A band of six soft colour blobs sweeps diagonally, waved by turbulence so it never reads as a ruler-straight stripe, plus an edge beam masked to a comet window on the same clock.

```html
<div class="aim-oshimmer" aria-hidden="true">
  <span class="aim-oshimmer-warp"><span class="aim-oshimmer-band"></span></span>
  <span class="aim-oshimmer-edge"><span class="aim-oshimmer-ring"></span></span>
</div>
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <filter id="aim-oshimmer-warp" x="-40%" y="-40%" width="180%" height="180%">
    <feTurbulence type="fractalNoise" baseFrequency="0.009 0.015" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="46" xChannelSelector="R" yChannelSelector="G"/>
  </filter>
</svg>
```

```css
.aim-oshimmer { --s: 1; --span: 26%; position: relative; width: 142px; height: 142px; border-radius: 12px; background: #eee; overflow: hidden; isolation: isolate; }
.aim-oshimmer[data-playing="false"] .aim-oshimmer-band, .aim-oshimmer[data-playing="false"] .aim-oshimmer-edge { animation-play-state: paused; }
/* wrapper warps + blurs the already-masked band (filter runs before mask on one element, hence the split) */
.aim-oshimmer-warp { position: absolute; inset: calc(-20px * var(--s)); filter: url(#aim-oshimmer-warp) blur(calc(5px * var(--s))); pointer-events: none; }
.aim-oshimmer-band { position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 49% 38% at 20% 15%, rgb(40 140 255 / 0.14), transparent),
    radial-gradient(ellipse 44% 33% at 65% 25%, rgb(255 50 100 / 0.13), transparent),
    radial-gradient(ellipse 38% 44% at 30% 55%, rgb(50 200 80 / 0.12), transparent),
    radial-gradient(ellipse 49% 38% at 75% 65%, rgb(180 40 240 / 0.13), transparent),
    radial-gradient(ellipse 38% 33% at 45% 85%, rgb(255 120 40 / 0.12), transparent),
    radial-gradient(ellipse 33% 33% at 10% 85%, rgb(30 185 170 / 0.11), transparent),
    linear-gradient(rgb(90 90 100 / 0.05), rgb(90 90 100 / 0.05));
  mask-image: linear-gradient(135deg, transparent 0%, transparent calc(50% - var(--span) * 0.8), rgb(255 255 255 / 0.25) calc(50% - var(--span) * 0.45), rgb(255 255 255 / 0.7) calc(50% - var(--span) * 0.18), #fff 50%, rgb(255 255 255 / 0.7) calc(50% + var(--span) * 0.18), rgb(255 255 255 / 0.25) calc(50% + var(--span) * 0.45), transparent calc(50% + var(--span) * 0.8), transparent 100%);
  mask-size: 280% 280%; mask-repeat: no-repeat; mask-position: 100% 100%;
  animation: aim-oshimmer-sweep 3s ease-out infinite; }
.aim-oshimmer-edge { position: absolute; inset: calc(-20px * var(--s)); z-index: 1; opacity: 0.7; pointer-events: none;
  mask-image: linear-gradient(135deg, transparent 0%, transparent calc(50% - var(--span) * 1.4), rgb(255 255 255 / 0.06) calc(50% - var(--span)), rgb(255 255 255 / 0.18) calc(50% - var(--span) * 0.6), rgb(255 255 255 / 0.45) calc(50% - var(--span) * 0.25), #fff 50%, rgb(255 255 255 / 0.5) calc(50% + var(--span) * 0.18), transparent calc(50% + var(--span) * 0.35), transparent 100%);
  mask-size: 280% 280%; mask-repeat: no-repeat; mask-position: 100% 100%;
  animation: aim-oshimmer-sweep 3s ease-out infinite; }
.aim-oshimmer-ring { position: absolute; inset: calc(20px * var(--s)); border-radius: 12px; padding: calc(1px * var(--s));
  background:
    radial-gradient(ellipse 30% 17% at 33% -7%, rgb(255 50 100 / 0.62), transparent),
    radial-gradient(ellipse 25% 15% at 12% -5%, rgb(40 140 255 / 0.48), transparent),
    radial-gradient(ellipse 17% 30% at 2% 68%, rgb(50 200 80 / 0.55), transparent),
    radial-gradient(ellipse 76% 13% at 74% 100%, rgb(100 70 255 / 0.58), transparent),
    radial-gradient(ellipse 31% 13% at 94% 0%, rgb(255 120 40 / 0.65), transparent),
    radial-gradient(ellipse 22% 20% at 100% 27%, rgb(180 40 240 / 0.56), transparent),
    linear-gradient(rgb(90 90 100 / 0.22), rgb(90 90 100 / 0.22));
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0); mask-composite: exclude; -webkit-mask-composite: xor; }
@keyframes aim-oshimmer-sweep { 0% { mask-position: 100% 100%; } 100% { mask-position: 0% 0%; } }
@media (prefers-reduced-motion: reduce) { .aim-oshimmer-band, .aim-oshimmer-edge { animation: none; } }
```

Set `--s` to `size / 142` for other tile sizes; below ~50px drop the edge beam. Only `mask-position` and `filter` animate — compositor work — but the turbulence warp is a real cost: one or two on screen, never a grid of them.

---

## 4. Matrix dot loader (4×4, four patterns)

Where a spinner is too loud: next to a status line, inside a compact button, in a table cell. One colour-pulse keyframe; a per-dot delay table is the whole "variant".

```html
<div class="aim-matrix" data-variant="scan" role="status" aria-label="Loading"></div>
```

```css
.aim-matrix { display: grid; grid-template-columns: repeat(4, 3px); grid-auto-rows: 3px; gap: 3px; }
.aim-matrix i { display: block; background: var(--matrix-base, #d9d9d9); border-radius: 1px; animation: aim-matrix-pulse 1200ms ease-in-out infinite; animation-delay: calc(var(--d, 0) * 1ms); }
.aim-matrix i.is-gap { visibility: hidden; animation: none; }
@keyframes aim-matrix-pulse { 0%, 45%, 100% { background-color: var(--matrix-base, #d9d9d9); } 15% { background-color: var(--matrix-active, #85858f); } }
@media (prefers-reduced-motion: reduce) { .aim-matrix i { animation-duration: 2400ms; } }
```

```js
function buildMatrix(el, cycle = 1200) {
  const v = el.dataset.variant || "scan", rounded = el.dataset.rounded === "true";
  const CORNERS = [0, 3, 12, 15], RING = [1, 2, 7, 11, 14, 13, 8, 4], INNER = [5, 6, 9, 10], TWINKLE = [7, 2, 11, 5, 14, 9, 0, 12, 3, 15, 6, 10, 13, 1, 8, 4];
  for (let i = 0; i < 16; i++) {
    const d = document.createElement("i"), col = i % 4;
    if (rounded && CORNERS.includes(i)) d.className = "is-gap";
    else if (v === "scan") d.style.setProperty("--d", String(Math.round(col * cycle / 10)));
    else if (v === "twinkle") d.style.setProperty("--d", String(Math.round(TWINKLE[i] * cycle / 16)));
    else if (v === "orbit") { const k = RING.indexOf(i); if (k !== -1) d.style.setProperty("--d", String(Math.round(k * cycle / 8))); else d.style.animation = "none"; }
    else if (v === "pulse") d.style.setProperty("--d", String(Math.round((INNER.includes(i) ? 0 : 1) * cycle * 0.16)));
    el.appendChild(d);
  }
}
```

---

## 5. Spinner

```css
.aim-spinner { width: 16px; height: 16px; border-radius: 50%; border: 2px solid rgb(0 0 0 / 0.12); border-top-color: currentColor; animation: aim-spin 800ms var(--ease-linear) infinite; }
@keyframes aim-spin { to { transform: rotate(360deg); } }
@media (prefers-reduced-motion: reduce) { .aim-spinner { animation-duration: 1.6s; } }   /* still spins: loading must stay legible */
```

800ms feels faster than 1.2s for the same wait. Replace with a check on completion (spinner→check morph).

---

## 6. Progress bars and steps

```css
/* motion-ok: determinate progress — width is the honest property; keep updates ≥ 200ms apart */
.aim-progress { height: 6px; border-radius: 3px; background: rgb(0 0 0 / 0.08); overflow: hidden; }
/* motion-ok: see above */
.aim-progress-fill { height: 100%; width: var(--p, 0%); background: var(--accent, #2563eb); transition: width var(--motion-slow) var(--ease-out), background-color var(--motion-slow) var(--ease-out); transform-origin: left; }
/* indeterminate: a sliding bar, compositor-only */
.aim-progress.is-indeterminate .aim-progress-fill { width: 30%; animation: aim-indeterminate 1.5s ease-in-out infinite; }
@keyframes aim-indeterminate { from { transform: translateX(-100%); } to { transform: translateX(400%); } }
@media (prefers-reduced-motion: reduce) { .aim-progress.is-indeterminate .aim-progress-fill { animation: aim-skel-fade 2s ease-in-out infinite; transform: none; width: 100%; } }
```

`role="progressbar" aria-valuenow`. For a `transform: scaleX()` version (no layout) set the fill to full width and `transform: scaleX(var(--p))` with `transform-origin: left`. Colour may shift as progress increases (grey → accent → success). Step indicators: completed step's number morphs to a check (icon swap), the connecting line fills with a `scaleX` sweep, the active step gets a static ring — no pulsing.

---

## 7. Pull-to-refresh (mobile pattern spec)

Overscroll → indicator scales/rotates with pull distance (direct style writes, no transition) → threshold: haptic tick, indicator snaps to the loading state on the `emphasis` spring → loading: spinner, content locked → complete: spinner morphs to a check, content slides back on the `release` spring. Never animate the whole list on every pull; only the indicator.
