# -*- coding: utf-8 -*-
import sys, os

# Додаємо шлях до scripts/ у корені репо
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

def path(d, stroke=LINE, sw=1.5, fill="none", dash=None):
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}"{d_attr}/>'

def polyline(pts, color=LINE, sw=1.5, dash=None):
    pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    d_attr = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<polyline points="{pts_str}" stroke="{color}" stroke-width="{sw}" fill="none"{d_attr}/>'

def dashed_rect(x, y, w, h, fill=FILL, stroke=LINE, sw=1.5, rx=6, dash="4,4"):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="%s" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>' % (x, y, w, h, rx, fill, stroke, sw, dash))


# ── Фігура 1: Наскрізний конвеєр протитиску (End-to-End Backpressure Pipeline) ─
def fig_end_to_end_pipeline():
    W, H = 1000, 580
    frags = []

    # Заголовок
    frags.append(text(500, 30, "Наскрізний ланцюг передачі протитиску через шари розподіленої системи", size=16, bold=True))

    # Прямий потік даних (Data Flow - синій) зверху
    frags.append(rect(60, 60, 880, 40, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(arrow(80, 80, 920, 80, color=NEG, sw=2.5))
    frags.append(text(500, 75, "Прямий потік даних: Клієнт → Шлюз → Сервіс прийому → Воркер → База даних", size=12, bold=True, color=NEG))

    # Вузли системи (5 блоків горизонтально)
    nodes = [
        ("Клієнт / SDK", "Мережевий буфер\nTCP send buffer", 140, 170),
        ("Шлюз (Proxy)", "Envoy / Nginx\nreadDisable(true)", 320, 170),
        ("Сервіс прийому", "gRPC / Netty\nStream Window = 0", 500, 170),
        ("Воркер обробки", "Обмежений буфер\nHigh Watermark", 680, 170),
        ("База даних / Sink", "LSM Compaction\nI/O Затримка", 860, 170),
    ]

    for title, desc, cx, cy in nodes:
        is_slow = ("База" in title)
        bg_col = "#fef2f2" if is_slow else "#ffffff"
        bd_col = POS if is_slow else LINE
        b_svg, bw, bh = textbox(cx, cy, f"{title}\n{desc}", size=11, pad=10, fill=bg_col, stroke=bd_col, sw=1.5, min_w=150)
        frags.append(b_svg)

    # Зворотний потік протитиску (Backpressure Flow - червоний) знизу
    frags.append(rect(60, 245, 880, 40, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(arrow(920, 265, 80, 265, color=POS, sw=2.5))
    frags.append(text(500, 260, "Зворотний сигнал протитиску (Flow Control): зменшення кредитів, пауза читання, TCP ZeroWindow", size=12, bold=True, color=POS))

    # Стрілки протитиску між блоками з підписами
    hops = [
        (860, 680, "1. Затримка I/O\nчерга заповнюється", 335),
        (680, 500, "2. High Watermark\nrequest(0) / Pause", 415),
        (500, 320, "3. WINDOW_UPDATE=0\nHTTP/2 Stream Pause", 335),
        (320, 140, "4. readDisable(true)\nTCP ZeroWindow (win=0)", 415),
    ]

    for x_from, x_to, lbl, y_lbl in hops:
        frags.append(arrow(x_from - 70, y_lbl, x_to + 70, y_lbl, color=POS, sw=1.8))
        frags.append(textbox((x_from + x_to) / 2, y_lbl - 24, lbl, size=10, pad=5, fill="#fff7ed", stroke="#f97316", sw=1)[0])

    # Підсумок у нижній панелі
    frags.append(rect(60, 495, 880, 60, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=6))
    frags.append(text(500, 517, "Результат наскрізного узгодження швидкості:", size=12, bold=True, color=FIELD))
    frags.append(text(500, 539, "Клієнт примусово знижує темп генерації на джерелі — жоден проміжний вузол не переповнює пам'ять і не падає з OOM.", size=11, color=INK))

    return render(os.path.join(IMG, 'end-to-end-backpressure-pipeline.svg'), W, H, *frags)


# ── Фігура 2: Моделі передачі даних (Push vs Poll vs Credit-Based) ─────────────
def fig_credit_based_flow_control():
    W, H = 1000, 500
    frags = []

    frags.append(text(500, 26, "Порівняння моделей передачі: Push, Наївний Poll та Кредитний потік", size=15, bold=True))

    # Стовпчик 1: Некерований Push
    frags.append(rect(40, 50, 280, 425, fill="#ffffff", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(180, 75, "1. Некерований Push", size=13, bold=True, color=POS))
    
    frags.append(textbox(180, 115, "Джерело (Producer)\nШле без обмежень", size=11, pad=8, fill="#eff6ff", stroke=NEG)[0])
    frags.append(arrow(180, 145, 180, 215, color=NEG, sw=2))
    frags.append(text(185, 180, "data(1..10000)", size=10, color=NEG, anchor="start"))
    
    frags.append(textbox(180, 250, "Одержувач (Consumer)\nБуфер переповнюється", size=11, pad=8, fill="#fef2f2", stroke=POS)[0])
    
    frags.append(rect(55, 305, 250, 155, fill="#fef2f2", stroke=POS, sw=1, rx=6))
    frags.append(text(180, 325, "Наслідки перевантаження:", size=11, bold=True, color=POS))
    frags.append(text(180, 350, "• Буфер росте без меж", size=10, color=INK))
    frags.append(text(180, 372, "• OOM-crash / скидання даних", size=10, color=INK))
    frags.append(text(180, 394, "• Падіння стабільності мережі", size=10, color=INK))
    frags.append(text(180, 420, "Швидкість диктує джерело!", size=10, bold=True, color=POS))

    # Стовпчик 2: Наївний Poll
    frags.append(rect(360, 50, 280, 425, fill="#ffffff", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(500, 75, "2. Наївний Poll (Опитування)", size=13, bold=True, color="#d97706"))

    frags.append(textbox(500, 115, "Джерело / Брокер\nЗберігає чергу", size=11, pad=8, fill="#f4f6f8", stroke=LINE)[0])
    frags.append(arrow(470, 215, 470, 145, color=LINE, sw=1.5))
    frags.append(text(465, 180, "poll() запит", size=10, color=MUTED, anchor="end"))
    frags.append(arrow(530, 145, 530, 215, color=NEG, sw=1.5))
    frags.append(text(535, 180, "відповідь з даними", size=10, color=NEG, anchor="start"))
    
    frags.append(textbox(500, 250, "Одержувач (Consumer)\nОпитує у циклі", size=11, pad=8, fill="#fff7ed", stroke="#f97316")[0])

    frags.append(rect(375, 305, 250, 155, fill="#fffbeb", stroke="#f59e0b", sw=1, rx=6))
    frags.append(text(500, 325, "Властивості опитування:", size=11, bold=True, color="#b45309"))
    frags.append(text(500, 350, "• Безпечно від переповнення", size=10, color=INK))
    frags.append(text(500, 372, "• Зайві RTT на кожну пачку", size=10, color=INK))
    frags.append(text(500, 394, "• Марні пусті запити (Spin)", size=10, color=INK))
    frags.append(text(500, 420, "Висока затримка доставки!", size=10, bold=True, color="#b45309"))

    # Стовпчик 3: Кредитний потік (Credit-based)
    frags.append(rect(680, 50, 280, 425, fill="#ffffff", stroke="#d1d5db", sw=1, rx=8))
    frags.append(text(820, 75, "3. Кредитний потік (Reactive)", size=13, bold=True, color=FIELD))

    frags.append(textbox(820, 115, "Джерело (Publisher)\nМає баланс: credit = N", size=11, pad=8, fill="#eff6ff", stroke=NEG)[0])
    frags.append(arrow(790, 215, 790, 145, color=FIELD, sw=1.8))
    frags.append(text(785, 180, "request(N)", size=10, bold=True, color=FIELD, anchor="end"))
    frags.append(arrow(850, 145, 850, 215, color=NEG, sw=1.8))
    frags.append(text(855, 180, "N подій (onNext)", size=10, color=NEG, anchor="start"))

    frags.append(textbox(820, 250, "Одержувач (Subscriber)\nВидає точні кредити", size=11, pad=8, fill="#f0fdf4", stroke=FIELD)[0])

    frags.append(rect(695, 305, 250, 155, fill="#f0fdf4", stroke=FIELD, sw=1, rx=6))
    frags.append(text(820, 325, "Ідеальний баланс:", size=11, bold=True, color=FIELD))
    frags.append(text(820, 350, "• Нульовий ризик OOM", size=10, color=INK))
    frags.append(text(820, 372, "• Потокова передача без пауз", size=10, color=INK))
    frags.append(text(820, 394, "• Максимальна утилізація BDP", size=10, color=INK))
    frags.append(text(820, 420, "Швидкість диктує споживач!", size=10, bold=True, color=FIELD))

    return render(os.path.join(IMG, 'credit-based-flow-control.svg'), W, H, *frags)


# ── Фігура 3: Гістерезис водяних знаків (Watermark Hysteresis) ─────────────────
def fig_watermark_hysteresis():
    W, H = 960, 480
    frags = []

    frags.append(text(480, 26, "Гістерезис буфера: запобігання флапінгу через High і Low Watermarks", size=15, bold=True))

    # Вісь часу та заповненості буфера
    ox, oy = 90, 410
    frags.append(arrow(ox, oy, 900, oy, color=LINE, sw=1.8)) # X
    frags.append(arrow(ox, oy, ox, 70, color=LINE, sw=1.8))   # Y

    frags.append(text(890, oy + 28, "Час (t)", size=11, color=MUTED, anchor="end"))
    frags.append(text(ox - 10, 65, "Рівень заповнення буфера (байтів / елементів)", size=11, color=MUTED, anchor="end"))

    # Пороги (Лінії)
    # Повна місткість Buffer Capacity
    frags.append(line(ox, 110, 870, 110, color=POS, sw=1.5, dash="4,4"))
    frags.append(text(875, 114, "Максимальна місткість буфера (Buffer Capacity)", size=10, bold=True, color=POS, anchor="start"))

    # High Watermark (Пауза)
    frags.append(line(ox, 160, 870, 160, color="#d97706", sw=1.5, dash="4,4"))
    frags.append(text(875, 164, "High Watermark (HWM: 80%) → СИГНАЛ ПАУЗИ", size=10, bold=True, color="#d97706", anchor="start"))

    # Low Watermark (Відновлення)
    frags.append(line(ox, 290, 870, 290, color=FIELD, sw=1.5, dash="4,4"))
    frags.append(text(875, 294, "Low Watermark (LWM: 30%) → ВІДНОВЛЕННЯ", size=10, bold=True, color=FIELD, anchor="start"))

    # Зона гістерезису
    frags.append(rect(ox + 2, 160, 778, 130, fill="#f8fafc", stroke="none"))
    frags.append(text(480, 225, "Зона гістерезису (Hysteresis Window): перемикання станів заблоковано", size=11, bold=True, color="#64748b"))

    # Крива заповнення буфера
    pts = [
        (90, 400), (160, 360), (240, 280), (320, 160), # досягли HWM
        (380, 135), # вхідні ще летять через RTT, але зупиняються до Capacity
        (460, 210), (540, 290), # розвантажилися до LWM
        (580, 320), # відновили читання
        (660, 250), (740, 160), # знову підйом до HWM
        (780, 140), (840, 230)
    ]
    frags.append(polyline(pts, color=NEG, sw=3))

    # Точки перемикання станів
    # 1. HWM Pause
    frags.append(circle(320, 160, 5, fill=POS, stroke="#ffffff", sw=1.5))
    frags.append(textbox(320, 100, "1. HWM досягнуто!\nВимкнення EPOLLIN / Stop", size=9, pad=5, fill="#fef2f2", stroke=POS)[0])

    # 2. In-flight absorption
    frags.append(circle(380, 135, 4, fill="#f97316", stroke="#ffffff", sw=1.5))
    frags.append(textbox(380, 70, "Поглинання in-flight пакетів\n(Запас RTT × BDP)", size=9, pad=5, fill="#fff7ed", stroke="#f97316")[0])

    # 3. LWM Resume
    frags.append(circle(540, 290, 5, fill=FIELD, stroke="#ffffff", sw=1.5))
    frags.append(textbox(540, 355, "2. LWM досягнуто!\nУвімкнення EPOLLIN / Resume", size=9, pad=5, fill="#f0fdf4", stroke=FIELD)[0])

    # 4. HWM Pause 2
    frags.append(circle(740, 160, 5, fill=POS, stroke="#ffffff", sw=1.5))
    frags.append(textbox(740, 100, "3. HWM досягнуто!\nПовторна пауза", size=9, pad=5, fill="#fef2f2", stroke=POS)[0])

    return render(os.path.join(IMG, 'watermark-hysteresis-oscillation.svg'), W, H, *frags)


# ── Фігура 4: Мультиплексоване блокування потоків (HTTP/2 Stream Flow Control) ─
def fig_multiplexed_flow_control():
    W, H = 1000, 500
    frags = []

    frags.append(text(500, 26, "Мультиплексування в HTTP/2 та HTTP/3: ізоляція протитиску між потоками", size=15, bold=True))

    # Загальне з'єднання TCP / QUIC (Зовнішній контур)
    frags.append(dashed_rect(60, 55, 880, 370, fill="#ffffff", stroke="#9ca3af", sw=1.5, rx=8, dash="6,6"))
    frags.append(text(190, 75, "Фізичне з'єднання TCP / QUIC (Connection Window)", size=11, bold=True, color=MUTED))

    # Потік 1: Повільний потік (Heavy Download / Compacting Table)
    frags.append(rect(80, 95, 840, 95, fill="#fef2f2", stroke=POS, sw=1.5, rx=6))
    frags.append(text(100, 120, "Потік #1 (Stream 1: Великий експорт / важкий звіт)", size=11, bold=True, color=POS, anchor="start"))
    frags.append(textbox(320, 150, "Одержувач зайнятий:\nStream Window = 0 байтів", size=10, pad=6, fill="#ffffff", stroke=POS)[0])
    frags.append(textbox(640, 150, "Джерело ПРИЗУПИНЕНО:\nЧекає WINDOW_UPDATE", size=10, pad=6, fill="#fee2e2", stroke=POS)[0])
    frags.append(arrow(410, 150, 540, 150, color=POS, sw=1.8))

    # Потік 2: Швидкий потік (Критичний RPC / Heartbeat / Healthcheck)
    frags.append(rect(80, 210, 840, 95, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    frags.append(text(100, 235, "Потік #2 (Stream 3: Критичний RPC / Оплата / Heartbeat)", size=11, bold=True, color=FIELD, anchor="start"))
    frags.append(textbox(320, 265, "Одержувач вільний:\nStream Window = 64 КБ", size=10, pad=6, fill="#ffffff", stroke=FIELD)[0])
    frags.append(textbox(640, 265, "Джерело ПЕРЕДАЄ:\nПовна швидкість", size=10, pad=6, fill="#dcfce7", stroke=FIELD)[0])
    frags.append(arrow(540, 265, 410, 265, color=FIELD, sw=2))

    # Потік 3: Потік #3
    frags.append(rect(80, 320, 840, 90, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(100, 345, "Потік #3 (Stream 5: Стандартний запит API Gateway)", size=11, bold=True, color=NEG, anchor="start"))
    frags.append(textbox(320, 375, "Одержувач готовий:\nStream Window = 32 КБ", size=10, pad=6, fill="#ffffff", stroke=NEG)[0])
    frags.append(textbox(640, 375, "Джерело ПЕРЕДАЄ:\nШтатний режим", size=10, pad=6, fill="#dbeafe", stroke=NEG)[0])
    frags.append(arrow(540, 375, 410, 375, color=NEG, sw=2))

    # Нижній висновок
    frags.append(rect(60, 435, 880, 48, fill="#f8fafc", stroke=LINE, sw=1, rx=6))
    frags.append(text(500, 455, "Перевага роздільного контролю потоку на рівні Stream:", size=11, bold=True, color=INK))
    frags.append(text(500, 470, "Зупинка Потоку #1 не викликає блокування голови черги (Head-of-Line Blocking) для Потоку #2 та Потоку #3.", size=10, color=MUTED))

    return render(os.path.join(IMG, 'multiplexed-ho-blocking-http2.svg'), W, H, *frags)


def main():
    fig_end_to_end_pipeline()
    fig_credit_based_flow_control()
    fig_watermark_hysteresis()
    fig_multiplexed_flow_control()
    print("Всі фігури успішно згенеровано.")

if __name__ == '__main__':
    main()
