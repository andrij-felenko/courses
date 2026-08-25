# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

CODE_BG = "#0f1b14"
CODE_FG = "#eaf6ee"
IR_BG   = "#151d2b"
IR_FG   = "#bcd0ff"


def codebox(x, y, w, h, s, fg=CODE_FG, bg=CODE_BG, size=11):
    """Рамка для коду з моноширинним шрифтом."""
    out = rect(x, y, w, h, fill=bg, stroke="#0a120d", sw=1.4, rx=6)
    out += ('<text x="%.1f" y="%.1f" font-family="Consolas, \'DejaVu Sans Mono\', monospace" '
            'font-size="%d" fill="%s" text-anchor="start" font-weight="700">%s</text>'
            % (x + 12, y + h / 2 + size * 0.35, size, fg, esc(s)))
    return out


# ── 1. overview: Класична збірка проти LTO ──────────────────────────────────
def fig_overview():
    W, H = 840, 430
    p = []

    # Розділювач панелей
    p.append(line(W / 2, 50, W / 2, 385, color=MUTED, sw=1.2, dash="4 4"))

    # ── Ліва панель: Класична окрема компіляція ──
    p.append(text(210, 40, "Класична збірка (без LTO)", size=13, color=POS, bold=True))

    # Вихідні файли
    b1, _, _ = textbox(110, 95, "main.c", size=11, bold=True, fill="#fdf2f0", stroke=POS, sw=1.5, min_w=85)
    b2, _, _ = textbox(310, 95, "math.c", size=11, bold=True, fill="#fdf2f0", stroke=POS, sw=1.5, min_w=85)
    p.extend([b1, b2])

    p.append(arrow(110, 115, 110, 155, color=INK, sw=1.5))
    p.append(arrow(310, 115, 310, 155, color=INK, sw=1.5))
    p.append(text(110, 138, "компілятор", size=9.5, color=MUTED))
    p.append(text(310, 138, "компілятор", size=9.5, color=MUTED))

    # Об'єктні файли (машинний код)
    bo1, _, _ = textbox(110, 185, "main.o\n(машинний код)", size=10, bold=True, fill="#f4f6f8", stroke=LINE, sw=1.5, min_w=120)
    bo2, _, _ = textbox(310, 185, "math.o\n(машинний код)", size=10, bold=True, fill="#f4f6f8", stroke=LINE, sw=1.5, min_w=120)
    p.extend([bo1, bo2])

    # Стіна між файлами
    p.append(line(210, 160, 210, 210, color=POS, sw=2, dash="3 3"))
    p.append(text(210, 226, "межа файлів: AST та IR втрачено", size=9.5, color=POS, italic=True))

    p.append(arrow(110, 215, 180, 280, color=INK, sw=1.5))
    p.append(arrow(310, 215, 240, 280, color=INK, sw=1.5))

    # Класичний лінкер
    blk, _, _ = textbox(210, 305, "Класичний лінкер\n(лише релокації та адреси)", size=10.5, bold=True, fill="#fdecea", stroke=POS, sw=1.8, min_w=200)
    p.append(blk)

    p.append(arrow(210, 335, 210, 375, color=INK, sw=1.8))
    bout1, _, _ = textbox(210, 395, "Бінарний файл (виклики між .o лишились)", size=10, bold=True, fill="#f4f6f8", stroke=LINE, sw=1.5, min_w=240)
    p.append(bout1)

    # ── Права панель: Збірка з LTO ──
    ox = 420
    p.append(text(ox + 210, 40, "Збірка з LTO (-flto)", size=13, color=FIELD, bold=True))

    # Вихідні файли
    b3, _, _ = textbox(ox + 110, 95, "main.c", size=11, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.5, min_w=85)
    b4, _, _ = textbox(ox + 310, 95, "math.c", size=11, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.5, min_w=85)
    p.extend([b3, b4])

    p.append(arrow(ox + 110, 115, ox + 110, 155, color=INK, sw=1.5))
    p.append(arrow(ox + 310, 115, ox + 310, 155, color=INK, sw=1.5))
    p.append(text(ox + 110, 138, "фронтенд", size=9.5, color=MUTED))
    p.append(text(ox + 310, 138, "фронтенд", size=9.5, color=MUTED))

    # Об'єктні файли з IR
    bo3, _, _ = textbox(ox + 110, 185, "main.o\n(LLVM IR біткод)", size=10, bold=True, fill="#151d2b", stroke="#2457d6", color="#bcd0ff", sw=1.5, min_w=120)
    bo4, _, _ = textbox(ox + 310, 185, "math.o\n(LLVM IR біткод)", size=10, bold=True, fill="#151d2b", stroke="#2457d6", color="#bcd0ff", sw=1.5, min_w=120)
    p.extend([bo3, bo4])

    p.append(text(ox + 210, 226, "збережено семантику та граф викликів", size=9.5, color=FIELD, italic=True))

    p.append(arrow(ox + 110, 215, ox + 180, 270, color=INK, sw=1.5))
    p.append(arrow(ox + 310, 215, ox + 240, 270, color=INK, sw=1.5))

    # LTO оптимізатор + лінкер
    blto, _, _ = textbox(ox + 210, 300, "Лінкер + LTO-плагін\n(міжмодульний аналіз, інлайнінг, кодоген)", size=10.5, bold=True, fill="#fff7e6", stroke="#b8860b", color="#b8860b", sw=1.8, min_w=260)
    p.append(blto)

    p.append(arrow(ox + 210, 335, ox + 210, 375, color=INK, sw=1.8))
    bout2, _, _ = textbox(ox + 210, 395, "Оптимізований бінарник (інлайнінг + чистка)", size=10, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.5, min_w=250)
    p.append(bout2)

    render(os.path.join(OUT, "overview.svg"), W, H, *p,
           title="Порівняння конвеєрів: класична збірка проти оптимізації під час лінкування")


# ── 2. cross-tu-opt: Міжмодульні оптимізації ────────────────────────────────
def fig_cross_tu_opt():
    W, H = 840, 390
    p = []

    # ── Блок 1: До LTO (два окремі модулі) ──
    p.append(text(210, 40, "До LTO: дві ізольовані одиниці трансляції", size=12.5, color=POS, bold=True))

    # Лівий файл math.c
    p.append(rect(30, 65, 175, 175, fill="#fdf2f0", stroke=POS, sw=1.5, rx=8))
    p.append(text(117, 85, "math.c", size=11, bold=True, color=POS))
    p.append(codebox(40, 100, 155, 30, "int scale(int x) {", size=10))
    p.append(codebox(40, 134, 155, 30, "  return x * 4;", size=10))
    p.append(codebox(40, 168, 155, 30, "}", size=10))
    p.append(codebox(40, 202, 155, 30, "void dead_fn() { ... }", size=9.5, fg="#9ca3af"))

    # Правий файл main.c
    p.append(rect(225, 65, 175, 175, fill="#fdf2f0", stroke=POS, sw=1.5, rx=8))
    p.append(text(312, 85, "main.c", size=11, bold=True, color=POS))
    p.append(codebox(235, 100, 155, 30, "int main() {", size=10))
    p.append(codebox(235, 134, 155, 30, "  int a = scale(10);", size=10))
    p.append(codebox(235, 168, 155, 30, "  return a + 2;", size=10))
    p.append(codebox(235, 202, 155, 30, "}", size=10))

    # Виклик через межу
    p.append(arrow(235, 149, 195, 115, color=POS, sw=1.6))
    p.append(text(215, 130, "call", size=9.5, color=POS, bold=True))

    p.append(text(210, 265, "Без LTO: непрямий виклик call scale;", size=10, color=INK))
    p.append(text(210, 285, "невикористана dead_fn() потрапляє в бінарник", size=10, color=POS))

    # Стрілка переходу
    p.append(arrow(415, 150, 465, 150, color=INK, sw=2.5))
    p.append(text(440, 135, "LTO", size=11, color="#b8860b", bold=True))

    # ── Блок 2: Після LTO (єдиний оптимізований модуль) ──
    ox = 480
    p.append(text(ox + 170, 40, "Після LTO: оптимізація всієї програми", size=12.5, color=FIELD, bold=True))

    p.append(rect(ox + 10, 65, 320, 175, fill="#eef6ef", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(ox + 170, 85, "main (результат міжмодульної оптимізації)", size=11, bold=True, color=FIELD))

    p.append(codebox(ox + 25, 105, 290, 32, "int main() {", size=10.5))
    p.append(codebox(ox + 25, 141, 290, 32, "  return 42; // scale(10)*4+2 обчислено!", size=10.5, fg="#7fe0a0"))
    p.append(codebox(ox + 25, 177, 290, 32, "}", size=10.5))

    # Три висновки під блоком
    p.append(text(ox + 170, 260, "1. Cross-TU Inlining: функцію scale() вбудовано в main()", size=10, color=FIELD))
    p.append(text(ox + 170, 280, "2. Constant Propagation: аргумент 10 розгорнуто (10*4+2 = 42)", size=10, color=FIELD))
    p.append(text(ox + 170, 300, "3. Dead Code Elimination: dead_fn() і scale() видалено", size=10, color=FIELD))

    p.append(text(W / 2, 360, "Міжмодульні оптимізації перетворюють виклики через межі файлів на прямі константні вирази",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "cross-tu-opt.svg"), W, H, *p,
           title="Міжмодульний інлайнінг, згортання констант та усунення мертвого коду")


# ── 3. devirtualization: Девіртуалізація через CHA ──────────────────────────
def fig_devirtualization():
    W, H = 840, 410
    p = []

    # ── Ліва панель: Класичний віртуальний виклик ──
    p.append(text(210, 40, "Без LTO: непрямий виклик через vtable", size=12.5, color=POS, bold=True))

    # Об'єкт в пам'яті
    p.append(rect(40, 75, 150, 105, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=6))
    p.append(text(115, 95, "Об'єкт у пам'яті", size=10.5, bold=True))
    p.append(rect(50, 110, 130, 26, fill="#eef4ff", stroke=NEG, sw=1.2, rx=4))
    p.append(text(115, 127, "vptr (покажчик)", size=10, color=NEG, bold=True))
    p.append(rect(50, 142, 130, 26, fill="#ffffff", stroke=MUTED, sw=1.2, rx=4))
    p.append(text(115, 159, "поля даних...", size=9.5, color=MUTED))

    # Таблиця vtable
    p.append(rect(230, 75, 150, 105, fill="#fff7e6", stroke="#b8860b", sw=1.5, rx=6))
    p.append(text(305, 95, "Таблиця vtable", size=10.5, bold=True, color="#b8860b"))
    p.append(rect(240, 110, 130, 26, fill="#ffffff", stroke="#b8860b", sw=1.2, rx=4))
    p.append(text(305, 127, "&Circle::draw", size=10, bold=True))
    p.append(rect(240, 142, 130, 26, fill="#ffffff", stroke="#b8860b", sw=1.2, rx=4))
    p.append(text(305, 159, "&Circle::area", size=10, bold=True))

    # Стрілка від vptr до vtable
    p.append(arrow(180, 123, 230, 123, color=NEG, sw=1.8))

    # Стрілка від vtable до виклику
    p.append(arrow(305, 180, 305, 230, color="#b8860b", sw=1.8))
    p.append(text(305, 255, "call *%rax (непрямий перехід)", size=10.5, color=POS, bold=True))
    p.append(text(210, 290, "Компілятор не знає, чи існують інші класи в інших .o,", size=9.5, color=MUTED))
    p.append(text(210, 310, "тому змушений звертатися до пам'яті vtable під час роботи.", size=9.5, color=MUTED))

    # Розділювач
    p.append(line(W / 2, 50, W / 2, 340, color=MUTED, sw=1.2, dash="4 4"))

    # ── Права панель: Девіртуалізація з LTO ──
    ox = 420
    p.append(text(ox + 210, 40, "З LTO: аналіз ієрархії (CHA) + прямий виклик", size=12.5, color=FIELD, bold=True))

    # Блок аналізу ієрархії
    bcha, _, _ = textbox(ox + 210, 100, "Аналіз ієрархії класів (Class Hierarchy Analysis)\nВся програма перевірена: єдиний нащадок Shape — Circle!",
                         size=10, bold=True, fill="#fff7e6", stroke="#b8860b", color="#b8860b", sw=1.6, min_w=360)
    p.append(bcha)

    p.append(arrow(ox + 210, 135, ox + 210, 175, color=FIELD, sw=2))

    # Прямий виклик або інлайнінг
    bdev, _, _ = textbox(ox + 210, 205, "Девіртуалізація (Devirtualization):\ncall Circle::draw()  →  прямий виклик без vtable!",
                         size=10.5, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD, sw=1.8, min_w=340)
    p.append(bdev)

    p.append(arrow(ox + 210, 240, ox + 210, 275, color=FIELD, sw=2))

    binl, _, _ = textbox(ox + 210, 305, "Інлайнінг (Inlining):\nТіло Circle::draw() вбудовано прямо в місце виклику!",
                         size=10.5, bold=True, fill="#eef6ef", stroke=FIELD, color=FIELD, sw=1.8, min_w=340)
    p.append(binl)

    p.append(text(W / 2, 380, "LTO відкриває повну картину спадкування в проєкті, усуваючи накладні витрати ООП-поліморфізму",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "devirtualization.svg"), W, H, *p,
           title="Девіртуалізація віртуальних функцій на етапі лінкування")


# ── 4. monolithic-vs-thinlto: Full LTO проти ThinLTO ────────────────────────
def fig_monolithic_vs_thinlto():
    W, H = 840, 430
    p = []

    # Розділювач панелей
    p.append(line(W / 2, 50, W / 2, 380, color=MUTED, sw=1.2, dash="4 4"))

    # ── Ліва панель: Монолітний Full LTO ──
    p.append(text(210, 40, "Монолітний LTO (Full LTO)", size=12.5, color=POS, bold=True))

    # Модулі на вході
    b_ir1, _, _ = textbox(90, 85, "IR-модуль 1", size=10, bold=True, fill="#151d2b", stroke="#2457d6", color="#bcd0ff", sw=1.4, min_w=100)
    b_ir2, _, _ = textbox(210, 85, "IR-модуль 2", size=10, bold=True, fill="#151d2b", stroke="#2457d6", color="#bcd0ff", sw=1.4, min_w=100)
    b_ir3, _, _ = textbox(330, 85, "IR-модуль N", size=10, bold=True, fill="#151d2b", stroke="#2457d6", color="#bcd0ff", sw=1.4, min_w=100)
    p.extend([b_ir1, b_ir2, b_ir3])

    p.append(arrow(90, 105, 170, 150, color=INK, sw=1.5))
    p.append(arrow(210, 105, 210, 150, color=INK, sw=1.5))
    p.append(arrow(330, 105, 250, 150, color=INK, sw=1.5))

    # Величезний монолітний модуль
    b_mono, _, _ = textbox(210, 195, "Один гігантський модуль IR\n(усі модулі проєкту в одному процесі)\nПам'ять: десятки гігабайтів (OOM!)",
                           size=10, bold=True, fill="#fdecea", stroke=POS, color=POS, sw=1.8, min_w=330)
    p.append(b_mono)

    p.append(arrow(210, 240, 210, 275, color=INK, sw=1.8))

    # Однопотокова оптимізація
    b_opt1, _, _ = textbox(210, 310, "Однопотокова оптимізація та кодоген\n(пляшкове горло збірки: години роботи)",
                           size=10, bold=True, fill="#f4f6f8", stroke=LINE, sw=1.5, min_w=310)
    p.append(b_opt1)

    p.append(text(210, 360, "✖ Не масштабується на сотні ядер і великі кодові бази", size=9.5, color=POS, bold=True))

    # ── Права панель: ThinLTO ──
    ox = 420
    p.append(text(ox + 210, 40, "ThinLTO (двофазний паралельний аналіз)", size=12.5, color=FIELD, bold=True))

    # Фаза 1: Модулі + Зведення (Summary)
    b_th1, _, _ = textbox(ox + 90, 85, "IR + Summary 1", size=9.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, min_w=105)
    b_th2, _, _ = textbox(ox + 210, 85, "IR + Summary 2", size=9.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, min_w=105)
    b_th3, _, _ = textbox(ox + 330, 85, "IR + Summary N", size=9.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, min_w=105)
    p.extend([b_th1, b_th2, b_th3])

    p.append(arrow(ox + 90, 105, ox + 170, 145, color=INK, sw=1.5))
    p.append(arrow(ox + 210, 105, ox + 210, 145, color=INK, sw=1.5))
    p.append(arrow(ox + 330, 105, ox + 250, 145, color=INK, sw=1.5))

    # Фаза 2: Глобальний індекс зведень (легкий)
    b_idx, _, _ = textbox(ox + 210, 185, "Глобальний індекс (Summary Index)\nЗавантажуються лише графи викликів (МБ, не ГБ!)\nШвидке рішення: хто що імпортує",
                          size=9.5, bold=True, fill="#fff7e6", stroke="#b8860b", color="#b8860b", sw=1.8, min_w=340)
    p.append(b_idx)

    p.append(arrow(ox + 170, 225, ox + 90, 270, color=FIELD, sw=1.6))
    p.append(arrow(ox + 210, 225, ox + 210, 270, color=FIELD, sw=1.6))
    p.append(arrow(ox + 250, 225, ox + 330, 270, color=FIELD, sw=1.6))

    # Фаза 3: Паралельні тонкі бекенди
    b_be1, _, _ = textbox(ox + 80, 310, "Бекенд 1\n(потік 1)", size=9.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, min_w=90)
    b_be2, _, _ = textbox(ox + 210, 310, "Бекенд 2\n(потік 2)", size=9.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, min_w=90)
    b_be3, _, _ = textbox(ox + 340, 310, "Бекенд N\n(потік N)", size=9.5, bold=True, fill="#eef6ef", stroke=FIELD, sw=1.4, min_w=90)
    p.extend([b_be1, b_be2, b_be3])

    p.append(text(ox + 210, 360, "✓ Повне розпаралелення, кешування та низьке споживання RAM", size=9.5, color=FIELD, bold=True))

    p.append(text(W / 2, 408, "ThinLTO поєднує глобальний міжмодульний аналіз із паралельною масштабованою компіляцією",
                  size=11, color=INK, bold=True))

    render(os.path.join(OUT, "monolithic-vs-thinlto.svg"), W, H, *p,
           title="Монолітний LTO проти масштабованого ThinLTO")


if __name__ == "__main__":
    fig_overview()
    fig_cross_tu_opt()
    fig_devirtualization()
    fig_monolithic_vs_thinlto()
    print("OK: all LTO figures rendered to", OUT)
