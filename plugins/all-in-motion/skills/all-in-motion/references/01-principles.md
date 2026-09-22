# Principles — the doctrine behind every decision

This file is the judgment layer: how to decide whether something moves, how much, and in what character. Code lives in the catalog; values live in `02-tokens.md`.

---

## 0. The one sentence

> The best UI animation is the one the user never consciously notices. It makes the interface feel like it is listening.

If a user says "nice animation!" about a control they use every day, it is too prominent. If they say "this feels really nice" about the product as a whole, it is right. Exceptions are onboarding, celebrations, kids' products and marketing pages, where delight is the actual job.

---

## 1. The Frequency Gate — run this first, every time

Before choosing a curve, a duration or a library, ask **how often the user triggers this**:

| Frequency | Examples | Decision |
| --- | --- | --- |
| 100+ times a day, keyboard-initiated | ⌘K palette, arrow-key list navigation, shortcuts, tab switching in a tool | **No animation. Ever.** Instant state change. |
| Tens of times a day | hover on rows, list navigation, filter chips, frequent toggles | Near-imperceptible: fast (≤150ms), tiny distance, or nothing |
| Occasional (daily) | modals, drawers, dropdowns, toasts, tooltips | Standard, fast UI motion (150–300ms) |
| Rare / first-time | onboarding, success, upgrade, empty states, celebrations | The delight budget lives here (springs, overshoot, particles, longer) |

**Keyboard-initiated is a disqualifier, not a judgment call.** A command launcher that people open hundreds of times a day is right to have no open/close animation at all.

Corollaries:
- Something that delights on the first use annoys on the hundredth. Design for the hundredth.
- A high-frequency tool (dashboard, editor, terminal UI) benefits from *less* motion than a consumer app.
- Marketing pages are the exception: one visit, so longer and more expressive is fine (500–1000ms).

If a request fails this gate, say so plainly and do not write the animation. Offer the non-motion alternative (instant state, static affordance, colour change). Producing zero lines of code is a success, not a dodge.

---

## 2. Purpose — name it in one word or don't build it

Every animation must answer "why does this move?" with one of:

- **Feedback** — the interface heard the user (press scale, check draw, colour change).
- **Spatial consistency / orientation** — where something came from or went (a dropdown grows from its trigger, a page slides in the direction of travel).
- **State indication** — a state change made legible (toggle travel, icon swap, badge appear).
- **Preventing a jarring change** — bridging content that would otherwise teleport (cross-fade, height change, list reflow).
- **Continuity** — keeping context through a transition (shared element, morph).
- **Explanation** — demonstrating how something works (onboarding, marketing only).
- **Delight** — only at the rare / first-time tier.

"It looks cool" on a frequently seen element is a reason to stop. Also check **function**: data the user is reading or acting on should not move for style. A mouse-tracking effect belongs on a landing page, not on a chart in a banking app.

---

## 3. The four parts of any micro-interaction

State these explicitly when designing something new:

```
TRIGGER  →  RULES  →  FEEDBACK  →  LOOPS & MODES
```

1. **Trigger** — what starts it (tap, hover, scroll, gesture, system event, timer).
2. **Rules** — what happens, what is allowed during it, what interrupts it.
3. **Feedback** — how the user knows it worked (visual, haptic, auditory; usually motion).
4. **Loops & modes** — does it repeat, change over time, behave differently in another context (first tooltip vs subsequent, first visit vs hundredth)?

The decision checklist that follows from it:

```
Does this action need confirmation?         → add feedback
Is something loading or processing?         → add progress / skeleton / shimmer
Is there a state change?                    → animate the transition (or make it instant if high-frequency)
Could the user miss something important?    → draw attention once, never in a loop
Is this frequent / repeated?                → be subtle, or remove
Is this purely decorative?                  → skip unless the tier allows delight
Does it work with animation disabled?       → it must
Would this frustrate on the 100th use?      → tone down or remove
```

---

## 4. The three lenses — weight them by context

Three perspectives answer three different questions. They are not universal rules; they are lenses to weight against the product.

| Lens | Question it asks | What it reaches for | Best for |
| --- | --- | --- | --- |
| **Restraint** | *Should this animate at all?* | frequency gate, sub-300ms, ease-out, nothing on keyboard actions, clip-path reveals, springs only for gestures | productivity tools, dashboards, dev tools |
| **Polish** | *Is this subtle and refined enough to ship?* | opacity + translateY + blur enters, subtler exits, springs without bounce, shadows over borders, optical alignment, animated icon swaps | shipped consumer apps, client work, e-commerce |
| **Expression** | *What could this become?* | `linear()` bounces, `@property`, decomposed transforms, 3D built from cuboids, negative delays, scroll-driven with fixed duration | creative sites, portfolios, kids' apps, learning |

Context → weighting:

| Project type | Primary | Secondary | Selective |
| --- | --- | --- | --- |
| Productivity tool (issue trackers, launchers, editors) | Restraint | Polish | Expression (onboarding only) |
| SaaS dashboard | Restraint | Polish | Expression (empty states) |
| Mobile app | Polish | Restraint | Expression (delighters) |
| E-commerce | Polish | Restraint | Expression (product showcase) |
| Marketing / landing page | Polish | Expression | Restraint (forms, nav) |
| Creative portfolio | Polish | Expression | Restraint (high-frequency interactions) |
| Kids / educational app | Polish | Expression | Restraint (high-frequency game loops) |
| Banking / serious UI | Restraint | Polish | — |

Duration follows the weighting: restraint-weighted → under 300ms (180ms ideal); polish → 200–500ms is fine where the surface is large; expression → whatever serves the effect. **Do not universally cap durations without checking the weighting first.** Synthesis: restraint decides *if*, polish decides *how* for production, expression decides *how far* when delight is the goal.

Infer the context from the request, `package.json`, CLAUDE.md and existing components before generating. For a small, well-specified request ("press-scale on this button") state the inference in one line and proceed; for a whole component or an audit, confirm it.

---

## 5. Cohesion — one product, one motion personality

- Motion should match the component's personality and the rest of the product. A playful product can be bouncier; a dashboard stays crisp. A well-tuned toast can be slightly slower with a plain `ease` and read as elegant precisely because pacing, visual design and copy all agree.
- **One clock per gesture**: everything that moves because of one action shares one preset. Two clocks for one gesture read as lag.
- **Extend the codebase's tokens, don't fork them.** If an `--ease-out` or a duration scale already exists, use it. A parallel system is a defect. If the project already animates with 500ms springs, a new 150ms ease-out component feels foreign — match the conventions unless they are the thing being fixed.
- **Same action = same feedback everywhere.** Consistency beats novelty.
- When unsure whether motion feels right, the strongest move is usually to delete it.

---

## 6. Enter vs exit, open vs close — asymmetry rules

- **Closes are faster and quieter than opens.** Opening is an invitation; closing should get out of the way. Dropdown/modal open 250ms → close 150ms. Panel open 400ms → close 350ms. Toast in 350ms → out 250ms.
- **Exits are subtler than enters**: smaller translate, same blur/opacity. The user's attention is already moving on. Exception: when the exit itself is meaningful (user-initiated dismissal, deletion, directional page transitions).
- **Exit the way it entered**: a toast that rises from the bottom leaves through the bottom. Symmetric paths make swipe-to-dismiss obvious.
- **Symmetric exceptions** (single reversible motions — do NOT split): page side-by-side, tab indicator slide, accordion, icon swap, text swap.
- **Overshoot belongs to entrances and emphasis only.** Never bounce a close. Never bounce a utility toggle, dropdown or menu (see anti-patterns).
- **Hover in vs out**: in is quick and direct (≤250ms, ease-out); out may be softer and springier so the row settles instead of snapping — the one place the *out* is more elaborate than the *in*.
- **Deliberate vs system**: slow where the user is deciding (hold-to-confirm fill 2s linear), instant where the system responds (release 200ms ease-out). Symmetric timing on a press-and-release is a finding.
- **Enter on `open`, leave on `close`**: opening lands with a little life (≈2.5% overshoot), closing never bounces away from a dismissal.

---

## 7. Feedback must be immediate

The interface should feel like it is listening. Every action gets instant visual feedback even when the real work takes time: pressed state at pointer-down (not on click), spinner replaces the label, success morphs in, errors shake once. Feedback should be instant even if the operation is slow. Never block input while a decorative animation plays.

---

## 8. Reduced motion is part of the animation, not a follow-up

Every animation ships with its `prefers-reduced-motion` variant in the same code. Reduced means **fewer and gentler**, not zero: keep opacity and colour, remove movement and position changes, collapse spring bounce, drop blur and folds. Loaders still need to communicate loading. See `06-accessibility.md`.

---

## 9. Animate what you swap

A container that already animates its entrance does not get a second transition on its root. Transitions go on the content replaced inside it. If a dialog component already slides in, do not also fold its root. Reserve space so swapped content does not shift its neighbours.

---

## 10. The Golden Rule, restated per tier

| Tier | The rule |
| --- | --- |
| Productivity UI | Motion is invisible: ≤300ms, ease-out, transform/opacity only, nothing on keyboard actions |
| Production polish | Users feel it but cannot point at it: blur enters, subtle exits, springs without bounce, 200–500ms where size warrants |
| Delight moments | Users are supposed to notice: overshoot, particles, longer, playful curves — once, on rare events |

When two treatments could fit, prefer the lower-overhead one (card resize over panel reveal, dropdown over modal, success check over a modal celebration) unless the design clearly calls for the heavier surface.
