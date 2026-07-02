# -*- coding: utf-8 -*-
"""Фігури до статті «Sigma-delta АЦП» (book/electronics/analog/sigma-delta-adc).
Чотири фігури:
  loop.svg     — структура: суматор → інтегратор → 1-бітний компаратор → ЦАП у петлі
  shape.svg    — ідея noise shaping: шум витиснуто з робочої смуги вгору частотою
  stream.svg   — потік 1-бітів: середня густина одиниць = напруга на вході
  decimate.svg — два кроки після модулятора: цифровий ФНЧ + проріджування
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def render_notitle(path, w, h, *frags):
    """Як render(), але без заголовка-тексту (у book/ підписів-номерів немає)."""
    return render(path, w, h, *frags)


# ── 1. Петля модулятора ─────────────────────────────────────────────────────
def fig_loop():
    W, H = 720, 300
    f = []
    yc = 150
    # вхід
    f.append(text(40, yc - 12, "вхід", size=13, color=MUTED, anchor="middle"))
    f.append(text(40, yc + 8, "U(t)", size=14, color=INK, anchor="middle", bold=True))
    f.append(arrow(72, yc, 120, yc, color=INK, sw=2))
    # суматор (різниця)
    f.append(circle(140, yc, 20, fill="#ffffff", stroke=INK, sw=1.8))
    f.append(text(140, yc + 5, "−", size=22, color=NEG, anchor="middle", bold=True))
    f.append(text(118, yc - 26, "+", size=16, color=POS, anchor="middle", bold=True))
    f.append(arrow(160, yc, 210, yc, color=INK, sw=2))
    # інтегратор (накопичувач)
    b1 = fitbox(210, yc - 32, 130, 64, "інтегратор\n(накопичує\nрізницю)", size=13, fill="#eafaf1", stroke=FIELD)
    f.append(b1)
    f.append(arrow(340, yc, 400, yc, color=INK, sw=2))
    # компаратор (1-бітний АЦП)
    b2 = fitbox(400, yc - 32, 120, 64, "компаратор\n1 біт", size=13, fill="#f4f6f8", stroke=LINE)
    f.append(b2)
    f.append(arrow(520, yc, 600, yc, color=INK, sw=2))
    # вихід
    f.append(text(660, yc - 12, "потік бітів", size=12, color=MUTED, anchor="middle"))
    f.append(text(660, yc + 9, "1 0 1 1 0 1", size=14, color=INK, anchor="middle", bold=True))
    # зворотний звʼязок: відгалуження після компаратора вниз і назад у суматор
    f.append(line(560, yc, 560, 250, color=INK, sw=1.8))
    f.append(line(560, 250, 140, 250, color=INK, sw=1.8))
    f.append(arrow(140, 250, 140, yc + 20, color=INK, sw=1.8))
    b3 = fitbox(300, 228, 130, 44, "1-бітний ЦАП", size=13, fill="#fdecea", stroke=POS)
    f.append(b3)
    f.append(text(560, 245, "копія виходу", size=11, color=MUTED, anchor="end"))
    render_notitle(os.path.join(IMG, "loop.svg"), W, H, *f)


# ── 2. Noise shaping: спектр ────────────────────────────────────────────────
def fig_shape():
    W, H = 720, 340
    f = []
    x0, y0 = 70, 270          # початок осей
    xmax, ymax = 670, 50
    # осі
    f.append(arrow(x0, y0, xmax, y0, color=INK, sw=1.8))
    f.append(arrow(x0, y0, x0, ymax, color=INK, sw=1.8))
    f.append(text(xmax, y0 + 24, "частота", size=13, color=MUTED, anchor="end"))
    f.append(text(x0 - 8, ymax + 4, "густина шуму", size=12, color=MUTED, anchor="end"))
    # межа робочої смуги
    fb = x0 + 130
    f.append(line(fb, y0, fb, ymax + 10, color=MUTED, sw=1.4, dash="5,5"))
    f.append(text(fb, ymax - 4, "край смуги сигналу", size=12, color=MUTED, anchor="middle"))
    # частота вибірки (праворуч)
    fs = xmax - 30
    f.append(line(fs, y0, fs, ymax + 60, color=MUTED, sw=1.4, dash="5,5"))
    f.append(text(fs, ymax + 52, "f_д / 2", size=12, color=MUTED, anchor="middle"))
    # крива шуму без формування (горизонтальна) — пунктир
    flat_y = 200
    f.append(line(x0, flat_y, fs, flat_y, color=NEG, sw=2, dash="6,4"))
    f.append(text(x0 + 250, flat_y - 8, "без формування: рівний шум", size=12, color=NEG, anchor="middle"))
    # крива з noise shaping: низько в смузі, круто росте вгору
    import math
    pts = []
    for i in range(0, 101):
        t = i / 100.0
        xx = x0 + t * (fs - x0)
        # майже нуль зліва, круте зростання праворуч
        val = 250 - 200 * (t ** 2.2)
        pts.append((xx, val))
    path = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, POS))
    f.append(text(fb + 120, 110, "з формуванням:", size=13, color=POS, anchor="middle", bold=True))
    f.append(text(fb + 120, 128, "шум витиснуто вгору", size=12, color=POS, anchor="middle"))
    # зелене виділення: тихо в робочій смузі
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.12"/>' % (x0, 215, fb - x0, y0 - 215, FIELD))
    f.append(text((x0 + fb) / 2, 245, "тут тихо", size=12, color=FIELD, anchor="middle", bold=True))
    render_notitle(os.path.join(IMG, "shape.svg"), W, H, *f)


# ── 3. Потік 1-бітів ↔ напруга ──────────────────────────────────────────────
def fig_stream():
    W, H = 720, 360
    f = []
    # три рівні входу й відповідна густина одиниць
    rows = [
        ("вхід низько", "0 1 0 0 0 1 0 0 0 1 0 0", "мало одиниць", 0.25),
        ("вхід посередині", "0 1 0 1 1 0 1 0 0 1 1 0", "половина одиниць", 0.50),
        ("вхід високо", "1 1 0 1 1 1 0 1 1 1 1 0", "майже всі одиниці", 0.83),
    ]
    y = 60
    for label, bits, note, frac in rows:
        f.append(text(120, y, label, size=13, color=INK, anchor="middle", bold=True))
        # ряд бітів
        bx = 230
        for ch in bits.split():
            col = POS if ch == "1" else MUTED
            fill = "#fdecea" if ch == "1" else "#eef1f4"
            f.append(rect(bx, y - 16, 22, 24, fill=fill, stroke=col, sw=1.4, rx=4))
            f.append(text(bx + 11, y + 1, ch, size=13, color=col, anchor="middle", bold=True))
            bx += 26
        # стовпчик-індикатор густини
        gx = bx + 30
        f.append(rect(gx, y - 16, 120, 24, fill="#ffffff", stroke=LINE, sw=1.2, rx=4))
        f.append(rect(gx, y - 16, 120 * frac, 24, fill=FIELD, stroke="none", rx=4))
        f.append(text(gx + 130, y + 1, note, size=12, color=MUTED, anchor="start"))
        y += 100
    f.append(text(W / 2, 330, "Середня частка одиниць у потоці = рівень входу.", size=13, color=INK, anchor="middle"))
    render_notitle(os.path.join(IMG, "stream.svg"), W, H, *f)


# ── 4. Децимація: ФНЧ + проріджування ───────────────────────────────────────
def fig_decimate():
    W, H = 720, 240
    f = []
    yc = 120
    f.append(text(70, yc - 14, "потік 1-біт", size=12, color=MUTED, anchor="middle"))
    f.append(text(70, yc + 8, "f_д висока", size=13, color=INK, anchor="middle", bold=True))
    f.append(arrow(120, yc, 180, yc, color=INK, sw=2))
    b1 = fitbox(180, yc - 36, 150, 72, "цифровий ФНЧ\n(усереднює,\nприбирає шум\nзгори)", size=12, fill="#eafaf1", stroke=FIELD)
    f.append(b1)
    f.append(arrow(330, yc, 400, yc, color=INK, sw=2))
    b2 = fitbox(400, yc - 36, 150, 72, "проріджування\n↓ N\n(беремо кожен\nN-й відлік)", size=12, fill="#f4f6f8", stroke=LINE)
    f.append(b2)
    f.append(arrow(550, yc, 610, yc, color=INK, sw=2))
    f.append(text(665, yc - 14, "багатобітні", size=12, color=MUTED, anchor="middle"))
    f.append(text(665, yc + 8, "слова", size=13, color=INK, anchor="middle", bold=True))
    f.append(text(665, yc + 28, "f_вих низька", size=11, color=MUTED, anchor="middle"))
    render_notitle(os.path.join(IMG, "decimate.svg"), W, H, *f)


# ── 5. |NTF| проти частоти: нуль на DC, highpass, порядки 1 і 2 ──────────────
def fig_ntf():
    import math
    W, H = 720, 360
    f = []
    x0, y0 = 80, 300          # початок осей (низ-ліво)
    xmax, ytop = 670, 50
    # осі
    f.append(arrow(x0, y0, xmax, y0, color=INK, sw=1.8))
    f.append(arrow(x0, y0, x0, ytop, color=INK, sw=1.8))
    f.append(text(xmax, y0 + 24, "частота  f / f_д", size=13, color=MUTED, anchor="end"))
    f.append(text(x0 - 10, ytop - 2, "|NTF|", size=13, color=MUTED, anchor="end"))
    # вісь частот: 0 ... 0.5 (f_д/2)
    fhalf = xmax - 20
    # межа робочої смуги (вузька, ліворуч)
    fb = x0 + 95
    f.append(line(fb, y0, fb, ytop + 10, color=MUTED, sw=1.3, dash="5,5"))
    f.append(text(fb, ytop + 2, "край смуги сигналу", size=12, color=MUTED, anchor="middle"))
    f.append(text(fhalf, y0 + 24, "f_д/2", size=12, color=MUTED, anchor="middle"))
    # затінена робоча смуга
    f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity="0.10"/>'
             % (x0, ytop + 10, fb - x0, y0 - ytop - 10, FIELD))
    f.append(text((x0 + fb) / 2, y0 - 12, "робоча", size=11, color=FIELD, anchor="middle", bold=True))
    f.append(text((x0 + fb) / 2, y0 + 0, "смуга", size=11, color=FIELD, anchor="middle", bold=True))

    # масштаб: |NTF| = 2|sin(pi f / fд)|, fд=1; f від 0 до 0.5 -> 2 sin(pi f) від 0 до 2
    def curve(power, col, sw):
        pts = []
        for i in range(0, 121):
            ff = 0.5 * i / 120.0                 # f/fд від 0 до 0.5
            base = 2.0 * math.sin(math.pi * ff)  # |1 - e^-j...| = 2 sin(pi f)
            val = base ** power                  # порядок L -> степінь
            xx = x0 + (ff / 0.5) * (fhalf - x0)
            # вертикаль: 0 -> y0 (низ), 2^power (макс) -> ytop
            yy = y0 - (val / (2.0 ** power)) * (y0 - ytop)
            pts.append((xx, yy))
        path = "M %.1f %.1f " % pts[0] + " ".join("L %.1f %.1f" % p for p in pts[1:])
        f.append('<path d="%s" fill="none" stroke="%s" stroke-width="%.1f"/>' % (path, col, sw))

    curve(1, NEG, 2.4)        # перший порядок
    curve(2, POS, 2.6)        # другий порядок (крутіший)
    # підписи кривих
    f.append(text(fhalf - 70, 120, "2-й порядок", size=13, color=POS, anchor="middle", bold=True))
    f.append(text(fhalf - 70, 138, "(1−z⁻¹)²", size=12, color=POS, anchor="middle"))
    f.append(text(fhalf - 150, 210, "1-й порядок", size=13, color=NEG, anchor="middle", bold=True))
    f.append(text(fhalf - 150, 228, "(1−z⁻¹)", size=12, color=NEG, anchor="middle"))
    # точка нуля на DC
    f.append(circle(x0, y0, 4, fill=INK, stroke=INK, sw=1))
    f.append(text(x0 + 6, y0 - 8, "нуль на f=0", size=11, color=INK, anchor="start"))
    render_notitle(os.path.join(IMG, "ntf.svg"), W, H, *f)


# ── 6. SNR проти OSR (log-log): нахил за порядком ───────────────────────────
def fig_snr_osr():
    import math
    W, H = 720, 380
    f = []
    x0, y0 = 90, 320
    xmax, ytop = 660, 50
    f.append(arrow(x0, y0, xmax, y0, color=INK, sw=1.8))
    f.append(arrow(x0, y0, x0, ytop, color=INK, sw=1.8))
    f.append(text(xmax, y0 + 24, "OSR (октав, log₂)", size=13, color=MUTED, anchor="end"))
    f.append(text(x0 - 12, ytop - 2, "виграш SNR, дБ", size=12, color=MUTED, anchor="start"))
    # вісь X: октави 0..14; вісь Y: дБ 0..220
    octmax = 14.0
    dbmax = 230.0

    def X(oct_):
        return x0 + (oct_ / octmax) * (xmax - x0)

    def Y(db):
        return y0 - (db / dbmax) * (y0 - ytop)

    # сітка октав
    for o in range(2, 15, 2):
        f.append(line(X(o), y0, X(o), y0 + 5, color=MUTED, sw=1.2))
        f.append(text(X(o), y0 + 20, str(o), size=11, color=MUTED, anchor="middle"))

    # лінії: виграш = (6L+3)*октав для L=0(просто OSR:3дБ),1,2,3
    orders = [(0, 3, MUTED, "порядок 0: 3 дБ/окт"),
              (1, 9, NEG, "1-й: 9 дБ/окт"),
              (2, 15, FIELD, "2-й: 15 дБ/окт"),
              (3, 21, POS, "3-й: 21 дБ/окт")]
    for L, slope, col, lab in orders:
        x1, y1 = X(0.0), Y(0.0)
        # обрізаємо лінію по верхній межі дБ
        oc_top = min(octmax, dbmax / slope)
        x2, y2 = X(oc_top), Y(slope * oc_top)
        f.append(line(x1, y1, x2, y2, color=col, sw=2.4 if L else 2.0,
                      dash=None if L else "6,4"))
        # підпис у кінці лінії
        f.append(text(x2 + 6, y2 + 4, lab, size=12, color=col, anchor="start", bold=(L > 0)))
    f.append(text((x0 + xmax) / 2, ytop - 18, "Кожен порядок додає +6 дБ/октаву до нахилу", size=12, color=INK, anchor="middle"))
    render_notitle(os.path.join(IMG, "snr-osr.svg"), W, H, *f)


if __name__ == "__main__":
    fig_loop()
    fig_shape()
    fig_stream()
    fig_decimate()
    fig_ntf()
    fig_snr_osr()
    print("OK: 6 фігур у", IMG)
