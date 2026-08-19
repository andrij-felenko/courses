# -*- coding: utf-8 -*-
"""Фігури до теми «Швидкість збірки: Ninja, ccache, PCH, unity»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"     # червонуватий / перезбирання / вузьке місце
CLEAN = "#eaf7ef"     # зеленуватий / оптимізовано
PANEL = "#f8fafc"
ACCENT = "#eaf0fd"    # блакитний


# ── 1. Анатомія часу збірки C/C++ ──────────────────────────────────────────
def fig_pipeline_bottlenecks():
    W, H = 1060, 440
    p = []

    # Заголовок блоків
    p.append(text(530, 35, "Анатомія часу збірки: де насправді зникають секунди",
                  size=16, bold=True))

    stages = [
        ("1. Препроцесинг та I/O", "Читання тисяч .h файлів,\nрозгортання макросів.\n50 рядків .cpp → 500k рядків", 150, DIRTY, POS),
        ("2. Парсинг та AST", "Лексичний/синтаксичний аналіз,\nінстанціювання шаблонів.\nПовторюється для кожного TU", 400, DIRTY, POS),
        ("3. Оптимізація та Codegen", "LLVM IR / GIMPLE проходи,\nінлайнінг, векторизація,\nгенерація машинного коду", 650, ACCENT, NEG),
        ("4. Лінкування (Linker)", "Злиття секцій, релокації,\nдедуплікація COMDAT,\nобробка гігабайтів DWARF", 900, DIRTY, POS),
    ]

    for title, desc, cx, bg_col, border_col in stages:
        box_w, box_h = 220, 160
        cy = 150
        p.append(rect(cx - box_w/2, cy - box_h/2, box_w, box_h, fill=bg_col, stroke=border_col, sw=1.8))
        p.append(text(cx, cy - 50, title, size=13.5, bold=True, color=border_col))
        p.append(mtext(cx, cy - 15, desc, size=12, color=INK, lh=1.35))

    # Стрілки між стадіями
    p.append(arrow(263, 150, 286, 150, color=LINE, sw=1.8))
    p.append(arrow(513, 150, 536, 150, color=LINE, sw=1.8))
    p.append(arrow(763, 150, 786, 150, color=LINE, sw=1.8))

    # Нижня панель інструментів оптимізації
    p.append(rect(40, 260, 980, 140, fill=PANEL, stroke=MUTED, sw=1.5))
    p.append(text(530, 290, "Які інструменти б'ють по кожному вузькому місцю", size=14, bold=True))

    tools = [
        ("PCH та Unity builds", 150, FIELD),
        ("ccache / sccache", 400, FIELD),
        ("Розпаралелення (Ninja)", 650, FIELD),
        ("mold / lld + Split DWARF", 900, FIELD),
    ]
    for name, cx, col in tools:
        tb, tw, th = textbox(cx, 350, name, size=12.5, bold=True, fill=CLEAN, stroke=col, pad=8)
        p.append(tb)
        p.append(arrow(cx, 325, cx, 235, color=col, sw=1.6))

    render(os.path.join(IMG, "pipeline-bottlenecks.svg"), W, H, *p,
           title="Анатомія часу збірки C/C++")


# ── 2. Ninja: .ninja_deps проти тисяч окремих .d файлів ─────────────────────
def fig_ninja_deps_flow():
    W, H = 960, 400
    p = []

    # Ліва панель: Make + тисячі .d файлів
    p.append(rect(40, 40, 420, 330, fill=PANEL, stroke=POS, sw=1.6))
    p.append(text(250, 75, "Традиційний Make: розсип .d файлів", size=14.5, bold=True, color=POS))
    p.append(fitbox(65, 105, 370, 70, "Компілятор пише окремий foo.d\nдля кожного з 10 000 об'єктних файлів", size=12.5, fill=BG))

    p.append(fitbox(65, 195, 370, 75, "Make парсить 10 000 текстових файлів\nі робить сотні тисяч викликів stat()\nпри кожному запуску збірки", size=12.5, fill=DIRTY, stroke=POS))
    p.append(text(250, 320, "Час холостого запуску: 5–25 секунд", size=13.5, bold=True, color=POS))

    # Права панель: Ninja + єдиний .ninja_deps
    p.append(rect(500, 40, 420, 330, fill=PANEL, stroke=FIELD, sw=1.6))
    p.append(text(710, 75, "Ninja: компактний лог .ninja_deps", size=14.5, bold=True, color=FIELD))
    p.append(fitbox(525, 105, 370, 70, "Компілятор повертає залежності,\nNinja дописує їх у єдиний бінарний лог", size=12.5, fill=BG))

    p.append(fitbox(525, 195, 370, 75, "Індексований бінарний файл:\nшляхи дедупліковано в числові ID,\nчитається за один послідовний mmap()", size=12.5, fill=CLEAN, stroke=FIELD))
    p.append(text(710, 320, "Час холостого запуску: 0.03 секунди", size=13.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "ninja-deps-flow.svg"), W, H, *p,
           title="Ninja .ninja_deps проти розсипу depfiles")


# ── 3. ccache: Прямий режим проти режиму препроцесора ───────────────────────
def fig_ccache_modes():
    W, H = 1000, 450
    p = []

    p.append(text(500, 35, "ccache: як прямий режим обходить стадію препроцесингу",
                  size=15.5, bold=True))

    # Вхідний виклик
    src_box, sw_w, sw_h = textbox(140, 140, "Запит на компіляцію:\nfoo.cpp + CFLAGS", size=13, bold=True, fill=BG, stroke=LINE)
    p.append(src_box)

    # Прямий режим (Direct mode)
    p.append(rect(300, 60, 360, 160, fill=CLEAN, stroke=FIELD, sw=1.8))
    p.append(text(480, 90, "Прямий режим (Direct mode)", size=14, bold=True, color=FIELD))
    p.append(mtext(480, 130, "Звірити mtime/геші foo.cpp та\nсписку заголовків з маніфесту.\nПрепроцесор НЕ запускається!", size=12.5, color=INK))

    p.append(arrow(215, 140, 298, 140, color=FIELD, sw=2))

    # Кеш-влучання з прямого режиму
    hit_box, _, _ = textbox(810, 140, "CACHE HIT (прямий):\nМиттєва віддача foo.o\nЧас: ~1–3 мс", size=13, bold=True, fill=CLEAN, stroke=FIELD, pad=10)
    p.append(hit_box)
    p.append(arrow(662, 140, 715, 140, color=FIELD, sw=2))

    # Режим препроцесора (Fallback / Classic)
    p.append(rect(300, 250, 360, 160, fill=PANEL, stroke=MUTED, sw=1.6))
    p.append(text(480, 280, "Режим препроцесора (cpp mode)", size=14, bold=True, color=INK))
    p.append(mtext(480, 320, "Запуск cpp/clang -E → повне читання .h,\nгешування розгорнутого тексту.\nВлучання: віддача foo.o (~30-100 мс)", size=12, color=INK))

    # Стрілка промаху прямого режиму в препроцесор
    p.append(arrow(480, 222, 480, 248, color=MUTED, sw=1.6))
    p.append(text(545, 238, "промах direct", size=11, color=MUTED, italic=True))

    # Кеш-промах: повна компіляція
    miss_box, _, _ = textbox(810, 330, "CACHE MISS:\nПовна компіляція\n+ запис у кеш (~1000 мс)", size=13, bold=True, fill=DIRTY, stroke=POS, pad=10)
    p.append(miss_box)
    p.append(arrow(662, 330, 710, 330, color=POS, sw=1.8))

    render(os.path.join(IMG, "ccache-modes.svg"), W, H, *p,
           title="Режими роботи ccache")


# ── 4. Попередньо скомпільовані заголовки (PCH) ─────────────────────────────
def fig_pch_ast_snapshot():
    W, H = 980, 420
    p = []

    # Ліворуч: без PCH
    p.append(rect(40, 40, 430, 350, fill=PANEL, stroke=POS, sw=1.6))
    p.append(text(255, 75, "Без PCH: повторний парсинг N разів", size=14.5, bold=True, color=POS))
    p.append(fitbox(65, 105, 380, 60, "Важкі заголовки: <vector>, <string>,\n<algorithm>, <boost/asio.hpp> (300k рядків)", size=12, fill=BG))

    p.append(arrow(255, 168, 255, 198, color=POS, sw=1.8))

    p.append(fitbox(65, 202, 380, 110, "Компілятор парсить 300 000 рядків\nі будує AST окремо для a.cpp, b.cpp,\nc.cpp ... z.cpp (1000 разів).\n90% часу процесора марнується.", size=12.5, fill=DIRTY, stroke=POS))
    p.append(text(255, 355, "Загальний час парсингу: 1000 × 0.4 с = 400 с", size=12.5, bold=True, color=POS))

    # Праворуч: з PCH
    p.append(rect(510, 40, 430, 350, fill=PANEL, stroke=FIELD, sw=1.6))
    p.append(text(725, 75, "З PCH: зліпок AST на диску", size=14.5, bold=True, color=FIELD))
    p.append(fitbox(535, 105, 380, 60, "Парсинг важких заголовків 1 раз\n→ збереження зліпка AST у pch.h.pch", size=12, fill=CLEAN, stroke=FIELD))

    p.append(arrow(725, 168, 725, 198, color=FIELD, sw=1.8))

    p.append(fitbox(535, 202, 380, 110, "Усі a.cpp ... z.cpp завантажують\nготовий AST через швидкий mmap() і\nодразу переходять до аналізу власного коду.", size=12.5, fill=CLEAN, stroke=FIELD))
    p.append(text(725, 355, "Загальний час: 1 раз 0.5 с + 1000 × 0.02 с = 20.5 с", size=12.5, bold=True, color=FIELD))

    render(os.path.join(IMG, "pch-ast-snapshot.svg"), W, H, *p,
           title="Ефект попередньо скомпільованих заголовків")


# ── 5. Split DWARF: винесення налагоджувальної інформації ────────────────────
def fig_split_dwarf_flow():
    W, H = 1000, 430
    p = []

    p.append(text(500, 35, "Split DWARF (-gsplit-dwarf): розвантаження компонувальника",
                  size=15.5, bold=True))

    # Ліва сторона: Монолітний DWARF
    p.append(rect(40, 65, 430, 335, fill=PANEL, stroke=POS, sw=1.6))
    p.append(text(255, 95, "Звичайне лінкування: важкі .o файли", size=14, bold=True, color=POS))

    p.append(fitbox(65, 120, 380, 80, "Об'єктний файл foo.o (50 МБ):\n[ Машинний код 2 МБ ] + [ DWARF 48 МБ ]\nЛінкер змушений завантажити всі гігабайти", size=12.5, fill=DIRTY, stroke=POS))

    p.append(arrow(255, 205, 255, 245, color=POS, sw=1.8))

    p.append(fitbox(65, 250, 380, 120, "Лінкер читає 50 ГБ даних з диску,\nдедуплікує типи та формує 2 ГБ бінарник.\nВузьке місце: пам'ять, I/O та шина CPU.\nЧас лінкування: 45–90 секунд", size=12, fill=BG))

    # Права сторона: Split DWARF
    p.append(rect(530, 65, 430, 335, fill=PANEL, stroke=FIELD, sw=1.6))
    p.append(text(745, 95, "Split DWARF: розділення коду і налагодження", size=14, bold=True, color=FIELD))

    p.append(fitbox(555, 120, 180, 80, "foo.o (2 МБ):\nКод, релокації,\nхеш-посилання", size=12, fill=CLEAN, stroke=FIELD))
    p.append(fitbox(755, 120, 180, 80, "foo.dwo (48 МБ):\nПовні налагоджувальні\nсимволи DWARF", size=12, fill=BG, stroke=MUTED))

    p.append(arrow(645, 205, 645, 245, color=FIELD, sw=1.8))

    p.append(fitbox(555, 250, 380, 120, "Лінкер читає ЛИШЕ код із foo.o (2 ГБ замість 50 ГБ),\nшвидко зшиває бінарник за 2 секунди.\nНалагоджувач (gdb/lldb) читає .dwo напряму.\nЧас лінкування: 2–4 секунди", size=12, fill=CLEAN, stroke=FIELD))

    render(os.path.join(IMG, "split-dwarf-flow.svg"), W, H, *p,
           title="Split DWARF")


if __name__ == "__main__":
    fig_pipeline_bottlenecks()
    fig_ninja_deps_flow()
    fig_ccache_modes()
    fig_pch_ast_snapshot()
    fig_split_dwarf_flow()
