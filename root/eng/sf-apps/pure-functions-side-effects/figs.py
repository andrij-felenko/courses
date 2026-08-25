# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Чиста проти нечистої: приховані канали ───────────────────────────────────
def fig_pure_vs_impure():
    W, H = 1040, 560
    frags = []

    # ── ЛІВА половина: ЧИСТА ──
    lcx = 250
    frags.append(text(lcx, 62, "Чиста функція", size=18, bold=True, color=FIELD))

    bw, bh = 190, 110
    bx, by = lcx - bw / 2, 235
    frags.append(rect(bx, by, bw, bh, fill="#f2faf5", stroke=FIELD, sw=2.2, rx=10))
    frags.append(text(lcx, by + bh / 2 + 11, "f", size=34, bold=True, color=FIELD))

    # єдиний вхід згори
    frags.append(text(lcx, 132, "аргументи", size=13, bold=True, color=INK))
    frags.append(arrow(lcx, 146, lcx, by - 6, color=INK, sw=2.4))

    # єдиний вихід знизу
    frags.append(arrow(lcx, by + bh + 6, lcx, by + bh + 60, color=INK, sw=2.4))
    frags.append(text(lcx, by + bh + 82, "значення", size=13, bold=True, color=INK))

    frags.append(text(lcx, H - 30, "один вхід · один вихід · усе видно",
                      size=12, color=FIELD, bold=True))

    # ── роздільник ──
    frags.append(line(W / 2, 46, W / 2, H - 46, color="#d0d5db", sw=1.2, dash="5,5"))

    # ── ПРАВА половина: НЕЧИСТА ──
    rcx = 790
    frags.append(text(rcx, 62, "Нечиста функція", size=18, bold=True, color=POS))

    bx2, by2 = rcx - bw / 2, 235
    frags.append(rect(bx2, by2, bw, bh, fill="#fdecea", stroke=POS, sw=2.2, rx=10))
    frags.append(text(rcx, by2 + bh / 2 + 11, "f", size=34, bold=True, color=POS))

    # оголошений вхід згори
    frags.append(text(rcx, 132, "аргументи", size=13, bold=True, color=INK))
    frags.append(arrow(rcx, 146, rcx, by2 - 6, color=INK, sw=2.4))

    # оголошений вихід знизу
    frags.append(arrow(rcx, by2 + bh + 6, rcx, by2 + bh + 60, color=INK, sw=2.4))
    frags.append(text(rcx, by2 + bh + 82, "значення", size=13, bold=True, color=INK))

    # ПРИХОВАНІ входи зліва — коробки стоять у лівій колонці правої половини
    in_cx = 600
    ins = ["годинник", "глобальний стан", "файл"]
    for i, lab in enumerate(ins):
        yy = by2 + 14 + i * 36
        tb, tw, th = textbox(in_cx, yy, lab, size=11, pad=6,
                             fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
        frags.append(tb)
        frags.append(arrow(in_cx + tw / 2 + 4, yy, bx2 - 4, yy, color=POS, sw=1.8))

    # ПРИХОВАНІ виходи справа — коробки стоять у правій колонці
    out_cx = 965
    outs = ["запис у лог", "мутація входу", "посилка в мережу"]
    for i, lab in enumerate(outs):
        yy = by2 + 14 + i * 36
        tb, tw, th = textbox(out_cx, yy, lab, size=11, pad=6,
                             fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
        # спершу знаємо ширину — стрілка до лівого краю коробки
        frags.append(arrow(bx2 + bw + 4, yy, out_cx - tw / 2 - 4, yy, color=POS, sw=1.8))
        frags.append(tb)

    frags.append(text(rcx, H - 30, "приховані канали з боків — у сигнатурі їх не видно",
                      size=12, color=POS, bold=True))

    render(os.path.join(IMG, 'pure-vs-impure.svg'), W, H, *frags,
           title="Що видно в сигнатурі, а що сховано збоку")


# ── Ефекти на край: чисте ядро в брудній оболонці ────────────────────────────
def fig_core_shell():
    W, H = 860, 620
    frags = []

    cx, cy = W / 2, 330

    # зовнішнє кільце — оболонка (брудна)
    frags.append(circle(cx, cy, 210, fill="#fdecea", stroke=POS, sw=2.0))
    # внутрішнє коло — ядро (чисте)
    frags.append(circle(cx, cy, 110, fill="#f2faf5", stroke=FIELD, sw=2.4))

    # підписи кілець (обидва в порожніх місцях)
    frags.append(text(cx, cy - 60, "ЧИСТЕ ЯДРО", size=15, bold=True, color=FIELD))
    frags.append(text(cx, cy - 40, "уся логіка й рішення", size=11, color=MUTED))
    frags.append(text(cx, cy + 40, "той самий вхід", size=11, color=FIELD))
    frags.append(text(cx, cy + 56, "→ той самий вихід", size=11, color=FIELD))

    frags.append(text(cx, cy - 178, "ІМПЕРАТИВНА ОБОЛОНКА (тонка)",
                      size=14, bold=True, color=POS))

    # ефекти — стрілки крізь оболонку до/від ядра, підписи ЗА межами великого кола
    # приносять дані (зліва, всередину)
    frags.append(arrow(cx - 300, cy - 40, cx - 116, cy - 24, color=POS, sw=2.0))
    tb, tw, th = textbox(cx - 300, cy - 66, "читання з БД", size=11, pad=6,
                         fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
    frags.append(tb)
    frags.append(arrow(cx - 300, cy + 40, cx - 116, cy + 24, color=POS, sw=2.0))
    tb, tw, th = textbox(cx - 300, cy + 66, "читання конфіга", size=11, pad=6,
                         fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
    frags.append(tb)

    # виносять ефекти (справа, назовні)
    frags.append(arrow(cx + 116, cy - 24, cx + 300, cy - 40, color=POS, sw=2.0))
    tb, tw, th = textbox(cx + 300, cy - 66, "запис у БД", size=11, pad=6,
                         fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
    frags.append(tb)
    frags.append(arrow(cx + 116, cy + 24, cx + 300, cy + 40, color=POS, sw=2.0))
    tb, tw, th = textbox(cx + 300, cy + 66, "вивід у лог", size=11, pad=6,
                         fill="#fff4f2", stroke=POS, sw=1.4, color=POS)
    frags.append(tb)

    # нижній підпис-висновок
    cap, cw, ch = textbox(cx, H - 40,
                          "Бруд приносить дані в ядро й виносить його рішення — "
                          "рішень у ньому нема",
                          size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'core-shell.svg'), W, H, *frags,
           title="Ефекти — на край: чисте всередині, брудне зовні")


# ── Справжня сигнатура: світ як прихований другий аргумент/результат ──────────
def fig_true_signature():
    W, H = 900, 600
    frags = []

    # ── ВЕРХ: оголошена (чиста) ──
    frags.append(text(450, 40, "Оголошена сигнатура — те, що бачить читач",
                      size=15, color=FIELD, bold=True))

    frags.append(rect(375, 88, 150, 80, fill="#f2faf5", stroke=FIELD, sw=2.2, rx=10))
    frags.append(text(450, 142, "f", size=34, bold=True, color=FIELD))

    frags.append(arrow(250, 128, 371, 128, color=INK, sw=2.4))
    frags.append(text(305, 113, "аргументи", size=13, bold=True, color=INK))
    frags.append(arrow(529, 128, 650, 128, color=INK, sw=2.4))
    frags.append(text(597, 113, "значення", size=13, bold=True, color=INK))

    frags.append(text(450, 205, "world не бере участі → залежить лише від аргументів",
                      size=12, color=FIELD))

    # роздільник
    frags.append(line(80, 240, 820, 240, color=MUTED, sw=1.0, dash="6,6"))

    # ── НИЗ: справжня (нечиста) ──
    frags.append(text(450, 278, "Справжня сигнатура нечистої — те, що є насправді",
                      size=15, color=POS, bold=True))

    frags.append(rect(375, 320, 150, 110, fill="#fdecea", stroke=POS, sw=2.2, rx=10))
    frags.append(text(450, 388, "f", size=34, bold=True, color=POS))

    # оголошені (чорні) стрілки
    frags.append(arrow(250, 352, 371, 352, color=INK, sw=2.2))
    frags.append(text(305, 338, "аргументи", size=12, bold=True, color=INK))
    frags.append(arrow(529, 352, 650, 352, color=INK, sw=2.2))
    frags.append(text(597, 338, "значення", size=12, bold=True, color=INK))

    # приховані (червоні) стрілки — світ
    frags.append(arrow(250, 400, 371, 400, color=POS, sw=2.2))
    frags.append(text(300, 386, "світ до", size=12, bold=True, color=POS))
    frags.append(arrow(529, 400, 650, 400, color=POS, sw=2.2))
    frags.append(text(600, 386, "світ після", size=12, bold=True, color=POS))

    cap, cw, ch = textbox(450, 500,
                          "світ до — усе, що f таємно ЧИТАЄ: годинник, глобалі, файли.\n"
                          "світ після — усе, що вона таємно ЗМІНИЛА: лог, мутації, БД.",
                          size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'true-signature.svg'), W, H, *frags,
           title="Нечиста функція — це чиста функція від (аргументи, світ)")


# ── Чистота як шкала: три зони за спостережністю ефекту ───────────────────────
def fig_purity_spectrum():
    W, H = 1120, 400
    frags = []

    AMBER_T, AMBER_F, AMBER_S = "#b9812f", "#fef8ec", "#d9a441"

    # смуги
    frags.append(rect(60, 92, 370, 208, fill="#f2faf5", stroke=FIELD, sw=1.6, rx=10))
    frags.append(rect(430, 92, 210, 208, fill=AMBER_F, stroke=AMBER_S, sw=1.6, rx=10))
    frags.append(rect(640, 92, 420, 208, fill="#fdecea", stroke=POS, sw=1.6, rx=10))

    # заголовки смуг
    frags.append(text(245, 118, "прозора за посиланням", size=14, bold=True, color=FIELD))
    frags.append(text(535, 118, "нешкідливий бруд", size=14, bold=True, color=AMBER_T))
    frags.append(text(850, 118, "отруйні ефекти", size=14, bold=True, color=POS))

    def chip(cx, s, stroke):
        tb, tw, th = textbox(cx, 190, s, size=11, pad=6, fill=BG, stroke=stroke,
                             sw=1.4, color=INK)
        return tb

    frags.append(chip(128, "sin(x)", FIELD))
    frags.append(chip(245, "локальна\nмутація", FIELD))
    frags.append(chip(368, "нешкідливий\nкеш (memo)", FIELD))
    frags.append(chip(492, "лог для\nдебагу", AMBER_S))
    frags.append(chip(592, "assert", AMBER_S))
    frags.append(chip(722, "читає час,\nRNG", POS))
    frags.append(chip(852, "мутує вхід,\nглобаль", POS))
    frags.append(chip(985, "запис у БД,\nмережа, екран", POS))

    # підписи-висновки під зонами
    frags.append(text(245, 264, "виклик можна замінити значенням", size=11, color=MUTED))
    frags.append(text(535, 264, "результату не міняє", size=11, color=MUTED))
    frags.append(text(850, 264, "спільний світ залежить від нього", size=11, color=MUTED))

    cap, cw, ch = textbox(560, 352,
                          "Тримай ядро логіки якнайлівіше; неминучі ефекти збери "
                          "праворуч — тонким шаром на межі зі світом.",
                          size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'purity-spectrum.svg'), W, H, *frags,
           title="Чистота — це шкала, а не прапорець")


# ── Підстановка значенням відмикає оптимізації ───────────────────────────────
def fig_substitution_license():
    W, H = 1020, 500
    frags = []

    # рівність f(a) ⇄ значення
    frags.append(rect(310, 81, 120, 58, fill="#f2faf5", stroke=FIELD, sw=2, rx=8))
    frags.append(text(370, 120, "f(a)", size=22, bold=True, color=FIELD))
    frags.append(rect(570, 81, 160, 58, fill="#eef4ff", stroke=INK, sw=2, rx=8))
    frags.append(text(650, 118, "значення v", size=17, bold=True, color=INK))

    frags.append(text(500, 66, "замінити на значення", size=12, color=MUTED))
    frags.append(text(500, 124, "⇄", size=34, bold=True, color=INK))
    frags.append(text(500, 158, "лише якщо f чиста", size=13, bold=True, color=FIELD))

    # вниз до віяла свобод
    frags.append(arrow(500, 176, 500, 210, color=INK, sw=2))
    frags.append(text(500, 232, "тоді вільно:", size=14, bold=True, color=INK))

    chips = [
        (118, "memo / кеш:\nпорахувати раз"),
        (308, "CSE:\nспільне — раз"),
        (500, "hoisting:\nвинести з циклу"),
        (700, "лінивість, DCE:\nне рахувати зайве"),
        (895, "паралельно:\nбудь-який порядок"),
    ]
    for cx, s in chips:
        frags.append(arrow(500, 244, cx, 293, color=MUTED, sw=1.4))
    for cx, s in chips:
        tb, tw, th = textbox(cx, 320, s, size=12, pad=8, fill=BG, stroke=FIELD,
                             sw=1.5, color=INK)
        frags.append(tb)

    frags.append(text(510, 384,
                      "порядок обчислення не змінює результату — "
                      "це конфлюентність (Черч — Россер, 1936)",
                      size=12, color=MUTED, italic=True))

    cap, cw, ch = textbox(510, 444,
                          "Уся ця свобода — з одного дозволу: виклик чистої функції "
                          "дорівнює своєму значенню.",
                          size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'substitution-license.svg'), W, H, *frags,
           title="Прозорість за посиланням відмикає оптимізації")


# ── Конфлюентність: діамант Черча — Россера ──────────────────────────────────
def fig_confluence_diamond():
    W, H = 980, 560
    frags = []

    T = (490, 96)
    A = (222, 262)
    B = (758, 262)
    C = (490, 430)

    def node(cx, cy, s, size=17):
        return textbox(cx, cy, s, size=size, pad=12, fill="#f2faf5", stroke=FIELD,
                       sw=2.0, color=INK, bold=True)

    tT, wT, hT = node(*T, "(λx. x+x) (2+3)")
    tA, wA, hA = node(*A, "(λx. x+x) 5")
    tB, wB, hB = node(*B, "(2+3) + (2+3)")
    tC, wC, hC = node(*C, "10", size=22)

    # стрілки згори вниз (від краю коробки до краю наступної)
    frags.append(arrow(T[0] - 46, T[1] + hT / 2, A[0] + wA / 2 - 12, A[1] - hA / 2, color=INK, sw=2.2))
    frags.append(arrow(T[0] + 46, T[1] + hT / 2, B[0] - wB / 2 + 12, B[1] - hB / 2, color=INK, sw=2.2))
    frags.append(arrow(A[0] + wA / 2 - 12, A[1] + hA / 2, C[0] - 46, C[1] - hC / 2, color=INK, sw=2.2))
    frags.append(arrow(B[0] - wB / 2 + 12, B[1] + hB / 2, C[0] + 46, C[1] - hC / 2, color=INK, sw=2.2))

    frags += [tT, tA, tB, tC]

    # підписи стратегій — у порожніх зовнішніх зонах, не на лініях
    frags.append(text(300, 150, "зведи спершу аргумент", size=12, color=MUTED))
    frags.append(text(688, 150, "зведи спершу λ", size=12, color=MUTED))
    frags.append(text(206, 362, "далі β, тоді +", size=12, color=MUTED))
    frags.append(text(772, 362, "далі два +", size=12, color=MUTED))

    cap, cw, ch = textbox(490, 512,
                          "Хоч би яким шляхом зводив вираз — приходиш у той самий "
                          "результат. Це конфлюентність (Черч — Россер, 1936).",
                          size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'confluence-diamond.svg'), W, H, *frags,
           title="Порядок зведення не змінює значення чистого виразу")


# ── Контекстуальна рівність: те саме оточення → той самий результат ───────────
def fig_contextual_equivalence():
    W, H = 1000, 520
    frags = []

    frags.append(text(500, 60, "Підстав e₁ або e₂ в ТЕ САМЕ оточення C — і дивись на результат",
                      size=14, bold=True, color=INK))

    yA, yB = 150, 300

    e1, w1, h1 = textbox(150, yA, "вираз e₁", size=15, pad=12, fill="#f2faf5",
                         stroke=FIELD, sw=2.0, bold=True)
    cA, wcA, hcA = textbox(470, yA, "C[ e₁ ]", size=16, pad=14, fill="#eef4ff",
                           stroke=INK, sw=1.8, bold=True)
    rA, wrA, hrA = textbox(790, yA, "результат r", size=15, pad=12, fill=BG,
                           stroke=MUTED, sw=1.6)

    e2, w2, h2 = textbox(150, yB, "вираз e₂", size=15, pad=12, fill="#f2faf5",
                         stroke=FIELD, sw=2.0, bold=True)
    cB, wcB, hcB = textbox(470, yB, "C[ e₂ ]", size=16, pad=14, fill="#eef4ff",
                           stroke=INK, sw=1.8, bold=True)
    rB, wrB, hrB = textbox(790, yB, "результат r", size=15, pad=12, fill=BG,
                           stroke=MUTED, sw=1.6)

    frags.append(arrow(150 + w1 / 2, yA, 470 - wcA / 2, yA, color=INK, sw=2.0))
    frags.append(arrow(470 + wcA / 2, yA, 790 - wrA / 2, yA, color=INK, sw=2.0))
    frags.append(arrow(150 + w2 / 2, yB, 470 - wcB / 2, yB, color=INK, sw=2.0))
    frags.append(arrow(470 + wcB / 2, yB, 790 - wrB / 2, yB, color=INK, sw=2.0))

    frags += [e1, cA, rA, e2, cB, rB]

    # той самий контекст: вертикальна пунктирна прив'язка між C-коробками
    frags.append(line(470, yA + hcA / 2 + 6, 470, yB - hcB / 2 - 6, color=MUTED, sw=1.2, dash="5,5"))
    frags.append(text(548, 232, "той самий C", size=11, color=MUTED))

    # той самий результат: вертикальна прив'язка між r-коробками
    frags.append(line(790, yA + hrA / 2 + 6, 790, yB - hrB / 2 - 6, color=FIELD, sw=1.4, dash="5,5"))
    frags.append(text(884, 232, "той самий r", size=11, color=FIELD, bold=True))

    cap, cw, ch = textbox(500, 452,
                          "Контекстуальна (спостережна) рівність e₁ ≅ e₂: у КОЖНОМУ оточенні C "
                          "обидва дають той самий результат — жоден навколишній код їх не розрізнить.",
                          size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'contextual-equivalence.svg'), W, H, *frags,
           title="Взаємозамінні тоді й лише тоді, коли жоден контекст не розрізнить")


# ── Ефект як дані: ядро → план → крихітний виконавець на краю ─────────────────
def fig_plan_as_data():
    W, H = 1180, 520
    frags = []

    # 1) впорснуті входи
    frags.append(text(105, 165, "явні входи", size=13, bold=True, color=FIELD))
    inbox, iw, ih = textbox(105, 250, "дані\nчас\nкидок\nконфіг",
                            size=13, pad=10, fill="#f2faf5", stroke=FIELD, color=INK)
    frags.append(inbox)
    frags.append(arrow(105 + iw / 2 + 4, 250, 296, 250, color=FIELD, sw=2.2))

    # 2) чисте ядро
    frags.append(rect(300, 175, 210, 150, fill="#f2faf5", stroke=FIELD, sw=2.4, rx=10))
    frags.append(text(405, 242, "чисте ядро", size=15, bold=True, color=FIELD))
    frags.append(text(405, 268, "decide(…)", size=13, color=INK))
    frags.append(text(405, 292, "повертає план", size=11, color=MUTED))
    frags.append(arrow(514, 250, 623, 250, color=INK, sw=2.2))

    # 3) план ефектів як дані — стос карток
    frags.append(text(680, 150, "план ефектів (дані)", size=13, bold=True, color=NEG))
    for lab, yy in (("saveUser", 200), ("appendLedger", 250), ("notify", 300)):
        cb, cw, ch = textbox(680, yy, lab, size=12, pad=10,
                             fill="#eef4ff", stroke=NEG, color=INK)
        frags.append(cb)

    # 4) межа зі світом
    frags.append(text(800, 108, "межа зі світом", size=12, bold=True, color=POS))
    frags.append(line(800, 122, 800, 400, color=POS, sw=1.4, dash="6,6"))
    frags.append(arrow(735, 250, 831, 250, color=INK, sw=2.2))

    # 5) виконавець (нейтральний — лише крутить список)
    frags.append(rect(835, 205, 180, 92, fill=FILL, stroke=INK, sw=2.0, rx=10))
    frags.append(text(925, 238, "виконавець", size=13, bold=True, color=INK))
    frags.append(text(925, 262, "for e in план:", size=11, color=INK))
    frags.append(text(925, 283, "run(e)", size=11, color=INK))

    # 6) світ
    frags.append(text(1090, 150, "світ", size=13, bold=True, color=POS))
    wb1, w1, h1 = textbox(1090, 210, "БД", size=12, pad=10,
                          fill="#fdecea", stroke=POS, color=POS)
    wb2, w2, h2 = textbox(1090, 300, "пошта", size=12, pad=10,
                          fill="#fdecea", stroke=POS, color=POS)
    frags.append(arrow(1018, 235, 1090 - w1 / 2 - 4, 214, color=POS, sw=2.0))
    frags.append(arrow(1018, 268, 1090 - w2 / 2 - 4, 296, color=POS, sw=2.0))
    frags.append(wb1)
    frags.append(wb2)

    cap, cw, ch = textbox(590, 482,
                          "Ядро повертає ПЛАН ефектів як дані; світу торкається "
                          "лише крихітний виконавець на самому краю",
                          size=12, pad=10, fill="#eef4ff", stroke=INK, sw=1.4)
    frags.append(cap)

    render(os.path.join(IMG, 'plan-as-data.svg'), W, H, *frags,
           title="Ефект як значення: ядро планує, виконавець на краю робить")


# ── Значення проти плану: чим це відрізняється від extract-pure-core ──────────
def fig_value_vs_plan():
    W, H = 1100, 540
    frags = []

    # ── ВЕРХ: розрізати обчислення й ефекти (extract-pure-core) ──
    frags.append(text(550, 58, "Розрізати обчислення й ефекти  (extract-pure-core)",
                      size=15, bold=True, color=INK))

    frags.append(rect(90, 95, 190, 95, fill="#f2faf5", stroke=FIELD, sw=2.2, rx=10))
    frags.append(text(185, 135, "чисте ядро", size=14, bold=True, color=FIELD))
    frags.append(text(185, 160, "→ значення", size=12, color=INK))
    frags.append(arrow(285, 142, 375, 142, color=INK, sw=2.2))

    frags.append(rect(380, 95, 300, 110, fill="#fdecea", stroke=POS, sw=2.2, rx=10))
    frags.append(text(530, 122, "тонка оболонка", size=13, bold=True, color=POS))
    frags.append(text(530, 147, "db.save(id, total)", size=12, color=INK))
    frags.append(text(530, 169, "notify(mail, …)", size=12, color=INK))
    frags.append(text(530, 192, "вписані вручну", size=10, color=MUTED))

    ann1, aw1, ah1 = textbox(530, 238,
                             "які ефекти — вирішує ОБОЛОНКА (імперативно, у коді)",
                             size=12, pad=8, fill="#fdecea", stroke=POS, color=POS)
    frags.append(ann1)

    # ── місток ──
    note, nw, nh = textbox(550, 280,
                           "⇩  рішення «які ефекти» переносимо в ЯДРО — як дані  ⇩",
                           size=12, pad=10, bold=True, fill="#eef4ff", stroke=INK)
    frags.append(note)

    # ── НИЗ: ефекти як значення (effects-as-values) ──
    frags.append(text(550, 332, "Ефекти як значення  (effects-as-values)",
                      size=15, bold=True, color=INK))

    frags.append(rect(90, 362, 190, 95, fill="#f2faf5", stroke=FIELD, sw=2.2, rx=10))
    frags.append(text(185, 402, "чисте ядро", size=14, bold=True, color=FIELD))
    frags.append(text(185, 427, "→ Effect[]", size=12, color=INK))
    frags.append(arrow(285, 409, 360, 409, color=INK, sw=2.2))

    frags.append(rect(365, 370, 190, 80, fill="#eef4ff", stroke=NEG, sw=2.0, rx=10))
    frags.append(text(460, 402, "план (дані)", size=12, bold=True, color=NEG))
    frags.append(text(460, 428, "[ save·ledger·notify ]", size=11, color=INK))
    frags.append(arrow(560, 409, 650, 409, color=INK, sw=2.2))

    frags.append(rect(655, 362, 250, 95, fill=FILL, stroke=INK, sw=2.0, rx=10))
    frags.append(text(780, 400, "виконавець", size=13, bold=True, color=INK))
    frags.append(text(780, 424, "for e in план: run(e)", size=11, color=INK))
    frags.append(text(780, 445, "generic · написаний раз", size=10, color=MUTED))

    ann2, aw2, ah2 = textbox(500, 498,
                             "які ефекти — вирішує ЯДРО (як дані); виконавець лише крутить список",
                             size=12, pad=8, fill="#eef4ff", stroke=NEG, color=NEG)
    frags.append(ann2)

    render(os.path.join(IMG, 'value-vs-plan.svg'), W, H, *frags,
           title="Повернути значення — чи повернути сам план ефектів")


# ── Пастка: ефект, що читає результат попереднього ────────────────────────────
def fig_dependent_effects():
    W, H = 1080, 500
    frags = []

    # ── ВЕРХ: незалежні → плаский список годиться ──
    frags.append(text(540, 58, "Незалежні ефекти — плаский список Effect[] годиться",
                      size=14, bold=True, color=FIELD))
    for lab, cx in (("saveUser", 250), ("appendLedger", 500), ("notify", 750)):
        cb, cw, ch = textbox(cx, 130, lab, size=12, pad=10,
                             fill="#eef4ff", stroke=NEG, color=INK)
        frags.append(cb)
    note1, n1w, n1h = textbox(540, 195,
                              "жоден не читає результату іншого → виконуй у будь-якому порядку",
                              size=12, pad=8, fill=BG, stroke=FIELD, color=INK)
    frags.append(note1)

    # ── НИЗ: залежні → списку замало ──
    frags.append(text(540, 275, "Ефект B читає РЕЗУЛЬТАТ ефекту A — списку замало",
                      size=14, bold=True, color=POS))

    ca, caw, cah = textbox(240, 340, "insert(row)\n→ новий id", size=12, pad=10,
                           fill="#fdecea", stroke=POS, color=INK)
    frags.append(ca)
    frags.append(text(392, 322, "id є лише ПІСЛЯ виконання", size=11, color=MUTED))
    frags.append(arrow(240 + caw / 2 + 4, 340, 496, 340, color=INK, sw=2.0))
    cbx, cbw, cbh = textbox(560, 340, "notify(user, id)\n← потребує id", size=12, pad=10,
                            fill="#fdecea", stroke=POS, color=INK)
    frags.append(cbx)

    note2, n2w, n2h = textbox(540, 440,
                              "потрібен ЛАНЦЮГ: наступний крок = функція(результат) — "
                              "це форма монади IO (bind)",
                              size=12, pad=10, fill="#eef4ff", stroke=INK)
    frags.append(note2)

    render(os.path.join(IMG, 'dependent-effects.svg'), W, H, *frags,
           title="Де плаский план ефектів перестає давати раду")


if __name__ == "__main__":
    fig_pure_vs_impure()
    fig_core_shell()
    fig_true_signature()
    fig_purity_spectrum()
    fig_substitution_license()
    fig_confluence_diamond()
    fig_contextual_equivalence()
    fig_plan_as_data()
    fig_value_vs_plan()
    fig_dependent_effects()
    print("figures written to", IMG)
