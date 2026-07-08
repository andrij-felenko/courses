# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


# ── Карта контекстів однієї компанії ─────────────────────────────────────────
# Кожен контекст — рамка (область змісту). Стик — підписана стрілка від верхового
# (диктує) до низового (наздоганяє). Мета розкладки: жодна лінія не ріже напис
# наскрізь — рамки й підписи розставлені з ЗАПАСОМ, лінії ведено ПОВЗ написи.
def fig_context_map():
    W, H = 1280, 760
    frags = []

    def ctx(cx, cy, name, sub, col, fill, w=224, h=92):
        x, y = cx - w / 2, cy - h / 2
        frags.append(rect(x, y, w, h, fill=fill, stroke=col, sw=2.0, rx=12))
        frags.append(text(cx, cy - 10, name, size=15, bold=True, color=col))
        frags.append(line(x + 18, cy + 4, x + w - 18, cy + 4, color=col, sw=1.0))
        frags.append(text(cx, cy + 27, sub, size=11, color=MUTED))
        return dict(cx=cx, cy=cy, x=x, y=y, w=w, h=h)

    money_col = "#0f766e"

    # ── розкладка: широкі зазори, вузол «Продажі» посередині ──
    sales   = ctx(640, 165, "Продажі",         "Client = воронка",       NEG,       "#eaf0fd")
    stock   = ctx(215, 165, "Склад",            "Item = позиція запасу",  FIELD,     "#f2faf5")
    billing = ctx(215, 470, "Бухгалтерія",      "Payer = платник",        "#b8860b", "#fdf6e3")
    bank    = ctx(1065, 165, "Платіжний банк",  "чужий велетень",         "#7a5195", "#f3eefb")
    quote   = ctx(640, 470, "Прорахунок ціни",  "спільна фіча",           NEG,       "#eaf0fd")
    mud     = ctx(1065, 470, "Стара «головна» база", "усе змішано",       POS,       "#fdecea", w=252)

    # Склад → Продажі : замовник/постачальник (склад верховий) — горизонтально вгорі
    frags.append(arrow(stock['cx'] + stock['w'] / 2, 150, sales['cx'] - sales['w'] / 2, 150,
                       color=INK, sw=2.0))
    frags.append(text(428, 128, "замовник ← постачальник", size=12, bold=True, color=INK))
    frags.append(text(428, 112, "склад диктує, продажі просять", size=10, italic=True, color=MUTED))

    # Банк → Продажі : конформіст (банк верховий) — горизонтально вгорі
    frags.append(arrow(bank['cx'] - bank['w'] / 2, 150, sales['cx'] + sales['w'] / 2, 150,
                       color="#7a5195", sw=2.0))
    frags.append(text(852, 128, "конформіст", size=12, bold=True, color="#7a5195"))
    frags.append(text(852, 112, "модель банку беремо як є", size=10, italic=True, color=MUTED))

    # Продажі → Бухгалтерія : через ACL (стрілка вниз-ліворуч, ACL на стику).
    # Ведемо ДВОМА прямими сегментами через вузол-ACL, щоб лінія впиралася в ACL, а не різала написи.
    aclbox, aw, ah = textbox(415, 320, "ACL",
                             size=12, bold=True, fill="#fff4e6", stroke=POS, sw=2.0, pad=9)
    frags.append(arrow(sales['cx'] - 0.55 * sales['w'] / 2, sales['cy'] + sales['h'] / 2,
                       415 + aw / 2, 320 - ah / 2, color=INK, sw=2.0))
    frags.append(arrow(415 - aw / 2 * 0.2, 320 + ah / 2,
                       billing['cx'] + 0.35 * billing['w'] / 2, billing['cy'] - billing['h'] / 2,
                       color=INK, sw=2.0))
    frags.append(aclbox)
    # підпис ПРАВОРУЧ від ACL-рамки (у чистій зоні, не на шляху жодної стрілки)
    frags.append(text(415 + aw / 2 + 12, 316, "перекладач:", size=10, italic=True,
                      color=POS, anchor="start"))
    frags.append(text(415 + aw / 2 + 12, 330, "воронку в облік не пускає", size=10, italic=True,
                      color=POS, anchor="start"))

    # Продажі ↔ Прорахунок : партнерство. Лінію ведемо ЗЛІВА від осі (x≈600),
    # напис ставимо ПРАВОРУЧ від лінії (x≈690), щоб лінія не різала текст.
    frags.append(line(sales['cx'] - 40, sales['cy'] + sales['h'] / 2,
                      quote['cx'] - 40, quote['cy'] - quote['h'] / 2, color=NEG, sw=2.4))
    frags.append(text(694, 305, "партнерство", size=12, bold=True, color=NEG, anchor="start"))
    frags.append(text(694, 321, "релізяться разом", size=10, italic=True, color=MUTED, anchor="start"))

    # Спільне ядро «Гроші» — вузол між Складом і Бухгалтерією (ліва колонка),
    # напис ЛІВОРУЧ, штрихові лінії йдуть праворуч від нього до рамок.
    kx, ky = 130, 320
    kbox, kw, kh = textbox(kx, ky, "спільне\nядро\n«Гроші»",
                           size=11, bold=True, fill="#e8f5f2", stroke=money_col, sw=1.8, pad=8)
    frags.append(line(stock['cx'] - 0.3 * stock['w'] / 2, stock['cy'] + stock['h'] / 2,
                      kx + kw / 2, ky - kh / 2 + 4, color=money_col, sw=1.6, dash="5,4"))
    frags.append(line(billing['cx'] - 0.3 * billing['w'] / 2, billing['cy'] - billing['h'] / 2,
                      kx + kw / 2, ky + kh / 2 - 4, color=money_col, sw=1.6, dash="5,4"))
    frags.append(kbox)

    # Продажі — Стара база : окремі шляхи (навмисний розрив).
    # Штрих ведемо низько (y≈205 → y≈452), напис ставимо ВИЩЕ лінії (y≈300), у порожнечі.
    frags.append(line(sales['cx'] + sales['w'] / 2, sales['cy'] + 0.5 * sales['h'],
                      mud['cx'] - mud['w'] / 2 - 20, mud['cy'] - mud['h'] / 2 - 8,
                      color=MUTED, sw=1.8, dash="2,7"))
    frags.append(text(905, 300, "окремі шляхи", size=12, bold=True, color=MUTED))
    frags.append(text(905, 316, "зв'язку немає навмисно", size=10, italic=True, color=MUTED))
    # штрихове огородження навколо грудки багна
    mx, my, mw, mh = mud['x'] - 14, mud['y'] - 14, mud['w'] + 28, mud['h'] + 28
    frags.append(rect(mx, my, mw, mh, fill="none", stroke=POS, sw=1.6, rx=14))
    frags.append(text(mud['cx'], my + mh + 16, "огороджено: визнаємо межу хаосу",
                      size=10, italic=True, color=POS))

    # легенда напряму течії — низ ліворуч, у чистій зоні
    ly0 = 700
    frags.append(text(70, ly0, "напрям стрілки = напрям болю від зміни:",
                      size=12, bold=True, color=INK, anchor="start"))
    frags.append(text(70, ly0 + 20, "верховий (диктує)  →  низовий (наздоганяє)",
                      size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'context-map.svg'), W, H, *frags,
           title="Карта контекстів компанії: межі змісту й іменований зв'язок на кожному стику")


# ── Перевірка карти-як-код: дві множини стрілок і їхня різниця ────────────────
# Ліворуч — ОГОЛОШЕНА карта (дозволені стрілки), праворуч — ЗНАЙДЕНІ в коді
# імпорти. Внизу — множинна різниця: ребро, якого нема в карті, і є пастка.
def fig_declared_vs_found():
    W, H = 1200, 620
    frags = []

    def node(cx, cy, name, col, r=30):
        frags.append(circle(cx, cy, r, fill="#f7f9fc", stroke=col, sw=2.0))
        frags.append(text(cx, cy + 5, name, size=14, bold=True, color=col))

    # два однакові трикутники вузлів (Продажі, Склад, Бухгалтерія) у двох панелях
    def panel(ox, edges, title, tcol):
        # рамка панелі
        frags.append(rect(ox, 70, 470, 300, fill="none", stroke=MUTED, sw=1.4, rx=12))
        frags.append(text(ox + 235, 96, title, size=15, bold=True, color=tcol))
        # координати вузлів усередині панелі
        S  = (ox + 235, 165)   # Продажі — вершина
        St = (ox + 120, 320)   # Склад — ліво-низ
        B  = (ox + 350, 320)   # Бухгалтерія — право-низ
        pos = {"S": S, "St": St, "B": B}
        for a, b, ok in edges:
            (x1, y1), (x2, y2) = pos[a], pos[b]
            col = FIELD if ok else POS
            # відступ від кола, щоб стрілка не впиралась у контур вузла
            import math
            dx, dy = x2 - x1, y2 - y1
            L = math.hypot(dx, dy) or 1
            ux, uy = dx / L, dy / L
            frags.append(arrow(x1 + ux * 34, y1 + uy * 34,
                               x2 - ux * 34, y2 - uy * 34,
                               color=col, sw=2.2 if not ok else 2.0))
        node(*S,  "Продажі",     NEG)
        node(*St, "Склад",       FIELD)
        node(*B,  "Бухгалтерія", "#b8860b")

    # ЛІВА панель: карта дозволяє Склад→Продажі та Продажі→Бухгалтерія
    panel(40, [("St", "S", True), ("S", "B", True)],
          "оголошено (карта як код)", NEG)
    # ПРАВА панель: у коді ті самі дві + зайва Бухгалтерія→Продажі (заборонена)
    panel(690, [("St", "S", True), ("S", "B", True), ("B", "S", False)],
          "знайдено (реальні імпорти)", INK)

    # стрілка «порівнюємо»
    frags.append(arrow(520, 220, 685, 220, color=INK, sw=2.0))
    frags.append(text(602, 205, "diff", size=13, bold=True, color=INK))

    # нижня плашка: різниця = порушення
    by = 430
    box, bw, bh = textbox(600, by + 34, "Бухгалтерія  →  Продажі",
                          size=15, bold=True, fill="#fdecea", stroke=POS, sw=2.0,
                          pad=12, color=POS, min_w=360)
    frags.append(box)
    frags.append(text(600, by, "різниця = стрілка, якої нема на карті  →  збірка падає (exit 1)",
                      size=14, bold=True, color=POS))
    frags.append(text(600, by + 70, "бухгалтерія тягне поняття продажів через межу — модель протікає",
                      size=12, italic=True, color=MUTED))

    render(os.path.join(IMG, 'declared-vs-found.svg'), W, H, *frags,
           title="Перевірка карти: оголошені стрілки проти знайдених у коді")


# ── Історія словника карти контекстів: три корені збігаються в одну мову ──────
# Вертикальна вісь часу (три віхи), кожна віха — картка ПРАВОРУЧ від осі, у своїй
# смузі, з широким зазором. Написи НЕ торкаються ні осі, ні сусідніх карток,
# ні власної рамки — ширину карток узято з ЗАПАСОМ під найдовший рядок.
def fig_vocab_timeline():
    W, H = 1240, 740
    frags = []

    axis_x = 150            # вертикальна вісь часу
    top, bot = 90, 660
    frags.append(line(axis_x, top, axis_x, bot, color=INK, sw=2.4))
    frags.append(text(axis_x, top - 20, "час", size=12, bold=True, color=MUTED))

    # три віхи на осі (зверху вниз — за роками)
    ys = [155, 360, 570]
    years = ["1968", "1997", "2003"]
    ycol = [NEG, POS, "#0f766e"]

    for yy, yr, cc in zip(ys, years, ycol):
        frags.append(circle(axis_x, yy, 9, fill=cc, stroke=cc, sw=2))
        frags.append(text(axis_x - 26, yy + 5, yr, size=16, bold=True, color=cc, anchor="end"))

    # ── картка ПРАВОРУЧ від осі: заголовок, автор, суть — кожна у своїй смузі ──
    def card(cy, col, fill, head, who, body_lines, cw=920):
        cx0 = axis_x + 66
        ch = 44 + len(body_lines) * 21 + 16
        x, y = cx0, cy - ch / 2
        frags.append(rect(x, y, cw, ch, fill=fill, stroke=col, sw=2.0, rx=12))
        # короткий горизонтальний конектор від осі до картки
        frags.append(line(axis_x + 9, cy, x, cy, color=col, sw=1.8))
        frags.append(text(x + 20, y + 26, head, size=15, bold=True, color=col, anchor="start"))
        frags.append(text(x + cw - 20, y + 26, who, size=12, italic=True,
                          color=MUTED, anchor="end"))
        yy = y + 48
        for ln in body_lines:
            frags.append(text(x + 20, yy, ln, size=12, color=INK, anchor="start"))
            yy += 21

    card(ys[0], NEG, "#eef3fe",
         "Закон Конвея — межі системи повторюють межі команд",
         "M. Conway, Datamation",
         ["«Система переймає форму спілкування організації, що її будує.»",
          "Корінь питання «звідки взялися самі кордони» на карті."])

    card(ys[1], POS, "#fdecea",
         "«Велика грудка багна» — чесне ім'я для хаосу",
         "B. Foote · J. Yoder, PLoP '97",
         ["Стихійно заросла система — де-факто найпоширеніша архітектура.",
          "Термін передує Евансу; карта переймає його як законний елемент."])

    card(ys[2], "#0f766e", "#e8f5f2",
         "Карта контекстів і словник із восьми відносин",
         "E. Evans, DDD · частина IV",
         ["partnership · shared kernel · customer/supplier · conformist",
          "anticorruption layer · open host service · published language · separate ways",
          "Не винахід одного — синтез спостережень спільноти патернів."])

    frags.append(text(axis_x + 66, bot + 40,
                      "Три різні корені — форма організації, чесність про хаос, іменований "
                      "зв'язок — зійшлися в одну робочу мову.",
                      size=12, italic=True, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'vocab-timeline.svg'), W, H, *frags,
           title="Звідки склалася мова карти контекстів: три корені однієї словникової системи")


if __name__ == "__main__":
    fig_context_map()
    fig_declared_vs_found()
    fig_vocab_timeline()
    print("figures written to", IMG)
