# Catalog · Reveals, staggers, group hovers

Entrance motion is where uniformity turns into slop fastest. Budget it: one hero moment per view, staggers only where a group *is* a moment, nothing on body copy, and never on repeat visits of a high-frequency screen.

---

## 1. Texts reveal (headline + supporting line, staggered blur rise)

Tier: rare (hero copy, empty states, onboarding steps). Exit is a single quiet fade with no Y return so dismissing does not replay the reveal backwards.

```html
<div class="aim-textreveal">
  <strong class="aim-textreveal-line" style="--i:0">Everything in one place</strong>
  <span class="aim-textreveal-line" style="--i:1">Plan, build and ship without leaving the editor.</span>
</div>
```

```css
.aim-textreveal-line { display: block; opacity: 0; transform: translateY(var(--move-medium)); filter: blur(calc(var(--blur-medium) * var(--motion-blur-scale)));
  transition: opacity var(--motion-deliberate) var(--ease-out), transform var(--motion-deliberate) var(--ease-out), filter var(--motion-deliberate) var(--ease-out);
  transition-delay: calc(var(--i, 0) * var(--stagger-base)); will-change: transform, opacity, filter; }
.aim-textreveal.is-shown .aim-textreveal-line { opacity: 1; transform: none; filter: blur(0); }
.aim-textreveal.is-hiding .aim-textreveal-line { opacity: 0; transform: none; filter: blur(0); transition: opacity 200ms ease, transform 0s, filter 0s; transition-delay: 0s; }
@media (prefers-reduced-motion: reduce) { .aim-textreveal-line { transform: none; filter: none; transition: opacity var(--motion-quick) var(--ease-out); } }
```

```js
const show = () => { el.classList.remove("is-hiding", "is-shown"); void el.offsetHeight; el.classList.add("is-shown"); };
const hide = () => { el.classList.add("is-hiding"); el.classList.remove("is-shown"); setTimeout(() => el.classList.remove("is-hiding"), 200); };
```

---

## 2. Stagger a group entrance

Tier: occasional — a list the user sees sometimes, not one they scroll past all day. 30–80ms apart, total under ~300ms, `fill-mode: both` so nothing flashes before its delay. Decorative: never blocks interaction.

```css
.aim-stagger > * { opacity: 0; transform: translateY(var(--move-base)); animation: aim-fade-up var(--motion-fast) var(--ease-out) both; animation-delay: calc(var(--i, 0) * var(--stagger-base)); }
@keyframes aim-fade-up { to { opacity: 1; transform: none; } }
@media (prefers-reduced-motion: reduce) { .aim-stagger > * { transform: none; animation-name: aim-fade; animation-delay: 0s; } }
@keyframes aim-fade { to { opacity: 1; } }
```

```js
[...list.children].forEach((c, i) => c.style.setProperty("--i", Math.min(i, 7)));   // cap: the 8th+ item arrives with the 8th
```

Motion library: `staggerChildren: 0.04, delayChildren: 0.1`. Negative delays (`calc(var(--i) * -0.2s)`) make a looping group appear already mid-flight.

---

## 3. Scroll reveal (once, when meaningfully in view)

Tier: marketing surfaces only — not functional UI a user visits daily. Trigger at a position (≥100px inside the viewport), run on a fixed clock, fire once.

```css
.aim-inview { opacity: 0; transform: translateY(20px); transition: opacity var(--motion-deliberate) var(--ease-out), transform var(--motion-deliberate) var(--ease-out); }
.aim-inview.is-visible { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { .aim-inview { transform: none; transition: opacity var(--motion-quick) var(--ease-out); } }
```

```js
const io = new IntersectionObserver((entries) => entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("is-visible"); io.unobserve(e.target); } }),
                                    { rootMargin: "-100px 0px", threshold: 0 });
document.querySelectorAll(".aim-inview").forEach((el) => io.observe(el));
```

Pure CSS where supported: `animation-timeline: view(); animation-range: entry 0% entry 40%` — but that ties speed to scrolling; the observer + fixed duration feels better for UI. Motion library: `useInView(ref, { once: true, margin: "-100px" })`.

---

## 4. Clip-path reveal (image, block, comparison)

Hardware-accelerated, no layout shift, no extra DOM.

```css
.aim-clipreveal { clip-path: inset(0 0 100% 0); transition: clip-path 600ms var(--ease-in-out); }
.aim-clipreveal.is-visible { clip-path: inset(0 0 0 0); }
/* patterns: inset(0 0 100% 0) bottom-up · inset(100% 0 0 0) top-down · inset(0 100% 0 0) from the left · circle(0 at x y) → circle(150% at x y) radial */
@media (prefers-reduced-motion: reduce) { .aim-clipreveal { clip-path: none; transition: opacity var(--motion-quick) var(--ease-out); } }
```

WAAPI: `el.animate([{ clipPath: "inset(0 0 100% 0)" }, { clipPath: "inset(0)" }], { duration: 600, easing: "cubic-bezier(0.77,0,0.175,1)", fill: "forwards" })`. Comparison slider: two stacked images, the top one clipped by `inset(0 var(--x) 0 0)` driven from the pointer with direct style writes.

---

## 5. Avatar group hover (distance-falloff lift, springy return)

Tier: tens/day → 4px lift; the physical feel comes from direction-aware easing: clean ease-out on the way up, a strong overshoot on the way back. The timing function is set inline *before* the variable writes so each direction gets its own curve.

```html
<div class="aim-avatars"><div class="aim-avatar">A</div><div class="aim-avatar">B</div><div class="aim-avatar">C</div><div class="aim-avatar">D</div><div class="aim-avatar">E</div></div>
```

```css
.aim-avatars { display: flex; }
.aim-avatar { width: 36px; height: 36px; margin-left: -8px; border-radius: 50%; border: 2px solid #fff; background: #ddd; display: grid; place-items: center;
  transform-origin: center; transform: translateY(var(--shift, 0px)) scale(var(--s, 1));   /* translate before scale */
  transition: transform 320ms var(--ease-out); will-change: transform; }
@media (prefers-reduced-motion: reduce) { .aim-avatar { transition: none; transform: none !important; } }
```

```js
function wireAvatars(root, { lift = -4, falloff = 0.45, scale = 1.05 } = {}) {
  const items = [...root.querySelectorAll(".aim-avatar")];
  const cs = getComputedStyle(document.documentElement);
  const set = (active, phase) => {
    const tf = phase === "out" ? cs.getPropertyValue("--ease-bounce-strong").trim() : cs.getPropertyValue("--ease-out").trim();
    items.forEach((el, i) => {
      el.style.transitionTimingFunction = tf;               // BEFORE the writes below
      if (active == null) { el.style.setProperty("--shift", "0px"); el.style.setProperty("--s", "1"); return; }
      const d = Math.abs(i - active);
      el.style.setProperty("--shift", (lift * Math.pow(falloff, d)).toFixed(3) + "px");
      el.style.setProperty("--s", i === active ? String(scale) : "1");
    });
  };
  if (!matchMedia("(hover: hover) and (pointer: fine)").matches) return;
  items.forEach((el, i) => el.addEventListener("mouseenter", () => set(i, "in")));
  root.addEventListener("mouseleave", () => set(null, "out"));
}
```

Also for chip rows, tag pills, reaction rows.

---

## 6. Card stack hover (fan out with a spring)

Tier: occasional. Three stacked cards fan out on container hover and spring back together; the hovered card scales on its own slower clock. Each card owns its slot geometry inline; shared multipliers scale the fan.

```html
<div class="aim-cardstack" aria-label="Attachments">
  <button class="aim-cardstack-card" style="--cx:28px;--cy:20px;--rot:4deg;--dx:2px;--dy:-26px;--drot:7deg;z-index:0"></button>
  <button class="aim-cardstack-card" style="--cx:12px;--cy:20px;--rot:-8deg;--dx:-4px;--dy:-6px;--drot:-7deg;z-index:1"></button>
  <button class="aim-cardstack-card" style="--cx:21px;--cy:26px;--rot:0deg;--dx:2px;--dy:26px;--drot:4deg;z-index:2"></button>
</div>
```

```css
.aim-cardstack { --spread: 1.42; --rotation: 1; position: relative; width: 120px; height: 120px; }
.aim-cardstack-card { appearance: none; border: 0; padding: 0; position: absolute; top: 0; left: 0; width: 78px; height: 78px; border-radius: 12px; background: #fff; box-shadow: var(--shadow-float); cursor: pointer;
  translate: var(--cx) var(--cy); rotate: var(--rot); scale: 1;
  transition: translate 360ms cubic-bezier(0.34, 1.9, 0.64, 1), rotate 360ms cubic-bezier(0.34, 1.9, 0.64, 1), scale 610ms var(--ease-out);   /* rest = collapse */
  will-change: translate, rotate, scale; }
@media (hover: hover) {
  .aim-cardstack:hover .aim-cardstack-card { translate: calc(var(--cx) + var(--dx)) calc(var(--cy) + var(--dy) * var(--spread)); rotate: calc(var(--rot) + var(--drot) * var(--rotation));
    transition: translate 410ms cubic-bezier(0.31, 2.34, 0.64, 1), rotate 410ms cubic-bezier(0.31, 2.34, 0.64, 1), scale 610ms var(--ease-out); }
  .aim-cardstack-card:hover { scale: 1.04; z-index: 30; }
}
@media (prefers-reduced-motion: reduce) { .aim-cardstack-card { transition: none; } }
```

Individual transform properties are fine here (HTML, not SVG). Hover-only; touch gets a plain tap.

---

## 7. Blur bridge (mask a crossfade that won't settle)

When two states overlap visibly during a transition and no easing/duration tuning fixes it, blur the seam. The eye stops reading two objects and sees one transformation. Keep it ≤2px.

```css
.aim-bridge { transition: filter var(--motion-fast) ease, opacity var(--motion-fast) ease; }
.aim-bridge.is-transitioning { filter: blur(2px); opacity: 0.7; }
@media (prefers-reduced-motion: reduce) { .aim-bridge.is-transitioning { filter: none; } }
```

Applied to a button whose background swaps, a card whose content re-renders, or a tab panel changing. Do not apply to every entrance (anti-pattern §2).

---

## 8. 3D card flip

```css
.aim-flip { perspective: 1000px; }
.aim-flip-inner { position: relative; transform-style: preserve-3d; transition: transform var(--motion-deliberate) var(--ease-in-out); }
.aim-flip.is-flipped .aim-flip-inner { transform: rotateY(180deg); }
.aim-flip-face { position: absolute; inset: 0; backface-visibility: hidden; }
.aim-flip-back { transform: rotateY(180deg); }
@media (prefers-reduced-motion: reduce) { .aim-flip-inner { transition: opacity var(--motion-quick) var(--ease-out); transform: none; } .aim-flip.is-flipped .aim-flip-front { opacity: 0; } .aim-flip.is-flipped .aim-flip-back { transform: none; } }
```

Mental model: `rotateX` turns around a horizontal axis like a garage door, `rotateY` around a vertical axis like a revolving door. Rare-tier motion; a flip on a frequently used card is a chore.
