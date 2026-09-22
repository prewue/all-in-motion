# Anti-patterns — what to flag, what never to ship

Three layers: hard blocks (never ship), AI-generated-UI motion tells (flag by frequency), and the mistakes that only show up in slow motion. `scripts/scan.py` greps for the mechanical ones.

---

## 1. Never ship — automatic blocks in review

| Never | Instead |
| --- | --- |
| `transition: all` | Name the exact properties |
| `transform: scale(0)` entrance | `scale(0.95)` + `opacity: 0` |
| `ease-in` on a UI element | `--ease-out` or a strong custom curve (`--ease-exit` only for a pure fade-away) |
| Built-in `ease-out` / `ease` on deliberate motion | `cubic-bezier(0.22, 1, 0.36, 1)` |
| `linear` on a UI transition | any easing; linear only for constant-rate motion |
| Animation on a keyboard shortcut or 100+/day action | No animation |
| UI duration over 300ms with no reason | 150–250ms (drawer 500ms, panel 400ms, marketing are the known exceptions) |
| `transform-origin: center` on a trigger-anchored popover | origin at the trigger (modals exempt) |
| Keyframes on toasts, toggles, anything rapidly re-triggered | State-driven CSS transitions / `@starting-style` / springs |
| Animating `width` / `height` / `margin` / `padding` / `top` / `left` | `transform` / `opacity` / `clip-path` (accordion: `grid-template-rows`) |
| Motion library `x` / `y` / `scale` shorthands on motion that runs while the page is busy | Full `transform` string |
| Driving a child transform from a CSS variable on the parent | `element.style.transform` directly |
| Ungated `:hover` motion | `@media (hover: hover) and (pointer: fine)` |
| Missing `prefers-reduced-motion` | Gentler variant, not zero |
| Everything entering at once where a list is a moment | 30–80ms stagger, total under ~300ms |
| Symmetric timing on press-and-release / hold | Slow deliberate phase, snappy release |
| Delay on a close or a hover-out | Never delay dismissal |
| Overshoot / bounce on a close | Overshoot on entrances only |
| Bouncy spring on a utility action (dropdown, toggle, menu, modal, settings) | `bounce: 0` / `state` spring; playfulness belongs to celebrations |
| No exit animation (element just disappears) | Exit subtler than enter, through the way it came |
| Feature that only works if the animation completes | Functionality independent of motion |

---

## 2. Motion fingerprints of AI-generated UI — flag by frequency

None of these is wrong in isolation. What makes them slop is *uniformity* and *frequency*: one instance is polish, the same pattern across the codebase is the tell. Each has a heuristic so single intentional uses do not trip the gate.

### Pulsing indicators
Glowing dots, breathing CTAs, throbbing rings, "live / online / recording / AI active" pulses, dark-mode glow loops. Look for `@keyframes *pulse|glow|breathe|throb*`, `animation: … infinite` on small status elements, opacity/box-shadow loops, Tailwind `animate-pulse` / `animate-ping` on indicators.
**Flag any instance.** The only exception is a single brand element with stated rationale. Fix: static treatment.

### Blur on every entrance
`filter: blur()` on every entering section, card, image and paragraph. The opacity + translateY + blur enter is excellent in moderation.
**Flag when ≥3 distinct components in one view share the same blur enter**, or when blur sits on text-bearing entrances (headings, body) and hurts first-paint readability. Fix: keep it for one hero element or a modal; plain fades elsewhere.

### Hover-scale on everything
`scale(1.0X)` on `:hover` on every card, button and image; `hover:scale-105` across grids of repeated items.
**Flag when ≥3 distinct components share the same hover scale with no discriminating context.** Fix: none on utility elements; a fill change on cards/rows; grow only what is clickable and singular.

### Stagger on every list
`staggerChildren`, `animation-delay: calc(var(--i) * 50ms)` on every list, grid and repeated block, including search results, settings, table rows.
**Flag when ≥2 lists in one view stagger.** Fix: no stagger on utility lists; one intentional moment may keep it.

### Bouncy springs on utility actions
`type: "spring", bounce > 0` or overshoot beziers on dropdowns, popovers, menus, toggles, modal opens, settings panels; identical spring configs pasted across utility components.
**Flag any bounce on a utility action.** Fix: `state` / `open` presets (≤2.5% overshoot reads as life, not bounce), `bounce: 0`.

### Uniform fade-in on every element
Identical `opacity + translateY` enters on every section, card, heading and paragraph; `whileInView` with the same options on every block; generic keyframe names (`fadeInUp`, `enter`, `reveal`) attached to many selectors.
**Flag when ≥4 distinct components share identical enter values.** Three is acceptable baseline; four is uniformity. Fix: hierarchy — the hero materialises, supporting content appears.

### Motion on mount for static content
Entrance animation on `<h1>`, `<h2>`, `<p>`, `<nav>`, body copy; `whileInView` on prose.
**Flag any motion on a text-only or navigation element whose only purpose is the entrance itself.** Carousels, hero moments and narrative pacing are fine. Fix: instant; content is for reading.

### Also common
- Gradient text everywhere (`background-clip: text` on every heading) — reserve for one word.
- Coloured `border-left` accent stripes as a "card" signifier.
- Glassmorphism blur on large scrolling areas (`backdrop-filter` cost).
- Purple-to-blue gradients and neon cyan accents as the default palette for anything animated.
- Everything animates at the same duration regardless of size.

---

## 3. Mistakes that only show in slow motion or on the tenth interaction

- **Mismatched close cleanup**: a close class (`.is-closing`) left on means the next open starts from the closing scale instead of the pre-open scale. Remove it after the close duration.
- **Forgotten reflow** when replaying keyframes (`void el.offsetWidth` between removing and re-adding the class) — the animation silently does not replay.
- **Animating the container instead of the pieces**: for a badge, animate the dot, not the trigger; for page slides, the page sections, not the wrapper.
- **`will-change` stripped** from a tuned snippet, or added globally.
- **Hardcoded `stroke-dasharray`** placeholders on path draws: measure with `getTotalLength()` and round up by 1 or the stroke pre-reveals / over-draws.
- **Timing function set in CSS for a direction-aware hover**: the return needs a different curve, set inline in JS *before* writing the variables so the new transition picks it up.
- **State classes merged** (`.is-error` and `.is-shaking` as one) so the shake cannot replay without flickering the error treatment.
- **First position of a sliding pill written with a transition** — it animates in from `translateX(0)` / `width: 0` on first paint. Snap it with `transition: none` + reflow + restore.
- **Pointer tracked on the tilting element** — its rotating edges slip under the cursor and hover flickers. Track on a flat outer wrapper.
- **Padding on the `0fr` grid track** of an accordion — a residual strip keeps it from fully closing.
- **`d:` path morphs** — Chromium-only; flip with `scaleY(-1)` instead.
- **`animation-fill-mode: both` on a delayed second phase** — yanks the element to the second phase's `from` immediately; use `forwards`.
- **Glow layers with `mix-blend-mode: multiply` in dark mode** — vanish; flip to `screen` and paint white.
- **rAF hop to release an enter class** — skipped when the frame clock is throttled; flush with a reflow in the same task.
- **JS offsets not reset with the CSS variables** after a drop — the next drag starts from a stale origin and teleports.
- **A second `transition` on a container that already animates its entrance** — plays twice.
- **Two clocks for one gesture** (a hand-rolled spring next to a preset doing the same job) — reads as lag.
- **`:hover` used to drive a fanned stack's spread** — the gaps between fanned items belong to no element; drive spread from pointer geometry.
- **Opacity and height fighting in an entering list** — there is no formula; tune, then look again the next day.

---

## 4. Not animating is also a bug (motion gaps)

Instant swaps in primary UI are often worse than poorly tuned motion. During an audit, search for conditional renders and dynamic inline styles with no transition:

```bash
grep -n "&&\s*(" --include="*.tsx" --include="*.jsx" -r .     # {open && <Modal/>}
grep -n "?\s*<"  --include="*.tsx" --include="*.jsx" -r .     # {a ? <A/> : <B/>}
grep -n "style={{[^}]*\(height\|opacity\|transform\)" -r .    # dynamic style, no transition
```

Common gaps: `{isOpen && <Modal />}` with no exit, mode switches in inspector/settings panels, loading → content snaps, `height: isExpanded ? 200 : 0` without a transition, tab content swapping with no cross-fade, toasts that pop in. Each is a **Critical** finding in primary UI (and a non-finding on keyboard/high-frequency paths, where instant is correct).

---

## 5. Marking a reviewed exception

Several entries in the never-ship table have narrow, legitimate exceptions: a tooltip that tweens its width as it travels, a tab pill measured from the active tab, a card that genuinely resizes, a loader dot that scales to zero because it is vanishing rather than entering, a determinate progress bar where width is the honest property.

When an exception has actually been reasoned through, mark it so the scanner stops asking and the next reader sees the reasoning:

```css
.tooltip {
  /* motion-ok: the bubble tweens its width as it travels between triggers */
  transition: translate 150ms var(--ease-out), width 150ms var(--ease-out);
}
```

`scripts/scan.py` skips a finding when `motion-ok` appears on the matched line or the line directly above it. The window is deliberately one line: a wider one would let a single pragma quietly cover the declarations that follow. An unexplained `motion-ok` is itself a review finding — the point is the reason after the colon, not the silence.

---

## 6. Context blindness

- Applying one lens universally: sub-300ms restraint is wrong for a kids' app; elastic playfulness is wrong for a banking dashboard. Confirm the weighting.
- Ignoring the existing codebase's conventions.
- Expecting delight in productivity tools; expecting restraint on a launch page.
- One duration for everything: small elements move faster than large ones.
