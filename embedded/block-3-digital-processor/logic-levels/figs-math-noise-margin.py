# -*- coding: utf-8 -*-
"""
Фігури до 🧮-вставки «Бюджет завадостійкості: VOH/VOL/VIH/VIL і розрахунок
noise margin з даташита» (до §3.1.3, Модуль 3, Розділ 3.1).

Окремий скрипт вставки — головний figs.py розділу НЕ чіпаємо (AUTHORING §9, §16).
Чистий Python без залежностей; вивід → ./img/ тієї самої папки.
Стиль успадковано від figs.py розділу: білий фон; «1»/HIGH червоний, «0»/LOW синій;
«дійсне/запас» — зелене; пороги входу — помаранчеві; шрифт sans-serif.
Нумерація підписів у тексті — «Рис. 3.1.3m.k».
"""
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── палітра (копія з figs.py розділу, §9 — спільний вигляд) ───────────────────
RED    = "#c0271e"   # HIGH / «1»
BLUE   = "#1f47b5"   # LOW / «0»
GREEN  = "#1f8a3b"   # дійсне / запас
ORANGE = "#b06a1e"   # пороги входу
INK    = "#1b1b1b"
GREY   = "#8a8a8a"
FAINT  = "#e4e4e4"
AMBER  = "#caa24a"
FONT   = "Segoe UI, Arial, Helvetica, sans-serif"


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def header(w, h):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}">\n'
        f'<rect width="{w}" height="{h}" fill="#ffffff"/>\n'
        f'<defs>\n'
        f'  <marker id="aInk" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{INK}"/></marker>\n'
        f'  <marker id="aGreen" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{GREEN}"/></marker>\n'
        f'  <marker id="aRed" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{RED}"/></marker>\n'
        f'  <marker id="aOrange" markerWidth="11" markerHeight="11" refX="8" refY="3.2" '
        f'orient="auto" markerUnits="strokeWidth"><path d="M0,0 L8.5,3.2 L0,6.4 Z" fill="{ORANGE}"/></marker>\n'
        f'</defs>\n'
    )


def footer():
    return "</svg>\n"


_MARK = {INK: "aInk", GREEN: "aGreen", RED: "aRed", ORANGE: "aOrange"}


def line(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} stroke-linecap="round"/>\n')


def arrow(x1, y1, x2, y2, color=INK, w=2, dash=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = _MARK.get(color, "aInk")
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="{w}"{d} marker-end="url(#{m})"/>\n')


def text(x, y, s, size=15, color=INK, anchor="start", weight="normal", style="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" font-weight="{weight}" '
            f'font-style="{style}">{_esc(s)}</text>\n')


def rect(x, y, w, h, fill="none", stroke=INK, sw=2, rx=0):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>\n')


def save(name, body):
    body += footer()
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(body)
    print("wrote", name)


# Канонічні числа сімейств (узгоджено з figs.py розділу, словник FAM):
#   3.3 В LVCMOS із TTL-сумісними порогами входу.
LV = dict(vdd=3.3, vol=0.4, voh=3.0, vil=0.8, vih=2.0)   # драйвер і приймач LVCMOS
TTL = dict(vdd=5.0, vol=0.4, voh=2.4, vil=0.8, vih=2.0)  # вхід 5 В TTL (для крос-сімейного стовпця)


# ── Рис. 3.1.3m.1 — від рядка даташита до запасу ─────────────────────────────
def fig_datasheet_to_margin():
    """Зліва — фрагмент таблиці DC Characteristics з умовами тесту;
    праворуч — ті самі чотири числа на шкалі напруг і обидва запаси."""
    W, H = 980, 560
    s = header(W, H)
    s += text(W / 2, 32, "Як прочитати запас із даташита: чотири числа, їхні УМОВИ — і відніми",
              20, INK, "middle", "bold")
    s += text(W / 2, 54,
              "приклад: 3.3-вольтовий LVCMOS-буфер; беремо гарантовані межі (min/max), а не «typical»",
              12.5, GREY, "middle", style="italic")

    # ── ЛІВО: фрагмент таблиці DC Characteristics ──
    tx, ty = 40, 96
    tw = 470
    s += text(tx, ty - 12, "Electrical Characteristics  ·  DC  (фрагмент)", 13.5, INK, "start", "bold")
    s += text(tx, ty + 6, "Vdd = 3.3 В,  TA = −40…+85 °C  —  гарантії для НАЙГІРШОГО випадку",
              11, GREY, "start", style="italic")
    cols = [tx, tx + 60, tx + 150, tx + 250, tx + 350, tx + tw]
    rowh = 34
    head_y = ty + 18
    s += rect(tx, head_y, tw, rowh, "#eef2f8", INK, 1.3)
    heads = ["Симв.", "Параметр", "Умови (test)", "Min", "Max"]
    hpos = [tx + 30, tx + 105, tx + 200, tx + 300, tx + 400]
    for hp, hh in zip(hpos, heads):
        s += text(hp, head_y + 22, hh, 11.5, INK, "middle", "bold")

    rows = [
        ("VOH", "вихід «1»",  "IOH = −4 мА",  "3.0", "—",  RED),
        ("VOL", "вихід «0»",  "IOL = +4 мА",  "—",   "0.4", BLUE),
        ("VIH", "вхід «1»",   "(гарант.)",    "2.0", "—",  ORANGE),
        ("VIL", "вхід «0»",   "(гарант.)",    "—",   "0.8", ORANGE),
        ("IIL/IIH", "витік входу", "Vi=0…Vdd", "—", "±1 мкА", GREY),
    ]
    for i, (sym, par, cond, vmin, vmax, col) in enumerate(rows):
        ry = head_y + rowh * (i + 1)
        bg = "#ffffff" if i % 2 == 0 else "#fafbfd"
        s += rect(tx, ry, tw, rowh, bg, GREY, 1)
        s += text(hpos[0], ry + 22, sym, 12, col, "middle", "bold")
        s += text(tx + 70, ry + 22, par, 11.5, INK, "start")
        s += text(hpos[2], ry + 22, cond, 10.5, GREY, "middle")
        s += text(hpos[3], ry + 22, vmin, 12, (col if vmin != "—" else GREY), "middle",
                  "bold" if vmin != "—" else "normal")
        s += text(hpos[4], ry + 22, vmax, 12, (col if vmax != "—" else GREY), "middle",
                  "bold" if vmax != "—" else "normal")
    # вертикальні лінії стовпців
    for cx in cols:
        s += line(cx, head_y, cx, head_y + rowh * 6, GREY, 1)

    # підказки до умов
    note_y = head_y + rowh * 6 + 26
    s += text(tx, note_y, "Умова — частина числа!  VOH = 3.0 В гарантовано лише",
              11.5, INK, "start", "bold")
    s += text(tx, note_y + 17, "доки витягуєш не більше IOH = 4 мА; візьмеш більший струм —",
              11.5, INK, "start")
    s += text(tx, note_y + 34, "вихід «1» просяде нижче, і запас зменшиться.", 11.5, INK, "start")

    # ── стрілки переносу чотирьох чисел праворуч ──
    bridge_x = tx + tw + 8
    s += text(bridge_x + 18, head_y - 2, "→", 18, GREEN, "middle", "bold")

    # ── ПРАВО: шкала напруг з чотирма рівнями ──
    sx = 690
    top_y, bot_y = 110, 470
    vdd = LV["vdd"]

    def vy(v):
        return bot_y - (v / vdd) * (bot_y - top_y)

    # вісь
    s += line(sx, top_y, sx, bot_y, INK, 2)
    for v in range(0, 4):
        s += line(sx - 5, vy(v), sx + 5, vy(v), GREY, 1.4)
        s += text(sx - 9, vy(v) + 4, str(v), 10.5, GREY, "end")
    s += text(sx - 9, vy(vdd) + 4, "3.3", 10.5, GREY, "end")
    s += text(sx - 9, top_y - 8, "В", 10.5, GREY, "end")

    bx0, bw = sx + 24, 150
    voh, vih, vil, vol = LV["voh"], LV["vih"], LV["vil"], LV["vol"]
    # смуги станів
    s += rect(bx0, top_y, bw, vy(voh) - top_y, "#fdf4f4", "none", 0)        # драйвер «1»
    s += rect(bx0, vy(voh), bw, vy(vih) - vy(voh), "#eafaef", "none", 0)    # NMH
    s += rect(bx0, vy(vih), bw, vy(vil) - vy(vih), "#ededed", "none", 0)    # заборонено
    s += rect(bx0, vy(vil), bw, vy(vol) - vy(vil), "#eafaef", "none", 0)    # NML
    s += rect(bx0, vy(vol), bw, bot_y - vy(vol), "#f3f5fd", "none", 0)      # драйвер «0»
    s += rect(bx0, top_y, bw, bot_y - top_y, "none", INK, 1.5)

    for v, col, lab, dash in ((voh, RED, "VOH 3.0", None), (vih, ORANGE, "VIH 2.0", "5 4"),
                              (vil, ORANGE, "VIL 0.8", "5 4"), (vol, BLUE, "VOL 0.4", None)):
        s += line(bx0, vy(v), bx0 + bw, vy(v), col, 1.8, dash)
        s += text(bx0 + bw + 6, vy(v) + 4, lab, 11, col, "start", "bold")
    s += text(bx0 + bw / 2, (top_y + vy(voh)) / 2 + 4, "драйвер «1»", 11, RED, "middle", "bold")
    s += text(bx0 + bw / 2, (vy(vih) + vy(vil)) / 2 + 4, "заборонено", 10.5, "#5a5a5a", "middle", "bold")
    s += text(bx0 + bw / 2, (vy(vol) + bot_y) / 2 + 4, "драйвер «0»", 11, BLUE, "middle", "bold")

    # дужки запасів усередині смуг
    s += text(bx0 + bw / 2, (vy(voh) + vy(vih)) / 2 + 4, "NMH", 12.5, GREEN, "middle", "bold")
    s += text(bx0 + bw / 2, (vy(vil) + vy(vol)) / 2 + 4, "NML", 12.5, GREEN, "middle", "bold")

    # ── підсумкова формула знизу праворуч ──
    fx, fy = sx + 4, bot_y + 22
    nmh = voh - vih
    nml = vil - vol
    s += text(fx, fy, f"NMH = VOH−VIH = 3.0−2.0 = {nmh:.1f} В", 12, GREEN, "start", "bold")
    s += text(fx, fy + 20, f"NML = VIL−VOL = 0.8−0.4 = {nml:.1f} В", 12, GREEN, "start", "bold")
    s += text(fx, fy + 40, f"запас лінії = min = {min(nmh, nml):.1f} В  ← слабший бік",
              12, INK, "start", "bold")

    save("fig-14-3m-1-datasheet-to-margin.svg", s)


# ── Рис. 3.1.3m.2 — своя пара vs крос-сімейний стик ──────────────────────────
def fig_pairing():
    """Дві перевірки в одному кадрі: однакові числа (LVCMOS→LVCMOS) і
    крос-сімейний випадок (LVCMOS-драйвер → 5 В TTL-вхід). Завжди:
    вихід ДРАЙВЕРА проти входу ПРИЙМАЧА; беремо менший із двох запасів."""
    W, H = 980, 516
    s = header(W, H)
    s += text(W / 2, 32, "Завжди: вихід ДРАЙВЕРА проти входу ПРИЙМАЧА — і береш менший запас",
              19.5, INK, "middle", "bold")
    s += text(W / 2, 54,
              "числа драйвера й приймача — з РІЗНИХ таблиць; запас «1» рахуй з VOH(драйв.) і VIH(прийм.), «0» — з VIL(прийм.) і VOL(драйв.)",
              11.5, GREY, "middle", style="italic")

    def panel(cx, title, drv, rcv, drv_lbl, rcv_lbl):
        top_y, bot_y = 100, 380
        vdd = max(drv["vdd"], rcv["vdd"])

        def vy(v):
            return bot_y - (v / vdd) * (bot_y - top_y)

        s_ = text(cx, 86, title, 14.5, INK, "middle", "bold")
        # вісь
        ax = cx - 150
        s_ += line(ax, top_y, ax, bot_y, INK, 1.8)
        for v in range(0, int(vdd) + 1):
            s_ += line(ax - 4, vy(v), ax + 4, vy(v), GREY, 1.2)
            s_ += text(ax - 8, vy(v) + 4, str(v), 10, GREY, "end")
        s_ += text(ax - 8, top_y - 8, "В", 10, GREY, "end")

        # колонка ДРАЙВЕР (виходи)
        dx, dw = cx - 110, 95
        s_ += text(dx + dw / 2, top_y - 10, drv_lbl, 11.5, INK, "middle", "bold")
        s_ += text(dx + dw / 2, top_y - 26, "ДРАЙВЕР", 10.5, GREY, "middle", "bold")
        s_ += rect(dx, top_y, dw, vy(drv["voh"]) - top_y, "#fdf4f4", RED, 1.4)
        s_ += rect(dx, vy(drv["vol"]), dw, bot_y - vy(drv["vol"]), "#f3f5fd", BLUE, 1.4)
        s_ += line(dx, vy(drv["voh"]), dx + dw, vy(drv["voh"]), RED, 1.6)
        s_ += line(dx, vy(drv["vol"]), dx + dw, vy(drv["vol"]), BLUE, 1.6)
        s_ += text(dx + dw / 2, vy(drv["voh"]) - 6, f"VOH {drv['voh']:.1f}", 10.5, RED, "middle", "bold")
        s_ += text(dx + dw / 2, vy(drv["vol"]) + 14, f"VOL {drv['vol']:.1f}", 10.5, BLUE, "middle", "bold")

        # колонка ПРИЙМАЧ (входи)
        rx, rw = cx + 20, 95
        s_ += text(rx + rw / 2, top_y - 10, rcv_lbl, 11.5, INK, "middle", "bold")
        s_ += text(rx + rw / 2, top_y - 26, "ПРИЙМАЧ", 10.5, GREY, "middle", "bold")
        s_ += rect(rx, top_y, rw, vy(rcv["vih"]) - top_y, "#fdf4f4", ORANGE, 1.4)
        s_ += rect(rx, vy(rcv["vih"]), rw, vy(rcv["vil"]) - vy(rcv["vih"]), "#ededed", GREY, 1.2)
        s_ += rect(rx, vy(rcv["vil"]), rw, bot_y - vy(rcv["vil"]), "#f3f5fd", ORANGE, 1.4)
        s_ += line(rx, vy(rcv["vih"]), rx + rw, vy(rcv["vih"]), ORANGE, 1.6, "4 3")
        s_ += line(rx, vy(rcv["vil"]), rx + rw, vy(rcv["vil"]), ORANGE, 1.6, "4 3")
        s_ += text(rx + rw / 2, vy(rcv["vih"]) - 6, f"VIH {rcv['vih']:.1f}", 10.5, ORANGE, "middle", "bold")
        s_ += text(rx + rw / 2, vy(rcv["vil"]) + 14, f"VIL {rcv['vil']:.1f}", 10.5, ORANGE, "middle", "bold")
        s_ += text(rx + rw / 2, (vy(rcv["vih"]) + vy(rcv["vil"])) / 2 + 4, "заборон.", 9.5, "#5a5a5a", "middle")

        # запаси: дужки між колонками
        nmh = drv["voh"] - rcv["vih"]
        nml = rcv["vil"] - drv["vol"]
        # NMH дужка
        gxh = dx + dw + 6
        col_h = GREEN if nmh >= 0 else RED
        s_ += line(gxh, vy(drv["voh"]), gxh, vy(rcv["vih"]), col_h, 2)
        s_ += line(gxh - 4, vy(drv["voh"]), gxh + 4, vy(drv["voh"]), col_h, 2)
        s_ += line(gxh - 4, vy(rcv["vih"]), gxh + 4, vy(rcv["vih"]), col_h, 2)
        s_ += text(gxh + 2, (vy(drv["voh"]) + vy(rcv["vih"])) / 2 + 4,
                   f"NMH {nmh:+.1f}", 10.5, col_h, "start", "bold")
        # NML дужка
        col_l = GREEN if nml >= 0 else RED
        s_ += line(gxh, vy(rcv["vil"]), gxh, vy(drv["vol"]), col_l, 2)
        s_ += line(gxh - 4, vy(rcv["vil"]), gxh + 4, vy(rcv["vil"]), col_l, 2)
        s_ += line(gxh - 4, vy(drv["vol"]), gxh + 4, vy(drv["vol"]), col_l, 2)
        s_ += text(gxh + 2, (vy(rcv["vil"]) + vy(drv["vol"])) / 2 + 4,
                   f"NML {nml:+.1f}", 10.5, col_l, "start", "bold")

        verdict = f"min = {min(nmh, nml):+.1f} В"
        vcol = GREEN if min(nmh, nml) > 0 else RED
        s_ += rect(cx - 150, bot_y + 16, 300, 30, "#f4f7f4", vcol, 1.5, 8)
        tail = "  → стикується з запасом" if min(nmh, nml) > 0 else "  → НЕ стикується!"
        s_ += text(cx, bot_y + 36, verdict + tail, 12.5, vcol, "middle", "bold")
        return s_

    s += panel(255, "Своя пара: 3.3 В LVCMOS → 3.3 В LVCMOS", LV, LV,
               "LVCMOS 3.3", "LVCMOS 3.3")
    s += panel(725, "Крос-сімейство: 3.3 В LVCMOS → 5 В TTL", LV, TTL,
               "LVCMOS 3.3", "5 В TTL")

    s += rect(40, 452, W - 80, 44, "#eef4ff", BLUE, 1.5, 10)
    s += text(W / 2, 470,
              "3.3-вольтовий вихід (VOH 3.0) дотягується до TTL-порога VIH 2.0 — стик працює В ЦЕЙ БІК.",
              12, INK, "middle", "bold")
    s += text(W / 2, 488,
              "Зворотний бік (5 В драйвер → 3.3 В вхід) — окрема перевірка: там загроза вже не запасу, а максимальної напруги входу (§3.1.4).",
              11, GREY, "middle", style="italic")
    save("fig-14-3m-2-pairing.svg", s)


if __name__ == "__main__":
    fig_datasheet_to_margin()
    fig_pairing()
    print("done.")
