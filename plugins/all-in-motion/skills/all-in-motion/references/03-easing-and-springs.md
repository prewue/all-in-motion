# Easing and springs — the most important decision after "should it animate"

> Easing is the single most influential ingredient of an animation: the right curve rescues mediocre timing, the wrong one ruins perfect timing.

Wrong easing propagates poor feel through the whole interaction even when everything else is right. Tokens are in `02-tokens.md`; this file is the reasoning and the techniques.

---

## 1. Which easing

| Situation | Easing | Why |
| --- | --- | --- |
| Entering or exiting the screen | `--ease-out` | Starts fast (immediate response), settles smoothly. `ease-out` at 200ms *feels* faster than `ease-in` at 200ms. |
| Already on screen, moving to a new place | `--ease-in-out` | Accelerates then decelerates, like a vehicle. Carousels, tab indicators, reorders, drag settle. |
| In-place cross-fade / swap | `--ease-swap` (`ease-in-out`) | Symmetric blend reads as one object changing. |
| Hover colour / fill | `--ease-hover` (`ease`) | The keyword is fine for colour; anything more complex needs a custom curve. |
| Constant motion (progress, shimmer, marquee, spinner, hold fill) | `--ease-linear` | Progress should not ease; a fill that eases lies about time. |
| Drawer / bottom sheet | `--ease-drawer` at 500ms | Matches the native iOS sheet curve; it makes 500ms feel faster than it is. |
| Pure fade-away exit with no movement | `--ease-exit` | The only place ease-in belongs: the element is leaving and nobody is watching the end. |
| Entrance pop / emphasis | `--ease-bounce` or a spring preset | Overshoot says "arrived". Entrances only. |
| Hover-out return | `--ease-bounce-strong` | The row settles instead of snapping. |
| Playful / marketing | `--ease-overshoot`, `linear()` bounce | Personality. Not on utility UI, error states, or anything repeated. |
| Gesture-driven, interruptible, "alive" | spring | Carries velocity across interruptions; no fixed duration. |

**Never `ease-in` on UI.** It is the more common mistake than `linear`. **Never `linear` for UI transitions** (robotic) except constant-rate motion.

Built-in keywords lack energy for deliberate motion. `transition: transform 200ms ease-out` feels generic; `cubic-bezier(0.22, 1, 0.36, 1)` feels intentional. Register curves once (CSS tokens, Tailwind `@theme`) rather than repeating 30-character literals that drift when a digit is mistyped.

---

## 2. Easing has personality

Each curve communicates something. Context matters more than rules: "You wouldn't use Elastic for a bank's website, but it might work perfectly for an energetic site for children." Brand personality drives easing choice. When NOT to use bouncy/elastic: professional or enterprise apps, frequently repeated interactions (gets tiresome), error states or serious UI, anywhere users need to complete tasks quickly.

---

## 3. Springs

Nothing in the real world moves on a perfect Bézier. Springs simulate physics: no fixed duration, they settle on their parameters, and — the decisive property — **they preserve velocity when interrupted**. A CSS transition or keyframe restarts from a computed value; a spring reverses mid-gesture with the momentum it had. Use springs for:

- drag with momentum, drag-to-dismiss, snap points
- elements that should feel alive (Dynamic Island, a floating pill)
- gestures the user can interrupt or reverse
- decorative mouse-tracking (interpolate with `useSpring`; direct binding to the pointer has no momentum and reads artificial)
- any value that should interpolate smoothly rather than snap (a counter, a position)

Not for: speed-critical functional UI where a fixed ease-out is faster and calmer, or anything triggered hundreds of times a day.

### Two ways to write one

```js
// Apple-style: duration + bounce. Easier to reason about. Recommended.
{ type: "spring", duration: 0.5, bounce: 0.2 }

// Physics: precise control when the duration model cannot express it.
{ type: "spring", mass: 1, stiffness: 100, damping: 10 }
```

Bounce 0.1–0.3 for UI; `bounce: 0` is the production default: smooth deceleration without overshoot. Reserve visible bounce for drag-to-dismiss and playful moments. `stiffness: 700, damping: 15` overshoots wildly and is hard to tune by intuition.

### The SwiftUI model (used for the presets)

`response` (seconds, roughly the period) and `dampingFraction ζ` (1 = critically damped, no overshoot; lower = bouncier), mass 1:

```
stiffness k = (2π / response)²
damping   c = 4π · ζ / response
bounce     = 1 − ζ            (SwiftUI's bounce parameter)
```

`scripts/spring.py R Z` prints stiffness, damping, bounce, settle time (until within 0.1% of target), overshoot and a CSS `linear()` curve. `assets/motion.ts` has `springEase(r, ζ)` for GSAP or hand-rolled loops, and `motionTransition()` / `reactSpring()` / `waapi()` to hand the same preset to each library.

### Springs in pure CSS: `linear()`

`linear()` accepts a sampled curve, which is how a spring (or a bounce/elastic curve) runs in CSS and WAAPI with no JS. Chrome/Edge 113+, Safari 17.2+, Firefox 112+; older browsers fall back to the default easing at the same duration, which is acceptable.

```css
:root {
  --bounce-easing: linear(
    0, 0.004, 0.016, 0.035, 0.063, 0.098, 0.141 13.6%, 0.25, 0.391, 0.563, 0.765,
    1, 0.891 40.9%, 0.848, 0.813, 0.785, 0.766, 0.754, 0.75, 0.754, 0.766, 0.785,
    0.813, 0.848, 0.891 68.2%, 1 72.7%, 0.973, 0.953, 0.941, 0.938, 0.941, 0.953,
    0.973, 1, 0.988, 0.984, 0.988, 1
  );
}
```

Generator for custom curves: https://linear-easing-generator.netlify.app/ (Jake Archibald). The twenty presets are already sampled in `motion-springs.css`. A spring in a `transition` animates from wherever the value is when it changes, so an interrupted hover reverses smoothly from its current point.

### Interruptibility test

Click rapidly. Animations should blend, not queue and not jump. Springs and CSS transitions pass; keyframes fail (they restart from zero). Test it before shipping any toggle, toast, or drawer.

---

## 4. Duration is timing, timing is naturalness

- 150–250ms for micro UI (buttons, toggles, tooltips, dropdowns).
- 250–400ms for larger context switches (modals, panels, page transitions).
- 500ms for sheets/drawers with the iOS curve; success and reveal moments.
- Longer only for marketing, onboarding, first-run.
- **Asymmetric**: deliberate phases slow (hold-to-confirm 2s linear), system responses snap (release 200ms ease-out). Closes 60–75% of opens.
- **Delay vs duration**: if motion feels late, trim the duration before adding delay. Delay is for intent gating (tooltip 80ms), stagger, and deliberate sequencing — never padding, never on a close or a hover-out.
- **Stagger**: 30–80ms between items; total (offset × count) under ~300ms so the last item is not late. For long lists cap the staggered items or shrink the offset. Stagger is decorative — it must never block interaction.
- **Negative delays** (`animation-delay: calc(var(--i) * -0.2s)`) make a looping group appear already mid-flight instead of booting in sync.
- **`animation-fill-mode: backwards`** for delayed fade-ins, or elements flash at full opacity before their delayed animation starts. `both` when the end state must hold too.

---

## 5. Tooltip timing

First tooltip in a group: delay (80–300ms) + animation. Subsequent tooltips while one is open: **instant** — skip both delay and animation (`[data-instant] { transition-duration: 0ms; transition-delay: 0ms; }`). The delay filters accidental hovers; skipping it afterwards makes the whole toolbar feel faster. A shared bubble that *travels* between neighbouring triggers (tween x and width on `--motion-quick`) is the polished version.

---

## 6. Perceived performance

Faster animations do not just finish sooner; they make the whole interface feel more responsive. 180ms vs 400ms is a different product. When in doubt, go faster. A faster spinner makes the same load feel shorter. Instant subsequent tooltips make a toolbar feel faster. The reverse is also true: one 600ms dropdown makes everything around it feel slow.
