# -*- coding: utf-8 -*-
"""Фігури до теми «SIP: сигналізація сеансів зв'язку»."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SOFT = "#eef3fb"
WARM = "#fdf3e6"


def box(cx, cy, s, size=13, fill=FILL, bold=False):
    body, w, h = textbox(cx, cy, s, size=size, fill=fill, bold=bold)
    return body, w / 2.0, h / 2.0


# ─────────────────────────────────────────────────────────────────────────────
# 1. Побачення: реєстрація пише адресу під іменем, виклик роздвоюється,
#    медіа йде повз сервери.
# ─────────────────────────────────────────────────────────────────────────────
def fig_rendezvous():
    W, H = 1000, 580
    f = []

    # ── панель «реєстрація» ──────────────────────────────────────────────
    f.append(rect(30, 30, 940, 200, fill=SOFT, stroke="#c8d6ea", sw=1.2, rx=10))
    f.append(text(50, 58, "Спершу — реєстрація: ім'я дізнається, де апарат зараз",
                  size=13, color=MUTED, anchor="start", bold=True))

    d1, d1w, d1h = box(170, 110, "Настільний телефон\n198.51.100.9:5060", size=12)
    d2, d2w, d2h = box(170, 185, "Ноутбук Олени\n203.0.113.7:41055", size=12)
    rg, rgw, rgh = box(520, 148, "Реєстратор\nexample.com", size=13)
    db, dbw, dbh = box(830, 148,
                       "sip:olena@example.com\n→ 198.51.100.9:5060\n→ 203.0.113.7:41055",
                       size=11, fill="#ffffff")
    f += [d1, d2, rg, db]

    f.append(arrow(170 + d1w, 112, 520 - rgw, 138))
    f.append(arrow(170 + d2w, 183, 520 - rgw, 160))
    f.append(text(345, 100, "REGISTER", size=12))
    f.append(text(345, 200, "REGISTER", size=12))
    f.append(arrow(520 + rgw, 148, 830 - dbw, 148))
    f.append(text(690, 134, "два записи під", size=11, color=MUTED))
    f.append(text(690, 176, "одним іменем", size=11, color=MUTED))

    # ── панель «виклик» ──────────────────────────────────────────────────
    f.append(rect(30, 258, 940, 292, fill=WARM, stroke="#e6d3b3", sw=1.2, rx=10))
    f.append(text(50, 286, "Потім — виклик: одне ім'я, два апарати, пряме медіа",
                  size=13, color=MUTED, anchor="start", bold=True))

    ca, caw, cah = box(140, 392, "Богдан", size=13)
    px, pxw, pxh = box(455, 352, "Проксі\nexample.com", size=13)
    p1, p1w, p1h = box(810, 330, "Настільний\nтелефон", size=12)
    p2, p2w, p2h = box(810, 440, "Ноутбук", size=12)
    f += [ca, px, p1, p2]

    f.append(arrow(140 + caw, 384, 455 - pxw, 366))
    f.append(text(300, 330, "INVITE sip:olena@example.com", size=12))
    f.append(arrow(455 + pxw, 342, 810 - p1w, 330))
    f.append(arrow(455 + pxw, 366, 810 - p2w, 425))
    f.append(text(630, 312, "INVITE", size=12))
    f.append(text(620, 418, "INVITE", size=12))
    f.append(text(660, 470, "дзвонять обидва; хто відповість", size=11, color=MUTED))
    f.append(text(660, 488, "перший — забирає дзвінок", size=11, color=MUTED))

    # медіа — низом, повз проксі
    my = 528
    f.append(line(140, 392 + cah, 140, my, color=POS, sw=2.6))
    f.append(line(140, my, 810, my, color=POS, sw=2.6))
    f.append(arrow(810, my, 810, 440 + p2h + 4, color=POS, sw=2.6))
    f.append(text(430, my - 12, "RTP: медіа тече напряму, проксі його не бачить",
                  size=12, color=POS))

    render(os.path.join(OUT, 'rendezvous.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 2. Дві шкали стану: транзакція (запит + його відповіді) і діалог
#    (стосунок, що живе від 200 OK до BYE).
# ─────────────────────────────────────────────────────────────────────────────
def fig_ladder():
    W, H = 1080, 640
    f = []
    xa, xp, xb = 150, 440, 730
    top, bot = 92, 600

    for x, name in ((xa, "Богдан"), (xp, "Проксі"), (xb, "Олена")):
        b, _, _ = box(x, 52, name, size=13, bold=True)
        f.append(b)
        f.append(line(x, top - 12, x, bot, color=MUTED, sw=1.2, dash="5,5"))

    def msg(y, x1, x2, label, color=INK):
        f.append(arrow(x1, y, x2, y, color=color))
        f.append(text((x1 + x2) / 2.0, y - 9, label, size=12, color=color))

    msg(132, xa, xp, "INVITE (пропозиція SDP)")
    msg(160, xp, xb, "INVITE")
    msg(196, xp, xa, "100 Trying")
    msg(238, xb, xp, "180 Ringing")
    msg(266, xp, xa, "180 Ringing")
    msg(318, xb, xp, "200 OK (відповідь SDP)")
    msg(346, xp, xa, "200 OK")
    msg(392, xa, xb, "ACK — повз проксі, прямо за Contact")

    f.append(line(xa, 434, xb, 434, color=POS, sw=2.6))
    f.append(line(xa, 470, xb, 470, color=POS, sw=2.6))
    f.append(text((xa + xb) / 2.0, 458, "потік RTP в обидва боки", size=12, color=POS))

    msg(520, xb, xa, "BYE")
    msg(556, xa, xb, "200 OK")

    def bracket(x, y1, y2, tick=11):
        return (line(x, y1, x, y2, color=MUTED, sw=1.4) +
                line(x - tick, y1, x, y1, color=MUTED, sw=1.4) +
                line(x - tick, y2, x, y2, color=MUTED, sw=1.4))

    f.append(bracket(800, 122, 356))
    f.append(mtext(816, 226, ["транзакція INVITE:", "один запит і всі", "його відповіді"],
                   size=11, color=MUTED, anchor="start"))
    f.append(bracket(800, 382, 402))
    f.append(mtext(816, 396, ["ACK — окрема", "транзакція"], size=11, color=MUTED,
                   anchor="start"))
    f.append(bracket(800, 510, 566))
    f.append(mtext(816, 544, ["транзакція BYE"], size=11, color=MUTED, anchor="start"))

    f.append(bracket(1010, 338, 530, tick=13))
    f.append(mtext(1026, 416, ["діалог:", "живе від", "200 OK", "до BYE"],
                   size=11, color=INK, anchor="start", lh=1.35))

    render(os.path.join(OUT, 'transaction-dialog.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Via: відповідь іде не за адресою, а за слідом, який запит лишив по дорозі.
# ─────────────────────────────────────────────────────────────────────────────
def fig_via():
    W, H = 1000, 420
    f = []
    xs = [110, 380, 650, 900]
    names = ["Богдан", "Проксі A", "Проксі B", "Олена"]
    halfs = []
    for x, n in zip(xs, names):
        b, hw, hh = box(x, 70, n, size=13, bold=True)
        f.append(b)
        halfs.append(hw)

    # запит іде вправо, стос Via росте
    for i in range(3):
        f.append(arrow(xs[i] + halfs[i], 70, xs[i + 1] - halfs[i + 1], 70))

    stacks = [["Via: Богдан"],
              ["Via: Проксі A", "Via: Богдан"],
              ["Via: Проксі B", "Via: Проксі A", "Via: Богдан"]]
    for i, st in enumerate(stacks):
        cx = (xs[i] + xs[i + 1]) / 2.0
        b, _, _ = box(cx, 168, "\n".join(st), size=11, fill="#ffffff")
        f.append(b)
        f.append(line(cx, 92, cx, 132, color=MUTED, sw=1.1, dash="4,4"))

    f.append(text(500, 232,
                  "Кожен вузол дописує свій рядок Via зверху — запит несе власний слід",
                  size=12, color=MUTED))

    # відповідь іде вліво, стос тане
    y = 300
    for i in (2, 1, 0):
        f.append(arrow(xs[i + 1] - halfs[i + 1], y, xs[i] + halfs[i], y, color=NEG))
    f.append(text(500, 288,
                  "Відповідь нікуди не адресують: знімають верхній Via — він і каже, кому далі",
                  size=12, color=NEG))

    f.append(text(500, 360,
                  "Тому проксі може не пам'ятати нічого: адреса зворотного шляху їде в самому повідомленні",
                  size=12, color=INK))

    render(os.path.join(OUT, 'via-stack.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 4. Історія: від запрошень на MBone-конференції до сигналізації IMS.
# ─────────────────────────────────────────────────────────────────────────────
def fig_birth_timeline():
    W, H = 1180, 470
    f = []
    axis_y = 250

    marks = [
        (110, "1996, лютий",
         "Дві чернетки MMUSIC:\nSIP (запрошення на MBone)\nі SCIP", "up"),
        (330, "1996, грудень",
         "Злиття у SIP версії 2:\nURL, заголовки, коди —\nвигляд як у HTTP", "down"),
        (560, "1999, березень",
         "RFC 2543:\nперший стандарт,\n153 сторінки", "up"),
        (790, "2000, листопад",
         "3GPP бере SIP\nсигналізацією IMS\n(пленарна сесія — грудень)", "down"),
        (1050, "2002, червень",
         "RFC 3261 і супутні\n3262 · 3263 · 3264 · 3265", "up"),
    ]

    f.append(line(60, axis_y, W - 40, axis_y, sw=2.5))

    for x, when, what, side in marks:
        f.append(circle(x, axis_y, 8, fill="#ffffff", sw=2.5))
        if side == "up":
            f.append(line(x, axis_y - 8, x, axis_y - 46, color=MUTED, sw=1.4))
            f.append(text(x, axis_y - 56, when, size=13, bold=True))
            body, w, h = textbox(x, axis_y - 130, what, size=12, fill=SOFT)
            f.append(body)
        else:
            f.append(line(x, axis_y + 8, x, axis_y + 46, color=MUTED, sw=1.4))
            f.append(text(x, axis_y + 62, when, size=13, bold=True))
            body, w, h = textbox(x, axis_y + 136, what, size=12, fill=WARM,
                                 stroke="#e6d3b3")
            f.append(body)

    f.append(text(60, axis_y - 200,
                  "Конференції в дослідницькій мережі",
                  size=13, color=MUTED, anchor="start", bold=True))
    f.append(text(W - 40, axis_y + 218,
                  "Телефонія операторів",
                  size=13, color=MUTED, anchor="end", bold=True))

    render(os.path.join(OUT, 'sip-timeline.svg'), W, H, *f)




# ─────────────────────────────────────────────────────────────────────────────
# 5. Клієнтська транзакція INVITE: стани й таймери (до вставки proj-).
# ─────────────────────────────────────────────────────────────────────────────
def fig_invite_fsm():
    W, H = 980, 615
    f = []

    st_c, cw, ch = box(175, 210, "Calling\nзапит у польоті", size=13, fill=WARM)
    st_p, pw, ph = box(480, 210, "Proceeding\nтелефон дзвонить", size=13, fill=SOFT)
    st_t, tw, th = box(830, 210, "Terminated\nстан звільнено", size=13)
    st_m, mw, mh = box(470, 430, "Completed\nдублі поглинаються", size=13, fill=SOFT)
    f += [st_c, st_p, st_t, st_m]

    # вхід у автомат
    f.append(arrow(45, 210, 175 - cw, 210))
    f.append(text((45 + 175 - cw) / 2, 194, "INVITE", size=11))

    # петля таймера A над станом Calling
    f.append(line(205, 210 - ch, 205, 140))
    f.append(line(205, 140, 145, 140))
    f.append(arrow(145, 140, 145, 210 - ch))
    f.append(text(175, 121, "таймер A: повтор, інтервал ×2", size=11, color=MUTED))

    # Calling → Proceeding
    f.append(arrow(175 + cw, 210, 480 - pw, 210))
    f.append(text((175 + cw + 480 - pw) / 2, 193, "1xx: повтори спиняються", size=11))

    # Proceeding → Terminated (2xx)
    xm = (480 + pw + 830 - tw) / 2
    f.append(arrow(480 + pw, 210, 830 - tw, 210))
    f.append(text(xm, 193, "2xx: транзакція гине одразу", size=11))
    f.append(text(xm, 236, "ACK шле TU окремою транзакцією", size=11, color=MUTED))

    # Calling → Completed і Proceeding → Completed
    f.append(arrow(175, 210 + ch, 400, 430 - mh))
    f.append(mtext(310, 352, ["300–699", "шлемо ACK"], size=11, anchor="end"))
    f.append(arrow(470, 210 + ph, 470, 430 - mh))
    f.append(mtext(492, 300, ["300–699", "шлемо ACK"], size=11, anchor="start"))

    # Completed → Terminated (таймер D)
    f.append(arrow(470 + mw, 415, 796, 210 + th))
    f.append(text(700, 400, "таймер D: 32 с", size=11, anchor="start"))

    # Calling → Terminated (таймер B), обхідним шляхом низом
    f.append(line(140, 210 + ch, 140, 545))
    f.append(line(140, 545, 830, 545))
    f.append(arrow(830, 545, 830, 210 + th))
    f.append(text(455, 527,
                  "таймер B: 64·T1 = 32 с — здача; нормативно лише зі стану Calling",
                  size=11, color=MUTED))

    f.append(text(45, 587,
                  "З Proceeding нормативного виходу за часом немає: дзвонити можна довго — "
                  "межу кладуть CANCEL від TU або таймер C на проксі",
                  size=11, color=MUTED, anchor="start"))

    render(os.path.join(OUT, 'invite-fsm.svg'), W, H, *f)


# ─────────────────────────────────────────────────────────────────────────────
# 6. Два різні ACK: до 300–699 і до 2xx (до вставки proj-).
# ─────────────────────────────────────────────────────────────────────────────
def fig_two_acks():
    W, H = 1020, 575
    f = []

    f.append(rect(30, 40, 460, 500, fill=SOFT, stroke="#c8d6ea", sw=1.2, rx=10))
    f.append(rect(530, 40, 460, 500, fill=WARM, stroke="#e6d3b3", sw=1.2, rx=10))
    f.append(text(45, 72, "Відповідь 300–699: ACK робить сама транзакція",
                  size=12, color=MUTED, anchor="start", bold=True))
    f.append(text(545, 72, "Відповідь 2xx: ACK робить TU — окрема транзакція",
                  size=12, color=MUTED, anchor="start", bold=True))

    for x, name in ((95, "Богдан"), (260, "Проксі"), (425, "Олена"),
                    (595, "Богдан"), (760, "Проксі"), (925, "Олена")):
        f.append(text(x, 105, name, size=12, bold=True))
        f.append(line(x, 115, x, 385, color=MUTED, sw=1.2))

    def msg(xa, xb, y, label, muted=False):
        col = MUTED if muted else LINE
        return [arrow(xa, y, xb, y, color=col),
                text((xa + xb) / 2, y - 14, label, size=11, color=col)]

    f += msg(95, 260, 155, "INVITE")
    f += msg(260, 425, 185, "INVITE")
    f += msg(425, 260, 240, "486 Busy Here")
    f += msg(260, 95, 270, "486 Busy Here")
    f += msg(95, 260, 325, "ACK (той самий branch)")
    f += msg(260, 425, 355, "ACK")

    f += msg(595, 760, 155, "INVITE")
    f += msg(760, 925, 185, "INVITE")
    f += msg(925, 760, 240, "200 OK")
    f += msg(760, 595, 270, "200 OK")
    f += msg(925, 760, 310, "200 OK (повтор)", muted=True)
    f += msg(760, 595, 340, "200 OK (повтор)", muted=True)
    f.append(arrow(595, 375, 925, 375))
    f.append(text(672, 361, "ACK — новий branch", size=11))

    nb1, _, _ = textbox(260, 445,
                        "ACK летить тим самим ланцюгом і несе той самий branch:\n"
                        "він належить транзакції INVITE",
                        size=11, fill="#ffffff")
    nb2, _, _ = textbox(760, 445,
                        "ACK іде прямо на Contact і несе НОВИЙ branch —\n"
                        "це окрема транзакція; поки він не дійде, 200 повторюється",
                        size=11, fill="#ffffff")
    f += [nb1, nb2]

    render(os.path.join(OUT, 'two-acks.svg'), W, H, *f)


if __name__ == '__main__':
    fig_rendezvous()
    fig_ladder()
    fig_via()
    fig_birth_timeline()
    fig_invite_fsm()
    fig_two_acks()
    print("ok")
