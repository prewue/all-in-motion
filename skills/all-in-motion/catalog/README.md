# Catalog index — every prepared animation

79 recipes, all `aim-*` classes, all reading the shared tokens, all with a reduced-motion path. Live examples of each: `demo/index.html`.

## Decision rules — match the visible element first, then the verb

| You see… | Use |
| --- | --- |
| Any pressable element | **Button press** (01·1) — always |
| Primary action that deserves a "got it" | **Press bounce** (01·2) |
| Mouse over a row / card / pill | **Hover fill / grow / lift** (01·3) — fill for rows, grow only for clickable pills |
| Like / favourite / heart | **Like button** (01·4) |
| Boolean box | **Checkbox** (01·5) · switch → **Toggle** (01·6) · chip → **Selected pill** (01·7) |
| "Done / paid / uploaded" moment | **Success check** (01·8); row-level spinner that ends → **Spinner→check morph** (01·9) |
| Invalid input, wrong PIN | **Error shake** (01·10) — once |
| Destructive click too easy to fire | **Hold to confirm** (01·11); inline "Delete?" → **Inline confirmation** (01·12) |
| Status text after an action | **Success line** (01·13) · link with a chevron → **Learn more arrow** (01·14) · async submit → **Button loading** (01·15) |
| Trigger + surface that grows from it | **Dropdown / popover** (02·1); fold variant **Reveal** (02·1) |
| Hover/focus hint over a trigger | **Tooltip** (02·2) |
| Surface on top of the page, not anchored | **Modal** (02·3) |
| Surface from a screen edge, draggable | **Drawer / sheet** (02·4) |
| Surface sliding into a region | **Panel reveal** (02·5) |
| Round trigger becomes the panel | **Plus → menu morph** (02·6); liquid split → **Gooey menu** (02·7) |
| Header + collapsible body | **Accordion** (02·8) |
| Container changes its own size | **Card resize** (02·9) |
| ⌘K / keyboard-opened surface | **No animation** (02·10) |
| Transient confirmation | **Toast** (03·1); several at once → **Toast stack** (03·2); top banners → (03·4) |
| Dot on a bell | **Notification badge** (03·3) |
| Mutually exclusive options with a moving highlight | **Tabs sliding pill** (04·1); colour must stay in sync → **Clip-path tabs** (04·2) |
| List ↔ detail, wizard steps | **Page side-by-side** (04·3); router → View Transitions (04·7) |
| Horizontal pages | **Paged carousel** (04·4) · scrolling rows → **Edge fade** (04·5) · centred choice → **Wheel picker** (04·6) |
| Rows of data that reorder, arrive or leave | **Data table** (10·1) — FLIP so rows travel, never blink |
| A row with more inside it | **Expandable table row** (10·2) |
| A heading that should reveal a search or filter | **Expanding title with search** (10·3) |
| Text changes in place | **Text swap** (05·1) · icon in one slot → **Icon swap** (05·2) |
| A number updates | quiet/frequent → **Rolling number** (05·4) · occasional → **Number pop-in** (05·3) · jackpot → **Spinning counter** (05·5) |
| Control / label appears inside a row | **Element / unfold / side folds** (05·6) |
| Placeholder becomes content | **Skeleton reveal** (05·7) · AI image → **Image-gen placeholder** (05·8) |
| Model output arriving | **Streaming text** (05·9) · status line while working → **Thinking states** (05·10) · scrolling transcript → **Reasoning stream** (05·11) |
| "Generating…" label | **Shimmer text** (06·1) · surface → **Skeleton shimmer** (06·2) · premium tile → **Organic shimmer** (06·3) |
| A loader that whispers | **Matrix dot loader** (06·4) · **Spinner** (06·5) · **Progress** (06·6) · mobile → **Pull to refresh** (06·7) |
| Hero copy entering | **Texts reveal** (07·1) · a list that is a moment → **Stagger** (07·2) · marketing sections → **Scroll reveal** (07·3) · images → **Clip-path reveal** (07·4) |
| Avatar / chip row hover | **Avatar group hover** (07·5) · stacked thumbnails → **Card stack hover** (07·6) |
| A crossfade that won't settle | **Blur bridge** (07·7) · card back side → **3D flip** (07·8) |
| Swipe a toast/card away | **Drag to dismiss** (08·1) · list row actions → **Swipe actions** (08·2) |
| Move a thing into a target with weight | **Drag & drop physics** (08·3) |
| Card reacting to the pointer in 3D | **Card tilt** (08·4) · preview zooming open → **Image open tilt** (08·5) · pointer-follow decoration → (08·7) |
| Celebration | **Confetti** (09·1) · delightful delete → **Smoky dissolve** (09·2) |
| One premium word / CTA | **Gradient text** (09·3) · **Rim-glow button** (09·4) |
| Theme switch | **Dark-mode toggle** (09·5) · e-commerce add → **Add to cart** (09·6) · dashboard → **Chart bars hover** (09·7) |

Tie-breakers: prefer the lower-overhead surface (card resize over panel reveal, dropdown over modal, success check over a modal celebration) unless the design clearly needs the heavier one. Success check is appear-only; pair with icon swap to replace a spinner. If nothing matches, list the catalog and let the user pick — do not guess.

## Files

| File | Contents |
| --- | --- |
| `01-feedback-controls.md` | press, press bounce, hover fill/grow/lift, like, checkbox, toggle, selected pill, success check, spinner→check morph, error shake, hold to confirm, inline confirmation, success line, learn-more arrow, button loading, focus ring |
| `02-surfaces.md` | dropdown/popover (+ fold reveal), tooltip, modal, drawer/sheet with drag & snap, panel reveal, plus→menu morph, gooey menu, accordion, card resize, command palette (none) |
| `03-notifications.md` | toast (two personalities, `@starting-style`), toast stack, notification badge, banner |
| `04-navigation.md` | tabs pill, clip-path tabs, page side-by-side, paged carousel, edge fade, wheel picker, shared element / FLIP |
| `05-content-swap.md` | text swap, icon swap, number pop-in, rolling number, spinning counter, element/unfold/side folds, skeleton reveal, image-gen placeholder, streaming text, thinking states, reasoning stream |
| `10-data-tables.md` | data table sort/insert/remove via FLIP, expandable table row, expanding title with a search field |
| `06-loading.md` | shimmer text, skeleton shimmer, organic shimmer, matrix loader, spinner, progress + steps, pull to refresh |
| `07-reveal-stagger.md` | texts reveal, stagger, scroll reveal, clip-path reveal, avatar group hover, card stack hover, blur bridge, 3D flip |
| `08-gestures.md` | drag to dismiss, swipe actions, drag & drop physics, card tilt, image open tilt, pointer-follow |
| `09-celebration-brand.md` | confetti, smoky dissolve, gradient text, rim-glow button, dark-mode toggle, add to cart, chart bars |

## Installing a recipe into a project

1. Install `assets/motion-tokens.css` (+ `motion-springs.css` if springs are used) once, before the recipe. If the project already has motion tokens, map by usage instead of adding a second scale.
2. Paste the recipe's CSS verbatim: keep the exact property list, the `will-change`, and the reduced-motion block.
3. Wire the documented hooks (`data-open`, `data-state`, `aria-*`, `.is-*`) from whatever already drives state.
4. Copy the JS orchestration when the recipe has one; keep the token reads so timing stays in sync with the CSS.
5. Keep the diff small: only the files needed; no renaming of the project's variables; no motion library for a fade.
