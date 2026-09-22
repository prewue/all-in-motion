# Properties, tools and performance

---

## 1. Pick the cheapest tool that works

Walk down; stop at the first that fits.

| Need | Tool |
| --- | --- |
| Hover, press, colour, a state toggle driven by a class or attribute | **CSS transition** |
| Entry animation on mount, no JS state | **CSS `@starting-style`** (fallback: `data-mounted` flag set in an effect) |
| Predetermined motion that must stay smooth while the page is busy | **CSS animation** (compositor thread) |
| Programmatic control with CSS performance, no library | **WAAPI** `element.animate()` |
| Springs, layout/FLIP animations, exit animations, gesture-driven values | **Motion** (`motion.dev`) / react-spring |
| Complex timelines, sequencing across many elements | **GSAP** |
| Pre-built vector animation asset | **Lottie / Rive** |
| Cross-document or route transitions with shared elements | **View Transitions API** |
| Scroll-linked | `animation-timeline: scroll()/view()` with an IntersectionObserver fallback |

Do not install a motion library for a fade. If the task is a *component* (toast, drawer, command menu, dropdown) rather than an animation, reach for a headless primitive (Base UI, Radix, a maintained toast/drawer/command-menu library) before hand-rolling: a `<div>` dropdown with no focus management is not saved by a nice curve.

**CSS beats JS under load.** CSS transitions/animations and WAAPI run on the compositor; `requestAnimationFrame`-driven animation (including Motion's JS path) drops frames while the browser loads, scripts, or paints. Use CSS for predetermined motion, JS/springs for dynamic and interruptible motion.

---

## 2. Which properties

**`transform` and `opacity` only.** They skip layout and paint and run on the GPU. `width`, `height`, `top`, `left`, `margin`, `padding`, `border`, `font-size`, `box-shadow` on large areas trigger layout → paint → composite on every frame.

Sanctioned additions:
- `clip-path` — hardware-accelerated reveals with no layout shift and no extra DOM (`inset(t r b l)`: each value eats in from that side).
- `filter: blur()` — with a budget (below).
- `grid-template-rows: 0fr ↔ 1fr` — the one acceptable way to animate an accordion's height without measuring in JS. The inner element must clip its own overflow; padding goes on the inner element, never on the `0fr` track (a padded track never fully closes).
- `background-position`, `mask-position` — compositor-cheap for shimmers and gradient drift. Colour stops and gradient swaps are expensive; animate a pseudo-element's position instead.
- `stroke-dashoffset` — SVG path draws.
- Individual transform properties (`translate`, `rotate`, `scale`) — great for composing independent clocks on HTML elements (a lift on `scale`, a drag on `translate`, a velocity tilt on `rotate`). **Not on SVG elements in WebKit**, and not inside `@keyframes` for Safari — use classic `transform` there.

```css
/* BAD: layout every frame — motion-ok: this is the counter-example */
.panel { transition: height 300ms, padding 300ms; }
/* GOOD: compositor */
.panel { transition: transform 300ms var(--ease-out), opacity 300ms var(--ease-out); }
```

`height: auto` cannot be transitioned; measure in JS or use the grid trick. Card resizes that genuinely need width/height are tolerated on small, occasional surfaces with `will-change` — know that it costs layout.

---

## 3. Transform details

- **Never `scale(0)`.** Start from `scale(0.9–0.97)` + `opacity: 0`. Nothing real appears from nothing. Pure fades with no initial transform read as flat; add a 4–8px translate or 0.97 scale.
- **`transform-origin` at the trigger** for dropdowns, popovers, menus, tooltips (`top left`, `var(--transform-origin)` in Base UI, `var(--radix-*-content-transform-origin)` in Radix). **Modals are exempt**: they are not anchored, they stay centered.
- **Percentages in `translate()`** are relative to the element's own size: `translateY(100%)` moves a toast by its own height whatever the content. Prefer over hardcoded pixels.
- **`scale()` scales children** — font, icons, everything. A feature for press feedback; a bug for zoomable content where text must stay readable (use opacity + translate instead).
- **`rotateX/Y` + `transform-style: preserve-3d` + `perspective`** on the parent for flips, folds, tilts. Think in cuboids for 3D objects.
- **Order matters**: `translateY(var(--shift)) scale(var(--s))` — translate before scale so scale does not amplify the lift.
- **Transform on a wrapper, not the `<svg>`**: transforming an inline SVG makes Chromium rasterise it at 1× (blurry on hi-DPI). Pop the wrapper.
- **Decomposed transforms with `@property`** let two typed custom properties animate on different keyframe schedules, producing curved paths a monolithic `transform` cannot:

```css
@property --x { syntax: '<percentage>'; initial-value: 0%; inherits: false; }
@property --y { syntax: '<percentage>'; initial-value: 0%; inherits: false; }
.ball { transform: translateX(var(--x)) translateY(var(--y)); animation: throw 1s; }
@keyframes throw { 0% { --x: -500%; } 50% { --y: -250%; } 100% { --x: 500%; } }
```

Without `@property` a custom property is a string and cannot interpolate; declare its type (`<length>`, `<number>`, `<percentage>`, `<color>`, `<angle>`, `<time>`).

---

## 4. Motion (framer-motion) specifics

- `x` / `y` / `scale` shorthands are **not hardware-accelerated**: they run through rAF on the main thread and drop frames under load. For motion that plays while the page is busy, use the full transform string: `animate={{ transform: "translateX(100px)" }}`.
- `layoutId` for FLIP between different components (card → modal). Keep `layoutId` elements **outside** `AnimatePresence` or the enter/exit opacity fights the layout animation. Use `<AnimatePresence mode="popLayout">` for list swaps and `mode="wait"` for icon swaps.
- `useReducedMotion()` for programmatic fallbacks; `useSpring(value, { stiffness: 300, damping: 30 })` to interpolate mouse position or counters.
- Motion supports interruption natively; test rapid re-triggers anyway.

---

## 5. Interruptible by construction

- **Transitions, not keyframes, for anything the user can re-trigger** (toasts, toggles, sidebars, anything opened twice in a second). A transition retargets from the current value; keyframes restart from zero and jump.
- State-driven pattern: rest style + `.is-open` style + `transition`. Entry without JS: `@starting-style`.

```css
.toast {
  opacity: 1; transform: translateY(0);
  transition: opacity 400ms ease, transform 400ms ease;
  @starting-style { opacity: 0; transform: translateY(100%); }
}
```

- When keyframes are the right tool (one-shot celebrations, shakes, pops), replay them with the reflow trick: remove the class/attribute, `void el.offsetWidth`, re-add. Keep state classes orthogonal (`.is-error` vs `.is-shaking`) so a replay does not flicker the whole treatment.
- Close-state cleanup: when a close uses its own class (`.is-closing`), remove it after the close duration or the next open starts from the closing scale.

---

## 6. Style recalculation and drag

- **Do not drive a moving element through a CSS variable on its parent.** Variables inherit; updating `--drag-y` on a container recalculates styles for every descendant (a drawer with 20 list items drops frames this way). Set `element.style.transform = \`translateY(${y}px)\`` directly on the moving element. Per-element custom properties written on the element itself (`--dx` on the chip) are fine.
- While dragging, no transition on the dragged property: the element must track the pointer 1:1. Add the settle transition/spring only on release (`.is-returning`).
- Read tokens with `getComputedStyle` once per gesture, not per frame — per-frame style reads force recalcs (Safari drops to ~30fps).
- Hover effects inside scrolling content fire while the page scrolls under a resting pointer; add `pointer-events: none` to hover-driven children while `.is-scrolling` (no hover while scrolling).

---

## 7. `will-change`

A hint that promotes an element to its own compositor layer before the animation starts, removing first-frame stutter and the 1px sub-pixel shift at the end of a transform animation.

- Specific properties only: `will-change: transform, opacity` (also `filter`, `clip-path`, `mask`).
- Scope it to the element and, ideally, the gesture: `data-[dragging=true]:will-change-transform`. Remove after the animation; each layer costs GPU memory.
- Never global. Not a fix for jank (find the cause). Budget: 0–3 promoted elements fine, 4–10 test on low-end devices, 10+ reconsider (virtualise, stagger, simplify).
- Promoting a filtered SVG layer (`will-change: filter, transform`) fixes WebKit repainting goo/blur a frame behind the DOM.

---

## 8. Blur budget

Blur is the expensive channel, especially in Safari.
- Keep it small: 2px bridges a crossfade; 3–4px materialises an element; 8–14px only for folds/emphasis; never above ~20px.
- The budget: full radius on high-refresh displays, half at 60Hz (min 1.5px), a third in low-power mode (min 1px), zero under reduced motion. `--motion-blur-scale` in CSS, `blurRadius()` in `motion.ts`. Drop to 0.5 on long pages with many simultaneous transitions.
- `filter` applies **before** `mask`/clipping on the same element and creates its own compositing context. To blur a masked layer, split into wrapper (filter) + inner (mask). To cross-blur a badge that scales and hops, blur a wrapper, not the badge.
- Declare `filter: blur(0)` explicitly on the rest state; `blur → none` is not reliably interpolated and the cross-blur snaps.
- Blur as a bridge: when a crossfade shows two overlapping states despite tuning, `filter: blur(2px)` during the transition blends them into one perceived transformation.
- Blur on text-bearing entrances impairs first-paint readability; do not blur every heading.

---

## 9. Clip-path

`clip-path: inset(top right bottom left [round r])` is hardware-accelerated, causes no layout shift, and needs no extra DOM. Uses: reveal-on-scroll (`inset(0 0 100% 0)` → `inset(0 0 0 0)`), hold-to-confirm fill, image reveals, comparison sliders, and **aligned tab transitions**: duplicate the tab list, style the copy as the active state, clip it to the active tab and animate the clip — text and background change in perfect sync because they are one element being revealed, not two colours interpolating. `circle(r at x y)` for dark-mode toggles radiating from the switch.

---

## 10. Scroll-driven animations

Scroll-linked animation is tied to scroll *speed*; slow scrolling plays it slowly, which feels wrong for most UI. Trigger at a position, then run on a fixed duration: an IntersectionObserver (or `useInView({ once: true, margin: "-100px" })`) flips a class and the CSS runs its own clock. Fire once; do not re-animate on every scroll-by. Require ~100px (or 10–20% of the element) inside the viewport before triggering. Pure-CSS version: a scroll-driven trigger animation toggles a custom property, a style query starts the duration-based one; feature-detect with `CSS.supports('animation-timeline', 'scroll()')` and fall back to the observer.

---

## 11. WebKit / Safari gotchas (from the pro recipes; each cost real debugging time)

| Symptom | Cause | Fix |
| --- | --- | --- |
| SVG filter effect renders as a grey slab or never animates | CSS `filter: url(#id)` on **HTML** content; WebKit does not run `feDisplacementMap`/goo on HTML | Apply the filter to SVG shapes inside an `<svg>` (`<g filter="url(#id)">`) and mirror the geometry 1:1 under crisp HTML controls |
| `var()` inside `animation:` shorthand runs at 0s | WebKit mis-parses `var()` in the shorthand | Use longhands: `animation-name`, `animation-duration`, `animation-timing-function`, `animation-delay`, `animation-fill-mode` |
| Fan / stagger desync on SVG circles, hop feels wrong | Individual `translate:` / `scale:` on SVG elements or inside `@keyframes` | Classic `transform` on SVG and in keyframes; individual properties are fine on HTML |
| Displacement bend via `feImage` never appears | WebKit never loads `feImage` data-URI maps | Draw the warp to a `<canvas>` (software displacement) or drop the bend |
| Animated SVG filter stutters / stale frames | WebKit runs SVG filters on the CPU and does not reliably repaint animated primitives | Canvas `drawImage` pipelines for dissolves; `will-change: filter, transform` on a static filtered layer |
| A delayed second animation yanks the element to its `from` immediately | `animation-fill-mode: both` on a delayed phase | Use `forwards` on multi-phase chains (`up` then `down`) |
| Goo shadow doubles or looks muddy | Chained `feDropShadow` compound; `linearRGB` interpolation | Build each shadow pass from the same `shape` result and `feMerge` behind it; set `color-interpolation-filters="sRGB"` |
| `feMorphology dilate` ring shows a second hairline | Dilating the soft alpha fringe | Binarise alpha first (`feColorMatrix` slope 60 / −29.5), then dilate |
| Chevron path morph snaps on iOS/Firefox | CSS `d:` interpolation is Chromium-only | Flip with `transform: scaleY(-1)` on a path symmetric about its viewBox centre, `vector-effect: non-scaling-stroke` |
| Canvas positioned with `inset` does not stretch | Canvas is a replaced element | Size the CSS box explicitly (`width/height` in px) and the bitmap in device px |
| Toggling `overflow` mid-flight janks a scale/tilt | Element leaves its compositor layer | Keep `overflow: visible` and clip via `border-radius: inherit` on the inner image |
| rAF hop skipped, element lands with no motion | Frame clock throttled (background tab, low power) | Flush with `void el.offsetWidth` and release the enter class in the same task |
| Physics explode after a tab switch | One huge `dt` | Substep the simulation in ≤16ms slices, cap the frame delta (0.25s) |
| Gradient text on hi-DPI pixelated | transform on inline SVG | Pop an HTML wrapper |
| p3 shadow ignored / rgba fallback | — | Two `box-shadow` declarations: `rgba()` first, `color(display-p3 …)` second |

---

## 12. Mobile budget

- Functional transitions ≤400ms, decorative ≤1s. Max 3–5 concurrent animations.
- Avoid on mobile: parallax, continuous background animation, complex SVG morphs, `backdrop-filter` on large areas.
- Prefer CSS transitions, simple transforms, opacity fades. Test on a real low-end device; if under 60fps, simplify.
- `touch-action: none` on anything dragged (or a touch drag scrolls the page and no `pointermove` arrives). `-webkit-tap-highlight-color: transparent` on custom pressables.

---

## 13. Checklist

- [ ] Only `transform` / `opacity` (+ `clip-path`, budgeted `filter`, `grid-template-rows` for accordions)
- [ ] Transitions or springs for anything re-triggerable; keyframes only for one-shots with a reflow replay
- [ ] Exact property list, never `transition: all`
- [ ] `transform-origin` at the trigger; modals centered
- [ ] No `scale(0)`; enter from 0.9–0.97 + opacity
- [ ] Direct `style.transform` for drags; no parent CSS-variable driving
- [ ] `will-change` scoped and removed; < 10 promoted layers
- [ ] Blur ≤ 20px, budgeted, `blur(0)` rest state declared
- [ ] Motion library shorthands avoided where the page is busy
- [ ] WebKit: filters on SVG content, longhand `animation-*`, classic `transform` on SVG
