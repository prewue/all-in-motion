# Debugging feel — how to check what code cannot tell you

Most animation flaws are invisible at full speed. These are the checks to prescribe (and to run) whenever feel is uncertain.

## 1. Slow it down

- Bump the duration 5–10× while tuning (`160ms → 1600ms`), then revert. Or in DevTools → Animations panel set playback to 10–25%.
- Programmatically: `document.getAnimations().forEach(a => a.playbackRate = 0.2)` slows every running CSS transition/animation and WAAPI animation; new ones need it again (hook `transitionrun` / `animationstart`). The demo page ships this as a toggle.
- Look for: two overlapping states in a crossfade instead of one blend · easing that starts or stops abruptly · a `transform-origin` scaling from the wrong point · `opacity`, `transform` and `color` drifting out of sync · a close that bounces · a jump at the start or end.

## 2. Frame by frame

Chrome DevTools → Animations: scrub the timeline. Timing drift between coordinated properties (highlight bar vs text colour, shadow vs lift) shows up here and nowhere else. If two properties should change as one thing and keep drifting, make them one thing (clip-path reveal of a duplicated layer) rather than tuning delays.

## 3. Rapid re-trigger

Click / toggle five times in a second. Motion should blend and retarget, never queue, never jump to zero. Failing this means keyframes where a transition or spring belongs, or a missing close-cleanup.

## 4. Real devices

Gestures (drawers, swipe-to-dismiss, wheels, tilt) only tell the truth on a phone: connect one, hit the dev server by IP, use Safari's remote inspector for iOS. Check: momentum dismissal on a short flick · damping past edges · a second finger not stealing the drag · scroll vs drag conflict at the top of a sheet · no page scroll during a drag (`touch-action`) · 60fps on a mid-range device with 3–5 concurrent animations.

## 5. Reduced motion

Toggle the OS setting (macOS: Accessibility → Display → Reduce motion; DevTools → Rendering → Emulate `prefers-reduced-motion`). Every state change must still be legible; loaders still load; nothing bounces.

## 6. Both themes, real content

Blur bridges and glow layers behave differently on dark surfaces (`multiply` vanishes; use `screen`). Long labels, empty states and RTL change distances and origins. Check each demo at 320px width.

## 7. Fresh eyes

Look again the next day. Imperfections invisible during development surface after a night. Then test the tenth interaction in a row: does it still feel right, or has it become friction?

## 8. Feel-check prompts to hand the user

When the result depends on something code cannot settle, say so and point at the check:
- "Play it at 25% in DevTools and watch the crossfade — if two states overlap, add a 2px blur bridge."
- "Toggle it five times fast; if it jumps, switch the keyframes to a transition."
- "Test the swipe on a real phone; the 0.11 px/ms threshold may need ±20% for your card size."
- "The opacity/height balance in the entering list is trial and error; tune, then look tomorrow."

## 9. Measuring

- `performance.now()` deltas around a gesture for velocity; substep physics in ≤16ms slices.
- Chrome DevTools → Performance: look for long purple (style/layout) bars during a transition — a sign of layout properties, CSS-variable cascades, or per-frame `getComputedStyle`.
- Layers panel: count promoted layers; over ~10 during an interaction means `will-change` is too broad.
- Safari Web Inspector → Timelines → Rendering for filter cost.
