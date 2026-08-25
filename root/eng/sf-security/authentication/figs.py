# -*- coding: utf-8 -*-
"""Фігури теми «Автентифікація». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)

REDFILL = "#fdecea"
GRNFILL = "#e7f6ec"
BLUFILL = "#eaf0fd"


# ── 1. Автентифікація vs авторизація: двоє дверей по черзі ────────────────────
def fig_authn_vs_authz():
    W, H = 1020, 360
    f = []

    # відвідувач
    b, bw, bh = textbox(95, 180, "відвідувач", size=13, fill=FILL, stroke=MUTED)
    f.append(b)

    # двері 1 — автентифікація
    b1, w1, h1 = textbox(340, 180, "Двері 1\nАВТЕНТИФІКАЦІЯ\nхто ти?",
                         size=14, fill=BLUFILL, stroke=NEG, sw=2, pad=14)
    f.append(b1)

    # двері 2 — авторизація
    b2, w2, h2 = textbox(630, 180, "Двері 2\nАВТОРИЗАЦІЯ\nщо тобі можна?",
                         size=14, fill=GRNFILL, stroke=FIELD, sw=2, pad=14)
    f.append(b2)

    # стрілки з підписами над ними
    f.append(arrow(150, 180, 340 - w1 / 2 - 8, 180))
    f.append(arrow(340 + w1 / 2 + 8, 180, 630 - w2 / 2 - 8, 180))
    f.append(text((340 + w1 / 2 + 630 - w2 / 2) / 2, 165, "впущено", size=12, color=MUTED))
    f.append(arrow(630 + w2 / 2 + 8, 180, 820, 180))
    f.append(text((630 + w2 / 2 + 8 + 900) / 2, 165, "за правами", size=12, color=MUTED))

    # кімнати праворуч — частина відчинена, частина замкнена
    rooms = [("кабінет", True, 105), ("звіти", False, 180), ("серверна", False, 255)]
    for name, ok, cy in rooms:
        rb, rw, rh = textbox(905, cy, name, size=12, fill=FILL, stroke=LINE)
        f.append(rb)
        if ok:
            f.append(plus(905 - rw / 2 - 16, cy))
        else:
            f.append(minus(905 - rw / 2 - 16, cy))

    render(out("authn-vs-authz.svg"), W, H, *f,
           title="Спершу — хто ти (автентифікація), лише потім — що можна (авторизація)")


# ── 2. Три фактори автентифікації ────────────────────────────────────────────
def fig_three_factors():
    W, H = 1020, 480
    f = []

    cols = [
        (195, "ЗНАЄШ", NEG, BLUFILL,
         "пароль\nPIN\nтаємне питання",
         "можна підгледіти,\nвиманити, підібрати"),
        (510, "МАЄШ", INK, FILL,
         "телефон\nапаратний ключ\nкартка-перепустка",
         "можна вкрасти\nчи загубити"),
        (825, "Є", FIELD, GRNFILL,
         "відбиток\nобличчя\nрайдужка",
         "витік — назавжди,\nвже не зміниш"),
    ]
    for cx, head, col, fill, examples, weak in cols:
        hb, hw, hh = textbox(cx, 92, head, size=16, bold=True, fill=fill, stroke=col, sw=2, pad=14, min_w=150)
        f.append(hb)
        eb, ew, eh = textbox(cx, 210, examples, size=13, fill=FILL, stroke=LINE, pad=12)
        f.append(eb)
        wb, ww, wh = textbox(cx, 330, weak, size=13, fill=REDFILL, stroke=POS, pad=12)
        f.append(wb)

    # підпис-стрілка «слабкість»
    f.append(text(510, 275, "вроджена слабкість кожного:", size=12, color=MUTED))

    # нижня рамка — MFA
    nb, nw, nh = textbox(510, 435,
                         "MFA: вимагай доказів із ДВОХ різних кошиків —\n"
                         "щоб пройти, замало підгледіти пароль, треба ще й тримати телефон",
                         size=13, bold=True, fill=GRNFILL, stroke=FIELD, sw=2, pad=14)
    f.append(nb)

    render(out("three-factors.svg"), W, H, *f,
           title="Три джерела доказу особи — і слабкість у кожного")


# ── 3. Життєвий цикл: вхід один раз, жетон на кожному запиті ──────────────────
def fig_login_to_session():
    W, H = 1020, 470
    f = []

    cx_cl, cx_sv = 200, 820
    # заголовки-акторки
    cb, cbw, cbh = textbox(cx_cl, 66, "Клієнт", size=15, bold=True, fill=FILL, stroke=LINE, min_w=140)
    sb, sbw, sbh = textbox(cx_sv, 66, "Сервер", size=15, bold=True, fill=FILL, stroke=LINE, min_w=140)
    f.append(cb); f.append(sb)

    # лінії життя
    f.append(line(cx_cl, 100, cx_cl, 430, color=MUTED, sw=1.2, dash="5,5"))
    f.append(line(cx_sv, 100, cx_sv, 430, color=MUTED, sw=1.2, dash="5,5"))

    mid = (cx_cl + cx_sv) / 2
    # 1. вхід — пароль
    f.append(text(mid, 138, "1. вхід: пароль (лише один раз)", size=13, color=NEG))
    f.append(arrow(cx_cl, 152, cx_sv, 152, color=NEG))
    # 2. сервер видає жетон
    f.append(text(mid, 202, "2. сервер видає жетон — випадковий секрет", size=13, color=FIELD))
    f.append(arrow(cx_sv, 216, cx_cl, 216, color=FIELD))

    # 3. кожен запит несе жетон (повторювані стрілки)
    f.append(text(mid, 292, "3. далі КОЖЕН запит несе жетон замість пароля", size=13, color=INK))
    for y in (306, 350, 394):
        f.append(arrow(cx_cl, y, cx_sv, y, color=LINE, sw=1.6))
    f.append(text(cx_sv + 20, 358, "(повторюється", size=12, color=MUTED, anchor="start"))
    f.append(text(cx_sv + 20, 376, " щоразу)", size=12, color=MUTED, anchor="start"))

    render(out("login-to-session.svg"), W, H, *f,
           title="Пароль — один раз під час входу; жетон — на кожному запиті")


# ── 4. Спільний секрет проти пари ключів ─────────────────────────────────────
def fig_secret_vs_pubkey():
    W, H = 1120, 520
    f = []

    f.append(line(560, 60, 560, 500, color=MUTED, sw=1.2, dash="6,6"))
    f.append(text(285, 58, "Спільний секрет (пароль)", size=15, bold=True, color=POS))
    f.append(text(840, 58, "Пара ключів (passkey)", size=15, bold=True, color=FIELD))

    # ── ліва панель: пароль ──
    lb, lw, lh = textbox(160, 150, "клієнт\nзнає пароль", size=13, fill=BLUFILL, stroke=NEG, pad=12)
    f.append(lb)
    rb, rw, rh = textbox(410, 150, "сервер\nзберігає хеш", size=13, fill=FILL, stroke=LINE, pad=12)
    f.append(rb)
    f.append(text(285, 120, "секрет тече дротом", size=12, color=POS))
    f.append(arrow(160 + lw / 2 + 6, 150, 410 - rw / 2 - 6, 150, color=POS))

    for i, s in enumerate(["дротом — секрет можна перехопити",
                           "у базі — можна викрасти при зламі",
                           "фішинг — можна виманити в людини"]):
        cy = 250 + i * 60
        f.append(minus(90, cy))
        f.append(text(112, cy + 5, s, size=13, color=INK, anchor="start"))

    # ── права панель: пара ключів ──
    lb2, lw2, lh2 = textbox(720, 150, "пристрій\nзакритий ключ\n(не виходить)", size=13, fill=GRNFILL, stroke=FIELD, pad=12)
    f.append(lb2)
    rb2, rw2, rh2 = textbox(970, 150, "сервер\nвідкритий ключ", size=13, fill=FILL, stroke=LINE, pad=12)
    f.append(rb2)
    f.append(text(845, 120, "дротом іде лише підпис", size=12, color=FIELD))
    f.append(arrow(720 + lw2 / 2 + 6, 150, 970 - rw2 / 2 - 6, 150, color=FIELD))

    for i, s in enumerate(["дротом — нічого придатного до повтору",
                           "у базі — лише відкриті ключі, вони безпечні",
                           "фішинг — підпис прив'язаний до адреси сайту"]):
        cy = 250 + i * 60
        f.append(plus(600, cy))
        f.append(text(622, cy + 5, s, size=13, color=INK, anchor="start"))

    render(out("secret-vs-pubkey.svg"), W, H, *f,
           title="Вроджена вада пароля — спільний секрет; пара ключів прибирає саму спільність")


# ── 5. Хронологія: вада пароля була вбудована від першого дня ─────────────────
def fig_password_timeline():
    W, H = 1000, 680
    f = []
    x_spine = 178
    f.append(line(x_spine, 92, x_spine, 606, color=MUTED, sw=2))

    nodes = [
        (128, "1961", "CTSS у MIT: народжується пароль.\nСписок паролів лежить у ВІДКРИТОМУ файлі.", NEG, BLUFILL),
        (240, "1962", "Аллан Шерр: перша крадіжка.\nДрукує весь файл паролів звичайним запитом.", POS, REDFILL),
        (352, "1966", "Випадковий витік: редактор плутає\nфайл паролів із вітанням — усі бачать усі.", POS, REDFILL),
        (464, "кін. 1960-х", "Multics: однобічне шифрування пароля\n(ідея Джозефа Вайценбаума).", FIELD, GRNFILL),
        (576, "1979", "UNIX: Морріс і Томпсон додають сіль\nі навмисно повільний хеш (crypt).", FIELD, GRNFILL),
    ]
    box_cx = 610
    for cy, year, label, col, fill in nodes:
        b, w, h = textbox(box_cx, cy, label, size=13, fill=fill, stroke=col, sw=1.8, pad=13)
        f.append(line(x_spine + 9, cy, box_cx - w / 2, cy, color=MUTED, sw=1.3))
        f.append(b)
        f.append(circle(x_spine, cy, 9, fill=fill, stroke=col, sw=2.6))
        f.append(text(x_spine - 26, cy + 5, year, size=15, color=col, bold=True, anchor="end"))

    render(out("password-timeline.svg"), W, H, *f,
           title="Пароль: вада спільного секрета була вбудована від першого дня")


# ── 6. Перелічення користувачів: час відповіді зраджує акаунт ─────────────────
def fig_enum_timing():
    W, H = 1120, 620
    f = []
    X0 = 320            # t = 0, початок обробки запиту
    look = 24           # ширина сегмента «пошук у БД»
    argon = 430         # ширина сегмента «argon2»

    def bar(y, label, segs, tail, tailcol=MUTED):
        f.append(text(X0 - 22, y + 5, label, size=13, color=INK, anchor="end", bold=True))
        x = X0
        for w, fill, stroke, name in segs:
            f.append(rect(x, y - 17, w, 34, fill=fill, stroke=stroke, sw=1.5))
            if w > 70:
                f.append(text(x + w / 2, y + 5, name, size=12, color=INK))
            x += w
        f.append(line(x, y - 27, x, y + 27, color=tailcol, sw=1.2))
        f.append(text(x + 10, y + 5, tail, size=13, color=tailcol, anchor="start", bold=True))
        return x

    # верхня панель — наївно (витік)
    f.append(text(W / 2, 62, "Наївно: час відповіді виказує, чи існує акаунт",
                  size=15, bold=True, color=POS))
    y1, y2 = 122, 186
    e1 = bar(y1, "акаунт Є",
             [(look, FILL, LINE, "пошук"), (argon, BLUFILL, NEG, "argon2 — перевірка хешу")],
             "≈ 200 мс")
    e2 = bar(y2, "акаунта НЕМА",
             [(look, FILL, LINE, "пошук")],
             "≈ 5 мс", tailcol=POS)
    f.append(line(e2, y2 + 17, e2, 262, color=POS, sw=1.2, dash="4,4"))
    f.append(line(e1, y1 + 17, e1, 262, color=POS, sw=1.2, dash="4,4"))
    f.append(arrow(e2 + 4, 250, e1 - 4, 250, color=POS))
    f.append(text((e1 + e2) / 2, 284, "розрив у часі → акаунт існує", size=13, color=POS, bold=True))

    # нижня панель — захищено (вирівняно)
    f.append(text(W / 2, 372, "Захищено: фіктивний хеш вирівнює час",
                  size=15, bold=True, color=FIELD))
    y3, y4 = 432, 496
    b1 = bar(y3, "акаунт Є",
             [(look, FILL, LINE, "пошук"), (argon, BLUFILL, NEG, "argon2 — перевірка хешу")],
             "≈ 200 мс")
    b2 = bar(y4, "акаунта НЕМА",
             [(look, FILL, LINE, "пошук"), (argon, GRNFILL, FIELD, "argon2 — проти ФІКТИВНОГО хешу")],
             "≈ 200 мс", tailcol=FIELD)
    f.append(line(b1, y3 - 17, b1, 540, color=FIELD, sw=1.2, dash="4,4"))
    f.append(text((X0 + b1) / 2, 562, "час однаковий → існування акаунта не витікає",
                  size=13, color=FIELD, bold=True))

    render(out("enum-timing.svg"), W, H, *f,
           title="Перелічення користувачів: як час зраджує акаунт — і як його вирівняти")


# ── 7. Два хеші, дві протилежні задачі ───────────────────────────────────────
def fig_two_hashes():
    W, H = 1180, 540
    f = []
    xL, xR = 640, 980       # центри колонок значень
    xlab = 300              # права межа підписів рядків (anchor end)

    hb1, _, _ = textbox(xL, 96, "ПАРОЛЬ", size=16, bold=True,
                        fill=BLUFILL, stroke=NEG, sw=2, pad=14, min_w=230)
    hb2, _, _ = textbox(xR, 96, "ТОКЕН СЕСІЇ", size=16, bold=True,
                        fill=GRNFILL, stroke=FIELD, sw=2, pad=14, min_w=230)
    f.append(hb1)
    f.append(hb2)

    rows = [
        (190, "ентропія секрету", "≈ 38 бітів\n(вигадала людина)", "128 бітів\n(CSPRNG)"),
        (280, "хеш-функція", "argon2id —\nнавмисно ПОВІЛЬНА", "SHA-256 —\nшвидка"),
        (370, "сіль", "так —\nпроти райдужних таблиць", "не треба —\nвже випадковий"),
        (460, "навіщо хешуємо", "щоб перебір\nкоштував часу", "щоб витік БД не\nвіддав живих сесій"),
    ]
    for y, lab, v1, v2 in rows:
        f.append(text(xlab, y + 5, lab, size=13, bold=True, color=INK, anchor="end"))
        b1, _, _ = textbox(xL, y, v1, size=12, fill=FILL, stroke=LINE, pad=11, min_w=230)
        b2, _, _ = textbox(xR, y, v2, size=12, fill=FILL, stroke=LINE, pad=11, min_w=230)
        f.append(b1)
        f.append(b2)

    render(out("two-hashes.svg"), W, H, *f,
           title="Два хеші, дві задачі: повільний — на пароль, швидкий — на токен")


if __name__ == "__main__":
    fig_authn_vs_authz()
    fig_three_factors()
    fig_login_to_session()
    fig_secret_vs_pubkey()
    fig_password_timeline()
    fig_enum_timing()
    fig_two_hashes()
    print("OK: 7 фігур згенеровано в", IMG)
