# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)


def fig_roundtrips():
    """Дрібнозернистий виклик (N звернень по мережі) проти одного DTO."""
    W, H = 760, 360
    frags = []
    frags.append(text(W / 2, 28, "Чому DTO: зменшити кількість перетинів межі", size=17, bold=True))

    # ліва колонка — багато дрібних викликів
    cxL = 190
    b1, _, _ = textbox(cxL, 90, "клієнт", size=14, bold=True, min_w=150)
    b2, _, _ = textbox(cxL, 300, "сервер\n(інший процес)", size=13, min_w=200)
    frags += [b1, b2]
    labels = ["getName()", "getEmail()", "getPhone()", "getAddress()"]
    for i, lab in enumerate(labels):
        yy = 130 + i * 34
        frags.append(arrow(cxL - 30, yy, cxL + 30, yy, color=POS))
        frags.append(text(cxL, yy - 6, lab, size=11, color=MUTED))
    frags.append(text(cxL, 340, "4 перетини межі — 4× латентність", size=12, color=POS, bold=True))

    # права колонка — один виклик з DTO
    cxR = 570
    b3, _, _ = textbox(cxR, 90, "клієнт", size=14, bold=True, min_w=150)
    b4, _, _ = textbox(cxR, 300, "сервер\n(інший процес)", size=13, min_w=200)
    frags += [b3, b4]
    frags.append(arrow(cxR - 30, 200, cxR + 30, 200, color=FIELD, sw=2.4))
    bd, _, _ = textbox(cxR, 165, "один DTO:\nname · email\nphone · address", size=12,
                       fill="#eafaf1", stroke=FIELD)
    frags.append(bd)
    frags.append(text(cxR, 340, "1 перетин межі — усі поля разом", size=12, color=FIELD, bold=True))

    # роздільник
    frags.append(line(W / 2, 60, W / 2, 340, color=MUTED, sw=1, dash="4 4"))
    render(os.path.join(IMG, "roundtrips.svg"), W, H, *frags)


def fig_boundary():
    """Домен усередині, DTO на межі, перекладач між ними."""
    W, H = 780, 340
    frags = []
    frags.append(text(W / 2, 28, "DTO живе на межі, домен — усередині", size=17, bold=True))

    # внутрішнє ядро (домен)
    core, _, _ = textbox(180, 190, "Модель домену\n\nOrder\nповедінка + правила\nінваріанти", size=13,
                         fill="#eafaf1", stroke=FIELD, min_w=230)
    frags.append(core)
    frags.append(text(180, 300, "багата, з поведінкою", size=12, color=FIELD))

    # межа (пунктир)
    frags.append(line(400, 70, 400, 300, color=MUTED, sw=1.5, dash="5 5"))
    frags.append(text(400, 60, "межа процесу", size=12, color=MUTED, bold=True))

    # зовнішнє (DTO)
    dto, _, _ = textbox(640, 190, "DTO\n\nOrderDto\nсамі поля\nбез поведінки", size=13,
                        fill="#f4f6f8", stroke=LINE, min_w=210)
    frags.append(dto)
    frags.append(text(640, 300, "пласка, серіалізовна", size=12, color=MUTED))

    # перекладач-стрілки крізь межу
    frags.append(arrow(300, 165, 535, 165, color=INK))
    frags.append(text(417, 155, "збірка", size=11, color=INK))
    frags.append(arrow(535, 215, 300, 215, color=INK))
    frags.append(text(417, 235, "розбір", size=11, color=INK))
    render(os.path.join(IMG, "boundary.svg"), W, H, *frags)


def fig_versions():
    """Одна межа-DTO розв'язує дві сторони: кожна еволюціонує окремо."""
    W, H = 760, 300
    frags = []
    frags.append(text(W / 2, 28, "DTO як контракт: сторони міняються нарізно", size=17, bold=True))

    # сервер
    s, _, _ = textbox(160, 150, "внутрішня\nмодель сервера\n(вільно переписуй)", size=13,
                      fill="#eafaf1", stroke=FIELD, min_w=220)
    frags.append(s)
    # контракт
    c, _, _ = textbox(400, 150, "DTO-контракт\n{ id, total,\n  items[] }", size=13,
                      fill="#fff7e6", stroke="#d68910", min_w=180)
    frags.append(c)
    # клієнт
    cl, _, _ = textbox(640, 150, "клієнт\n(читає лише\nпотрібні поля)", size=13,
                       fill="#f4f6f8", stroke=LINE, min_w=190)
    frags.append(cl)

    frags.append(arrow(270, 150, 310, 150, color=MUTED))
    frags.append(arrow(490, 150, 545, 150, color=MUTED))
    frags.append(text(W / 2, 250, "стабільна форма посередині тримає обидві сторони незалежними",
                      size=12, color=MUTED))
    render(os.path.join(IMG, "contract.svg"), W, H, *frags)


def fig_hist_timeline():
    """Часова смуга: чотири дати, за які пакунок полів двічі змінив ім'я."""
    W, H = 940, 380
    frags = []
    frags.append(text(W / 2, 30, "Як плаский пакунок полів двічі змінив ім'я", size=17, bold=True))

    # вісь часу
    axy = 150
    x0, x1 = 90, W - 60
    frags.append(arrow(x0, axy, x1, axy, color=INK, sw=2))
    frags.append(text(x1, axy - 12, "час", size=12, color=MUTED))

    # чотири події: (x, рік, текст, колір, вниз/вгору)
    events = [
        (170, "1998", "EJB / RMI:\nдрібнозернисті\nвіддалені виклики\nповзуть", MUTED, +1),
        (400, "2001", "Core J2EE, 1-ше вид.:\nпакунок названо\nValue Object", POS, -1),
        (640, "2002", "Fowler, PoEAA:\nзакріплено\nData Transfer Object;\nсвій Value Object —\nмаленький Money", FIELD, +1),
        (860, "2003", "Core J2EE, 2-ге вид.:\nперейменовано на\nTransfer Object", INK, -1),
    ]
    for x, year, txt, col, dir in events:
        frags.append(circle(x, axy, 7, fill=BG, stroke=col, sw=2.4))
        frags.append(text(x, axy + (-16 if dir < 0 else 22), year, size=14, bold=True, color=col))
        if dir < 0:
            bx, _, _ = textbox(x, axy - 78, txt, size=11, min_w=150, stroke=col)
        else:
            bx, _, _ = textbox(x, axy + 92, txt, size=11, min_w=150, stroke=col)
        frags.append(bx)

    # зіткнення значень слова Value Object між 2001 і 2002
    frags.append(line(400, axy - 20, 400, axy - 40, color=POS, sw=1.2, dash="3 3"))
    frags.append(line(640, axy + 20, 640, axy + 44, color=FIELD, sw=1.2, dash="3 3"))
    frags.append(text(W / 2, H - 18,
                      "зіткнення 2001↔2002: слово «Value Object» уже означало інше — маленький незмінний тип",
                      size=12, color=MUTED, italic=True))
    render(os.path.join(IMG, "hist-timeline.svg"), W, H, *frags)


def fig_hist_localdto():
    """Коли DTO виправданий, а коли — зайвий податок."""
    W, H = 820, 400
    frags = []
    frags.append(text(W / 2, 30, "Одна межа-DTO: коли платити, коли ні", size=17, bold=True))

    # ЛІВОРУЧ: справжня межа — DTO виправданий
    lx = 220
    a, _, _ = textbox(lx, 110, "клієнт", size=13, bold=True, min_w=140)
    b, _, _ = textbox(lx, 300, "чужий процес\n/ мережа / черга", size=12, min_w=200)
    frags += [a, b]
    frags.append(line(lx, 150, lx, 268, color=MUTED, sw=1.4, dash="5 5"))
    frags.append(text(lx - 96, 145, "справжня межа процесу", size=11, color=MUTED, anchor="start"))
    frags.append(arrow(lx, 158, lx, 262, color=FIELD, sw=2.6))
    frags.append(text(lx + 92, 212, "DTO", size=12, bold=True, color=FIELD))
    frags.append(text(lx, 344, "DTO виправданий:", size=12, color=FIELD, bold=True))
    frags.append(text(lx, 362, "купує швидкодію й розв'язку", size=11, color=FIELD))

    # роздільник
    frags.append(line(W / 2, 60, W / 2, 366, color=LINE, sw=1, dash="2 4"))

    # ПРАВОРУЧ: немає межі — DTO зайвий
    rx = 600
    c, _, _ = textbox(rx, 110, "виклик A", size=13, bold=True, min_w=140)
    d, _, _ = textbox(rx, 300, "виклик B\n(той самий процес)", size=12, min_w=200)
    frags += [c, d]
    # перекреслена стрілка DTO (напис — праворуч, поза зоною перекреслення)
    frags.append(arrow(rx, 158, rx, 262, color=MUTED, sw=2.6))
    frags.append(line(rx - 22, 232, rx + 22, 188, color=POS, sw=3))
    frags.append(text(rx + 92, 212, "DTO", size=12, bold=True, color=MUTED))
    frags.append(text(rx, 344, "DTO зайвий:", size=12, color=POS, bold=True))
    frags.append(text(rx, 362, "сама ціна, нуль користі", size=11, color=POS))

    frags.append(text(W / 2, H - 14,
                      "«Перший закон: не розподіляй свої об'єкти» — М. Фаулер, PoEAA",
                      size=12, color=INK, italic=True))
    render(os.path.join(IMG, "hist-localdto.svg"), W, H, *frags)


def fig_assembler():
    """Перекладач-складач третьою стороною: домен і DTO не знають одне про одного."""
    W, H = 820, 340
    frags = []
    frags.append(text(W / 2, 30, "Перекладач знає про обидва боки; краї — ні про кого", size=16, bold=True))

    ay = 175
    # лівий край — домен
    dom, _, _ = textbox(150, ay, "Домен\n\nOrder\nправила\nінваріанти", size=13,
                        fill="#eafaf1", stroke=FIELD, min_w=190)
    frags.append(dom)
    frags.append(text(150, 300, "не знає про DTO", size=12, color=FIELD))

    # правий край — DTO
    dto, _, _ = textbox(670, ay, "OrderDto\n\nпласкі поля\nбез поведінки", size=13,
                        fill="#f4f6f8", stroke=LINE, min_w=190)
    frags.append(dto)
    frags.append(text(670, 300, "не знає про домен", size=12, color=MUTED))

    # центр — складач
    asm, _, _ = textbox(410, ay, "Assembler\n(перекладач)", size=14, bold=True,
                        fill="#fff7e6", stroke="#d68910", min_w=200)
    frags.append(asm)
    frags.append(text(410, 296, "єдиний, хто знає про обидва боки", size=12, color="#b9770e"))

    # стрілки повз написи: fromDto (у домен) і toDto (у DTO)
    frags.append(arrow(300, ay + 22, 250, ay + 22, color=INK))
    frags.append(text(275, ay + 44, "fromDto: митниця", size=11, color=INK))
    frags.append(arrow(520, ay - 22, 570, ay - 22, color=INK))
    frags.append(text(545, ay - 32, "toDto: показ", size=11, color=INK))

    render(os.path.join(IMG, "assembler.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_roundtrips()
    fig_boundary()
    fig_versions()
    fig_hist_timeline()
    fig_hist_localdto()
    fig_assembler()
    print("ok")
