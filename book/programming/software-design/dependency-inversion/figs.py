# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Розворот стрілки: «природно» ліворуч → «інверсія» праворуч ────────────────
def fig_inversion():
    W, H = 1000, 560
    frags = []

    # роздільник між двома панелями
    frags.append(line(W / 2, 70, W / 2, H - 30, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА панель: природний напрямок ──
    lcx = W / 4
    frags.append(text(lcx, 58, "Природно: стрілка тече вниз", size=15, bold=True))

    hi, hw, hh = textbox(lcx, 130, "Модуль високого рівня\n(бізнес-правило)",
                         size=13, bold=True, pad=14, fill="#eef4ff", stroke=INK, sw=1.8)
    frags.append(hi)
    lo, lw, lh = textbox(lcx, 400, "Конкретна деталь\n(база / мережа / пристрій)",
                         size=13, pad=14, fill="#fdecea", stroke=POS, sw=1.8)
    frags.append(lo)
    # стрілка залежності зверху вниз
    frags.append(arrow(lcx, 130 + hh / 2 + 6, lcx, 400 - lh / 2 - 6, color=POS, sw=2.6))
    lbl, _, _ = textbox(lcx + 96, 265, "залежить\nвід", size=11, pad=6,
                        fill="#ffffff", stroke=POS, sw=1.2, color=POS, bold=True)
    frags.append(lbl)
    frags.append(text(lcx, 470, "важливе прибите до дрібного",
                      size=12, bold=True, color=POS))

    # ── ПРАВА панель: інверсія ──
    rcx = 3 * W / 4
    frags.append(text(rcx, 58, "Інверсія: обидві стрілки — до абстракції",
                      size=15, bold=True))

    hi2, hw2, hh2 = textbox(rcx, 130, "Модуль високого рівня\n(бізнес-правило)",
                            size=13, bold=True, pad=14, fill="#eef4ff", stroke=INK, sw=1.8)
    frags.append(hi2)
    ab, abw, abh = textbox(rcx, 265, "Абстракція\n(інтерфейс, мовою ядра)",
                           size=13, bold=True, pad=14, fill="#f2faf5", stroke=FIELD, sw=2.2)
    frags.append(ab)
    de, dew, deh = textbox(rcx, 400, "Конкретна деталь\n(реалізує інтерфейс)",
                           size=13, pad=14, fill="#fdecea", stroke=POS, sw=1.8)
    frags.append(de)

    # стрілка ядро → абстракція (вниз)
    frags.append(arrow(rcx, 130 + hh2 / 2 + 6, rcx, 265 - abh / 2 - 6, color=INK, sw=2.4))
    # стрілка деталь → абстракція (вгору!)
    frags.append(arrow(rcx, 400 - deh / 2 - 6, rcx, 265 + abh / 2 + 6, color=POS, sw=2.4))

    frags.append(text(rcx + 150, 197, "залежить від", size=11, bold=True, color=INK))
    frags.append(text(rcx + 150, 335, "реалізує", size=11, bold=True, color=POS))
    frags.append(text(rcx, 470, "деталь на кінці — замінна",
                      size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, 'inversion.svg'), W, H, *frags,
           title="Інверсія залежностей: розворот природного напрямку стрілки")


# ── Хто кого гукає: бібліотека (ти → неї) проти каркаса (він → тебе) ──────────
def fig_hollywood():
    W, H = 1020, 470
    frags = []

    # роздільник між двома панелями
    frags.append(line(W / 2, 74, W / 2, H - 34, color="#d0d5db", sw=1.2, dash="5,5"))

    top_y, bot_y = 150, 350   # центри верхнього й нижнього блоків

    # ── ЛІВА панель: БІБЛІОТЕКА ──
    lcx = W / 4
    frags.append(text(lcx, 56, "Бібліотека: керування лишається в тебе",
                      size=15, bold=True))

    ta, taw, tah = textbox(lcx, top_y, "Твій код\n(головний хід)",
                           size=13, bold=True, pad=15, fill="#eef4ff",
                           stroke=INK, sw=1.9, min_w=210)
    frags.append(ta)
    ba, baw, bah = textbox(lcx, bot_y, "Бібліотека\n(набір функцій)",
                           size=13, pad=15, fill="#f2faf5",
                           stroke=FIELD, sw=1.9, min_w=210)
    frags.append(ba)

    off = 46   # рознесення двох зустрічних стрілок по горизонталі
    # ти ГУКАЄШ бібліотеку (вниз, ліворуч від центру)
    frags.append(arrow(lcx - off, top_y + tah / 2 + 6,
                       lcx - off, bot_y - bah / 2 - 6, color=INK, sw=2.4))
    # бібліотека ПОВЕРТАЄ керування (вгору, праворуч від центру)
    frags.append(arrow(lcx + off, bot_y - bah / 2 - 6,
                       lcx + off, top_y + tah / 2 + 6, color=FIELD, sw=2.4))

    l1, _, _ = textbox(lcx - off - 66, (top_y + bot_y) / 2, "ти\nгукаєш",
                       size=11, pad=6, fill="#ffffff", stroke=INK, sw=1.1,
                       color=INK, bold=True)
    frags.append(l1)
    l2, _, _ = textbox(lcx + off + 74, (top_y + bot_y) / 2, "керування\nназад",
                       size=11, pad=6, fill="#ffffff", stroke=FIELD, sw=1.1,
                       color=FIELD, bold=True)
    frags.append(l2)

    # ── ПРАВА панель: КАРКАС ──
    rcx = 3 * W / 4
    frags.append(text(rcx, 56, "Каркас: керування тримає він",
                      size=15, bold=True))

    fr, frw, frh = textbox(rcx, top_y, "Каркас\n(головний хід)",
                           size=13, bold=True, pad=15, fill="#f2faf5",
                           stroke=FIELD, sw=1.9, min_w=210)
    frags.append(fr)
    yc, ycw, ych = textbox(rcx, bot_y, "Твій обробник\n(вставлено збоку)",
                           size=13, pad=15, fill="#eef4ff",
                           stroke=INK, sw=1.9, min_w=210)
    frags.append(yc)

    # каркас ГУКАЄ твій код (вниз, ліворуч від центру)
    frags.append(arrow(rcx - off, top_y + frh / 2 + 6,
                       rcx - off, bot_y - ych / 2 - 6, color=POS, sw=2.6))
    # твій обробник ВІДПРАЦЮВАВ — керування назад каркасу (вгору, праворуч)
    frags.append(arrow(rcx + off, bot_y - ych / 2 - 6,
                       rcx + off, top_y + frh / 2 + 6, color=INK, sw=2.2))

    r1, _, _ = textbox(rcx - off - 84, (top_y + bot_y) / 2, "він гукає\nтебе",
                       size=11, pad=6, fill="#ffffff", stroke=POS, sw=1.1,
                       color=POS, bold=True)
    frags.append(r1)
    r2, _, _ = textbox(rcx + off + 66, (top_y + bot_y) / 2, "керування\nназад",
                       size=11, pad=6, fill="#ffffff", stroke=INK, sw=1.1,
                       color=INK, bold=True)
    frags.append(r2)

    frags.append(text(rcx, H - 16, "«не дзвоніть нам — ми подзвонимо вам»",
                      size=12, bold=True, italic=True, color=POS))

    render(os.path.join(IMG, 'hollywood.svg'), W, H, *frags,
           title="Інверсія керування: хто кого гукає в часі виконання")


# ── Дві стрілки на одній межі: керування вниз, залежність джерела — вгору ─────
def fig_two_flows():
    W, H = 1040, 520
    frags = []
    yrow = 300

    pol, pw, ph = textbox(215, yrow, "Політика\n(високий рівень)", size=13, bold=True,
                          pad=13, fill="#eef4ff", stroke=INK, sw=1.9, min_w=200)
    port, rw, rh = textbox(520, yrow, "Порт (інтерфейс)\nмовою політики", size=13, bold=True,
                           pad=13, fill="#f2faf5", stroke=FIELD, sw=2.2, min_w=250)
    adp, aw, ah = textbox(825, yrow, "Адаптер\n(база / мережа / SDK)", size=13,
                          pad=13, fill="#fdecea", stroke=POS, sw=1.9, min_w=220)
    frags += [pol, port, adp]

    pol_r = 215 + pw / 2
    port_l, port_r = 520 - rw / 2, 520 + rw / 2
    adp_l = 825 - aw / 2

    # залежність коду (компіляція): обидві стрілки — ВСЕРЕДИНУ, до порту
    frags.append(arrow(pol_r + 6, yrow, port_l - 6, yrow, color=INK, sw=2.5))
    frags.append(arrow(adp_l - 6, yrow, port_r + 6, yrow, color=POS, sw=2.5))
    frags.append(text((pol_r + port_l) / 2, yrow - 16, "залежить від", size=11, bold=True, color=INK))
    frags.append(text((port_r + adp_l) / 2, yrow - 16, "реалізує", size=11, bold=True, color=POS))

    # керування (рантайм): дужкою над блоками, від політики через порт до адаптера
    ytop = 178
    frags.append(line(215, yrow - ph / 2 - 6, 215, ytop, color=FIELD, sw=2.2, dash="6,5"))
    frags.append(line(215, ytop, 825, ytop, color=FIELD, sw=2.2, dash="6,5"))
    frags.append(arrow(825, ytop, 825, yrow - ah / 2 - 6, color=FIELD, sw=2.6))
    frags.append(text(520, ytop - 12, "керування у рантаймі: політика гукає адаптер",
                      size=13, bold=True, color=FIELD))

    frags.append(text(520, 416, "Одна межа — два зустрічні потоки.", size=14, bold=True))
    frags.append(text(520, 446, "Керування тече праворуч (у деталь), а залежність коду — ліворуч (у порт).",
                      size=12, color=MUTED))
    frags.append(text(520, 470, "Тому деталь замінна, а політика про заміну й не знає.",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'two-flows.svg'), W, H, *frags,
           title="Дві стрілки на одній межі: керування вниз, залежність — угору")


# ── Де живе інтерфейс, там і напрямок залежності пакета ───────────────────────
def fig_ownership():
    W, H = 1100, 560
    frags = []
    frags.append(line(W / 2, 82, W / 2, H - 44, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ЛІВА: інтерфейс у пакеті ДЕТАЛІ — інверсії деплою НЕМА ──
    lcx = 275
    frags.append(text(lcx, 62, "Інтерфейс — у пакеті деталі", size=15, bold=True))

    frags.append(rect(lcx - 130, 100, 260, 84, fill="#ffffff", stroke=INK, sw=1.6))
    frags.append(text(lcx - 120, 118, "пакет високого рівня", size=10, color=MUTED, anchor="start"))
    hi, _, _ = textbox(lcx, 152, "Політика", size=13, bold=True, pad=10,
                       fill="#eef4ff", stroke=INK, sw=1.6, min_w=150)
    frags.append(hi)

    frags.append(rect(lcx - 150, 300, 300, 150, fill="#ffffff", stroke=POS, sw=1.6))
    frags.append(text(lcx - 140, 318, "пакет низького рівня", size=10, color=MUTED, anchor="start"))
    itf, _, _ = textbox(lcx, 352, "Інтерфейс", size=12, bold=True, pad=9,
                        fill="#f2faf5", stroke=FIELD, sw=1.8, min_w=150)
    frags.append(itf)
    adp, _, _ = textbox(lcx, 414, "Адаптер", size=12, pad=9,
                        fill="#fdecea", stroke=POS, sw=1.6, min_w=150)
    frags.append(adp)

    # клас-залежність: Політика → Інтерфейс (вниз, крізь межу пакетів)
    frags.append(arrow(lcx, 172, lcx, 335, color=INK, sw=2.2))
    # пакет-залежність (ліворуч): високий → низький
    frags.append(arrow(lcx - 178, 184, lcx - 178, 300, color=POS, sw=3.4))
    frags.append(text(lcx, 492, "політика тягне пакет деталі —", size=12, bold=True, color=POS))
    frags.append(text(lcx, 514, "деплой-залежність НЕ перевернулась", size=12, bold=True, color=POS))

    # ── ПРАВА: інтерфейс у пакеті ПОЛІТИКИ — деплой перевернувся ──
    rcx = 825
    frags.append(text(rcx, 62, "Інтерфейс — у пакеті політики", size=15, bold=True))

    frags.append(rect(rcx - 150, 100, 300, 150, fill="#ffffff", stroke=INK, sw=1.6))
    frags.append(text(rcx - 140, 118, "пакет високого рівня", size=10, color=MUTED, anchor="start"))
    hi2, _, _ = textbox(rcx, 150, "Політика", size=13, bold=True, pad=9,
                        fill="#eef4ff", stroke=INK, sw=1.6, min_w=150)
    frags.append(hi2)
    itf2, _, _ = textbox(rcx, 212, "Інтерфейс", size=12, bold=True, pad=9,
                         fill="#f2faf5", stroke=FIELD, sw=1.8, min_w=150)
    frags.append(itf2)

    frags.append(rect(rcx - 130, 366, 260, 84, fill="#ffffff", stroke=POS, sw=1.6))
    frags.append(text(rcx - 120, 384, "пакет низького рівня", size=10, color=MUTED, anchor="start"))
    adp2, _, _ = textbox(rcx, 416, "Адаптер", size=12, pad=10,
                         fill="#fdecea", stroke=POS, sw=1.6, min_w=150)
    frags.append(adp2)

    # клас-залежність: Адаптер → Інтерфейс (вгору, реалізує, крізь межу)
    frags.append(arrow(rcx, 396, rcx, 233, color=POS, sw=2.2))
    # пакет-залежність (праворуч): низький → високий
    frags.append(arrow(rcx + 178, 366, rcx + 178, 250, color=FIELD, sw=3.4))
    frags.append(text(rcx, 492, "адаптер залежить від пакета політики —", size=12, bold=True, color=FIELD))
    frags.append(text(rcx, 514, "деплой-залежність перевернулась", size=12, bold=True, color=FIELD))

    render(os.path.join(IMG, 'ownership.svg'), W, H, *frags,
           title="Хто володіє інтерфейсом, той і диктує напрямок залежності пакета")


# ── Граф залежностей одного сценарію: усі стрілки коду — до домену ─────────────
def fig_hexagon_inward():
    W, H = 1140, 660
    frags = []

    # ── ДОМЕН (велика рамка) ──
    dx, dy, dw, dh = 340, 92, 470, 300
    frags.append(rect(dx, dy, dw, dh, fill="#f6f9ff", stroke=INK, sw=2.4))
    cx = dx + dw / 2   # 575
    frags.append(text(cx, dy + 26, "ДОМЕН (політика)", size=14, bold=True))

    # сутність
    ent, _, _ = textbox(cx, 170, "Order — сутність + правила\n(сума, валідність)",
                        size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.6, min_w=310)
    frags.append(ent)
    # сценарій
    uc, _, uch = textbox(cx, 240, "PlaceOrder — сценарій\nзберегти замовлення + сповістити",
                         size=12, bold=True, pad=10, fill="#eef4ff", stroke=INK, sw=2.0, min_w=340)
    frags.append(uc)
    # два порти на нижньому краї домену
    op, opw, oph = textbox(cx - 108, 338, "Orders\nпорт-репозиторій",
                           size=11, bold=True, pad=8, fill="#f2faf5", stroke=FIELD, sw=2.0, min_w=152)
    npb, npw, nph = textbox(cx + 108, 338, "Notifier\nпорт-сповіщувач",
                            size=11, bold=True, pad=8, fill="#f2faf5", stroke=FIELD, sw=2.0, min_w=152)
    frags += [op, npb]
    # внутрішні стрілки: сценарій → кожен порт (залежить від)
    frags.append(arrow(cx - 44, 240 + uch / 2 + 4, cx - 100, 338 - oph / 2 - 5, color=INK, sw=1.9))
    frags.append(arrow(cx + 44, 240 + uch / 2 + 4, cx + 100, 338 - nph / 2 - 5, color=INK, sw=1.9))

    # ── АДАПТЕРИ (зовні, знизу) ──
    ay = 514
    specs = [(378, "InMemoryOrders\nMap у пам'яті", cx - 148),
             (556, "PgOrders\nPostgres · SQL", cx - 88),
             (734, "InMemoryNotifier\nшпигун", cx + 92),
             (918, "SmtpNotifier\nSMTP · лист", cx + 140)]
    port_bottom = 338 + oph / 2
    for axc, label, target_x in specs:
        box, bw, bh = textbox(axc, ay, label, size=11, pad=8,
                              fill="#fdecea", stroke=POS, sw=1.6, min_w=152)
        frags.append(box)
        frags.append(arrow(axc, ay - bh / 2 - 4, target_x, port_bottom + 6, color=POS, sw=1.9))

    # ── КОРІНЬ ЗБІРКИ (main) ──
    mainbox, mbw, mbh = textbox(150, 150, "main\n(корінь збірки)",
                                size=12, bold=True, pad=10, fill="#f2faf5", stroke=FIELD, sw=1.8, min_w=156)
    frags.append(mainbox)
    frags.append(arrow(150 + mbw / 2 + 4, 158, dx - 5, 186, color=FIELD, sw=2.0))
    frags.append(text(150, 150 + mbh / 2 + 22, "знає домен і всі 4 адаптери", size=10, color=MUTED))

    # ── ЛЕГЕНДА (лівий нижній кут, поза стрілками) ──
    lx, ly = 74, 588
    frags.append(text(lx, ly, "стрілки коду:", size=11, bold=True, anchor="start", color=INK))
    frags.append(text(lx, ly + 22, "— залежить від", size=11, bold=True, anchor="start", color=INK))
    frags.append(text(lx, ly + 44, "— реалізує порт", size=11, bold=True, anchor="start", color=POS))
    frags.append(text(lx + 200, ly + 22, "— складає (main)", size=11, bold=True, anchor="start", color=FIELD))

    render(os.path.join(IMG, 'hexagon-inward.svg'), W, H, *frags,
           title="Граф залежностей сценарію: кожна стрілка коду впирається в домен")


# ── Сценарій-тест на підробках: один драйвер — два перевірені ефекти ──────────
def fig_scenario_test():
    W, H = 1080, 540
    frags = []

    tb, tbw, tbh = textbox(175, 120, "тест (драйвер)\nбез бази й мережі",
                           size=12, bold=True, pad=10, fill="#eef4ff", stroke=INK, sw=1.8, min_w=176)
    frags.append(tb)

    pob, pobw, pobh = textbox(540, 140, "PlaceOrder.run(cmd)\nсценарій-політика",
                              size=13, bold=True, pad=12, fill="#f2faf5", stroke=FIELD, sw=2.4, min_w=300)
    frags.append(pob)
    frags.append(arrow(175 + tbw / 2 + 4, 128, 540 - pobw / 2 - 5, 138, color=INK, sw=1.9))
    frags.append(text((175 + tbw / 2 + 540 - pobw / 2) / 2, 112, "гукає", size=10, color=MUTED))

    fo, fow, foh = textbox(350, 320, "FakeOrders\nсловник у пам'яті",
                           size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.6, min_w=182)
    fn, fnw, fnh = textbox(730, 320, "FakeNotifier — шпигун\nзаписує надіслане",
                           size=12, pad=10, fill="#fdecea", stroke=POS, sw=1.6, min_w=182)
    frags += [fo, fn]

    py = 140 + pobh / 2 + 4
    frags.append(arrow(470, py, 360, 320 - foh / 2 - 5, color=INK, sw=1.9))
    frags.append(arrow(610, py, 720, 320 - fnh / 2 - 5, color=INK, sw=1.9))
    frags.append(text(392, 236, "orders.save", size=10, color=INK, anchor="end"))
    frags.append(text(690, 236, "notifier.send", size=10, color=INK, anchor="start"))

    as1 = fitbox(214, 418, 272, 46, "✔ byId(id) → той самий Order\nзамовлення збережено",
                 size=11, pad=8, fill="#f2faf5", stroke=FIELD, sw=1.8)
    as2 = fitbox(586, 418, 288, 46, "✔ рівно 1 лист, на пошту клієнта\nсповіщення надіслано",
                 size=11, pad=8, fill="#f2faf5", stroke=FIELD, sw=1.8)
    frags += [as1, as2]
    frags.append(arrow(350, 320 + foh / 2 + 4, 350, 416, color=FIELD, sw=1.9))
    frags.append(arrow(730, 320 + fnh / 2 + 4, 730, 416, color=FIELD, sw=1.9))

    render(os.path.join(IMG, 'scenario-test.svg'), W, H, *frags,
           title="Сценарій-тест на підробках: один драйвер — два перевірені ефекти")


# ── Головна послідовність A+I=1: де сидять пакети, дві отруйні зони ────────────
def fig_main_sequence():
    W, H = 680, 560
    frags = []
    frags.append(text(W / 2, 30, "Головна послідовність A+I=1: стабільне ⇒ абстрактне",
                      size=16, bold=True))

    ox, oy = 150, 460
    L = 330

    def px(i, a):
        return ox + i * L, oy - a * L

    # осі
    frags.append(arrow(ox, oy, ox + L + 30, oy, color=INK, sw=1.6))
    frags.append(arrow(ox, oy, ox, oy - L - 30, color=INK, sw=1.6))
    frags.append(text(ox + L + 22, oy + 26, "I (нестабільність)", size=12, color=INK, anchor="end"))
    frags.append(text(ox - 42, oy - L / 2 - 4, "A", size=13, color=INK, bold=True))
    frags.append(text(ox - 54, oy - L / 2 + 14, "(абстр.)", size=10, color=MUTED))
    frags.append(text(ox, oy + 26, "0", size=11, color=MUTED))
    frags.append(text(ox + L, oy + 26, "1", size=11, color=MUTED))
    frags.append(text(ox - 20, oy + 4, "0", size=11, color=MUTED))
    frags.append(text(ox - 20, oy - L + 8, "1", size=11, color=MUTED))

    # діагональ — головна послідовність
    x0, y0 = px(0, 1)
    x1, y1 = px(1, 0)
    frags.append(line(x0, y0, x1, y1, color=FIELD, sw=3))
    frags.append(text(x0 + 104, y0 + 12, "A + I = 1", size=13, color=FIELD, bold=True, anchor="start"))
    frags.append(text(x0 + 104, y0 + 30, "(DIP-ідеал)", size=11, color=FIELD, anchor="start"))

    # зона болю — нижній лівий кут (I≈0, A≈0)
    bx, by = px(0, 0)
    frags.append(circle(bx + 5, by - 5, 7, fill="#fdeeec", stroke=POS, sw=2))
    fb, wb, hb = textbox(300, 408,
                         "ЗОНА БОЛЮ (I≈0, A≈0)\nстабільне + конкретне:\nусі залежать — гнучкості нема",
                         size=11, pad=8, fill="#fdeeec", stroke=POS, sw=1.4)
    frags.append(line(bx + 11, by - 9, 300 - wb / 2, 408 + hb / 2, color=POS, sw=1.2, dash="4 3"))
    frags.append(fb)

    # зона марності — верхній правий кут (I≈1, A≈1)
    ux, uy = px(1, 1)
    frags.append(circle(ux - 5, uy + 5, 7, fill="#eaf0fd", stroke=NEG, sw=2))
    fu, wu, hu = textbox(350, 180,
                         "ЗОНА МАРНОСТІ (I≈1, A≈1)\nабстрактне без клієнтів",
                         size=11, pad=8, fill="#eaf0fd", stroke=NEG, sw=1.4)
    frags.append(line(ux - 11, uy + 9, 350 + wu / 2, 180 - hu / 2, color=NEG, sw=1.2, dash="4 3"))
    frags.append(fu)

    # приклад-пакети на діагоналі: домен (стаб.+абстр.), інфра (нестаб.+конкр.)
    dpx, dpy = px(0.09, 0.86)
    frags.append(circle(dpx, dpy, 6, fill=FIELD, stroke=INK, sw=1))
    frags.append(text(dpx + 30, dpy - 14, "домен", size=12, color=INK, bold=True, anchor="start"))
    ipx, ipy = px(0.90, 0.05)
    frags.append(circle(ipx, ipy, 6, fill=FIELD, stroke=INK, sw=1))
    frags.append(text(ipx + 16, ipy - 6, "інфра", size=12, color=INK, bold=True, anchor="start"))

    render(os.path.join(IMG, 'main-sequence.svg'), W, H, *frags)


# ── Чому D = |A+I−1|: відстань точки до прямої A+I=1 (пряма під 45°) ───────────
def fig_distance_geom():
    W, H = 720, 480
    frags = []
    frags.append(text(W / 2, 30, "Чому D = |A+I−1|: відстань до прямої під 45°",
                      size=16, bold=True))

    # пряма A+I=1 під 45° (екранний нахил +1)
    frags.append(line(170, 140, 450, 420, color=FIELD, sw=2.6))
    frags.append(text(212, 150, "A + I = 1", size=13, color=FIELD, bold=True, anchor="start"))
    frags.append(text(212, 168, "(головна послідовність)", size=10.5, color=FIELD, anchor="start"))

    # точка P нижче прямої (A+I<1), вертикальний розрив і перпендикуляр
    P = (290, 390)
    V = (290, 260)   # на прямій, точно над P
    F = (355, 325)   # основа перпендикуляра з P
    frags.append(line(P[0], P[1], V[0], V[1], color=INK, sw=1.8, dash="5 3"))  # вертикаль
    frags.append(line(P[0], P[1], F[0], F[1], color=POS, sw=2.2))              # перпендикуляр
    frags.append(circle(P[0], P[1], 6, fill=INK, stroke=INK, sw=1))
    frags.append(circle(V[0], V[1], 4, fill=BG, stroke=FIELD, sw=1.6))

    frags.append(text(283, 325, "|A+I−1|", size=12, color=INK, bold=True, anchor="end"))
    frags.append(text(342, 360, "D⊥", size=13, color=POS, bold=True, anchor="start"))
    frags.append(text(255, 250, "45°", size=11, color=MUTED, anchor="end"))
    frags.append(text(290, 408, "P = (I, A)", size=12, color=INK, anchor="middle"))

    # позначка прямого кута при F
    frags.append(line(347, 331, 353, 337, color=POS, sw=1.2))
    frags.append(line(353, 337, 361, 329, color=POS, sw=1.2))

    # підсумок унизу
    frags.append(text(W / 2, 448,
                      "Пряма стоїть під 45°, тому перпендикуляр коротший за вертикальний розрив рівно в √2.",
                      size=12, color=INK))
    frags.append(text(W / 2, 466,
                      "Мартін відкидає √2 і бере нормовану D = |A+I−1| ∈ [0,1].",
                      size=12, color=MUTED))

    render(os.path.join(IMG, 'distance-geom.svg'), W, H, *frags)


if __name__ == "__main__":
    fig_inversion()
    fig_hollywood()
    fig_two_flows()
    fig_ownership()
    fig_hexagon_inward()
    fig_scenario_test()
    fig_main_sequence()
    fig_distance_geom()
    print("figures written to", IMG)
