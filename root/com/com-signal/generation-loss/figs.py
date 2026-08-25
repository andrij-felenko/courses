# -*- coding: utf-8 -*-
"""Фігури до теми «Втрата поколінь: накопичення похибки при копіюванні».
Запуск: python figs.py -> пише SVG у ./img/
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *
import math

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

WARN = "#d35400" # помаранчевий зауваження

# ── 1. Графік порівняння трьох типів копіювання ──────────────────────────────
def fig_analog_vs_digital_cascade():
    W, H = 780, 320
    f = [text(W / 2, 26, "Поведінка якості сигналу при послідовному копіюванні",
              size=15, bold=True)]

    x0, y0 = 80, 250
    w_axis, h_axis = 640, 190

    # Осі
    f.append(line(x0, y0, x0 + w_axis + 15, y0, color=INK, sw=1.6))
    f.append(line(x0, y0, x0, y0 - h_axis - 15, color=INK, sw=1.6))
    f.append(text(x0 + w_axis + 10, y0 + 22, "Покоління (N)", size=11, color=MUTED, italic=True, anchor="end"))
    f.append(text(x0 - 15, y0 - h_axis - 10, "Якість (SNR / PSNR, дБ)", size=11, color=MUTED, italic=True, anchor="start"))

    # Позначки осі X (Покоління 1..10)
    for gen in range(1, 11):
        x = x0 + (gen - 1) * (w_axis / 9.0)
        f.append(line(x, y0, x, y0 + 5, color=INK, sw=1.2))
        f.append(text(x, y0 + 18, str(gen), size=10, color=MUTED))

    # Позначки осі Y (дБ)
    for db_val, label in [(0, "0 дБ"), (0.33, "20 дБ"), (0.66, "40 дБ"), (1.0, "60 дБ")]:
        y = y0 - db_val * h_axis
        f.append(line(x0 - 5, y, x0, y, color=INK, sw=1.2))
        f.append(text(x0 - 10, y + 4, label, size=10, color=MUTED, anchor="end"))
        if db_val > 0:
            f.append(line(x0, y, x0 + w_axis, y, color="#e5e7eb", sw=1.0, dash="3,3"))

    # Лінія 1: Lossless digital (зелена, незмінна 60 дБ)
    y_lossless = y0 - 1.0 * h_axis
    f.append(line(x0, y_lossless, x0 + w_axis, y_lossless, color=FIELD, sw=2.5))
    f.append(circle(x0 + w_axis, y_lossless, 4, fill=FIELD))
    f.append(text(x0 + w_axis - 10, y_lossless - 10, "Цифрове точное копіювання (Lossless): 0 дБ втрат",
                  size=11, color=FIELD, bold=True, anchor="end"))

    # Лінія 2: Analog cascade (червона, log decay: 60 - 10*log10(N)*3)
    pts_analog = []
    for i in range(100):
        t = i / 99.0
        gen = 1 + t * 9.0
        loss_db = 10.0 * math.log10(gen) * 2.8
        snr = max(0.0, 60.0 - loss_db)
        x = x0 + t * w_axis
        y = y0 - (snr / 60.0) * h_axis
        pts_analog.append((x, y))
    poly_analog = " ".join("%.1f,%.1f" % p for p in pts_analog)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly_analog, POS))
    f.append(text(x0 + w_axis - 50, pts_analog[-1][1] + 20, "Аналоговий перезапис: шуми додаються (+3 дБ/покоління)",
                  size=11, color=POS, bold=True, anchor="end"))

    # Лінія 3: Lossy digital transcoding (помаранчева, ступені/спадання з плато)
    pts_lossy = []
    for i in range(100):
        t = i / 99.0
        gen = 1 + t * 9.0
        loss_db = 12.0 * (1.0 - math.exp(-gen / 2.5)) + gen * 0.8
        snr = max(0.0, 60.0 - loss_db)
        x = x0 + t * w_axis
        y = y0 - (snr / 60.0) * h_axis
        pts_lossy.append((x, y))
    poly_lossy = " ".join("%.1f,%.1f" % p for p in pts_lossy)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,3"/>' % (poly_lossy, WARN))
    f.append(text(x0 + w_axis - 100, pts_lossy[-1][1] - 12, "Цифрове стиснення з втратами (Lossy)",
                  size=11, color=WARN, bold=True, anchor="end"))

    f.append(text(W / 2, H - 12,
                  "Цифровий точно скопійований файл не змінюється · Аналогове копіювання накопичує шум постійно · Lossy кодек деградує від переквантування",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "analog-vs-digital-cascade.svg"), W, H, *f)


# ── 2. Шумова полиця та АЧХ в аналоговому каскаді ───────────────────────────
def fig_analog_noise_stack():
    W, H = 780, 260
    f = [text(W / 2, 24, "Накопичення шуму та спад високих частот в аналоговому каскаді",
              size=15, bold=True)]

    panel_w = 220
    panel_h = 160
    y_base = 210

    panels = [
        ("1-ше покоління (Оригінал)", 10, "#eaf6ef", FIELD),
        ("3-тє покоління (Дубль)", 30, "#fffbeb", WARN),
        ("10-те покоління (Копія копії)", 65, "#fef2f2", POS)
    ]

    for idx, (title, noise_h, bg_col, stroke_col) in enumerate(panels):
        px = 35 + idx * 245
        f.append(rect(px, y_base - panel_h, panel_w, panel_h, fill=bg_col, stroke=FIELD, sw=1.4))
        f.append(text(px + panel_w / 2, y_base - panel_h + 20, title, size=11, bold=True, color=stroke_col))

        ax_x0 = px + 20
        ax_y0 = y_base - 25
        ax_w = panel_w - 35
        ax_h = panel_h - 60
        f.append(line(ax_x0, ax_y0, ax_x0 + ax_w, ax_y0, color=INK, sw=1.2))
        f.append(line(ax_x0, ax_y0, ax_x0, ax_y0 - ax_h, color=INK, sw=1.2))
        f.append(text(ax_x0 + ax_w, ax_y0 + 14, "f (кГц)", size=9, color=MUTED, anchor="end"))
        f.append(text(ax_x0 - 5, ax_y0 - ax_h + 5, "Амплітуда", size=9, color=MUTED, anchor="start"))

        noise_y = ax_y0 - (noise_h / 80.0) * ax_h
        f.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" fill-opacity="0.25" stroke="none"/>' %
                 (ax_x0, noise_y, ax_w, ax_y0 - noise_y, stroke_col))
        f.append(line(ax_x0, noise_y, ax_x0 + ax_w, noise_y, color=stroke_col, sw=1.2, dash="3,2"))
        f.append(text(ax_x0 + 10, noise_y - 4, "Шум", size=9, color=stroke_col, bold=True))

        pts_sig = []
        for i in range(50):
            t = i / 49.0
            x = ax_x0 + t * ax_w
            roll_off = math.exp(-t * (idx * 0.8))
            tone = 0.7 * math.exp(-((t - 0.3) ** 2) / 0.008)
            val = (tone * roll_off) * (ax_h - 15)
            y = min(ax_y0 - val, noise_y)
            pts_sig.append((x, y))

        poly_sig = " ".join("%.1f,%.1f" % p for p in pts_sig)
        f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.0"/>' % (poly_sig, INK))

    f.append(text(W / 2, H - 10,
                  "З кожним перезаписом шумовий поріг зростає, а вищі частоти згасають через неідеальний тракт",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "analog-noise-stack.svg"), W, H, *f)


# ── 3. Цикл повторного перекодування ─────────────────────────────────────────
def fig_lossy_reencode_cycle():
    W, H = 780, 240
    f = [text(W / 2, 24, "Цикл втрати інформації при повторному стисненні з втратами",
              size=15, bold=True)]

    y_mid = 115

    b1_x, b1_w = 40, 130
    b2_x, b2_w = 210, 150
    b3_x, b3_w = 400, 160
    b4_x, b4_w = 600, 140

    f.append(rect(b1_x, y_mid - 35, b1_w, 70, fill="#eef2fb", stroke=FIELD, sw=1.5))
    f.append(mtext(b1_x + b1_w / 2, y_mid - 8, ["Стиснений файл", "Покоління N"], size=11, bold=True, color=INK))

    f.append(arrow(b1_x + b1_w, y_mid, b2_x, y_mid, color=INK, sw=1.6))

    f.append(rect(b2_x, y_mid - 35, b2_w, 70, fill="#f8fafc", stroke=FIELD, sw=1.5))
    f.append(mtext(b2_x + b2_w / 2, y_mid - 14, ["Декодування у PCM/RGB", "+ Зсув сітки / колір"], size=10, color=INK))

    f.append(arrow(b2_x + b2_w, y_mid, b3_x, y_mid, color=INK, sw=1.6))

    f.append(rect(b3_x, y_mid - 35, b3_w, 70, fill="#fef2f2", stroke=POS, sw=2.0))
    f.append(mtext(b3_x + b3_w / 2, y_mid - 14, ["ДКТ / Психоакустика", "+ ПОВТОРНЕ КВАНТУВАННЯ"], size=11, bold=True, color=POS))
    f.append(text(b3_x + b3_w / 2, y_mid + 20, "[ Похибка e_n+1 ]", size=10, color=POS, bold=True))

    f.append(arrow(b3_x + b3_w, y_mid, b4_x, y_mid, color=INK, sw=1.6))

    f.append(rect(b4_x, y_mid - 35, b4_w, 70, fill="#fffbeb", stroke=WARN, sw=1.5))
    f.append(mtext(b4_x + b4_w / 2, y_mid - 8, ["Стиснений файл", "Покоління N+1"], size=11, bold=True, color=WARN))

    curve_path = "M %.1f,%.1f C %.1f,%.1f %.1f,%.1f %.1f,%.1f" % (
        b4_x + b4_w / 2, y_mid + 35,
        b4_x + b4_w / 2, y_mid + 90,
        b1_x + b1_w / 2, y_mid + 90,
        b1_x + b1_w / 2, y_mid + 35
    )
    f.append('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-dasharray="5,4"/>' % (curve_path, MUTED))
    f.append(text(W / 2, y_mid + 78, "Повторне збереження / перекодування", size=10, color=MUTED, bold=True))

    f.append(text(W / 2, H - 12,
                  "Похибка квантування відкидає дрібні коефіцієнти при кожному збереженні, спотворюючи геометрію та хрому",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "lossy-reencode-cycle.svg"), W, H, *f)


# ── 4. Атрактор vs Дрейф ─────────────────────────────────────────────────────
def fig_codec_attractor_drift():
    W, H = 780, 300
    f = [text(W / 2, 26, "Стабілізація на атракторі проти неухильного дрейфу помилки",
              size=15, bold=True)]

    x0, y0 = 80, 240
    w_axis, h_axis = 640, 180

    f.append(line(x0, y0, x0 + w_axis + 15, y0, color=INK, sw=1.6))
    f.append(line(x0, y0, x0, y0 - h_axis - 15, color=INK, sw=1.6))
    f.append(text(x0 + w_axis + 10, y0 + 22, "Покоління (N)", size=11, color=MUTED, italic=True, anchor="end"))
    f.append(text(x0 - 15, y0 - h_axis - 10, "Якість (PSNR, дБ)", size=11, color=MUTED, italic=True, anchor="start"))

    for gen in range(1, 16):
        x = x0 + (gen - 1) * (w_axis / 14.0)
        f.append(line(x, y0, x, y0 + 5, color=INK, sw=1.2))
        f.append(text(x, y0 + 18, str(gen), size=10, color=MUTED))

    pts_attractor = []
    for i in range(100):
        t = i / 99.0
        gen = 1 + t * 14.0
        psnr = 45.0 - 5.0 * (1.0 - math.exp(-(gen - 1) / 0.8))
        x = x0 + t * w_axis
        y = y0 - (psnr / 50.0) * h_axis
        pts_attractor.append((x, y))
    poly_attractor = " ".join("%.1f,%.1f" % p for p in pts_attractor)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (poly_attractor, FIELD))
    f.append(text(x0 + w_axis - 20, pts_attractor[-1][1] - 10,
                  "Сценарій А: Вирівняна сітка блоків -> Стабільний атрактор", size=11, color=FIELD, bold=True, anchor="end"))

    pts_drift = []
    for i in range(100):
        t = i / 99.0
        gen = 1 + t * 14.0
        psnr = 45.0 - 3.5 * math.sqrt(gen - 1) - (gen - 1) * 0.8
        psnr = max(15.0, psnr)
        x = x0 + t * w_axis
        y = y0 - (psnr / 50.0) * h_axis
        pts_drift.append((x, y))
    poly_drift = " ".join("%.1f,%.1f" % p for p in pts_drift)
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,3"/>' % (poly_drift, POS))
    f.append(text(x0 + w_axis - 20, pts_drift[-1][1] + 20,
                  "Сценарій Б: Зсув сітки / зміна кодека -> Нескінченний дрейф", size=11, color=POS, bold=True, anchor="end"))

    f.append(text(W / 2, H - 12,
                  "Якщо сітка ДКТ та квантування збігаються, коефіцієнти перестають змінюватись; зсув на 1 піксель руйнує атрактор",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(IMG, "codec-attractor-drift.svg"), W, H, *f)


if __name__ == "__main__":
    fig_analog_vs_digital_cascade()
    fig_analog_noise_stack()
    fig_lossy_reencode_cycle()
    fig_codec_attractor_drift()
    print("Всі 4 фігури успішно згенеровано у ./img/")

