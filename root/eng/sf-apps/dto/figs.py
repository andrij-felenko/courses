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


def fig_cost_regimes():
    """Ціна межі — долина, а не схил: стіна латентності ліворуч, стіна пропускної праворуч."""
    W, H = 820, 440
    frags = []
    frags.append(text(W / 2, 30, "Ціна межі має долину: «більше за раз» краще лише до дна", size=16, bold=True))

    # осі
    ox, oy = 110, 360           # початок координат
    frags.append(arrow(ox, oy, 750, oy, color=INK, sw=2))      # вісь X
    frags.append(arrow(ox, oy, ox, 90, color=INK, sw=2))       # вісь Y
    frags.append(text(430, 398, "дані за один перетин межі →", size=12, color=MUTED))
    frags.append(text(ox + 6, 84, "загальний час", size=11, color=MUTED, anchor="start"))

    # крива-долина: y = ybottom - a*(x-x0)^2 (у екранних координатах низ долини = велике y)
    x0, ybottom, a = 410, 300, 0.0023
    pts = []
    x = 155
    while x <= 685:
        y = ybottom - a * (x - x0) ** 2
        pts.append("%.1f,%.1f" % (x, y))
        x += 20
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), INK))
    frags.append(circle(x0, ybottom, 5, fill=FIELD, stroke=FIELD))   # дно долини

    # ліва стіна — надто дрібно
    lb, _, _ = textbox(215, 122, "надто дрібно:\nбагато перетинів,\nстіна латентності",
                       size=11, stroke=POS, min_w=150)
    frags.append(lb)
    # права стіна — надто грубо
    rb, _, _ = textbox(620, 118, "надто грубо:\nнадвибірка,\nстіна пропускної\nздатності",
                       size=11, stroke=POS, min_w=150)
    frags.append(rb)
    # дно — золота середина
    mb, _, _ = textbox(410, 208, "золота середина:\nрівно потрібні поля",
                       size=11, stroke=FIELD, fill="#eafaf1", min_w=160)
    frags.append(mb)
    frags.append(arrow(x0, 236, x0, 291, color=FIELD, sw=2))   # стрілка від підпису до дна

    render(os.path.join(IMG, "cost-regimes.svg"), W, H, *frags)


def fig_evolution():
    """Розширення-звуження: нове поле поруч зі старим, тоді старе прибирається, слот резервується."""
    W, H = 940, 390
    frags = []
    frags.append(text(W / 2, 28, "Розширення-звуження: змінити форму, нікого не зламавши", size=16, bold=True))

    # вісь часу
    frags.append(arrow(110, 66, 845, 66, color=INK, sw=1.8))
    frags.append(text(840, 58, "версії в часі →", size=11, color=MUTED, anchor="end"))

    cols = [185, 400, 615, 830]
    for cx, name in zip(cols, ["v1", "v2", "v3", "v4"]):
        frags.append(text(cx, 96, name, size=14, bold=True, color=INK))

    # верхній слот (#2: поле name) і нижній слот (#5: поле fullName) — по колонках
    TOP, BOT = 155, 252
    # v1: лише name
    b, _, _ = textbox(cols[0], TOP, "name", size=13, min_w=150); frags.append(b)
    # v2: name живий + fullName нове
    b, _, _ = textbox(cols[1], TOP, "name", size=13, min_w=150); frags.append(b)
    b, _, _ = textbox(cols[1], BOT, "fullName\n← нове", size=12, fill="#eafaf1", stroke=FIELD, min_w=150); frags.append(b)
    # v3: name застаріле + fullName
    b, _, _ = textbox(cols[2], TOP, "name\n(застаріле)", size=12, stroke=MUTED, color=MUTED, min_w=150); frags.append(b)
    b, _, _ = textbox(cols[2], BOT, "fullName", size=13, min_w=150); frags.append(b)
    # v4: reserved слот + fullName
    b, _, _ = textbox(cols[3], TOP, "reserved #2", size=12, fill="#fdecea", stroke=POS, color=POS, min_w=150); frags.append(b)
    b, _, _ = textbox(cols[3], BOT, "fullName", size=13, min_w=150); frags.append(b)

    # фази між колонками
    frags.append(text((cols[0] + cols[1]) / 2, 202, "expand", size=12, bold=True, color=FIELD))
    frags.append(text((cols[1] + cols[2]) / 2, 202, "migrate", size=12, bold=True, color=INK))
    frags.append(text((cols[2] + cols[3]) / 2, 202, "contract", size=12, bold=True, color=POS))

    # смуга сумісності: старий читач працює, поки name живий (v1..v3)
    frags.append(line(cols[0], 315, cols[2], 315, color=FIELD, sw=2.6))
    frags.append(line(cols[0], 308, cols[0], 322, color=FIELD, sw=2.6))
    frags.append(line(cols[2], 308, cols[2], 322, color=FIELD, sw=2.6))
    frags.append(text((cols[0] + cols[2]) / 2, 340,
                      "старий читач (знає лише name) працює, поки name живий", size=11, color=FIELD))
    frags.append(text(W / 2, 373,
                      "слот #2 після видалення — reserved назавжди: перевикористати номер = зламати старі дані",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "evolution.svg"), W, H, *frags)


def fig_shapes():
    """Одне поняття — багато форм на різних межах, тиски яких суперечать."""
    W, H = 960, 380
    frags = []
    frags.append(text(W / 2, 28, "Одне поняття — багато форм, кожна під своїм тиском", size=16, bold=True))

    # центр — доменне поняття
    core, _, _ = textbox(480, 92, "Order — доменне поняття\n(правила, інваріанти)", size=13,
                         fill="#eafaf1", stroke=FIELD, min_w=340)
    frags.append(core)

    cols = [145, 373, 601, 829]
    boxes = ["RequestDto\nвхід", "ResponseDto\nвихід", "Рядок БД\nзберігання", "ViewModel\nекран"]
    press = ["часткове, optional,\nвалідація на вході",
             "обчислене, повне,\nлише дозволене",
             "стовпці, типи схеми,\nіндекси",
             "форматоване,\nзлите з джерел"]
    for cx, bx, pr in zip(cols, boxes, press):
        frags.append(arrow(480, 120, cx, 208, color=MUTED, sw=1.6))
        b, _, _ = textbox(cx, 235, bx, size=13, min_w=190)
        frags.append(b)
        frags.append(mtext(cx, 285, pr, size=11, color=MUTED))

    frags.append(text(W / 2, 356,
                      "Одне поняття — багато форм. Спільний клас на всіх злива межі назад в одну.",
                      size=12, color=INK, italic=True))
    render(os.path.join(IMG, "shapes.svg"), W, H, *frags)


def fig_compat_matrix():
    """Флот читачів різних версій проти проводу різних версій: безпечна смуга + кути, що не співіснують у часі."""
    W, H = 1000, 470
    frags = []
    frags.append(text(W / 2, 30, "Флот читачів проти проводу: безпечно скрізь, де версії співіснують у часі",
                      size=16, bold=True))

    col_cx = [300, 495, 690, 885]
    col_hdr = ["провід v1\nemail(3)", "провід v2\n+ id(4)", "провід v3\nдубль-запис", "провід v4\nemail знято"]
    for cx, h in zip(col_cx, col_hdr):
        frags.append(mtext(cx, 76, h, size=12, color=INK, bold=True))

    row_cy = [170, 275, 380]
    row_hdr = ["читач A\n(бере email)", "читач B\n(email + id)", "читач C\n(лише id)"]
    for cy, h in zip(row_cy, row_hdr):
        frags.append(mtext(112, cy - 6, h, size=12, color=INK, bold=True))

    #        W1     W2     W3     W4
    grid = [
        ["ok", "ok", "ok", "na"],   # читач A (збірка v1)
        ["ok", "ok", "ok", "ok"],   # читач B (збірка v2–v3)
        ["na", "na", "ok", "ok"],   # читач C (збірка v4)
    ]
    verdict = {
        (0, 0): "OK", (0, 1): "OK\nполе 4 повз", (0, 2): "OK\nбере email", (0, 3): "—",
        (1, 0): "OK\nid порожній\n→ email", (1, 1): "OK", (1, 2): "OK", (1, 3): "OK\nбере id",
        (2, 0): "—", (2, 1): "—", (2, 2): "OK", (2, 3): "OK",
    }
    for r, cy in enumerate(row_cy):
        for c, cx in enumerate(col_cx):
            if grid[r][c] == "ok":
                b, _, _ = textbox(cx, cy, verdict[(r, c)], size=12, min_w=150,
                                  fill="#eafaf1", stroke=FIELD, color=INK)
            else:
                b, _, _ = textbox(cx, cy, "не співіснує\nв часі", size=11, min_w=150,
                                  fill="#f4f6f8", stroke=LINE, color=MUTED)
            frags.append(b)

    frags.append(rect(238, 432, 22, 14, fill="#eafaf1", stroke=FIELD))
    frags.append(text(268, 443, "безпечно: пряма + зворотна сумісність тримається",
                      size=11, color=INK, anchor="start"))
    frags.append(rect(716, 432, 22, 14, fill="#f4f6f8", stroke=LINE))
    frags.append(text(746, 443, "читача виведено до звуження", size=11, color=MUTED, anchor="start"))
    render(os.path.join(IMG, "compat-matrix.svg"), W, H, *frags)


def fig_number_reuse():
    """Перевикористаний номер поля: ті самі байти читаються як інше поле — тиха корупція."""
    W, H = 940, 430
    frags = []
    frags.append(text(W / 2, 30, "Перевикористати номер поля: ті самі байти, інший сенс", size=16, bold=True))

    # збережені байти: поле 3, varint, значення 500123 → 18 9B C3 1E
    bytes_hex = ["18", "9B", "C3", "1E"]
    bx0, byy = 348, 205
    for i, h in enumerate(bytes_hex):
        x = bx0 + i * 58
        frags.append(rect(x, byy - 18, 50, 36, fill="#fdf6e3", stroke="#d68910"))
        frags.append(text(x + 25, byy + 6, h, size=15, bold=True, color=INK))
    frags.append(text(bx0 + 116, byy - 30, "збережене повідомлення (диск, логи, старий клієнт)",
                      size=11, color=MUTED))
    frags.append(text(bx0 + 25, byy + 36, "18 = поле 3, varint", size=10, color=MUTED))
    frags.append(text(bx0 + 3 * 58 + 25, byy + 36, "9B C3 1E = 500123", size=10, color=MUTED))

    # верхній шлях — чесна схема
    up, _, _ = textbox(178, 108, "схема v1:\nполе 3 = legacy_ref (int64)", size=12,
                       fill="#eafaf1", stroke=FIELD, min_w=250)
    frags.append(up)
    frags.append(arrow(348, 195, 250, 128, color=FIELD, sw=2))
    frags.append(text(178, 158, "legacy_ref = 500123   правильно", size=11, color=FIELD, bold=True))

    # нижній шлях — порушник
    dn, _, _ = textbox(178, 322, "схема-порушник:\nполе 3 ПЕРЕВИКОРИСТАНО\n= warehouse_id (int64)", size=12,
                       fill="#fdecea", stroke=POS, min_w=250)
    frags.append(dn)
    frags.append(arrow(348, 216, 250, 300, color=POS, sw=2))
    frags.append(text(178, 262, "warehouse_id = 500123   тихо неправильно", size=11, color=POS, bold=True))

    frags.append(text(W / 2, 384,
                      "Ті самі байти розшифрувалися як інше поле: замовлення тихо приписане складу №500123.",
                      size=12, color=INK, italic=True))
    frags.append(text(W / 2, 410,
                      "reserved 3;  reserved \"legacy_ref\";  — компілятор не дасть посадити нове поле на мертвий номер.",
                      size=12, color=POS, bold=True))
    render(os.path.join(IMG, "number-reuse.svg"), W, H, *frags)


def fig_marginal():
    """Формальне дно долини: гранична економія на латентності (∝1/k²) проти сталої плати t."""
    W, H = 820, 460
    frags = []
    frags.append(text(W / 2, 30, "Дно долини: де гранична економія зрівнюється з граничною платою",
                      size=15, bold=True))

    ox, oy = 110, 380
    frags.append(arrow(ox, oy, 770, oy, color=INK, sw=2))        # вісь X
    frags.append(arrow(ox, oy, ox, 80, color=INK, sw=2))         # вісь Y
    frags.append(text(500, 414, "k — полів у DTO за один перетин →", size=12, color=MUTED))
    frags.append(text(ox + 6, 74, "гранична вартість доданого поля", size=11, color=MUTED, anchor="start"))

    # спадна крива граничної економії: value = 585/k² (екранні координати)
    pts = []
    k = 1.5
    while k <= 9.0:
        pts.append("%.1f,%.1f" % (110 + 70 * k, oy - 585.0 / (k * k)))
        k += 0.25
    frags.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>'
                 % (" ".join(pts), FIELD))

    # стала лінія граничної плати t
    frags.append(line(215, 300, 745, 300, color=POS, sw=2.4))

    # перетин k* — дно долини
    frags.append(circle(299, 300, 6, fill=BG, stroke=INK, sw=2.4))
    frags.append(line(299, 300, 299, oy, color=MUTED, sw=1.2, dash="4 4"))
    frags.append(text(299, 400, "k* = √(u·(L+m)/t)", size=13, bold=True, color=INK))

    b, _, _ = textbox(392, 150, "гранична економія\nна латентності\n∝ (L+m)/k²",
                      size=12, stroke=FIELD, min_w=170); frags.append(b)
    b, _, _ = textbox(632, 268, "= t\nплата за 1 зайве поле",
                      size=12, stroke=POS, min_w=150); frags.append(b)
    b, _, _ = textbox(210, 345, "тут DTO росте\nз користю",
                      size=11, stroke=FIELD, fill="#eafaf1", min_w=140); frags.append(b)
    b, _, _ = textbox(600, 210, "далі — надвибірка:\nплата > економія",
                      size=11, stroke=POS, fill="#fdecea", min_w=150); frags.append(b)
    render(os.path.join(IMG, "marginal.svg"), W, H, *frags)


def fig_rho_ladder():
    """ρ = (L+m)/t зростає на порядки з дорожчанням межі — і разом з ним виграш DTO."""
    W, H = 860, 440
    frags = []
    frags.append(text(W / 2, 30, "Що дорожча межа, то більший ρ = (L+m)/t — і виграш DTO",
                      size=15, bold=True))

    frags.append(arrow(64, 90, 64, 360, color=INK, sw=1.8))
    frags.append(mtext(30, 205, "межа\nдорожчає", size=11, color=MUTED))

    rows = [
        ("виклик функції (той самий процес)\nL+m ≈ 5 нс · t ≈ 1 нс",
         "ρ ≈ 5\nмежі майже нема:\nDTO — сама ціна", POS, "#fdecea"),
        ("інший процес (IPC на машині)\nL+m ≈ 10 мкс · t ≈ 0.1 мкс",
         "ρ ≈ 100\nвиграш помітний", MUTED, FILL),
        ("мережа, той самий ЦОД (RTT)\nL+m ≈ 500 мкс · t ≈ 1 мкс",
         "ρ ≈ 500\nDTO окупається", FIELD, "#eafaf1"),
        ("інший континент (RTT)\nL+m ≈ 150 мс · t ≈ 1 мкс",
         "ρ ≈ 150 000\nбери якнайгрубіше", FIELD, "#eafaf1"),
    ]
    for (lft, rgt, col, fillc), yy in zip(rows, [98, 180, 262, 344]):
        b, _, _ = textbox(255, yy, lft, size=12, min_w=300); frags.append(b)
        frags.append(arrow(425, yy, 515, yy, color=MUTED, sw=1.8))
        b, _, _ = textbox(660, yy, rgt, size=12, stroke=col, fill=fillc, min_w=220); frags.append(b)
    frags.append(text(W / 2, 420,
                      "ρ = (L+m)/t — скільки полів «коштує» один похід через межу; що твердіша межа, то більший ρ",
                      size=11, color=MUTED, italic=True))
    render(os.path.join(IMG, "rho-ladder.svg"), W, H, *frags)


def fig_chattiness():
    """Читомість C — вимірна: перетинів на задачу; час росте лінійно T = C·(L+m)."""
    W, H = 820, 440
    frags = []
    frags.append(text(W / 2, 30, "Читомість C: перетинів на задачу; час росте лінійно T = C·(L+m)",
                      size=15, bold=True))

    ox, oy = 110, 380
    frags.append(arrow(ox, oy, 770, oy, color=INK, sw=2))
    frags.append(arrow(ox, oy, ox, 80, color=INK, sw=2))
    frags.append(text(500, 414, "читомість C = перетинів на задачу →", size=12, color=MUTED))
    frags.append(text(ox + 6, 74, "час на задачу T (RTT межі 80 мс)", size=11, color=MUTED, anchor="start"))

    def px(C):
        return 110 + 13.5 * C

    def py(C):
        return oy - 5.9 * C

    frags.append(line(px(0), py(0), px(48), py(48), color=INK, sw=2.6))

    for C, col in [(1, FIELD), (12, MUTED), (47, POS)]:
        frags.append(circle(px(C), py(C), 6, fill=BG, stroke=col, sw=2.6))

    b, _, _ = textbox(250, 150, "нахил = L+m\n(латентність межі)", size=12, stroke=INK, min_w=170)
    frags.append(b)
    b, _, _ = textbox(250, 255, "C=12\n0.96 с", size=12, stroke=MUTED, min_w=120); frags.append(b)
    b, _, _ = textbox(600, 120, "C=47: наївний екран\n3.76 с", size=12, stroke=POS, min_w=150); frags.append(b)
    frags.append(text(300, 372, "C=1 (BFF): 80 мс", size=11, color=FIELD, bold=True))
    render(os.path.join(IMG, "chattiness.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_roundtrips()
    fig_boundary()
    fig_versions()
    fig_hist_timeline()
    fig_hist_localdto()
    fig_assembler()
    fig_cost_regimes()
    fig_evolution()
    fig_shapes()
    fig_compat_matrix()
    fig_number_reuse()
    fig_marginal()
    fig_rho_ladder()
    fig_chattiness()
    print("ok")
