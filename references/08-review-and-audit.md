# Review, audit and polish workflows

Three related jobs, three postures:

| Mode | Input | Output | Posture |
| --- | --- | --- | --- |
| **Review** | a diff / a component / a snippet | findings table + verdict (Block / Approve) | adversarial; approval is earned |
| **Audit** | a whole codebase | per-lens report, motion gaps, severity tables, optional HTML report with looping demos | reconnaissance first, never apply rules blindly |
| **Polish** | motion that already exists | token-aligned change list, then applied edits on confirmation | match on usage, never on the nearest number |

---

## 1. Review

### Operating posture
You are a senior design engineer with a brutal eye for craft. Bias toward motion that *feels* right, not motion that merely runs. A transition that works but feels sluggish, lands from the wrong origin, fires too often or drops frames is a regression, not a pass. Default to flagging.

### The ten standards — a violation is a finding
1. **Justified**: every animation answers "why" (feedback, orientation, state, continuity, explanation). "Looks cool" on a frequent element is a block.
2. **Frequency-appropriate**: keyboard and 100+/day get none; tens/day get near-imperceptible; occasional standard; rare may delight.
3. **Responsive easing**: enters/exits on ease-out or a strong custom curve; `ease-in` on UI is a block; built-in keywords too weak on deliberate motion.
4. **Sub-300ms UI**: anything slower on a UI element needs a stated reason.
5. **Origin & physicality**: trigger-anchored surfaces scale from the trigger; never from `scale(0)`; modals stay centered.
6. **Interruptible**: rapidly-triggered or gesture-driven motion retargets (transitions/springs), never restarts (keyframes).
7. **Compositor-only**: transform/opacity (+ clip-path, budgeted blur); layout properties and library shorthands under load are findings.
8. **Accessible**: reduced-motion honoured (gentler, not zero); hover gated behind a pointer query.
9. **Asymmetric**: deliberate phases slow, responses snap; closes faster than opens; exits subtler than enters.
10. **Cohesive**: matches the component's personality and the product; one clock per gesture; when in doubt, delete.

### Escalation triggers — flag on sight
`transition: all` · `scale(0)` or pure-fade entrances · `ease-in` anywhere in UI · animation on keyboard/high-frequency actions · UI > 300ms unexplained · `transform-origin: center` on a popover · keyframes on toasts/toggles · layout-property animation · library `x/y/scale` under load · CSS-variable-driven child transforms · missing reduced motion · ungated hover · symmetric press/release · all-at-once entrance where a stagger belongs · bounce on a close or a utility action · delay on a close · looping pulses on indicators.

### Remedial hierarchy — propose earlier moves first
1. **Delete** (high-frequency, no purpose, keyboard-triggered).
2. **Reduce** (shorter, smaller transform, fewer properties).
3. **Fix easing** (ease-in → ease-out; keyword → custom curve).
4. **Fix origin / physicality** (transform-origin; `scale(0)` → 0.95 + opacity).
5. **Make interruptible** (keyframes → transitions; spring for gestures).
6. **Move to the compositor** (layout props → transform; shorthand → full string; WAAPI for programmatic CSS).
7. **Asymmetric timing**.
8. **Polish** (blur bridge, stagger, `@starting-style`, spring for alive elements).
9. **Accessibility & cohesion**.

### Output format (required)
**Part 1 — findings table.** One row per issue, `file:line` cited, exact replacement values from `02-tokens.md`, never approximated.

| Before | After | Why |
| --- | --- | --- |
| `transition: all 300ms` | `transition: transform 200ms var(--ease-out), opacity 200ms var(--ease-out)` | `all` animates unintended properties off the compositor |
| `transform: scale(0)` | `transform: scale(0.95); opacity: 0` | Nothing appears from nothing |
| `ease-in` on dropdown | `var(--ease-out)` | ease-in delays the moment the user watches most |
| `transform-origin: center` on popover | `top left` / `var(--transform-origin)` | Popovers grow from their trigger (modals exempt) |

**Part 2 — verdict**, grouped by impact tier, highest first, empty tiers omitted:
1. Feel-breaking regressions · 2. Missed simplifications · 3. Performance · 4. Interruptibility & timing · 5. Origin, physicality & cohesion · 6. Accessibility.

Close with **Block** (any feel-breaking regression, keyboard/high-frequency animation, `scale(0)`/`ease-in` on UI, an easily-fixable non-compositor animation) or **Approve** (durations and easing in bounds, nothing that should be deleted, interruptibility handled, reduced motion respected). When feel cannot be settled from code, say so and prescribe the check (slow motion, frame-by-frame, real device, fresh eyes) instead of guessing.

---

## 2. Audit

### Step 1 — reconnaissance (do this first)
1. Read CLAUDE.md, `package.json`, the component structure: what kind of product is this (productivity tool, marketing site, kids app, mobile PWA)?
2. Grep existing motion: `motion`, `animate`, `transition`, `@keyframes`, durations, easing, libraries. What conventions exist?
3. **Motion-gap analysis** (do not skip): conditional renders and ternary swaps without exit handling, dynamic inline styles without transitions, mode switches, expandable sections, loading→content, toasts, error states. See `07-anti-patterns.md §4`.
4. Run `scripts/scan.py` for the mechanical red flags.
5. Propose the lens weighting from the context table in `01-principles.md`, state your inference, and **confirm with the user before the full audit**:

```
## Reconnaissance
Project type: <inferred>
Existing motion style: <durations, curves, libraries, patterns>
Likely intent: <e.g. calm productivity / delight for children>
Motion gaps found: N conditional renders without transitions — <areas>
Proposed weighting: Primary <lens> · Secondary <lens> · Selective <lens>
Does this sound right, or should I adjust?
```

### Step 2 — full audit (after confirmation)
Work through, in order:
- **Philosophy**: frequency, keyboard, purpose, will users notice it on the 10th use, reduced motion tested, easing fits the brand, duration fits the context.
- **Motion gaps** (above).
- **Enter/exit**: opacity + translate (+ blur where it earns it); exits subtler; `fill-mode: backwards` on delayed sequences; no flash before delayed starts.
- **Easing & timing**: custom curves, springs for interactive elements, consistent related timings, origin at the source.
- **Visual polish**: shadows over borders on varied backgrounds, `oklch` gradients, blur used as a signal not a default, optical alignment of icons.
- **State transitions**: icon swaps animated, loading states smooth, hover transitions 150–200ms, press scale, no `scale(0)`.
- **Interaction**: tooltip first-delayed/then-instant, interruptible, clip-path for reveals, no animation on high-frequency/keyboard.
- **Performance**: `will-change` scoped, compositor properties, no purposeless loops, direct style writes for drags, velocity thresholds.
- **Accessibility**: reduced motion, vestibular triggers, pausable loops, non-motion alternatives.
- **Anti-pattern gate** (`07-anti-patterns.md §2`) with its frequency heuristics.

### Severity
- **Critical (must fix)**: missing reduced motion · layout-property animation · no exit animations · motion gaps in primary UI · keyboard/high-frequency animation · pulsing indicators.
- **Important (should fix)**: exits as prominent as enters · `scale(0)` · default keywords on deliberate motion · wrong origin · bounce on utility · uniform enters/staggers beyond the heuristics.
- **Context-dependent**: durations over 300ms (restraint flags, polish/expression may approve).
- **Opportunity**: optical alignment, `oklch` gradients, springs instead of ease, press feedback, tooltip delay pattern, a delight moment on a rare event.

### Scorecard (1–5 each; give fixes for anything under 4)
Feedback (critical) · Timing (high) · Easing (high) · Consistency (high) · Performance (critical) · Accessibility (critical) · Responsive/touch (high) · Purpose (medium) · Delight (medium) · Restraint (medium).

### Report
Per lens (ordered by weighting): what works (with `file:line`), issues (Critical/Important, each with What / Why it matters / Recommended motion / location), opportunities, and a one-paragraph "through this lens" take. Then combined tables by severity (Issue · File · Fix) and a closing note on which lens dominated and how to lean differently. Do not summarise per-lens findings away; users want the full perspective.

**HTML report (optional, default when a browser is available).** Write `motion-audits/<project>-<YYYY-MM-DD>.html` at the project root (git top-level, else cwd; do not touch `.gitignore`), self-contained, and open it. Design contract:
- Neutral cool-slate palette in `oklch`, dark by default with a pure-CSS `Dark / Light` toggle (`:root:has(#theme-light:checked)`); severity is the **only** colour (red / amber / green, fixed).
- **The report itself has no entrance, scroll or mount animation.** The only animated elements are the per-finding demo cards (Critical and Important only), each a looping CSS demo of the *recommended* motion: `animation-duration: 3s`, keyframes at 0% / ~60% / 100%, motion done by ~1.8s then held; the 100% state must equal the static rest state so the shell's reduced-motion guard (which disables all demo animations) shows the right visual. Suffix keyframe and class names with the finding index (`m{n}`, `.demo-{n}__mt`) so findings never collide. Demo stages carry their own tokens (`--st-bg`, `--st-fg`, `--st-line`, `--st-dim`) and a 3-state Auto/Light/Dark segmented switch.
- A duration-budget diagram (0–600ms axis; instant/responsive green, deliberate amber, sluggish red; missing transitions plotted as hollow dots at 0ms) plotting every animation found.
- Bans inside the report: no gradient text, no coloured `border-left` accent stripes, no pulsing UI, no chromatic accent by default.
- Print a 3-line terminal summary (counts · path · how to get the inline version). Terminal mode (`--terminal` / "show inline") renders the same content as decorated markdown and writes no file.

---

## 3. Polish (align existing motion to the tokens)

1. **Scan everything**: stylesheets, CSS-in-JS, styled-components, `<style>` blocks, inline `style=`, Tailwind arbitrary values (`duration-[300ms]`), library `transition={{…}}` props. Read `@keyframes` via the `animation` that drives them.
2. For every value infer **what the motion does** from selectors and component names (modal close, dropdown open, tooltip, badge appear, page slide, text reveal, shake, hover lift…).
3. Look the usage up in `02-tokens.md` and suggest the token whose documented usage matches. **Usage first, never nearest number.** If nothing matches, list it as `no matching token usage` and leave it.
4. Apply the polish rules: open/close asymmetry, hover in/out, stagger totals under ~300ms, delays only for intent/sequence, distance ≤ ~40px unless a panel, pre-scale ≥ 0.9, blur only on swaps/slides (and add it where the usage calls for it).
5. Output a numbered list grouped by file, only values that should change:
   - `src/Modal.css:L42` — `modal close: 300ms → var(--motion-quick) (150ms)` — closes are quicker than the 250ms open
   - `src/List.tsx:L20` — `stagger: 120ms → var(--stagger-base) (40ms)` — 8 × 120ms = 960ms, the last item is late
6. Do not edit until confirmed. On confirmation: replace with `var(--…)` where the tokens are imported, otherwise write the literal and note that importing the tokens would centralise it; keep the file's unit style; touch only motion values; handle plain CSS, modules, CSS-in-JS, Tailwind utilities/config, inline style objects and library variants. Offer to install `assets/motion-tokens.css` once if absent. End with a one-line summary of files touched.
