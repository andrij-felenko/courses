# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до статті «Джойстик через станцію проти власного пульта».
svgkit імпортуємо зі scripts/, вивід у ./img/."""
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(SCRIPT_DIR, "img")
os.makedirs(IMG_DIR, exist_ok=True)

sys.path.insert(0, os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'scripts'))
from svgkit import *

def path(d, fill="none", stroke=LINE, sw=1.5):
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"/>'


# ── Фігура 1: порівняння двох архітектур доставки команд ────────────────────
def fig_direct_rc_vs_gcs_joystick():
    W, H = 1020, 520
    P = []
    P.append(text(W / 2, 28, "Архітектура тракту керування: прямий RC-лінк проти джойстика через станцію",
                  size=16, bold=True))

    # --- Верхня доріжка: Прямий RC ---
    top_y = 60
    P.append(rect(15, top_y, W - 30, 185, fill="#f4faf6", stroke=FIELD, sw=1.5, rx=8))
    P.append(text(35, top_y + 24, "ТРАКТ 1: ПРЯМИЙ RC-ПУЛЬТ (ExpressLRS / CRSF / S.BUS) — ДЕТЕРМІНОВАНИЙ РЕАЛЬНИЙ ЧАС",
                  size=12.5, color=FIELD, bold=True, anchor="start"))

    rc_blocks = [
        ("Стіки / Датчики\nХолла (АЦП 12-bit)", 115, 90),
        ("Мікроконтролер\nEdgeTX / OpenTX", 285, 90),
        ("RF-трансивер\nSX1280 (2.4 ГГц)", 455, 90),
        ("Бортовий RX\nExpressLRS", 675, 90),
        ("Автопілот (FC)\nUART DMA / Timer", 870, 90)
    ]

    by = top_y + 90
    for i, (label, cx, cw) in enumerate(rc_blocks):
        fr, _, _ = textbox(cx, by, label, size=11, bold=True, fill="#ffffff", stroke=INK, min_w=cw)
        P.append(fr)
        if i < len(rc_blocks) - 1:
            next_cx = rc_blocks[i + 1][1]
            if i == 2: # RF ефір
                P.append(arrow(cx + cw / 2 + 10, by, next_cx - rc_blocks[i+1][2] / 2 - 10, by, color=FIELD, sw=2.5))
                P.append(text((cx + next_cx) / 2, by - 16, "Прямий ефір\n150–500 Гц", size=10.5, color=FIELD, bold=True))
            else:
                P.append(arrow(cx + cw / 2 + 8, by, next_cx - rc_blocks[i+1][2] / 2 - 8, by, color=INK, sw=1.8))

    # Підсумок прямого тракту
    P.append(rect(35, top_y + 145, W - 70, 28, fill="#e8f8f0", stroke=FIELD, sw=1, rx=4))
    P.append(text(W / 2, top_y + 163, "Наскрізна затримка: 3–8 мс  •  Джитер: <0.5 мс  •  Апаратний таймер  •  Прямий перехід у Failsafe",
                  size=11.5, color=FIELD, bold=True))

    # --- Нижня доріжка: GCS Joystick ---
    bot_y = 265
    P.append(rect(15, bot_y, W - 30, 235, fill="#fdf7f6", stroke=POS, sw=1.5, rx=8))
    P.append(text(35, bot_y + 24, "ТРАКТ 2: USB-ДЖОЙСТИК ЧЕРЕЗ СТАНЦІЮ (QGroundControl + MAVLink #69) — НЕЖОРСТКИЙ ЧАС",
                  size=12.5, color=POS, bold=True, anchor="start"))

    gcs_blocks = [
        ("USB-геймпад\nОпитування 125 Гц", 95, 95),
        ("Драйвер ОС HID\nЧерга подій OS", 245, 95),
        ("GCS (Qt EventLoop)\nПакет MAVLink #69", 400, 105),
        ("USB-UART міст\nБуфер FTDI (16 мс)", 560, 100),
        ("Телеметрійний\nРадіомодем (SiK)", 715, 95),
        ("Автопілот (FC)\nMAVLink парсер", 875, 95)
    ]

    by2 = bot_y + 90
    for i, (label, cx, cw) in enumerate(gcs_blocks):
        fr, _, _ = textbox(cx, by2, label, size=10.5, bold=True, fill="#ffffff", stroke=INK, min_w=cw)
        P.append(fr)
        if i < len(gcs_blocks) - 1:
            next_cx = gcs_blocks[i + 1][1]
            if i == 4: # Радіомодем ефір
                P.append(arrow(cx + cw / 2 + 8, by2, next_cx - gcs_blocks[i+1][2] / 2 - 8, by2, color=POS, sw=2.5))
                P.append(text((cx + next_cx) / 2, by2 - 16, "Півдуплекс\n20–50 Гц", size=10.5, color=POS, bold=True))
            else:
                P.append(arrow(cx + cw / 2 + 6, by2, next_cx - gcs_blocks[i+1][2] / 2 - 6, by2, color=INK, sw=1.8))

    # Джерела небезпеки в GCS
    P.append(rect(35, bot_y + 145, W - 70, 42, fill="#fbeae8", stroke=POS, sw=1, rx=4))
    P.append(text(W / 2, bot_y + 162, "Джерела затримок: Планування ОС (DPC/ISR) + Таймер FTDI + Черга телеметрії + Втрата фокусу вікна",
                  size=11, color=POS, bold=True))
    P.append(text(W / 2, bot_y + 178, "Наскрізна затримка: 45–180+ мс  •  Плаваючий джитер: 20–120 мс  •  Ризик застигання осей при лагу софту",
                  size=11, color=POS, bold=True))

    render(os.path.join(IMG_DIR, "direct-rc-vs-gcs-joystick.svg"), W, H, *P)


# ── Фігура 2: розподіл затримки та джитеру ──────────────────────────────────
def fig_latency_jitter_distribution():
    W, H = 940, 420
    P = []
    P.append(text(W / 2, 28, "Розподіл затримки: детермінований пульт проти плаваючого джойстика GCS",
                  size=16, bold=True))

    ox = 90
    oy = 330
    gw = 780
    gh = 240

    # Осі координат
    P.append(line(ox, oy, ox + gw, oy, color=INK, sw=1.8))
    P.append(line(ox, oy, ox, oy - gh, color=INK, sw=1.8))
    P.append(text(ox + gw - 10, oy + 25, "Затримка доставки команди (мс)", size=12, bold=True, anchor="end"))
    P.append(text(ox - 10, oy - gh + 15, "Густина\nймовірності", size=11, color=MUTED, anchor="end"))

    # Поділки на осі X (шкала 0 .. 200 мс)
    ticks = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
    for t in ticks:
        tx = ox + (t / 200.0) * (gw - 40)
        P.append(line(tx, oy, tx, oy + 5, color=LINE, sw=1.2))
        P.append(text(tx, oy + 18, str(t), size=10.5, color=MUTED))

    # 1. Прямий RC (гострий високий пік біля 4 мс)
    rc_peak_x = ox + (5.0 / 200.0) * (gw - 40)
    rc_path = f"M {rc_peak_x - 12:.1f} {oy:.1f} Q {rc_peak_x:.1f} {oy - 210:.1f} {rc_peak_x + 12:.1f} {oy:.1f} Z"
    P.append(path(rc_path, fill="#27ae60", stroke=FIELD, sw=2.0))
    P.append(rect(rc_peak_x + 18, oy - 200, 220, 45, fill="#eafaf1", stroke=FIELD, sw=1.2, rx=4))
    P.append(text(rc_peak_x + 28, oy - 184, "Прямий RC (ELRS 250 Гц)", size=11, color=FIELD, bold=True, anchor="start"))
    P.append(text(rc_peak_x + 28, oy - 168, "Середнє: 4.2 мс  |  Джитер: ±0.3 мс", size=10.5, color=INK, anchor="start"))

    # 2. GCS Joystick (розмитий плоский купол з довгим хвостом, центр ≈ 65 мс)
    gcs_x0 = ox + (35.0 / 200.0) * (gw - 40)
    gcs_top = ox + (65.0 / 200.0) * (gw - 40)
    gcs_tail = ox + (190.0 / 200.0) * (gw - 40)
    gcs_path = f"M {gcs_x0:.1f} {oy:.1f} C {gcs_top - 30:.1f} {oy - 85:.1f}, {gcs_top:.1f} {oy - 85:.1f}, {gcs_top + 40:.1f} {oy - 50:.1f} C {gcs_top + 80:.1f} {oy - 25:.1f}, {gcs_tail - 20:.1f} {oy - 10:.1f}, {gcs_tail:.1f} {oy:.1f} Z"
    P.append(path(gcs_path, fill="#f9d5d1", stroke=POS, sw=2.0))
    
    # Виноска GCS
    P.append(rect(gcs_top + 20, oy - 110, 260, 56, fill="#fdf2f0", stroke=POS, sw=1.2, rx=4))
    P.append(text(gcs_top + 30, oy - 94, "Джойстик через GCS + Телеметрія", size=11, color=POS, bold=True, anchor="start"))
    P.append(text(gcs_top + 30, oy - 78, "Середнє: 65–85 мс  |  Джитер: ±45 мс", size=10.5, color=INK, anchor="start"))
    P.append(text(gcs_top + 30, oy - 62, "Важкий хвіст: сплески до 200–350 мс", size=10, color=POS, bold=True, anchor="start"))

    # Пояснення знизу
    fr, _, _ = textbox(W / 2, H - 25,
                       "Низький джитер пульта забезпечує передбачуваність петлі; плаваючий джитер GCS руйнує запас стійкості оператора",
                       size=11.5, bold=True, fill="#f4f6f8", stroke=MUTED, min_w=780)
    P.append(fr)

    render(os.path.join(IMG_DIR, "latency-jitter-distribution.svg"), W, H, *P)


# ── Фігура 3: безпечний автомат станів MANUAL_CONTROL ────────────────────────
def fig_safe_manual_control_fsm():
    W, H = 940, 480
    P = []
    P.append(text(W / 2, 28, "Автомат безпечного арбітражу та обробки MANUAL_CONTROL на борті",
                  size=16, bold=True))

    # Стан 1: RC Direct (Пріоритетний прямий пульт)
    s1_cx, s1_cy = 200, 120
    fr, _, _ = textbox(s1_cx, s1_cy, "RC_ACTIVE\nПрямий RC-лінк\n(Найвищий пріоритет)",
                       size=12, bold=True, fill="#e8f8f0", stroke=FIELD, min_w=170)
    P.append(fr)

    # Стан 2: GCS Manual Active
    s2_cx, s2_cy = 650, 120
    fr, _, _ = textbox(s2_cx, s2_cy, "GCS_MANUAL_ACTIVE\nПрийом MANUAL_CONTROL #69\n(Пакет свіжий: dt < 200 мс)",
                       size=12, bold=True, fill="#eaf2fc", stroke=NEG, min_w=210)
    P.append(fr)

    # Стан 3: Stick Timeout Degrade (М'яка деградація)
    s3_cx, s3_cy = 650, 310
    fr, _, _ = textbox(s3_cx, s3_cy, "STICK_DEGRADE\nЛаг пакета (200..1000 мс)\nНейтралізація осей + Утримання",
                       size=12, bold=True, fill="#fef9e7", stroke="#d4ac0d", min_w=220)
    P.append(fr)

    # Стан 4: Hard Failsafe
    s4_cx, s4_cy = 200, 310
    fr, _, _ = textbox(s4_cx, s4_cy, "HARD_FAILSAFE\nПовна втрата (dt > 1000 мс)\nПерехід у RTL / Land / Hold",
                       size=12, bold=True, fill="#fdecea", stroke=POS, min_w=190)
    P.append(fr)

    # Стрілки переходів
    # 1 -> 2 (Прямий RC у центрі, GCS надсилає команду)
    P.append(arrow(s1_cx + 85, s1_cy - 10, s2_cx - 105, s2_cy - 10, color=MUTED, sw=1.6))
    P.append(text((s1_cx + s2_cx) / 2, s1_cy - 22, "RC у нулі + GCS активний", size=10, color=MUTED))

    # 2 -> 1 (Оператор торкнувся стіка RC — миттєве перехоплення!)
    P.append(arrow(s2_cx - 105, s2_cy + 15, s1_cx + 85, s1_cy + 15, color=FIELD, sw=2.2))
    P.append(text((s1_cx + s2_cx) / 2, s1_cy + 28, "Рух стіка RC (ПЕРЕХОПЛЕННЯ)", size=10.5, color=FIELD, bold=True))

    # 2 -> 3 (Таймаут MANUAL_CONTROL > 200 мс)
    P.append(arrow(s2_cx, s2_cy + 35, s3_cx, s3_cy - 35, color=POS, sw=1.8))
    P.append(text(s2_cx + 10, (s2_cy + s3_cy) / 2, "dt > 200 мс\n(лаг / зависання)", size=10, color=POS, anchor="start"))

    # 3 -> 2 (Відновлення потоку)
    P.append(arrow(s3_cx - 40, s3_cy - 35, s2_cx - 40, s2_cy + 35, color=NEG, sw=1.5))
    P.append(text(s3_cx - 48, (s2_cy + s3_cy) / 2, "dt < 50 мс\n(відновлення)", size=9.5, color=NEG, anchor="end"))

    # 3 -> 4 (Таймаут > 1000 мс)
    P.append(arrow(s3_cx - 110, s3_cy, s4_cx + 95, s4_cy, color=POS, sw=2.0))
    P.append(text((s3_cx + s4_cx) / 2, s3_cy - 12, "dt > 1000 мс (немає пакетів)", size=10, color=POS, bold=True))

    # 4 -> 1 (Відновлення керування з пульта)
    P.append(arrow(s4_cx, s4_cy - 35, s1_cx, s1_cy + 35, color=FIELD, sw=1.8))
    P.append(text(s1_cx - 10, (s1_cy + s4_cy) / 2, "Команда з RC", size=10, color=FIELD, anchor="end"))

    # Пояснення знизу
    fr, _, _ = textbox(W / 2, H - 35,
                       "Принцип безпеки: GCS ніколи не може заблокувати апаратний RC; при зависанні софту станції осі скидаються в нуль до включення RTL",
                       size=11, bold=True, fill="#f4f6f8", stroke=MUTED, min_w=850)
    P.append(fr)

    render(os.path.join(IMG_DIR, "safe-manual-control-fsm.svg"), W, H, *P)


if __name__ == "__main__":
    fig_direct_rc_vs_gcs_joystick()
    fig_latency_jitter_distribution()
    fig_safe_manual_control_fsm()
    print("All figures generated successfully.")
