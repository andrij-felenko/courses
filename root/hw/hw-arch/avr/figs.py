# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── datapath: гарвардський тракт AVR, де майже кожна інструкція = один такт ─────
# Ідея: дві окремі шини (код / дані) сходяться на 32-регістровому файлі й АЛП;
# під'єднаний дворівневий конвеєр (вибірка наступної, поки виконується поточна)
# дає чесний такт. Це те, що дозволяє рахувати час олівцем.

def fig_datapath():
    W, H = 720, 360
    p = []

    # дві пам'яті — окремі шини (гарвардська риса)
    fb, fw, fh = (40, 70, 64)
    p.append(fitbox(fb, fw, 150, fh, "Flash\n(програма)", size=13, bold=True,
                    fill="#eef4ff", stroke=NEG, sw=1.8))
    db, dw, dh = (40, 226, 64)
    p.append(fitbox(db, dw, 150, dh, "SRAM\n(дані)", size=13, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.8))

    # 32-регістровий файл — серце, куди сходяться обидві шини
    rx, ry, rw, rh = (300, 120, 150, 120)
    p.append(rect(rx, ry, rw, rh, fill="#f6f4ec", stroke=INK, sw=2))
    p.append(text(rx + rw / 2, ry + 26, "32 регістри", size=13, bold=True))
    p.append(text(rx + rw / 2, ry + 46, "R0 … R31", size=11, color=MUTED))
    # натяк на регістрову «драбинку»
    for i in range(6):
        yy = ry + 60 + i * 9
        p.append(line(rx + 18, yy, rx + rw - 18, yy, color="#cfc9b4", sw=1.0))

    # АЛП праворуч — два входи з регістрів, один такт
    ax, ay, aw_, ah_ = (560, 150, 120, 60)
    p.append(fitbox(ax, ay, aw_, ah_, "АЛП\n8-біт", size=13, bold=True,
                    fill="#fdecea", stroke=POS, sw=1.8))

    # шина коду: Flash → регістри/декодер
    p.append(arrow(fb + 150, fw + fh / 2, rx, ry + 36, color=NEG, sw=2.0))
    p.append(text(245, 120, "шина коду", size=10, color=NEG, anchor="middle"))
    # шина даних: SRAM ↔ регістри
    p.append(arrow(db + 150, dw + dh / 2, rx, ry + rh - 30, color=FIELD, sw=2.0))
    p.append(text(245, 250, "шина даних", size=10, color=FIELD, anchor="middle"))

    # регістри → АЛП (два операнди) і назад (результат)
    p.append(arrow(rx + rw, ry + 36, ax, ay + 16, color=INK, sw=1.8))
    p.append(arrow(rx + rw, ry + rh - 36, ax, ay + ah_ - 16, color=INK, sw=1.8))
    p.append(text((rx + rw + ax) / 2, ry + 12, "2 операнди", size=10, color=MUTED))
    # результат назад у регістр (дуга під АЛП)
    p.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" '
             'stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
             % (ax, ay + ah_ - 8, ax - 40, ay + ah_ + 50,
                rx + rw / 2, ry + rh + 60, rx + rw / 2, ry + rh, INK))
    p.append(text((ax + rx) / 2, ay + ah_ + 56, "результат → регістр (1 такт)",
                  size=10, color=INK, anchor="middle"))

    # конвеєр-натяк угорі: вибірка наступної, поки виконується поточна
    cy = 40
    p.append(rect(300, cy - 16, 380, 26, fill="#f4f6f8", stroke=MUTED, sw=1.2))
    p.append(text(490, cy + 2, "конвеєр: вибірка наступної ∥ виконання поточної",
                  size=10, color=MUTED))

    render(os.path.join(OUT, "datapath.svg"), W, H, *p,
           title="Гарвардський тракт AVR: майже кожна інструкція — один такт")


# ── clock-budget: чому такт рахується на AVR і ні — на МК під RTOS ─────────────
# Ідея: дві смуги однакової «роботи». На AVR кожна інструкція — рівний блок
# фіксованої довжини, сума передбачувана. На потужному МК під RTOS ту саму
# роботу рвуть промахи кешу, конвеєр і перемикання контексту — довжина «плаває».

def fig_clock_budget():
    W, H = 720, 320
    p = []
    bx, bw = 70, 580

    # ── смуга AVR: однакові блоки = чесний такт ──
    ay = 90
    p.append(text(bx, ay - 14, "AVR: однакові такти → сума передбачувана",
                  size=12, color=FIELD, anchor="start", bold=True))
    seg = bw / 8
    for i in range(8):
        p.append(rect(bx + i * seg, ay, seg - 3, 40, fill="#eafaf0",
                      stroke=FIELD, sw=1.4, rx=3))
        p.append(text(bx + i * seg + seg / 2, ay + 25, "1", size=12, color=FIELD, bold=True))
    p.append(text(bx + bw + 8, ay + 25, "= N тактів", size=11, color=FIELD, anchor="start"))

    # ── смуга МК під RTOS: нерівні блоки + розриви ──
    ry = 200
    p.append(text(bx, ry - 14, "МК під RTOS: кеш, конвеєр, перемикання → довжина «плаває»",
                  size=12, color=POS, anchor="start", bold=True))
    # нерівні блоки роботи
    widths = [0.10, 0.07, 0.22, 0.05, 0.14, 0.09, 0.18, 0.06]
    gap = 0.0
    x = bx
    labels = {2: "промах\nкешу", 6: "перемикання\nконтексту"}
    for i, frac in enumerate(widths):
        w = bw * frac
        fill = "#fdecea" if i in labels else "#fbe3e0"
        p.append(rect(x, ry, w - 2, 40, fill=fill, stroke=POS, sw=1.3, rx=3))
        if i in labels:
            p.append(mtext(x + w / 2, ry - 4 if i == 2 else ry + 56, labels[i],
                           size=9, color=POS))
        x += w
    p.append(text(bx + bw + 8, ry + 25, "= ?", size=13, color=POS, anchor="start", bold=True))

    p.append(text(W / 2, H - 18,
                  "та сама робота: на AVR її довжину рахуєш олівцем, під RTOS — ні",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "clock-budget.svg"), W, H, *p,
           title="Чому затримку рахуєш на AVR, а на МК під RTOS — ні")


# ── one-clock-one-instruction (hist): CISC/8051 проти AVR ──────────────────────
# Ідея: ті самі МГц, зовсім різна робота за такт. 8051 розтягує одну операцію
# на 12 тактів кварцу й має мало регістрів; AVR через короткий конвеєр і 32
# регістри робить ≈1 інструкцію за такт — звідси «олівець».

def fig_one_clock():
    W, H = 800, 400
    p = []
    p.append(text(W / 2, 50, "ті самі МГц, зовсім різна робота за такт",
                  size=12, color=MUTED))

    # ── ліворуч: 8051 / CISC ──
    b, w_, _h = textbox(200, 88, "8051 / CISC-підхід", size=14, bold=True,
                        color=POS, fill="#fdecea", stroke=POS, sw=2)
    p.append(b)
    # 12 тактів кварцу на одну операцію
    for i in range(12):
        x = 51.5 + i * 25
        p.append(rect(x, 125, 22, 24, fill="#ffc0b8", stroke=POS, sw=1.0, rx=3))
        p.append(text(x + 11, 140, str(i + 1), size=9))
    p.append(text(200, 163, "12 тактів кварцу", size=11, color=POS, bold=True))
    p.append(text(200, 177, "= 1 машинна операція", size=11, color=POS))
    p.append(text(200, 199, "Робочі регістри: 4–8 шт.", size=11, color=MUTED))
    p.append(text(200, 215, "Операнди часто через RAM", size=11, color=MUTED))
    p.append(fitbox(120, 224, 160, 42, "≈ 1 МГц → ~83 000 оп./с\n(÷12, оригінальний 8051)",
                    size=11, color=POS, fill="#fff0f0", stroke=POS, sw=1.2))

    # розділювач
    p.append(line(400, 70, 400, 380, color=MUTED, sw=1.0, dash="5 5"))
    p.append(fitbox(386, 75, 28, 26, "vs", size=14, color=MUTED, fill=BG, stroke=MUTED, sw=1.2))

    # ── праворуч: AVR / RISC ──
    b, w_, _h = textbox(600, 88, "AVR (RISC)", size=14, bold=True,
                        color=NEG, fill="#eaf0fd", stroke=NEG, sw=2)
    p.append(b)
    # двоступеневий конвеєр
    p.append(fitbox(505, 125, 90, 46, "Вибірка\n(Fetch)", size=11, fill="#d0e8ff", stroke=NEG, sw=1.5))
    p.append(arrow(595, 148, 605, 148, color=NEG, sw=1.5))
    p.append(fitbox(605, 125, 90, 46, "Виконання\n(Execute)", size=11, fill="#d0f0e8", stroke=NEG, sw=1.5))
    p.append(text(600, 185, "двоступеневий конвеєр", size=11, color=NEG, bold=True))
    p.append(text(600, 199, "~1 такт = 1 інструкція (більшість команд)", size=11, color=NEG))
    p.append(text(600, 221, "32 регістри загального призначення", size=11, color=NEG, bold=True))
    p.append(text(600, 237, "більшість операцій — регістр↔регістр", size=11, color=MUTED))
    p.append(fitbox(504, 246, 192, 42, "≈ 1 MIPS / МГц\nтакти рахуються олівцем",
                    size=11, color=NEG, fill="#eaf4ff", stroke=NEG, sw=1.2))

    # підсумок
    p.append(fitbox(110, 360, 580, 27,
                    "коротші однакові інструкції + конвеєр + 32 регістри = чесний, передбачуваний такт",
                    size=11, color=FIELD, fill="#f0faf0", stroke=FIELD, sw=1.5))

    render(os.path.join(OUT, "one-clock-one-instruction.svg"), W, H, *p,
           title="Чому олівець працює: CISC/8051 проти AVR")


# ── from-thesis-to-arduino (hist): чотири щаблі від задуму до масового чипа ─────
# Ідея: ланцюг NTH → Nordic VLSI → Atmel → Arduino; на кожному щаблі та сама
# наскрізна нитка «1 такт = 1 інструкція, ядро під C» наближається до тиражу.

def fig_thesis_to_arduino():
    W, H = 860, 380
    p = []
    p.append(text(W / 2, 50, "кожен щабель наближає ідею «такт-у-такт, дружню до C» до масового чипа",
                  size=12, color=MUTED))

    steps = [
        (48,  "NTH, Тронгейм",  "~1994–1996", INK,   "#f4f6f8",
         ["Боген + Воллан", "студентський задум:", "8-біт ядро під C,", "1 такт = 1 інструкція"]),
        (246, "Nordic VLSI",    "~1996–1997", NEG,   "#e8f4f8",
         ["µRISC — перший", "робочий кремній;", "задум стає", "реальним чипом"]),
        (444, "Atmel Norway",   "кін. 1990-х", FIELD, "#eef6ee",
         ["AVR + Flash;", "серія AT90S:", "ISP-прошивка", "без програматора"]),
        (642, "Arduino",        "2005+",       POS,   "#fff8e6",
         ["ATmega168/328:", "масове поширення,", "ціле покоління", "перших прошивок"]),
    ]
    bw, bh, top = 170, 130, 88
    for i, (x, title_, when, col, fill, lines) in enumerate(steps):
        p.append(rect(x, top, bw, bh, fill=fill, stroke=col, sw=2, rx=8))
        p.append(text(x + bw / 2, top - 12, when, size=11, color=MUTED))
        p.append(text(x + bw / 2, top + 24, title_, size=13, bold=True))
        for j, ln in enumerate(lines):
            p.append(text(x + bw / 2, top + 48 + j * 16, ln, size=10))
        if i > 0:
            px = steps[i - 1][0] + bw
            p.append(arrow(px, top + bh / 2, x - 2, top + bh / 2, color=INK, sw=2.0))

    # наскрізна нитка
    p.append(line(48, 340, 812, 340, color=FIELD, sw=2.5, dash="8 4"))
    p.append(fitbox(214, 348, 432, 26,
                    "наскрізна нитка: 1 такт = 1 інструкція, ядро під компілятор C",
                    size=12, color=FIELD, fill="#f0faf0", stroke=FIELD, sw=1.5))

    render(os.path.join(OUT, "from-thesis-to-arduino.svg"), W, H, *p,
           title="Від студентського задуму в Тронгеймі до серця Arduino")


# ── board-anatomy (comp): Uno/Nano-клас проти ESP32 DevKit, вузол за вузлом ─────
# Ідея: ті самі ролі вузлів обабіч пунктиру, але навколо 8-бітного AVR їх більше
# окремими деталями; ключова практична відмінність — рівні (5 В проти 3.3 В).

def fig_board_anatomy():
    W, H = 860, 520
    p = []
    p.append(fitbox(75, 17, 280, 34, "Uno/Nano-клас (AVR ATmega328P)", size=14, bold=True,
                    fill="#e8f4fd", stroke=NEG, sw=1.5))
    p.append(fitbox(583, 17, 124, 34, "ESP32 DevKit", size=14, bold=True,
                    fill="#edf7ed", stroke=FIELD, sw=1.5))
    p.append(line(430, 58, 430, 478, color=MUTED, sw=1.2, dash="6 4"))

    L, R = 215, 645
    rows = [
        (86, ["USB-UART міст", "FT232 / CH340-клас", "(або окремий 8U2/16U2 AVR)"],
             ["USB-UART міст", "CP210x / CH340-клас"]),
        (176, ["Зовнішній кварц 16 МГц", "(фіксована частота, без PLL)"],
              ["Кварц 40 МГц + PLL", "(до 240 МГц; всередині чипа)"]),
        (261, ["Лінійний стабілізатор", "(5 В або 3.3 В)"],
              ["LDO 3.3 В", "(AMS1117-клас)"]),
        (336, ["DIP-панелька", "(чип вийнятний)"],
              ["WROOM-модуль", "(чип назавжди припаяний)"]),
    ]
    for y, la, ra in rows:
        p.append(fitbox(L - 110, y, 220, 50, "\n".join(la), size=11,
                        fill="#e8f4fd", stroke=NEG, sw=1.4))
        p.append(fitbox(R - 110, y, 220, 50, "\n".join(ra), size=11,
                        fill="#edf7ed", stroke=FIELD, sw=1.4))
    # нижній рядок — рівні (акцент)
    p.append(fitbox(L - 95, 406, 190, 56, "Кнопка reset\n+ гребінки GPIO\n(рівні: переважно 5 В!)",
                    size=11, fill="#fef3e2", stroke=POS, sw=1.5))
    p.append(fitbox(R - 75, 406, 150, 56, "Кнопки EN + BOOT\n+ гребінки GPIO\n(рівні: 3.3 В!)",
                    size=11, fill="#edf7ed", stroke=FIELD, sw=1.4))

    p.append(fitbox(87, 482, 686, 27,
                    "навколо 8-бітного AVR — більше дискретних вузлів; у ESP32 USB-логіку й тактування глибше в чипі",
                    size=11, color=MUTED, fill="#f8f8f8", stroke=MUTED, sw=1.5))

    render(os.path.join(OUT, "board-anatomy.svg"), W, H, *p,
           title="Анатомія плати: Uno/Nano-клас проти ESP32 DevKit")


# ── integration-ladder (comp): сходи самодостатності плат ──────────────────────
# Ідея: та сама логіка «носія», різний рівень інтеграції — від Pro Mini (треба
# зовнішній перехідник) до ESP32 DevKit (усе на борту). Висота стовпця = ступінь.

def fig_integration_ladder():
    W, H = 820, 360
    p = []
    cols = [
        (20,  250, POS,   "#fdecea", ["Pro Mini-клас", "без USB", "(треба зовн. FTDI)"]),
        (225, 200, "#e67e22", "#fef9e7", ["Nano-клас", "USB на борту", "(під макетку)"]),
        (430, 150, FIELD, "#edf7ed", ["Uno-клас", "USB + шилд-роз'єм", "+ DIP-панелька"]),
        (635, 100, NEG,   "#e8f4fd", ["ESP32 DevKit", "USB + Wi-Fi/BLE", "у чипі", "авто-скидання"]),
    ]
    bw = 165
    base = 300
    for x, top, col, fill, lines in cols:
        h = base - top
        p.append(rect(x, top, bw, h, fill=fill, stroke=col, sw=2.0))
        for j, ln in enumerate(lines):
            p.append(text(x + bw / 2, top + 24 + j * 16, ln, size=12))
    p.append(arrow(60, 320, 760, 320, color=MUTED, sw=1.6))
    p.append(text(W / 2, 344, "рівень інтеграції / самодостатності →",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "integration-ladder.svg"), W, H, *p,
           title="Сходи самодостатності плат: від Pro Mini до ESP32 DevKit")


if __name__ == "__main__":
    fig_datapath()
    fig_clock_budget()
    fig_one_clock()
    fig_thesis_to_arduino()
    fig_board_anatomy()
    fig_integration_ladder()
    print("OK: figures written to", OUT)
