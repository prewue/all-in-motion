---
name: all-in-motion
description: The complete UI motion and micro-interaction system for web interfaces — build, review, polish and audit animation with one doctrine, one token scale, twenty spring presets and a 79-recipe catalog (press, hover, toggles, checks, dropdowns, tooltips, modals, drawers, toasts, tabs, page slides, data tables, expandable rows, text/icon/number swaps, skeletons, shimmers, loaders, reveals, staggers, drag/swipe/tilt gestures, confetti, dissolves, gradient text) with a live demo page. Use whenever the user asks to animate, add motion, transition, make something feel smooth/alive/snappy/polished/Apple-like, choose an easing, duration or spring, fix janky or slow animation, add hover/press/loading/success/error feedback, build a toast/drawer/dropdown/tooltip/tab/carousel/counter, implement drag-to-dismiss or swipe, review or audit animations, tokenize motion, handle prefers-reduced-motion, or mentions micro-interactions, motion design, Framer Motion/Motion, GSAP, react-spring, WAAPI, View Transitions, Tailwind motion utilities.
---

# All-In-Motion

One system that closes the whole UI-motion question: **judgment** (should it move, how much, in what character), **values** (one token scale, springs), **recipes** (79 drop-in animations) and **process** (build → review → polish → audit). Web first (CSS, WAAPI, React/Motion, Vue, Svelte, Tailwind), with a native mapping for iOS/Android/RN.

## Step 0 — detect the mode

| Signal | Mode | Read |
| --- | --- | --- |
| "animate", "add motion", "make it feel…", "build a toast/dropdown/…", "transition" | **Build** | this file → catalog entry → `references/01`, `02` |
| "review", "is this animation good", a diff or snippet to critique | **Review** | `references/08-review-and-audit.md §1` + `07-anti-patterns.md` |
| "polish", "tune the timing", "tokenize", "align to tokens", "too slow/fast" | **Polish** | `references/08 §3` + `02-tokens.md` |
| "audit my animations", whole codebase, "where would motion help" | **Audit** | `references/08 §2` (reconnaissance first, confirm weighting, then audit) |
| Ambiguous ("look at this modal animation") | ask: build or review? | — |

## Build sequence — decisions in the order that determines feel

1. **Frequency gate.** 100+/day or keyboard-initiated → no animation, say so, offer the instant alternative. Tens/day → near-imperceptible. Occasional → standard. Rare → delight allowed. (`references/01-principles.md §1`)
2. **Purpose in one word**: feedback · orientation · state · preventing a jarring change · continuity · explanation · delight. Can't name it → don't build it.
3. **Context weighting**: restraint (productivity, dashboards) · polish (consumer, e-commerce, mobile) · expression (marketing, creative, kids). Infer from the request, `package.json`, CLAUDE.md, existing motion; state the inference; confirm only for whole components or audits. Match the codebase's existing tokens — never fork a parallel scale.
4. **Catalog first.** Match the visible element with `catalog/README.md`; start from the recipe, never from a blank file. If it is a *component* with focus/ARIA duties (dropdown, dialog, command menu), pair the recipe with a headless primitive rather than hand-rolling the widget.
5. **Tool**: cheapest that works — CSS transition → `@starting-style` → CSS animation → WAAPI → motion library (springs, layout, exit, gestures) → GSAP (timelines). No library for a fade.
6. **Properties**: `transform` + `opacity` (+ `clip-path`, budgeted `filter: blur`, `grid-template-rows` for accordions). Never `width/height/top/left/margin/padding`. Never `scale(0)`; enter from 0.9–0.97. Origin at the trigger; modals centered.
7. **Easing & duration** from `references/02-tokens.md`: enter/exit/open/close → `--ease-out` (`cubic-bezier(0.22, 1, 0.36, 1)`); on-screen movement → `--ease-in-out`; swaps → `ease-in-out`; colour → `ease`; constant motion → `linear`; drawers → `--ease-drawer` 500ms. Never `ease-in` on UI. UI ≤300ms (quick 150 / fast 250 / medium 350 / slow 400 / deliberate 500). Springs for gestures and "alive" elements: `open`/`close`/`state`/`press`/`release`/… presets, or `{ type: "spring", duration: 0.5, bounce: 0.2 }`.
8. **Asymmetry**: closes faster and quieter than opens; exits subtler than enters; deliberate phases slow, responses snap; overshoot only on entrances; never delay a close.
9. **Interruptible**: transitions or springs for anything re-triggerable; keyframes only for one-shots (replay with a reflow). Direct `style.transform` for drags.
10. **Reduced motion + hover gating ship in the same code**: gentler (opacity/colour kept, movement/blur/bounce dropped), never zero; `@media (hover: hover) and (pointer: fine)` around hover motion.
11. **Self-check** against `references/07-anti-patterns.md §1` (the never-ship table) and the AI-slop tells (§2). Run `scripts/scan.py <path>` on anything larger than a snippet, and mark any genuine exception `motion-ok: <reason>` rather than leaving it to be re-litigated.

## Output (build mode)

Write the code. Then, in a few lines: the gate result (tier + purpose, and anything rejected), the ingredients (tool · properties · curve · duration/spring), and what to feel-check when code cannot settle it (slow motion, rapid re-trigger, real device, next day). No menus of options — make the call, state the reason, ship it. Match the user's language for prose; code and identifiers stay in English.

## Hard rules

- No approximated values: every curve, duration, distance and spring comes from `02-tokens.md` or the catalog. Need a curve not listed → easing.dev / easings.co; need a spring → `scripts/spring.py R Z`.
- Extend the project's tokens; don't create a second scale. Map by **usage**, never by nearest number.
- Keep the diff small: touch only the files the animation needs; paste catalog CSS verbatim (exact property lists, `will-change`, reduced-motion block intact).
- One clock per gesture; animate what you swap, not the container that already animates.
- Never ship: `transition: all` · `scale(0)` · `ease-in` on UI · animation on keyboard/100+/day actions · layout-property animation · keyframes on toasts/toggles · ungated hover · missing reduced motion · bounce on a close or a utility control · looping pulse indicators.

## Assets

| Path | What |
| --- | --- |
| `assets/motion-tokens.css` | durations, easings, distances, scales, blur, stagger, shadows, reduced-motion overrides |
| `assets/motion-springs.css` / `.json` | twenty spring presets as CSS `linear()` + physics (generated) |
| `assets/motion.ts` | presets for WAAPI / Motion / react-spring / GSAP, `bezier()`, `readToken()`, blur budget, fold keyframes, `reveal()`, `rollDigits()`, `edgeFade()`, `wheelItem()`, `VelocityTracker`, `damp()` |
| `scripts/spring.py` | `R Z` → spring params + `linear()`; `--tokens` regenerates the spring assets |
| `scripts/scan.py` | static red-flag scanner (`transition: all`, `scale(0)`, `ease-in`, layout props, pulses, missing reduced motion, >300ms UI…). Reads only code, never comments or prose; a reviewed exception is marked `motion-ok: <reason>` on the line or the line above |
| `demo/index.html` | self-contained live page with every catalog animation, theme toggle, slow-motion switch |

## References (load on demand)

| File | Load when |
| --- | --- |
| `references/01-principles.md` | any build or audit — frequency gate, purpose, lenses, cohesion, asymmetry |
| `references/02-tokens.md` | choosing any value; polish mode |
| `references/03-easing-and-springs.md` | picking a curve, tuning a spring, `linear()` in CSS, stagger/delay/tooltip timing |
| `references/04-properties-and-performance.md` | tool choice, compositor rules, `will-change`, blur budget, clip-path, `@property`, WebKit gotchas, mobile budget |
| `references/05-interaction-patterns.md` | press/hover/tooltip/drag/swipe/sheet/toast/list/number behaviour |
| `references/06-accessibility.md` | reduced motion strategies, vestibular safety, ARIA, focus, touch |
| `references/07-anti-patterns.md` | self-check before shipping; the review escalation list; motion gaps |
| `references/08-review-and-audit.md` | review / audit / polish workflows and output formats |
| `references/09-frameworks.md` | CSS, WAAPI, Motion, react-spring, Vue, Svelte, Tailwind v4, GSAP, View Transitions, scroll-driven, native platforms |
| `references/10-debugging.md` | feel checks: slow motion, frame-by-frame, re-trigger, real devices, fresh eyes |
| `catalog/README.md` | decision rules + index of all 79 recipes; then the category file |

## Tone

Opinionated and brief. When the honest answer is "this shouldn't animate", give it. When feel cannot be settled from code, say so and prescribe the check instead of guessing a value.
