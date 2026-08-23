# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODEBG = "#0f1b14"
CODE_HAL = "#9ec5ff"   # HAL — блакитний
CODE_LL  = "#ffd27f"   # LL — бурштиновий
CODE_REG = "#7fe0a0"   # голі регістри — зелений


def codeline(cx, cy, code, accent, w=320, h=40):
    out = rect(cx - w / 2, cy - h / 2, w, h, fill=CODEBG, stroke="#0a120d", sw=1.4, rx=8)
    out += ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
            'font-size="12.5" fill="%s" text-anchor="middle" font-weight="700">%s</text>'
            % (cx, cy + 5, accent, esc(code)))
    return out


# ── 1. three-layers: стек STM32Cube над регістрами ───────────────────────────
def fig_three_layers():
    W, H = 760, 400
    p = []
    cx = W / 2
    layers = [
        ("ваш код", "застосунок прошивки", "#eafaf0", INK, None),
        ("HAL", "високорівневі функції, переносність", "#eef3ff", NEG, CODE_HAL),
        ("LL", "тонкі обгортки 1-до-1 над бітами регістрів", "#fff4e0", "#b8860b", CODE_LL),
        ("CMSIS-регістри", "RCC->, GPIOA-> : структури = адреси заліза", "#eafaf0", FIELD, CODE_REG),
        ("залізо", "кремній: тригери, ніжки, тактові домени", "#efefef", MUTED, None),
    ]
    bw, bh = 470, 50
    y = 64
    gap = 16
    bottoms = []
    for name, sub, fill, col, _ in layers:
        b = rect(cx - bw / 2, y, bw, bh, fill=fill, stroke=INK, sw=1.6, rx=8)
        b += text(cx - bw / 2 + 14, y + bh / 2 + 5, name, size=13, color=col, anchor="start", bold=True)
        b += ('<text x="%.1f" y="%.1f" font-family="%s" font-size="10.5" '
              'fill="%s" text-anchor="end">%s</text>' % (cx + bw / 2 - 14, y + bh / 2 + 4, FONT, MUTED, esc(sub)))
        p.append(b)
        bottoms.append(y + bh)
        y += bh + gap
    for i in range(len(layers) - 1):
        p.append(arrow(cx, bottoms[i] + 1, cx, bottoms[i] + gap - 1, color=INK, sw=1.7))
    # підпис праворуч: усі три верхні шари зрештою пишуть у ті самі регістри
    p.append(text(cx + bw / 2 + 16, bottoms[2] + gap / 2,
                  "усі три шляхи\nзводяться донизу —\nдо тих самих бітів", size=10, color=POS, anchor="start"))
    render(os.path.join(OUT, "three-layers.svg"), W, H, *p,
           title="Стек STM32Cube: HAL і LL стоять на CMSIS-регістрах")


# ── 2. same-blink: та сама дія трьома мовами ─────────────────────────────────
def fig_same_blink():
    W, H = 780, 320
    p = []
    cols = [
        ("HAL", NEG, CODE_HAL, "#eef3ff",
         "HAL_GPIO_WritePin(\nGPIOA, GPIO_PIN_5,\nGPIO_PIN_SET);",
         "найясніше, переносно"),
        ("LL", "#b8860b", CODE_LL, "#fff4e0",
         "LL_GPIO_SetOutputPin(\nGPIOA,\nLL_GPIO_PIN_5);",
         "тонко, швидко"),
        ("регістри", FIELD, CODE_REG, "#eafaf0",
         "GPIOA->BSRR =\n(1 << 5);",
         "гола правда заліза"),
    ]
    cw = 240
    gap = 18
    total = len(cols) * cw + (len(cols) - 1) * gap
    x = (W - total) / 2 + cw / 2
    for name, col, acc, fill, code, note in cols:
        p.append(text(x, 64, name, size=15, color=col, bold=True))
        lines = code.split("\n")
        bh = 26 + len(lines) * 20
        by = 86
        p.append(rect(x - cw / 2 + 6, by, cw - 12, bh, fill=CODEBG, stroke="#0a120d", sw=1.4, rx=8))
        ty = by + 24
        for ln in lines:
            p.append('<text x="%.1f" y="%.1f" font-family="Consolas, monospace" font-size="12.5" '
                     'fill="%s" text-anchor="middle">%s</text>' % (x, ty, acc, esc(ln)))
            ty += 20
        p.append(text(x, by + bh + 22, note, size=11, color=col, italic=True))
        x += cw + gap
    p.append(mtext(W / 2, H - 30,
                   "одна дія — «підняти ніжку PA5» — три записи; усі три зрештою\nставлять той самий біт у тому самому регістрі BSRR",
                   size=11, color=MUTED))
    render(os.path.join(OUT, "same-blink.svg"), W, H, *p,
           title="Та сама дія трьома мовами: HAL, LL, голий регістр")


# ── 3. cost-bars: ціна кожного шару за трьома осями ──────────────────────────
def fig_cost_bars():
    W, H = 780, 340
    p = []
    # три групи стовпчиків: розмір коду, такти на дію, зусилля написання
    groups = ["розмір коду", "тактів на дію", "зусилля написати"]
    # значення 0..1 (на око, відносно), HAL/LL/REG
    data = {
        "розмір коду":      [1.0, 0.32, 0.28],
        "тактів на дію":    [1.0, 0.30, 0.22],
        "зусилля написати": [0.30, 0.62, 1.0],   # тут навпаки: регістри писати найважче
    }
    names = ["HAL", "LL", "регістр"]
    cols = [NEG, "#b8860b", FIELD]
    fills = ["#eef3ff", "#fff4e0", "#eafaf0"]
    base = 250
    gx0 = 110
    gw = 200          # ширина групи
    bw = 44           # ширина стовпчика
    barmax = 150
    for gi, g in enumerate(groups):
        gx = gx0 + gi * gw
        p.append(text(gx + gw / 2 - 30, base + 28, g, size=11, color=INK))
        for bi in range(3):
            v = data[g][bi]
            h = max(barmax * v, 6)
            x = gx + bi * (bw + 8)
            p.append(rect(x, base - h, bw, h, fill=fills[bi], stroke=cols[bi], sw=1.6, rx=4))
        # роздільна риска групи
    # легенда
    lx = W - 150
    for i, n in enumerate(names):
        ly = 80 + i * 26
        p.append(rect(lx, ly - 12, 16, 16, fill=fills[i], stroke=cols[i], sw=1.6, rx=3))
        p.append(text(lx + 24, ly + 1, n, size=12, color=cols[i], anchor="start", bold=True))
    p.append(line(gx0 - 14, base, W - 170, base, color=INK, sw=1.5))
    p.append(mtext(W / 2, H - 28,
                   "HAL найбільший і найповільніший, зате писати найлегше; голі регістри\nнайменші й найшвидші, зате найдорожчі в написанні; LL — посередині",
                   size=11, color=MUTED))
    render(os.path.join(OUT, "cost-bars.svg"), W, H, *p,
           title="Ціна кожного шару: розмір, такти, зусилля")


# ── 4. when-which: коли який шар ──────────────────────────────────────────────
def fig_when_which():
    W, H = 780, 300
    p = []
    rows = [
        ("HAL", NEG, "#eef3ff",
         "за замовчуванням · ініціалізація · USB/Ethernet/SD · переносність між родинами"),
        ("LL", "#b8860b", "#fff4e0",
         "гаряча перерва · щільний цикл · обмежена Flash · потрібен тонкий контроль"),
        ("голі регістри", FIELD, "#eafaf0",
         "максимум швидкості · біт, якого немає в LL · вчуся / відлагоджую правду заліза"),
    ]
    y = 78
    bw, bh = 640, 56
    x = (W - bw) / 2
    for name, col, fill, desc in rows:
        p.append(rect(x, y, bw, bh, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(x + 16, y + bh / 2 + 5, name, size=14, color=col, anchor="start", bold=True))
        p.append(fitbox(x + 150, y + 8, bw - 166, bh - 16, desc, size=11,
                        fill=fill, stroke=fill, sw=0, color=INK))
        y += bh + 16
    p.append(text(W / 2, H - 22,
                  "і це не «або-або»: HAL для каркаса, LL/регістри — точково в гарячих місцях",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "when-which.svg"), W, H, *p,
           title="Коли який шар: HAL за замовчуванням, нижче — за потребою")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури для вставки hist-stm32-libs.md (історія бібліотек STM32)
# ════════════════════════════════════════════════════════════════════════════

# ── H1. libs-timeline: двадцять років в одній смузі ──────────────────────────
def fig_libs_timeline():
    W, H = 820, 320
    p = []
    y = 150
    x0, x1 = 70, W - 70
    p.append(line(x0, y, x1, y, color=INK, sw=2))
    p.append(arrow(x1 - 2, y, x1 + 24, y, color=INK, sw=2))
    events = [
        # year, label, sub, above?, color, fill
        (0.04, "2007", "SPL", "на кожну родину\nокремо", True, FIELD, "#eafaf0"),
        (0.30, "2008", "CMSIS", "спільний\nфундамент імен", False, NEG, "#eaf0fd"),
        (0.62, "2014", "STM32Cube", "HAL + CubeMX\n(SPL приречено)", True, POS, "#fdecea"),
        (0.88, "2016", "LL у CubeMX", "тонкий шар\nповернувся (L4)", False, "#b8860b", "#fff4e0"),
    ]
    for frac, year, name, sub, above, col, fill in events:
        x = x0 + frac * (x1 - x0)
        p.append(circle(x, y, 8, fill=fill, stroke=col, sw=2.4))
        if above:
            p.append(text(x, y - 66, year, size=13, color=col, bold=True))
            b, w, h = textbox(x, y - 40, name, size=12, color=col, fill=fill,
                              stroke=col, sw=1.6, bold=True)
            p.append(b)
            p.append(mtext(x, y - 86, sub, size=9.5, color=MUTED))
            p.append(line(x, y - 28, x, y - 8, color=col, sw=1.4))
        else:
            p.append(text(x, y + 78, year, size=13, color=col, bold=True))
            b, w, h = textbox(x, y + 52, name, size=12, color=col, fill=fill,
                              stroke=col, sw=1.6, bold=True)
            p.append(b)
            p.append(mtext(x, y + 96, sub, size=9.5, color=MUTED))
            p.append(line(x, y + 8, x, y + 40, color=col, sw=1.4))
    p.append(text(W / 2, H - 14,
                  "кожна точка — відповідь на біль попередньої, а не пункт стрункого плану",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "libs-timeline.svg"), W, H, *p,
           title="Бібліотеки STM32: двадцять років в одній смузі")


# ── H2. cmsis-foundation: CMSIS як спільний фундамент ────────────────────────
def fig_cmsis_foundation():
    W, H = 760, 360
    p = []
    cx = W / 2
    # знизу — ядро, над ним CMSIS, угорі — три виробники зі своєю периферією
    core_y = 250
    cmsis_y = 188
    bw = 560
    # ядро
    p.append(rect(cx - bw / 2, core_y, bw, 48, fill="#efefef", stroke=INK, sw=1.6, rx=8))
    p.append(text(cx, core_y + 22, "ядро ARM Cortex-M — однакове в усіх", size=12.5,
                  color=MUTED, bold=True))
    # CMSIS
    p.append(rect(cx - bw / 2, cmsis_y, bw, 44, fill="#eaf0fd", stroke=NEG, sw=2, rx=8))
    p.append(text(cx, cmsis_y + 20, "CMSIS — спільна мова ядра + єдиний опис периферії",
                  size=12, color=NEG, bold=True))
    p.append(arrow(cx, cmsis_y + 44, cx, core_y - 2, color=INK, sw=1.6))
    # три виробники згори
    vendors = [("ST", "#eafaf0", FIELD), ("NXP", "#fff4e0", "#b8860b"), ("Atmel", "#fdecea", POS)]
    vw = 150
    gap = 30
    total = len(vendors) * vw + (len(vendors) - 1) * gap
    x = cx - total / 2 + vw / 2
    for name, fill, col in vendors:
        p.append(rect(x - vw / 2, 96, vw, 48, fill=fill, stroke=col, sw=1.8, rx=8))
        p.append(text(x, 116, name, size=13, color=col, bold=True))
        p.append(text(x, 134, "своя периферія", size=9.5, color=MUTED))
        p.append(arrow(x, cmsis_y - 2, x, 144 + 2, color=INK, sw=1.5))
        x += vw + gap
    p.append(mtext(cx, H - 30,
                   "тільки над спільним фундаментом кожен кладе своє;\nкод на CMSIS переноситься між виробниками там, де йдеться про ядро",
                   size=11, color=MUTED))
    render(os.path.join(OUT, "cmsis-foundation.svg"), W, H, *p,
           title="CMSIS: спільний фундамент під усіма Cortex-M")


# ── H3. spl-to-cube: розрізнені SPL → єдиний стек Cube ───────────────────────
def fig_spl_to_cube():
    W, H = 800, 360
    p = []
    # ліворуч: купа окремих SPL
    lx = 165
    p.append(text(lx, 64, "до 2014: SPL на кожну родину", size=12.5, color=FIELD, bold=True))
    fams = ["F1", "F4", "F0", "L1", "F3"]
    fy = 92
    for i, f in enumerate(fams):
        yy = fy + i * 40
        p.append(rect(lx - 90, yy, 180, 32, fill="#eafaf0", stroke=FIELD, sw=1.5, rx=6))
        p.append(text(lx, yy + 20, "SPL для %s" % f, size=11.5, color=FIELD, bold=True))
    p.append(text(lx, fy + len(fams) * 40 + 18, "кожну окремо підтримувати",
                  size=10, color=MUTED, italic=True))
    # стрілка переходу
    p.append(arrow(lx + 110, H / 2 - 10, lx + 210, H / 2 - 10, color=INK, sw=2.4))
    p.append(text(lx + 160, H / 2 - 22, "2014", size=11, color=POS, bold=True))
    # праворуч: єдиний стек Cube
    rx = W - 200
    p.append(text(rx, 64, "Cube: один стек на всі родини", size=12.5, color=NEG, bold=True))
    stack = [
        ("CubeMX (генератор)", "#eef3ff", NEG),
        ("HAL — спільний на всі родини", "#eef3ff", NEG),
        ("CMSIS-регістри", "#eaf0fd", "#3b5bdb"),
    ]
    sy = 120
    for name, fill, col in stack:
        p.append(rect(rx - 130, sy, 260, 44, fill=fill, stroke=col, sw=1.7, rx=7))
        p.append(text(rx, sy + 26, name, size=11, color=col, bold=True))
        sy += 56
    p.append(mtext(rx, sy + 18, "виграш: кінець дублювання,\nпереносність",
                   size=10, color=POS))
    p.append(mtext(W / 2, H - 26,
                   "ціна: єдиний шар (HAL) вийшов товстим, а тонкої альтернативи спершу не лишилося",
                   size=11, color=MUTED))
    render(os.path.join(OUT, "spl-to-cube.svg"), W, H, *p,
           title="Перелом 2014-го: від розрізнених SPL до єдиного Cube")


# ── H4. why-two-layers: чому шарів саме два (HAL і LL) ────────────────────────
def fig_why_two_layers():
    W, H = 780, 330
    p = []
    cards = [
        ("HAL", NEG, "#eef3ff",
         ["прийшов 2014-го", "ставка на переносність", "і готову складність",
          "→ вийшов товстим"],
         "скарга: «дайте простоти\nй переносності»"),
        ("LL", "#b8860b", "#fff4e0",
         ["додали ~2016 (з L4)", "повертає дух SPL:", "тонко, близько до заліза",
          "→ майже швидкість регістрів"],
         "скарга: «дайте швидкості\nй контролю»"),
    ]
    cw = 300
    gap = 60
    total = len(cards) * cw + gap
    x = (W - total) / 2 + cw / 2
    for name, col, fill, lines, note in cards:
        p.append(rect(x - cw / 2, 70, cw, 150, fill=fill, stroke=col, sw=2, rx=10))
        p.append(text(x, 98, name, size=16, color=col, bold=True))
        ty = 124
        for ln in lines:
            p.append(text(x, ty, ln, size=11, color=INK))
            ty += 22
        p.append(mtext(x, 246, note, size=10.5, color=col))
        x += cw + gap
    p.append(text(W / 2, H - 20,
                  "не конкуренти, а відповіді на дві різні скарги — звідси й два паралельні шари",
                  size=11, color=MUTED, italic=True))
    render(os.path.join(OUT, "why-two-layers.svg"), W, H, *p,
           title="Чому шарів саме два: HAL і LL виросли з різних потреб")


if __name__ == "__main__":
    fig_three_layers()
    fig_same_blink()
    fig_cost_bars()
    fig_when_which()
    fig_libs_timeline()
    fig_cmsis_foundation()
    fig_spl_to_cube()
    fig_why_two_layers()
    print("OK: figures written to", OUT)
