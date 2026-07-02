# -*- coding: utf-8 -*-
"""Фігури до вставки «Інтерфейсні передавачі з керованим нахилом» (comp-line-transceiver).
Запуск:  python figs-transceiver.py   → пише SVG у ./img/
Помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Блок-схема трансивера: логіка ⇄ два дроти, вивід нахилу ────────────────
# Ідея: в одному корпусі драйвер + приймач; всередину — TXD/RXD (одна ніжка на
# логічний рівень), назовні — два дроти CANH/CANL (A/B); окремий вивід RS задає
# крутість / режим. Показати, ЩО з'єднує чіп: логіку з парою.
def fig_blocks():
    W, H = 780, 380
    f = []
    f.append(text(W / 2, 30,
                  "Трансивер: драйвер + приймач в одному корпусі між логікою й двома дротами",
                  size=12.5, color=MUTED, italic=True))

    # корпус чіпа
    cx0, cy0, cw, ch = 250, 70, 280, 250
    f.append(rect(cx0, cy0, cw, ch, fill="#f7f9fb", stroke=INK, sw=2, rx=10))
    f.append(text(cx0 + cw / 2, cy0 + 22, "приймачопередавач", size=12.5, color=INK, bold=True))

    # драйвер (верх): TXD → дзеркальна пара
    dbx, dby, dbw, dbh = cx0 + 26, cy0 + 44, 150, 74
    f.append(rect(dbx, dby, dbw, dbh, fill="#fdf0ee", stroke=POS, sw=1.6, rx=6))
    f.append(text(dbx + dbw / 2, dby + 22, "драйвер", size=11.5, color=POS, bold=True))
    f.append(text(dbx + dbw / 2, dby + 42, "один рівень → пара", size=9.5, color=MUTED))
    f.append(text(dbx + dbw / 2, dby + 58, "«+» вгору, «−» вниз", size=9.5, color=MUTED))

    # приймач (низ): пара → RXD
    rbx, rby, rbw, rbh = cx0 + 26, cy0 + 132, 150, 74
    f.append(rect(rbx, rby, rbw, rbh, fill="#eef2fd", stroke=NEG, sw=1.6, rx=6))
    f.append(text(rbx + rbw / 2, rby + 22, "приймач", size=11.5, color=NEG, bold=True))
    f.append(text(rbx + rbw / 2, rby + 42, "різниця пари → рівень", size=9.5, color=MUTED))
    f.append(text(rbx + rbw / 2, rby + 58, "широке синфазне вікно", size=9.5, color=MUTED))

    # логіка ліворуч: TXD / RXD
    lx = 70
    f.append(text(lx, cy0 + 20, "логіка МК", size=11, color=INK, bold=True, anchor="start"))
    # TXD в драйвер
    ty = dby + dbh / 2
    f.append(text(lx, ty - 8, "TXD", size=11, color=INK, anchor="start"))
    f.append(arrow(lx + 40, ty, dbx, ty, color=INK, sw=1.8))
    # RXD з приймача
    ry = rby + rbh / 2
    f.append(text(lx, ry - 8, "RXD", size=11, color=INK, anchor="start"))
    f.append(arrow(rbx, ry, lx + 40, ry, color=INK, sw=1.8))

    # вивід RS / SLOPE вниз
    sx = cx0 + cw / 2
    f.append(line(sx, cy0 + ch, sx, cy0 + ch + 30, color=FIELD, sw=2))
    f.append(text(sx, cy0 + ch + 46, "RS / SLOPE — вивід керування нахилом (режимом)",
                  size=10.5, color=FIELD, bold=True))

    # два дроти праворуч: CANH / CANL (A/B)
    wx = cx0 + cw
    # об'єднати обидва плеча в спільний вузол пари
    ah = dby + 18  # верхнє плече з драйвера/в приймач
    al = rby + rbh - 18
    px = wx + 60
    # плечі від драйвера
    f.append(line(dbx + dbw, ah, px, ah, color=POS, sw=2.2))
    f.append(line(rbx + rbw, al, px, al, color=NEG, sw=2.2))
    # приймач теж торкається пари (пунктир — спільні виводи)
    f.append(line(dbx + dbw, ah + 22, wx + 20, ah + 22, color=POS, sw=1.2, dash="3,3"))
    f.append(line(rbx + rbw, al - 22, wx + 20, al - 22, color=NEG, sw=1.2, dash="3,3"))
    f.append(line(wx + 20, ah + 22, wx + 20, al - 22, color=MUTED, sw=1, dash="3,3"))

    # два дроти назовні
    f.append(line(px, ah, px + 90, ah, color=POS, sw=2.6))
    f.append(line(px, al, px + 90, al, color=NEG, sw=2.6))
    f.append(text(px + 94, ah + 4, "CANH / A", size=11, color=POS, anchor="start", bold=True))
    f.append(text(px + 94, al + 4, "CANL / B", size=11, color=NEG, anchor="start", bold=True))
    f.append(text(px + 45, (ah + al) / 2, "вита пара", size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "transceiver-blocks.svg"), W, H, *f)


# ── 2. Вивід RS: три режими, резистор задає крутість ─────────────────────────
# Ідея: один вивід — три ролі. RS→GND = найшвидше; резистор на землю = нахил
# (більший опір → пологіше); RS→VCC = standby. Показати обернену залежність.
def fig_rs_modes():
    W, H = 780, 400
    f = []
    f.append(text(W / 2, 30,
                  "Вивід RS: одна ніжка — три режими; резистор на землю задає крутість",
                  size=12.5, color=MUTED, italic=True))

    col_w = W / 3
    y0 = 60
    boxh = 150

    def mode(cx, title, wiring, tint, edge, note):
        bw = col_w - 60
        bx = cx - bw / 2
        f.append(rect(bx, y0, bw, boxh, fill=tint, stroke=edge, sw=1.8, rx=8))
        f.append(text(cx, y0 + 26, title, size=12.5, color=edge, bold=True))
        f.append(text(cx, y0 + 48, wiring, size=10.5, color=INK))
        f.append(text(cx, y0 + 118, note, size=9.5, color=MUTED))
        return bx, bw

    # режим 1: high-speed
    bx1, bw1 = mode(col_w * 0.5, "high-speed", "RS ── 0 Ω ── GND", "#fdf0ee", POS,
                    "без обмеження нахилу")
    # крута сходинка
    ex, ey = col_w * 0.5, y0 + 88
    f.append('<polyline points="%d,%d %d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ex - 44, ey, ex - 6, ey, ex - 6, ey - 26, ex + 44, ey - 26, POS))

    # режим 2: slope control
    bx2, bw2 = mode(col_w * 1.5, "slope control", "RS ── R ── GND", "#eef6ef", FIELD,
                    "нахил ∝ 1/R")
    ex, ey = col_w * 1.5, y0 + 88
    f.append('<polyline points="%d,%d %d,%d %d,%d" fill="none" stroke="%s" stroke-width="2.6"/>'
             % (ex - 44, ey, ex + 10, ey - 26, ex + 44, ey - 26, FIELD))

    # режим 3: standby
    bx3, bw3 = mode(col_w * 2.5, "standby / silent", "RS ── високий рівень", "#eef2fd", NEG,
                    "драйвер спить, приймач чує")
    ex, ey = col_w * 2.5, y0 + 88
    f.append(line(ex - 44, ey - 13, ex + 44, ey - 13, color=NEG, sw=2.2, dash="5,4"))
    f.append(text(ex, ey + 6, "тиша на шині", size=9, color=NEG))

    # нижня шкала: резистор → крутість (обернено)
    ay = 320
    f.append(line(120, ay, 660, ay, color=INK, sw=2))
    f.append(arrow(660, ay, 672, ay, color=INK, sw=2))
    f.append(text(120, ay + 24, "малий R  →  крутіше (≈15 В/мкс при 10 кОм)",
                  size=10, color=MUTED, anchor="start"))
    f.append(text(660, ay + 24, "великий R  →  пологіше (≈2 В/мкс при 100 кОм)",
                  size=10, color=MUTED, anchor="end"))
    # мітки
    for rx, lbl in [(190, "0 Ω"), (300, "10к"), (470, "47к"), (600, "100к")]:
        f.append(line(rx, ay - 5, rx, ay + 5, color=INK, sw=1.5))
        f.append(text(rx, ay - 12, lbl, size=9.5, color=INK))
    f.append(text(W / 2, ay + 48,
                  "правило класу: бери НАЙПОЛОГІШИЙ фронт, що ще несе потрібну швидкість шини",
                  size=10.5, color=FIELD, bold=True))

    render(os.path.join(IMG, "rs-modes.svg"), W, H, *f)


# ── 3. Топологія шини: термінатори на кінцях, спільна земля, дросель ──────────
# Ідея: клас живе на спільній лінії. Дві граблі — де ставити 120 Ω (тільки на
# двох кінцях, не на кожному вузлі) і спільна земля. Плюс синфазний дросель.
def fig_bus():
    W, H = 800, 340
    f = []
    f.append(text(W / 2, 30,
                  "Спільна шина: 120 Ω рівно на двох кінцях, спільна земля, дросель проти синфазного",
                  size=12, color=MUTED, italic=True))

    # дві лінії пари
    yH, yL = 110, 150
    x0, x1 = 90, 710
    f.append(line(x0, yH, x1, yH, color=POS, sw=2.6))
    f.append(line(x0, yL, x1, yL, color=NEG, sw=2.6))
    f.append(text(x0 - 6, yH + 4, "H", size=11, color=POS, anchor="end", bold=True))
    f.append(text(x0 - 6, yL + 4, "L", size=11, color=NEG, anchor="end", bold=True))

    # термінатори на двох кінцях (120 Ω між H і L)
    def term(x, ok):
        c = FIELD if ok else POS
        f.append(rect(x - 9, yH, 18, yL - yH, fill="#fff", stroke=c, sw=2, rx=3))
        f.append(text(x, (yH + yL) / 2 + 4, "120", size=9, color=c, bold=True))
    term(x0 + 14, True)
    term(x1 - 14, True)
    f.append(text(x0 + 14, yL + 22, "кінець", size=9, color=FIELD))
    f.append(text(x1 - 14, yL + 22, "кінець", size=9, color=FIELD))

    # три вузли-трансивери вздовж лінії (короткі відводи)
    for nx, lbl in [(240, "вузол"), (400, "вузол"), (560, "вузол")]:
        f.append(line(nx, yL, nx, yL + 46, color=MUTED, sw=1.4))
        f.append(line(nx - 14, yH, nx - 14, yL + 46, color=MUTED, sw=1.4))
        f.append(rect(nx - 30, yL + 46, 58, 34, fill="#f7f9fb", stroke=INK, sw=1.4, rx=5))
        f.append(text(nx - 1, yL + 67, lbl, size=9.5, color=INK))
        f.append(text(nx - 1, yL + 92, "БЕЗ 120", size=8, color=MUTED))

    # спільна земля (третій провід) знизу
    gy = yL + 130
    f.append(line(x0, gy, x1, gy, color=INK, sw=1.8, dash="6,4"))
    f.append(text(W / 2, gy - 8, "спільна земля / зворотний провід — тримає синфазний рівень у вікні",
                  size=10, color=INK, italic=True))
    # позначка землі
    f.append(line(x1 - 40, gy, x1 - 40, gy + 12, color=INK, sw=1.6))
    for i, wgnd in enumerate([16, 10, 5]):
        f.append(line(x1 - 40 - wgnd, gy + 12 + i * 4, x1 - 40 + wgnd, gy + 12 + i * 4, color=INK, sw=1.6))

    # синфазний дросель біля одного вузла
    dcx = 400
    f.append(circle(dcx - 14, yH, 5, fill="#fff", stroke=FIELD, sw=1.6))
    f.append(circle(dcx, yL, 5, fill="#fff", stroke=FIELD, sw=1.6))
    f.append(text(dcx + 40, yH - 14, "синфазний", size=9, color=FIELD, anchor="middle"))
    f.append(text(dcx + 40, yH - 3, "дросель", size=9, color=FIELD, anchor="middle"))

    render(os.path.join(IMG, "bus-topology.svg"), W, H, *f)


if __name__ == "__main__":
    fig_blocks()
    fig_rs_modes()
    fig_bus()
    print("OK: transceiver-blocks, rs-modes, bus-topology")
