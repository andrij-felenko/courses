# -*- coding: utf-8 -*-
"""Фігури до теми «Лінк під глушінням» (jamming-fhss).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── 1. Що таке глушіння: гучна завада топить корисний сигнал ──────────────────
# Ідея, яку важко сказати словами: глушилка не «ламає» приймач, а просто
# піднімає шумовий п'єдестал на робочій частоті так, що корисна купка тоне в ньому.
def fig_jamming():
    W, H = 720, 380
    ox, oy = 70, 300            # лівий низ поля (рівень 0)
    aw, ah = 580, 230           # ширина/висота поля
    f = []

    def px(t):  return ox + t * aw          # t ∈ [0..1] — частота
    def py(v):  return oy - v * ah           # v ∈ [0..1] — потужність

    # осі
    f.append(line(ox, oy, ox + aw + 12, oy, color=MUTED, sw=1.3))
    f.append(arrow(ox + aw, oy, ox + aw + 16, oy, color=MUTED, sw=1.3))
    f.append(text(ox + aw + 22, oy + 4, "частота", 12, MUTED, "start"))
    f.append(line(ox, oy + 4, ox, py(1.04), color=MUTED, sw=1.3))
    f.append(text(ox - 8, py(1.0), "потужність", 12, MUTED, "end"))

    # п'єдестал теплового шуму
    nf = 0.12
    f.append(line(ox, py(nf), ox + aw, py(nf), color=MUTED, sw=1.2, dash="4 4"))
    f.append(text(ox + 6, py(nf) - 6, "рівень шуму", 11, MUTED, "start"))

    # корисний вузький сигнал — скромна купка трохи над шумом
    sx = px(0.34)
    f.append('<rect x="%.1f" y="%.1f" width="32" height="%.1f" rx="4" fill="#eef6ef" stroke="%s" stroke-width="2"/>'
             % (sx - 16, py(0.46), py(nf) - py(0.46), FIELD))
    # обидва рядки підпису піднято НАД верхом стовпчика, з запасом до його межі
    f.append(text(sx, py(0.46) - 24, "корисний", 11.5, FIELD, "middle", bold=True))
    f.append(text(sx, py(0.46) - 10, "сигнал", 10.5, FIELD, "middle"))

    # глушилка — гучна вузька завада, що накриває ту саму частоту
    jx = px(0.40)
    f.append('<rect x="%.1f" y="%.1f" width="26" height="%.1f" rx="4" fill="#fdecea" stroke="%s" stroke-width="2.4"/>'
             % (jx - 13, py(0.94), py(nf) - py(0.94), POS))
    f.append(text(jx + 70, py(0.9), "глушилка:", 12, POS, "middle", bold=True))
    f.append(text(jx + 78, py(0.9) + 16, "гучна завада на", 11, POS, "middle"))
    f.append(text(jx + 78, py(0.9) + 30, "тій самій частоті", 11, POS, "middle"))

    # стрілка «тоне»
    f.append(arrow(sx, py(0.46) + 6, sx, py(nf) - 6, color=MUTED, sw=1.6))
    f.append(fitbox(px(0.62), py(0.42), 230, 46,
                    "корисна купка тоне:\nсигнал/шум падає під поріг",
                    size=12, fill="#fdecea", stroke=POS, color=INK))

    render(os.path.join(IMG, "jamming.svg"), W, H, *f,
           title="Глушіння: гучна завада топить корисний сигнал")

def fig_fhss():
    W, H = 720, 400
    ox, oy = 70, 330
    aw, ah = 590, 250
    nch, nhop = 8, 12          # каналів × стрибків
    f = []

    cw = aw / nhop
    chh = ah / nch

    def cx(i):  return ox + i * cw
    def cy(c):  return oy - (c + 1) * chh

    # осі
    f.append(text(ox - 8, oy - ah / 2, "частота", 12, MUTED, "end"))
    f.append(text(ox + aw / 2, oy + 34, "час →", 12, MUTED, "middle"))
    f.append(line(ox, oy, ox + aw, oy, color=MUTED, sw=1.2))
    f.append(line(ox, oy, ox, oy - ah, color=MUTED, sw=1.2))

    # завада — постійно зайнятий канал (червона смуга через усе)
    jam = 5
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" stroke="%s" stroke-width="1.4"/>'
             % (ox, cy(jam), aw, chh, POS))
    f.append(text(ox + aw - 6, cy(jam) + chh / 2 + 4, "завада сидить тут", 11, POS, "end", bold=True))

    # псевдовипадкова послідовність стрибків
    seq = [1, 6, 3, 5, 0, 7, 2, 5, 4, 1, 6, 3]
    lost = 0
    for i, c in enumerate(seq):
        hit = (c == jam)
        col = POS if hit else FIELD
        fill = "#fdecea" if hit else "#eef6ef"
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="3" fill="%s" stroke="%s" stroke-width="1.8"/>'
                 % (cx(i) + 2, cy(c) + 2, cw - 4, chh - 4, fill, col))
        if hit:
            f.append(text(cx(i) + cw / 2, cy(c) + chh / 2 + 4, "✗", 13, POS, "middle", bold=True))
            lost += 1

    # підпис-висновок
    f.append(fitbox(ox + aw / 2 - 175, oy + 44, 350, 30,
                    "з %d стрибків зіпсовано лише %d — їх перевідправлять" % (nhop, lost),
                    size=12, fill="#eef6ef", stroke=FIELD, color=INK))

    render(os.path.join(IMG, "fhss.svg"), W, H, *f,
           title="Стрибки частоти (FHSS): нерухома завада псує лічені хопи")


# ── 3. DSSS: розгортання піднімає корисне, а заваду розмазує ──────────────────
# Ідея: множення на «свій» код стискає розмазаний сигнал у вузьку купку (вгору),
# а вузьку заваду той самий код розмазує по всій смузі (вниз) — SNR стрибає.
def fig_dsss():
    W, H = 760, 360
    f = [text(W / 2, 26, "Розгортання DSSS: код збирає сигнал, а заваду розмазує", 16, INK, "middle", bold=True)]

    def panel(x0, title):
        f.append(rect(x0, 56, 330, 270, fill="#fbfcfd", stroke="#dde3ea", sw=1.4, rx=8))
        f.append(text(x0 + 165, 78, title, 13.5, INK, "middle", bold=True))
        # локальні осі
        ax, ay, aw, ah = x0 + 36, 290, 260, 180
        f.append(line(ax, ay, ax + aw, ay, color=MUTED, sw=1.1))
        f.append(line(ax, ay, ax, ay - ah, color=MUTED, sw=1.1))
        f.append(text(ax + aw / 2, ay + 18, "частота", 10.5, MUTED, "middle"))
        return ax, ay, aw, ah

    nf = 0.18
    # ── ліва панель: до розгортання (у каналі) ──
    ax, ay, aw, ah = panel(30, "У каналі: обидва вузькі/широкі")
    # шум
    noise_y = ay - nf * ah
    f.append(line(ax, noise_y, ax + aw, noise_y, color=MUTED, sw=1, dash="4 4"))
    # корисний — РОЗМАЗАНИЙ широко й низько (під шумом)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#eef6ef" stroke="%s" stroke-width="1.6"/>'
             % (ax + 20, ay - 0.13 * ah, aw - 40, 0.13 * ah, FIELD))
    # напис піднято вище над лінією шуму, щоб не перетинати її
    f.append(text(ax + aw / 2, noise_y - 10, "корисний: розмазаний, під шумом", 10, FIELD, "middle"))
    # завада — вузька й гучна
    f.append('<rect x="%.1f" y="%.1f" width="20" height="%.1f" rx="3" fill="#fdecea" stroke="%s" stroke-width="2"/>'
             % (ax + 0.62 * aw, ay - 0.82 * ah, 0.82 * ah, POS))
    f.append(text(ax + 0.62 * aw + 10, ay - 0.82 * ah - 8, "завада", 10.5, POS, "middle", bold=True))

    # стрілка-перехід
    f.append(arrow(372, 190, 412, 190, color=INK, sw=2.2))
    f.append(text(392, 178, "× код", 11, INK, "middle", bold=True))

    # ── права панель: після розгортання у приймачі ──
    ax, ay, aw, ah = panel(400, "Після × коду: ролі помінялися")
    f.append(line(ax, ay - nf * ah, ax + aw, ay - nf * ah, color=MUTED, sw=1, dash="4 4"))
    # корисний — СТИСНУТИЙ у вузьку високу купку
    f.append('<rect x="%.1f" y="%.1f" width="22" height="%.1f" rx="3" fill="#eef6ef" stroke="%s" stroke-width="2.2"/>'
             % (ax + 0.30 * aw, ay - 0.88 * ah, 0.88 * ah, FIELD))
    f.append(text(ax + 0.30 * aw + 11, ay - 0.88 * ah - 8, "корисний ↑", 10.5, FIELD, "middle", bold=True))
    # завада — РОЗМАЗАНА широко й низько (під шумом)
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="#fdecea" stroke="%s" stroke-width="1.4"/>'
             % (ax + 16, ay - 0.10 * ah, aw - 32, 0.10 * ah, POS))
    f.append(text(ax + aw / 2, ay - 0.10 * ah - 7, "завада ↓ розмазана", 10, POS, "middle"))

    render(os.path.join(IMG, "dsss.svg"), W, H, *f)

def fig_pgain():
    # полотно розширено ліворуч (ox 90→150, W 680→740), щоб підпис осі "end" не вилазив за межі
    W, H = 740, 430
    ox, oy = 150, 350
    aw, ah = 520, 280
    f = []

    # осі (лог-вісь PG зліва→справа, лінійна dB)
    f.append(line(ox, oy, ox + aw + 12, oy, color=MUTED, sw=1.3))
    f.append(arrow(ox + aw, oy, ox + aw + 16, oy, color=MUTED, sw=1.3))
    f.append(text(ox + aw / 2, oy + 40, "у скільки разів розширили смугу (виграш обробки)", 12, MUTED, "middle"))
    f.append(line(ox, oy + 4, ox, oy - ah - 4, color=MUTED, sw=1.3))
    f.append(text(ox - 12, oy - ah / 2, "підйом\nсигнал/шум, дБ", 11.5, MUTED, "end"))

    # крива 10·log10(x): по осі x — log10 від PG (1..10000), по y — дБ
    PGs = [1, 11, 100, 1023, 20460]
    dBmax = 46.0
    def px(pg):  return ox + (math.log10(pg) / math.log10(20460)) * aw
    def py(db):  return oy - (db / dBmax) * ah

    pts = []
    x = 1.0
    while x <= 20460:
        pts.append("%.1f,%.1f" % (px(x), py(10 * math.log10(x))))
        x *= 1.06
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.8"/>'
             % (" ".join(pts), NEG))

    # сітка dB
    for db in [10, 20, 30, 40]:
        f.append(line(ox, py(db), ox + aw, py(db), color="#e5e7eb", sw=1, dash="3 4"))
        f.append(text(ox - 8, py(db) + 4, "%d дБ" % db, 10.5, MUTED, "end"))

    # маркери реальних систем
    marks = [(11, "Wi-Fi 802.11b\n(код Баркера)"), (20460, "GPS: 1.023 МЧ\nна 50 біт/с")]
    for pg, lab in marks:
        x, y = px(pg), py(10 * math.log10(pg))
        f.append(circle(x, y, 5, fill=NEG, stroke=NEG, sw=1))
        f.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1" stroke-dasharray="3 3"/>'
                 % (x, y, x, oy, MUTED))
        f.append(text(px(pg), oy + 18, "×%d" % pg, 10.5, NEG, "middle", bold=True))
        bw = 150
        bx0 = min(x - 10, ox + aw - bw)        # не вилазити за праву межу поля
        f.append(fitbox(bx0, y - 48, bw, 38, lab,
                        size=10.5, fill="#eaf0fd", stroke=NEG, color=INK))

    # формула на полі
    f.append(fitbox(ox + 30, py(40) - 4, 250, 30, "виграш = 10·log₁₀(W_розш / W_дані)",
                    size=12, fill="#ffffff", stroke=NEG, color=INK))

    render(os.path.join(IMG, "processing-gain.svg"), W, H, *f,
           title="Виграш обробки: ширша смуга = вищий сигнал над завадою")

def fig_tradeoff():
    W, H = 720, 320
    f = [text(W / 2, 28, "Що платимо за стійкість до глушіння", 16, INK, "middle", bold=True)]
    pay = [
        ("+ Стійкість до завад", "вузька завада псує лише частину —\nрешта проходить", "#eef6ef", FIELD),
        ("+ Скритність (LPI)", "сигнал нижчий за шум —\nважко виявити й підслухати", "#eef6ef", FIELD),
        ("− Широка смуга", "займаємо в N разів більше спектра,\nніж потрібно для самих даних", "#fdecea", POS),
        ("− Складність і синхронізація", "приймач має знати код/розклад\nі точно зловити фазу та час", "#fdecea", POS),
    ]
    y = 64
    for name, desc, fill, stroke in pay:
        f.append(rect(40, y, 280, 52, fill=fill, stroke=stroke, sw=1.7, rx=6))
        f.append(text(180, y + 30, name, 13, INK, "middle", bold=True))
        f.append(text(340, y + 20, desc.split("\n")[0], 11.5, INK, "start"))
        f.append(text(340, y + 37, desc.split("\n")[1], 11.5, MUTED, "start"))
        y += 62
    render(os.path.join(IMG, "tradeoff.svg"), W, H, *f)


# ── 6. Де працює: RC-керування й телеметрія ──────────────────────────────────
def fig_where():
    W, H = 720, 330
    f = [text(W / 2, 28, "Де це працює: керування й телеметрія під завадами", 15.5, INK, "middle", bold=True)]

    # земля
    gx, gy = 110, 230
    f.append(rect(gx - 70, gy - 30, 140, 70, fill="#eef3f9", stroke=LINE, sw=1.6, rx=8))
    f.append(text(gx, gy - 6, "наземний", 12, INK, "middle", bold=True))
    f.append(text(gx, gy + 12, "пульт", 12, INK, "middle"))

    # борт
    bx, by = 610, 230
    f.append(rect(bx - 70, by - 30, 140, 70, fill="#eef3f9", stroke=LINE, sw=1.6, rx=8))
    f.append(text(bx, by - 6, "борт", 12, INK, "middle", bold=True))
    f.append(text(bx, by + 12, "(дрон/модель)", 10.5, MUTED, "middle"))

    # канал керування вгору (RC) — FHSS
    f.append(arrow(gx + 72, by - 14, bx - 72, by - 14, color=FIELD, sw=2.4))
    f.append(text(W / 2, by - 22, "керування (RC) — стрибки частоти, FHSS", 11.5, FIELD, "middle", bold=True))

    # телеметрія вниз — DSSS/FHSS
    f.append(arrow(bx - 72, by + 18, gx + 72, by + 18, color=NEG, sw=2.4))
    f.append(text(W / 2, by + 34, "телеметрія вниз — розширений спектр", 11.5, NEG, "middle", bold=True))

    # завада посередині
    f.append('<rect x="%.1f" y="%.1f" width="120" height="56" rx="8" fill="#fdecea" stroke="%s" stroke-width="2"/>'
             % (W / 2 - 60, 78, POS))
    f.append(text(W / 2, 100, "завада / глушилка", 12, POS, "middle", bold=True))
    f.append(text(W / 2, 118, "на 2.4 ГГц", 10.5, POS, "middle"))
    f.append(arrow(W / 2, 134, W / 2, by - 30, color=POS, sw=1.6))
    f.append(text(W / 2 + 150, 150, "лінк тримається:", 11, INK, "middle", bold=True))
    f.append(text(W / 2 + 150, 166, "губиться частина,", 10.5, MUTED, "middle"))
    f.append(text(W / 2 + 150, 180, "не весь зв'язок", 10.5, MUTED, "middle"))

    render(os.path.join(IMG, "where.svg"), W, H, *f)


if __name__ == "__main__":
    fig_jamming()
    fig_fhss()
    fig_dsss()
    fig_pgain()
    fig_tradeoff()
    fig_where()
    print("OK: figures written to", IMG)
