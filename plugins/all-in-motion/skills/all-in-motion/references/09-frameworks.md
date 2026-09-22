# Frameworks and platforms — the same motion in each stack

Install once: copy `assets/motion-tokens.css` and `assets/motion-springs.css` into the project (tokens first), and `assets/motion.ts` when script drives motion (strip types for JS). Then express every animation through `var(--…)` or the helpers so the whole product shares one scale.

---

## Plain CSS

```css
.button {
  transition:
    background-color var(--spring-hover-duration) var(--spring-hover-easing),
    transform var(--spring-release-duration) var(--spring-release-easing);
}
.button:active {
  transform: scale(var(--scale-press));
  transition-duration: var(--spring-press-duration);
  transition-timing-function: var(--spring-press-easing);
}
dialog[open] {
  animation: aim-reveal var(--spring-open-duration) var(--spring-open-easing) both;
  transform-origin: 50% 0;
}
```

A spring in a `transition` animates from wherever the value is when it changes, so an interrupted hover reverses from its current point. `linear()` is supported in Chrome/Edge 113+, Safari 17.2+, Firefox 112+; older browsers fall back to the default easing at the same duration.

Entry without JS: `@starting-style` (add `transition-behavior: allow-discrete` when `display` also toggles).

```css
.popover {
  opacity: 1; transform: scale(1);
  transition: opacity var(--motion-fast) var(--ease-out), transform var(--motion-fast) var(--ease-out), display var(--motion-fast) allow-discrete;
  @starting-style { opacity: 0; transform: scale(var(--scale-dropdown)); }
}
```

## Web Animations API

```ts
import { transitions, waapi } from "./motion";
badge.animate(transitions.element(), waapi("open"));
await note.animate(transitions.unfoldOut(), { duration: 100, easing: "cubic-bezier(0.42, 0, 1, 1)", fill: "both" }).finished;
el.animate([{ clipPath: "inset(0 0 100% 0)" }, { clipPath: "inset(0)" }],
           { duration: 600, easing: "cubic-bezier(0.77, 0, 0.175, 1)", fill: "forwards" });
```

Hardware-accelerated, interruptible (`anim.cancel()`, `anim.reverse()`), no bundle cost. Slow-motion debugging: `document.getAnimations().forEach(a => a.playbackRate = 0.2)`.

## React + Motion (framer-motion)

```tsx
import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { motionTransition } from "./motion";

<motion.button whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.97 }} transition={motionTransition("hoverScale")} />

<AnimatePresence mode="popLayout">
  <motion.span
    key={status}
    initial={{ opacity: 0, filter: "blur(14px)", scaleX: 0.8, rotateX: -12 }}
    animate={{ opacity: 1, filter: "blur(0px)", scaleX: 1, rotateX: 0 }}
    exit={{ opacity: 0, filter: "blur(14px)", scaleX: 0.8, rotateX: -12 }}
    transition={motionTransition("open")}
    style={{ transformOrigin: "50% 0", transformPerspective: 600 }}
  />
</AnimatePresence>

// Polished enter / subtler exit
<motion.div
  initial={{ opacity: 0, translateY: 8, filter: "blur(4px)" }}
  animate={{ opacity: 1, translateY: 0, filter: "blur(0px)" }}
  exit={{ opacity: 0, translateY: -4, filter: "blur(4px)" }}
  transition={{ type: "spring", duration: 0.45, bounce: 0 }}
/>

// Icon swap
<AnimatePresence mode="wait">
  {copied
    ? <motion.span key="check" initial={{ opacity: 0, scale: 0.8, filter: "blur(4px)" }} animate={{ opacity: 1, scale: 1, filter: "blur(0px)" }} exit={{ opacity: 0, scale: 0.8, filter: "blur(4px)" }}><CheckIcon/></motion.span>
    : <motion.span key="copy" …><CopyIcon/></motion.span>}
</AnimatePresence>

// Layout / shared element (keep layoutId elements outside AnimatePresence)
<motion.div layoutId="card" transition={{ layout: motionTransition("state") }} />

// Stagger
const list = { show: { transition: { staggerChildren: 0.04, delayChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 8 }, show: { opacity: 1, y: 0 } };

// Reduced motion
const reduce = useReducedMotion();
<motion.aside animate={{ opacity: open ? 1 : 0, x: open ? 0 : reduce ? 0 : "-100%" }} />
```

Under load prefer `animate={{ transform: "translateX(100px)" }}` over `x`. `useSpring(mouseX, { stiffness: 300, damping: 30 })` for decorative pointer following. `layout` animations run FLIP automatically.

## react-spring

```tsx
import { useSpring, animated } from "@react-spring/web";
import { reactSpring } from "./motion";
const style = useSpring({ scale: hovered ? 1.08 : 1, config: reactSpring("hoverScale") });
return <animated.button style={style} />;
```

## Vue

```vue
<Transition enter-active-class="aim-element-in" leave-active-class="aim-element-out" mode="out-in">
  <span :key="status">{{ status }}</span>
</Transition>
```

Vue waits for the CSS animation to end before removing the leaving node; use `<TransitionGroup>` with `move-class` for list reorders (FLIP built in).

## Svelte

```svelte
<script>
  import { springEase, waapi } from "./motion";
  function element(node) {
    const { duration } = waapi("open");
    return {
      duration,
      easing: springEase(0.47, 0.76),
      css: (t) => `opacity:${Math.min(1, t)};filter:blur(${(1 - Math.min(1, t)) * 14}px);transform-origin:50% 0;transform:perspective(600px) rotateX(${(1 - t) * -12}deg) scaleX(${0.8 + 0.2 * t})`,
    };
  }
</script>
{#key status}<span transition:element>{status}</span>{/key}
```

## Tailwind CSS v4

```css
@import "tailwindcss";
@theme {
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
  --ease-spring-open: var(--spring-open-easing);
  --duration-quick: 150ms;
  --duration-fast: 250ms;
}
```

| Principle | Utility |
| --- | --- |
| exact properties + ease-out + sub-300ms | `transition-[transform,opacity] duration-200 ease-out` (never `transition-all`) |
| press feedback | `transition-transform duration-150 ease-out active:scale-[0.97]` (`active:` fires on touch; `hover:` does not in v4) |
| asymmetric press/release | `duration-200 active:duration-[2000ms]`; JS-driven: `duration-200 data-[open]:duration-500` |
| enter with `@starting-style` | `transition-discrete transition-[transform,opacity] translate-y-0 opacity-100 starting:translate-y-full starting:opacity-0` |
| reduced motion | `opacity-100 transition-opacity motion-safe:transition-[transform,opacity] motion-safe:translate-y-0` |
| origin | `origin-top-left` … (nine positions) |
| will-change scoped | `data-[dragging=true]:will-change-transform` |
| hover gated | `hover:` is already hover-capable-only in v4; add `pointer-fine:` if configured |

Tailwind v3: add the same names under `theme.extend.transitionTimingFunction` / `transitionDuration`.

## GSAP

```ts
import { springEase, springPresets } from "./motion";
const open = springPresets.open.spring;
gsap.from(card, { scale: 0.4, opacity: 0, duration: open.settleSeconds, ease: springEase(open.response, open.dampingFraction) });
```

Use GSAP timelines for sequences across many elements; keep each tween on compositor properties.

## View Transitions API

```css
::view-transition-old(root), ::view-transition-new(root) {
  animation-duration: var(--motion-fast);
  animation-timing-function: var(--ease-out);
}
.hero { view-transition-name: hero; }   /* shared element across navigations */
```

```js
if (document.startViewTransition) document.startViewTransition(() => update());
else update();
```

Cross-fade surrounding content at 200ms, move the shared element over 300–400ms with an emphasized ease-out.

## Scroll-driven

```css
@supports (animation-timeline: view()) {
  .reveal { animation: aim-fade-up linear both; animation-timeline: view(); animation-range: entry 0% entry 40%; }
}
```

For "trigger once, then run on a fixed duration" use an IntersectionObserver (`rootMargin: "-100px 0px"`, unobserve after the first hit) and let CSS own the clock.

---

## Native platforms — the same decisions, different APIs

| | iOS (SwiftUI / UIKit) | Android (Compose / Material 3) | React Native |
| --- | --- | --- | --- |
| Default motion | springs: `.spring(response: 0.35, dampingFraction: 0.8)`, presets `.snappy` `.smooth` `.bouncy` `.interactiveSpring` | MD3 duration/easing tokens; `animateXAsState`, `AnimatedVisibility`, `AnimatedContent`, `Crossfade`; `spring(dampingRatio, stiffness)` | Reanimated 3: `useSharedValue`, `useAnimatedStyle`, `withSpring`, `withTiming` |
| Gestures | UIKit gesture recognisers / SwiftUI `DragGesture` with velocity | `Modifier.pointerInput`, `draggable`, `swipeable` | Gesture Handler `Gesture.Pan()`, `Gesture.Pinch()` |
| Shared element | `matchedGeometryEffect` | `SharedTransitionLayout` + `sharedElement()` / `sharedBounds()` | Reanimated shared transitions |
| Haptics | `UIImpactFeedbackGenerator`, `UINotificationFeedbackGenerator`, `UISelectionFeedbackGenerator` | `HapticFeedbackConstants`, `VibrationEffect` | `expo-haptics` / `react-native-haptic-feedback` |
| Reduced motion | `UIAccessibility.isReduceMotionEnabled`, `accessibilityReduceMotion` | `Settings.Global.ANIMATOR_DURATION_SCALE` | `AccessibilityInfo.isReduceMotionEnabled()` |
| Pre-built assets | Lottie / Rive | Lottie / Rive | `lottie-react-native`, Rive |

The spring presets map directly: `response` / `dampingFraction` are SwiftUI's parameters; `stiffness` / `damping` are Compose's and Reanimated's. Haptic ticks pair with threshold crossings (pull-to-refresh, swipe thresholds, toggle completion), never with every frame.
