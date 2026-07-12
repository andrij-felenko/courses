# -*- coding: utf-8 -*-
"""Фігури до кроку «Вибір координації під задачу»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREENFILL = "#eafaf0"
BLUEFILL  = "#eef2fb"
REDFILL   = "#fdecea"
AMBERFILL = "#fff8ec"
AMBER     = "#c9922e"


def fig_coordination_ladder():
    """Драбина координації: три щаблі, ціна вгору, автономність униз."""
    W, H = 1180, 540
    f = []
    cx = 590
    minw = 560

    # ── три щаблі (згори — найдорожчий) ──
    b, _, _ = textbox(cx, 150,
                      "Щабель 2 · Консенсус — згода про ПОРЯДОК\n"
                      "один узгоджений лог · лідер · конфіг · замок · «рівно один»",
                      size=13, fill=REDFILL, stroke=POS, min_w=minw, bold=True)
    f.append(b)
    b, _, _ = textbox(cx, 290,
                      "Щабель 1 · Кворум — згода про ЗНАЧЕННЯ\n"
                      "W + R > N · лідера нема · розбіжність зводимо пізніше",
                      size=13, fill=BLUEFILL, stroke=NEG, min_w=minw, bold=True)
    f.append(b)
    b, _, _ = textbox(cx, 430,
                      "Щабель 0 · Ніякої координації — незалежні шарди\n"
                      "розклад за ключем · запит живе на одному вузлі · вузли не ждуть одне одного",
                      size=13, fill=GREENFILL, stroke=FIELD, min_w=minw, bold=True)
    f.append(b)

    # маленькі стрілки-«сходинки» між щаблями (знизу вгору)
    f.append(arrow(cx, 405, cx, 317, color=MUTED, sw=1.5))
    f.append(arrow(cx, 265, cx, 177, color=MUTED, sw=1.5))

    # ── права вісь: ціна росте вгору ──
    f.append(arrow(1030, 460, 1030, 122, color=POS, sw=2.2))
    f.append(text(1108, 150, "УГОРУ:", size=12, color=POS, bold=True))
    f.append(text(1108, 172, "↑ ціна рішення", size=11.5, color=MUTED))
    f.append(text(1108, 192, "↑ ризик простою", size=11.5, color=MUTED))
    f.append(text(1108, 212, "↑ складність", size=11.5, color=MUTED))

    # ── ліва вісь: автономність росте вниз ──
    f.append(arrow(150, 122, 150, 460, color=FIELD, sw=2.2))
    f.append(text(80, 388, "УНИЗ:", size=12, color=FIELD, bold=True))
    f.append(text(80, 410, "↑ автономність", size=11.5, color=MUTED))
    f.append(text(80, 430, "↑ дешевий масштаб", size=11.5, color=MUTED))
    f.append(text(80, 450, "↑ доступність", size=11.5, color=MUTED))

    f.append(text(cx, 502,
                  "Дефолт — найнижчий щабель, що ще коректний; нагору лізь, лише коли задача змусить.",
                  size=13, color=INK, italic=True))

    render(os.path.join(IMG, "coordination-ladder.svg"), W, H, *f,
           title="Драбина координації: скільки згоди справді треба")


def fig_coordination_tax():
    """Звідки ціна: шард торкається одного вузла; консенсус — раунд до живої більшості."""
    W, H = 1180, 520
    f = []
    f.append(line(590, 70, 590, 470, color=MUTED, sw=1, dash="4,6"))

    # ── Ліворуч: щабель 0, шард ──
    f.append(text(295, 68, "Щабель 0 · шард", size=15, bold=True))
    b, _, _ = textbox(295, 116, "запит", size=12, fill=FILL, stroke=MUTED, min_w=96)
    f.append(b)
    b, _, _ = textbox(295, 214, "вузол дому", size=13, fill=GREENFILL, stroke=FIELD,
                      min_w=168, bold=True)
    f.append(b)
    f.append(arrow(295, 134, 295, 190, color=FIELD, sw=2))
    # два незалежні сусідні шарди осторонь — не задіяні
    b, _, _ = textbox(150, 300, "інший\nшард", size=11, fill="#eef1f4", stroke=MUTED, min_w=84)
    f.append(b)
    b, _, _ = textbox(440, 300, "інший\nшард", size=11, fill="#eef1f4", stroke=MUTED, min_w=84)
    f.append(b)
    f.append(text(295, 372, "0 додаткових мережевих раундів", size=12.5, color=FIELD, bold=True))
    f.append(text(295, 396, "сусідній шард упав → цей працює далі", size=12, color=MUTED))
    f.append(text(295, 420, "масштаб — просто додай іще шардів", size=12, color=MUTED))

    # ── Праворуч: щабель 2, консенсус ──
    f.append(text(885, 68, "Щабель 2 · консенсус", size=15, bold=True))
    b, _, _ = textbox(885, 112, "пропозиція рішення", size=12, fill=FILL, stroke=MUTED, min_w=176)
    f.append(b)
    nodes = [(705, True), (795, True), (885, True), (975, False), (1065, False)]
    for i, (nx, acked) in enumerate(nodes):
        col = FIELD if acked else MUTED
        fillc = GREENFILL if acked else "#eef1f4"
        b, _, _ = textbox(nx, 262, "N%d" % (i + 1), size=12, fill=fillc, stroke=col,
                          min_w=64, bold=acked)
        f.append(b)
        f.append(arrow(885, 132, nx, 238,
                       color=(FIELD if acked else MUTED), sw=(1.7 if acked else 1.2)))
    f.append(text(885, 322, "3 з 5 підтвердили = ЖИВА більшість → рішення ухвалено",
                  size=12.5, color=FIELD, bold=True))
    f.append(text(885, 372, "раунд туди-й-назад на КОЖНЕ рішення", size=12, color=POS))
    f.append(text(885, 396, "нема більшості живих → рішення не ухвалюється", size=12, color=POS))
    f.append(text(885, 420, "додав вузлів → кворум БІЛЬШИЙ, не швидший", size=12, color=MUTED))

    f.append(text(590, 500,
                  "Кожен щабель угору — ще один раунд до більшості й ще одна причина стати недоступним.",
                  size=13, color=INK, italic=True))

    render(os.path.join(IMG, "coordination-tax.svg"), W, H, *f,
           title="Ціна координації: локальний шард проти раунду в більшість")


def fig_dh_map():
    """DH: велика площина даних без координації + крихітне консенсус-ядро."""
    W, H = 1200, 560
    f = []

    # ── Data plane: велика зелена площина ──
    f.append(rect(40, 74, 700, 400, fill="#f2fbf6", stroke=FIELD, sw=1.8, rx=12))
    f.append(text(390, 104, "Data plane — шарди за home_id · нуль координації",
                  size=14, bold=True, color=INK))
    cells = [
        (215, 168, "шард 1 · доми A–F"),
        (565, 168, "шард 2 · доми G–M"),
        (215, 300, "шард 3 · доми N–S"),
        (565, 300, "шард 4 · доми T–Z"),
    ]
    for (bx, by, label) in cells:
        b, _, _ = textbox(bx, by, label, size=12.5, fill=GREENFILL, stroke=FIELD,
                          min_w=300, bold=True)
        f.append(b)
        f.append(text(bx, by + 34, "твін · телеметрія · автоматизації — усе тут",
                      size=10.5, color=MUTED))
    f.append(text(390, 448, "99% роботи — тут, кожен дім самодостатній, вузли не ждуть одне одного",
                  size=12, color=FIELD, italic=True))

    # ── Control plane: крихітне червоне ядро ──
    f.append(rect(812, 74, 348, 210, fill="#fdf0ee", stroke=POS, sw=1.8, rx=12))
    f.append(text(986, 104, "Control plane", size=14, bold=True, color=INK))
    f.append(text(986, 124, "консенсус-ядро · 3–5 вузлів", size=11, color=MUTED))
    for i, label in enumerate(("shard-map: де живе дім", "вибір лідера джоб", "конфіг кластера")):
        b, _, _ = textbox(986, 160 + i * 42, label, size=12, fill=REDFILL, stroke=POS, min_w=300)
        f.append(b)

    # ── Репліки: кворум-читання ──
    f.append(rect(812, 320, 348, 154, fill="#eef2fb", stroke=NEG, sw=1.6, rx=12))
    f.append(text(986, 350, "Репліки твіна", size=14, bold=True, color=INK))
    b, _, _ = textbox(986, 400, "кворум-читання\nлаг терпимо (щабель 1)", size=12,
                      fill=BLUEFILL, stroke=NEG, min_w=300)
    f.append(b)
    f.append(text(986, 452, "широкі читання дому без походу в ядро", size=10.5, color=MUTED))

    # ── зв'язок: площина даних питає ядро ЗРІДКА ──
    f.append(line(740, 180, 812, 180, color=MUTED, sw=1.8, dash="6,6"))
    f.append(text(776, 166, "зрідка", size=10.5, color=MUTED))
    f.append(text(776, 202, "«де мій шард?»", size=10.5, color=MUTED))

    f.append(text(600, 520,
                  "Мала сильно-узгоджена серцевина вирішує кілька глобальних фактів; велика площина роботи їх лише зчитує.",
                  size=12.5, color=INK, italic=True))

    render(os.path.join(IMG, "dh-coordination-map.svg"), W, H, *f,
           title="DH: велика площина без координації + крихітне консенсус-ядро")


def fig_shared_nothing_lineage():
    """Родовід ідеї: від «нічого спільного заради швидкості» до «координуй лише немонотонне»."""
    W, H = 1400, 470
    f = []
    axis_y = 300

    # ── дві зони (структурний бік ліворуч, точковий праворуч) ──
    f.append(rect(44, 150, 700, 250, fill=GREENFILL, stroke=FIELD, sw=1.5, rx=12))
    f.append(rect(800, 150, 556, 250, fill=AMBERFILL, stroke=AMBER, sw=1.5, rx=12))
    f.append(text(394, 178, "СТРУКТУРНО: не ділити нічого — ні пам'яті, ні диска між вузлами",
                  size=13, bold=True, color=FIELD))
    f.append(text(1078, 178, "ТОЧКОВО: координувати лише там, де логіка немонотонна",
                  size=13, bold=True, color=AMBER))

    # ── осі часу в межах кожної зони ──
    f.append(line(72, axis_y, 716, axis_y, color=MUTED, sw=2))
    f.append(line(824, axis_y, 1332, axis_y, color=MUTED, sw=2))

    # ── розрив у часі між зонами ──
    f.append(line(772, 246, 772, 354, color=MUTED, sw=1.4, dash="5,6"))
    f.append(text(772, 234, "пауза", size=11, color=MUTED))
    f.append(text(772, 372, "~24 роки", size=11, color=MUTED))

    events = [
        (165, "1974", "Tandem засновано\nДж. Трейбіг (ex-HP)", "up",   FIELD, GREENFILL),
        (280, "1976", "NonStop → Citibank\nSN заради надійності", "down", FIELD, GREENFILL),
        (395, "1979", "Teradata засновано\nФ. Нечес (Caltech)", "up",   FIELD, GREENFILL),
        (510, "1983", "DBC/1012 — перша\nкомерційна SN-БД", "down", FIELD, GREENFILL),
        (625, "1986", "Стоунбрейкер назвав\nпатерн «shared nothing»", "up", FIELD, GREENFILL),
        (915, "2010", "CALM-конжектура\nГеллерстайн (PODS)", "up",   AMBER, AMBERFILL),
        (1078, "2014", "Уникання координації\nБейліс та ін. (VLDB)", "down", AMBER, AMBERFILL),
        (1240, "2019", "«Keeping CALM»\nГеллерстайн, Альваро", "up", AMBER, AMBERFILL),
    ]
    for (x, year, desc, side, col, fillc) in events:
        # вузол з роком усередині
        f.append(circle(x, axis_y, 17, fill=fillc, stroke=col, sw=2))
        f.append(text(x, axis_y + 4, year, size=11, bold=True, color=INK))
        if side == "up":
            f.append(line(x, axis_y - 18, x, axis_y - 44, color=col, sw=1.4))
            b, _, _ = textbox(x, axis_y - 68, desc, size=11.5, fill="#ffffff",
                              stroke=col, min_w=200)
            f.append(b)
        else:
            f.append(line(x, axis_y + 18, x, axis_y + 44, color=col, sw=1.4))
            b, _, _ = textbox(x, axis_y + 68, desc, size=11.5, fill="#ffffff",
                              stroke=col, min_w=200)
            f.append(b)

    render(os.path.join(IMG, "shared-nothing-lineage.svg"), W, H, *f,
           title="Родовід «уникати координації»: спершу структурою, згодом — точково")


def fig_audit_traps():
    """Три операції DH, що падають не туди, куди підказує чуйка (пастки аудиту)."""
    W, H = 1180, 560
    f = []
    f.append(text(W / 2, 52,
                  "Ворота: «чи мусить бути рівно один / строгий порядок?»",
                  size=13, color=MUTED, italic=True))
    # заголовки колонок
    f.append(text(175, 92, "Операція", size=13, bold=True))
    f.append(text(510, 92, "Як підказує чуйка", size=13, bold=True, color=AMBER))
    f.append(text(905, 92, "Що каже питання воріт", size=13, bold=True, color=INK))

    lanes = [
        (168, "Унікальний ID\nпристрою / замовлення",
              "наче щабель 2\nкожен номер — через ядро",
              "насправді щабель 0\nліза блоку ID → далі локально", GREENFILL, FIELD),
        (310, "Оновлення\nпрошивки пристрою",
              "наче щабель 0\nпросто запис у пристрій",
              "насправді щабель 2\nдвоє не разом → замок + fencing", REDFILL, POS),
        (452, "Лічильник\nвикористання / білінг",
              "наче щабель 2\nмає бути точно до копійки",
              "насправді щабель 0\nлічильники домів → сума потім", GREENFILL, FIELD),
    ]
    for (y, op, naive, real, rfill, rstroke) in lanes:
        b, _, _ = textbox(175, y, op, size=12.5, fill=FILL, stroke=MUTED,
                          min_w=232, bold=True)
        f.append(b)
        f.append(arrow(296, y, 372, y, color=MUTED, sw=1.6))
        b, _, _ = textbox(510, y, naive, size=12, fill=AMBERFILL, stroke=AMBER, min_w=258)
        f.append(b)
        f.append(arrow(648, y, 752, y, color=rstroke, sw=2))
        b, _, _ = textbox(905, y, real, size=12, fill=rfill, stroke=rstroke,
                          min_w=292, bold=True)
        f.append(b)

    f.append(text(W / 2, 528,
                  "Наївний щабель — амбер; справжній — зелений (0) чи червоний (2). "
                  "Пастка саме там, де чуйка тягне не туди.",
                  size=12.5, color=INK, italic=True))
    render(os.path.join(IMG, "audit-traps.svg"), W, H, *f,
           title="Три пастки аудиту: де чуйка бреше про щабель")


def fig_round_tax():
    """Податок раундів: локальна операція проти рішення консенсусом + чому +вузли не швидші."""
    W, H = 1200, 680
    f = []

    # ── Регіон 1: часова смуга ──
    f.append(text(W / 2, 60, "Ціна однієї операції на спільній осі часу (RTT у ДЦ ≈ 1 мс)",
                  size=14, bold=True))

    def X(t):
        return 150 + t * 250.0

    # вісь часу
    f.append(line(150, 250, 1000, 250, color=MUTED, sw=1.4))
    for t in (0, 1, 2, 3):
        f.append(line(X(t), 246, X(t), 254, color=MUTED, sw=1.2))
        f.append(text(X(t), 272, ("%d мс" % t) if t else "0", size=11, color=MUTED))

    # Лане 0 — локальна операція
    f.append(text(150, 108, "Щабель 0 · локальна операція", size=13, bold=True, anchor="start"))
    f.append(rect(150, 120, X(0.2) - 150, 28, fill=GREENFILL, stroke=FIELD, sw=1.8))
    f.append(text(X(0.2) + 14, 139, "≈ 0.2 мс · 0 мережевих раундів",
                  size=12.5, color=FIELD, anchor="start", bold=True))
    f.append(line(X(0.2), 148, X(0.2), 172, color=MUTED, sw=1, dash="3,5"))
    f.append(line(X(0.2), 190, X(0.2), 196, color=MUTED, sw=1, dash="3,5"))

    # Лане 2 — рішення консенсусом (сегменти)
    f.append(text(150, 184, "Щабель 2 · рішення консенсусом", size=13, bold=True, anchor="start"))
    f.append(rect(X(0.0), 196, X(0.5) - X(0.0), 28, fill=AMBERFILL, stroke=AMBER, sw=1.6))
    f.append(rect(X(0.5), 196, X(1.5) - X(0.5), 28, fill=BLUEFILL, stroke=NEG, sw=1.6))
    f.append(rect(X(1.5), 196, X(2.4) - X(1.5), 28, fill=GREENFILL, stroke=FIELD, sw=1.6))
    f.append(line(X(2.4), 224, X(2.4), 250, color=POS, sw=1.4, dash="3,4"))
    f.append(text(X(2.4) + 10, 214, "≈ кілька мс", size=12.5, color=POS, anchor="start", bold=True))
    # підписи сегментів
    f.append(text((X(0.0) + X(0.5)) / 2, 242, "fsync лідера", size=10.5, color=MUTED))
    f.append(text((X(0.5) + X(1.5)) / 2, 242, "1 RTT до живої більшості", size=10.5, color=NEG))
    f.append(text((X(1.5) + X(2.4)) / 2, 242, "коміт", size=10.5, color=FIELD))

    f.append(text(W / 2, 300,
                  "Локальна операція фінішує там, де консенсус лише починає роздавати пропозицію.",
                  size=12.5, color=INK, italic=True))

    # ── Регіон 2: чому +вузли не швидші ──
    f.append(line(120, 330, 1080, 330, color=MUTED, sw=1, dash="4,6"))
    f.append(text(W / 2, 362, "Чому додати вузлів не робить консенсус швидшим", size=14, bold=True))

    step = 58
    x0 = 250
    markers = []
    for (N, y) in ((3, 418), (5, 500), (7, 582)):
        maj = N // 2 + 1
        f.append(text(178, y + 4, "N=%d" % N, size=13, bold=True))
        for i in range(N):
            cx = x0 + i * step
            if i < maj:
                f.append(circle(cx, y, 15, fill=GREENFILL, stroke=FIELD,
                                sw=(2.4 if i == 0 else 1.6)))
                if i == 0:
                    f.append(text(cx, y + 4, "L", size=11, color=INK, bold=True))
            else:
                f.append(circle(cx, y, 15, fill="#eef1f4", stroke=MUTED, sw=1.2))
        xt = x0 + (maj - 1) * step + step // 2
        markers.append((xt, y))
        f.append(line(xt, y - 30, xt, y + 30, color=POS, sw=1.8, dash="4,4"))
        f.append(text(772, y + 4, "кворум %d · чекає %d акк%s"
                      % (maj, maj - 1, "" if maj - 1 == 1 else "и"),
                      size=12, color=INK, anchor="start"))
    # дрейф порога праворуч
    f.append(text(markers[0][0], 392, "поріг: останній потрібний акк",
                  size=10.5, color=POS))
    f.append(arrow(markers[0][0], markers[0][1] + 30, markers[2][0], markers[2][1] - 30,
                   color=POS, sw=1.6))

    f.append(text(W / 2, 646,
                  "Кворум = ⌊N/2⌋+1: більше вузлів → більший кворум → останній потрібний акк лише пізніше. "
                  "+Вузли = витривалість, не швидкість; лідер із логом лишається один.",
                  size=12, color=INK, italic=True))

    render(os.path.join(IMG, "round-tax.svg"), W, H, *f,
           title="Податок раундів: локальна операція проти рішення консенсусом")


if __name__ == "__main__":
    fig_coordination_ladder()
    fig_coordination_tax()
    fig_dh_map()
    fig_shared_nothing_lineage()
    fig_audit_traps()
    fig_round_tax()
    print("OK: coordination-ladder.svg, coordination-tax.svg, dh-coordination-map.svg, "
          "shared-nothing-lineage.svg, audit-traps.svg, round-tax.svg")
