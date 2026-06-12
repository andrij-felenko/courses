# -*- coding: utf-8 -*-
"""
Фігури для вставки 🔌 «Бузер активний і пасивний: коли ШІМ стає звуком»
(до теми §4.7.1 «ШІМ: „вдавати" аналог цифровою ніжкою»).

fig-25-1c-1-active-vs-passive.svg  → Рис. 4.7.1c.1
fig-25-1c-2-wiring-and-signal.svg  → Рис. 4.7.1c.2

Імпортує спільний kit; примітиви з svgkit — НЕ переписуються тут.
"""
import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '_tools'))
from svgkit import *  # noqa: F401,F403

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)

# ── локальні кольори, узгоджені з палітрою figs.py розділу ──────────────────
RED   = "#c0271e"
BLUE  = "#1f47b5"
GREEN = "#1f8a3b"
GREY  = "#8a8a8a"
LRED  = "#fbecec"
LBLUE = "#e9eefb"
LGRN  = "#eef6ef"
LAMB  = "#fff6e0"
GOLD  = "#caa24a"
FAINT = "#e4e4e4"
METAL = "#9a9aa0"


def _pwm_wave(x, y_hi, y_lo, period_w, duty, n_periods, col=BLUE, sw=2.2):
    """Меандр: n_periods прямокутних імпульсів зі скрипт-кроком duty (0..1)."""
    pts = []
    cx = x
    pts.append((cx, y_lo))
    for _ in range(n_periods):
        hi_w = period_w * duty
        lo_w = period_w * (1 - duty)
        pts += [(cx, y_hi), (cx + hi_w, y_hi), (cx + hi_w, y_lo), (cx + period_w, y_lo)]
        cx += period_w
    # побудова через polyline
    from svgkit import esc as _esc
    pts_str = " ".join(f"{px:.1f},{py:.1f}" for px, py in pts)
    return (f'<polyline points="{pts_str}" fill="none" stroke="{col}" '
            f'stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"/>\n')


def _dc_line(x1, y, x2, col=RED, sw=2.4):
    """Пряма горизонтальна лінія (рівень DC/HIGH)."""
    return line(x1, y, x2, y, color=col, sw=sw)


def _membrane_symbol(cx, cy, r=28, fill="#f4f6f8", stroke_col=METAL):
    """Спрощений символ п'єзопластини: велике коло + сектор кераміки."""
    frags = []
    # металевий диск
    frags.append(circle(cx, cy, r, fill=fill, stroke=stroke_col, sw=2))
    # сектор кераміки (верхня половина — темніша)
    # реалізуємо як шляхову дугу
    x1 = cx - r
    x2 = cx + r
    frags.append(
        f'<path d="M {x1:.1f} {cy:.1f} A {r:.1f} {r:.1f} 0 0 1 {x2:.1f} {cy:.1f}" '
        f'fill="#c5cfe0" stroke="{stroke_col}" stroke-width="1.5"/>\n'
    )
    return "".join(frags)


def _sound_waves(cx, cy_top, col=GREEN):
    """Три дуги-хвилі праворуч від точки (cx, cy_top) — символ звуку."""
    frags = []
    for i, r in enumerate([14, 22, 30]):
        alpha = 40
        rad = math.radians(alpha)
        sx = cx + r * math.cos(math.radians(180 - alpha))
        sy = cy_top - r * math.sin(rad)
        ex = cx + r * math.cos(math.radians(180 + alpha))
        ey = cy_top + r * math.sin(rad)
        frags.append(
            f'<path d="M {sx:.1f} {sy:.1f} A {r:.1f} {r:.1f} 0 0 1 {ex:.1f} {ey:.1f}" '
            f'fill="none" stroke="{col}" stroke-width="{1.8 - i*0.2:.1f}" stroke-linecap="round"/>\n'
        )
    return "".join(frags)


def _gnd_symbol(cx, y_top, col=BLUE):
    """GND: коротка ніжка + три горизонтальних риски, що звужуються."""
    frags = []
    frags.append(line(cx, y_top, cx, y_top + 12, color=col, sw=1.8))
    widths = [18, 12, 6]
    for i, w in enumerate(widths):
        yy = y_top + 12 + i * 6
        frags.append(line(cx - w / 2, yy, cx + w / 2, yy, color=col, sw=1.8))
    return "".join(frags)


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.1c.1 — Активний бузер vs пасивний: що всередині й який сигнал
# fig-25-1c-1-active-vs-passive.svg
# ═══════════════════════════════════════════════════════════════════════════════
def fig_1c1_active_vs_passive():
    W, H = 720, 340
    path = os.path.join(OUT, "fig-25-1c-1-active-vs-passive.svg")

    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 26, "Активний vs пасивний бузер: де живе генератор?",
                      size=15, color=INK, anchor="middle", bold=True))

    # ── Роздільник по центру ───────────────────────────────────────────────────
    frags.append(line(W / 2, 44, W / 2, H - 10, color=FAINT, sw=1.5))

    # ───────────────────── ЛІВА ПОЛОВИНА: АКТИВНИЙ ────────────────────────────
    lx = W / 4  # центр лівої половини

    frags.append(text(lx, 56, "АКТИВНИЙ", size=14, color=RED, anchor="middle", bold=True))
    frags.append(text(lx, 72, "(active buzzer)", size=10, color=GREY, anchor="middle"))

    # корпус-кружок (великий)
    body_r = 48
    body_cy = 155
    frags.append(circle(lx, body_cy, body_r, fill="#fff0ee", stroke=RED, sw=2))

    # п'єзопластина всередині (менший кружок)
    frags.append(_membrane_symbol(lx, body_cy, r=22, fill="#f4f6f8", stroke_col=METAL))

    # внутрішній генератор — маленький прямокутник із підписом
    gen_w, gen_h = 36, 20
    gen_x = lx - gen_w / 2
    gen_y = body_cy - body_r + 6
    frags.append(rect(gen_x, gen_y, gen_w, gen_h, fill=LRED, stroke=RED, sw=1.5, rx=4))
    frags.append(text(lx, gen_y + 13, "генер.", size=9, color=RED, anchor="middle", bold=True))

    # вхідний сигнал — пряма лінія зліва (DC HIGH)
    sig_x_left = lx - body_r - 52
    sig_y = body_cy
    frags.append(line(sig_x_left, sig_y, lx - body_r, sig_y, color=RED, sw=2.2))
    frags.append(text(sig_x_left - 2, sig_y - 6, "HIGH", size=10, color=RED, anchor="end", bold=True))

    # хвилі звуку праворуч
    frags.append(_sound_waves(lx + body_r, body_cy, col=GREEN))

    # підпис «хоче»
    tb1, _, _ = textbox(lx, body_cy + body_r + 28,
                         "хоче: сталий HIGH\n→ один тон ~2–4 кГц",
                         size=10, fill=LRED, stroke=RED, color=RED, pad=7)
    frags.append(tb1)

    # мінівисновок унизу
    frags.append(text(lx, H - 22, "→ digitalWrite(HIGH / LOW)",
                      size=10, color=RED, anchor="middle", bold=True))

    # ───────────────────── ПРАВА ПОЛОВИНА: ПАСИВНИЙ ───────────────────────────
    rx = W * 3 / 4  # центр правої половини

    frags.append(text(rx, 56, "ПАСИВНИЙ", size=14, color=BLUE, anchor="middle", bold=True))
    frags.append(text(rx, 72, "(passive buzzer)", size=10, color=GREY, anchor="middle"))

    # корпус-кружок
    frags.append(circle(rx, body_cy, body_r, fill="#eef2ff", stroke=BLUE, sw=2))

    # п'єзопластина всередині — без генератора
    frags.append(_membrane_symbol(rx, body_cy, r=22, fill="#f4f6f8", stroke_col=METAL))

    # підпис «БЕЗ генератора»
    frags.append(text(rx, body_cy + 30, "без генератора", size=9, color=GREY, anchor="middle"))

    # вхідний сигнал — ШІМ-меандр зліва
    pwm_start = rx - body_r - 62
    pwm_y_hi = body_cy - 14
    pwm_y_lo = body_cy + 14
    frags.append(_pwm_wave(pwm_start, pwm_y_hi, pwm_y_lo,
                            period_w=15, duty=0.5, n_periods=4, col=BLUE, sw=2.0))
    frags.append(text(pwm_start + 30, pwm_y_hi - 7, "ШІМ", size=9, color=BLUE, anchor="middle", bold=True))

    # хвилі звуку праворуч
    frags.append(_sound_waves(rx + body_r, body_cy, col=GREEN))

    # підпис «хоче»
    tb2, _, _ = textbox(rx, body_cy + body_r + 28,
                         "хоче: ШІМ-меандр\n→ частота = будь-яка нота",
                         size=10, fill=LBLUE, stroke=BLUE, color=BLUE, pad=7)
    frags.append(tb2)

    # мінівисновок унизу
    frags.append(text(rx, H - 22, "→ ledcWriteTone(pin, freq)",
                      size=10, color=BLUE, anchor="middle", bold=True))

    render(path, W, H, *frags, title=None)
    print("wrote", os.path.basename(path))


# ═══════════════════════════════════════════════════════════════════════════════
# Рис. 4.7.1c.2 — Підключення бузера до ESP32 і сигнал, що його живить
# fig-25-1c-2-wiring-and-signal.svg
# ═══════════════════════════════════════════════════════════════════════════════
def fig_1c2_wiring_and_signal():
    W, H = 760, 380
    path = os.path.join(OUT, "fig-25-1c-2-wiring-and-signal.svg")

    frags = []

    # ── Заголовок ─────────────────────────────────────────────────────────────
    frags.append(text(W / 2, 26, "Підключення: прямо до GPIO чи через транзистор-ключ?",
                      size=15, color=INK, anchor="middle", bold=True))
    frags.append(text(W / 2, 44, "струм бузера визначає схему; сорт бузера — форму сигналу",
                      size=10, color=GREY, anchor="middle"))

    # роздільник
    frags.append(line(W / 2, 52, W / 2, 250, color=FAINT, sw=1.5))

    # ═══════════════════════════════════════════════════════════════════════════
    # ЛІВА ПОЛОВИНА: п'єзо — прямо до GPIO
    # ═══════════════════════════════════════════════════════════════════════════
    lx = W / 4

    # Блок ESP32 GPIO
    tb_esp, tw_esp, th_esp = textbox(60, 120, "GPIO\nESP32\n3.3 В",
                                      size=11, fill=LBLUE, stroke=BLUE, pad=8, bold=False)
    frags.append(tb_esp)
    esp_rx = 60 + tw_esp / 2
    esp_cx = 60
    esp_mid_y = 120

    # лінія GPIO → бузер
    buz_lx = 175
    frags.append(line(60 + tw_esp / 2, 120, buz_lx, 120, color=BLUE, sw=2))

    # Бузер-прямокутник
    tb_buz, tw_buz, _ = textbox(buz_lx + 30, 120, "п'єзо\nбузер",
                                  size=11, fill=LRED, stroke=RED, pad=8)
    frags.append(tb_buz)
    buz_rx = buz_lx + 30 + tw_buz / 2

    # лінія бузер → GND
    gnd_y = 165
    frags.append(line(buz_lx + 30, 120 + 22, buz_lx + 30, gnd_y, color=INK, sw=1.8))
    frags.append(_gnd_symbol(buz_lx + 30, gnd_y, col=BLUE))

    # підпис
    frags.append(text(lx, 198, "п'єзо ~одиниці мА:", size=10, color=INK, anchor="middle", bold=True))
    frags.append(text(lx, 214, "прямо до GPIO", size=10, color=GREEN, anchor="middle", bold=True))

    # ═══════════════════════════════════════════════════════════════════════════
    # ПРАВА ПОЛОВИНА: гучний/котушковий — через транзистор-ключ
    # ═══════════════════════════════════════════════════════════════════════════
    rx_base = W / 2 + 20

    # Блок ESP32 GPIO (правий)
    tb_esp2, tw_esp2, _ = textbox(rx_base + 20, 120, "GPIO\n3.3 В",
                                    size=11, fill=LBLUE, stroke=BLUE, pad=8)
    frags.append(tb_esp2)

    # лінія до транзистора
    mos_cx = rx_base + 20 + tw_esp2 / 2 + 55
    frags.append(line(rx_base + 20 + tw_esp2 / 2, 120, mos_cx - 18, 120, color=BLUE, sw=2))

    # Транзистор-ключ (NPN/N-MOS) — прямокутник із підписом
    tb_mos, tw_mos, th_mos = textbox(mos_cx, 120, "NPN /\nN-MOS",
                                      size=10, fill=LAMB, stroke=GOLD, pad=7)
    frags.append(tb_mos)

    # лінія від транзистора до бузера (вгору)
    buz2_cy = 75
    buz2_cx = mos_cx
    frags.append(line(mos_cx, 120 - th_mos / 2, mos_cx, buz2_cy + 20, color=INK, sw=1.8))

    # Бузер2
    tb_buz2, tw_buz2, _ = textbox(buz2_cx, buz2_cy, "гучний\nбузер", size=10, fill=LRED, stroke=RED, pad=7)
    frags.append(tb_buz2)

    # живлення 5В зверху (через бузер до +5В)
    frags.append(line(buz2_cx, buz2_cy - 18, buz2_cx, 52, color=POS, sw=2))
    frags.append(text(buz2_cx + 4, 56, "+5 В", size=10, color=POS, anchor="start", bold=True))

    # флайбек-діод паралельно бузеру: трикутник+риска
    diode_x = buz2_cx + tw_buz2 / 2 + 14
    dy_top = buz2_cy - 18
    dy_bot = buz2_cy + 18
    dy_mid = (dy_top + dy_bot) / 2
    # тіло діода — трикутник (cathode вгорі)
    frags.append(
        f'<polygon points="{diode_x:.1f},{dy_top:.1f} {diode_x+12:.1f},{dy_mid:.1f} {diode_x:.1f},{dy_bot:.1f}" '
        f'fill="{LAMB}" stroke="{GOLD}" stroke-width="1.5"/>\n'
    )
    # риска катода
    frags.append(line(diode_x - 3, dy_top, diode_x + 13, dy_top, color=GOLD, sw=1.8))
    frags.append(text(diode_x + 16, dy_mid + 4, "флайбек-\nдіод",
                      size=8, color=GREY, anchor="start"))

    # GND від транзистора
    gnd2_y = 165
    frags.append(line(mos_cx, 120 + th_mos / 2, mos_cx, gnd2_y, color=INK, sw=1.8))
    frags.append(_gnd_symbol(mos_cx, gnd2_y, col=BLUE))

    # спільна земля підпис
    frags.append(text(mos_cx + 14, gnd2_y + 8, "спільна земля", size=9, color=GREY, anchor="start"))

    # підпис правої частини
    frags.append(text(rx_base + 140, 198, "гучний/котушковий:", size=10, color=INK, anchor="middle", bold=True))
    frags.append(text(rx_base + 140, 214, "ключ + флайбек-діод", size=10, color=RED, anchor="middle", bold=True))

    # ═══════════════════════════════════════════════════════════════════════════
    # ОСЦИЛОГРАМИ: нижня половина
    # ═══════════════════════════════════════════════════════════════════════════
    sep_y = 248
    frags.append(line(30, sep_y, W - 30, sep_y, color=FAINT, sw=1.2))
    frags.append(text(W / 2, sep_y + 14, "Форма сигналу залежить від сорту бузера",
                      size=11, color=INK, anchor="middle", bold=True))

    # ── Ліворуч: пасивний → меандр ──────────────────────────────────────────
    oc_lx = 60
    oc_y_hi = sep_y + 38
    oc_y_lo = sep_y + 78
    oc_w = 230

    frags.append(text(oc_lx, sep_y + 30, "пасивний бузер:", size=10, color=BLUE, anchor="start", bold=True))
    # вісь
    frags.append(line(oc_lx, oc_y_lo + 6, oc_lx + oc_w, oc_y_lo + 6, color=FAINT, sw=1))
    # меандр
    frags.append(_pwm_wave(oc_lx, oc_y_hi, oc_y_lo, period_w=28, duty=0.5, n_periods=8, col=BLUE))
    frags.append(text(oc_lx + oc_w / 2, oc_y_lo + 22,
                      "частота = висота тону", size=9, color=BLUE, anchor="middle", bold=True))

    # ── Праворуч: активний → HIGH-полиця ────────────────────────────────────
    oc_rx = W / 2 + 30
    oc_y_hi2 = sep_y + 48
    oc_y_lo2 = sep_y + 78
    oc_w2 = 230

    frags.append(text(oc_rx, sep_y + 30, "активний бузер:", size=10, color=RED, anchor="start", bold=True))
    # вісь
    frags.append(line(oc_rx, oc_y_lo2 + 6, oc_rx + oc_w2, oc_y_lo2 + 6, color=FAINT, sw=1))
    # HIGH-полиця (суцільна лінія у HIGH)
    frags.append(line(oc_rx, oc_y_lo2, oc_rx, oc_y_hi2, color=RED, sw=2.2))
    frags.append(line(oc_rx, oc_y_hi2, oc_rx + oc_w2, oc_y_hi2, color=RED, sw=2.2))
    frags.append(text(oc_rx + oc_w2 / 2, oc_y_lo2 + 22,
                      "сталий рівень, генератор усередині", size=9, color=RED, anchor="middle", bold=True))

    # підпис-висновок
    note, _, _ = textbox(W / 2, H - 20,
                          "Вибір «прямо чи через ключ» = струм бузера.\nСорт бузера = форма сигналу й вид коду.",
                          size=10, fill=LAMB, stroke=GOLD, color=INK, pad=7)
    frags.append(note)

    render(path, W, H, *frags, title=None)
    print("wrote", os.path.basename(path))


# ─── main ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    fig_1c1_active_vs_passive()
    fig_1c2_wiring_and_signal()
    print("Done.")
