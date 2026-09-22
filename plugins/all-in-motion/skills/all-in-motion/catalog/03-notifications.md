# Catalog · Notifications — toasts, stacks, badges

---

## 1. Toast (rise + cross-blur, slower in than out)

Tier: occasional. **Purpose**: state indication. Transitions, never keyframes — toasts get added rapidly and must retarget. One class gives the asymmetry.

```html
<div class="aim-toast" role="status" aria-live="polite" data-open="false">Changes saved</div>
```

```css
.aim-toast {
  position: fixed; left: 50%; bottom: 24px; translate: -50% 0;
  padding: 10px 14px; border-radius: 10px; background: #111; color: #fff; box-shadow: var(--shadow-float);
  opacity: 0;
  transform: translateY(16px) scale(var(--scale-dropdown));
  filter: blur(calc(var(--blur-small) * var(--motion-blur-scale)));
  will-change: transform, opacity, filter;
  transition: opacity var(--motion-fast) var(--ease-out), transform var(--motion-fast) var(--ease-out), filter var(--motion-fast) var(--ease-out);   /* rest = out: 250 */
}
.aim-toast[data-open="true"] {
  opacity: 1; transform: translateY(0) scale(1); filter: blur(0);
  transition: opacity var(--motion-medium) var(--ease-out), transform var(--motion-medium) var(--ease-out), filter var(--motion-medium) var(--ease-out);   /* in: 350 */
}
@media (prefers-reduced-motion: reduce) { .aim-toast { transform: none; filter: none; transition: opacity var(--motion-quick) var(--ease-out); } }
```

Two correct personalities: the crisp one above, or the elegant one — `transition: opacity 400ms ease, transform 400ms ease` with `translateY(100%)` from `@starting-style` and no blur. Pick by product. `translateY(100%)` moves by the toast's own height whatever its content.

`@starting-style` version for a toast that mounts already open:

```css
.aim-toast--auto {
  opacity: 1; transform: translateY(0);
  transition: opacity 400ms ease, transform 400ms ease;
  @starting-style { opacity: 0; transform: translateY(100%); }
}
```

Behaviour: auto-dismiss ~4s, pause the timer on hover and when the tab is hidden, swipe to dismiss with velocity (`08-gestures.md`), upward drag with friction, close button always. Exit through the edge it entered from.

---

## 2. Toast stacking (newest in front, older push back)

Tier: occasional. Each new toast rises in; older ones step back: smaller, higher, dimmer. The fourth arrival sends the oldest out. Hover fans the stack into a readable list.

```html
<div class="aim-stack"></div>   <!-- banners appended by JS -->
```

```css
.aim-stack { position: fixed; right: 24px; bottom: 24px; width: 320px; height: 64px; }
.aim-stack-item {
  position: absolute; left: 0; right: 0; bottom: 0; padding: 12px 14px; border-radius: 12px; background: #fff; box-shadow: var(--shadow-float);
  transform-origin: 50% 50%; filter: blur(0);   /* explicit blur(0): blur → none does not interpolate */
  will-change: transform, opacity, filter;
  transition: transform var(--motion-medium) var(--ease-out), opacity var(--motion-medium) var(--ease-out), filter var(--motion-medium) var(--ease-out);
}
.aim-stack-item[data-depth="0"] { z-index: 3; transform: translateY(0) scale(1); opacity: 1; }
.aim-stack-item[data-depth="1"] { z-index: 2; transform-origin: 50% 100%; transform: translateY(-12px) scale(0.94); opacity: 0.6; filter: blur(calc(1px * var(--motion-blur-scale))); }
.aim-stack-item[data-depth="2"] { z-index: 1; transform-origin: 50% 100%; transform: translateY(-24px) scale(0.88); opacity: 0.36; filter: blur(calc(2px * var(--motion-blur-scale))); }
.aim-stack.is-spread .aim-stack-item[data-depth="1"], .aim-stack.is-spread .aim-stack-item[data-depth="2"] { opacity: 1; filter: blur(0); }
.aim-stack.is-spread .aim-stack-item[data-depth="1"] { transform: translateY(calc((100% + 8px) * -1)) scale(1); }
.aim-stack.is-spread .aim-stack-item[data-depth="2"] { transform: translateY(calc((100% + 8px) * -2)) scale(1); }
.aim-stack-item.is-enter { transition: none; transform: translateY(60px) scale(var(--scale-dropdown)); opacity: 0; filter: blur(calc(var(--blur-small) * var(--motion-blur-scale))); }
.aim-stack-item.is-leaving { z-index: 0; transform-origin: 50% 100%; transform: translateY(-36px) scale(0.82); opacity: 0; filter: blur(var(--blur-small));
  transition: transform var(--motion-fast) var(--ease-out), opacity var(--motion-fast) var(--ease-out), filter var(--motion-fast) var(--ease-out); }
@media (prefers-reduced-motion: reduce) { .aim-stack-item { transition: opacity var(--motion-quick) var(--ease-out); transform: none !important; filter: none !important; } }
```

```js
function createStack(stack) {
  let items = [];                                        // newest first
  function add(html) {
    const el = document.createElement("div");
    el.className = "aim-stack-item is-enter"; el.dataset.depth = "0"; el.setAttribute("role", "status"); el.innerHTML = html;
    items.unshift(el); stack.appendChild(el);
    items.forEach((b, i) => {
      if (i === 0) return;
      if (i > 2) { if (!b.classList.contains("is-leaving")) { b.classList.add("is-leaving"); setTimeout(() => b.remove(), 310); } }
      else b.dataset.depth = String(i);
    });
    items = items.slice(0, 3).concat(items.slice(3).filter((b) => !b.classList.contains("is-leaving")));
    void el.offsetWidth;                                 // flush the pre-open rest state in the SAME task (a rAF hop can be throttled away)
    el.classList.remove("is-enter");
  }
  // spread is pointer geometry, not :hover — the gaps between fanned items belong to no element
  const stage = stack.parentElement;
  const within = (e, above) => { const r = stack.getBoundingClientRect(); return e.clientX >= r.left && e.clientX <= r.right && e.clientY <= r.bottom && e.clientY >= r.top - above; };
  stage.addEventListener("pointermove", (e) => {
    if (stack.classList.contains("is-spread")) { if (!within(e, (stack.offsetHeight + 8) * 2)) stack.classList.remove("is-spread"); }
    else if (within(e, 0)) stack.classList.add("is-spread");
  });
  stage.addEventListener("pointerleave", () => stack.classList.remove("is-spread"));
  return { add };
}
```

Compact variant without the fan: `transform: translateY(calc(-14px * var(--i))) scale(calc(1 - 0.05 * var(--i)))` with `--i` set per toast — the classic offset + scale depth.

---

## 3. Notification badge (slide in + pop the dot)

Tier: occasional. **Purpose**: state indication / attention (once). Animate the dot, not the trigger.

```html
<button class="aim-press" style="position:relative">🔔
  <span class="aim-badge" data-open="false"><span class="aim-badge-dot">3</span></span>
</button>
```

```css
.aim-badge { position: absolute; top: -6px; right: -8px; pointer-events: none; will-change: transform; }
.aim-badge[data-open="true"] { animation: aim-badge-slide 260ms var(--ease-out); }
@keyframes aim-badge-slide { from { transform: translate(-8px, 12px); } to { transform: translate(0, 0); } }
.aim-badge-dot {
  display: grid; place-items: center; min-width: 18px; height: 18px; padding: 0 5px; border-radius: 999px; background: var(--danger, #e5484d); color: #fff; font-size: 11px; font-weight: 600;
  transform-origin: center; transform: scale(1); opacity: 1; filter: blur(0);
  transition: transform var(--motion-deliberate) var(--ease-bounce), opacity var(--motion-slow) var(--ease-bounce), filter var(--motion-deliberate) var(--ease-bounce);   /* open: pop */
}
.aim-badge[data-open="false"] .aim-badge-dot {
  transform: scale(0.5); opacity: 0; filter: blur(var(--blur-small));
  transition: transform 180ms var(--ease-exit), opacity 180ms var(--ease-exit), filter 180ms var(--ease-exit);   /* close: quick ease-in fade-away */
}
@media (prefers-reduced-motion: reduce) { .aim-badge { animation: none !important; } .aim-badge-dot { transform: none !important; filter: none; transition: opacity var(--motion-quick) var(--ease-out); } }
```

Count changes: roll the digits (`05-content-swap.md`). Do **not** add a pulse loop to draw attention — a single pop on arrival is the whole attention budget.

---

## 4. Banner (top of page, dismissible)

Same recipe as the toast with `translateY(-16px)` and `transform-origin: 50% 0`; stack with the same depth rules. A banner that appears on every page load for returning users should not animate at all (it is a high-frequency element for them): animate on first appearance only, using a session flag.
