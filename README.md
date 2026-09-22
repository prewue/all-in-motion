# All-In-Motion

**The complete knowledge base for UI motion.**

Collected from across the discipline and distilled into one skill: when to animate, which curve and duration, and the code to ship. Drop-in, framework-agnostic, accessible by default, and fully open source.

| | |
| --- | --- |
| **79** | production recipes |
| **20** | measured spring presets |
| **1** | token scale |
| **0** | dependencies |

Open [`demo/index.html`](demo/index.html) in a browser to see every recipe running live.

---

## What this is

A [Claude Code Skill](https://docs.claude.com/en/docs/claude-code/skills): a folder of instructions and assets that an AI coding agent loads on demand when a task involves interface animation. It is also perfectly usable by hand — the catalog is plain CSS and JavaScript, and the tokens are a stylesheet.

It answers four different questions, which most motion resources answer only one of:

- **Should this move at all?** A frequency gate that produces zero lines of code when the honest answer is no.
- **What exact values?** One token scale plus twenty spring presets, chosen by usage rather than by taste.
- **What's the code?** 79 drop-in recipes, each with its markup hooks, its JavaScript, and its reduced-motion path.
- **Is the existing motion any good?** Review, audit and polish workflows with a static scanner.

---

## Install

### As a Claude Code skill

Clone into your skills directory and it is available immediately.

```bash
# Personal skills — available in every project
git clone https://github.com/prewue/all-in-motion.git ~/.claude/skills/all-in-motion

# or Project skills — committed alongside the repo, shared with the team
git clone https://github.com/prewue/all-in-motion.git .claude/skills/all-in-motion
```

Verify it loaded:

```
/skills
```

Then just describe what you need. The skill triggers on animation work without being named:

```
add a dropdown that opens from its trigger
make this toast feel less abrupt
review the motion in this diff
audit the animations in src/
```

### As a plain asset library, no agent involved

Copy two stylesheets into your project and reference the tokens.

```bash
curl -O https://raw.githubusercontent.com/prewue/all-in-motion/main/assets/motion-tokens.css
curl -O https://raw.githubusercontent.com/prewue/all-in-motion/main/assets/motion-springs.css
```

```css
/* tokens first, springs second */
@import "./motion-tokens.css";
@import "./motion-springs.css";
```

```css
.button {
  transition: transform var(--motion-quick) var(--ease-out);
}
.button:active {
  transform: scale(var(--scale-press));
}
```

For script-driven motion, add [`assets/motion.ts`](assets/motion.ts). It has no dependencies; strip the types for a JavaScript project.

```ts
import { waapi, motionTransition, transitions, VelocityTracker } from "./motion";

badge.animate(transitions.element(), waapi("open"));           // Web Animations API
<motion.div transition={motionTransition("hoverScale")} />      // Motion / framer-motion
```

Then open [`catalog/README.md`](catalog/README.md), find your component, and paste the recipe.

---

## Layout

```
SKILL.md              entry point: mode detection and the build sequence
references/           the reasoning — 10 files, loaded on demand
catalog/              the code — 79 recipes across 10 category files
assets/               tokens, spring presets, TypeScript helpers
scripts/              spring generator, static motion scanner
demo/index.html       every recipe, live, in one self-contained page
```

| Reference | Load it when |
| --- | --- |
| `01-principles.md` | deciding whether and how much something should move |
| `02-tokens.md` | choosing any duration, curve, distance or scale |
| `03-easing-and-springs.md` | picking a curve or tuning a spring |
| `04-properties-and-performance.md` | tool choice, compositor rules, WebKit gotchas |
| `05-interaction-patterns.md` | press, hover, drag, swipe, sheets, toasts |
| `06-accessibility.md` | reduced motion, vestibular safety, ARIA, focus |
| `07-anti-patterns.md` | self-check before shipping |
| `08-review-and-audit.md` | reviewing a diff or auditing a codebase |
| `09-frameworks.md` | CSS, WAAPI, React, Vue, Svelte, Tailwind, GSAP, native |
| `10-debugging.md` | when motion feels wrong and code cannot say why |

---

## Tools

### Spring generator

Any spring, as physics terms and as a CSS `linear()` curve.

```bash
python3 scripts/spring.py 0.3 0.8       # response (seconds), damping fraction
python3 scripts/spring.py --tokens      # regenerate every spring asset
```

```json
{
  "stiffness": 438.649,
  "damping": 33.51,
  "settleSeconds": 0.405,
  "overshoot": 0.0152,
  "cssLinear": "linear(0, 0.0201, 0.0716, …)"
}
```

### Motion scanner

Greps a project for the red flags the review workflow blocks on.

```bash
python3 scripts/scan.py src/
python3 scripts/scan.py src/ --json
```

It reads only code, never comments or prose. A reviewed exception is marked in place, and the scanner stops asking:

```css
.tooltip {
  /* motion-ok: the bubble tweens its width as it travels between triggers */
  transition: translate 150ms var(--ease-out), width 150ms var(--ease-out);
}
```

---

## The short version of the doctrine

1. **Run the frequency gate first.** Keyboard-initiated and 100+/day actions get no animation, ever. Producing zero lines of code is a success.
2. **Name the purpose in one word** — feedback, orientation, state, continuity — or don't build it.
3. **Animate `transform` and `opacity`.** Layout properties cost layout every frame.
4. **Never `ease-in` on UI.** It delays the exact moment the user is watching.
5. **Closes are faster and quieter than opens.** Overshoot belongs to entrances only.
6. **Reduced motion ships in the same block of CSS**, and means gentler, not zero.

The long version is in [`references/01-principles.md`](references/01-principles.md).

---

## Contributing

Recipes are welcome. A new one should:

- read the shared tokens rather than hardcoding values
- carry a `prefers-reduced-motion` path in the same snippet
- state its frequency tier and its purpose
- pass `python3 scripts/scan.py`, or carry a `motion-ok` note explaining why not
- come with a demo card in `demo/index.html`

## License

MIT
