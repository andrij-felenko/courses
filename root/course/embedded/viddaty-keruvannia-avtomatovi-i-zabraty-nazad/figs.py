# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

AMBER   = "#caa24a"
AMBERBG = "#fff6e0"
AMBERTX = "#8a6d1a"
GREENBG = "#eef6ef"
BLUEBG  = "#e9eefb"
REDBG   = "#fbecec"


# ── 1. takeover-mechanisms: тумблер режимів проти Stick Stirring ─────────────
def fig_takeover_mechanisms():
    W, H = 860, 440
    p = []
    p.append(text(W / 2, 28, "Механізми перехоплення керування: тумблер режимів проти Stick Stirring", size=15, color=INK, bold=True))

    # Ліва колонка: Mode Switch Takeover
    bx1, bw1, by, bh = 25, 390, 55, 340
    p.append(rect(bx1, by, bw1, bh, fill=BLUEBG, stroke=NEG, sw=1.8, rx=10))
    p.append(text(bx1 + bw1 / 2, by + 26, "Апаратний тумблер (Mode Switch)", size=13, color=NEG, bold=True))
    p.append(text(bx1 + bw1 / 2, by + 46, "Дискретне перемикання через окремий RC-канал", size=10, color=MUTED, italic=True))

    # Блоки ланцюга тумблера
    p.append(rect(bx1 + 20, by + 65, bw1 - 40, 52, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(bx1 + bw1 / 2, by + 86, "Трьохпозиційний перемикач пульта", size=11, color=INK, bold=True))
    p.append(text(bx1 + bw1 / 2, by + 104, "CH5: Pos 1 (Auto) → Pos 2/3 (Manual)", size=9.5, color=MUTED))

    p.append(arrow(bx1 + bw1 / 2, by + 118, bx1 + bw1 / 2, by + 138, color=NEG, sw=1.8))

    p.append(rect(bx1 + 20, by + 140, bw1 - 40, 52, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(bx1 + bw1 / 2, by + 161, "Декодер RC-сигналу та фільтр антибрязкоту", size=11, color=INK, bold=True))
    p.append(text(bx1 + bw1 / 2, by + 179, "Гістерезис PWM 1000…2000 мкс (Δ > 50 мкс)", size=9.5, color=MUTED))

    p.append(arrow(bx1 + bw1 / 2, by + 193, bx1 + bw1 / 2, by + 213, color=NEG, sw=1.8))

    p.append(rect(bx1 + 20, by + 215, bw1 - 40, 105, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(bx1 + bw1 / 2, by + 236, "Властивості тумблерного перехоплення:", size=10.5, color=NEG, bold=True))
    p.append(text(bx1 + 30, by + 258, "✓ 100% явний намір оператора", size=9.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(bx1 + 30, by + 278, "✓ Повне апаратне відключення автоматики", size=9.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(bx1 + 30, by + 298, "✗ Затримка реакції людини: 0.8…1.5 с на пошук", size=9.5, color=POS, bold=True, anchor="start"))

    # Права колонка: Stick Stirring / Deflection Override
    bx2, bw2 = 445, 390
    p.append(rect(bx2, by, bw2, bh, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=10))
    p.append(text(bx2 + bw2 / 2, by + 26, "Перевизначення стіками (Stick Stirring)", size=13, color=AMBERTX, bold=True))
    p.append(text(bx2 + bw2 / 2, by + 46, "Автоматичне виявлення відхилення ручок керування", size=10, color=MUTED, italic=True))

    # Блоки ланцюга Stick Stirring
    p.append(rect(bx2 + 20, by + 65, bw2 - 40, 52, fill=BG, stroke=AMBER, sw=1.2, rx=6))
    p.append(text(bx2 + bw2 / 2, by + 86, "Рух стіків пілота (Roll, Pitch, Yaw, Throttle)", size=11, color=INK, bold=True))
    p.append(text(bx2 + bw2 / 2, by + 104, "Інстинктивна дія оператора при загрозі", size=9.5, color=MUTED))

    p.append(arrow(bx2 + bw2 / 2, by + 118, bx2 + bw2 / 2, by + 138, color=AMBERTX, sw=1.8))

    p.append(rect(bx2 + 20, by + 140, bw2 - 40, 52, fill=BG, stroke=AMBER, sw=1.2, rx=6))
    p.append(text(bx2 + bw2 / 2, by + 161, "Детектор мертвої зони (|Δstick| > 10…15%)", size=11, color=INK, bold=True))
    p.append(text(bx2 + bw2 / 2, by + 179, "Захист від люфту пружин і тремтіння рук", size=9.5, color=MUTED))

    p.append(arrow(bx2 + bw2 / 2, by + 193, bx2 + bw2 / 2, by + 213, color=AMBERTX, sw=1.8))

    p.append(rect(bx2 + 20, by + 215, bw2 - 40, 105, fill=BG, stroke=AMBER, sw=1.2, rx=6))
    p.append(text(bx2 + bw2 / 2, by + 236, "Властивості перехоплення стіками:", size=10.5, color=AMBERTX, bold=True))
    p.append(text(bx2 + 30, by + 258, "✓ Миттєва реакція: 100…200 мс (без пошуку тумблера)", size=9.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(bx2 + 30, by + 278, "✓ Підтримка Fly-Through (підрулювання на курсі)", size=9.5, color=FIELD, bold=True, anchor="start"))
    p.append(text(bx2 + 30, by + 298, "✗ Потребує таймера центровки для повернення в авто", size=9.5, color=AMBERTX, bold=True, anchor="start"))

    # Нижній висновок
    p.append(rect(25, 403, 810, 28, fill=FILL, stroke=LINE, sw=1.2, rx=5))
    p.append(text(W / 2, 421, "Надійний автопілот комбінує обидва: стіки дають миттєвий тактичний маневр, тумблер — жорсткий вихід з авторежиму", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "takeover-mechanisms.svg"), W, H, *p,
           title="Механізми перехоплення керування")


# ── 2. integrator-windup-conflict: інтегральне насичення та ривок ───────────
def fig_integrator_windup():
    W, H = 860, 440
    p = []
    p.append(text(W / 2, 28, "Конфлікт автопілота й пілота: інтегральне насичення та ривок при передачі", size=15, color=INK, bold=True))

    # Верхній блок: Модель виникнення помилки неузгодженості
    ty, th = 55, 135
    p.append(rect(25, ty, 810, th, fill=AMBERBG, stroke=AMBER, sw=1.8, rx=8))
    p.append(text(W / 2, ty + 24, "Фізика конфлікту траєкторій (Pilot vs Autopilot Conflict)", size=13, color=AMBERTX, bold=True))

    # Складові верхнього блоку
    p.append(rect(45, ty + 42, 230, 75, fill=BG, stroke=NEG, sw=1.2, rx=6))
    p.append(text(160, ty + 64, "Уставка автопілота (Setpt)", size=11, color=NEG, bold=True))
    p.append(text(160, ty + 84, "Автопілот веде літак за курсом", size=9.5, color=INK))
    p.append(text(160, ty + 102, "Target: Heading = 090°", size=9.5, color=MUTED))

    p.append(rect(315, ty + 42, 230, 75, fill=BG, stroke=POS, sw=1.2, rx=6))
    p.append(text(430, ty + 64, "Дія пілота (Manual Override)", size=11, color=POS, bold=True))
    p.append(text(430, ty + 84, "Пілот відхиляє ручку вліво", size=9.5, color=INK))
    p.append(text(430, ty + 102, "Actual: Heading = 060°", size=9.5, color=MUTED))

    p.append(rect(585, ty + 42, 230, 75, fill=BG, stroke=AMBER, sw=1.2, rx=6))
    p.append(text(700, ty + 64, "Помилка контуру: e(t) ≠ 0", size=11, color=AMBERTX, bold=True))
    p.append(text(700, ty + 84, "e(t) = Setpoint - Actual = +30°", size=9.5, color=INK))
    p.append(text(700, ty + 102, "Інтегратор накопичує I = Ki · ∫ e dt", size=9.5, color=POS, bold=True))

    # Нижній блок: Порівняння результатів передачі керування
    by, bh = 205, 195
    p.append(rect(25, by, 390, bh, fill=REDBG, stroke=POS, sw=1.8, rx=8))
    p.append(text(220, by + 24, "БЕЗ скидання інтегратора (Windup Fault)", size=12, color=POS, bold=True))

    p.append(rect(45, by + 40, 350, 48, fill=BG, stroke=POS, sw=1, rx=5))
    p.append(text(220, by + 60, "I-term виріс до максимального упору (I_max)", size=10, color=POS, bold=True))
    p.append(text(220, by + 76, "Регулятор перенасичений вправо на 100%", size=9.5, color=INK))

    p.append(rect(45, by + 98, 350, 85, fill=BG, stroke=POS, sw=1, rx=5))
    p.append(text(220, by + 118, "АВАРІЙНИЙ НАСЛІДОК ПРИ ПОВЕРНЕННІ В АВТО:", size=10, color=POS, bold=True))
    p.append(text(220, by + 138, "• Миттєвий удар кермами вправо (Control Bump)", size=9.5, color=INK))
    p.append(text(220, by + 156, "• Перевантаження крила, зрив потоку, штопор", size=9.5, color=INK))
    p.append(text(220, by + 172, "• Трагедія Нагоя 1994: боротьба з тримером", size=9.5, color=POS, bold=True))

    p.append(rect(445, by, 390, bh, fill=GREENBG, stroke=FIELD, sw=1.8, rx=8))
    p.append(text(640, by + 24, "З Anti-Windup та плавною синхронізацією", size=12, color=FIELD, bold=True))

    p.append(rect(465, by + 40, 350, 48, fill=BG, stroke=FIELD, sw=1, rx=5))
    p.append(text(640, by + 60, "I-term заморожується або експоненційно згасає", size=10, color=FIELD, bold=True))
    p.append(text(640, by + 76, "dI/dt = 0 під час ручного втручання оператора", size=9.5, color=INK))

    p.append(rect(465, by + 98, 350, 85, fill=BG, stroke=FIELD, sw=1, rx=5))
    p.append(text(640, by + 118, "БЕЗПЕЧНА ПОВЕДІНКА ПРИ ПЕРЕДАЧІ:", size=10, color=FIELD, bold=True))
    p.append(text(640, by + 138, "• Setpoint підтягується до фактичного курсу", size=9.5, color=INK))
    p.append(text(640, by + 156, "• Плавне наростання авторитету без ривка (Bumpless)", size=9.5, color=INK))
    p.append(text(640, by + 172, "• Стабільне утримання нової траєкторії", size=9.5, color=FIELD, bold=True))

    # Нижній висновок
    p.append(rect(25, 408, 810, 24, fill=FILL, stroke=LINE, sw=1.2, rx=5))
    p.append(text(W / 2, 424, "Під час перехоплення інтегратор не повинен накопичувати помилку, спричинену діями пілота", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "integrator-windup-conflict.svg"), W, H, *p,
           title="Інтегральне насичення та конфлікт траєкторій")


# ── 3. smooth-handover-blending: динамічне змішування авторитетів ────────────
def fig_smooth_blending():
    W, H = 860, 440
    p = []
    p.append(text(W / 2, 28, "Динамічне змішування авторитетів (Alpha Blending) та часові фази", size=15, color=INK, bold=True))

    # Графік ваг авторитету
    gx, gy, gw, gh = 60, 60, 740, 230
    p.append(rect(gx, gy, gw, gh, fill=BG, stroke=LINE, sw=1.5, rx=6))

    # Вісі графіка
    p.append(line(gx + 40, gy + gh - 35, gx + gw - 20, gy + gh - 35, color=LINE, sw=1.5))
    p.append(line(gx + 40, gy + gh - 35, gx + 40, gy + 25, color=LINE, sw=1.5))
    p.append(text(gx + gw - 15, gy + gh - 30, "t", size=12, color=INK, bold=True))
    p.append(text(gx + 30, gy + 25, "α", size=13, color=INK, bold=True))

    # Позначки осі Y: 0.0, 0.5, 1.0
    p.append(text(gx + 25, gy + gh - 35, "0.0", size=9.5, color=MUTED))
    p.append(text(gx + 25, gy + gh / 2 - 5, "0.5", size=9.5, color=MUTED))
    p.append(text(gx + 25, gy + 45, "1.0", size=9.5, color=MUTED))
    p.append(line(gx + 36, gy + 45, gx + gw - 20, gy + 45, color=LINE, sw=0.8, dash="3,3"))
    p.append(line(gx + 36, gy + gh / 2 - 5, gx + gw - 20, gy + gh / 2 - 5, color=LINE, sw=0.8, dash="3,3"))

    # Фазові вертикальні розділювачі
    x_t0 = gx + 40
    x_t1 = gx + 170  # Початок перехоплення
    x_t2 = gx + 250  # Повний ручний
    x_t3 = gx + 470  # Повернення стіків у центр
    x_t4 = gx + 590  # Закінчення таймауту центровки
    x_t5 = gx + 670  # Повне повернення в авто

    phases_lines = [x_t1, x_t2, x_t3, x_t4, x_t5]
    for px_val in phases_lines:
        p.append(line(px_val, gy + 25, px_val, gy + gh - 35, color=MUTED, sw=1, dash="4,4"))

    # Підписи фаз угорі графіка
    p.append(text((x_t0 + x_t1) / 2, gy + 18, "ФАЗА 1: AUTO", size=10, color=NEG, bold=True))
    p.append(text((x_t1 + x_t2) / 2, gy + 18, "ФАЗА 2: TAKE", size=9.5, color=AMBERTX, bold=True))
    p.append(text((x_t2 + x_t3) / 2, gy + 18, "ФАЗА 3: MANUAL OVERRIDE", size=10, color=POS, bold=True))
    p.append(text((x_t3 + x_t4) / 2, gy + 18, "ФАЗА 4: TIMEOUT", size=9.5, color=AMBERTX, bold=True))
    p.append(text((x_t4 + x_t5) / 2, gy + 18, "ФАЗА 5: BLEND", size=9.5, color=FIELD, bold=True))
    p.append(text((x_t5 + gx + gw - 20) / 2, gy + 18, "AUTO", size=10, color=NEG, bold=True))

    # Крива Alpha Pilot (Червона)
    y_zero = gy + gh - 35
    y_one  = gy + 45

    pts_pilot = [
        (x_t0, y_zero), (x_t1, y_zero),
        (x_t2, y_one),
        (x_t3, y_one), (x_t4, y_one),
        (x_t5, y_zero), (gx + gw - 20, y_zero)
    ]
    for i in range(len(pts_pilot) - 1):
        p.append(line(pts_pilot[i][0], pts_pilot[i][1], pts_pilot[i+1][0], pts_pilot[i+1][1], color=POS, sw=2.5))

    # Крива Alpha Autopilot (Синя, 1 - Alpha)
    pts_auto = [
        (x_t0, y_one), (x_t1, y_one),
        (x_t2, y_zero),
        (x_t3, y_zero), (x_t4, y_zero),
        (x_t5, y_one), (gx + gw - 20, y_one)
    ]
    for i in range(len(pts_auto) - 1):
        p.append(line(pts_auto[i][0], pts_auto[i][1], pts_auto[i+1][0], pts_auto[i+1][1], color=NEG, sw=2.5, dash="5,3"))

    # Пояснення інтервалів на графіку
    p.append(text((x_t1 + x_t2) / 2, y_zero - 45, "T_blend", size=10, color=AMBERTX, bold=True))
    p.append(text((x_t3 + x_t4) / 2, y_one + 35, "T_hold", size=10, color=POS, bold=True))
    p.append(text((x_t4 + x_t5) / 2, y_zero - 45, "T_blend", size=10, color=FIELD, bold=True))

    # Легенда
    p.append(line(gx + 50, gy + gh - 15, gx + 85, gy + gh - 15, color=POS, sw=2.5))
    p.append(text(gx + 92, gy + gh - 12, "Вага оператора α(t)", size=9.5, color=POS, bold=True, anchor="start"))

    p.append(line(gx + 250, gy + gh - 15, gx + 285, gy + gh - 15, color=NEG, sw=2.5, dash="5,3"))
    p.append(text(gx + 292, gy + gh - 12, "Вага автопілота 1 − α(t)", size=9.5, color=NEG, bold=True, anchor="start"))

    # Нижня формульна панель
    fy, fh = 300, 125
    p.append(rect(25, fy, 810, fh, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    p.append(text(W / 2, fy + 24, "Математична модель змішування: u(t) = (1 − α(t)) · u_auto(t) + α(t) · u_pilot(t)", size=12.5, color=INK, bold=True))

    blocks = [
        (45, fy + 38, 235, 75, "1. Початок перехоплення", "Стіки > 12% порогу → α плавно зростає від 0 до 1 за 200 мс. Повна відсутність стрибка моменту на сервоприводах.", BLUEBG, NEG),
        (312, fy + 38, 235, 75, "2. Утримання центру", "Стіки повернулися в мертву зону. Запускається таймер T_hold (1.0…2.0 с) для запобігання хибному поверненню в авто.", AMBERBG, AMBER),
        (580, fy + 38, 235, 75, "3. Плавне повернення", "Таймер вичерпано → α плавно спадає від 1 до 0 за 400 мс. Автопілот захоплює оновлену лінію шляху без клевка.", GREENBG, FIELD),
    ]
    for bx, by_box, bw, bh_box, title_b, desc_b, bg_b, stroke_b in blocks:
        tag_c = AMBERTX if stroke_b == AMBER else stroke_b
        p.append(rect(bx, by_box, bw, bh_box, fill=bg_b, stroke=stroke_b, sw=1.2, rx=6))
        p.append(text(bx + bw / 2, by_box + 20, title_b, size=10.5, color=tag_c, bold=True))
        lines_d = [desc_b[:48], desc_b[48:96], desc_b[96:]]
        for j, ln in enumerate(lines_d):
            if ln.strip():
                p.append(text(bx + bw / 2, by_box + 38 + j * 14, ln.strip(), size=9.5, color=INK))

    render(os.path.join(OUT, "smooth-handover-blending.svg"), W, H, *p,
           title="Динамічне змішування авторитетів")


# ── 4. takeover-state-machine: скінченний автомат перехоплення ──────────────
def fig_takeover_fsm():
    W, H = 860, 440
    p = []
    p.append(text(W / 2, 28, "Скінченний автомат станів системи перехоплення керування", size=15, color=INK, bold=True))

    # Стан 1: AUTO_NAV
    s1_x, s1_y, s1_w, s1_h = 40, 75, 210, 110
    p.append(rect(s1_x, s1_y, s1_w, s1_h, fill=BLUEBG, stroke=NEG, sw=2, rx=8))
    p.append(text(s1_x + s1_w / 2, s1_y + 26, "STATE_AUTO_NAV", size=12, color=NEG, bold=True))
    p.append(text(s1_x + s1_w / 2, s1_y + 48, "Автономний політ (α = 0.0)", size=10, color=INK, bold=True))
    p.append(text(s1_x + s1_w / 2, s1_y + 68, "• Керує навігаційний контур", size=9.5, color=MUTED))
    p.append(text(s1_x + s1_w / 2, s1_y + 88, "• Відстеження колії / місії", size=9.5, color=MUTED))

    # Стан 2: OVERRIDE_BLENDING_IN
    s2_x, s2_y, s2_w, s2_h = 325, 75, 210, 110
    p.append(rect(s2_x, s2_y, s2_w, s2_h, fill=AMBERBG, stroke=AMBER, sw=2, rx=8))
    p.append(text(s2_x + s2_w / 2, s2_y + 26, "STATE_OVERRIDE_IN", size=12, color=AMBERTX, bold=True))
    p.append(text(s2_x + s2_w / 2, s2_y + 48, "Наростання втручання", size=10, color=INK, bold=True))
    p.append(text(s2_x + s2_w / 2, s2_y + 68, "• 0.0 < α < 1.0 (Ramp up)", size=9.5, color=MUTED))
    p.append(text(s2_x + s2_w / 2, s2_y + 88, "• Заморозка I-терму автопілота", size=9.5, color=MUTED))

    # Стан 3: MANUAL_OVERRIDE
    s3_x, s3_y, s3_w, s3_h = 610, 75, 210, 110
    p.append(rect(s3_x, s3_y, s3_w, s3_h, fill=REDBG, stroke=POS, sw=2, rx=8))
    p.append(text(s3_x + s3_w / 2, s3_y + 26, "STATE_MANUAL_HOLD", size=12, color=POS, bold=True))
    p.append(text(s3_x + s3_w / 2, s3_y + 48, "Повний ручний контроль (α = 1.0)", size=10, color=INK, bold=True))
    p.append(text(s3_x + s3_w / 2, s3_y + 68, "• Прямий відгук на стіки", size=9.5, color=MUTED))
    p.append(text(s3_x + s3_w / 2, s3_y + 88, "• Стабілізований / кутовий контур", size=9.5, color=MUTED))

    # Стан 4: HANDBACK_WAIT
    s4_x, s4_y, s4_w, s4_h = 610, 265, 210, 110
    p.append(rect(s4_x, s4_y, s4_w, s4_h, fill=AMBERBG, stroke=AMBER, sw=2, rx=8))
    p.append(text(s4_x + s4_w / 2, s4_y + 26, "STATE_HANDBACK_WAIT", size=12, color=AMBERTX, bold=True))
    p.append(text(s4_x + s4_w / 2, s4_y + 48, "Очікування центровки стіків", size=10, color=INK, bold=True))
    p.append(text(s4_x + s4_w / 2, s4_y + 68, "• Стіки в Deadband (< 12%)", size=9.5, color=MUTED))
    p.append(text(s4_x + s4_w / 2, s4_y + 88, "• Таймер T_hold рахує 1.5 с", size=9.5, color=MUTED))

    # Стан 5: BLENDING_OUT
    s5_x, s5_y, s5_w, s5_h = 325, 265, 210, 110
    p.append(rect(s5_x, s5_y, s5_w, s5_h, fill=GREENBG, stroke=FIELD, sw=2, rx=8))
    p.append(text(s5_x + s5_w / 2, s5_y + 26, "STATE_BLENDING_OUT", size=12, color=FIELD, bold=True))
    p.append(text(s5_x + s5_w / 2, s5_y + 48, "Повернення авторитету", size=10, color=INK, bold=True))
    p.append(text(s5_x + s5_w / 2, s5_y + 68, "• 1.0 > α > 0.0 (Ramp down)", size=9.5, color=MUTED))
    p.append(text(s5_x + s5_w / 2, s5_y + 88, "• Синхронізація уставки Setpoint", size=9.5, color=MUTED))

    # Стрілки переходів
    # S1 -> S2: |stick| > Deadband
    p.append(arrow(s1_x + s1_w + 4, s1_y + 55, s2_x - 4, s2_y + 55, color=AMBERTX, sw=2))
    p.append(text((s1_x + s1_w + s2_x) / 2, s1_y + 45, "|stick| > 12%", size=9.5, color=AMBERTX, bold=True))

    # S2 -> S3: alpha == 1.0
    p.append(arrow(s2_x + s2_w + 4, s2_y + 55, s3_x - 4, s3_y + 55, color=POS, sw=2))
    p.append(text((s2_x + s2_w + s3_x) / 2, s2_y + 45, "α = 1.0", size=9.5, color=POS, bold=True))

    # S3 -> S4: |stick| <= Deadband
    p.append(arrow(s3_x + s3_w / 2, s3_y + s3_h + 4, s4_x + s4_w / 2, s4_y - 4, color=AMBERTX, sw=2))
    p.append(text(s3_x + s3_w / 2 + 55, (s3_y + s3_h + s4_y) / 2, "|stick| < 12%", size=9.5, color=AMBERTX, bold=True))

    # S4 -> S3 (якщо знову смикнув стік): |stick| > Deadband
    p.append(arrow(s4_x + 30, s4_y - 4, s3_x + 30, s3_y + s3_h + 4, color=POS, sw=1.6))
    p.append(text(s4_x + 12, (s3_y + s3_h + s4_y) / 2, "Стік > 12%", size=9.5, color=POS))

    # S4 -> S5: timer >= T_hold
    p.append(arrow(s4_x - 4, s4_y + 55, s5_x + s5_w + 4, s5_y + 55, color=FIELD, sw=2))
    p.append(text((s4_x + s5_x + s5_w) / 2, s4_y + 45, "t ≥ T_hold", size=9.5, color=FIELD, bold=True))

    # S5 -> S1: alpha == 0.0
    p.append(arrow(s5_x - 4, s5_y + 55, s1_x + s1_w / 2, s1_y + s1_h + 4, color=NEG, sw=2))
    p.append(text(s1_x + s1_w / 2 + 60, s5_y + 20, "α = 0.0 (Auto OK)", size=9.5, color=NEG, bold=True))

    # Нижній висновок
    p.append(rect(40, 400, 780, 28, fill=FILL, stroke=LINE, sw=1.2, rx=5))
    p.append(text(W / 2, 418, "Автомат гарантує нерозривність керування: жодна комбінація дій не залишає приводи без командного сигналу", size=9.8, color=INK, bold=True))

    render(os.path.join(OUT, "takeover-state-machine.svg"), W, H, *p,
           title="Скінченний автомат перехоплення керування")


def main():
    fig_takeover_mechanisms()
    fig_integrator_windup()
    fig_smooth_blending()
    fig_takeover_fsm()
    print("Усі 4 фігури успішно згенеровано.")

if __name__ == "__main__":
    main()
