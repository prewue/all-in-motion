# Accessibility — not optional, not a follow-up

Motion can cause discomfort, nausea or distraction. Every animation ships with its reduced-motion path in the same commit.

---

## 1. `prefers-reduced-motion` — fewer and gentler, never zero

Reduced motion does **not** mean no motion. Going nuclear removes loaders, state feedback and the cues that make an interface understandable. Ranked approaches:

**A. Per-component fallback (preferred).** Keep opacity and colour, drop movement, scale, blur and folds. Collapse spring bounce.

```css
.sidebar {
  transition: transform 300ms var(--ease-out), opacity 300ms var(--ease-out);
}
@media (prefers-reduced-motion: reduce) {
  .sidebar {
    transform: none;                              /* no movement */
    transition: opacity 200ms var(--ease-out);    /* still fades: feedback survives */
  }
  .spinner   { animation: pulse 1s ease-in-out infinite; }  /* loading still reads as loading */
  .error     { animation: error-pulse 200ms var(--ease-out); } /* colour pulse instead of shake */
}
```

**B. Opt-in motion.** The rest state is the default; motion is added only under `no-preference`. Good for entrance animations and anything decorative.

```css
.card { opacity: 1; transform: none; }
@media (prefers-reduced-motion: no-preference) {
  .card { animation: fade-up 300ms var(--ease-out) both; }
}
```

**C. Token-level.** The shipped tokens already do most of the work: under reduced motion `--motion-blur-scale` is 0, distances collapse to 0, bouncy easings resolve to `--ease-out`, long durations shrink to 150–200ms, and bouncy springs collapse to short ease-outs. Components that only use tokens degrade automatically. Do not shorten again on top of a preset.

**D. Global safety net (last resort).** Only for a legacy codebase you cannot audit, and even then exempt loaders:

```css
@media (prefers-reduced-motion: reduce) {
  *:not(.spinner):not(.progress), *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

What stays under reduced motion: opacity fades, colour changes, spinners (as gentle pulses), progress, `press` / `release` / `drag` springs (they follow the user's own hand). What goes: parallax, large translations, zooms, spins, folds, blur, particles, smoke, confetti, autoplaying loops, background scale-downs.

Functional vs decorative test: does removing this animation break the user's ability to understand what happened? If yes it is functional and needs a non-motion alternative (instant state change, colour, text). If no it can be fully removed.

Tailwind v4: `motion-safe:` adds the transform, `motion-reduce:` keeps the fade. Prefer a softened alternative over `motion-reduce:transition-none`.

```tsx
<div className="opacity-100 transition-opacity duration-300 ease-out
                motion-safe:transition-[transform,opacity] motion-safe:translate-y-0" />
```

JS:

```js
const reduce = matchMedia("(prefers-reduced-motion: reduce)");
reduce.matches; reduce.addEventListener("change", update);
// Motion: const shouldReduce = useReducedMotion(); const closedX = shouldReduce ? 0 : "-100%";
```

React hook:

```jsx
function useReducedMotion() {
  const [reduced, set] = useState(() => matchMedia("(prefers-reduced-motion: reduce)").matches);
  useEffect(() => {
    const mq = matchMedia("(prefers-reduced-motion: reduce)");
    const on = (e) => set(e.matches);
    mq.addEventListener("change", on);
    return () => mq.removeEventListener("change", on);
  }, []);
  return reduced;
}
```

---

## 2. Vestibular safety

- Avoid large-scale motion: full-screen zooms, parallax, spinning, anything that moves the whole viewport.
- Avoid continuous or looping motion that cannot be paused. Provide a pause control for ambient animation; respect `data-playing="false"` in shimmers and loaders.
- Scale changes above ~10% on large surfaces and rotations beyond a few degrees are triggers; gate them behind reduced motion.
- Flashing: never more than three flashes per second.

---

## 3. ARIA and announcements

```html
<div aria-live="polite" aria-atomic="true">…toast text…</div>   <!-- role="status" for toasts -->
<div role="alert">…error…</div>                                  <!-- assertive; errors only -->
<div role="progressbar" aria-valuenow="65" aria-valuemin="0" aria-valuemax="100"></div>
<button aria-busy="true" aria-disabled="true">Saving…</button>
<button role="switch" aria-checked="true">…</button>
<button role="checkbox" aria-checked="false">…</button>
<button aria-expanded="true" aria-controls="panel-1">…</button>
<span role="img" aria-label="In progress">…spinner badge…</span>
```

- Decorative layers (particles, glare, blob layers, skeletons) get `aria-hidden="true"`.
- A rolling number keeps its `aria-label` in sync with the full value; add `aria-live="polite"` only if the number matters to screen-reader users.
- Route changes announce the new page title.
- Shimmer / thinking states: `role="status"` on the line so the state text is announced when it changes.

---

## 4. Focus

- Modals trap focus inside and return it to the trigger on close; Escape and scrim click both close.
- Focus rings are instant and visible: `:focus-visible { outline: 2px solid currentColor; outline-offset: 2px; }`. Never animate a focus ring in; never remove it for keyboard users.
- Hover-only affordances (arrow slide, tilt, glare) must not carry meaning: keyboard and touch fall back to the resting state and lose nothing.
- Satellite buttons in a collapsed menu are `tabindex="-1"` and `pointer-events: none` while closed, so they neither swallow clicks nor trap focus.

---

## 5. Touch and pointer

- Touch targets: 44×44px minimum (48×48dp on Android). Pad the hit area, not just the visual.
- Gate hover motion behind `@media (hover: hover) and (pointer: fine)`; provide `:active` feedback for touch.
- `touch-action: none` only on the element that is actually dragged; never on the page.
- `-webkit-tap-highlight-color: transparent` on custom pressables, but then provide your own press feedback.

---

## 6. Checklist

- [ ] Tested with reduced motion ON — every component still communicates state
- [ ] No vestibular triggers ungated (zoom, spin, parallax, viewport-scale motion)
- [ ] Loops can be paused; loaders remain visible under reduced motion
- [ ] Functional animations have non-motion alternatives
- [ ] Every task completable with animation disabled
- [ ] Live regions on toasts/status; `aria-hidden` on decorative layers
- [ ] Focus trapped and returned for modals; rings instant
- [ ] Hover gated; touch targets ≥ 44px; `:active` feedback exists
