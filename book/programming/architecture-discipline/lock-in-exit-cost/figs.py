# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_iceberg():
    """Вартість виходу як айсберг: над водою — те, за що платимо явно;
    під водою — приховані статті, що часто більші."""
    W, H = 760, 500
    frags = []
    # лінія води
    water_y = 168
    frags.append(line(40, water_y, W - 40, water_y, color=NEG, sw=2, dash="7 6"))
    frags.append(text(52, water_y - 10, "ватерлінія рахунку", size=13, color=NEG,
                      anchor="start", italic=True))

    # верхівка (видиме)
    top, wt, ht = textbox(W / 2, 108, "Ціна ліцензії / підписки\n(те, що бачить бюджет)",
                          size=15, fill="#eaf0fd", stroke=NEG, sw=2, bold=True, pad=14)
    frags.append(top)

    # підводна маса — статті прихованої вартості
    items = [
        "Перенесення й перетворення даних",
        "Перепис інтеграцій та контрактів API",
        "Перенавчання команди й нові процеси",
        "Паралельний запуск двох систем (dual-run)",
        "Втрачені можливості під час переїзду",
        "Ризик простою й помилок міграції",
    ]
    y = water_y + 34
    for i, it in enumerate(items):
        frags.append(fitbox(150, y, W - 300, 34, it, size=14,
                            fill="#f4f6f8", stroke=LINE, sw=1.3))
        y += 44
    frags.append(text(W / 2, y + 8, "приховане тіло: зазвичай більше за видиму ціну",
                      size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, 'exit-cost-iceberg.svg'), W, H, *frags,
           title="З чого складається вартість виходу")


def fig_spectrum():
    """Вісь зворотності: від дешевого відкату до глухої прив'язки;
    де зʼявляється «премія прив'язки»."""
    W, H = 820, 360
    frags = []
    ax_y = 150
    frags.append(line(60, ax_y, W - 60, ax_y, color=INK, sw=2))
    frags.append(arrow(W - 90, ax_y, W - 50, ax_y, color=INK, sw=2))
    frags.append(text(70, ax_y - 16, "легко відкотити", size=13, color=FIELD,
                      anchor="start", bold=True))
    frags.append(text(W - 70, ax_y - 16, "глуха прив'язка", size=13, color=POS,
                      anchor="end", bold=True))
    frags.append(text(W / 2, H - 22, "зростання вартості виходу →", size=13,
                      color=MUTED, italic=True))

    # три позначки на осі з підписами вгору/вниз (щоб не накладались)
    marks = [
        (0.14, "прапорець\nу конфізі", FIELD, -1),
        (0.42, "своя абстракція\nнад SDK", INK, 1),
        (0.72, "формат даних\nвендора", POS, -1),
        (0.92, "керована\nпослуга-моноліт", POS, 1),
    ]
    for fx, label, col, side in marks:
        x = 60 + fx * (W - 150)
        frags.append(circle(x, ax_y, 7, fill="#ffffff", stroke=col, sw=2.5))
        if side < 0:
            b, w, h = textbox(x, ax_y - 58, label, size=13, stroke=col, sw=1.6, pad=9)
            frags.append(b)
            frags.append(line(x, ax_y - 58 + h / 2, x, ax_y - 9, color=col, sw=1.3))
        else:
            b, w, h = textbox(x, ax_y + 60, label, size=13, stroke=col, sw=1.6, pad=9)
            frags.append(b)
            frags.append(line(x, ax_y + 9, x, ax_y + 60 - h / 2, color=col, sw=1.3))
    render(os.path.join(OUT, 'reversibility-spectrum.svg'), W, H, *frags,
           title="Що далі вправо — то дорожче вийти")


def fig_seam():
    """Шов переносності: застосунок говорить із власним інтерфейсом,
    вендори — змінні адаптери. Праворуч — пряме зчеплення без шва."""
    W, H = 820, 430
    frags = []

    # ── ліва половина: зі швом ──
    lx = 40
    b, w, h = textbox(lx + 140, 92, "Застосунок", size=15, fill="#eafaf0",
                      stroke=FIELD, sw=2, bold=True, min_w=210, pad=14)
    frags.append(b)
    b2, w2, h2 = textbox(lx + 140, 188, "Свій інтерфейс\n(порт / шов)", size=14,
                         fill="#f4f6f8", stroke=INK, sw=2, min_w=210, pad=12)
    frags.append(b2)
    frags.append(arrow(lx + 140, 118, lx + 140, 168, color=INK, sw=2))

    # два адаптери під швом
    ax1 = lx + 66
    ax2 = lx + 214
    b3, _, _ = textbox(ax1, 300, "Адаптер\nвендор A", size=13, stroke=NEG, sw=1.8, pad=10)
    b4, _, _ = textbox(ax2, 300, "Адаптер\nвендор B", size=13, stroke=NEG, sw=1.8, pad=10)
    frags.append(b3)
    frags.append(b4)
    frags.append(arrow(lx + 118, 210, ax1 + 6, 276, color=NEG, sw=1.6))
    frags.append(arrow(lx + 162, 210, ax2 - 6, 276, color=NEG, sw=1.6))
    frags.append(text(lx + 140, 360, "поміняти вендора = поміняти адаптер",
                      size=13, color=FIELD, italic=True))

    # роздільник
    midx = W / 2 + 10
    frags.append(line(midx, 66, midx, H - 40, color=MUTED, sw=1.2, dash="4 6"))

    # ── права половина: без шва ──
    rx = midx + 40
    b5, _, _ = textbox(rx + 130, 92, "Застосунок", size=15, fill="#fdecea",
                       stroke=POS, sw=2, bold=True, min_w=200, pad=14)
    frags.append(b5)
    b6, _, _ = textbox(rx + 130, 300, "SDK вендора\nвсюди в коді", size=14,
                       fill="#fdecea", stroke=POS, sw=2, min_w=200, pad=12)
    frags.append(b6)
    # багато прямих звʼязків
    for dx in (-70, -24, 24, 70):
        frags.append(line(rx + 130 + dx, 118, rx + 130 + dx * 0.4, 272,
                          color=POS, sw=1.4))
    frags.append(text(rx + 130, 360, "поміняти вендора = переписати скрізь",
                      size=13, color=POS, italic=True))

    render(os.path.join(OUT, 'portability-seam.svg'), W, H, *frags,
           title="Шов переносності проти прямого зчеплення")


def fig_breakeven():
    """Точка беззбитковості переходу: наведена (дисконтована) кумулятивна
    економія росте й перетинає пласку разову вартість виходу. До перетину
    переїзд у мінусі, після — у плюсі."""
    W, H = 820, 470
    frags = []
    # поле графіка
    x0, y0 = 96, 60          # лівий-верх осей
    xr, yb = W - 60, H - 78   # правий край X, низ (вісь X)
    # осі
    frags.append(arrow(x0, yb, x0, y0 - 6, color=INK, sw=2))          # вгору — гроші
    frags.append(arrow(x0, yb, xr + 6, yb, color=INK, sw=2))          # вправо — час
    frags.append(text(x0 - 10, y0 + 4, "гроші, наведені до сьогодні", size=13,
                      color=MUTED, anchor="end", italic=False))
    frags.append(text(xr, yb + 34, "місяці після переходу →", size=13,
                      color=MUTED, anchor="end", italic=True))

    months = 24
    def sx(t):  # t у місяцях 0..months
        return x0 + (xr - x0) * (t / months)
    exit_cost = 13000.0       # разова вартість виходу (як у статті)
    save_m = 2400.0           # економія на місяць
    r_m = 0.01                # місячна ставка дисконтування
    ymax = 42000.0
    def sy(v):
        return yb - (yb - y0) * (v / ymax)

    # пласка лінія разової вартості виходу
    frags.append(line(x0, sy(exit_cost), xr, sy(exit_cost), color=POS, sw=2, dash="7 6"))
    frags.append(text(xr - 6, sy(exit_cost) - 12, "разова вартість виходу", size=13,
                      color=POS, anchor="end", bold=True))

    # крива наведеної кумулятивної економії PV(t) = Σ save/(1+r)^k
    pts = []
    acc = 0.0
    be_t = None
    for t in range(0, months + 1):
        if t > 0:
            acc += save_m / ((1 + r_m) ** t)
        pts.append((sx(t), sy(min(acc, ymax))))
        if be_t is None and acc >= exit_cost:
            be_t = t
    path = "M " + " L ".join("%.1f %.1f" % p for p in pts)
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (path, FIELD))
    frags.append(text(sx(months) - 4, sy(min(acc, ymax)) - 12,
                      "наведена сумарна економія", size=13, color=FIELD,
                      anchor="end", bold=True))

    # точка беззбитковості
    if be_t is not None:
        bx, by = sx(be_t), sy(exit_cost)
        frags.append(circle(bx, by, 7, fill="#ffffff", stroke=INK, sw=2.5))
        frags.append(line(bx, by, bx, yb, color=MUTED, sw=1.2, dash="3 5"))
        b, w, h = textbox(bx, y0 + 40, "беззбитковість\n≈ %d міс." % be_t, size=13,
                          stroke=INK, sw=1.8, pad=9)
        frags.append(b)
        frags.append(line(bx, y0 + 40 + h / 2, bx, by - 9, color=INK, sw=1.2, dash="3 5"))
        frags.append(text(bx + 14, yb - 8, "тут переїзд стає вигідним", size=12,
                          color=FIELD, anchor="start", italic=True))

    render(os.path.join(OUT, 'exit-breakeven.svg'), W, H, *frags,
           title="За скільки місяців економія покриває вихід")


def fig_leak():
    """Дірява абстракція: сигнатури чисті, але поведінка (порядок, збій,
    затримка, консистентність) протікає крізь шов, і код на неї спирається."""
    W, H = 860, 480
    frags = []

    # верх: чистий інтерфейс (те, що видно в сигнатурах)
    top_y = 78
    b, w, h = textbox(W / 2, top_y,
                      "Свій інтерфейс:   put()  ·  get()  ·  list()",
                      size=15, fill="#f4f6f8", stroke=INK, sw=2, bold=True,
                      min_w=580, pad=14)
    frags.append(b)
    frags.append(text(W / 2, top_y + 36,
                      "у сигнатурах — лише типи й імена: тут усе виглядає чисто",
                      size=12, color=MUTED, italic=True))

    # межа-шов
    seam_y = 158
    frags.append(line(60, seam_y, W - 60, seam_y, color=INK, sw=2))
    frags.append(text(68, seam_y - 8, "шов", size=12, color=INK, anchor="start", bold=True))

    # знизу: чотири «протікання», що піднімаються крізь шов
    leaks = [
        "порядок:\nчитання одразу\nпісля запису",
        "семантика збою:\nвиняток чи\nкод помилки",
        "ретраї та\nідемпотентність\nповтору",
        "затримка\nпід\nнавантаженням",
    ]
    n = len(leaks)
    slot = (W - 140) / n
    for i, lk in enumerate(leaks):
        cx = 70 + slot * (i + 0.5)
        b2, w2, h2 = textbox(cx, 348, lk, size=12, fill="#fdecea",
                             stroke=POS, sw=1.6, pad=11)
        frags.append(b2)
        # стрілка «просочується» вгору крізь шов
        frags.append(arrow(cx, 348 - h2 / 2, cx, seam_y + 4, color=POS, sw=1.6))

    frags.append(text(W / 2, H - 28,
                      "код нишком починає покладатися на конкретного вендора — попри чисті сигнатури",
                      size=13, color=POS, italic=True))
    render(os.path.join(OUT, 'leaky-seam.svg'), W, H, *frags,
           title="Що протікає крізь чистий інтерфейс")


def fig_contract():
    """Контрактний тест: один набір перевірок, наведений на КОЖНУ реалізацію
    того самого інтерфейсу, — так ловиться прихована залежність від вендора."""
    W, H = 860, 430
    frags = []

    # єдиний набір контрактних тестів
    b, w, h = textbox(W / 2, 96, "Один контрактний набір\n(перевіряє поведінку, не вендора)",
                      size=14, fill="#eafaf0", stroke=FIELD, sw=2, bold=True,
                      min_w=360, pad=14)
    frags.append(b)

    # три цілі: два адаптери + фейк
    targets = [
        (0.17, "Адаптер\nвендор A", NEG),
        (0.50, "Адаптер\nвендор B", NEG),
        (0.83, "Фейк\nу пам'яті", INK),
    ]
    ty = 306
    for fx, label, col in targets:
        cx = 70 + fx * (W - 140)
        b2, w2, h2 = textbox(cx, ty, label, size=13, stroke=col, sw=1.8, pad=12)
        frags.append(b2)
        frags.append(arrow(W / 2, 96 + h / 2, cx, ty - h2 / 2, color=col, sw=1.6))

    frags.append(text(W / 2, H - 26,
                      "розійшлися результати між адаптерами → знайдено протікання, поки воно ще в тесті",
                      size=13, color=FIELD, italic=True))
    render(os.path.join(OUT, 'contract-test.svg'), W, H, *frags,
           title="Той самий контракт проти кожної реалізації")


def fig_lineage():
    """Родовід ідеї: як абстрактна економіка бар'єрів перетворилася
    на щоденне архітектурне «vendor lock-in». Вертикальна вісь років,
    події праворуч від осі — щоб підписи не накладались."""
    W, H = 900, 740
    frags = []
    ax_x = 150
    top_y, bot_y = 66, H - 44
    frags.append(line(ax_x, top_y, ax_x, bot_y, color=INK, sw=2.5))
    frags.append(arrow(ax_x, top_y + 30, ax_x, top_y, color=INK, sw=2.5))
    frags.append(text(ax_x, top_y - 22, "час", size=13, color=MUTED, italic=True))

    # (рік, хто, суть, колір крапки)
    rows = [
        ("1979", "Портер", "П'ять сил: вартість переходу —\nбар'єр входу й важіль вендора", NEG),
        ("1985", "Девід", "QWERTY: залежність від шляху\n(чи гірша розкладка — спірно)", MUTED),
        ("1987", "Клемперер", "Ринки зі switching costs: другий\nперіод — менш конкурентний", NEG),
        ("1988", "Фаррелл, Шапіро", "Динаміка з витратою переходу:\nчастка нині → прибуток потім", NEG),
        ("1989", "Артур", "Зростні віддачі: система\n«замикається» на шляху (lock-in)", FIELD),
        ("1990", "Лібовіц, Марґоліс", "«Байка про клавіші»: докази\nнеоптимальності QWERTY хиткі", POS),
        ("1999", "Шапіро, Варіан", "Information Rules: прибуток\n≈ сукупна вартість переходу", FIELD),
        ("сер.\n1990-х", "інженери", "vendor lock-in — щоденний\nархітектурний термін", INK),
    ]
    n = len(rows)
    step = (bot_y - top_y - 44) / (n - 1)
    box_x = ax_x + 220           # ліва грань правих рамок
    for i, (yr, who, what, col) in enumerate(rows):
        y = top_y + 44 + i * step
        frags.append(circle(ax_x, y, 7, fill="#ffffff", stroke=col, sw=2.5))
        # рік ліворуч від осі, з запасом
        yr_lines = yr.count("\n")
        frags.append(mtext(ax_x - 24, y - yr_lines * 7 + 5, yr,
                           size=14, color=col, anchor="end", bold=True))
        # хто — ярлик над рамкою
        frags.append(text(box_x + 4, y - 30, who, size=12.5, color=col,
                          anchor="start", bold=True))
        # суть — у рамці праворуч
        frags.append(fitbox(box_x, y - 20, W - box_x - 30, 46, what, size=12.5,
                            fill="#f4f6f8", stroke=col, sw=1.4))
        # конектор
        frags.append(line(ax_x + 7, y, box_x, y, color=col, sw=1.3, dash="3 4"))
    render(os.path.join(OUT, 'lockin-lineage.svg'), W, H, *frags,
           title="Родовід поняття: від бар'єра входу до vendor lock-in")


if __name__ == '__main__':
    fig_iceberg()
    fig_spectrum()
    fig_seam()
    fig_breakeven()
    fig_leak()
    fig_contract()
    fig_lineage()
    print("figs done")
