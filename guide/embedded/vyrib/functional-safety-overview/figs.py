# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


# ── Фігура 1: одне коріння (IEC 61508) — і галузеві нащадки ──────────────────
def fig_family():
    W, H = 780, 400
    frags = []
    frags.append(text(W / 2, 30, "Одне коріння, галузеві діалекти: як розгалужується функційна безпека",
                      size=15, bold=True))

    # корінь — IEC 61508
    root, rw, rh = textbox(W / 2, 90, "IEC 61508\nзагальний стандарт для електроніки",
                           size=14, bold=True, fill="#eef2f7", stroke=INK, sw=2.2, min_w=340)
    frags.append(root)
    frags.append(text(W / 2, 90 + rh / 2 + 16, "рівні цілісності: SIL 1 … SIL 4",
                      size=11, color=MUTED))

    # нащадки-галузі, кожен зі своєю назвою рівня
    kids = [
        ("ISO 26262", "автомобілі", "ASIL A…D", NEG),
        ("DO-178C", "авіоніка", "DAL A…E", POS),
        ("IEC 62304", "медтехніка", "клас A/B/C", FIELD),
        ("EN 50128", "залізниця", "SIL 0…4", "#8a5a1f"),
    ]
    n = len(kids)
    bw, gap = 158, 16
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    ytop = 250
    bh = 78
    trunk_y = 90 + rh / 2 + 34
    frags.append(line(W / 2, trunk_y, W / 2, ytop - 34, color=MUTED, sw=1.6))
    frags.append(line(x0 + bw / 2, ytop - 34, x0 + total - bw / 2, ytop - 34, color=MUTED, sw=1.6))
    for i, (name, dom, lvl, col) in enumerate(kids):
        x = x0 + i * (bw + gap)
        cx = x + bw / 2
        frags.append(line(cx, ytop - 34, cx, ytop, color=col, sw=1.6))
        frags.append(fitbox(x, ytop, bw, bh, name + "\n" + dom + "\n" + lvl, size=13, bold=True,
                            fill="#fbfbfb", stroke=col, sw=1.8))
    frags.append(fitbox(x0, H - 42, total, 30,
                        "Спільна ідея одна; кожна галузь лише перекладає її своєю мовою ризику.",
                        size=12, fill="#fdf6ec", stroke=POS, sw=1.5))
    render(os.path.join(OUT, 'safety-standards-family.svg'), W, H, *frags)


# ── Фігура 2: драбина SIL — що вищий рівень, то менша дозволена ймовірність ───
def fig_sil_ladder():
    W, H = 760, 420
    frags = []
    frags.append(text(W / 2, 30, "Драбина SIL: кожен щабель — удесятеро суворіша вимога до відмови",
                      size=15, bold=True))

    rows = [
        ("SIL 4", "10⁻⁵ … 10⁻⁴", "×100 000", "#8e1b1b"),
        ("SIL 3", "10⁻⁴ … 10⁻³", "×10 000", "#c0392b"),
        ("SIL 2", "10⁻³ … 10⁻²", "×1 000", "#d98324"),
        ("SIL 1", "10⁻² … 10⁻¹", "×100", "#c9a227"),
    ]
    x0 = 120
    bw = 300
    step = 82
    y0 = 78
    frags.append(text(x0 + bw / 2, y0 - 14, "ймовірність небезпечної відмови на вимогу (PFD)",
                      size=11, color=MUTED))
    for i, (name, pfd, rrf, col) in enumerate(rows):
        y = y0 + i * step
        # ширина смуги росте донизу — щабель нижче «легший»
        w = bw * (0.55 + 0.15 * i)
        frags.append(rect(x0, y, w, step - 20, fill="#f4f6f8", stroke=col, sw=2.0))
        frags.append(text(x0 + 14, y + (step - 20) / 2 + 5, name, size=15, color=col, bold=True,
                          anchor="start"))
        frags.append(text(x0 + 118, y + (step - 20) / 2 + 5, pfd, size=13, color=INK, anchor="start"))
        # праворуч — множник зменшення ризику
        frags.append(text(x0 + bw + 150, y + (step - 20) / 2 + 5,
                          "зниження ризику " + rrf, size=12, color=col, anchor="end"))
    # стрілка «суворіше вгору»
    ax = x0 - 32
    frags.append(arrow(ax, y0 + 3 * step, ax, y0 - 4, color=INK, sw=2))
    frags.append(text(ax - 8, (y0 + 3 * step + y0) / 2, "суворіше", size=12, color=INK,
                      anchor="middle"))
    # обертаємо підпис вертикально вручну через transform
    frags[-1] = ('<text x="%.1f" y="%.1f" font-family="%s" font-size="12" fill="%s" '
                 'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">суворіше</text>'
                 % (ax - 8, (y0 + 3 * step + y0) / 2, FONT, INK, ax - 8, (y0 + 3 * step + y0) / 2))
    frags.append(fitbox(x0, H - 40, bw + 200, 28,
                        "SIL 4 дозволяє одну небезпечну відмову на 10 000–100 000 звернень.",
                        size=12, fill="#eef2f7", stroke=INK, sw=1.4))
    render(os.path.join(OUT, 'sil-ladder.svg'), W, H, *frags)


# ── Фігура 3: цикл безпеки й перехід у безпечний стан ────────────────────────
def fig_safety_loop():
    W, H = 800, 380
    frags = []
    frags.append(text(W / 2, 30, "Життєвий цикл безпеки: від небезпеки до перевірки — і що робить залізо при відмові",
                      size=14, bold=True))

    # верхня стрічка — цикл вимог
    steps = [
        ("Небезпека", "що може\nпоранити", NEG),
        ("Оцінка ризику", "SIL / ASIL:\nнаскільки суворо", POS),
        ("Вимога безпеки", "що система\nмусить робити", "#8a5a1f"),
        ("Реалізація", "код, залізо,\nрезерв", INK),
        ("Доказ", "тести, аналіз,\nаудит", FIELD),
    ]
    n = len(steps)
    bw, gap = 132, 18
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    ytop = 70
    bh = 64
    for i, (name, sub, col) in enumerate(steps):
        x = x0 + i * (bw + gap)
        frags.append(fitbox(x, ytop, bw, bh, name + "\n" + sub, size=12, bold=True,
                            fill="#fbfbfb", stroke=col, sw=1.7))
        if i < n - 1:
            frags.append(arrow(x + bw + 2, ytop + bh / 2, x + bw + gap - 2, ytop + bh / 2,
                               color=MUTED, sw=1.8))
    # петля назад: доказ → знову небезпека (щось змінили)
    ry = ytop + bh + 26
    frags.append(line(x0 + total - bw / 2, ytop + bh, x0 + total - bw / 2, ry, color=MUTED, sw=1.4, dash="4,4"))
    frags.append(line(x0 + bw / 2, ry, x0 + total - bw / 2, ry, color=MUTED, sw=1.4, dash="4,4"))
    frags.append(line(x0 + bw / 2, ry, x0 + bw / 2, ytop + bh, color=MUTED, sw=1.4, dash="4,4"))
    frags.append(text(W / 2, ry + 15, "змінив систему → цикл повторюється", size=11, color=MUTED))

    # нижня частина — суть реалізації: виявив відмову → безпечний стан
    by = 250
    ok, okw, okh = textbox(180, by, "Робота\n(усе справне)", size=13, bold=True,
                           fill="#eafaf1", stroke=FIELD, sw=1.8, min_w=170)
    frags.append(ok)
    safe, sw2, sh2 = textbox(600, by, "БЕЗПЕЧНИЙ СТАН\n(двигун стоп, гальмо, сигнал)",
                             size=13, bold=True, fill="#fdecea", stroke=POS, sw=2.0, min_w=250)
    frags.append(safe)
    frags.append(arrow(180 + okw / 2, by, 600 - sw2 / 2, by, color=POS, sw=2.2))
    frags.append(text((180 + okw / 2 + 600 - sw2 / 2) / 2, by - 12,
                      "виявив відмову — не приховуй, а йди у відомий безпечний стан",
                      size=11, color=POS))
    frags.append(text((180 + okw / 2 + 600 - sw2 / 2) / 2, by + 18,
                      "watchdog · перевірка входів · резерв", size=10, color=MUTED))
    render(os.path.join(OUT, 'safety-lifecycle.svg'), W, H, *frags)


# ── Фігура 4 (вставка math): звідки береться порядок — ланцюг тол.ризик→RRF→PFD
def fig_risk_chain():
    W, H = 820, 430
    frags = []
    frags.append(text(W / 2, 30,
                      "Звідки береться число: терпимий ризик ÷ голий ризик = у скільки разів знизити",
                      size=14, bold=True))

    # три коробки ланцюга
    y = 120
    bh = 96
    b1, w1, h1 = textbox(150, y, "Голий ризик\nбез захисту\n\n1 небезпечна подія\nна 10 років",
                         size=12, bold=True, fill="#fdecea", stroke=POS, sw=2.0, min_w=230)
    frags.append(b1)
    b2, w2, h2 = textbox(410, y, "Терпимий ризик\n(суспільна межа)\n\n1 подія\nна 10 000 років",
                         size=12, bold=True, fill="#eafaf1", stroke=FIELD, sw=2.0, min_w=230)
    frags.append(b2)
    b3, w3, h3 = textbox(680, y, "Треба знизити\nу RRF разів\n\n10 000 / 10\n= 1000",
                         size=12, bold=True, fill="#eef2f7", stroke=INK, sw=2.2, min_w=210)
    frags.append(b3)
    frags.append(arrow(150 + w1 / 2, y, 410 - w2 / 2, y, color=MUTED, sw=2.0))
    frags.append(arrow(410 + w2 / 2, y, 680 - w3 / 2, y, color=MUTED, sw=2.0))
    frags.append(text((150 + w1 / 2 + 410 - w2 / 2) / 2, y - h1 / 2 - 8,
                      "ділимо", size=11, color=MUTED))

    # стрілка вниз до PFD
    frags.append(arrow(680, y + h3 / 2, 680, y + h3 / 2 + 40, color=INK, sw=2.0))
    b4, w4, h4 = textbox(680, y + h3 / 2 + 40 + 40,
                         "PFD = 1 / RRF\n= 1/1000 = 10⁻³\n→ це SIL 2",
                         size=13, bold=True, fill="#fdf6ec", stroke="#8a5a1f", sw=2.0, min_w=210)
    frags.append(b4)

    # нижня стрічка — чому саме множники десять
    frags.append(fitbox(70, H - 96, W - 140, 34,
                        "Кожна ×10 у терпимому ризику зсуває PFD на один порядок — тому щаблі SIL і йдуть десятками, а не як заманеться.",
                        size=12, fill="#eef2f7", stroke=INK, sw=1.4))
    frags.append(fitbox(70, H - 52, W - 140, 30,
                        "Число не з таблиці впало — воно РАХУЄТЬСЯ з того, наскільки суспільство терпить цю конкретну біду.",
                        size=12, fill="#fdf6ec", stroke=POS, sw=1.4))
    render(os.path.join(OUT, 'risk-to-pfd-chain.svg'), W, H, *frags)


# ── Фігура 5 (вставка math): пилка PFD між перевірками; резерв зсуває середнє ──
def fig_pfd_sawtooth():
    W, H = 820, 440
    frags = []
    frags.append(text(W / 2, 28,
                      "Чому інтервал перевірки й резерв рухають ймовірність",
                      size=14, bold=True))

    # спільні осі
    ox, oy = 80, 250          # початок координат (лівий-нижній)
    axw, axh = 280, 170
    # ── ліва панель: 1oo1, довга пилка ──
    frags.append(text(ox + axw / 2, 60, "Один канал (1oo1)", size=13, bold=True, color=POS))
    frags.append(line(ox, oy, ox + axw, oy, color=INK, sw=1.6))          # вісь часу
    frags.append(line(ox, oy, ox, oy - axh, color=INK, sw=1.6))          # вісь PFD(t)
    frags.append(text(ox + axw / 2, oy + 30, "час →  (перевірки TI)", size=11, color=MUTED))
    frags.append(('<text x="%.1f" y="%.1f" font-family="%s" font-size="11" fill="%s" '
                  'text-anchor="middle" transform="rotate(-90 %.1f %.1f)">миттєва PFD(t)</text>'
                  % (ox - 26, oy - axh / 2, FONT, MUTED, ox - 26, oy - axh / 2)))
    # пилка: PFD росте лінійно λ·t, перевірка обнуляє. Два зуби на всю ширину.
    peak = axh * 0.82
    teeth = 2
    tw = axw / teeth
    for i in range(teeth):
        x0 = ox + i * tw
        frags.append(line(x0, oy, x0 + tw, oy - peak, color=POS, sw=2.2))
        frags.append(line(x0 + tw, oy - peak, x0 + tw, oy, color=POS, sw=1.4, dash="3,3"))
    # середнє = половина піку
    frags.append(line(ox, oy - peak / 2, ox + axw, oy - peak / 2, color=INK, sw=1.6, dash="6,4"))
    frags.append(text(ox + axw + 4, oy - peak / 2 + 4, "PFDavg", size=11, color=INK, anchor="start"))
    frags.append(text(ox + tw / 2, oy - peak - 8, "λ·TI", size=11, color=POS))

    # ── права панель: 1oo2, крихітна пилка ──
    ox2 = ox + axw + 120
    frags.append(text(ox2 + axw / 2, 60, "Два канали (1oo2)", size=13, bold=True, color=FIELD))
    frags.append(line(ox2, oy, ox2 + axw, oy, color=INK, sw=1.6))
    frags.append(line(ox2, oy, ox2, oy - axh, color=INK, sw=1.6))
    frags.append(text(ox2 + axw / 2, oy + 30, "той самий час, той самий TI", size=11, color=MUTED))
    peak2 = axh * 0.14        # квадратично менший
    for i in range(teeth):
        x0 = ox2 + i * tw
        frags.append(line(x0, oy, x0 + tw, oy - peak2, color=FIELD, sw=2.2))
        frags.append(line(x0 + tw, oy - peak2, x0 + tw, oy, color=FIELD, sw=1.4, dash="3,3"))
    frags.append(line(ox2, oy - peak2 / 2, ox2 + axw, oy - peak2 / 2, color=INK, sw=1.4, dash="6,4"))
    frags.append(text(ox2 + tw / 2, oy - peak2 - 8, "~(λ·TI)²", size=11, color=FIELD))
    # пунктирна «стеля» спільної причини
    ccf = axh * 0.30
    frags.append(line(ox2, oy - ccf, ox2 + axw, oy - ccf, color=POS, sw=1.6, dash="2,3"))
    frags.append(text(ox2 + axw - 4, oy - ccf - 6, "стеля спільної причини β·λ·TI/2",
                      size=10, color=POS, anchor="end"))

    # підсумкові рядки
    frags.append(fitbox(70, H - 96, W - 140, 34,
                        "Удвічі частіші перевірки — удвічі нижча пилка: PFDavg ≈ λ·TI/2 лінійно залежить від TI.",
                        size=12, fill="#eef2f7", stroke=INK, sw=1.4))
    frags.append(fitbox(70, H - 52, W - 140, 30,
                        "Резерв робить пилку квадратичною (~(λ·TI)²) — та лише до стелі β: спільна причина не ділиться навпіл.",
                        size=12, fill="#fdecea", stroke=POS, sw=1.4))
    render(os.path.join(OUT, 'pfd-sawtooth.svg'), W, H, *frags)


# ── Фігура D1 (детальна): два види відмов — випадкова vs систематична ─────────
def fig_two_failure_species():
    W, H = 860, 470
    frags = []
    frags.append(text(W / 2, 30, "Два роди відмов: лише один має ймовірність",
                      size=15, bold=True))

    # корінь — усі відмови
    root, rw, rh = textbox(W / 2, 78, "Відмова системи безпеки", size=14, bold=True,
                           fill="#eef2f7", stroke=INK, sw=2.2, min_w=300)
    frags.append(root)

    # дві гілки
    lx, rx = W * 0.27, W * 0.73
    ytop = 150
    frags.append(line(W / 2, 78 + rh / 2, W / 2, ytop - 26, color=MUTED, sw=1.6))
    frags.append(line(lx, ytop - 26, rx, ytop - 26, color=MUTED, sw=1.6))
    frags.append(line(lx, ytop - 26, lx, ytop, color=POS, sw=1.8))
    frags.append(line(rx, ytop - 26, rx, ytop, color=NEG, sw=1.8))

    # ліва гілка — випадкова
    lhead, lw, lh = textbox(lx, ytop + 24, "ВИПАДКОВА\nвідмова заліза",
                            size=13, bold=True, fill="#fdecea", stroke=POS, sw=2.0, min_w=230)
    frags.append(lhead)
    frags.append(fitbox(lx - 150, ytop + 66, 300, 84,
                        "транзистор пробило · конденсатор висох ·\n"
                        "космічний промінь перевернув біт\n\n"
                        "рідкісна, непередбачувана в часі,\n"
                        "але статистично рівна для мільйона копій",
                        size=11, fill="#fff8f7", stroke=POS, sw=1.3))
    frags.append(fitbox(lx - 150, ytop + 160, 300, 46,
                        "→ має λ і ймовірність (PFD/PFH)\n→ б'ється числом, резервом, діагностикою",
                        size=11.5, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.6))

    # права гілка — систематична
    rhead, rw2, rh2 = textbox(rx, ytop + 24, "СИСТЕМАТИЧНА\nвідмова",
                              size=13, bold=True, fill="#eaf0fd", stroke=NEG, sw=2.0, min_w=230)
    frags.append(rhead)
    frags.append(fitbox(rx - 150, ytop + 66, 300, 84,
                        "хибна специфікація · «>» замість «>=» ·\n"
                        "компілятор викинув перевірку\n\n"
                        "вже сидить у системі з народження,\n"
                        "спрацьовує ЩОРАЗУ однаково в усіх копіях",
                        size=11, fill="#f7f9ff", stroke=NEG, sw=1.3))
    frags.append(fitbox(rx - 150, ytop + 160, 300, 46,
                        "→ ймовірності НЕ має (або є, або ні)\n→ б'ється ЛИШЕ процесом: рецензування, тести",
                        size=11.5, bold=True, fill="#eafaf1", stroke=FIELD, sw=1.6))

    frags.append(fitbox(60, H - 44, W - 120, 30,
                        "Різні природи → різні засоби → різні частини стандарту. Резерв двох каналів не рятує від тієї самої помилки в коді обох.",
                        size=12, fill="#fdf6ec", stroke="#8a5a1f", sw=1.4))
    render(os.path.join(OUT, 'two-failure-species.svg'), W, H, *frags)


# ── Фігура D2 (детальна): SIL як вектор трьох осей — мінімум по найслабшій ────
def fig_sil_three_axes():
    W, H = 860, 430
    frags = []
    frags.append(text(W / 2, 30, "Рівень — вектор із трьох вимог: SIL = мінімум по найслабшій осі",
                      size=15, bold=True))

    axes = [
        ("Цільова міра відмов", "PFD / PFH", "ловить ВИПАДКОВЕ", "доведення: розрахунок", POS),
        ("Архітектурні обмеження", "SFF · HFT · тип A/B", "страховка на неточність\nмоделі відмов", "доведення: структура", "#8a5a1f"),
        ("Систематична спроможність", "SC 1…4", "ловить СИСТЕМАТИЧНЕ", "доведення: аудит процесу", NEG),
    ]
    n = len(axes)
    bw, gap = 240, 26
    total = n * bw + (n - 1) * gap
    x0 = (W - total) / 2
    ytop = 74
    bh = 172
    for i, (name, sym, catch, proof, col) in enumerate(axes):
        x = x0 + i * (bw + gap)
        frags.append(rect(x, ytop, bw, bh, fill="#fbfbfb", stroke=col, sw=2.0))
        frags.append(text(x + bw / 2, ytop + 26, name, size=13, bold=True, color=col))
        frags.append(text(x + bw / 2, ytop + 54, sym, size=15, bold=True, color=INK))
        frags.append(mtext(x + bw / 2, ytop + 88, catch, size=11.5, color=MUTED))
        frags.append(line(x + 20, ytop + bh - 40, x + bw - 20, ytop + bh - 40, color=col, sw=1.0, dash="3,3"))
        frags.append(text(x + bw / 2, ytop + bh - 18, proof, size=11.5, bold=True, color=col))
        # знак «AND» між осями
        if i < n - 1:
            frags.append(text(x + bw + gap / 2, ytop + bh / 2, "×", size=22, bold=True, color=INK))

    # нижня плашка — правило мінімуму
    frags.append(fitbox(x0, ytop + bh + 34, total, 40,
                        "Усі три мусять дотягтися до планки. Блискуча PFD при слабкій структурі АБО недорецензованому коді → рівень падає до найслабшої осі.",
                        size=12, fill="#eef2f7", stroke=INK, sw=1.5))
    frags.append(fitbox(x0, ytop + bh + 84, total, 30,
                        "Класична помилка новачка: оптимізувати одну вісь (PFD), а рівень визначає інша.",
                        size=12, fill="#fdecea", stroke=POS, sw=1.4))
    render(os.path.join(OUT, 'sil-three-axes.svg'), W, H, *frags)


# ── Фігура D3 (детальна): бюджет часу реакції — FDTI + FRTI < FTTI ────────────
def fig_ftti_timeline():
    W, H = 860, 420
    frags = []
    frags.append(text(W / 2, 30, "Безпечний стан має дедлайн: виявити + відреагувати < час до шкоди",
                      size=15, bold=True))

    # головна смуга часу
    ax0, ax1 = 90, 770
    ty = 150
    frags.append(line(ax0, ty, ax1, ty, color=INK, sw=2.2))
    frags.append(arrow(ax1 - 2, ty, ax1 + 24, ty, color=INK, sw=2.2))
    frags.append(text(ax1 + 30, ty + 4, "час", size=12, color=INK, anchor="start"))

    # три точки на осі: відмова, виявлення, безпечний стан; праворуч — шкода (дедлайн)
    x_fault = ax0 + 20
    x_detect = ax0 + 300
    x_safe = ax0 + 430
    x_harm = ax1 - 30

    for x, lbl, col in [(x_fault, "відмова\nсталася", POS),
                        (x_detect, "діагностика\nзасікла", "#8a5a1f"),
                        (x_safe, "безпечний\nстан зайнято", FIELD),
                        (x_harm, "ШКОДА\n(якщо нічого не робити)", POS)]:
        frags.append(line(x, ty - 12, x, ty + 12, color=col, sw=2.4))
        # підпис угору для крайніх, униз для середніх — щоб не накладались
    frags.append(mtext(x_fault, ty - 30, "відмова\nсталася", size=11, color=POS, bold=True))
    frags.append(mtext(x_detect, ty - 30, "діагностика\nзасікла", size=11, color="#8a5a1f", bold=True))
    frags.append(mtext(x_safe, ty - 30, "безпечний\nстан зайнято", size=11, color=FIELD, bold=True))
    frags.append(mtext(x_harm, ty - 30, "ШКОДА\nбез реакції", size=11, color=POS, bold=True))

    # інтервали під віссю: FDTI, FRTI, і зверху великий FTTI
    def span(x1, x2, y, label, col, up=False):
        out = [line(x1, y, x2, y, color=col, sw=1.8)]
        out.append(line(x1, y - 5, x1, y + 5, color=col, sw=1.8))
        out.append(line(x2, y - 5, x2, y + 5, color=col, sw=1.8))
        out.append(text((x1 + x2) / 2, y + (16 if not up else -8), label, size=12, bold=True, color=col))
        return out

    frags += span(x_fault, x_detect, ty + 46, "FDTI  (виявлення)", "#8a5a1f")
    frags += span(x_detect, x_safe, ty + 46, "FRTI  (реакція)", FIELD)
    # великий FTTI зверху — від відмови до шкоди
    frags += span(x_fault, x_harm, ty + 96, "FTTI  —  дедлайн від фізики небезпеки", POS)

    # нерівність унизу
    frags.append(fitbox(90, H - 128, W - 180, 40,
                        "FDTI + FRTI  <  FTTI     —     час помітити плюс час відреагувати мусить лишатися меншим за час до біди.",
                        size=13, bold=True, fill="#eef2f7", stroke=INK, sw=1.6))
    frags.append(fitbox(90, H - 78, W - 180, 30,
                        "FDTI задається частотою діагностики: DTI < FTTI/2, інакше відмова дозріє до шкоди між двома перевірками.",
                        size=12, fill="#fdf6ec", stroke="#8a5a1f", sw=1.4))
    frags.append(fitbox(90, H - 40, W - 180, 28,
                        "Не вклався в дедлайн — failsafe спрацює вже ПІСЛЯ біди, і вся логіка марна.",
                        size=12, fill="#fdecea", stroke=POS, sw=1.4))
    render(os.path.join(OUT, 'ftti-timeline.svg'), W, H, *frags)


# ── Фігура (hist): де жила першопричина — розтин HSE «Out of Control» ─────────
def fig_hsg_phases():
    W, H = 820, 430
    frags = []
    frags.append(text(W / 2, 30, "Де жила першопричина 34 аварій: розтин HSE «Out of Control»",
                      size=15, bold=True))
    frags.append(text(W / 2, 50, "частка аварій, чия головна причина зародилась у цій фазі життєвого циклу",
                      size=11, color=MUTED))

    # (мітка фази, відсоток, колір); специфікація — гаряча, вона й «переможець»
    rows = [
        ("Специфікація", 44, POS),
        ("Зміни після впровадження", 20, "#d98324"),
        ("Проєктування й реалізація", 15, NEG),
        ("Експлуатація й обслуговування", 15, "#8a5a1f"),
        ("Монтаж і введення в дію", 6, FIELD),
    ]
    lab_x = 250            # права межа колонки з підписами фаз
    bar_x = lab_x + 20     # старт смуг
    scale = 9.6            # px на 1%
    y0 = 92
    step = 58
    bh = 34

    # вісь-шкала 10/20/30/40 %: лише короткі поділки над смугами (без наскрізних
    # ліній — щоб жодна не перетнула підписів усередині діаграми).
    for g in (10, 20, 30, 40):
        gx = bar_x + g * scale
        frags.append(line(gx, y0 - 10, gx, y0 - 2, color=MUTED, sw=1.4))
        frags.append(text(gx, y0 - 16, "%d%%" % g, size=10, color=MUTED))

    for i, (name, pct, col) in enumerate(rows):
        y = y0 + i * step
        frags.append(text(lab_x, y + bh / 2 + 5, name, size=13, color=INK, anchor="end"))
        frags.append(rect(bar_x, y, pct * scale, bh, fill="#f4f6f8", stroke=col, sw=2.0))
        frags.append(text(bar_x + pct * scale + 10, y + bh / 2 + 5, "%d%%" % pct,
                          size=14, color=col, bold=True, anchor="start"))

    # виноска до смуги специфікації: з чого ті 44% складаються
    sy = y0 + bh + 6
    frags.append(mtext(bar_x + 8, sy + 15,
                       ["з них: неповні функційні вимоги + непродумана",
                        "цілісність безпеки — обидва народжуються за столом"],
                       size=11, color=POS, anchor="start", lh=1.25))

    # підсумковий рядок унизу (два рядки — щоб шрифт лишався читабельним)
    frags.append(fitbox(60, H - 62, W - 120, 44,
                        "Майже дві третини аварій (44% + 20%) — не «зламалось залізо»,\n"
                        "а «людина чогось не задумала»: пропущений режим або необдумана зміна.",
                        size=13, bold=True, fill="#fdecea", stroke=POS, sw=1.5))
    render(os.path.join(OUT, 'hsg238-phases.svg'), W, H, *frags)


if __name__ == '__main__':
    fig_family()
    fig_sil_ladder()
    fig_safety_loop()
    fig_risk_chain()
    fig_pfd_sawtooth()
    fig_two_failure_species()
    fig_sil_three_axes()
    fig_ftti_timeline()
    fig_hsg_phases()
    print("ok")
