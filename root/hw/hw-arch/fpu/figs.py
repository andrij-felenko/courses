# -*- coding: utf-8 -*-
"""Фігури до теми «Блок дробових чисел (FPU)».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

GOLD = "#b9770e"     # тепле застереження / «проміжне»
PALE_R = "#fdecea"
PALE_B = "#eaf0fd"
PALE_G = "#eaf7ee"
PALE_Y = "#fbf4e6"


# ── 1. Що робить FPU за одну операцію: вирівняти · порахувати · нормалізувати · округлити
def fig_work():
    W, H = 760, 372
    f = []
    steps = [("вирівняти", "порядки", NEG,
              "менший порядок зсуваємо", "до більшого — коми в ряд"),
             ("порахувати", "мантиси", FIELD,
              "тепер це просто ціле", "додавання/множення"),
             ("нормалізувати", "результат", GOLD,
              "повернути вигляд 1.xxxx —", "зсув + правка порядку"),
             ("округлити", "надлишок", POS,
              "зайві біти зрізати за", "правилом до парного")]
    x0, w, gap = 44, 158, 14
    for i, (a, b, col, l1, l2) in enumerate(steps):
        x = x0 + i * (w + gap)
        f.append(rect(x, 78, w, 118, fill="#fafafa", stroke=col, sw=1.8))
        f.append(text(x + w / 2, 106, a, size=14, color=col, bold=True))
        f.append(text(x + w / 2, 126, b, size=12, color=INK))
        f.append(text(x + w / 2, 156, l1, size=10, color=MUTED))
        f.append(text(x + w / 2, 172, l2, size=10, color=MUTED))
        if i < 3:
            f.append(arrow(x + w + 1, 137, x + w + gap - 1, 137, color=INK, sw=1.8))
    f.append(fitbox(44, 218, 672, 50,
                    "Оце чотири кроки на КОЖНЕ +, −, ×, ÷ над float.\n"
                    "FPU робить їх апаратно за один-кілька тактів;\n"
                    "без FPU ту саму логіку виконує програма — десятки тактів.",
                    size=12, fill=PALE_G, stroke=FIELD, sw=1.6))
    f.append(fitbox(44, 282, 672, 62,
                    "Чому цілий ALU так не вміє: у float число розкидане на три поля\n"
                    "(знак · порядок · мантиса), і перед арифметикою їх треба узгодити,\n"
                    "а після — зібрати назад. Це не одна дія, а маленька програма —\n"
                    "тож їй дали окреме залізо.",
                    size=12, fill=FILL, stroke=INK, sw=1.4))
    render(os.path.join(IMG, "work.svg"), W, H, *f,
           title="Що FPU робить за одну float-операцію")


# ── 2. Де живе FPU: ядро + окремий банк float-регістрів ──────────────────────
def fig_where():
    W, H = 720, 380
    f = []
    # процесор — велика рамка
    f.append(rect(48, 64, 624, 232, fill=BG, stroke=INK, sw=2))
    f.append(text(360, 88, "процесор (одна мікросхема)", size=13, color=MUTED, bold=True))
    # цілочисельне ядро
    f.append(rect(80, 108, 250, 168, fill=PALE_B, stroke=NEG, sw=1.8))
    f.append(text(205, 132, "цілочисельне ядро", size=13, color=NEG, bold=True))
    f.append(text(205, 158, "ALU · регістри r0…r15", size=11, color=INK))
    f.append(text(205, 182, "керує потоком, адресує", size=11, color=MUTED))
    f.append(text(205, 200, "пам'ять, дає команди FPU", size=11, color=MUTED))
    f.append(text(205, 236, "цілі та адреси —", size=11, color=INK))
    f.append(text(205, 254, "тут", size=11, color=INK, bold=True))
    # FPU
    f.append(rect(390, 108, 250, 168, fill=PALE_G, stroke=FIELD, sw=1.8))
    f.append(text(515, 132, "FPU (блок дробів)", size=13, color=FIELD, bold=True))
    f.append(text(515, 158, "суматор/множник float", size=11, color=INK))
    f.append(text(515, 182, "власний банк:", size=11, color=MUTED))
    f.append(text(515, 200, "s0…s31 (float-регістри)", size=11, color=INK, bold=True))
    f.append(text(515, 236, "дробові числа —", size=11, color=INK))
    f.append(text(515, 254, "окремо від цілих", size=11, color=INK, bold=True))
    # обмін
    f.append(arrow(330, 175, 390, 175, color=INK, sw=1.8))
    f.append(arrow(390, 205, 330, 205, color=INK, sw=1.8))
    f.append(text(360, 168, "команда", size=9.5, color=MUTED))
    f.append(text(360, 224, "результат", size=9.5, color=MUTED))
    f.append(fitbox(48, 316, 624, 50,
                    "FPU — не окремий комп'ютер, а спеціалізований підблок поряд із ядром,\n"
                    "зі СВОЇМИ регістрами. Ядро віддає йому дробову роботу й забирає відповідь.",
                    size=12, fill=FILL, stroke=INK, sw=1.4))
    render(os.path.join(IMG, "where.svg"), W, H, *f,
           title="Де живе FPU: поряд із ядром, зі своїми регістрами")


# ── 3. Hard-float vs soft-float: два шляхи тієї самої a*b+c ──────────────────
def fig_paths():
    W, H = 760, 372
    f = []
    f.append(text(200, 92, "hard-float (є FPU)", size=13, color=FIELD, bold=True))
    f.append(text(560, 92, "soft-float (немає FPU)", size=13, color=POS, bold=True))
    # спільний вихід
    f.append(fitbox(250, 108, 260, 34, "у коді: y = a * b + c;", size=12.5,
                    fill=PALE_Y, stroke=GOLD, sw=1.6))
    # hard
    f.append(rect(50, 156, 330, 120, fill="none", stroke=FIELD, sw=1.7))
    f.append(text(215, 180, "компілятор ставить", size=11.5, color=INK, bold=True))
    f.append(text(66, 206, "vmul.f32  s2, s0, s1", size=12, color=FIELD, anchor="start"))
    f.append(text(66, 226, "vadd.f32  s2, s2, s3", size=12, color=FIELD, anchor="start"))
    f.append(text(66, 256, "2 апаратні інструкції → одиниці тактів", size=10.5, color=MUTED, anchor="start"))
    # soft
    f.append(rect(400, 156, 310, 120, fill="none", stroke=POS, sw=1.7))
    f.append(text(555, 180, "компілятор кличе підпрограму", size=11, color=INK, bold=True))
    f.append(text(416, 206, "bl  __aeabi_fmul", size=12, color=POS, anchor="start"))
    f.append(text(416, 226, "bl  __aeabi_fadd", size=12, color=POS, anchor="start"))
    f.append(text(416, 256, "цілими зсувами й додаваннями → десятки тактів", size=10.5, color=MUTED, anchor="start"))
    f.append(fitbox(50, 294, 660, 62,
                    "Той самий рядок C. Прапорцем збірки (напр. -mfpu=fpv4-sp-d16 -mfloat-abi=hard) "
                    "ви кажете компілятору вживати інструкції FPU. Немає FPU або зібрано soft — і кожне "
                    "float-множення стає викликом бібліотечної функції.",
                    size=12, fill=FILL, stroke=INK, sw=1.4))
    render(os.path.join(IMG, "paths.svg"), W, H, *f,
           title="Один рядок C — два шляхи: апаратний FPU чи емуляція")


# ── 4. FPU у мікроконтролерах: є / нема, одинарна / подвійна ─────────────────
def fig_embedded():
    W, H = 760, 388
    f = []
    rows = [("Cortex-M0 / M0+ / M3", "немає FPU", "float — лише емуляцією", POS),
            ("Cortex-M4F", "одинарна (FPv4-SP)", "float швидко, double — емуляцією", FIELD),
            ("Cortex-M7", "одинарна + подвійна (FPv5)", "і float, і double апаратно", FIELD),
            ("8-бітні (AVR)", "немає FPU", "float дуже дорогий — беруть цілі", POS)]
    y = 84
    f.append(text(150, y, "ядро", size=11, color=MUTED, bold=True))
    f.append(text(415, y, "апаратна точність", size=11, color=MUTED, bold=True))
    f.append(text(632, y, "наслідок", size=11, color=MUTED, bold=True))
    y += 20
    for i, (core, prec, note, col) in enumerate(rows):
        f.append(rect(48, y, 664, 46, fill=("#f6f8f6" if i % 2 == 0 else BG),
                      stroke=MUTED, sw=1, rx=6))
        f.append(text(64, y + 29, core, size=12.5, color=INK, anchor="start", bold=True))
        f.append(text(300, y + 29, prec, size=12, color=col, anchor="start", bold=True))
        f.append(text(500, y + 29, note, size=11, color=INK, anchor="start"))
        y += 52
    f.append(fitbox(48, y + 6, 664, 52,
                    "Ключова пастка: навіть коли FPU Є, він часто ЛИШЕ одинарної точності.\n"
                    "Написали double — і на M4F воно тихо емулюється, повільно.\n"
                    "На МК float за замовчуванням означає float32.",
                    size=12, fill=PALE_R, stroke=POS, sw=1.6))
    render(os.path.join(IMG, "embedded.svg"), W, H, *f,
           title="FPU у мікроконтролерах: є чи нема, одинарна чи подвійна")


# ── 5. Історія: окремий чип → на кристалі → опція (часова стрічка) ───────────
def fig_hist_timeline():
    W, H = 780, 388
    f = []
    y = 150
    f.append(line(56, y, 724, y, color=MUTED, sw=2))
    marks = [
        (120, "1980", "Intel 8087", "окремий чип", NEG,
         "перший матем.", "співпроцесор"),
        (300, "1989", "80486DX", "FPU на кристалі", FIELD,
         "той самий", "кремній"),
        (480, "1991", "486SX", "FPU вимкнено", GOLD,
         "опція, не", "обов'язок"),
        (660, "нині", "Cortex-M", "то є, то нема", POS,
         "опція й", "донині"),
    ]
    for x, yr, name, what, col, l1, l2 in marks:
        f.append(circle(x, y, 8, fill=col, stroke=col, sw=2))
        f.append(text(x, y - 62, yr, size=15, color=col, bold=True))
        f.append(text(x, y - 42, name, size=12.5, color=INK, bold=True))
        f.append(line(x, y - 32, x, y - 8, color=col, sw=1.4, dash="3,3"))
        f.append(text(x, y + 30, what, size=10.5, color=MUTED))
        f.append(text(x, y + 50, l1, size=10, color=col))
        f.append(text(x, y + 64, l2, size=10, color=col))
    # три епохи-дуги під стрічкою
    f.append(fitbox(56, 250, 388, 40,
                    "окремий чип  →  той самий кристал",
                    size=12.5, fill=PALE_B, stroke=NEG, sw=1.5))
    f.append(fitbox(456, 250, 268, 40,
                    "…і завжди лишається опцією",
                    size=12.5, fill=PALE_Y, stroke=GOLD, sw=1.5))
    f.append(fitbox(56, 306, 668, 56,
                    "Одна лінія розвитку: спершу дробову арифметику винесли в ОКРЕМУ мікросхему,\n"
                    "далі транзистори здешевшали — і FPU переїхав на кристал ядра;\n"
                    "але він так і не став обов'язковим — і на 486SX, і на сучасних МК це ОПЦІЯ.",
                    size=12, fill=FILL, stroke=INK, sw=1.4))
    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *f,
           title="FPU у часі: окремий чип → на кристалі → опція")


# ── 6. Як 8087 працював як співпроцесор: підслуховував шину ──────────────────
def fig_hist_coproc():
    W, H = 760, 372
    f = []
    # головний CPU
    f.append(rect(60, 78, 250, 132, fill=PALE_B, stroke=NEG, sw=1.8))
    f.append(text(185, 104, "8086 / 8088", size=14, color=NEG, bold=True))
    f.append(text(185, 128, "головний процесор", size=11, color=MUTED))
    f.append(text(185, 154, "бачить у коді ESC —", size=11, color=INK))
    f.append(text(185, 172, "«це не мені», лишає", size=11, color=INK))
    f.append(text(185, 190, "адресу на шині", size=11, color=INK))
    # 8087 співпроцесор
    f.append(rect(450, 78, 250, 132, fill=PALE_G, stroke=FIELD, sw=1.8))
    f.append(text(575, 104, "8087", size=14, color=FIELD, bold=True))
    f.append(text(575, 128, "співпроцесор", size=11, color=MUTED))
    f.append(text(575, 154, "підслуховує ту саму", size=11, color=INK))
    f.append(text(575, 172, "шину, ловить ESC —", size=11, color=INK))
    f.append(text(575, 190, "«о, це мені» й рахує", size=11, color=INK))
    # спільна шина
    f.append(line(120, 244, 640, 244, color=INK, sw=3))
    f.append(text(380, 236, "спільна шина команд і даних", size=11, color=MUTED))
    f.append(line(185, 210, 185, 244, color=NEG, sw=1.6))
    f.append(line(575, 210, 575, 244, color=FIELD, sw=1.6))
    # синхронізація WAIT
    f.append(arrow(310, 120, 450, 120, color=INK, sw=1.6))
    f.append(text(380, 112, "тест «зайнятий?»", size=9.5, color=MUTED))
    f.append(fitbox(60, 272, 640, 44,
                    "Обидва чипи слухають ОДНУ шину. Команду FPU (опкод ESC) головний процесор пропускає,\n"
                    "а 8087 підхоплює й виконує; інструкція WAIT змушує CPU дочекатися, поки 8087 закінчить.",
                    size=11.5, fill=FILL, stroke=INK, sw=1.4))
    render(os.path.join(IMG, "hist-coproc.svg"), W, H, *f,
           title="8087 як «спів-процесор»: два чипи на одній шині")


if __name__ == "__main__":
    fig_work()
    fig_where()
    fig_paths()
    fig_embedded()
    fig_hist_timeline()
    fig_hist_coproc()
    print("OK: 6 фігур у", IMG)
