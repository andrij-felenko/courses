# -*- coding: utf-8 -*-
"""Фігури до теми «Лінійне кодування».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG, exist_ok=True)


# ── допоміжне: полілінія й цифрова хвиля з майже прямовисними фронтами ───────
def polyline(pts, color=INK, sw=2.0, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    pd = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return ('<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>'
            % (pd, color, sw, d))


def levels_wave(x0, ub, samples, y_of, color=INK, sw=2.2):
    """Хвиля за списком рівнів на кожен слот: samples[i] = ключ у y_of.
    Прямі полички + вертикальні перепади на межах слотів."""
    seq = []
    prev = None
    for i, s in enumerate(samples):
        y = y_of[s]
        x = x0 + i * ub
        if prev is not None and prev != y:
            seq.append((x, prev))       # вертикальний перепад на межі
        seq.append((x, y))
        seq.append((x + ub, y))
        prev = y
    return polyline(seq, color=color, sw=sw)


def slot_grid(x0, ub, n, ytop, ybot, color=MUTED):
    """Тонкі вертикальні межі слотів (пунктир) для читабельності тактів."""
    out = []
    for i in range(n + 1):
        x = x0 + i * ub
        out.append(line(x, ytop, x, ybot, color=color, sw=0.8, dash="2,4"))
    return out


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 1 — та сама послідовність бітів чотирма кодами (NRZ / RZ / Манчестер / AMI)
# ════════════════════════════════════════════════════════════════════════════
def fig_codes():
    BITS = [1, 0, 1, 1, 0, 0, 0, 1]
    W, H = 760, 470
    x0, wv = 132, 500
    ub = wv / len(BITS)
    els = [text(W / 2, 24, "Один потік бітів — чотири лінійні коди", size=15, bold=True)]

    # шапка з бітами над усіма доріжками
    for i, b in enumerate(BITS):
        els.append(text(x0 + (i + 0.5) * ub, 46, str(b), size=13, bold=True, color=INK))
    els.append(text(x0 - 12, 46, "біти:", size=12, color=MUTED, anchor="end"))

    lane_h = 40           # висота розмаху рівнів у доріжці
    gap = 26              # проміжок між доріжками
    top = 66

    def track(row, name, mid_line_dash=False):
        yc = top + row * (lane_h + gap) + lane_h / 2
        yhi, ylo, ymid = yc - lane_h / 2, yc + lane_h / 2, yc
        # межі слотів
        for f in slot_grid(x0, ub, len(BITS), yhi - 6, ylo + 6):
            els.append(f)
        els.append(mtext(x0 - 12, yc - 6, name.split("\n"), size=11.5, color=INK, anchor="end", bold=True))
        return yhi, ylo, ymid

    # ── 1) NRZ: 1→високо, 0→низько; рівень тримається весь слот ──
    yhi, ylo, ymid = track(0, "NRZ")
    els.append(levels_wave(x0, ub, [("hi" if b else "lo") for b in BITS],
                           {"hi": yhi, "lo": ylo}, color=INK))
    els.append(text(x0 + wv + 8, ymid + 4, "рівень = біт", size=10.5, color=MUTED, anchor="start"))

    # ── 2) RZ: 1→імпульс у першій половині й назад до 0; 0→нуль ──
    yhi, ylo, ymid = track(1, "RZ")
    seq = []
    for i, b in enumerate(BITS):
        x = x0 + i * ub
        if b:
            seq += [(x, ymid), (x, yhi), (x + ub / 2, yhi), (x + ub / 2, ymid), (x + ub, ymid)]
        else:
            seq += [(x, ymid), (x + ub, ymid)]
    els.append(polyline(seq, color=INK, sw=2.2))
    els.append(text(x0 + wv + 8, ymid + 4, "1 = імпульс", size=10.5, color=MUTED, anchor="start"))

    # ── 3) Манчестер: у СЕРЕДИНІ кожного слоту завжди перехід (конвенція IEEE: 1 = ↑) ──
    yhi, ylo, ymid = track(2, "Манчестер")
    seq = []
    for i, b in enumerate(BITS):
        x = x0 + i * ub
        if b:                        # 1: низько→високо в середині
            a, c = ylo, yhi
        else:                        # 0: високо→низько в середині
            a, c = yhi, ylo
        # можливий вертикальний перескок на початку слоту, якщо рівень не збігся
        if seq and seq[-1][1] != a:
            seq.append((x, seq[-1][1]))
            seq.append((x, a))
        seq += [(x, a), (x + ub / 2, a), (x + ub / 2, c), (x + ub, c)]
    els.append(polyline(seq, color=FIELD, sw=2.4))
    els.append(text(x0 + wv + 8, ymid + 4, "перехід у центрі", size=10.5, color=FIELD, anchor="start", bold=True))

    # ── 4) AMI: 0 = нуль; 1 = імпульс, полярність чергується +,−,+,− ──
    yhi, ylo, ymid = track(3, "AMI")
    sign = 1
    seq = [(x0, ymid)]
    for i, b in enumerate(BITS):
        x = x0 + i * ub
        if b:
            y = yhi if sign > 0 else ylo
            seq += [(x, ymid), (x, y), (x + ub, y), (x + ub, ymid)]
            sign = -sign
        else:
            seq += [(x, ymid), (x + ub, ymid)]
    els.append(polyline(seq, color=INK, sw=2.2))
    # позначки полярності над одиницями
    sgn = 1
    for i, b in enumerate(BITS):
        if b:
            els.append(text(x0 + (i + 0.5) * ub, ymid - lane_h / 2 - 4,
                            "+" if sgn > 0 else "−", size=12, bold=True,
                            color=(POS if sgn > 0 else NEG)))
            sgn = -sgn
    els.append(text(x0 + wv + 8, ymid + 4, "1 чергує ±", size=10.5, color=MUTED, anchor="start"))

    render(os.path.join(IMG, "codes.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 2 — біда NRZ на довгій серії: лінія німіє, приймач пливе; Манчестер рятує
# ════════════════════════════════════════════════════════════════════════════
def fig_selfclock():
    BITS = [1, 0, 1, 1, 1, 1, 1, 1, 1, 0]
    W, H = 760, 360
    x0, wv = 150, 540
    ub = wv / len(BITS)
    els = [text(W / 2, 24, "Чому код мусить сам нести такт: довга серія однакових бітів", size=15, bold=True)]

    for i, b in enumerate(BITS):
        els.append(text(x0 + (i + 0.5) * ub, 46, str(b), size=13, bold=True, color=INK))
    els.append(text(x0 - 12, 46, "біти:", size=12, color=MUTED, anchor="end"))

    lane_h, gap, top = 46, 40, 66

    # ── NRZ: сім одиниць поспіль — рівний майданчик, жодного переходу ──
    yc = top + lane_h / 2
    yhi, ylo = yc - lane_h / 2, yc + lane_h / 2
    for f in slot_grid(x0, ub, len(BITS), yhi - 6, ylo + 6):
        els.append(f)
    els.append(mtext(x0 - 12, yc - 6, ["NRZ"], size=11.5, color=INK, anchor="end", bold=True))
    els.append(levels_wave(x0, ub, [("hi" if b else "lo") for b in BITS],
                           {"hi": yhi, "lo": ylo}, color=INK))
    # німа ділянка (індекси 2..8 — сім одиниць)
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10"/>'
               % (x0 + 2 * ub, yhi - 6, 7 * ub, lane_h + 12, POS))
    els.append(text(x0 + 5.5 * ub, ylo + 20, "лінія стоїть — жодного фронту, лічильник приймача пливе",
                    size=11.5, color=POS, anchor="middle"))

    # ── Манчестер: у кожному слоті гарантований перехід у центрі ──
    yc = top + (lane_h + gap) + lane_h / 2
    yhi, ylo = yc - lane_h / 2, yc + lane_h / 2
    for f in slot_grid(x0, ub, len(BITS), yhi - 6, ylo + 6):
        els.append(f)
    els.append(mtext(x0 - 12, yc - 6, ["Манчестер"], size=11.5, color=INK, anchor="end", bold=True))
    seq = []
    for i, b in enumerate(BITS):
        x = x0 + i * ub
        a, c = (ylo, yhi) if b else (yhi, ylo)
        if seq and seq[-1][1] != a:
            seq.append((x, seq[-1][1])); seq.append((x, a))
        seq += [(x, a), (x + ub / 2, a), (x + ub / 2, c), (x + ub, c)]
    els.append(polyline(seq, color=FIELD, sw=2.4))
    # стрілки-мітки центральних переходів
    for i in range(len(BITS)):
        xm = x0 + (i + 0.5) * ub
        els.append(circle(xm, yc, 2.6, fill=FIELD, stroke=FIELD, sw=1))
    els.append(text(x0 + wv / 2, ylo + 20,
                    "перехід у центрі кожного біта — приймач синхронізується щотакту",
                    size=11.5, color=FIELD, anchor="middle", bold=True))

    render(os.path.join(IMG, "self-clock.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 3 — розмін: що код дає і чим платить (три властивості vs ціна смуги)
# ════════════════════════════════════════════════════════════════════════════
def fig_tradeoff():
    W, H = 760, 340
    els = [text(W / 2, 24, "Що купує лінійний код і чим платить", size=15, bold=True)]

    # три бажані властивості (ліворуч) → код (центр) → ціна (праворуч)
    cx = W / 2
    box_w, box_h = 190, 46
    # центральний блок «лінійний код»
    els.append(fitbox(cx - 95, 150, 190, 60, "ЛІНІЙНИЙ КОД\nперетасування бітів",
                      size=13, fill="#eafaf0", stroke=FIELD, bold=True))

    wants = [
        ("самотактовість\n(переходи для CDR)", 70),
        ("нульова постійна\nскладова (баланс)", 150),
        ("мітки межі / контроль\n(K-коди)", 230),
    ]
    lx = 40
    for lab, yy in wants:
        els.append(fitbox(lx, yy - 22, 200, 46, lab, size=11, fill=FILL, stroke=NEG, color=NEG, bold=True))
        els.append(arrow(lx + 200, yy, cx - 96, 180 if yy == 150 else (172 if yy < 150 else 188),
                         color=NEG, sw=1.6))

    costs = [
        ("ширша смуга / вища\nчастота лінії", 110),
        ("накладні біти\n(8→10 = +25%)", 190),
    ]
    rx = W - 240
    for lab, yy in costs:
        els.append(fitbox(rx, yy - 22, 200, 46, lab, size=11, fill=FILL, stroke=POS, color=POS, bold=True))
        els.append(arrow(cx + 96, 175 if yy < 150 else 185, rx, yy, color=POS, sw=1.6))

    els.append(text(cx, 300,
                    "ліворуч — що потік отримує; праворуч — чим за це платять шириною й бітами",
                    size=11.5, color=MUTED))
    render(os.path.join(IMG, "tradeoff.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 4 (hist) — чому барабан вимагав DC-вільного коду:
#   головка → трансформатор → підсилювач. Трансформатор бачить лише ЗМІНИ.
#   Довга серія однакових бітів у NRZ дає рівну поличку → трансформатор її гасить.
#   Фазове кодування тримає перехід у кожному біті → трансформатор завжди «бачить».
# ════════════════════════════════════════════════════════════════════════════
def fig_drum_transformer():
    W, H = 780, 430
    els = [text(W / 2, 26, "Чому магнітний барабан вимагав коду без постійної складової", size=15, bold=True)]

    # ── верхній ряд: ланцюг зчитування головка → трансформатор → підсилювач ──
    yrow = 92
    els.append(fitbox(40, yrow - 30, 150, 60, "барабан\n(головка читає)", size=11.5,
                      fill="#eef2f7", stroke=INK, bold=True))
    els.append(arrow(192, yrow, 250, yrow, color=INK, sw=1.8))
    # трансформатор — дві котушки
    tx = 300
    els.append(rect(tx - 52, yrow - 34, 104, 68, fill=FILL, stroke=NEG, sw=2))
    els.append(line(tx - 8, yrow - 30, tx - 8, yrow + 30, color=NEG, sw=2))
    els.append(line(tx + 8, yrow - 30, tx + 8, yrow + 30, color=NEG, sw=2))
    for dy in (-22, -11, 0, 11, 22):
        els.append(line(tx - 26, yrow + dy, tx - 8, yrow + dy, color=NEG, sw=1.6))
        els.append(line(tx + 8, yrow + dy, tx + 26, yrow + dy, color=NEG, sw=1.6))
    els.append(text(tx, yrow + 52, "трансформатор", size=11.5, color=NEG, bold=True))
    els.append(text(tx, yrow + 68, "пропускає лише ЗМІНИ", size=10.5, color=NEG))
    els.append(arrow(tx + 52, yrow, tx + 110, yrow, color=INK, sw=1.8))
    els.append(fitbox(tx + 112, yrow - 26, 130, 52, "підсилювач →\nтригер", size=11.5,
                      fill="#eef2f7", stroke=INK, bold=True))

    # ── два потоки-приклади під ланцюгом ──
    BITS = [1, 1, 1, 1, 1, 1, 1, 1]
    x0, wv = 210, 470
    ub = wv / len(BITS)
    lane_h = 40

    def bits_header(y):
        for i, b in enumerate(BITS):
            els.append(text(x0 + (i + 0.5) * ub, y, str(b), size=12, bold=True, color=INK))
        els.append(text(x0 - 10, y, "вісім одиниць:", size=11, color=MUTED, anchor="end"))

    bits_header(196)

    # NRZ: рівна поличка — на виході трансформатора майже нічого
    yc = 236
    yhi, ylo = yc - lane_h / 2, yc + lane_h / 2
    for f in slot_grid(x0, ub, len(BITS), yhi - 6, ylo + 6):
        els.append(f)
    els.append(text(x0 - 10, yc - 4, "NRZ", size=11.5, color=INK, anchor="end", bold=True))
    els.append(text(x0 - 10, yc + 12, "на головці", size=9.5, color=MUTED, anchor="end"))
    els.append(levels_wave(x0, ub, [("hi") for _ in BITS], {"hi": yhi, "lo": ylo}, color=INK))
    els.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.10"/>'
               % (x0, yhi - 6, wv, lane_h + 12, POS))
    # після трансформатора — майже пряма на нулі
    els.append(line(x0, yc + lane_h + 6, x0 + wv, yc + lane_h + 6, color=POS, sw=2.2, dash="1,5"))
    els.append(text(x0 + wv + 8, yc, "рівно →", size=10.5, color=POS, anchor="start"))
    els.append(text(x0 + wv + 8, yc + lane_h + 10, "нічого", size=10.5, color=POS, anchor="start", bold=True))

    # Фазове кодування: перехід у кожному біті — трансформатор усе пропускає
    yc = 340
    yhi, ylo = yc - lane_h / 2, yc + lane_h / 2
    for f in slot_grid(x0, ub, len(BITS), yhi - 6, ylo + 6):
        els.append(f)
    els.append(text(x0 - 10, yc - 4, "фазове", size=11.5, color=FIELD, anchor="end", bold=True))
    els.append(text(x0 - 10, yc + 12, "кодування", size=11.5, color=FIELD, anchor="end", bold=True))
    seq = []
    for i, _ in enumerate(BITS):
        x = x0 + i * ub
        a, c = ylo, yhi
        if seq and seq[-1][1] != a:
            seq.append((x, seq[-1][1])); seq.append((x, a))
        seq += [(x, a), (x + ub / 2, a), (x + ub / 2, c), (x + ub, c)]
    els.append(polyline(seq, color=FIELD, sw=2.4))
    for i in range(len(BITS)):
        els.append(circle(x0 + (i + 0.5) * ub, yc, 2.6, fill=FIELD, stroke=FIELD, sw=1))
    els.append(text(x0 + wv + 8, yc, "усе →", size=10.5, color=FIELD, anchor="start"))
    els.append(text(x0 + wv + 8, yc + 16, "проходить", size=10.5, color=FIELD, anchor="start", bold=True))

    els.append(text(W / 2, 414,
                    "трансформатор глухий до сталого рівня — тож дані мусили самі весь час мінятися",
                    size=11.5, color=MUTED))
    render(os.path.join(IMG, "drum-transformer.svg"), W, H, *els)


# ════════════════════════════════════════════════════════════════════════════
# ФІГУРА 5 (hist) — дві конвенції на тому самому потоці:
#   Томас 1949 (низько-високо = 0)  ↔  IEEE 802.3 (низько-високо = 1) — дзеркала.
# ════════════════════════════════════════════════════════════════════════════
def fig_two_conventions():
    BITS = [1, 0, 1, 1, 0]
    W, H = 760, 330
    x0, wv = 190, 400
    ub = wv / len(BITS)
    lane_h, gap, top = 46, 54, 74
    els = [text(W / 2, 26, "Одні біти — дві дзеркальні конвенції манчестерського коду", size=15, bold=True)]

    for i, b in enumerate(BITS):
        els.append(text(x0 + (i + 0.5) * ub, 50, str(b), size=14, bold=True, color=INK))
    els.append(text(x0 - 12, 50, "біти:", size=12, color=MUTED, anchor="end"))

    def draw(row, name, one_up, note, note_color):
        yc = top + row * (lane_h + gap) + lane_h / 2
        yhi, ylo = yc - lane_h / 2, yc + lane_h / 2
        for f in slot_grid(x0, ub, len(BITS), yhi - 6, ylo + 6):
            els.append(f)
        els.append(mtext(x0 - 12, yc - 4, name.split("\n"), size=11.5, color=INK, anchor="end", bold=True))
        seq = []
        for i, b in enumerate(BITS):
            x = x0 + i * ub
            # one_up=True: 1 = низько→високо; one_up=False: 1 = високо→низько
            if (b == 1) == one_up:
                a, c = ylo, yhi
            else:
                a, c = yhi, ylo
            if seq and seq[-1][1] != a:
                seq.append((x, seq[-1][1])); seq.append((x, a))
            seq += [(x, a), (x + ub / 2, a), (x + ub / 2, c), (x + ub, c)]
        els.append(polyline(seq, color=FIELD, sw=2.4))
        els.append(text(x0 + wv + 10, yc + 4, note, size=11, color=note_color, anchor="start", bold=True))
        return yc

    draw(0, "Томас\n1949", one_up=False, note="низько-високо = 0", note_color=NEG)
    draw(1, "IEEE 802.3\n(Ethernet)", one_up=True, note="низько-високо = 1", note_color=POS)

    els.append(text(W / 2, H - 16,
                    "та сама механіка «дивись на перехід» — просто дзеркальне правило; інвертуй сигнал і одна стає іншою",
                    size=11, color=MUTED))
    render(os.path.join(IMG, "two-conventions.svg"), W, H, *els)


if __name__ == "__main__":
    fig_codes()
    fig_selfclock()
    fig_tradeoff()
    fig_drum_transformer()
    fig_two_conventions()
    print("OK: figures written to", IMG)
