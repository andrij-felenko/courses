# -*- coding: utf-8 -*-
"""svgcheck — швидка геометрична перевірка згенерованих SVG.
Замінює LLM-переогляд кожного файлу: textbox()/fitbox() зі svgkit уже гарантують,
що текст не вилазить за РАМКУ; цей скрипт ловить інше — елементи поза viewBox
(хибні координати) і нечитабельно дрібний шрифт.

    python svgcheck.py <тека> [--min-font 9] [--tol 6]

Код виходу 0 — чисто; 1 — є зауваження (друкує стислий звіт, по 1 прикладу на тип).
"""
import sys, os, re, glob


def check_svg(path, min_font=9, tol=6.0):
    issues = []
    try:
        s = open(path, encoding="utf-8").read()
    except Exception as e:
        return ["не прочитати: %s" % e]

    m = re.search(r'viewBox="([^"]+)"', s)
    if not m:
        return ["немає viewBox"]
    vb = re.split(r"[ ,]+", m.group(1).strip())
    if len(vb) < 4:
        return ["дивний viewBox: %s" % m.group(1)]
    try:
        x0, y0, W, H = (float(vb[0]), float(vb[1]), float(vb[2]), float(vb[3]))
    except ValueError:
        return ["дивний viewBox: %s" % m.group(1)]
    xmax, ymax = x0 + W, y0 + H

    # координати-атрибути поза межами полотна
    axes = [("x", x0, xmax), ("cx", x0, xmax), ("x1", x0, xmax), ("x2", x0, xmax),
            ("y", y0, ymax), ("cy", y0, ymax), ("y1", y0, ymax), ("y2", y0, ymax)]
    for attr, lo, hi in axes:
        for val in re.findall(r'\b%s="(-?[\d.]+)"' % attr, s):
            try:
                v = float(val)
            except ValueError:
                continue
            if v < lo - tol or v > hi + tol:
                issues.append("%s=%.0f поза [%.0f..%.0f]" % (attr, v, lo, hi))
                break  # одного прикладу на атрибут досить

    # rect, що вилазить правим/нижнім краєм
    for rm in re.finditer(r'<rect x="(-?[\d.]+)" y="(-?[\d.]+)" width="([\d.]+)" height="([\d.]+)"', s):
        rx, ry, rw, rh = map(float, rm.groups())
        if rx + rw > xmax + tol or ry + rh > ymax + tol:
            issues.append("rect виходить за межі (правий/нижній край %.0f×%.0f у %.0f×%.0f)"
                          % (rx + rw, ry + rh, xmax, ymax))
            break

    # нечитабельно дрібний шрифт
    for fs in re.findall(r'font-size="(\d+)"', s):
        if int(fs) < min_font:
            issues.append("шрифт %spx < %d" % (fs, min_font))
            break

    return issues


def main():
    for stream in (sys.stdout, sys.stderr):           # звіт містить кирилицю — не залежати від кодування консолі
        try:
            stream.reconfigure(encoding="utf-8")
        except Exception:
            pass
    pos = [a for a in sys.argv[1:] if not a.startswith("--")]
    d = pos[0] if pos else "."
    min_font, tol = 9, 6.0
    if "--min-font" in sys.argv:
        min_font = int(sys.argv[sys.argv.index("--min-font") + 1])
    if "--tol" in sys.argv:
        tol = float(sys.argv[sys.argv.index("--tol") + 1])

    if os.path.isfile(d):
        files = [d]
    else:
        files = sorted(glob.glob(os.path.join(d, "**", "*.svg"), recursive=True))

    bad = 0
    for f in files:
        iss = check_svg(f, min_font, tol)
        if iss:
            bad += 1
            try:
                rel = os.path.relpath(f, d)
            except ValueError:
                rel = f
            print("WARN %s: %s" % (rel, "; ".join(iss[:4])))
    print("SVG перевірено: %d; із зауваженнями: %d" % (len(files), bad))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
