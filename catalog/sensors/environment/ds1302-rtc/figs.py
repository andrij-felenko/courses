# -*- coding: utf-8 -*-
"""Фігури до каталог-теми «DS1302 — RTC-модуль (CR2032)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


# ── 1. Розводка: три дроти даних + живлення від МК до модуля ──────────────────
def fig_wiring():
    W, H = 900, 470
    f = [text(W / 2, 30, "П'ять дротів: три керують, два живлять",
              size=16, bold=True)]

    # МК ліворуч
    mkx, mky, mkw, mkh = 60, 110, 165, 250
    f.append(rect(mkx, mky, mkw, mkh, fill="#eef2f8", stroke=INK, sw=1.7, rx=10))
    f.append(text(mkx + mkw / 2, mky + 26, "Мікроконтролер", size=12.5, bold=True))
    f.append(text(mkx + mkw / 2, mky + 44, "(ESP32 / Arduino)", size=10, color=MUTED))
    mk_pins = [("3V3 / 5V", POS, mky + 92),
               ("GND", INK, mky + 132),
               ("будь-який GPIO", NEG, mky + 172),
               ("будь-який GPIO", NEG, mky + 210),
               ("будь-який GPIO", NEG, mky + 240)]
    for lbl, col, y in mk_pins:
        f.append(text(mkx + mkw - 12, y, lbl, size=10.5, bold=True, color=col, anchor="end"))

    # модуль праворуч
    ax, ay, aw, ah = 520, 90, 300, 300
    f.append(rect(ax, ay, aw, ah, fill="#fafbfc", stroke=MUTED, sw=1.8, rx=12))
    f.append(text(ax + aw / 2, ay + 24, "Модуль DS1302", size=13, bold=True))
    f.append(text(ax + aw / 2, ay + 42, "мікросхема · кварц 32.768 кГц · CR2032", size=9.5, color=MUTED))

    # п'ять вхідних контактів модуля (дзеркало МК)
    in_pins = [("VCC", POS,  mky + 92,  "2.0 – 5.5 В"),
               ("GND", INK,  mky + 132, "спільна земля"),
               ("CLK", NEG,  mky + 172, "такт (SCLK)"),
               ("DAT", NEG,  mky + 210, "дані I/O — двонапрямні"),
               ("RST", NEG,  mky + 240, "вибір кристала (CE)")]
    for lbl, col, y, note in in_pins:
        f.append(text(ax + 14, y, lbl, size=11.5, bold=True, color=col, anchor="start"))
        f.append(text(ax + 62, y, note, size=9.5, color=INK, anchor="start"))
        f.append(line(mkx + mkw, y, ax, y, color=col, sw=2.0))

    # батарейка й кварц — позначки всередині модуля
    f.append(circle(ax + aw / 2 - 55, ay + ah - 46, 22, fill="#fdf6e3", stroke=POS, sw=1.6))
    f.append(text(ax + aw / 2 - 55, ay + ah - 42, "CR2032", size=8.5, anchor="middle", bold=True))
    f.append(rect(ax + aw / 2 + 18, ay + ah - 62, 78, 32, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=5))
    f.append(text(ax + aw / 2 + 57, ay + ah - 48, "кварц", size=9, anchor="middle"))
    f.append(text(ax + aw / 2 + 57, ay + ah - 36, "32.768 кГц", size=8.5, anchor="middle"))

    b, bw, bh = textbox(W / 2, H - 22,
                        "CLK, DAT, RST — на будь-які три GPIO (це не апаратний SPI); DAT читає й пише по черзі однією лінією",
                        size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "wiring.svg"), W, H, *f)


# ── 2. Командний байт і BCD: як число «45 секунд» лягає в регістр ─────────────
def fig_command_bcd():
    W, H = 900, 560
    f = [text(W / 2, 30, "Командний байт задає регістр; дані в ньому — BCD",
              size=16, bold=True)]

    # верх: розклад командного байта на біти
    bx, by = 70, 90
    cw, ch = 95, 58
    bits = [
        ("1", "завжди 1", INK),
        ("R/C", "0=годинник\n1=RAM", NEG),
        ("A4", "", FIELD),
        ("A3", "адреса", FIELD),
        ("A2", "регістра", FIELD),
        ("A1", "", FIELD),
        ("A0", "", FIELD),
        ("R/W", "0=запис\n1=читання", POS),
    ]
    f.append(text(bx + 4 * cw, by - 16, "командний байт (біт 7 → біт 0)", size=12, bold=True))
    for i, (nm, desc, col) in enumerate(bits):
        x = bx + i * cw
        f.append(rect(x, by, cw, ch, fill=BG, stroke=INK, sw=1.6, rx=6))
        f.append(text(x + cw / 2, by + 22, nm, size=12.5, bold=True, color=col))
        if desc:
            f.append(mtext(x + cw / 2, by + 40, desc, size=8.5, color=MUTED, lh=1.15))

    # приклад-адреса секунд
    f.append(text(W / 2, by + ch + 34,
                  "Регістр секунд на запис = 1000 0000 = 0x80;  на читання — той самий, але біт 0 = 1 → 0x81",
                  size=11.5, color=INK))

    # низ: BCD — байт секунд, поділ на десятки/одиниці
    sby = by + ch + 90
    f.append(text(W / 2, sby - 18, "Регістр секунд у BCD: старший нібл — десятки, молодший — одиниці",
                  size=13, bold=True))
    sbx = 70
    sc = 95
    sbits = [
        ("CH", "стоп\nгодинника", POS),
        ("40", "десятки", FIELD),
        ("20", "секунд", FIELD),
        ("10", "(0–5)", FIELD),
        ("8", "одиниці", NEG),
        ("4", "секунд", NEG),
        ("2", "(0–9)", NEG),
        ("1", "", NEG),
    ]
    for i, (nm, desc, col) in enumerate(sbits):
        x = sbx + i * sc
        f.append(rect(x, sby, sc, ch, fill=BG, stroke=INK, sw=1.6, rx=6))
        f.append(text(x + sc / 2, sby + 22, nm, size=12, bold=True, color=col))
        if desc:
            f.append(mtext(x + sc / 2, sby + 40, desc, size=8.5, color=MUTED, lh=1.15))

    # рядок конкретного значення 45
    vy = sby + ch + 30
    vbits = ["0", "1", "0", "0", "0", "1", "0", "1"]
    for i, bit in enumerate(vbits):
        x = sbx + i * sc
        col = POS if bit == "1" else MUTED
        f.append(text(x + sc / 2, vy, bit, size=15, bold=True, color=col))
    f.append(text(sbx + 8 * sc + 26, vy, "= 45 с", size=13, bold=True, color=INK, anchor="start"))
    f.append(text(sbx + 4 * sc, vy + 26, "десятки 4 (0100)  ·  одиниці 5 (0101)  →  «45», а не 0x45",
                  size=11, color=INK))

    b, bw, bh = textbox(W / 2, H - 24,
                        "тому перед записом переводимо десяткове в BCD, а після читання — назад: dec = 10·(b>>4) + (b & 0x0F)",
                        size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "command-bcd.svg"), W, H, *f)


# ── 3. Сеанс читання: послідовність RST/CLK/DAT і перемикання напряму ─────────
def fig_read_session():
    W, H = 940, 470
    f = [text(W / 2, 30, "Сеанс читання: командний байт → перемкнули DAT → забрали дані",
              size=15.5, bold=True)]

    # три доріжки-сигнали
    x0, x1 = 150, 880          # межі осі часу
    lane = {"RST": 95, "CLK": 175, "DAT": 265}
    for nm, y in lane.items():
        f.append(text(x0 - 16, y + 4, nm, size=12.5, bold=True, anchor="end"))
        f.append(line(x0, y, x1, y, color=MUTED, sw=1.0, dash="3,3"))

    # межа між двома фазами: командний байт (вихід) | дані (вхід)
    xmid = 515
    f.append(line(xmid, 70, xmid, 300, color=FIELD, sw=1.4, dash="5,4"))
    f.append(text((x0 + xmid) / 2, 62, "фаза 1: командний байт — DAT ВИХІД",
                  size=11, bold=True, color=NEG))
    f.append(text((xmid + x1) / 2, 62, "фаза 2: дані — DAT ВХІД",
                  size=11, bold=True, color=POS))

    # RST: піднятий на весь сеанс
    ry = lane["RST"]
    f.append(line(x0, ry + 22, x0 + 24, ry + 22, color=INK, sw=2.4))       # низько
    f.append(line(x0 + 24, ry + 22, x0 + 24, ry, color=INK, sw=2.4))       # ↑
    f.append(line(x0 + 24, ry, x1 - 24, ry, color=INK, sw=2.4))            # високо
    f.append(line(x1 - 24, ry, x1 - 24, ry + 22, color=INK, sw=2.4))       # ↓
    f.append(line(x1 - 24, ry + 22, x1, ry + 22, color=INK, sw=2.4))       # низько
    f.append(text(x0 + 30, ry - 8, "підняли — сеанс почався", size=9.5, color=INK, anchor="start"))
    f.append(text(x1 - 30, ry + 38, "опустили — кінець", size=9.5, color=INK, anchor="end"))

    # CLK: рівні імпульси на весь сеанс
    cy = lane["CLK"]
    n = 16
    step = (x1 - 40 - (x0 + 40)) / (n * 2)
    cx = x0 + 40
    pts = [(cx, cy + 20)]
    for i in range(n):
        pts.append((cx, cy - 12)); pts.append((cx + step, cy - 12))       # ↑ і високо
        pts.append((cx + step, cy + 20)); pts.append((cx + 2 * step, cy + 20))  # ↓ і низько
        cx += 2 * step
    for i in range(len(pts) - 1):
        f.append(line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color=NEG, sw=1.8))

    # DAT: суцільний у фазі 1 (наш вихід), інша заливка у фазі 2 (вхід)
    dy = lane["DAT"]
    f.append(rect(x0 + 36, dy - 14, xmid - (x0 + 36) - 6, 30, fill="#eaf0fd", stroke=NEG, sw=1.4, rx=4))
    f.append(text((x0 + 36 + xmid) / 2 - 3, dy + 5, "МК виставляє біти команди", size=9.5, color=NEG))
    f.append(rect(xmid + 6, dy - 14, (x1 - 36) - (xmid + 6), 30, fill="#fdecea", stroke=POS, sw=1.4, rx=4))
    f.append(text((xmid + x1) / 2 - 3, dy + 5, "мікросхема віддає біти даних", size=9.5, color=POS))

    # два правила фронтів — підписи знизу, з запасом, повз лінії
    r1y, r2y = 340, 372
    f.append(circle(x0 + 8, r1y - 4, 5, fill="#eaf0fd", stroke=NEG, sw=1.4))
    f.append(text(x0 + 22, r1y, "ЗАПИС: МК виставляє біт, мікросхема зчитує його по ↑ (наростаючому) фронту CLK",
                  size=11, color=INK, anchor="start"))
    f.append(circle(x0 + 8, r2y - 4, 5, fill="#fdecea", stroke=POS, sw=1.4))
    f.append(text(x0 + 22, r2y, "ЧИТАННЯ: мікросхема виставляє біт по ↓ (спадному) фронту, МК читає ПІСЛЯ нього",
                  size=11, color=INK, anchor="start"))

    b, bw, bh = textbox(W / 2, H - 26,
                        "біти йдуть молодшим уперед (LSB); одна лінія DAT служить в обидва боки — тому pinMode перемикають посеред сеансу",
                        size=11, fill="#eef6ef", stroke=FIELD)
    f.append(b)
    render(os.path.join(IMG, "read-session.svg"), W, H, *f)


if __name__ == "__main__":
    fig_wiring()
    fig_command_bcd()
    fig_read_session()
    print("OK: 3 figures ->", IMG)
