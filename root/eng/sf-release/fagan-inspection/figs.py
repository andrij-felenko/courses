# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def box(cx, cy, s, size=13, pad=8, **kw):
    frag, w, h = textbox(cx, cy, s, size=size, pad=pad, **kw)
    return frag


# ── Фігура 1: Шість фаз формальної інспекції Фагана ──────────────────────────
def fig_six_phases():
    W, H = 1000, 490
    frags = []

    # Заголовок зверху
    frags.append(text(W / 2, 28, "Життєвий цикл формальної інспекції Фагана (шість послідовних фаз)",
                      size=15, bold=True, color=INK))

    y_top = 115
    # Фаза 1
    frags.append(box(110, y_top, "1. Планування\n(Planning)\n• Перевірка входу\n• Призначення ролей",
                     size=11, bold=True, fill="#f4f6f8", stroke=INK, min_w=150))
    # Фаза 2
    frags.append(box(280, y_top, "2. Огляд\n(Overview)\n• Контекст автора\n• Архітектура (опція)",
                     size=11, bold=True, fill="#f4f6f8", stroke=INK, min_w=150))
    # Фаза 3
    frags.append(box(460, y_top, "3. Підготовка\n(Preparation)\n• Читання за чеклістом\n• Темп: 120 рядків/год",
                     size=11, bold=True, fill="#e8f0ff", stroke=NEG, min_w=170))
    # Фаза 4
    frags.append(box(670, y_top, "4. Засідання\n(Meeting)\n• Читець веде код\n• Фіксація дефектів",
                     size=11, bold=True, fill="#fdecea", stroke=POS, min_w=180))
    # Фаза 5
    frags.append(box(890, y_top, "5. Доопрацювання\n(Rework)\n• Автор виправляє\n• Без нових дефектів",
                     size=11, bold=True, fill="#fdf6e3", stroke=MUTED, min_w=160))

    # Стрілки між верхніми фазами
    frags.append(arrow(185, y_top, 205, y_top, color=INK, sw=1.8))
    frags.append(arrow(355, y_top, 375, y_top, color=INK, sw=1.8))
    frags.append(arrow(545, y_top, 580, y_top, color=NEG, sw=1.8))
    frags.append(arrow(760, y_top, 810, y_top, color=POS, sw=1.8))

    # Фаза 6 під фазою 5
    y_bot = 270
    frags.append(box(890, y_bot, "6. Контроль\n(Follow-up)\n• Модератор звіряє\n• Перевірка виправлень",
                     size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=160))

    # Стрілка вниз від фази 5 до фази 6
    frags.append(arrow(890, y_top + 45, 890, y_bot - 45, color=INK, sw=1.8))

    # Вихідний термінал успіху (Exit) зліва від фази 6
    frags.append(box(600, y_bot, "Критерії виходу виконано (Exit Criteria)\nАртефакт допущено до релізу / виробництва",
                     size=11, bold=True, fill="#eafaf0", stroke=FIELD, min_w=280))
    frags.append(arrow(810, y_bot, 740, y_bot, color=FIELD, sw=2.0))

    # Зворотна петля: повторна інспекція при перевищенні порогу дефектів (>5% змін)
    frags.append(line(890, y_bot + 45, 890, 395, color=POS, sw=1.6, dash="5 4"))
    frags.append(line(890, 395, 460, 395, color=POS, sw=1.6, dash="5 4"))
    frags.append(arrow(460, 395, 460, y_top + 48, color=POS, sw=1.8))
    frags.append(box(675, 420, "Повторна інспекція (Re-inspection), якщо виправлено >5% коду або є системні хиби",
                     size=10, bold=True, fill="#fdecea", stroke=POS, pad=5))

    # Блоки критеріїв входу/виходу
    frags.append(box(210, 270, "Вхідні критерії (Entry Criteria):\n• Чистий статичний аналіз (MISRA/Linter)\n• Пройдені юніт-тести та DRC схем\n• Документована специфікація",
                     size=10, fill="#ffffff", stroke=MUTED, pad=6))
    frags.append(arrow(210, 215, 110, y_top + 45, color=MUTED, sw=1.5))

    frags.append(text(W / 2, H - 15,
                      "Метод Фагана усуває дефекти до тестування: суворий порядок ролей і контроль кожного виправлення.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'fagan-inspection-six-phases.svg'), W, H, *frags,
           title="Шість фаз формальної інспекції Фагана")


# ── Фігура 2: Залежність щільності виявлених дефектів від швидкості інспекції ─
def fig_defect_rate():
    W, H = 980, 520
    frags = []

    # Заголовок
    frags.append(text(W / 2, 26, "Щільність виявлених дефектів залежно від темпу вичитування",
                      size=15, bold=True, color=INK))

    ox, oy = 80, 440
    gw, gh = 840, 330

    # Сітка та фон графіка
    frags.append(rect(ox, oy - gh, gw, gh, fill="#fafbfc", stroke=MUTED, sw=1.0))

    # Зона оптимуму (вертикальні лінії та заливка без вкладених rect)
    # x діапазон: 50..500 LOC/h -> gw=840 => шкала x: scale_x = 840 / 450 = 1.866 px/(LOC/h)
    x_opt_start = ox + (100 - 50) * 1.866
    x_opt_end = ox + (160 - 50) * 1.866
    w_opt = x_opt_end - x_opt_start
    frags.append(rect(x_opt_start, oy - gh, w_opt, gh, fill="#eafaf0", stroke=FIELD, sw=1.2, rx=0))
    frags.append(text(x_opt_start + w_opt / 2, oy - gh - 15, "Оптимальна зона: 100–150 LOC/год (20–30 ICs/год)",
                      size=10, bold=True, color=FIELD, anchor="middle"))

    # Зона поверхневого перегляду (>300 LOC/h)
    x_bad_start = ox + (300 - 50) * 1.866
    w_bad = ox + gw - x_bad_start
    frags.append(rect(x_bad_start, oy - gh, w_bad, gh, fill="#fdecea", stroke=POS, sw=1.2, rx=0))
    frags.append(text(x_bad_start + w_bad / 2, oy - gh - 15, "Зона пропуску дефектів (>300 LOC/год — «ілюзія рев'ю»)",
                      size=10, bold=True, color=POS, anchor="middle"))

    # Горизонтальні лінії сітки (дефекти на KLOC: 5, 10, 15, 20, 25, 30)
    # gh = 330 => scale_y = 330 / 30 = 11.0 px/(def/KLOC)
    for d in [5, 10, 15, 20, 25, 30]:
        y_grid = oy - d * 11.0
        frags.append(line(ox, y_grid, ox + gw, y_grid, color="#e5e7eb", sw=1.0, dash="4 4"))
        frags.append(text(ox - 10, y_grid + 4, str(d), size=11, color=MUTED, anchor="end"))

    # Вертикальні лінії сітки (LOC/h: 100, 200, 300, 400, 500)
    for loc in [100, 200, 300, 400, 500]:
        x_grid = ox + (loc - 50) * 1.866
        frags.append(line(x_grid, oy, x_grid, oy - gh, color="#e5e7eb", sw=1.0, dash="4 4"))
        frags.append(text(x_grid, oy + 20, str(loc), size=11, color=MUTED, anchor="middle"))

    # Підписи осей
    frags.append(text(ox + gw / 2, oy + 42, "Швидкість інспекції (рядків коду або компонентів на годину) ►",
                      size=12, bold=True, color=INK))
    frags.append(text(ox + 10, oy - gh + 20, "▲ Знайдено дефектів на 1000 рядків коду (Defects / KLOC)",
                      size=11, bold=True, color=INK, anchor="start"))

    # Точки кривої
    pts = [
        (50, 16.0),
        (90, 22.0),
        (125, 25.5),
        (160, 21.0),
        (200, 15.0),
        (250, 9.5),
        (300, 5.0),
        (380, 2.5),
        (500, 1.0)
    ]
    svg_pts = []
    for loc, d in pts:
        px = ox + (loc - 50) * 1.866
        py = oy - d * 11.0
        svg_pts.append((px, py))

    # Лінії графіка
    for i in range(len(svg_pts) - 1):
        x1, y1 = svg_pts[i]
        x2, y2 = svg_pts[i + 1]
        frags.append(line(x1, y1, x2, y2, color=POS, sw=3.0))

    for px, py in svg_pts:
        frags.append(circle(px, py, 4.5, fill="#ffffff", stroke=POS, sw=2.0))

    # Текстові підписи (без внутрішніх rect, щоб уникнути конфліктів)
    peak_x, peak_y = svg_pts[2]
    frags.append(mtext(380, 135, ["Пік виявлення (25.5 дефектів / KLOC):",
                                  "глибокий пошук гонок та помилок пам'яті"],
                       size=11, bold=True, color=FIELD, anchor="start"))
    frags.append(arrow(375, 140, peak_x + 8, peak_y - 2, color=FIELD, sw=1.5))

    drop_x, drop_y = svg_pts[6]
    frags.append(mtext(560, 275, ["Падіння ефективності на 80%:",
                                  "пропуск гонок у перериваннях і хиб розв'язки шин"],
                       size=11, bold=True, color=POS, anchor="start"))
    frags.append(arrow(650, 295, drop_x + 10, drop_y + 10, color=POS, sw=1.5))

    frags.append(text(W / 2, H - 10,
                      "Перевищення темпу 200 LOC/год різко знижує якість виявлення критичних апаратних і програмних хиб.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'defect-density-vs-inspection-rate.svg'), W, H, *frags,
           title="Залежність виявлення дефектів від швидкості інспекції")


if __name__ == '__main__':
    fig_six_phases()
    fig_defect_rate()
    print("Figures generated successfully in img/")
