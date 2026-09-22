# Interaction patterns — gestures, pointer, hover, timing of feedback

Motion that responds to the hand has its own rules. Most of these details exist because a shipped toast or drawer component broke without them.

---

## 1. Press feedback

- `transform: scale(0.97)` on `:active`, `transition: transform 150–160ms var(--ease-out)`. Subtle: 0.95–0.98. Applies to any pressable element, including cards and rows that act as buttons. `scale()` carries the label and icon along, which is what makes it read as a physical press.
- `:active` fires on touch; `:hover` does not (Tailwind v4's `hover:` only applies on hover-capable devices). Never make hover the sole feedback.
- Two-phase presses: `press` spring on pointer-down (follows the hand, 193ms), `release` on pointer-up (302ms, 3% overshoot). A large surface under a held press uses `surfacePress` / `surfaceRelease`.
- Press bounce for a confirmed primary action: scale to 1.15 on `bounce`, back to 1 on `release` 180ms later. Swap a play/pause glyph in the same click with a cross-fade on `state`.
- Pressed feedback at pointer-down, not on click. Immediate feedback even if the operation is slow (spinner in the label, `aria-busy`).

## 2. Hover

- Gate hover motion: `@media (hover: hover) and (pointer: fine)`. Touch devices fire `:hover` on tap and leave it stuck.
- Hover in: quick, ≤250ms, ease-out. Hover out: may be longer and springier so the element settles instead of snapping.
- Cards and rows change their fill, not their size (`hover` spring). Only clickable pills/badges grow (1.08, chips 1.06): the grow *means* "you can press this".
- Controls that appear on hover (edit, delete) fade in and sit `position: absolute` on top of the row so content never shifts to make room.
- Hover lift for cards: `translateY(-2…-4px)` + shadow expand, 200ms; return 250ms. Image zoom 1.05 inside if the card has one.
- Do not put `scale(1.05)` on every card, button and image; one primary CTA or one product tile is polish, a grid of them is slop.
- Hover fires while the page scrolls under a resting pointer: disable hover-driven effects inside scrolling content while it moves (`pointer-events: none` on hover children during `.is-scrolling`, cleared ~220ms after the last scroll event).
- Fill gaps between hoverable siblings with a pseudo-element (`::after` covering the margin) so hover persists when moving between stacked toasts or menu items.

## 3. Tooltips

- Intent delay before the first one (80ms for toolbars, up to 300ms for sparse UI) so a passing cursor does not trigger it. Fade + scale from 0.98, 150ms.
- Leave hides immediately (out 50ms, no delay). The delay belongs only to the show rule.
- Once one tooltip is open, neighbours open instantly and the single bubble *travels*: tween `translate` and `width` (160ms) to the new trigger instead of popping a second bubble.
- `transform-origin` toward the trigger (`50% 100%` for a tooltip above it).

## 4. Drag, swipe, dismiss

- **Momentum dismissal**: dismiss on distance **or** velocity. `velocity = |distance| / elapsedMs`; `> 0.11 px/ms` dismisses. A short fast flick should work; a long slow drag should too.
- **Damping at boundaries**: past a natural edge the element moves less the further it goes (rubber band). `y * 0.3` is a simple version; `damp()` in `motion.ts` is the asymptotic one. Things in real life slow down before they stop.
- **Friction, not a wall**: allow the "wrong" direction with rising resistance rather than blocking it. Acknowledging the input while guiding it feels soft; a hard stop feels broken.
- **Pointer capture**: `setPointerCapture(pointerId)` on pointer-down so the drag continues when the pointer leaves the element (users overshoot). Release on up/cancel.
- **Multi-touch protection**: `if (isDragging) return` on new pointers. A second finger must not start a fresh drag and snap the element to it.
- **Scroll vs drag in a scrollable sheet**: only start a drag when `scrollTop === 0`, and only after ~100ms at the top so scroll momentum does not accidentally dismiss (iOS behaviour: pause at the top before dragging to close).
- **Snap points with velocity**: slow drag → nearest point; fast flick (velocity > ~0.5 px/ms) → the point in the direction of travel, skipping intermediates. Target = `start + (dx + velocity × 0.2) / pitch` for a wheel picker.
- **Direct style writes** during the drag (`el.style.transform`), no transition while dragging; spring or transition only on release. Settle with `{ type: "spring", duration: 0.5, bounce: 0.2 }` so an interrupted drag keeps its velocity.
- **Velocity tilt** for dragged chips: rotate by horizontal velocity (~28°/px·ms, clamped ±10°) with a 150ms `rotate` transition to smooth jitter; level out on release.
- Reset JS-side offsets together with the CSS variables after a drop, or the next pointer-down solves its origin against a stale offset and the element teleports.
- `touch-action: none` on the dragged element; `user-select: none`; `draggable="false"` on inner images.
- Hit-testing a drop: use the dragged element's **centre** inside the zone, so a drop reads the same whichever corner leads. Show `.is-over` feedback on the zone during the hover.
- Keep the spring for `press`, `release`, `drag` under reduced motion — they follow the user's own hand — but skip decorative extras (smoke, particles).

## 5. Toasts

- Enter from the edge with `translateY(100%)` (own height), `@starting-style` or a mounted flag; `transition`, never keyframes — toasts get added rapidly.
- Slightly slower and plain `ease` (400ms) reads elegant for a notification; `--ease-out` 350ms with a 2px cross-blur and scale 0.97 is the crisper tuning. Both are correct; pick by product personality.
- Stacking: older toasts step back with `translateY(-14px × index) scale(1 − 0.05 × index)` and dim/blur slightly; hovering the stack fans it into a list (driven by pointer geometry, not `:hover`, because the gaps belong to no element). A fourth arrival sends the oldest out.
- Swipe to dismiss with velocity; upward drag with friction; pause the auto-dismiss timer on hover and when the tab is hidden.
- Opacity vs height when the list reflows is trial and error — adjust, then check again the next day.

## 6. Drawers and sheets

- `transform: translateY(100%)` closed → `0` open, `500ms var(--ease-drawer)`. Backdrop opacity on the same clock.
- Drag to dismiss with all of §4. Snap points (peek / half / full) with velocity.
- Damping when dragging above the top; scroll-lock inside until at top.
- Background scale-down (0.95) on open is optional and belongs to consumer apps, not tools.

## 7. Buttons that wait: hold-to-confirm

- A destructive action that is too easy to fire: fill an overlay with `clip-path: inset(0 100% 0 0) → inset(0)` over 2s `linear` while `:active`; release snaps back in 200ms ease-out. Linear is correct — the fill is a progress indicator. Fire the action at the end of the hold.

## 8. Keyboard

- Keyboard-initiated actions do not animate. Arrow-key list selection updates instantly (`transform` set with no transition). ⌘K palettes open instantly. Focus rings appear instantly (`:focus-visible`, 2px outline, 2px offset).
- Escape and outside-click close popovers immediately with the close motion; never delay a close.

## 9. Forms

- Never validate while typing; validate on blur. Valid: border + check fade-in 150ms. Invalid: border colour + one shake (6px legs, 4px overshoot, 280ms total, per-leg easing) + message reveal; auto-revert after ~3s; typing cancels the revert immediately.
- Shake once. Never loop attention on an error.
- Clearing a field: the text flies out (12px, blur 2px) as the placeholder falls in; a per-word glow streak is the premium version.

## 10. Lists and reorder

- Insert/remove on `state` with reserved space; items sliding aside on a spring when a dragged item needs room.
- Pickup: `scale(1.05)`, shadow up, opacity 0.9, 100ms; slight rotation while dragging; drop springs to place; cancel springs home with overshoot.
- Deletion with weight: fade + 2px blur where it was let go, or the smoky dissolve for a rare, delightful removal.

## 11. Numbers

- Frequent updates: roll only the changed characters (7px rise through 3px blur on `state`, tabular figures, one cell per character). `aria-live="polite"` only if the number matters to screen-reader users.
- Occasional updates that deserve a moment: number pop-in (each digit re-enters with blur, last two stagger).
- Jackpot moments: spinning reels with vertical-only blur.
- Never re-render the whole number as one block; nothing else should move.

## 12. Carousels, wheels, scrollers

- Paged carousel: `scroll-snap-type: x mandatory`; while moving, fade both edges (120ms) so what leaves goes into shadow; after rest, the fade lingers 250ms then eases away over 450ms. `pointer-events: none` on hover children while moving.
- Edge fade on scrolling rows: fade only the edge that has more content behind it (28px horizontal, 18px vertical), switching on `state`.
- Endless wheel: continuous position, items placed by distance from centre (scale 1 → ~0.63 next to it, opacity −0.3/step to 0.2 floor), wheel events move without animation and snap 90ms after the last one on `emphasis`, drag snaps to the momentum target, report the selection as it crosses centre.

## 13. Feedback on completion

- Spinner → check: the spinner arc pauses and fades, the green disc fades in over it, the check draws itself starting 200ms *before* the fill completes (sequenced, not queued), the whole badge cross-blurs 0.5px for the first 45% of the fill. Reverting is just flipping the state back.
- Success line: swap the status text for "✓ Saved" via the element transition and swap back after 2.4s.
- Add-to-cart: label → spinner (150ms) → check; thumbnail flies to the cart along an arc (500ms, `offset-path`); cart icon bounces; badge count rolls up; label returns after 2s.
