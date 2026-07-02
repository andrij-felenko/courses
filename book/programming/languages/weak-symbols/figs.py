# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── strong-weak: правило розв'язання за силою ─────────────────────────────────
# Ідея: те саме ім'я дають сильне й слабке визначення — лінкер бере сильне,
# слабке мовчки відкидає (без multiple definition). Лишилось саме слабке — беруть його.

def fig_strong_weak():
    W, H = 720, 340
    p = []

    # ── ліва сцена: сильне vs слабке → перемагає сильне ──
    p.append(text(200, 74, "те саме ім'я — двічі", size=13, bold=True, color=INK))

    p.append(fitbox(70, 96, 260, 46, "СИЛЬНЕ визначення\nvoid SysTick_Handler(){…}",
                    size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))
    p.append(fitbox(70, 168, 260, 46, "СЛАБКЕ визначення\n__attribute__((weak)) …",
                    size=11, bold=True, fill="#eef4ff", stroke=NEG, color=NEG))

    # лінкер обирає
    p.append(arrow(330, 119, 392, 150, color=POS, sw=2.2))
    p.append(arrow(330, 191, 392, 160, color=MUTED, sw=1.4, ))
    pick, pw, ph = textbox(470, 155, "лінкер бере\nСИЛЬНЕ", size=12, bold=True,
                           fill="#eafaf0", stroke=FIELD, color=FIELD, min_w=130)
    p.append(pick)
    p.append(text(200, 236, "слабке мовчки відкинуто — без «multiple definition»",
                  size=10, color=MUTED, italic=True))

    # ── права підказка: лише слабке ──
    p.append(line(W / 2 + 20, 96, W / 2 + 20, 250, color=MUTED, sw=1.0, dash="4 4"))
    p.append(text(600, 286, "а якщо сильного нема —", size=11, color=INK))
    p.append(fitbox(500, 300, 200, 32, "лишається слабке → його й беруть",
                    size=10, bold=True, fill="#eef4ff", stroke=NEG, color=NEG))

    render(os.path.join(OUT, "strong-weak.svg"), W, H, *p,
           title="Сила символу: сильне перемагає слабке, слабке поступається")


# ── override: таблиця векторів — слабкі заглушки vs ваш сильний обробник ───────
# Ідея: усі обробники — слабкі псевдоніми Default_Handler; ваш сильний
# SysTick_Handler перекриває свій запис, решта лишаються на заглушці.

def fig_override():
    W, H = 720, 360
    p = []

    # таблиця векторів (ліворуч)
    vx, vy, vw = 60, 84, 210
    rows = ["NMI_Handler", "HardFault_Handler", "SysTick_Handler",
            "USART1_IRQHandler", "TIM2_IRQHandler"]
    rh = 40
    p.append(text(vx + vw / 2, vy - 14, "таблиця векторів", size=12, bold=True))
    rpos = []
    for i, nm in enumerate(rows):
        y = vy + i * (rh + 8)
        hot = (nm == "SysTick_Handler")
        p.append(fitbox(vx, y, vw, rh, nm, size=10, bold=hot,
                        fill="#eafaf0" if hot else FILL,
                        stroke=FIELD if hot else MUTED,
                        color=FIELD if hot else INK))
        rpos.append((vx + vw, y + rh / 2, hot))

    # заглушка Default_Handler (праворуч зверху)
    dh, dw = 44, 210
    dx, dy = 470, 96
    p.append(fitbox(dx, dy, dw, dh, "Default_Handler\nwhile(1){} — пастка",
                    size=10, bold=True, fill="#fdf6e3", stroke="#b79a5e", color="#8a6a14"))

    # ваш сильний обробник (праворуч знизу)
    ux, uy = 470, 250
    p.append(fitbox(ux, uy, dw, dh, "ваш SysTick_Handler\n(сильний — перекриває)",
                    size=10, bold=True, fill="#fdecea", stroke=POS, color=POS))

    # стрілки: усі слабкі записи → Default_Handler; гарячий → ваш
    for rx, ry, hot in rpos:
        if hot:
            p.append(arrow(rx + 4, ry, ux, uy + dh / 2, color=POS, sw=2.4))
        else:
            p.append(arrow(rx + 4, ry, dx, dy + dh / 2, color=MUTED, sw=1.3))

    p.append(text(W / 2, H - 16,
                  "написав свій обробник → лінкер вписав його адресу; решта — на заглушці",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "override.svg"), W, H, *p,
           title="Перекриття обробника: сильний стає на місце слабкого псевдоніма")


# ── weak-ref: слабке посилання — модуль є / модуля нема ────────────────────────
# Ідея: слабке посилання при відсутності цілі = адреса 0 (не помилка);
# if(fn) дивиться на адресу — є модуль → виклик, нема → тихо пропущено.

def fig_weak_ref():
    W, H = 720, 300
    p = []

    # центральний код-виклик
    cx = W / 2
    call, cw, ch = textbox(cx, 96, "if (optional_logger_init)\n    optional_logger_init();",
                           size=11, bold=True, fill=BG, stroke=INK, min_w=280)
    p.append(call)
    p.append(text(cx, 138, "перевірка дивиться на саму АДРЕСУ символу", size=10, color=MUTED))

    # ліва гілка: модуль долучено
    lx, ly = 150, 210
    p.append(fitbox(lx - 110, ly, 220, 44, "модуль у збірці\nадреса справжня → виклик іде",
                    size=10, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD))
    p.append(arrow(cx - 60, 118, lx, ly, color=FIELD, sw=2.0))

    # права гілка: модуля нема
    rx, ry = 570, 210
    p.append(fitbox(rx - 110, ry, 220, 44, "модуля нема\nадреса 0 → виклик пропущено",
                    size=10, bold=True, fill="#eef4ff", stroke=NEG, color=NEG))
    p.append(arrow(cx + 60, 118, rx, ry, color=NEG, sw=2.0))

    p.append(text(cx, H - 16,
                  "слабке посилання: нема цілі — не помилка, а нуль; той самий код працює обома способами",
                  size=10, color=MUTED, italic=True))

    render(os.path.join(OUT, "weak-ref.svg"), W, H, *p,
           title="Слабке посилання: необов'язкова залежність без #ifdef")


if __name__ == "__main__":
    fig_strong_weak()
    fig_override()
    fig_weak_ref()
    print("OK: figures written to", OUT)
