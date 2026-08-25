# -*- coding: utf-8 -*-
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: квадратні корені з одиниці — просте проти складеного ───────────────
# Ідея: серце тесту. За простим модулем одиниця має рівно два корені (±1); за
# складеним з'являються зайві, «нетривіальні», і сама їхня поява викриває
# складеність. Показуємо це на числовій прямій остач для 13 і 15.
def fig_square_roots():
    W, H = 960, 400
    p = []

    def panel(px, pw, m, roots, nontrivial, prime):
        # заголовок панелі
        head = "модуль %d — просте" % m if prime else "модуль %d — складене" % m
        hcol = FIELD if prime else POS
        p.append(text(px + pw / 2, 66, head, size=15, color=hcol, bold=True))
        # числова пряма остач 0..m-1
        ax0, ax1, ay = px + 40, px + pw - 40, 250.0
        p.append(line(ax0, ay, ax1, ay, color=INK, sw=1.6))
        sp = (ax1 - ax0) / (m - 1)

        def X(i):
            return ax0 + i * sp

        for i in range(m):
            p.append(line(X(i), ay - 5, X(i), ay + 5, color=INK, sw=1.1))
            p.append(text(X(i), ay + 22, str(i), size=11, color=MUTED))
        # позначаємо корені з одиниці
        for k in roots:
            nt = k in nontrivial
            col = POS if nt else FIELD
            p.append(circle(X(k), ay, 8.5, fill=col, stroke=BG, sw=2.0))
            # виноска над коренем
            lab = str(k)
            if k == m - 1:
                lab = "%d ≡ −1" % k
            note = "нетривіальний" if nt else "тривіальний"
            b, bw, bh = textbox(X(k), 150.0, lab + "\n" + note, size=11.5, bold=True,
                                fill="#fff", stroke=col, sw=1.7, min_w=96)
            p.append(b)
            p.append(line(X(k), 150.0 + bh / 2, X(k), ay - 9, color=col, sw=1.4, dash="4 3"))
        # підсумок під прямою
        summ = "лише 2 корені: 1 і −1" if prime else "4 корені — зайві %s" % (", ".join(map(str, sorted(nontrivial))))
        p.append(text(px + pw / 2, 320, summ, size=13, color=hcol, bold=True))
        p.append(text(px + pw / 2, 344, "x² ≡ 1 (mod %d)" % m, size=12, color=MUTED))

    panel(20, 460, 13, [1, 12], set(), True)
    # розділова риска
    p.append(line(480, 60, 480, 350, color="#dfe4ea", sw=1.4, dash="6 5"))
    panel(500, 440, 15, [1, 4, 11, 14], {4, 11}, False)

    render(os.path.join(OUT, "square-roots-of-1.svg"), W, H, *p,
           title="Квадратні корені з одиниці: у простого їх лише два")


# ── Фіг. 2: драбина квадратів — де народжується одиниця ───────────────────────
# Ідея: тест дивиться не на кінець ланцюжка a^d→a^2d→…→a^(n−1)=1, а на те, ЯК
# з'являється одиниця. Просте (41) неодмінно проходить через −1; складене (561)
# стрибає в одиницю просто з нетривіального кореня 67 — і цей стрибок його видає.
def fig_squaring_ladder():
    W, H = 980, 470
    p = []
    p.append(text(W / 2, 58, "кожен щабель — квадрат попереднього;  фініш  a^(n−1) = 1",
                  size=13, color=MUTED))

    bw, bh = 78.0, 42.0
    step = 128.0
    x0 = 250.0

    def cx(i):
        return x0 + i * step

    def row(ry, label_lines, lcol, cells):
        # ліва мітка-рамка
        b, lw, lh = textbox(140.0, ry, label_lines, size=12.5, bold=True,
                            fill="#fbfdff", stroke=lcol, sw=1.7, min_w=170)
        p.append(b)
        # клітинки-значення й стрілки між ними
        for i, (val, mark) in enumerate(cells):
            x = cx(i)
            fill, stroke = BG, "#c2cad4"
            if mark == "minus":
                fill, stroke = "#eaf7ef", FIELD
            elif mark == "root":
                fill, stroke = "#fdecea", POS
            elif mark == "faint":
                fill, stroke = "#f7f8fa", "#dfe4ea"
            tcol = MUTED if mark == "faint" else INK
            p.append(rect(x - bw / 2, ry - bh / 2, bw, bh, fill=fill, stroke=stroke,
                          sw=2.0 if mark in ("minus", "root") else 1.4, rx=7))
            p.append(text(x, ry + 5, val, size=14.5, color=tcol, bold=(mark != "faint")))
            if i > 0:
                acol = POS if (mark == "one_from_root") else "#8a94a0"
                ax1 = x - bw / 2 - 6
                ax0 = cx(i - 1) + bw / 2 + 6
                p.append(arrow(ax0, ry, ax1, ry, color=acol, sw=2.0))
                p.append(text((ax0 + ax1) / 2, ry - 14, "( )²", size=12,
                              color=acol, bold=(mark == "one_from_root")))

    # рядок 1: просте 41, основа 3 — проходить через −1
    row(160.0, "Просте\nn = 41,  a = 3", FIELD,
        [("38", None), ("9", None), ("40 ≡ −1", "minus"), ("1", "faint")])
    p.append(text(cx(2), 160.0 + bh / 2 + 26, "−1 з'явилось → пройшло",
                  size=12.5, color=FIELD, bold=True))

    # рядок 2: складене 561, основа 2 — стрибок у 1 з кореня 67
    row(320.0, "Складене\nn = 561,  a = 2", POS,
        [("263", None), ("166", None), ("67", "root"), ("1", "one_from_root")])
    p.append(text(cx(2), 320.0 - bh / 2 - 14, "нетривіальний корінь", size=11.5,
                  color=POS, bold=True))
    p.append(text((cx(2) + cx(3)) / 2, 320.0 + bh / 2 + 26,
                  "стрибок у 1 повз −1  →  свідок складеності",
                  size=12.5, color=POS, bold=True))

    render(os.path.join(OUT, "squaring-ladder.svg"), W, H, *p,
           title="Драбина квадратів: у простого шлях до 1 лягає через −1")


# ── Фіг. 3: частка брехунів — Ферма проти Міллера–Рабіна ──────────────────────
# Ідея: головна перевага. Число Кармайкла обманює тест Ферма на КОЖНІЙ основі
# (весь круг — брехуни). Тест Міллера–Рабіна будь-яке складене викриває
# щонайменше ¾ основ — універсального «хамелеона» для нього не існує.
def fig_liar_proportions():
    W, H = 920, 430
    p = []

    def wedge(cx, cy, r, a0, a1, fill, stroke):
        # кут від верху за годинниковою; a0<a1 у градусах
        def pt(a):
            t = math.radians(a)
            return (cx + r * math.sin(t), cy - r * math.cos(t))
        x0, y0 = pt(a0)
        x1, y1 = pt(a1)
        large = 1 if (a1 - a0) > 180 else 0
        return ('<path d="M %.1f %.1f L %.1f %.1f A %.1f %.1f 0 %d 1 %.1f %.1f Z" '
                'fill="%s" stroke="%s" stroke-width="1.8"/>'
                % (cx, cy, x0, y0, r, r, large, x1, y1, fill, stroke))

    r = 118.0
    # ── ліворуч: Ферма на числі Кармайкла ──
    lx, ly = 236.0, 236.0
    p.append(mtext(lx, 74, ["Тест Ферма", "на числі Кармайкла (561)"], size=14.5, bold=True))
    p.append(circle(lx, ly, r, fill="#fdecea", stroke=POS, sw=2.2))
    b, bw, bh = textbox(lx, ly, "усі основи\nбрешуть", size=15, bold=True,
                        fill="#fff", stroke=POS, sw=1.8, color=POS)
    p.append(b)
    p.append(text(lx, 388, "тест сліпий: свідків практично немає", size=12.5, color=MUTED))

    # ── праворуч: Міллер–Рабін на будь-якому складеному ──
    rx, ry = 684.0, 236.0
    p.append(mtext(rx, 74, ["Тест Міллера–Рабіна", "на будь-якому складеному"], size=14.5, bold=True))
    # ¾ свідки (зелений) від 0° до 270°, ¼ брехуни (червоний) від 270° до 360°
    p.append(wedge(rx, ry, r, 0, 270, "#eaf7ef", FIELD))
    p.append(wedge(rx, ry, r, 270, 360, "#fdecea", POS))
    # мітка свідків усередині зеленого сектора
    b2, bw2, bh2 = textbox(rx - 18, ry + 24, "≥ ¾\nсвідки", size=14, bold=True,
                           fill="#fff", stroke=FIELD, sw=1.8, color=FIELD)
    p.append(b2)
    # мітка брехунів — назовні від малого червоного сектора, з виноскою
    t = math.radians(315)
    ex, ey = rx + r * math.sin(t), ry - r * math.cos(t)
    b3, bw3, bh3 = textbox(rx + r + 66, ry - 74, "≤ ¼\nбрехуни", size=13, bold=True,
                           fill="#fff", stroke=POS, sw=1.7, color=POS)
    p.append(b3)
    p.append(line(rx + r + 66 - bw3 / 2, ry - 74 + bh3 / 2, ex, ey, color=POS, sw=1.5, dash="4 3"))
    p.append(text(rx, 388, "щонайменше ¾ основ викривають n", size=12.5, color=MUTED))

    render(os.path.join(OUT, "liar-proportions.svg"), W, H, *p,
           title="Чому Міллера–Рабіна не обдурити, як Ферма")


# ── Фіг. 4: чому a*b % n тихо ламається і як це лагодять ──────────────────────
# Ідея (proj): головна пастка робочого коду. Добуток двох ~62-бітних чисел має
# до ~124 біт — старші не влазять у 64-бітне слово й зникають, тож % n рахує
# сміття. Ширший тип (__uint128_t) тримає всі біти → залишок точний.
def fig_overflow_mulmod():
    W, H = 980, 432
    p = []
    bx0, bx1 = 196.0, 900.0            # bit 0 .. bit 128 на осі
    def BX(bit):
        return bx0 + (bx1 - bx0) * bit / 128.0
    b64 = BX(64)
    barh = 30.0

    # межа 64-бітного слова + шкала
    p.append(line(b64, 62, b64, 372, color=POS, sw=1.6, dash="6 5"))
    p.append(text(b64, 54, "межа 64-бітного слова", size=12, color=POS, bold=True))
    p.append(line(BX(128), 250, BX(128), 366, color="#c2cad4", sw=1.2, dash="4 4"))
    p.append(text(bx0, 388, "0", size=10.5, color=MUTED))
    p.append(text(b64, 388, "64", size=10.5, color=MUTED))
    p.append(text(BX(128), 388, "128 біт", size=10.5, color=MUTED))

    # рядок 1: множники
    y1 = 100.0
    p.append(textbox(108.0, y1, "a, b", size=13.5, bold=True, min_w=96, fill=BG, stroke=INK)[0])
    p.append(rect(bx0, y1 - barh / 2, BX(63) - bx0, barh, fill="#eef2f7", stroke=INK, sw=1.6, rx=5))
    p.append(text((bx0 + BX(63)) / 2, y1 + 5, "кожен < 2⁶³ — ще влазить у слово", size=12, color=INK))

    # рядок 2: наївний добуток переповнюється
    y2 = 186.0
    p.append(textbox(108.0, y2, "u64\na * b", size=12.5, bold=True, min_w=96, fill=BG, stroke=POS, color=POS)[0])
    p.append(rect(bx0, y2 - barh / 2, b64 - bx0, barh, fill="#f7f8fa", stroke="#c2cad4", sw=1.5, rx=5))
    p.append(text((bx0 + b64) / 2, y2 + 5, "лишається у регістрі", size=11.5, color=MUTED))
    p.append(rect(b64, y2 - barh / 2, BX(124) - b64, barh, fill="#fdecea", stroke=POS, sw=1.7, rx=5))
    p.append(text((b64 + BX(124)) / 2, y2 + 5, "старші біти відкинуто", size=11.5, color=POS, bold=True))
    p.append(text((b64 + BX(124)) / 2, y2 + barh / 2 + 20, "→ далі  % n  рахує сміття", size=11.5, color=POS, bold=True))

    # рядок 3: ширший тип тримає весь добуток
    y3 = 292.0
    p.append(textbox(108.0, y3, "u128\na * b", size=12.5, bold=True, min_w=96, fill=BG, stroke=FIELD, color=FIELD)[0])
    p.append(rect(bx0, y3 - barh / 2, BX(124) - bx0, barh, fill="#eaf7ef", stroke=FIELD, sw=1.7, rx=5))
    p.append(text((bx0 + BX(124)) / 2, y3 + 5, "усі 128 біт добутку на місці", size=12, color=FIELD, bold=True))
    # залишок після % n
    yr = 352.0
    axr = (bx0 + BX(58)) / 2
    p.append(arrow(axr, y3 + barh / 2, axr, yr - 13, color=FIELD, sw=1.8))
    p.append(text(axr + 74, (y3 + barh / 2 + yr) / 2, "% n", size=12.5, color=FIELD, bold=True, anchor="start"))
    p.append(rect(bx0, yr - 13, BX(58) - bx0, 26, fill="#eaf7ef", stroke=FIELD, sw=1.6, rx=5))
    p.append(text((bx0 + BX(58)) / 2, yr + 5, "результат < n — точний", size=11.5, color=FIELD, bold=True))

    p.append(text(W / 2, 418, "ширше за 128 біт: множення подвоєнням (портативно) або за Монтгомері (швидко)",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "overflow-mulmod.svg"), W, H, *p,
           title="Пастка a·b mod n: переповнення й ширший тип")


# ── Фіг. 5: конвеєр робочого тесту — від n до вироку ──────────────────────────
# Ідея (proj): що насправді робить is_prime(n). Спершу дешеві фільтри
# (крайові → решето), потім розклад n−1=2ˢ·d, тоді розгалуження на два режими
# (детермінований для 64 біт / імовірнісний для крипторозміру) і спільний
# фінал — перевірка основ.
def fig_test_pipeline():
    W, H = 980, 556
    p = []
    cx = 340.0
    bw, bh = 336.0, 46.0

    def stage(y, s, sub=None, stroke=INK, fill="#f4f7fb"):
        p.append(fitbox(cx - bw / 2, y - bh / 2, bw, bh, s, size=13.5, bold=True, fill=fill, stroke=stroke))
        if sub:
            p.append(text(cx + bw / 2 + 18, y + 4, sub, size=11.5, color=MUTED, anchor="start"))

    def down(y1, y2):
        p.append(arrow(cx, y1, cx, y2, color="#8a94a0", sw=1.8))

    y = 70
    stage(y, "Крайові:  n < 2,  n = 2,  n = 3,  парність", sub="миттєвий вирок")
    down(y + bh / 2, 142 - bh / 2)
    y = 142
    stage(y, "Решето: ділення на 3, 5, 7, …, 53", sub="більшість складених — уже тут")
    down(y + bh / 2, 214 - bh / 2)
    y = 214
    stage(y, "Розклад  n − 1 = 2ˢ · d", stroke=NEG, fill="#eef2fe")

    # розгалуження на два режими
    fy = 306.0
    lx, rx = 196.0, 484.0
    fw, fh = 258.0, 60.0
    p.append(arrow(cx, 214 + bh / 2, lx + 40, fy - fh / 2 - 2, color="#8a94a0", sw=1.8))
    p.append(arrow(cx, 214 + bh / 2, rx - 40, fy - fh / 2 - 2, color="#8a94a0", sw=1.8))
    p.append(fitbox(lx - fw / 2, fy - fh / 2, fw, fh, "n < 2⁶⁴\n12 основ {2, 3, …, 37}",
                    size=13, bold=True, fill="#eaf7ef", stroke=FIELD))
    p.append(text(lx, fy + fh / 2 + 18, "детерміновано — точна відповідь", size=11.5, color=FIELD, bold=True))
    p.append(fitbox(rx - fw / 2, fy - fh / 2, fw, fh, "n ≥ 2⁶⁴\nk основ із CSPRNG",
                    size=13, bold=True, fill="#f7f8fa", stroke=MUTED))
    p.append(text(rx, fy + fh / 2 + 18, "похибка ≤ 4⁻ᵏ", size=11.5, color=MUTED, bold=True))

    # спільний фінал
    cvy = 408.0
    p.append(arrow(lx, fy + fh / 2 + 26, cx - 60, cvy - bh / 2 - 2, color="#8a94a0", sw=1.8))
    p.append(arrow(rx, fy + fh / 2 + 26, cx + 60, cvy - bh / 2 - 2, color="#8a94a0", sw=1.8))
    p.append(fitbox(cx - bw / 2, cvy - bh / 2, bw, bh, "is_witness для кожної основи",
                    size=13.5, bold=True, fill="#f4f7fb", stroke=INK))

    # два виходи-вироки
    py = 496.0
    plx, prx = 214.0, 566.0
    p.append(arrow(cx - 40, cvy + bh / 2, plx + 30, py - 15, color=POS, sw=1.9))
    p.append(text((cx - 40 + plx + 30) / 2 - 40, (cvy + bh / 2 + py) / 2, "свідок", size=11.5, color=POS, bold=True))
    p.append(textbox(plx, py, "n складене", size=13, bold=True, fill="#fff", stroke=POS, color=POS, min_w=150)[0])
    p.append(arrow(cx + 40, cvy + bh / 2, prx - 40, py - 15, color=FIELD, sw=1.9))
    p.append(text((cx + 40 + prx - 40) / 2 + 34, (cvy + bh / 2 + py) / 2, "усі мовчать", size=11.5, color=FIELD, bold=True))
    p.append(textbox(prx, py, "n просте / ймовірно просте", size=13, bold=True, fill="#fff", stroke=FIELD, color=FIELD, min_w=150)[0])

    render(os.path.join(OUT, "test-pipeline.svg"), W, H, *p,
           title="Конвеєр робочого тесту: від n до вироку")


# ── Фіг. (hist): дві стежки до швидкого тесту простоти, 1976→2002 ─────────────
# Ідея (hist): два імені — дві протилежні угоди. Верхня стежка (синя) —
# детерміновані тести, точні, але лише за недоведеної гіпотези Рімана: Міллер
# (1976) → AKS (2002), що нарешті знімає гіпотезу. Нижня (зелена) — імовірнісні
# й безумовні, ціною керованої похибки: Соловей–Штрассен (1977) → Рабін і Моньє
# (1980). Рабін зшив критерій Міллера з випадковими основами Соловея–Штрассена —
# діагональ між стежками.
def fig_history_timeline():
    W, H = 1180, 470
    p = []
    topy, boty = 182.0, 348.0
    cw, ch = 214.0, 86.0

    def card(cx, cy, title, body, stroke, fill):
        p.append(text(cx, cy - ch / 2 - 12, title, size=13, color=stroke, bold=True))
        p.append(fitbox(cx - cw / 2, cy - ch / 2, cw, ch, body, size=12.5,
                        fill=fill, stroke=stroke, sw=2.0))

    # смуги-підписи стежок ліворуч
    p.append(fitbox(26, topy - 38, 158, 76, "детерміновані —\nточні лише за\nгіпотези Рімана",
                    size=12, bold=True, fill="#eef2fe", stroke=NEG, color=NEG))
    p.append(fitbox(26, boty - 38, 158, 76, "імовірнісні —\nбезумовні, з\nкерованою похибкою",
                    size=12, bold=True, fill="#eaf7ef", stroke=FIELD, color=FIELD))

    # x3/x4 рознесені ширше, ніж у першій версії: колонки-картки нижньої
    # стежки (x2,x3) стояли впритул одна до одної, і підпис конектора між
    # ними (як і діагональ) наїжджав на текст карток — тут між ними довший
    # проміжок під двострічковий підпис.
    x1, x2, x3, x4 = 352.0, 486.0, 900.0, 1050.0

    # верхня (детермінована) стежка
    card(x1, topy, "Ґері Міллер · 1976", "детермінований,\nполіноміальний —\nза гіпотези Рімана", NEG, "#eef2fe")
    card(x4, topy, "AKS · 2002", "Аґравал, Каял, Саксена:\nбезумовний,\nдетермінований", NEG, "#eef2fe")
    # нижня (імовірнісна) стежка
    card(x2, boty, "Соловей–Штрассен · 1977", "перший практичний\nімовірнісний тест,\nпохибка 2⁻ᵏ", FIELD, "#eaf7ef")
    card(x3, boty, "Рабін · Моньє · 1980", "безумовний\nімовірнісний тест,\nпохибка 4⁻ᵏ", FIELD, "#eaf7ef")

    # верхній конектор: сон Міллера, здійснений через 26 років
    p.append(arrow(x1 + cw / 2 + 6, topy, x4 - cw / 2 - 6, topy, color=NEG, sw=1.8))
    p.append(text((x1 + x4) / 2, topy - 12, "той самий сон — уже без гіпотези (26 років)",
                  size=11.5, color=NEG, bold=True))
    # нижній конектор: та сама ідея, гостріша межа — двострічковий підпис,
    # щоб влізти у проміжок між картками й не зачепити їхній текст
    p.append(arrow(x2 + cw / 2 + 6, boty, x3 - cw / 2 - 6, boty, color=FIELD, sw=1.8))
    p.append(mtext((x2 + x3) / 2, boty - 32, ["та сама ідея,", "вдвічі гостріша межа"],
                   size=11, color=FIELD, bold=True, lh=1.15))
    # діагональ: Рабін зшиває критерій Міллера з випадковими основами —
    # підпис піднято далеко над лінією (не просто на -8), щоб вона його не
    # перетинала, і теж розбито на два рядки
    p.append(arrow(x1, topy + ch / 2 + 4, x3 - 14, boty - ch / 2 - 6, color=MUTED, sw=1.6))
    p.append(mtext(x1 + 230, topy + 37, ["критерій Міллера +", "випадкові основи"],
                   size=11, color=MUTED, bold=True, lh=1.2))

    render(os.path.join(OUT, "primality-timeline.svg"), W, H, *p,
           title="Дві стежки до швидкого тесту простоти")


# ── Фіг. (math): чому рівні −1 обмежені найкоротшою компонентою ───────────────
# Ідея підрахунку Моньє: за КТЗ основа розкладається на компоненти за простими
# степенями. −1 у драбині мусить з'явитися ОДНОЧАСНО в усіх компонентах, а в
# i-й компоненті −1 доступне лише на рівнях j < sᵢ. Тому спільний −1 можливий
# тільки до рівня ν = min sᵢ — звідси в лічбі й береться множник 2^(rν).
def fig_crt_levels():
    W, H = 980, 440
    p = []
    p.append(text(W / 2, 52,
                  "−1 мусить з'явитися ОДНОЧАСНО в кожній компоненті; у i-й воно доступне, лише поки j < sᵢ",
                  size=12.5, color=MUTED))
    base_x, dx, cw, ch = 320.0, 150.0, 122.0, 46.0

    def cx(j):
        return base_x + j * dx

    for j in range(4):
        p.append(text(cx(j), 122, "рівень  j = %d" % j, size=12.5, color=INK, bold=True))

    def comp_row(y, label, si):
        b, lw, lh = textbox(120.0, y, label, size=12, bold=True,
                            fill="#fbfdff", stroke=INK, sw=1.5, min_w=190)
        p.append(b)
        for j in range(4):
            green = j < si
            fill = "#eaf7ef" if green else "#f2f3f5"
            stroke = FIELD if green else "#c2cad4"
            p.append(rect(cx(j) - cw / 2, y - ch / 2, cw, ch, fill=fill, stroke=stroke,
                          sw=2.0 if green else 1.3, rx=8))
            if green:
                p.append(text(cx(j), y + 5, "−1 можливе", size=12, color=FIELD, bold=True))
            else:
                p.append(text(cx(j), y + 5, "−1 неможливе", size=11, color=MUTED))

    comp_row(185.0, "mod p₁^e₁\n(s₁ = 2)", 2)
    comp_row(295.0, "mod p₂^e₂\n(s₂ = 3)", 3)

    ox0 = cx(0) - cw / 2 - 11
    ox1 = cx(1) + cw / 2 + 11
    oy0 = 185.0 - ch / 2 - 16
    oy1 = 295.0 + ch / 2 + 16
    p.append(rect(ox0, oy0, ox1 - ox0, oy1 - oy0, fill="none", stroke=POS, sw=2.2, rx=10))
    p.append(text((ox0 + ox1) / 2, oy1 + 26,
                  "спільний −1: рівні j = 0 … ν−1,   ν = min(s₁, s₂) = 2",
                  size=13, color=POS, bold=True))
    p.append(text(W / 2, oy1 + 50,
                  "коротша компонента (s₁) все обриває → у лічбі з'являється множник 2^(r·ν)",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "liar-crt-levels.svg"), W, H, *p,
           title="Найкоротша компонента обмежує рівні −1 числом ν = min sᵢ")


# ── Фіг. (math): межа ¼ за структурою n — і чому 9 з-під неї вислизає ─────────
# Ідея межі: степінь простого несе множник 1/p^(e−1), що заганяє частку нижче ¼;
# стелю ¼ дістають ЛИШЕ безквадратні числа (добутки різних простих). Єдиний
# виняток — 9: частка 1/3 > 1/4, бо φ(9)=6 замала навіть для двох брехунів ±1.
def fig_bound_structure():
    W, H = 980, 480
    p = []
    x0, x1 = 118.0, 940.0
    ybase, ytop, vmax = 392.0, 96.0, 0.36

    def Y(v):
        return ybase - (v / vmax) * (ybase - ytop)

    p.append(line(x0, ytop - 12, x0, ybase, color=INK, sw=1.6))
    p.append(line(x0, ybase, x1, ybase, color=INK, sw=1.6))
    for v in (0.0, 0.1, 0.2, 0.3):
        yy = Y(v)
        p.append(line(x0 - 5, yy, x0, yy, color=INK, sw=1.2))
        p.append(text(x0 - 12, yy + 4, "%.1f" % v, size=11, color=MUTED, anchor="end"))
    p.append(line(x0, Y(0.25), x1, Y(0.25), color=POS, sw=1.7, dash="7 5"))
    p.append(text(x1, Y(0.25) - 9, "стеля  ¼ = φ(n)/4", size=12.5, color=POS, bold=True, anchor="end"))

    bw = 62.0

    def bar(cxp, label, ratio, color, tag=None):
        p.append(rect(cxp - bw / 2, Y(ratio), bw, ybase - Y(ratio), fill=color, stroke=INK, sw=1.2, rx=4))
        val = ("%.3f" % ratio).rstrip("0").rstrip(".")
        p.append(text(cxp, Y(ratio) - 8, val, size=11.5, color=INK, bold=True))
        p.append(text(cxp, ybase + 19, "n=" + label, size=12, color=INK, bold=True))
        if tag:
            p.append(text(cxp, Y(ratio) - 26, tag, size=12, color=POS, bold=True))

    A = [("9", 0.3333, POS, "виняток"), ("25", 0.2000, NEG, None),
         ("49", 0.1429, NEG, None), ("27", 0.1111, NEG, None)]
    B = [("15", 0.2500, FIELD, None), ("91", 0.2500, FIELD, None),
         ("8911", 0.2500, FIELD, None), ("561", 0.03125, FIELD, None)]
    gx, sp = 178.0, 96.0
    xA = [gx + i * sp for i in range(4)]
    for cxp, rec in zip(xA, A):
        bar(cxp, rec[0], rec[1], rec[2], rec[3])
    xB = [xA[-1] + sp + 46 + i * sp for i in range(4)]
    for cxp, rec in zip(xB, B):
        bar(cxp, rec[0], rec[1], rec[2], rec[3])

    p.append(line((xA[-1] + xB[0]) / 2, ytop - 12, (xA[-1] + xB[0]) / 2, ybase + 34,
                  color="#dfe4ea", sw=1.3, dash="5 5"))
    p.append(text((xA[0] + xA[-1]) / 2, ybase + 44, "степінь простого  p^e  (e ≥ 2)",
                  size=13, color=INK, bold=True))
    p.append(text((xB[0] + xB[-1]) / 2, ybase + 44, "добуток різних простих (безквадратне)",
                  size=13, color=INK, bold=True))
    p.append(text(W / 2, 460,
                  "Стелю ¼ дістають лише безквадратні числа; степені простого лежать строго нижче — окрім 9.",
                  size=12, color=MUTED))

    render(os.path.join(OUT, "liar-bound-structure.svg"), W, H, *p,
           title="Частка брехунів за структурою n: ¼ і виняток 9")


if __name__ == "__main__":
    fig_square_roots()
    fig_squaring_ladder()
    fig_liar_proportions()
    fig_overflow_mulmod()
    fig_test_pipeline()
    fig_history_timeline()
    fig_crt_levels()
    fig_bound_structure()
    print("OK figs")
