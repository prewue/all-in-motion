#!/usr/bin/env python3
"""Static motion scanner for all-in-motion.

Greps a project for the motion red flags the review workflow blocks on and
prints them grouped by file with a suggested fix. It is a first pass, not a
verdict: every hit still needs a human (or the agent) to judge intent.

Usage:
    scan.py [PATH ...] [--json]

Scans .css .scss .less .html .vue .svelte .js .jsx .ts .tsx .mdx files.
Skips node_modules, dist, build, .git, .next, coverage, vendor.
"""
from __future__ import annotations

import json
import os
import re
import sys

EXTS = {".css", ".scss", ".less", ".md", ".html", ".vue", ".svelte", ".js", ".jsx", ".ts", ".tsx", ".mdx"}
SKIP_DIRS = {"node_modules", "dist", "build", ".git", ".next", "coverage", "vendor", "out", ".turbo", ".cache"}

# (id, severity, regex, message, fix)
RULES = [
    ("transition-all", "block", re.compile(r"transition\s*:\s*all\b|transition-property\s*:\s*all\b|\btransition-all\b"),
     "`transition: all` animates every changed property, including layout ones",
     "Name the exact properties: transition: transform 200ms var(--ease-out), opacity 200ms var(--ease-out)"),
    # `(?<![-\w])` keeps custom properties such as --motion-blur-scale: 0 out of this rule.
    ("scale-zero", "block", re.compile(r"scale\(\s*0\s*\)|(?<![-\w])scale\s*:\s*0\b(?![.\d])|\bscale-0\b"),
     "Entrance from scale(0): nothing in the real world appears from nothing",
     "Start from scale(0.95) + opacity: 0 (0.9–0.97 range)"),
    # Not preceded by a quote: `"ease-in": [0.42, 0, 1, 1]` is a curve lookup table,
    # not a transition. `(?![\w-])` already excludes ease-in-out.
    ("ease-in-ui", "block", re.compile(r"""(?<![\w"'-])ease-in(?![\w-])"""),
     "`ease-in` on a UI transition delays the moment the user is watching",
     "Use ease-out (var(--ease-out)) for enters/exits; ease-in is only for a pure exit fade"),
    ("layout-prop", "block", re.compile(r"transition\s*:[^;]*\b(width|height|top|left|right|bottom|margin[\w-]*|padding[\w-]*)\b(?!-)|animate=\{\{[^}]*\b(width|height|top|left|margin|padding)\s*:"),
     "Animating a layout property triggers layout + paint every frame",
     "Use transform/opacity (translate, scale) or clip-path; height only for accordions via grid-template-rows 0fr↔1fr"),
    ("keyframes-toast", "warn", re.compile(r"\.(toast|toggle|switch|snackbar)[^{]*\{[^}]*animation\s*:", re.S),
     "Keyframes on a rapidly re-triggered element restart from zero and cannot retarget",
     "Use a state-driven CSS transition (or @starting-style) so a second trigger blends instead of jumping"),
    ("motion-shorthand", "warn", re.compile(r"animate=\{\{\s*[^}]*\b(x|y|scale)\s*:"),
     "Motion x/y/scale shorthands run on the main thread and drop frames under load",
     "Use the full transform string: animate={{ transform: 'translateX(100px)' }} for motion that runs while the page is busy"),
    ("css-var-drag", "warn", re.compile(r"setProperty\(\s*['\"]--(drag|swipe|x|y|pos)[\w-]*['\"]"),
     "Driving a transform through a CSS variable on a parent recalculates styles for every child",
     "Set element.style.transform directly on the moving element"),
    ("will-change-global", "warn", re.compile(r"(\*|html|body)\s*\{[^}]*will-change", re.S),
     "Global will-change allocates a compositor layer for everything",
     "Scope will-change to the element and the gesture (data-[dragging] / .is-animating)"),
    ("pulse-loop", "warn", re.compile(r"@keyframes\s+[\w-]*(pulse|glow|breathe|throb)[\w-]*|\banimate-pulse\b|\banimate-ping\b"),
     "Looping attention pulse on a status element: the AI-slop tell",
     "Static treatment; a single brand element may keep one with stated rationale"),
    ("infinite-small", "info", re.compile(r"animation\s*:[^;]*\binfinite\b"),
     "Infinite animation: confirm it is a loader/shimmer with a purpose and a pause path",
     "Loaders and shimmers are fine; decorative infinite loops on UI chrome are not"),
    ("slow-ui", "warn", re.compile(r"(transition|animation)[^;{]*\b(4[0-9]{2}|[5-9][0-9]{2}|[1-9]\d{3})ms\b|(transition|animation)[^;{]*\b0?\.([4-9]\d*|[1-9]\d+)s\b|\bduration-(4[0-9]{2}|[5-9]\d{2}|\d{4})\b"),
     "UI duration over 300ms needs a reason (drawer/sheet 500ms, marketing, panel open 400ms are the known exceptions)",
     "Bring it to 150–250ms unless the element is a large surface or a one-time moment"),
    ("hover-ungated", "info", re.compile(r":hover\s*\{[^}]*(transform|translate|scale|rotate)\s*:", re.S),
     "Hover motion outside @media (hover: hover) fires on tap on touch devices",
     "Wrap hover transforms in @media (hover: hover) and (pointer: fine)"),
    ("nuclear-reduce", "warn", re.compile(r"prefers-reduced-motion[^{]*\{\s*\*[^}]*(0\.01ms|0s|none)\s*!important", re.S),
     "Nuclear reduced-motion kills loaders and state feedback too",
     "Prefer per-component fallbacks: keep opacity/colour, drop movement; keep spinners as a gentle pulse"),
    ("origin-center-popover", "info", re.compile(r"\.(dropdown|popover|menu|tooltip)[^{]*\{[^}]*transform-origin\s*:\s*center", re.S),
     "Trigger-anchored surface scaling from center instead of its trigger",
     "transform-origin: top left/center (or the library's --transform-origin); modals are exempt"),
]

REDUCED_RE = re.compile(r"prefers-reduced-motion|useReducedMotion|motion-safe:|motion-reduce:")
MOTION_RE = re.compile(r"@keyframes|transition\s*:|animation\s*:|<motion\.|animate=\{|\.animate\(|useSpring|gsap\.")


def iter_files(paths):
    for root in paths:
        if os.path.isfile(root):
            yield root
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
            for f in filenames:
                if os.path.splitext(f)[1] in EXTS:
                    yield os.path.join(dirpath, f)


def line_of(text, idx):
    return text.count("\n", 0, idx) + 1


def blank(text, start, end):
    """Replace a span with same-length whitespace so line numbers stay correct."""
    return text[:start] + "".join(c if c == "\n" else " " for c in text[start:end]) + text[end:]


def mask_noise(text, ext):
    """
    Blank out everything that is prose or commentary, so the rules only ever see code.
    Line numbers are preserved. Without this the scanner flags the word "ease-in" in a
    sentence, or a `scale: 0` in a comment explaining why not to do it.
    """
    # comments: /* ... */, // ... , <!-- ... -->
    for rx in (re.compile(r"/\*.*?\*/", re.S), re.compile(r"<!--.*?-->", re.S)):
        while True:
            m = rx.search(text)
            if not m:
                break
            text = blank(text, m.start(), m.end())
    for m in reversed(list(re.finditer(r"(?<!:)//[^\n]*", text))):
        text = blank(text, m.start(), m.end())

    if ext in {".html", ".vue", ".svelte", ".mdx"}:
        # keep only <style>, <script> and inline style="" / class-bearing attributes
        keep = []
        for rx in (re.compile(r"<style[^>]*>(.*?)</style>", re.S),
                   re.compile(r"<script[^>]*>(.*?)</script>", re.S),
                   re.compile(r'\bstyle="([^"]*)"')):
            keep.extend((m.start(1), m.end(1)) for m in rx.finditer(text))
        kept = "".join(c if c == "\n" else " " for c in text)
        kept = list(kept)
        for s, e in keep:
            kept[s:e] = list(text[s:e])
        text = "".join(kept)

    if ext == ".md":
        # only fenced code blocks are code; the prose around them is documentation
        kept = list("".join(c if c == "\n" else " " for c in text))
        for m in re.finditer(r"```[a-z]*\n(.*?)```", text, re.S):
            kept[m.start(1):m.end(1)] = list(text[m.start(1):m.end(1)])
        text = "".join(kept)
    return text


# An intentional, reviewed exception is marked with `motion-ok` on the same line
# or the line above (e.g. `transition: width 300ms; /* motion-ok: small card resize */`).
OK_RE = re.compile(r"motion-ok")


def suppressed(raw_lines, line):
    """
    True when the matched line, or the line directly above it, carries the pragma.
    `line` is 1-indexed and raw_lines is 0-indexed, so the match itself is
    raw_lines[line - 1]. The window is deliberately narrow: a wider one would let
    one pragma silently cover the declarations after it.
    """
    for n in (line - 1, line - 2):
        if 0 <= n < len(raw_lines) and OK_RE.search(raw_lines[n]):
            return True
    return False


def scan_file(path):
    try:
        raw = open(path, encoding="utf-8", errors="ignore").read()
    except OSError:
        return []
    ext = os.path.splitext(path)[1]
    text = mask_noise(raw, ext)
    raw_lines = raw.split("\n")
    findings = []
    for rule_id, sev, rx, msg, fix in RULES:
        for m in rx.finditer(text):
            line = line_of(text, m.start())
            if suppressed(raw_lines, line):
                continue
            snippet = raw[m.start():m.start() + 80].split("\n")[0].strip()
            findings.append({"file": path, "line": line, "rule": rule_id, "severity": sev, "message": msg, "fix": fix, "snippet": snippet})
    if MOTION_RE.search(text) and not REDUCED_RE.search(raw) and os.path.splitext(path)[1] in {".css", ".scss", ".less", ".vue", ".svelte"}:
        findings.append({"file": path, "line": 1, "rule": "no-reduced-motion", "severity": "block",
                         "message": "File animates but never mentions prefers-reduced-motion",
                         "fix": "Add a gentler variant under @media (prefers-reduced-motion: reduce) — fewer, not zero", "snippet": ""})
    return findings


def main(argv):
    as_json = "--json" in argv
    paths = [a for a in argv if not a.startswith("--")] or ["."]
    all_findings = []
    for f in iter_files(paths):
        all_findings.extend(scan_file(f))
    order = {"block": 0, "warn": 1, "info": 2}
    all_findings.sort(key=lambda x: (order[x["severity"]], x["file"], x["line"]))
    if as_json:
        print(json.dumps(all_findings, indent=2))
        return
    if not all_findings:
        print("No motion red flags found.")
        return
    counts = {k: sum(1 for x in all_findings if x["severity"] == k) for k in order}
    print(f"Motion scan: {counts['block']} block · {counts['warn']} warn · {counts['info']} info\n")
    current = None
    for x in all_findings:
        if x["file"] != current:
            current = x["file"]
            print(current)
        tag = {"block": "✗", "warn": "!", "info": "·"}[x["severity"]]
        print(f"  {tag} L{x['line']:<5} [{x['rule']}] {x['message']}")
        if x["snippet"]:
            print(f"           {x['snippet']}")
        print(f"           → {x['fix']}")
    print("\nEach hit is a question, not a verdict — check intent, frequency tier and context before changing anything.")


if __name__ == "__main__":
    main(sys.argv[1:])
