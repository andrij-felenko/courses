# -*- coding: utf-8 -*-
"""Фігури до кроку «Автентифікація проти авторизації»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREENBG = "#eef7f0"
REDBG = "#fdecea"
BLUEBG = "#eaf0fd"


def fig_two_questions():
    """Дві межі поспіль: автентифікація (хто?) → авторизація (чи можна?); 401 і 403."""
    W, H = 1180, 470
    ax = 182
    frags = []

    rq, rqw, rqh = textbox(92, ax, "запит\nвід Олі", size=14, fill=FILL)
    g1x = 350
    g1, g1w, g1h = textbox(g1x, ax, "Автентифікація\n«хто ти?»", size=15,
                           fill=GREENBG, stroke=FIELD, sw=1.9)
    g2x = 712
    g2, g2w, g2h = textbox(g2x, ax, "Авторизація\n«чи можна тобі\nсаме це?»", size=15,
                           fill=GREENBG, stroke=FIELD, sw=1.9)
    dnx = 1082
    dn, dnw, dnh = textbox(dnx, ax, "дію\nвиконано", size=14, fill=GREENBG, stroke=FIELD)

    # горизонтальний хребет
    frags.append(arrow(92 + rqw / 2, ax, g1x - g1w / 2, ax, color=INK, sw=2.2))
    frags.append(arrow(g1x + g1w / 2, ax, g2x - g2w / 2, ax, color=INK, sw=2.2))
    frags.append(arrow(g2x + g2w / 2, ax, dnx - dnw / 2, ax, color=INK, sw=2.2))
    # підписи успіху — над стрілками, одним рядком
    frags.append(text((g1x + g1w / 2 + g2x - g2w / 2) / 2, ax - 16,
                      "суб'єкт: Оля, справжня", size=12, color=FIELD))
    frags.append(text((g2x + g2w / 2 + dnx - dnw / 2) / 2, ax - 16,
                      "право є", size=12, color=FIELD))

    # відмови — падають униз
    fy = 372
    frags.append(arrow(g1x, ax + g1h / 2, g1x, fy - 34, color=POS, sw=2))
    frags.append(text(g1x - 14, (ax + g1h / 2 + fy - 34) / 2 + 4,
                      "нема / хибний доказ", size=11, color=MUTED, anchor="end"))
    frags.append(arrow(g2x, ax + g2h / 2, g2x, fy - 34, color=POS, sw=2))
    frags.append(text(g2x - 14, (ax + g2h / 2 + fy - 34) / 2 + 4,
                      "права бракує", size=11, color=MUTED, anchor="end"))

    # спершу бокси-хребта, тоді відмови (щоб лежали поверх)
    frags.extend([rq, g1, g2, dn])
    f401, _, _ = textbox(g1x, fy, "401 Unauthorized\n«не знаю, хто ти»", size=13,
                         fill=REDBG, stroke=POS)
    f403, _, _ = textbox(g2x, fy, "403 Forbidden\n«знаю — але ні»", size=13,
                         fill=REDBG, stroke=POS)
    frags.extend([f401, f403])

    frags.append(text(W / 2, 448,
                      "Пройти першу межу — ще не пройти другу; кожна ламається своїм кодом.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "two-questions.svg"), W, H, *frags,
           title="Дві межі: хто ти? (автентифікація) і що тобі можна? (авторизація)")


def fig_once_vs_every():
    """Особу доводять раз на сеанс; право перевіряють на кожну дію над її обʼєктом."""
    W, H = 1180, 400
    ay = 236
    frags = []

    # вісь часу
    frags.append(arrow(64, ay, 1112, ay, color=MUTED, sw=2.2))
    frags.append(text(1116, ay + 5, "час →", size=12, color=MUTED, anchor="start"))
    frags.append(text(1104, ay + 26, "один сеанс", size=11, color=MUTED, anchor="end"))

    # ── ліворуч: автентифікація РАЗ ──
    lx = 150
    frags.append(circle(lx, ay, 26, fill=GREENBG, stroke=FIELD, sw=2.6))
    frags.append(text(lx, ay + 5, "вхід", size=14, color=INK, bold=True))
    tok, tw, th = textbox(lx, 118, "автентифікація —\nраз: токен несе\nсуб'єкта далі", size=12,
                          fill=GREENBG, stroke=FIELD)
    frags.append(line(lx, 118 + th / 2, lx, ay - 26, color=FIELD, sw=1.6))
    frags.append(tok)

    # ── праворуч: авторизація ЩОРАЗУ ──
    acts = [
        (392, ["читати", "свій дім"], "так", FIELD),
        (588, ["змінити", "свою уставку"], "так", FIELD),
        (784, ["відкрити", "дім Марти"], "ні", POS),
        (980, ["знести", "акаунт"], "ні", POS),
    ]
    for x, label, verdict, col in acts:
        frags.append(circle(x, ay, 6, fill=INK, stroke=INK))
        box, bw, bh = textbox(x, 120, label, size=12, fill=FILL, stroke=MUTED)
        frags.append(line(x, 120 + bh / 2, x, ay - 6, color=MUTED, sw=1.3))
        frags.append(box)
        vb, vw, vh = textbox(x, 322, "авториз.?\n" + verdict, size=12,
                             fill=(GREENBG if col == FIELD else REDBG), stroke=col, color=col, bold=True)
        frags.append(line(x, ay + 6, x, 322 - vh / 2, color=col, sw=1.4))
        frags.append(vb)

    frags.append(text((392 + 980) / 2, 372,
                      "авторизація — щоразу, над своїм обʼєктом: одна особа, різні відповіді",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "once-vs-every.svg"), W, H, *frags,
           title="Один доказ особи на сеанс — багато перевірок права на дії")


def fig_conflation_idor():
    """Той самий автентифікований запит: із другою межею — 403; без неї — витік чужих даних."""
    W, H = 1200, 470
    frags = []

    rq, rqw, rqh = textbox(140, 235, "Оля\n(автентифікована)\nпросить дім Марти",
                           size=13, fill=FILL)

    # розгалуження вгору (правильно) і вниз (зламано)
    topy, boty = 118, 356
    frags.append(arrow(140 + rqw / 2, 210, 300, topy + 12, color=INK, sw=2))
    frags.append(arrow(140 + rqw / 2, 260, 300, boty - 12, color=INK, sw=2))

    # ── верхній шлях: є друга межа ──
    frags.append(text(360, topy - 66, "правильно: друга межа на місці", size=13,
                      color=FIELD, bold=True, anchor="start"))
    a1, a1w, a1h = textbox(360, topy, "автентиф. ✓", size=12, fill=GREENBG, stroke=FIELD)
    gate, gw, gh = textbox(560, topy, "авторизація:\n«Олин це дім?»", size=12,
                           fill=FILL, stroke=INK)
    verd, vw, vh = textbox(760, topy, "ні → 403", size=13, fill=REDBG, stroke=POS,
                           color=POS, bold=True)
    safe, sw_, sh = textbox(1000, topy, "дані Марти\nв безпеці", size=13,
                            fill=GREENBG, stroke=FIELD)
    frags.append(arrow(360 + a1w / 2, topy, 560 - gw / 2, topy, color=INK, sw=1.9))
    frags.append(arrow(560 + gw / 2, topy, 760 - vw / 2, topy, color=INK, sw=1.9))
    frags.append(arrow(760 + vw / 2, topy, 1000 - sw_ / 2, topy, color=POS, sw=1.9))
    frags.extend([a1, gate, verd, safe])

    # ── нижній шлях: другої межі немає ──
    frags.append(text(360, boty + 70, "зламано: «залогований = можна»", size=13,
                      color=POS, bold=True, anchor="start"))
    b1, b1w, b1h = textbox(360, boty, "автентиф. ✓", size=12, fill=GREENBG, stroke=FIELD)
    gap, gpw, gph = textbox(590, boty, "межі авторизації\nнемає", size=12,
                            fill=BG, stroke=POS, sw=1.6)
    leak, lw, lh = textbox(880, boty, "дім Марти\nвіддано Олі", size=13,
                           fill=REDBG, stroke=POS, color=POS, bold=True)
    # порожня межа — пунктир навколо; запит проходить наскрізь
    frags.append(arrow(360 + b1w / 2, boty, 590 - gpw / 2, boty, color=MUTED, sw=1.7))
    frags.append(arrow(590 + gpw / 2, boty, 880 - lw / 2, boty, color=POS, sw=2.1))
    frags.extend([b1, gap, leak])
    frags.append(text(880 + lw / 2 + 16, boty, "горизонтальна", size=12, color=POS, anchor="start"))
    frags.append(text(880 + lw / 2 + 16, boty + 18, "ескалація (IDOR)", size=12, color=POS, anchor="start"))

    frags.append(text(W / 2, 452,
                      "Різниця не в зламаному замку, а у відсутньому другому — перевірці, якої не написали.",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "conflation-idor.svg"), W, H, *frags,
           title="Відсутній другий замок: автентифікований ≠ авторизований")


def fig_three_roots():
    """Один розлам проступає тричі: у мові, у системах, у протоколі — той самий шов."""
    W, H = 1240, 560
    axy = 280
    frags = []

    # ── вісь часу ──
    frags.append(arrow(90, axy, 1150, axy, color=MUTED, sw=2.2))
    frags.append(text(1156, axy + 5, "час →", size=12, color=MUTED, anchor="start"))
    frags.append(text(1148, axy - 12, "різні століття, різні середовища",
                      size=11, color=MUTED, anchor="end"))

    nodes = [280, 620, 960]

    # ── події НАД віссю ──
    events = [
        ("≈ XV століття · у мові",
         ["хибна етимологія зрощує", "грецьке «справжній»", "з латинським «влада»"]),
        ("1977 → 1988 · у системах",
         ["«збитий з пантелику", "заступник» — привілей", "діє чужою рукою"]),
        ("1996 · у протоколі",
         ["HTTP 401 «Unauthorized»", "названо збоєм", "АВТЕНТИФІКАЦІЇ"]),
    ]
    for x, (head, body) in zip(nodes, events):
        card, cw, ch = textbox(x, 150, "\n".join([head] + body), size=13,
                               fill=FILL, stroke=INK, sw=1.7)
        frags.append(line(x, 150 + ch / 2, x, axy - 9, color=INK, sw=1.4))
        frags.append(card)
        frags.append(circle(x, axy, 8, fill=INK, stroke=INK))

    # ── наслідки ПІД віссю ──
    conseq = [
        "правопис «author» —\nшрам тієї плутанини",
        "компілятор переписав\nбілінг Tymshare",
        "401 і 403 плутають\nдосі",
    ]
    for x, s in zip(nodes, conseq):
        box, bw, bh = textbox(x, 372, s, size=12, fill=BG, stroke=MUTED, color=MUTED)
        frags.append(line(x, axy + 8, x, 372 - bh / 2, color=MUTED, sw=1.2))
        frags.append(box)

    # ── підсумок: той самий розлом ──
    frags.append(text(W / 2, 440, "усі три — той самий розлом:", size=13,
                      color=INK, bold=True))
    lb, lbw, lbh = textbox(468, 498, "справжність\n«хто ти?»", size=13,
                           fill=GREENBG, stroke=FIELD, color=FIELD, bold=True)
    rb, rbw, rbh = textbox(772, 498, "надане право\n«що тобі можна?»", size=13,
                           fill=BLUEBG, stroke=NEG, color=NEG, bold=True)
    # червоний зшив між ними
    frags.append(line(468 + lbw / 2 + 6, 502, 772 - rbw / 2 - 6, 502, color=POS, sw=2))
    frags.append(text(W / 2, 491, "сплутано в одне", size=12, color=POS, bold=True))
    frags.extend([lb, rb])

    render(os.path.join(IMG, "three-roots.svg"), W, H, *frags,
           title="Один розлам — три скам'янілості")


def fig_gate_placement():
    """Де сидить брама: після завантаження обʼєкта, не при дверях."""
    W, H = 1260, 560
    frags = []
    ay = 172

    nodes = [
        (120, "запит\n:id у URL", FILL, LINE, 1.5, False),
        (368, "автентифікація\nпри дверях\n«хто ти?»", GREENBG, FIELD, 1.9, False),
        (626, "завантажити\nдім за id", FILL, LINE, 1.5, False),
        (892, "АВТОРИЗАЦІЯ\nбрама\ncan(суб., дія, дім)?", GREENBG, FIELD, 2.4, True),
        (1136, "обробник\nдім — уже твій", GREENBG, FIELD, 1.9, False),
    ]
    built = []
    for x, s, fill, stroke, sw, bold in nodes:
        b, w, h = textbox(x, ay, s, size=13, fill=fill, stroke=stroke, sw=sw, bold=bold)
        built.append((x, w, h, b))
    for i in range(len(built) - 1):
        x1, w1, _, _ = built[i]
        x2, w2, _, _ = built[i + 1]
        frags.append(arrow(x1 + w1 / 2, ay, x2 - w2 / 2, ay, color=INK, sw=2.1))
    frags.append(text(626, ay + 60, "тепер відомі власник і члени", size=12, color=MUTED))
    frags.append(text(892, ay - 54, "трійця: суб'єкт · дія · обʼєкт", size=12, color=FIELD))
    for _, _, _, b in built:
        frags.append(b)

    bx, by = 368, 404
    frags.append(line(bx, ay + built[1][2] / 2, bx, by - 48, color=POS, sw=1.8, dash="6 5"))
    frags.append(text(bx + 18, (ay + built[1][2] / 2 + by - 48) / 2, "✗", size=20, color=POS,
                      bold=True, anchor="start"))
    blind, _, _ = textbox(bx, by, "брама ТУТ — сліпа:\nє лише рядок id,\nвласник ще невідомий",
                          size=12, fill=REDBG, stroke=POS, sw=1.8, color=POS)
    frags.append(blind)

    frags.append(text(W / 2, 516,
                      "Брама стоїть ПІСЛЯ завантаження: рішення потребує самого обʼєкта — його "
                      "власника й ролей, а не лише імені.", size=13, color=MUTED))
    render(os.path.join(IMG, "gate-placement.svg"), W, H, *frags,
           title="Де сидить брама авторизації — після завантаження обʼєкта")


def fig_role_matrix():
    """Ролі дому DH → дозволені дії; еволюція від owner-порівняння до ролей."""
    W, H = 1080, 500
    frags = []

    cols = [("читати", 500), ("керувати", 700), ("врядувати", 900)]
    rows = [
        ("гість", 262, [True, False, False]),
        ("сім'я / орендар", 332, [True, True, False]),
        ("засновник", 402, [True, True, True]),
    ]
    frags.append(text(210, 217, "роль дому", size=13, color=MUTED, bold=True))
    for name, x in cols:
        frags.append(text(x, 217, name, size=14, color=INK, bold=True))
    frags.append(line(120, 234, 970, 234, color=MUTED, sw=1.2))
    for rname, ry, cells in rows:
        frags.append(text(210, ry + 5, rname, size=14, color=INK))
        for (_, cx), ok in zip(cols, cells):
            col = FIELD if ok else POS
            bg = GREENBG if ok else REDBG
            frags.append(circle(cx, ry, 15, fill=bg, stroke=col, sw=2))
            frags.append(text(cx, ry + 6, "✓" if ok else "✗", size=17, color=col, bold=True))

    e1, w1, _ = textbox(258, 128, "було: дім = один власник\nsubject.id == home.ownerId",
                        size=12, fill=FILL, stroke=LINE)
    e2, w2, _ = textbox(772, 128, "стало: членство + роль\n(ця таблиця)",
                        size=12, fill=GREENBG, stroke=FIELD)
    frags.append(arrow(258 + w1 / 2, 128, 772 - w2 / 2, 128, color=INK, sw=2))
    frags.extend([e1, e2])

    frags.append(text(W / 2, 464,
                      "Не член дому → жодного рядка в таблиці → відмова за замовчуванням (fail-closed).",
                      size=13, color=MUTED))
    render(os.path.join(IMG, "role-matrix.svg"), W, H, *frags,
           title="Як росте can(): ролі дому DH")


def fig_toctou_window():
    """Вікно між перевіркою права й дією; дві оборони."""
    W, H = 1220, 520
    frags = []
    ay = 196

    frags.append(rect(524, ay - 62, 288, 124, fill=REDBG, stroke=POS, sw=1.4, rx=10))
    frags.append(text(668, ay - 76, "вікно TOCTOU", size=12, color=POS, bold=True))
    frags.append(text(668, ay + 84, "Марта відкликає Олю", size=12, color=POS))

    frags.append(arrow(80, ay, 1150, ay, color=MUTED, sw=2.2))
    frags.append(text(1156, ay + 5, "час →", size=12, color=MUTED, anchor="start"))

    marks = [
        (250, "t0 · завантажили дім\nОля = сім'я", GREENBG, FIELD),
        (468, "t1 · ПЕРЕВІРКА\ncan(Оля, write) = ✓", GREENBG, FIELD),
        (868, "t2 · ДІЯ\napply write", REDBG, POS),
    ]
    for x, s, bg, col in marks:
        frags.append(circle(x, ay, 7, fill=col, stroke=col))
        b, _, h = textbox(x, ay - 128, s, size=12, fill=bg, stroke=col)
        frags.append(line(x, ay - 128 + h / 2, x, ay - 7, color=col, sw=1.4))
        frags.append(b)
    frags.append(text(868, ay + 42, "рішення вже застаріле", size=12, color=POS))

    d1, _, _ = textbox(318, 420, "оборона 1 — той самий обʼєкт:\nне перечитувати за id після перевірки",
                       size=12, fill=FILL, stroke=FIELD)
    d2, _, _ = textbox(858, 420, "оборона 2 — злити перевірку в дію:\n"
                       "UPDATE … WHERE EXISTS(membership …)\nперевірка й дія — один вислів, вікна нема",
                       size=12, fill=GREENBG, stroke=FIELD)
    frags.extend([d1, d2])

    render(os.path.join(IMG, "toctou-window.svg"), W, H, *frags,
           title="TOCTOU: вікно між «перевірили» і «зробили»")


if __name__ == "__main__":
    fig_two_questions()
    fig_once_vs_every()
    fig_conflation_idor()
    fig_three_roots()
    fig_gate_placement()
    fig_role_matrix()
    fig_toctou_window()
    print("OK: two-questions.svg, once-vs-every.svg, conflation-idor.svg, three-roots.svg, "
          "gate-placement.svg, role-matrix.svg, toctou-window.svg")
