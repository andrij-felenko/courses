# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
from math import gcd

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── shuffle-collapse: множення на взаємно просте тасує, на не взаємно просте склеює
# Ідея: уся різниця між перестановкою й склейкою — в одному спільному дільнику.
# ×3 (НСД=1): десять стрілок у десять різних клітинок. ×2 (НСД=2): стрілки
# сходяться попарно, п'ять непарних клітинок недосяжні назавжди.
def fig_shuffle_collapse():
    W, H = 980, 500
    p = []
    CW, CH = 46, 25          # клітинка
    Y0, DY = 128, 31         # перший рядок і крок між рядками

    def panel(x_in, x_out, a, col, head, note):
        q = []
        cxm = (x_in + x_out) / 2
        q.append(text(cxm, 68, head, size=15, bold=True))
        q.append(text(x_in, 104, "x", size=12.5, color=MUTED))
        q.append(text(x_out, 104, "%d·x mod 10" % a, size=12.5, color=MUTED))

        hit = set((a * x) % 10 for x in range(10))
        for i in range(10):
            y = Y0 + i * DY
            # ліва колонка — вхід
            q.append(rect(x_in - CW / 2, y - CH / 2, CW, CH, fill=FILL, stroke=LINE, sw=1.2))
            q.append(text(x_in, y + 4.5, i, size=13))
            # права колонка — вихід (недосяжні лишки — сірі та порожні)
            live = i in hit
            q.append(rect(x_out - CW / 2, y - CH / 2, CW, CH,
                          fill="#fbfbfc" if live else BG,
                          stroke=col if live else "#cfd4da", sw=1.4 if live else 1.0))
            q.append(text(x_out, y + 4.5, i, size=13, color=INK if live else "#b6bcc4"))
        # стрілки живуть лише в смузі між колонками — жодного тексту там немає
        for i in range(10):
            y1 = Y0 + i * DY
            y2 = Y0 + ((a * i) % 10) * DY
            q.append(arrow(x_in + CW / 2 + 3, y1, x_out - CW / 2 - 4, y2, color=col, sw=1.3))
        q.append(mtext(cxm, 452, note, size=13, color=MUTED, lh=1.35))
        return q

    p += panel(140, 350, 3, FIELD, "×3 — НСД(3, 10) = 1",
               ["усі десять лишків на місці —", "просто переставлені"])
    p += panel(610, 820, 2, POS, "×2 — НСД(2, 10) = 2",
               ["0 і 5 обидва пішли в 0;", "п'ять непарних — недосяжні"])
    p.append(line(480, 60, 480, 480, color="#dde1e6", sw=1.2, dash="5,5"))
    render(os.path.join(OUT, "shuffle-collapse.svg"), W, H,
           *p, title="Множення за модулем 10: тасує або склеює")


# ── totient-sieve: φ(10) як просіювання, два способи порахувати те саме
# Ідея: не вціліти = ділитися бодай на один простий дільник числа. Десятка
# попадає під обидва ножі, тож віднята двічі — звідси «+1» і звідси ж формула.
def fig_totient_sieve():
    W, H = 960, 440
    p = []
    X0, DX, CW, CH = 260, 66, 56, 30

    rows_y = [92, 146, 194, 244]
    labels = ["число", "ділиться на 2", "ділиться на 5", "вціліло"]
    for y, lab in zip(rows_y, labels):
        p.append(text(220, y + 4.5, lab, size=13, color=MUTED, anchor="end"))

    for i in range(10):
        n = i + 1
        cx = X0 + i * DX
        alive = gcd(n, 10) == 1
        # рядок 1 — саме число
        p.append(rect(cx - CW / 2, rows_y[0] - CH / 2, CW, CH,
                      fill="#eafaf0" if alive else "#fdeeec",
                      stroke=FIELD if alive else POS, sw=1.6))
        p.append(text(cx, rows_y[0] + 5, n, size=15, bold=True,
                      color=FIELD if alive else POS))
        # рядки 2–3 — під який ніж попало
        if n % 2 == 0:
            p.append(text(cx, rows_y[1] + 6, "×", size=19, color=POS, bold=True))
        if n % 5 == 0:
            p.append(text(cx, rows_y[2] + 6, "×", size=19, color=NEG, bold=True))
        # рядок 4 — підсумок
        p.append(text(cx, rows_y[3] + 5, "так" if alive else "ні", size=13,
                      color=FIELD if alive else "#b6bcc4", bold=alive))

    p.append(text(380, 300, "порахувати відніманням", size=13.5, color=MUTED, bold=True))
    b, _, _ = textbox(380, 366, ["10 − 5 − 2 + 1 = 4",
                                 "усі − кратні 2 − кратні 5 + десятка",
                                 "(її відняли двічі: раз за 2, раз за 5)"],
                      size=13, pad=11, fill="#fbfbfc")
    p.append(b)
    p.append(text(750, 300, "порахувати часткою", size=13.5, color=MUTED, bold=True))
    b, _, _ = textbox(750, 366, ["10 · (1 − 1/2) · (1 − 1/5) = 4",
                                 "половина чисел не парна,",
                                 "чотири п'ятих не кратні 5"],
                      size=13, pad=11, fill="#fbfbfc")
    p.append(b)
    render(os.path.join(OUT, "totient-sieve.svg"), W, H,
           *p, title="φ(10): хто вцілів після просіювання")


# ── euler-shuffle-proof: доведення теореми Ейлера на очах
# Ідея: вцілілі не можуть ні втекти з набору, ні склеїтися між собою — отже
# множення лише переставляє їх. Набір той самий → добуток той самий → скорочуємо.
def fig_euler_shuffle_proof():
    W, H = 920, 510
    p = []
    surv = [1, 3, 7, 9]
    ys = [115, 165, 215, 265]

    p.append(text(150, 78, "вціліли за модулем 10", size=13, color=MUTED))
    p.append(text(470, 78, "кожного помножили на 3", size=13, color=MUTED))
    for r, y in zip(surv, ys):
        b, _, _ = textbox(150, y, str(r), size=15, pad=9, min_w=64,
                          fill="#eafaf0", stroke=FIELD, bold=True, color=FIELD)
        p.append(b)
        prod = 3 * r
        s = "3·%d = %d" % (r, prod) if prod < 10 else "3·%d = %d ≡ %d" % (r, prod, prod % 10)
        p.append(fitbox(385, y - 15, 170, 30, s, size=14, fill="#fbfbfc"))
        p.append(arrow(186, y, 381, y, color=FIELD, sw=1.6))

    p.append(text(608, 202, "⇒", size=26, color=MUTED))
    b, _, _ = textbox(762, 195, ["що вийшло: {3, 9, 1, 7}",
                                 "що було:   {1, 3, 7, 9}",
                                 "той самий набір,",
                                 "лише переставлений"],
                      size=13, pad=12, fill="#eafaf0", stroke=FIELD)
    p.append(b)

    p.append(text(460, 340, "перемножмо всі чотири рядки:", size=13.5, color=MUTED, bold=True))
    b, _, _ = textbox(460, 400, ["(3·1)·(3·3)·(3·7)·(3·9)  ≡  1·3·7·9   (mod 10)",
                                 "3⁴ · (1·3·7·9)  ≡  1·3·7·9   (mod 10)",
                                 "3⁴  ≡  1   (mod 10)"],
                      size=14, pad=12, fill="#fbfbfc")
    p.append(b)
    p.append(text(460, 470, "добуток вцілілих взаємно простий з 10 — тож його можна скоротити",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "euler-shuffle-proof.svg"), W, H,
           *p, title="Множення на 3 переставляє вцілілих — і звідси теорема")


# ── rsa-trapdoor: чому саме φ(n) є секретом
# Ідея: розклад n, φ(n) і d — не три секрети, а один у трьох виглядах; маючи
# будь-яке, решту дістають за кілька дій. Відкритий бік не має жодного з них.
def fig_rsa_trapdoor():
    W, H = 960, 520
    p = []

    b, w1, _ = textbox(140, 95, ["m = 7", "(повідомлення)"], size=13, pad=11, fill="#fbfbfc")
    p.append(b)
    b, w2, _ = textbox(480, 95, ["c = 13", "(шифротекст)"], size=13, pad=11,
                       fill="#fdeeec", stroke=POS)
    p.append(b)
    b, w3, _ = textbox(820, 95, ["m = 7", "(розшифровано)"], size=13, pad=11, fill="#fbfbfc")
    p.append(b)

    p.append(arrow(140 + w1 / 2 + 6, 95, 480 - w2 / 2 - 8, 95, color=LINE, sw=1.8))
    p.append(text(313, 72, "c = m³ mod 55", size=13, color=MUTED))
    p.append(arrow(480 + w2 / 2 + 6, 95, 820 - w3 / 2 - 8, 95, color=LINE, sw=1.8))
    p.append(text(650, 72, "m = c²⁷ mod 55", size=13, color=MUTED))

    b, _, _ = textbox(480, 190, ["e·d = 3·27 = 81 = 1 + 2·40 = 1 + 2·φ(n)",
                                 "c^d = m^(1+2·φ(n)) = m · (m^φ(n))² ≡ m · 1² = m"],
                      size=13, pad=11, fill="#fbfbfc")
    p.append(b)

    p.append(fitbox(60, 250, 390, 145,
                    ["ВІДКРИТО — бачать усі", "", "n = 55", "e = 3", "",
                     "цього досить, щоб зашифрувати"],
                    size=14, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(fitbox(510, 250, 390, 145,
                    ["ТАЄМНО — знає лише власник", "", "p = 5,  q = 11",
                     "φ(n) = (p−1)(q−1) = 40", "d = 27,  бо 3·27 ≡ 1 (mod 40)"],
                    size=14, fill="#fdeeec", stroke=POS, sw=2))

    b, _, _ = textbox(480, 445, "розклад n   ⇄   φ(n)   ⇄   d      —  одне дає решту",
                      size=14, pad=11, fill="#fbfbfc", bold=True)
    p.append(b)
    p.append(text(480, 492, "для 2048-бітного n усі три однаково недосяжні",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "rsa-trapdoor.svg"), W, H,
           *p, title="RSA: φ(n) — це і є секрет")


# ── cosets-lagrange: суміжні класи вкладають групу без дірок і без нахлистів
# Ідея (вставка math-euler-proof): та сама група (ℤ/15ℤ)* з восьми вцілілих,
# два різні елементи — два різні розбиття. Розміри блоків різні (4 і 2), але
# блоки ЗАВЖДИ однакові між собою й завжди вкладають вісімку націло. Звідси
# порядок елемента ділить φ(n) — і звідси теорема Ейлера як наслідок Лагранжа.
def fig_cosets_lagrange():
    W, H = 1000, 560
    p = []

    def panel(cx, a, sub, cosets, col, soft, note):
        q = []
        q.append(text(cx, 70, "підгрупа ⟨%d⟩ = {%s} — порядок %d"
                      % (a, ", ".join(str(v) for v in sub), len(sub)),
                      size=14.5, bold=True))
        q.append(text(cx, 95, "%d класи по %d" % (len(cosets), len(sub)),
                      size=13, color=MUTED))

        bw = 40 + len(sub) * 55        # ширина блока під його чипи
        step = 110 if len(sub) == 4 else 76
        bh = 62 if len(sub) == 4 else 56
        for i, (g, members) in enumerate(cosets):
            bt = 140 + i * step
            own = (i == 0)             # перший блок — сама підгрупа, решта — її зсуви
            q.append(rect(cx - bw / 2, bt, bw, bh,
                          fill="#eafaf0" if own else "#fbfbfc",
                          stroke=col, sw=2.0 if own else 1.3))
            q.append(text(cx - bw / 2, bt - 9,
                          "%d·⟨%d⟩%s" % (g, a, "  — сама підгрупа" if own else ""),
                          size=12, color=MUTED, anchor="start"))
            total = len(members) * 46 + (len(members) - 1) * 9
            x0 = cx - total / 2
            for j, v in enumerate(members):
                cxj = x0 + j * 55
                q.append(rect(cxj, bt + (bh - 30) / 2, 46, 30,
                              fill=BG, stroke=col, sw=1.3))
                q.append(text(cxj + 23, bt + (bh - 30) / 2 + 20, v, size=14, bold=True))
        b, _, _ = textbox(cx, 480, note, size=13.5, pad=12, fill="#fbfbfc")
        q.append(b)
        return q

    p += panel(255, 2, [1, 2, 4, 8],
               [(1, [1, 2, 4, 8]), (7, [7, 11, 13, 14])], FIELD, None,
               ["8 = 2 класи · 4 елементи", "порядок 4 ділить 8  →  2⁸ ≡ 1"])
    p += panel(745, 4, [1, 4],
               [(1, [1, 4]), (2, [2, 8]), (7, [7, 13]), (11, [11, 14])], NEG, None,
               ["8 = 4 класи · 2 елементи", "порядок 2 ділить 8  →  4⁸ ≡ 1"])

    p.append(line(500, 62, 500, 512, color="#dde1e6", sw=1.2, dash="5,5"))
    p.append(text(500, 538, "група та сама: (ℤ/15ℤ)* = {1, 2, 4, 7, 8, 11, 13, 14}, "
                            "φ(15) = 8 — змінився лише елемент",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "cosets-lagrange.svg"), W, H,
           *p, title="Суміжні класи вкладають групу націло")


# ── product-expansion: чому знакозмінна сума згортається в добуток
# Ідея (вставка math-euler-proof): у кожній дужці (1 − 1/p) є рівно два вибори.
# Три дужки — вісім шляхів, вісім доданків. Кожен шлях = свій набір простих,
# кожен доданок = свій член включення-виключення. Відповідність точна — тому
# сума з 2^r доданків і добуток з r дужок це те саме число.
def fig_product_expansion():
    W, H = 1000, 600
    p = []
    XS = [100, 260, 440, 620]          # рівні: корінь → (1−1/2) → (1−1/3) → (1−1/5)
    BW, BH = 66, 30

    leaves = [                          # (значення, що це за член)
        (30, "усі числа"), (-6, "кратні 5"), (-10, "кратні 3"), (2, "кратні 15"),
        (-15, "кратні 2"), (3, "кратні 10"), (5, "кратні 6"), (-1, "кратні 30"),
    ]
    ly = [100 + i * 58 for i in range(8)]
    l2y = [(ly[0] + ly[1]) / 2, (ly[2] + ly[3]) / 2, (ly[4] + ly[5]) / 2, (ly[6] + ly[7]) / 2]
    l1y = [(l2y[0] + l2y[1]) / 2, (l2y[2] + l2y[3]) / 2]
    l0y = (l1y[0] + l1y[1]) / 2

    def node(x, y, v, strong=False):
        s = "+%d" % v if v > 0 else str(v)
        return rect(x - BW / 2, y - BH / 2, BW, BH,
                    fill="#eafaf0" if v > 0 else "#fdeeec",
                    stroke=FIELD if v > 0 else POS, sw=2.0 if strong else 1.4) + \
               text(x, y + 5, s, size=14, bold=True, color=FIELD if v > 0 else POS)

    # заголовки рівнів — по одному на стовпець замість підпису на кожному ребрі
    for x, lab in ((180, "з (1 − 1/2)"), (350, "з (1 − 1/3)"), (530, "з (1 − 1/5)")):
        p.append(text(x, 48, lab, size=13, bold=True))
        p.append(text(x, 68, "беремо 1 або −1/p", size=11.5, color=MUTED))

    # ребра: зелене — лишили 1 (просте не бере участі), червоне — взяли −1/p
    def edge(x1, y1, x2, y2, keep):
        return line(x1 + BW / 2, y1, x2 - BW / 2, y2,
                    color=FIELD if keep else POS, sw=1.5)

    p.append(edge(XS[0], l0y, XS[1], l1y[0], True))
    p.append(edge(XS[0], l0y, XS[1], l1y[1], False))
    for i in range(2):
        p.append(edge(XS[1], l1y[i], XS[2], l2y[2 * i], True))
        p.append(edge(XS[1], l1y[i], XS[2], l2y[2 * i + 1], False))
    for i in range(4):
        p.append(edge(XS[2], l2y[i], XS[3], ly[2 * i], True))
        p.append(edge(XS[2], l2y[i], XS[3], ly[2 * i + 1], False))

    p.append(node(XS[0], l0y, 30, strong=True))
    for y, v in zip(l1y, (30, -15)):
        p.append(node(XS[1], y, v))
    for y, v in zip(l2y, (30, -10, -15, 5)):
        p.append(node(XS[2], y, v))
    for y, (v, what) in zip(ly, leaves):
        p.append(node(XS[3], y, v, strong=True))
        p.append(text(XS[3] + BW / 2 + 14, y + 5, what, size=13, color=MUTED, anchor="start"))

    b, _, _ = textbox(500, 560, ["30 − 6 − 10 + 2 − 15 + 3 + 5 − 1 = 8 = φ(30)",
                                 "вісім шляхів дерева — вісім членів включення-виключення"],
                      size=13.5, pad=12, fill="#fbfbfc")
    p.append(b)
    render(os.path.join(OUT, "product-expansion.svg"), W, H,
           *p, title="30 · (1 − 1/2) · (1 − 1/3) · (1 − 1/5): кожна дужка — розвилка")


# ── modexp-ladder: 13²⁷ mod 55 як ланцюг квадратів плюс вибірка за бітами
# Ідея (вставка proj-rsa-toy): ручний рахунок 13²⁷ ≡ 31·36·4·13 і є алгоритм.
# Ліва колонка — ланцюг квадратів 13, 13², 13⁴, 13⁸, 13¹⁶ (кожна ланка — квадрат
# попередньої, одразу зведений за модулем). Біти 27 = 11011₂ кажуть, які ланки
# вкрутити в накопичувач. Жодне число не переростає 55 — у цьому вся суть.
def fig_modexp_ladder():
    W, H = 1020, 600
    p = []
    COL_I, COL_BIT, COL_A, COL_R = 92, 168, 420, 800
    AW, RW = 300, 320

    p.append(text(510, 50, "27 = 11011₂ = 16 + 8 + 2 + 1", size=17, bold=True))
    p.append(text(510, 76, "біти показника кажуть, які ланки ланцюга квадратів перемножити",
                  size=13, color=MUTED))

    p.append(text(COL_I, 126, "i", size=12.5, color=MUTED))
    p.append(text(COL_BIT, 126, "біт", size=12.5, color=MUTED))
    p.append(text(COL_A, 126, "ланцюг квадратів:  a ← a² (mod 55)", size=12.5, color=MUTED))
    p.append(text(COL_R, 126, "біт = 1 → вкрутити:  r ← r·a (mod 55)", size=12.5, color=MUTED))

    b, _, _ = textbox(COL_R, 168, "старт:  r = 1", size=13.5, pad=8, fill="#fbfbfc")
    p.append(b)

    rows = [
        (0, 1, "13¹ = 13",          "r = 1 · 13 = 13"),
        (1, 1, "13² = 169 ≡ 4",     "r = 13 · 4 = 52"),
        (2, 0, "13⁴ ≡ 4² = 16",     None),
        (3, 1, "13⁸ ≡ 16² = 256 ≡ 36", "r = 52 · 36 = 1872 ≡ 2"),
        (4, 1, "13¹⁶ ≡ 36² = 1296 ≡ 31", "r = 2 · 31 = 62 ≡ 7"),
    ]
    Y0, DY = 224, 72
    for i, bit, sa, sr in rows:
        y = Y0 + i * DY
        p.append(text(COL_I, y + 5, str(i), size=13.5, color=MUTED))
        p.append(text(COL_BIT, y + 6, str(bit), size=17, bold=True,
                      color=FIELD if bit else "#b6bcc4"))
        p.append(fitbox(COL_A - AW / 2, y - 17, AW, 34, sa, size=13.5,
                        fill="#fbfbfc", stroke=NEG, sw=1.4))
        if sr:
            p.append(arrow(COL_A + AW / 2 + 8, y, COL_R - RW / 2 - 8, y, color=FIELD, sw=1.5))
            p.append(fitbox(COL_R - RW / 2, y - 17, RW, 34, sr, size=13.5,
                            fill="#eafaf0", stroke=FIELD, sw=1.6))
        else:
            p.append(text(COL_R, y + 5, "— біт 0: пропуск, r лишається 52",
                          size=13, color="#b6bcc4", italic=True))
        if i < 4:                    # стрілка вниз по ланцюгу квадратів
            p.append(arrow(COL_A, y + 17 + 3, COL_A, y + DY - 17 - 3, color=NEG, sw=1.4))

    b, _, _ = textbox(510, 545, ["13²⁷ ≡ 31 · 36 · 4 · 13 ≡ 7 (mod 55)  —  ті самі чотири числа, "
                                 "що й у рахунку на папері",
                                 "5 піднесень до квадрата + 4 множення = 9 дій замість 26"],
                      size=13.5, pad=12, fill="#fbfbfc", bold=True)
    p.append(b)
    render(os.path.join(OUT, "modexp-ladder.svg"), W, H,
           *p, title="13²⁷ mod 55: ланцюг квадратів і біти показника")


# ── keygen-flow: де в генерації ключа живе таємниця
# Ідея (вставка proj-rsa-toy): усе нижче за генератор випадкових бітів —
# чиста детермінована арифметика. Єдиний вхід, якого не знає зловмисник, —
# випадкові біти. Передбач їх — і решта конвеєра сама віддасть d.
def fig_keygen_flow():
    W, H = 1020, 640
    p = []
    LX, RX = 285, 735

    p.append(fitbox(180, 48, 660, 46,
                    "CSPRNG — криптографічний генератор випадкових бітів",
                    size=15, fill="#fdeeec", stroke=POS, sw=2.2))
    p.append(text(510, 112, "ЄДИНЕ джерело таємниці в усій схемі — все нижче лише арифметика",
                  size=13, color=MUTED, italic=True))

    for X in (LX, RX):
        p.append(arrow(X, 94, X, 138, color=LINE, sw=1.6))

    for X, lab in ((LX, "1024 випадкових біти"), (RX, "1024 випадкових біти")):
        p.append(fitbox(X - 140, 138, 280, 38, lab, size=13.5, fill="#fbfbfc"))
        p.append(arrow(X, 176, X, 222, color=LINE, sw=1.6))
        p.append(fitbox(X - 140, 222, 280, 38, "Міллер–Рабін: просте?", size=13.5,
                        fill="#fbfbfc", stroke=NEG, sw=1.6))
        p.append(arrow(X, 260, X, 306, color=FIELD, sw=1.8))
        p.append(text(X + 8, 288, "просте", size=12, color=FIELD, anchor="start"))

    # петля «не просте — тягни нові біти»: назовні, повз усі написи
    for X, side in ((LX, -1), (RX, +1)):
        ox = X + side * 196
        p.append(line(X + side * 140, 241, ox, 241, color=POS, sw=1.4, dash="4,4"))
        p.append(line(ox, 241, ox, 157, color=POS, sw=1.4, dash="4,4"))
        p.append(arrow(ox, 157, X + side * 140, 157, color=POS, sw=1.4))
        # підпис — ПІД петлею: вертикальна пунктирна лінія живе на y 157…241,
        # тож на y≈272 жодна лінія його не перетинає, а до рамки збоку лишається запас
        p.append(mtext(ox, 272, ["складене —", "нові біти"],
                       size=11.5, color=POS, lh=1.25))

    p.append(fitbox(LX - 90, 306, 180, 40, "p", size=17, fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(fitbox(RX - 90, 306, 180, 40, "q", size=17, fill="#eafaf0", stroke=FIELD, sw=2))

    # p і q сходяться на шину — з неї живляться і n, і φ
    p.append(line(LX, 346, LX, 380, color=LINE, sw=1.6))
    p.append(line(RX, 346, RX, 380, color=LINE, sw=1.6))
    p.append(line(LX, 380, RX, 380, color=LINE, sw=1.6))
    p.append(arrow(LX, 380, LX, 420, color=LINE, sw=1.6))
    p.append(arrow(RX, 380, RX, 420, color=LINE, sw=1.6))

    p.append(fitbox(LX - 175, 420, 350, 44, "n = p · q", size=15,
                    fill="#eafaf0", stroke=FIELD, sw=2))
    p.append(fitbox(RX - 175, 420, 350, 44, "φ(n) = (p − 1)(q − 1)", size=15,
                    fill="#fdeeec", stroke=POS, sw=2))

    p.append(arrow(LX, 464, LX, 536, color=LINE, sw=1.6))
    p.append(arrow(RX, 464, RX, 536, color=LINE, sw=1.6))
    p.append(text(RX + 8, 502, "розширений Евклід", size=12, color=MUTED, anchor="start"))

    p.append(fitbox(LX - 175, 536, 350, 46, "ВІДКРИТИЙ КЛЮЧ  (n, e = 65537)",
                    size=14, fill="#eafaf0", stroke=FIELD, sw=2.2))
    p.append(fitbox(RX - 175, 536, 350, 46, "ТАЄМНИЙ КЛЮЧ  d = e⁻¹ mod φ(n)",
                    size=14, fill="#fdeeec", stroke=POS, sw=2.2))

    p.append(text(510, 610, "передбачувані випадкові біти → передбачувані p і q → "
                            "чужий d за секунди", size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "keygen-flow.svg"), W, H,
           *p, title="Генерація ключа: таємниця входить лише зверху")


# ── fermat-filter: третя пропозиція 1640 року як фільтр пошуку дільника
# Ідея: теорема була не прикрасою, а знаряддям. Дільник 2³⁷−1 мусить мати
# вигляд 74j+1 — і безнадійний перебір обертається на прогулянку у два кроки.
def fig_fermat_filter():
    W, H = 980, 570
    p = []
    X0, X1 = 110.0, 900.0        # проміжок 1…300 на спільній осі для обох смуг
    sc = (X1 - X0) / 299.0
    x = lambda v: X0 + (v - 1) * sc

    def isp(v):
        if v < 2: return False
        i = 2
        while i * i <= v:
            if v % i == 0: return False
            i += 1
        return True

    p.append(text(W / 2, 46, "2³⁷ − 1 = 137438953471.  Просте — чи ні?", size=17, bold=True))
    p.append(text(W / 2, 76, "Щоб довести, що ні, треба пред'явити дільник. Усе питання — де його шукати.",
                  size=13, color=MUTED, italic=True))

    # ── смуга А: наосліп — кандидат кожне просте
    p.append(text(X0, 128, "Наосліп: кандидат — кожне просте", size=13.5, bold=True, anchor="start"))
    for v in range(2, 301):
        if isp(v):
            p.append(line(x(v), 148, x(v), 182, color=INK, sw=1.4))
    p.append(line(X0 - 6, 190, X1 + 6, 190, color="#cfd4da", sw=1.0))
    p.append(text(W / 2, 214, "62 штуки не доходячи й до 300 — а йти треба до √(2³⁷−1) = 370727. "
                              "Усього 31 579 ділень.", size=13, color=MUTED))

    # ── смуга Б: третя пропозиція лишає саму лише прогресію 74j+1
    p.append(text(X0, 262, "Третя пропозиція: дільник мусить мати вигляд 74j + 1", size=13.5,
                  bold=True, color=FIELD, anchor="start"))
    for j in range(1, 5):
        v = 74 * j + 1
        live = isp(v)
        p.append(line(x(v), 282, x(v), 316, color=FIELD if live else "#cfd4da",
                      sw=2.6 if live else 1.4))
        p.append(text(x(v), 340, v, size=13, bold=live, color=INK if live else "#b6bcc4"))
    p.append(text(W / 2, 368, "75 і 297 складені — їх Ферма проминув. У цілому проміжку лишилося двоє.",
                  size=13, color=MUTED))

    # ── прогулянка у два кроки
    p.append(fitbox(150, 400, 280, 62, "149 = 74·2 + 1\n2³⁷ mod 149 = 105 — мимо",
                    size=13.5, fill="#fdeeec", stroke=POS, sw=2))
    p.append(arrow(452, 431, 538, 431, color=LINE, sw=1.8))
    p.append(fitbox(560, 400, 280, 62, "223 = 74·3 + 1\n2³⁷ mod 223 = 1 — дільник",
                    size=13.5, fill="#eafaf0", stroke=FIELD, sw=2))

    p.append(text(W / 2, 500, "2³⁷ − 1 = 223 · 616318177", size=16, bold=True))
    p.append(text(W / 2, 532, "Складене — досконалого числа з нього не вийде. "
                              "Другий кандидат зі списку, а не сорок восьме просте поспіль.",
                  size=13, color=MUTED, italic=True))
    render(os.path.join(OUT, "fermat-filter.svg"), W, H,
           *p, title="Теорема Ферма як фільтр пошуку дільника")


# ── euler-three-proofs: інструмент вирішує, доки видно
# Ідея: біном приварений до простого й узагальнити його неможливо; перестановка
# про простоту не питає — тому загальна теорема лежала в доведенні 1755 року
# ще три роки, доки Ейлер не помітив, що p ніде не працює.
def fig_euler_three_proofs():
    W, H = 1020, 545
    p = []
    C1, W1 = 46, 216
    C2, W2 = 292, 372
    C3, W3 = 690, 284
    ROWS = [102, 232, 362]
    RH = 104

    p.append(text(W / 2, 44, "Три доведення Ейлера: інструмент вирішує, доки видно", size=17, bold=True))
    p.append(text(C1 + W1 / 2, 84, "праця", size=12.5, color=MUTED))
    p.append(text(C2 + W2 / 2, 84, "інструмент", size=12.5, color=MUTED))
    p.append(text(C3 + W3 / 2, 84, "доки дістає", size=12.5, color=MUTED))

    rows = [
        ("E54\nчитано 2.VIII.1736\nдрук 1741",
         "індукція за a + біном (a+1)ᵖ\nпросте вбиває середні коефіцієнти",
         "aᵖ ≡ a (mod p)\nтільки просте p",
         POS, "#fdeeec"),
        ("E262\nБерлін 13.II.1755\nдрук 1761",
         "множення на a переставляє лишки\nланцюг степенів мусить замкнутися",
         "порядок ділить p − 1\nповне твердження Ферма",
         FIELD, "#eafaf0"),
        ("E271\nБерлін 8.VI.1758\nдрук 1763",
         "той самий хід, але переставляють\nсамі лише взаємно прості з n",
         "a^φ(n) ≡ 1 (mod n)\nбудь-яке n",
         FIELD, "#eafaf0"),
    ]
    for y, (a, b, c, col, bg) in zip(ROWS, rows):
        p.append(fitbox(C1, y, W1, RH, a, size=13, fill=BG, stroke="#cfd4da", sw=1.4))
        p.append(fitbox(C2, y, W2, RH, b, size=13, fill=bg, stroke=col, sw=2))
        p.append(fitbox(C3, y, W3, RH, c, size=13.5, fill=BG, stroke=col, sw=2, bold=True))
        p.append(arrow(C1 + W1 + 8, y + RH / 2, C2 - 8, y + RH / 2, color=LINE, sw=1.6))
        p.append(arrow(C2 + W2 + 8, y + RH / 2, C3 - 8, y + RH / 2, color=LINE, sw=1.6))
    for y in ROWS[:-1]:
        p.append(line(C1, y + RH + 13, C3 + W3, y + RH + 13, color="#e3e6ea", sw=1.0))

    p.append(text(W / 2, 500, "Червоне не узагальнюється: біном працює рівно тому, що p просте. "
                              "Зелене про простоту не питало ніколи.",
                  size=13.5, color=MUTED, italic=True))
    render(os.path.join(OUT, "euler-three-proofs.svg"), W, H,
           *p, title="Три доведення Ейлера: від бінома до перестановки")


fig_shuffle_collapse()
fig_totient_sieve()
fig_euler_shuffle_proof()
fig_rsa_trapdoor()
fig_cosets_lagrange()
fig_product_expansion()
fig_modexp_ladder()
fig_keygen_flow()
fig_fermat_filter()
fig_euler_three_proofs()
print("ok:", sorted(os.listdir(OUT)))
