# -*- coding: utf-8 -*-
"""Фігури до теми «Кадрування повідомлень у потоці TCP».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

AMBER = "#b08900"          # третє повідомлення / тепле виділення
BLUE_F = "#e7edfb"         # заливка під NEG
GREEN_F = "#e8f6ed"        # заливка під FIELD
AMBER_F = "#fdf6e0"        # заливка під AMBER
GREY_F = "#eceff3"


# ── 1. Межі не переживають дороги ─────────────────────────────────────────────
# Ідея: ті самі байти, три різні розбиття — застосунком, стеком, приймачем.
def fig_boundaries():
    W, H = 900, 470
    x0, x1 = 70, 850
    span = x1 - x0
    bh = 46

    # спільна розмітка потоку: три повідомлення однакові в усіх рядках
    msgs = [(0.00, 0.34, NEG, BLUE_F, "повідомлення A"),
            (0.34, 0.60, FIELD, GREEN_F, "повідомлення B"),
            (0.60, 1.00, AMBER, AMBER_F, "повідомлення C")]

    rows = [
        (110, "як поділив застосунок: три виклики надсилання",
         [0.34, 0.60], ["надсилання №1", "надсилання №2", "надсилання №3"]),
        (250, "як поділив стек: сегменти за своїми правилами",
         [0.60, 0.82], ["сегмент №1", "сегмент №2", "сегмент №3"]),
        (390, "як побачив приймач: три виклики читання",
         [0.47, 0.75], ["читання №1", "читання №2", "читання №3"]),
    ]

    f = [text(W / 2, 30, "Ті самі байти — три різні розбиття", size=16, bold=True),
         text(W / 2, 54, "колір показує, до якого повідомлення належить байт",
              size=11, color=MUTED)]

    for ytop, title, cuts, names in rows:
        f.append(text(x0, ytop - 14, title, size=12, color=INK, anchor="start", bold=True))
        # кольорові смуги повідомлень (спільні для всіх рядків)
        for a, b, col, fill, _ in msgs:
            f.append(rect(x0 + a * span, ytop, (b - a) * span, bh,
                          fill=fill, stroke=fill, sw=0.8, rx=0))
        # зовнішня рамка смуги
        f.append(rect(x0, ytop, span, bh, fill="none", stroke=MUTED, sw=1.0, rx=0))
        # розрізи цього рядка
        bounds = [0.0] + cuts + [1.0]
        for c in cuts:
            f.append(line(x0 + c * span, ytop - 8, x0 + c * span, ytop + bh + 8,
                          color=INK, sw=3.0))
        # підписи шматків — під смугою, по центру кожного
        for i, nm in enumerate(names):
            cx = x0 + (bounds[i] + bounds[i + 1]) / 2 * span
            f.append(text(cx, ytop + bh + 26, nm, size=11.5, color=INK))

    # підписи самих повідомлень — усередині смуг першого рядка
    ytop = rows[0][0]
    for a, b, col, fill, nm in msgs:
        f.append(text(x0 + (a + b) / 2 * span, ytop + 29, nm, size=11.5, color=col, bold=True))

    render(os.path.join(IMG, "boundaries-lost.svg"), W, H, *f)


# ── 2. Чотири кадрування того самого тіла ─────────────────────────────────────
# Ідея: побайтова розкладка «PING» у чотирьох способах + що робить приймач.
def fig_four_framings():
    W, H = 940, 470
    lx, lw = 24, 168          # колонка з назвою
    bx = 210                  # початок побайтової розкладки
    nx, nw = 690, 226         # колонка «як знайти межу»
    cw, ch = 46, 36

    rows = [
        ("стала довжина", [("P", 0), ("I", 0), ("N", 0), ("G", 0)],
         "лічити до сталого N;\nслужбових байтів немає"),
        ("префікс довжини", [("00", 1), ("00", 1), ("00", 1), ("04", 1),
                             ("P", 0), ("I", 0), ("N", 0), ("G", 0)],
         "прочитати 4 байти заголовка,\nвідлічити стільки ж, скільки в них"),
        ("байт-роздільник", [("P", 0), ("I", 0), ("N", 0), ("G", 0), ("0A", 2)],
         "переглядати байти,\nдоки не трапиться 0x0A"),
        ("нетрядок", [("4", 1), (":", 2), ("P", 0), ("I", 0), ("N", 0), ("G", 0), (",", 2)],
         "прочитати число до ':',\nвідлічити, звірити ',' у кінці"),
    ]

    fills = {0: GREY_F, 1: BLUE_F, 2: AMBER_F}
    strokes = {0: MUTED, 1: NEG, 2: AMBER}

    f = [text(W / 2, 30, "Одне тіло «PING» — чотири способи покласти межу в байти",
              size=16, bold=True),
         text(bx, 56, "байти на дроті", size=11, color=MUTED, anchor="start"),
         text(nx, 56, "що робить приймач", size=11, color=MUTED, anchor="start")]

    y = 78
    for name, cells, note in rows:
        f.append(fitbox(lx, y + 2, lw, ch - 4, name, size=13, bold=True,
                        fill="#ffffff", stroke=INK, sw=1.4))
        for i, (val, kind) in enumerate(cells):
            f.append(fitbox(bx + i * cw, y, cw - 4, ch, val, size=13,
                            fill=fills[kind], stroke=strokes[kind], sw=1.4))
        f.append(fitbox(nx, y - 2, nw, ch + 4, note, size=11,
                        fill="#ffffff", stroke=MUTED, sw=1.0))
        y += 78

    # легенда — знизу, з відступом від останнього рядка
    ly = y + 6
    leg = [("тіло повідомлення", GREY_F, MUTED),
           ("довжина", BLUE_F, NEG),
           ("службовий знак", AMBER_F, AMBER)]
    cx = lx
    for label, fill, stroke in leg:
        f.append(rect(cx, ly, 26, 18, fill=fill, stroke=stroke, sw=1.3, rx=4))
        f.append(text(cx + 34, ly + 14, label, size=11.5, color=INK, anchor="start"))
        cx += 34 + text_width(label, 11.5) + 40

    render(os.path.join(IMG, "four-framings.svg"), W, H, *f)


# ── 3. Життєвий цикл накопичувального буфера ─────────────────────────────────
# Ідея: дописали → вийняли ВСІ повні кадри → зсунули неповний хвіст.
def fig_receive_buffer():
    W, H = 940, 360
    pw, gap = 292, 20
    px = [24, 24 + pw + gap, 24 + 2 * (pw + gap)]
    by, bh = 150, 52

    f = [text(W / 2, 30, "Три дії на кожну подію готовності сокета", size=16, bold=True)]

    titles = ["1. дописали прийняте в кінець",
              "2. вийняли ВСІ повні кадри",
              "3. зсунули хвіст на початок"]
    for i, t in enumerate(titles):
        f.append(text(px[i] + pw / 2, 66, t, size=12.5, bold=True, color=INK))

    # панель 1: хвіст попереднього читання + свіжа порція
    parts1 = [(0.00, 0.22, GREY_F, MUTED, "хвіст"), (0.22, 1.00, BLUE_F, NEG, "нова порція")]
    # панель 2: два повні кадри + недобудований хвіст
    parts2 = [(0.00, 0.34, GREEN_F, FIELD, "кадр 1"), (0.34, 0.72, GREEN_F, FIELD, "кадр 2"),
              (0.72, 1.00, GREY_F, MUTED, "неповний")]
    # панель 3: тільки хвіст, решта — вільне місце
    parts3 = [(0.00, 0.28, GREY_F, MUTED, "неповний"), (0.28, 1.00, "#ffffff", MUTED, "вільно")]

    for i, parts in enumerate((parts1, parts2, parts3)):
        f.append(rect(px[i], by, pw, bh, fill="#ffffff", stroke=INK, sw=1.6, rx=4))
        for a, b, fill, stroke, label in parts:
            x = px[i] + a * pw
            w = (b - a) * pw
            f.append(rect(x, by, w, bh, fill=fill, stroke=stroke, sw=1.3, rx=0))
            f.append(text(x + w / 2, by + bh / 2 + 4, label, size=11, color=INK))

    # у другій панелі — два кадри йдуть в обробку (стрілки вгору, підпис над буфером)
    for a, b in ((0.00, 0.34), (0.34, 0.72)):
        cx = px[1] + (a + b) / 2 * pw
        f.append(arrow(cx, by - 6, cx, by - 40, color=FIELD, sw=2.0))
    f.append(text(px[1] + pw / 2, by - 48, "у обробку", size=11.5, color=FIELD, bold=True))

    # пояснення під панелями
    notes = ["читання не знає про кадри —\nвоно приносить стільки, скільки є",
             "цикл зупиняється, коли залишку\nне вистачає навіть на заголовок",
             "інваріант відновлено: у буфері —\nпочаток ще не зібраного кадру"]
    for i, n in enumerate(notes):
        f.append(mtext(px[i] + pw / 2, by + bh + 34, n, size=11, color=MUTED, lh=1.35))

    render(os.path.join(IMG, "receive-buffer.svg"), W, H, *f)


# ── 4. Затримка на двох записах проти одного ──────────────────────────────────
# Ідея: притримування дрібного сегмента + відкладене підтвердження = пауза на таймер.
def fig_nagle_stall():
    W, H = 940, 470
    lx = 150                       # де починаються лінії учасників
    rx = 900

    def party_lines(ys, yr):
        out = [line(lx, ys, rx, ys, color=MUTED, sw=1.2),
               line(lx, yr, rx, yr, color=MUTED, sw=1.2),
               text(lx - 12, ys + 4, "відправник", size=11.5, color=INK, anchor="end"),
               text(lx - 12, yr + 4, "приймач", size=11.5, color=INK, anchor="end")]
        return out

    f = [text(W / 2, 30, "Той самий кадр: двома записами й одним", size=16, bold=True)]

    # ── верхня панель: два записи ──
    ys, yr = 118, 196
    f.append(text(lx, 66, "заголовок і тіло двома викликами запису",
                  size=12.5, bold=True, color=POS, anchor="start"))
    f += party_lines(ys, yr)
    f.append(arrow(lx + 30, ys, lx + 170, yr, color=NEG, sw=2.0))
    f.append(text(lx + 40, ys - 14, "заголовок 4 Б", size=11, color=NEG, anchor="start"))
    f.append(text(lx + 260, ys - 14, "тіло притримано: є непідтверджені дані",
                  size=11, color=POS, anchor="start"))
    f.append(text(lx + 30, yr + 22, "прийшло пів кадру — відповідати нічим",
                  size=11, color=MUTED, anchor="start"))
    f.append(fitbox(lx + 190, ys + 16, 330, 44,
                    "пауза ≈40 мс: підтвердження відкладено",
                    size=12, fill="#fdecea", stroke=POS, sw=1.4))
    f.append(arrow(lx + 540, yr, lx + 620, ys, color=FIELD, sw=2.0))
    f.append(text(lx + 500, yr + 22, "підтвердження нарешті пішло",
                  size=11, color=FIELD, anchor="start"))
    f.append(arrow(lx + 640, ys, rx - 40, yr, color=NEG, sw=2.0))
    f.append(text(lx + 620, ys - 14, "тіло 900 Б", size=11, color=NEG, anchor="start"))
    f.append(text(rx - 30, yr + 22, "кадр цілий", size=11, color=INK, anchor="end"))

    # ── нижня панель: один запис ──
    ys2, yr2 = 340, 418
    f.append(text(lx, 288, "заголовок і тіло одним викликом запису",
                  size=12.5, bold=True, color=FIELD, anchor="start"))
    f += party_lines(ys2, yr2)
    f.append(arrow(lx + 30, ys2, lx + 170, yr2, color=NEG, sw=2.0))
    f.append(text(lx + 40, ys2 - 14, "кадр цілком, 904 Б", size=11, color=NEG, anchor="start"))
    f.append(arrow(lx + 230, yr2, lx + 370, ys2, color=FIELD, sw=2.0))
    f.append(text(lx + 190, yr2 + 22, "кадр цілий одразу — є що відповісти",
                  size=11, color=MUTED, anchor="start"))
    f.append(fitbox(lx + 420, ys2 + 16, 300, 44, "жодного очікування таймера",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, "nagle-stall.svg"), W, H, *f)


# ── 5. Чим HTTP позначав кінець тіла в різні епохи (до вставки hist-) ────────
# Ідея: одна й та сама відповідь «PING» — чотири різні носії межі за 24 роки.
def fig_http_body_end():
    W, H = 1020, 510
    lx, lw = 24, 182           # колонка з назвою механізму й роком
    bx, bw = 224, 520          # побайтова смуга
    nx, nw = 766, 230          # колонка «що робить приймач»
    ch = 44

    fills = {0: GREY_F, 1: BLUE_F, 2: AMBER_F}
    strokes = {0: MUTED, 1: NEG, 2: AMBER}

    rows = [
        ("кінець з'єднання\nHTTP/0.9 · 1991",
         [(0.72, "тіло документа", 0), (0.28, "FIN: закрито", 2)],
         "читати до нуля від recv;\nобірване й закінчене\nне відрізнити"),
        ("Content-Length\nHTTP/1.0 · 1996",
         [(0.44, "Content-Length: 4", 1), (0.16, "CRLF CRLF", 2), (0.40, "PING", 0)],
         "прочитати число\nіз заголовка й відлічити\nстільки байтів тіла"),
        ("поблокове кодування\nHTTP/1.1 · 1997",
         [(0.20, "4 CRLF", 1), (0.18, "PING", 0), (0.14, "CRLF", 2),
          (0.20, "0 CRLF", 1), (0.28, "CRLF — кінець", 2)],
         "лічити блок за блоком,\nдоки не прийде блок\nнульового розміру"),
        ("двійковий кадр\nHTTP/2 · 2015",
         [(0.28, "довжина: 24 біти", 1), (0.13, "тип", 2), (0.17, "прапорці", 2),
          (0.16, "потік", 2), (0.26, "PING", 0)],
         "довжина — поле сталої\nширини на сталому місці\nу 9-байтовому заголовку"),
    ]

    f = [text(W / 2, 30, "Чим HTTP позначав кінець тіла: чотири епохи", size=16, bold=True),
         text(bx, 62, "байти на дроті", size=11, color=MUTED, anchor="start"),
         text(nx, 62, "що робить приймач", size=11, color=MUTED, anchor="start")]

    y = 86
    for name, segs, note in rows:
        f.append(fitbox(lx, y + 2, lw, ch - 4, name, size=12, bold=True,
                        fill="#ffffff", stroke=INK, sw=1.4))
        acc = 0.0
        for frac, label, kind in segs:
            f.append(fitbox(bx + acc * bw, y, frac * bw - 4, ch, label, size=11.5,
                            fill=fills[kind], stroke=strokes[kind], sw=1.4))
            acc += frac
        f.append(fitbox(nx, y - 2, nw, ch + 4, note, size=11,
                        fill="#ffffff", stroke=MUTED, sw=1.0))
        y += 92

    ly = y + 6
    leg = [("тіло", GREY_F, MUTED), ("довжина", BLUE_F, NEG), ("службове", AMBER_F, AMBER)]
    cx = lx
    for label, fill, stroke in leg:
        f.append(rect(cx, ly, 26, 18, fill=fill, stroke=stroke, sw=1.3, rx=4))
        f.append(text(cx + 34, ly + 14, label, size=11.5, color=INK, anchor="start"))
        cx += 34 + text_width(label, 11.5) + 46

    render(os.path.join(IMG, "http-body-end.svg"), W, H, *f)


# ── 6. Розсинхронізація: ті самі байти, два прочитання ───────────────────────
# Ідея: дві межі в одному запиті → фронтенд і бекенд ріжуть потік по-різному.
def fig_http_desync():
    W, H = 1020, 610
    cellw, ch = 76, 42
    x0 = 30
    ax = 520                    # колонка приміток праворуч від смуги
    aw = 470

    body = ["0", "CR", "LF", "CR", "LF", "G"]

    f = [text(W / 2, 30, "Одні байти — два різні прочитання", size=16, bold=True)]

    # ── зверху ліворуч: сам запит ──
    f.append(rect(x0, 56, 380, 184, fill="#ffffff", stroke=INK, sw=1.4, rx=6))
    f.append(rect(x0 + 10, 108, 360, 44, fill=AMBER_F, stroke=AMBER, sw=1.2, rx=4))
    req = ["POST /search HTTP/1.1", "Host: shop.example",
           "Content-Length: 6", "Transfer-Encoding: chunked",
           "", "0", "", "G"]
    ty = 80
    for ln in req:
        if ln:
            f.append(text(x0 + 22, ty, ln, size=12, color=INK, anchor="start"))
        ty += 21

    f.append(fitbox(440, 76, 556, 66,
                    "У ЦЬОМУ запиті межа тіла оголошена ДВІЧІ:\n"
                    "довжиною в 6 байтів і поблоковим кодуванням.",
                    size=13, fill=AMBER_F, stroke=AMBER, sw=1.4))
    f.append(fitbox(440, 156, 556, 78,
                    "Фронтенд і бекенд — різні програми різних авторів.\n"
                    "Кожна сама вирішує, котра межа головніша,\n"
                    "і про вибір сусіда нічого не знає.",
                    size=12.5, fill="#ffffff", stroke=MUTED, sw=1.2))

    # ── три смуги прочитань ──
    def band(y, label, kinds, note, ncolor):
        out = [text(x0, y - 10, label, size=12.5, bold=True, color=INK, anchor="start")]
        for i, b in enumerate(body):
            k = kinds[i]
            fill = GREEN_F if k == 0 else "#fdecea"
            stroke = FIELD if k == 0 else POS
            out.append(fitbox(x0 + i * cellw, y, cellw - 5, ch, b, size=13,
                              fill=fill, stroke=stroke, sw=1.5))
        out.append(fitbox(ax, y - 4, aw, ch + 8, note, size=11.5,
                          fill="#ffffff", stroke=ncolor, sw=1.2))
        return out

    f += band(282, "фронтенд лічить за Content-Length: 6", [0] * 6,
              "усі шість байтів — тіло запиту;\n"
              "фронтенд передає запит далі цілим і вважає справу закритою",
              FIELD)

    f += band(382, "бекенд лічить за Transfer-Encoding: chunked", [0] * 5 + [1],
              "блок нульового розміру закрив тіло на п'ятому байті;\n"
              "шостий байт «G» — це вже початок наступного запиту",
              POS)

    # ── третя смуга: лишок приклеюється до чужого запиту ──
    y3 = 486
    f.append(text(x0, y3 - 10, "що бекенд прочитає наступним", size=12.5,
                  bold=True, color=INK, anchor="start"))
    f.append(fitbox(x0, y3, cellw - 5, ch, "G", size=13,
                    fill="#fdecea", stroke=POS, sw=1.5))
    f.append(fitbox(x0 + cellw, y3, 4 * cellw - 5, ch,
                    "POST /account HTTP/1.1 …", size=12.5,
                    fill=GREY_F, stroke=MUTED, sw=1.3))
    f.append(text(x0 + cellw, y3 + ch + 20, "запит, який надіслав ІНШИЙ клієнт",
                  size=11.5, color=MUTED, anchor="start"))
    f.append(fitbox(ax, y3 - 4, aw, ch + 8,
                    "лишок зливається з чужим запитом в один;\n"
                    "метод стає «GPOST», а зміст запиту — чим завгодно",
                    size=11.5, fill="#fdecea", stroke=POS, sw=1.2))

    render(os.path.join(IMG, "http-desync.svg"), W, H, *f)


# ── 7. Заголовок кадру HTTP/2 (до вставки hist-) ─────────────────────────────
# Ідея: довжина повернулася в поле сталої ширини на сталому місці.
def fig_http2_frame():
    W, H = 980, 400
    cw, ch = 76, 46
    x0, y0 = 50, 152

    f = [text(W / 2, 30, "Заголовок кадру HTTP/2: дев'ять байтів на сталих місцях",
              size=16, bold=True)]

    spans = [(0, 3, "довжина\n24 біти", BLUE_F, NEG),
             (3, 4, "тип\n8", AMBER_F, AMBER),
             (4, 5, "прапорці\n8", AMBER_F, AMBER),
             (5, 9, "1 біт зарезервовано +\nідентифікатор потоку (31 біт)", AMBER_F, AMBER)]
    for a, b, label, fill, stroke in spans:
        f.append(fitbox(x0 + a * cw + 3, 76, (b - a) * cw - 6, 54, label,
                        size=12, fill=fill, stroke=stroke, sw=1.4))

    for i in range(9):
        f.append(rect(x0 + i * cw + 3, y0, cw - 6, ch, fill="#ffffff",
                      stroke=INK, sw=1.3, rx=4))
        f.append(text(x0 + i * cw + cw / 2, y0 + ch / 2 + 5, "байт %d" % i,
                      size=11.5, color=MUTED))

    # корисне навантаження — праворуч від заголовка
    f.append(fitbox(x0 + 9 * cw + 14, y0, W - (x0 + 9 * cw + 14) - 24, ch,
                    "тіло кадру", size=12.5, fill=GREY_F, stroke=MUTED, sw=1.3))

    f.append(text(x0, y0 + ch + 28,
                  "приймач читає рівно 9 байтів, бере з них число і відлічує рівно стільки далі",
                  size=12, color=INK, anchor="start"))

    f.append(fitbox(30, 262, 440, 86,
                    "HTTP/1.1\nмежу тіла оголошують заголовки — текст,\n"
                    "який кожен вузол розбирає власним кодом",
                    size=12.5, fill=AMBER_F, stroke=AMBER, sw=1.4))
    f.append(fitbox(510, 262, 440, 86,
                    "HTTP/2\nмежу задає поле сталої ширини на сталому місці —\n"
                    "розходитися в тлумаченні нема на чому",
                    size=12.5, fill=GREEN_F, stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, "http2-frame.svg"), W, H, *f)


# ── 8. Один код, три розбиття того самого потоку (вставка proj-framed-reader) ─
# Ідея: 18 байтів = два кадри; читання ріжуть їх по-різному, результат той самий.
def fig_reader_splits():
    W, H = 1060, 566
    n, cw, ch = 18, 34, 34
    sx = 250
    swid = n * cw                      # 612 → стрічка 250..862
    bx, bw = 884, 152                  # колонка результату

    hexb = ["00", "00", "00", "04", "50", "49", "4E", "47",
            "00", "00", "00", "06", "48", "45", "4C", "4C", "4F", "21"]
    segs = [(0, 4,   "#cad9f8", NEG,   "len = 4"),
            (4, 8,   "#e7edfb", NEG,   "тіло «PING»"),
            (8, 12,  "#c6e9d4", FIELD, "len = 6"),
            (12, 18, "#e8f6ed", FIELD, "тіло «HELLO!»")]

    def strip(y, hexes=False):
        out = []
        for a, b, fill, _c, _l in segs:
            out.append(rect(sx + a * cw, y, (b - a) * cw, ch,
                            fill=fill, stroke=fill, sw=0.8, rx=0))
        for i in range(1, n):          # білі розділювачі клітинок
            out.append(line(sx + i * cw, y, sx + i * cw, y + ch, color=BG, sw=1.0))
        out.append(rect(sx, y, swid, ch, fill="none", stroke=MUTED, sw=1.1, rx=0))
        if hexes:
            for i, hx in enumerate(hexb):
                out.append(text(sx + i * cw + cw / 2, y + ch / 2 + 4.5, hx,
                                size=11, color=INK))
        return out

    f = [text(W / 2, 32, "Один код, три розбиття того самого потоку", size=17, bold=True),
         text(W / 2, 56, "18 байтів — два кадри з чотирибайтовим префіксом довжини, "
                         "старшим байтом уперед", size=11.5, color=MUTED)]

    # ── еталонний потік із шістнадцятковими байтами ──
    ty = 100
    for i in range(n):
        f.append(text(sx + i * cw + cw / 2, ty - 9, str(i), size=9, color=MUTED))
    f += strip(ty, hexes=True)
    f.append(text(236, ty + ch / 2 + 5, "потік, 18 Б", size=12, color=INK,
                  anchor="end", bold=True))
    for a, b, _fill, col, lab in segs:
        f.append(text(sx + (a + b) / 2 * cw, ty + ch + 21, lab, size=11,
                      color=col, bold=True))

    # ── три розбиття ──
    rows = [("А · склеєно", "одне читання, 18 Б", [],
             "цикл розбору не спиняється після першого кадру — інакше «HELLO!» "
             "чекав би події, якої не буде"),
            ("Б · по байту", "18 читань по 1 Б", list(range(1, n)),
             "поки в буфері немає всіх чотирьох байтів заголовка, довжину не читає ніхто"),
            ("В · заголовок навпіл", "два читання: 10 Б + 8 Б", [10],
             "поле довжини другого кадру розірване між читаннями: хвіст у 2 Б "
             "зсунуто на початок буфера")]

    y = 218
    for name, sub, cuts, note in rows:
        f += strip(y)
        f.append(text(236, y + 13, name, size=12, color=INK, anchor="end", bold=True))
        f.append(text(236, y + 31, sub, size=10.5, color=MUTED, anchor="end"))
        for c in cuts:
            f.append(line(sx + c * cw, y - 7, sx + c * cw, y + ch + 7, color=INK, sw=2.2))
        f.append(fitbox(bx, y + 2, bw, 30, "видано: PING, HELLO!", size=10.5,
                        fill=GREY_F, stroke=MUTED, sw=1.0))
        f.append(text(sx, y + ch + 24, note, size=10.5, color=MUTED, anchor="start"))
        y += 97

    f.append(fitbox(250, 506, 786, 42,
                    "Гілки для цих випадків у коді немає: усе робить умова "
                    "«have − off ≥ HDR» і цикл до вичерпання.",
                    size=12, fill=GREEN_F, stroke=FIELD, sw=1.4))

    render(os.path.join(IMG, "framed-reader-splits.svg"), W, H, *f)


# ── 9. Часткове записування: зсув переформовує вектор (вставка proj) ──────────
# Ідея: заголовок формують раз; змінюється тільки sent, а з ним — межі iovec.
def fig_writer_offset():
    W, H = 1000, 488
    hx, hw = 210, 96                   # блок заголовка (масштаб не лінійний)
    bxx, bwd = 306, 534                # блок тіла
    bh = 34
    rx0, rw = 858, 124                 # колонка результату

    states = [(0,   "sent = 0",   "кадр щойно сформовано",
               "iov[0] = заголовок+0, 4 Б   ·   iov[1] = тіло+0, 900 Б   ·   разом 904 Б",
               "прийнято 3 Б"),
              (3,   "sent = 3",   "пішли 3 байти заголовка",
               "iov[0] = заголовок+3, 1 Б   ·   iov[1] = тіло+0, 900 Б   ·   разом 901 Б",
               "прийнято 500 Б"),
              (503, "sent = 503", "заголовок і 499 Б тіла",
               "iov[0] = тіло+499, 401 Б   ·   вектор із ОДНОГО шматка   ·   разом 401 Б",
               "прийнято 401 Б\nкадр пішов увесь")]

    f = [text(W / 2, 32, "Частковий запис: змінюється лише зсув", size=17, bold=True),
         text(W / 2, 56, "масштаб не лінійний — заголовок (4 Б) намальовано ширше, "
                         "щоб було видно зсув усередині нього", size=11.5, color=MUTED)]

    y = 100
    for sent, lab, sub, iovtext, res in states:
        hs = min(sent, 4)                       # скільки байтів заголовка пішло
        bs = max(0, sent - 4)                   # скільки байтів тіла пішло
        hcut = hw * hs / 4.0
        bcut = bwd * bs / 900.0

        # заголовок: що пішло — сіре, решта — синє
        f.append(rect(hx, y, hcut, bh, fill="#d5dae1", stroke="#d5dae1", sw=0.8, rx=0))
        f.append(rect(hx + hcut, y, hw - hcut, bh, fill="#cad9f8", stroke="#cad9f8",
                      sw=0.8, rx=0))
        f.append(rect(hx, y, hw, bh, fill="none", stroke=NEG, sw=1.4, rx=0))
        f.append(text(hx + hw / 2, y + bh / 2 + 4, "заголовок 4 Б", size=9.5, color=INK))

        # тіло: що пішло — сіре, решта — зелене
        f.append(rect(bxx, y, bcut, bh, fill="#d5dae1", stroke="#d5dae1", sw=0.8, rx=0))
        f.append(rect(bxx + bcut, y, bwd - bcut, bh, fill="#c6e9d4", stroke="#c6e9d4",
                      sw=0.8, rx=0))
        f.append(rect(bxx, y, bwd, bh, fill="none", stroke=FIELD, sw=1.4, rx=0))
        f.append(text(bxx + bwd / 2, y + bh / 2 + 4, "тіло 900 Б", size=11, color=INK))

        f.append(text(190, y + 13, lab, size=12, color=INK, anchor="end", bold=True))
        f.append(text(190, y + 31, sub, size=10, color=MUTED, anchor="end"))
        f.append(text(hx, y + bh + 21, iovtext, size=10.5, color=MUTED, anchor="start"))
        f.append(fitbox(rx0, y - 3, rw, 40, res, size=10, fill=GREY_F, stroke=MUTED, sw=1.0))
        y += 110

    f.append(fitbox(24, 400, 952, 56,
                    "Заголовок формують РАЗ і більше не чіпають — змінюється тільки зсув sent.\n"
                    "Переформувати кадр після часткового записування означає зробити з потоку кашу.",
                    size=12.5, fill=AMBER_F, stroke=AMBER, sw=1.4))

    render(os.path.join(IMG, "framed-writer-offset.svg"), W, H, *f)


if __name__ == "__main__":
    fig_boundaries()
    fig_four_framings()
    fig_receive_buffer()
    fig_nagle_stall()
    fig_http_body_end()
    fig_http_desync()
    fig_http2_frame()
    fig_reader_splits()
    fig_writer_offset()
    print("ok:", os.listdir(IMG))
