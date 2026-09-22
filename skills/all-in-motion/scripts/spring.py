#!/usr/bin/env python3
"""Spring calculator and token generator for all-in-motion.

Usage:
    spring.py RESPONSE DAMPING [--scale 1.18] [--stops 40]
        Print stiffness, damping, bounce, settle time, overshoot and a CSS
        linear() easing for one spring (SwiftUI-style response + dampingFraction).

    spring.py --tokens
        Regenerate assets/motion-springs.css, assets/motion-springs.json and
        the preset block inside assets/motion.ts from the PRESETS table below.

A spring here is SwiftUI's `.spring(response:dampingFraction:)` with mass 1:
    stiffness = (2*pi/response)^2
    damping   = 4*pi*zeta/response

The twenty presets are measured from a production macOS app's motion system and
renamed for the web. Prefer a preset; derive a new spring only when no intent fits.
"""
import json
import math
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

EASE = {
    "easeIn": [0.42, 0.0, 1.0, 1.0],
    "easeOut": [0.0, 0.0, 0.58, 1.0],
    "easeInOut": [0.42, 0.0, 0.58, 1.0],
}

# name: (kind, response|curve, dampingFraction|seconds, reducedMotion, use)
PRESETS = {
    "hover":          ("spring", 0.40, 0.85, ("ease", "easeOut", 0.14), "every hover change on buttons, links, cards, rows"),
    "hoverQuick":     ("ease", "easeOut", 0.10, None, "instant hover on small icons; a button's pressed colour"),
    "hoverScale":     ("spring", 0.36, 0.90, ("ease", "easeOut", 0.12), "grow on hover: a badge or pill that is a button"),
    "cardHover":      ("spring", 0.24, 0.80, None, "small lift or scale of a card under the pointer"),
    "state":          ("spring", 0.27, 1.00, None, "the default: toggles, selection, filters, list changes, content swaps"),
    "segmented":      ("spring", 0.22, 0.90, ("ease", "easeOut", 0.16), "segmented controls, chips, option tiles, pickers"),
    "emphasis":       ("spring", 0.28, 0.72, ("ease", "easeOut", 0.20), "important toggles, favourites, snapping onto a choice"),
    "bounce":         ("spring", 0.18, 0.56, ("ease", "easeOut", 0.20), "playful success: an icon or button that confirms a click"),
    "press":          ("spring", 0.14, 0.82, None, "pointer down on a control (follows the input)"),
    "release":        ("spring", 0.24, 0.74, None, "pointer up, the control springing back"),
    "drag":           ("spring", 0.10, 0.90, None, "dragged element following the pointer"),
    "pressSnap":      ("spring", 0.18, 0.62, None, "two-phase press, phase 1: snap on pointer down"),
    "pressSettle":    ("spring", 0.24, 0.78, None, "two-phase press, phase 2: settle on pointer up"),
    "surfacePress":   ("spring", 0.24, 0.82, ("ease", "easeOut", 0.16), "a large surface (hero card, tile) growing under a held press"),
    "surfaceRelease": ("spring", 0.34, 0.68, ("ease", "easeOut", 0.18), "the same surface relaxing back"),
    "open":           ("spring", 0.47, 0.76, ("spring", 0.30, 1.00), "anything opening or entering: modal, popover, dropdown, toast, drawer"),
    "close":          ("spring", 0.54, 0.90, ("spring", 0.30, 1.00), "anything closing: the same surfaces leave without bounce"),
    "morph":          ("spring", 0.42, 0.90, ("ease", "easeOut", 0.18), "a control changing width or shape in place (search expanding)"),
    "panelSlide":     ("spring", 0.32, 0.90, ("ease", "easeOut", 0.18), "a sidebar or inner panel sliding"),
    "tabSelect":      ("spring", 0.34, 0.82, ("ease", "easeOut", 0.16), "a tab or segment indicator sliding under the choice"),
}


def spring_terms(response, zeta):
    omega = 2 * math.pi / response
    return omega * omega, 4 * math.pi * zeta / response


def position(t, response, zeta):
    omega = 2 * math.pi / response
    if zeta < 1:
        wd = omega * math.sqrt(1 - zeta * zeta)
        return 1 - math.exp(-zeta * omega * t) * (math.cos(wd * t) + (zeta * omega / wd) * math.sin(wd * t))
    if zeta == 1:
        return 1 - math.exp(-omega * t) * (1 + omega * t)
    r1 = -omega * (zeta - math.sqrt(zeta * zeta - 1))
    r2 = -omega * (zeta + math.sqrt(zeta * zeta - 1))
    c2 = r1 / (r2 - r1)
    c1 = -1 - c2
    return 1 + c1 * math.exp(r1 * t) + c2 * math.exp(r2 * t)


def settle_time(response, zeta, tolerance=0.001):
    step = 0.001
    t = step
    last_outside = 0.0
    while t < 10 * response + 2:
        if abs(1 - position(t, response, zeta)) > tolerance:
            last_outside = t
        t += step
    return round(last_outside + step, 3)


def css_linear(response, zeta, stops=40):
    duration = settle_time(response, zeta)
    points = []
    for i in range(stops + 1):
        t = duration * i / stops
        value = 1.0 if i == stops else position(t, response, zeta)
        if value == 0:
            points.append("0")
        elif value == 1:
            points.append("1")
        else:
            points.append(f"{value:.4f}".rstrip("0").rstrip("."))
    return duration, "linear(" + ", ".join(points) + ")"


def overshoot(response, zeta):
    if zeta >= 1:
        return 0.0
    duration = settle_time(response, zeta)
    peak = max(position(duration * i / 400, response, zeta) for i in range(401))
    return round(max(0.0, peak - 1), 4)


def describe(response, zeta, scale=1.0, stops=40):
    response *= scale
    stiffness, damping = spring_terms(response, zeta)
    duration, linear = css_linear(response, zeta, stops)
    bounce = round(1 - zeta, 3) if zeta <= 1 else round(1 - 1 / zeta, 3)
    return {
        "response": round(response, 4),
        "dampingFraction": zeta,
        "stiffness": round(stiffness, 3),
        "damping": round(damping, 3),
        "mass": 1,
        "bounce": bounce,
        "settleSeconds": duration,
        "overshoot": overshoot(response, zeta),
        "cssLinear": linear,
    }


def ease_entry(curve, seconds, scale=1.0):
    return {"curve": curve, "cubicBezier": EASE[curve], "seconds": round(seconds * scale, 4)}


def tokens():
    data = {
        "source": "all-in-motion — spring presets measured from a production macOS motion system, renamed for the web",
        "note": "Base values for 100 Hz displays and up. Multiply by 1.1 on 75-99 Hz and 1.18 on 60 Hz if a page must feel identical to a native app there; otherwise leave them.",
        "presets": {},
    }
    for name, (kind, a, b, reduced, use) in PRESETS.items():
        entry = {"use": use}
        if kind == "spring":
            entry["spring"] = describe(a, b)
        else:
            entry["ease"] = ease_entry(a, b)
        if reduced:
            if reduced[0] == "ease":
                entry["reducedMotion"] = {"ease": ease_entry(reduced[1], reduced[2])}
            else:
                entry["reducedMotion"] = {"spring": describe(reduced[1], reduced[2])}
        else:
            entry["reducedMotion"] = "unchanged"
        data["presets"][name] = entry
    return data


def kebab(name):
    return "".join("-" + c.lower() if c.isupper() else c for c in name)


def css(data):
    lines = [
        "/* all-in-motion spring tokens. Generated by scripts/spring.py --tokens — do not edit by hand.",
        "   Each preset ships as --spring-<name>-duration + --spring-<name>-easing (a CSS linear() curve).",
        "   Use: transition: transform var(--spring-open-duration) var(--spring-open-easing);",
        "   Reduced motion is handled below: bouncy presets collapse to short ease-outs. */",
        ":root {",
    ]
    for name, entry in data["presets"].items():
        key = kebab(name)
        if "spring" in entry:
            s = entry["spring"]
            lines.append(f"  --spring-{key}-duration: {round(s['settleSeconds'] * 1000)}ms;")
            lines.append(f"  --spring-{key}-easing: {s['cssLinear']};")
        else:
            e = entry["ease"]
            lines.append(f"  --spring-{key}-duration: {round(e['seconds'] * 1000)}ms;")
            lines.append(f"  --spring-{key}-easing: cubic-bezier({', '.join(str(v) for v in e['cubicBezier'])});")
    lines.append("}")
    lines.append("")
    lines.append("@media (prefers-reduced-motion: reduce) {")
    lines.append("  :root {")
    for name, entry in data["presets"].items():
        reduced = entry["reducedMotion"]
        if reduced == "unchanged":
            continue
        key = kebab(name)
        if "ease" in reduced:
            e = reduced["ease"]
            lines.append(f"    --spring-{key}-duration: {round(e['seconds'] * 1000)}ms;")
            lines.append(f"    --spring-{key}-easing: cubic-bezier({', '.join(str(v) for v in e['cubicBezier'])});")
        else:
            s = reduced["spring"]
            lines.append(f"    --spring-{key}-duration: {round(s['settleSeconds'] * 1000)}ms;")
            lines.append(f"    --spring-{key}-easing: {s['cssLinear']};")
    lines.append("  }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def main(argv):
    if argv and argv[0] == "--tokens":
        data = tokens()
        (ROOT / "assets" / "motion-springs.json").write_text(json.dumps(data, indent=2) + "\n")
        (ROOT / "assets" / "motion-springs.css").write_text(css(data))
        ts_path = ROOT / "assets" / "motion.ts"
        if ts_path.exists():
            src = ts_path.read_text()
            start = src.index("export const springPresets = ")
            end = src.index(" as const;", start)
            src = src[:start] + "export const springPresets = " + json.dumps(data["presets"], indent=2) + src[end:]
            ts_path.write_text(src)
        print("wrote assets/motion-springs.json, assets/motion-springs.css and refreshed assets/motion.ts")
        return
    if len(argv) < 2:
        print(__doc__)
        sys.exit(1)
    response, zeta = float(argv[0]), float(argv[1])
    scale = float(argv[argv.index("--scale") + 1]) if "--scale" in argv else 1.0
    stops = int(argv[argv.index("--stops") + 1]) if "--stops" in argv else 40
    print(json.dumps(describe(response, zeta, scale, stops), indent=2))


if __name__ == "__main__":
    main(sys.argv[1:])
