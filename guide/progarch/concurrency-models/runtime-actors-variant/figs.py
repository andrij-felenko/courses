# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

ACT = "#7a4ea8"      # фіолетовий — актор
ACTBG = "#f3edfb"
WARN = "#b8862f"
WARNBG = "#fff6e0"


# ── shared-vs-mailboxes: у чому структурна перемога варіанта В ──────────────────
# Ідея: А і Б ділять ОДНУ памʼять — кілька виконавців тягнуться в один стан, і саме
# там живуть перегони/замки/дедлок. В прибирає спільну памʼять зовсім: у кожного
# актора приватний стан + своя скринька, а зв'язок — лише повідомленнями. Битися
# нема за що. Два панелі поруч, кожен напис у своїй смузі.
def fig_shared_vs_mailboxes():
    W, H = 980, 452
    p = []
    midx = 490
    p.append(line(midx, 52, midx, H - 26, color="#cfd6de", sw=1.4, dash="5 5"))

    # ── ЛІВА панель: спільна памʼять ──
    lcx = 250
    p.append(text(lcx, 70, "Варіанти А і Б: одна памʼять на всіх", size=13, color=NEG, bold=True))
    # три виконавці вгорі
    wy, ww, wh = 96, 118, 40
    workers = [(120, "потік / задача 1"), (250, "потік / задача 2"), (380, "потік / задача 3")]
    for wx, lbl in workers:
        p.append(fitbox(wx - ww / 2, wy, ww, wh, lbl, size=10.5, pad=6,
                        fill="#eaf0fd", stroke=NEG, sw=1.5))
    # спільний стан унизу
    sbx, sby, sbw, sbh = 96, 250, 308, 88
    p.append(rect(sbx, sby, sbw, sbh, fill="#eef2fc", stroke=NEG, sw=2))
    p.append(mtext(sbx + sbw / 2, sby + 38, "СПІЛЬНА ПАМʼЯТЬ\nстан усього дому в одному місці",
                   size=11.5, color=NEG, lh=1.35, bold=True))
    # стрілки: кожен виконавець тягнеться в один стан
    for wx, _ in workers:
        p.append(arrow(wx, wy + wh + 2, lcx + (wx - lcx) * 0.24, sby - 4, color=NEG, sw=1.7))
    # попередження
    wb, _, _ = textbox(lcx, sby + sbh + 34, "тут і живуть перегони · замки · дедлок",
                       size=11, pad=8, fill="#fdecea", stroke=POS, sw=1.7, color=POS, bold=True)
    p.append(wb)

    # ── ПРАВА панель: поштові скриньки ──
    rcx = 736
    p.append(text(rcx, 70, "Варіант В: скринька в кожного", size=13, color=ACT, bold=True))
    # три актори-клітини, кожна з приватним станом і скринькою
    cells = [(600, 108), (872, 108), (736, 246)]
    cw2, ch2 = 176, 96
    for cx, cy in cells:
        x, y = cx - cw2 / 2, cy
        p.append(rect(x, y, cw2, ch2, fill=ACTBG, stroke=ACT, sw=1.9, rx=12))
        p.append(text(cx, y + 22, "актор · пристрій", size=10.5, color=ACT, bold=True))
        p.append(fitbox(x + 12, y + 32, cw2 - 24, 30, "приватний стан", size=10, pad=4,
                        fill=BG, stroke=ACT, sw=1.2))
        # скринька — вкладка при нижньому краю
        p.append(fitbox(x + 12, y + ch2 - 26, cw2 - 24, 20, "скринька ▉▉▉", size=9.5, pad=3,
                        fill="#efe7f8", stroke=ACT, sw=1.2))
    # повідомлення між акторами (у скриньки, не в стан)
    p.append(arrow(600 + 60, 108 + 40, 872 - 66, 108 + 40, color=ACT, sw=1.7))
    p.append(text(736, 132, "повідомлення", size=10, color=ACT, italic=True))
    p.append(arrow(792, 108 + ch2, 760, 246 - 4, color=ACT, sw=1.7))
    p.append(arrow(680, 108 + ch2, 712, 246 - 4, color=ACT, sw=1.7))
    # висновок
    nb, _, _ = textbox(rcx, 246 + ch2 + 40, "нічого спільного — нема за що битися",
                       size=11, pad=8, fill="#eef6ef", stroke=FIELD, sw=1.7, color=FIELD, bold=True)
    p.append(nb)

    render(os.path.join(OUT, "shared-vs-mailboxes.svg"), W, H, *p,
           title="Не «як безпечно ділити памʼять», а «не ділити зовсім»")


# ── supervision: наглядач перезапускає впалого, сусіди живі ─────────────────────
# Ідея: дім складають в дерево нагляду. Один пристрій-актор упав (кривий драйвер,
# кинуло виняток) — наглядач кімнати перезапускає САМЕ його з чистого стану;
# брати по гілці й решта дому працюють далі. «Хай падає», а не «не впасти нізащо».
def fig_supervision_tree():
    W, H = 920, 452
    p = []
    # корінь
    rb, rw, rh = textbox(W / 2, 74, "наглядач хаба", size=12, pad=10,
                         fill=ACTBG, stroke=ACT, sw=2, color=ACT, bold=True, min_w=170)
    p.append(rb)
    # наглядачі кімнат
    rooms = [(240, "наглядач · вітальня"), (680, "наглядач · спальня")]
    ry = 168
    for rx, lbl in rooms:
        b, bw, bh = textbox(rx, ry, lbl, size=11, pad=9, fill="#efe7f8", stroke=ACT,
                            sw=1.7, color=INK, min_w=180)
        p.append(line(W / 2, 74 + rh / 2, rx, ry - bh / 2, color=ACT, sw=1.5))
        p.append(b)
    # листки-актори
    leaves_l = [(120, "термостат", True), (240, "розетка", False), (360, "давач", False)]
    leaves_r = [(560, "замок", False), (680, "лампа", False), (800, "камера", False)]
    ly = 300
    def draw_leaves(rx, leaves):
        for lx, lbl, crashed in leaves:
            col = POS if crashed else FIELD
            fill = "#fdecea" if crashed else "#eef6ef"
            b, bw, bh = textbox(lx, ly, lbl, size=10.5, pad=8, fill=fill, stroke=col,
                                sw=1.8, color=INK, min_w=104)
            p.append(line(rx, ry + 20, lx, ly - bh / 2, color="#b9a7d6", sw=1.3))
            p.append(b)
            if crashed:
                # хрест-падіння
                p.append(text(lx, ly - bh / 2 - 10, "✕ впав", size=10.5, color=POS, bold=True))
                # дуга-перезапуск назад до наглядача
                p.append(arrow(lx + bw / 2 + 4, ly, rx + 4, ry + 24, color=POS, sw=1.8))
    draw_leaves(240, leaves_l)
    draw_leaves(680, leaves_r)
    # пояснення перезапуску — окремою смугою внизу, під лівим кущем
    eb, ew, eh = textbox(240, 392, "наглядач перезапускає САМЕ термостат\nз чистого стану — решта дому працює",
                         size=10.5, pad=9, fill=WARNBG, stroke=WARN, sw=1.6, color=INK, bold=True, min_w=330)
    p.append(eb)
    p.append(text(680, 392, "брати по гілці — незворушні", size=10.5, color=FIELD, italic=True, bold=True))

    render(os.path.join(OUT, "supervision-tree.svg"), W, H, *p,
           title="Хай падає: впав один актор — перезапуск лише його")


# ── mailbox growth: прихована безмежність скриньки — ціна варіанта В ────────────
# Ідея: скринька — це черга. Якщо джерело шле швидше, ніж актор устигає (одне за
# раз), черга росте. Безмежна → памʼять вибухає (OOM). Обмежена → мусиш ОБРАТИ
# політику: відкинути зайве або притримати джерело (backpressure). Дармового буфера
# не буває.
def fig_mailbox_growth():
    W, H = 940, 384
    p = []
    # джерело
    sb, sbw, sbh = textbox(120, 150, "джерело\nподій", size=11.5, pad=10, fill="#eef2fc",
                           stroke=NEG, sw=1.8, color=NEG, bold=True, min_w=118)
    p.append(sb)
    p.append(arrow(120 + sbw / 2, 150, 300, 150, color=NEG, sw=3.4))
    p.append(text((120 + sbw / 2 + 300) / 2, 132, "швидко", size=10.5, color=NEG, italic=True))

    # скринька — стос клітин, що росте вгору
    qx, qcw, qch = 316, 150, 26
    n = 6
    qbase = 250
    for i in range(n):
        yy = qbase - i * (qch + 3)
        fade = "#efe7f8" if i < 4 else "#e3d4f4"
        p.append(rect(qx, yy, qcw, qch, fill=fade, stroke=ACT, sw=1.4, rx=4))
    p.append(text(qx + qcw / 2, qbase + qch + 20, "скринька росте", size=10.5, color=ACT, bold=True))
    # межа скриньки
    lim_y = qbase - 3 * (qch + 3) - 6
    p.append(line(qx - 16, lim_y, qx + qcw + 16, lim_y, color=POS, sw=1.8, dash="6 4"))
    p.append(text(qx + qcw + 24, lim_y + 4, "межа", size=10, color=POS, anchor="start", bold=True))

    # актор — повільний вихід
    ab, abw, abh = textbox(560, 150, "актор\nодне за раз", size=11.5, pad=10, fill=ACTBG,
                           stroke=ACT, sw=1.9, color=ACT, bold=True, min_w=128)
    p.append(arrow(qx + qcw, 150, 560 - abw / 2, 150, color=ACT, sw=1.4))
    p.append(text((qx + qcw + 560 - abw / 2) / 2, 132, "повільно", size=10.5, color=ACT, italic=True))
    p.append(ab)

    # дві розв'язки
    p.append(arrow(560 + abw / 2, 132, 700, 96, color=MUTED, sw=1.6))
    p.append(arrow(560 + abw / 2, 168, 700, 214, color=MUTED, sw=1.6))
    ob1, w1, h1 = textbox(806, 92, "безмежна скринька →\nпамʼять вибухає (OOM)",
                          size=10.5, pad=9, fill="#fdecea", stroke=POS, sw=1.7, color=POS, bold=True, min_w=228)
    p.append(ob1)
    ob2, w2, h2 = textbox(806, 218, "обмежена →  мусиш обрати:\nвідкинути чи притримати джерело",
                          size=10.5, pad=9, fill="#eef6ef", stroke=FIELD, sw=1.7, color=INK, bold=True, min_w=272)
    p.append(ob2)

    p.append(text(W / 2, H - 16, "скринька — прихована черга; дармового буфера не буває",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "mailbox-growth.svg"), W, H, *p,
           title="Ціна В: скринька — це черга, яку треба вгамувати")


# ── lineage timeline: телекомівський родовід «хай падає» (для hist-вставки) ─────
# Ідея: інженерна лінія надійності акторів — НЕ формалізм Хьюїтта, а телеком. Шість
# віх на осі: народження Erlang у лабораторії Ericsson → AXD301 і «дев'ять дев'яток»
# (з чесною зірочкою) → дисертація Армстронга з «хай падає» → WhatsApp → купівля
# Facebook → Discord (де гарячий шлях довелося винести в Rust). Кольори кодують суть:
# фіолет — ідея акторів, бурштин — цифра-із-заувагою, зелений — прод-доказ, синій —
# бізнес-подія. Підписи стаґеровано над/під віссю, щоб не налазили.
def fig_lineage_timeline():
    W, H = 1120, 452
    p = []
    axis_y = 214
    xs = [128, 288, 448, 608, 768, 940]
    p.append(line(xs[0] - 34, axis_y, xs[-1] + 40, axis_y, color="#c4ccd6", sw=2.4))
    p.append(text(xs[0] - 46, axis_y + 5, "час →", size=10.5, color=MUTED, anchor="end", italic=True))

    # (рік, підпис, колір, вгору?)
    nodes = [
        ("1986", "Erlang у лабораторії Ericsson\nАрмстронг · Вірдінг · Вільямс", ACT, False),
        ("1998", "AXD301 · >1 млн рядків Erlang\n«девʼять девʼяток» ⚠ із зірочкою", WARN, True),
        ("2003", "Дисертація Армстронга (KTH)\n«хай падає» + дерева нагляду", ACT, False),
        ("2012", "WhatsApp · ~2 млн зʼєднань\nна один сервер", FIELD, True),
        ("2014", "Facebook купує WhatsApp", NEG, False),
        ("2020", "Discord · 11 млн онлайн\nгарячий шлях → Rust", FIELD, True),
    ]
    for x, (year, lbl, col, up) in zip(xs, nodes):
        bgmap = {ACT: ACTBG, WARN: WARNBG, FIELD: "#eef6ef", NEG: "#eef2fc"}
        cy = 112 if up else 320
        box, bw, bh = textbox(x, cy, lbl, size=10.5, pad=9, fill=bgmap[col],
                              stroke=col, sw=1.8, color=INK, bold=False, min_w=212)
        # конектор від осі до близького краю рамки
        edge = cy + bh / 2 if up else cy - bh / 2
        p.append(line(x, axis_y, x, edge, color=col, sw=1.4, dash="4 4"))
        p.append(circle(x, axis_y, 7, fill=col, stroke=BG, sw=2))
        p.append(box)
        # рік — на дальшому від осі боці рамки, щоб не лягти на конектор
        yy = cy - bh / 2 - 12 if up else cy + bh / 2 + 22
        p.append(text(x, yy, year, size=14, color=col, bold=True))

    # наскрізна думка — смугою внизу
    p.append(text(W / 2, H - 20,
                  "Надійність тут будували, ПРИЙМАЮЧИ відмову, а не намагаючись її не допустити",
                  size=12, color=MUTED, italic=True))

    render(os.path.join(OUT, "lineage-timeline.svg"), W, H, *p,
           title="Телекомівський родовід «хай падає»: від комутатора до чатів планети")


# ── actor-loop: робочий актор-пристрій — типи, обмежена скринька, чисте ядро ──────
# Ідея (proj-вставка): чотири типи повідомлень падають в ОБМЕЖЕНУ скриньку; на її
# вінці — політика переповнення (відкинути / притримати); актор бере ОДНЕ за раз,
# крутить те саме чисте decide над ПРИВАТНИМ станом без замка; Query вертає Snapshot
# окремим каналом-відповіддю. Це «кістяк у мʼясі», якого база показала лише скелетом.
def fig_actor_loop():
    W, H = 1020, 500
    p = []
    # ── ліворуч: чотири типи повідомлень ──
    p.append(text(150, 92, "типи повідомлень", size=13, color=NEG, bold=True))
    msgs = [(120, "Tick"), (176, "SetThreshold{C}"), (232, "Command{action}"), (288, "Query{reply}")]
    for my, name in msgs:
        p.append(fitbox(40, my, 220, 42, name, size=11.5, pad=6, fill="#eaf0fd", stroke=NEG, sw=1.6))

    # ── скринька (обмежена FIFO) ──
    qx, qcw, qch, n = 366, 150, 24, 4
    qtop = 150
    for i in range(n):
        yy = qtop + i * (qch + 5)
        p.append(rect(qx, yy, qcw, qch, fill="#efe7f8", stroke=ACT, sw=1.4, rx=4))
    p.append(text(qx + qcw / 2, qtop - 16, "обмежена скринька · FIFO", size=11.5, color=ACT, bold=True))
    qbot = qtop + n * (qch + 5)
    p.append(line(qx - 14, qbot + 2, qx + qcw + 14, qbot + 2, color=POS, sw=1.8, dash="6 4"))
    p.append(text(qx + qcw + 20, qbot + 6, "межа: 64", size=10.5, color=POS, anchor="start", bold=True))
    # чотири стрілки у скриньку
    for k, (my, _) in enumerate(msgs):
        p.append(arrow(262, my + 21, qx - 3, qtop + 8 + k * (qch + 5), color=NEG, sw=1.4))
    # політика переповнення — окремою смугою під межею
    pol, pw, ph = textbox(qx + qcw / 2, qbot + 54, "повна → відкинути надлишок\nабо притримати джерело (зустрічний тиск)",
                          size=10, pad=8, fill=WARNBG, stroke=WARN, sw=1.6, color=INK, bold=True, min_w=280)
    p.append(pol)

    # ── актор: одне за раз, приватний стан, чисте decide ──
    ax, ay, aw, ah = 642, 116, 320, 194
    p.append(rect(ax, ay, aw, ah, fill=ACTBG, stroke=ACT, sw=2, rx=12))
    p.append(text(ax + aw / 2, ay + 26, "актор-термостат", size=13, color=ACT, bold=True))
    p.append(text(ax + aw / 2, ay + 45, "жодного замка", size=10.5, color=FIELD, italic=True, bold=True))
    p.append(fitbox(ax + 20, ay + 58, aw - 40, 30, "приватний стан:  { on, threshold }", size=10.5, pad=4,
                    fill=BG, stroke=ACT, sw=1.2))
    p.append(fitbox(ax + 20, ay + 100, aw - 40, 34, "чисте  decide(reading, threshold, on)", size=10.5, pad=4,
                    fill="#eef6ef", stroke=FIELD, sw=1.5))
    p.append(fitbox(ax + 20, ay + 144, aw - 40, 30, "actuate(on)  →  нагрівач", size=10.5, pad=4,
                    fill=BG, stroke=ACT, sw=1.2))
    # стрілка «одне за раз» зі скриньки в актор
    p.append(arrow(qx + qcw + 16, qtop + n * (qch + 5) / 2, ax - 3, ay + 78, color=ACT, sw=2))
    p.append(text((qx + qcw + ax) / 2 + 10, qtop + n * (qch + 5) / 2 - 12, "одне за раз",
                  size=11, color=ACT, italic=True, bold=True))

    # ── зворотний канал Query → Snapshot ──
    sny = ay + ah + 50
    snap, snw, snh = textbox(ax + aw / 2, sny, "Snapshot{ on, threshold }", size=10.5, pad=8,
                             fill="#eaf0fd", stroke=NEG, sw=1.6, color=NEG, bold=True, min_w=230)
    p.append(arrow(ax + aw / 2, ay + ah + 2, ax + aw / 2, sny - snh / 2 - 2, color=NEG, sw=1.6))
    p.append(text(ax + aw / 2 + snw / 2 + 16, (ay + ah + sny) / 2 + 2, "reply-канал",
                  size=10.5, color=NEG, italic=True, anchor="start", bold=True))
    p.append(snap)

    render(os.path.join(OUT, "actor-loop.svg"), W, H, *p,
           title="Робочий актор: типи → обмежена скринька → одне за раз → чисте decide")


# ── poison-restart: отруйне повідомлення — цикл рестарту й карантин; сусід живий ──
# Ідея: детермінований крах на КОЖЕН тік («отруєний» давач) дає не одне падіння, а
# ЦИКЛ. Наглядач має межу інтенсивності (BEAM: 3 рестарти / 5 с) — вичерпав → карантин,
# а не вічний рестарт. Сусід по гілці тіка далі: ізоляція справджується.
def fig_poison_restart():
    W, H = 1020, 430
    p = []
    t0, t1 = 176, 806

    # ── верхня доріжка: здоровий сусід ──
    yhi = 120
    p.append(text(56, yhi - 34, "сусід", size=12.5, color=FIELD, bold=True, anchor="start"))
    p.append(line(t0, yhi, t1, yhi, color="#cfd6de", sw=2))
    for i in range(6):
        x = t0 + i * ((t1 - t0) / 5)
        p.append(circle(x, yhi, 9, fill="#eef6ef", stroke=FIELD, sw=2))
    p.append(text((t0 + t1) / 2, yhi + 32, "тік · тік · тік — незворушно", size=11, color=FIELD, bold=True))
    p.append(text(t1 + 16, yhi + 4, "живий", size=11.5, color=FIELD, anchor="start", bold=True))

    # ── нижня доріжка: отруєний ──
    ylo = 286
    p.append(text(56, ylo - 34, "отруєний", size=12.5, color=POS, bold=True, anchor="start"))
    p.append(line(t0, ylo, t1, ylo, color="#cfd6de", sw=2))
    ev = [(t0 + 0, "тік"), (t0 + 92, "✕"), (t0 + 160, "⟳"),
          (t0 + 252, "тік"), (t0 + 344, "✕"), (t0 + 412, "⟳"),
          (t0 + 504, "тік"), (t0 + 596, "✕")]
    for x, sym in ev:
        if sym == "✕":
            p.append(text(x, ylo + 6, "✕", size=18, color=POS, bold=True))
            p.append(text(x, ylo - 18, "крах", size=9, color=POS))
        elif sym == "⟳":
            p.append(text(x, ylo + 7, "⟳", size=18, color=WARN, bold=True))
            p.append(text(x, ylo - 18, "рестарт", size=9, color=WARN))
        else:
            p.append(circle(x, ylo, 8, fill="#fdecea", stroke=POS, sw=1.8))
    # вікно інтенсивності
    wx0, wx1 = t0 - 14, t0 + 636
    p.append(rect(wx0, ylo - 60, wx1 - wx0, 120, fill="none", stroke=WARN, sw=1.5, rx=8))
    p.append(text((wx0 + wx1) / 2, ylo - 70, "вікно 5 с · межа 3 рестарти", size=10.5, color=WARN, bold=True))
    # карантин
    qb, qbw, qbh = textbox(t1 + 44, ylo, "КАРАНТИН\nбільше не рестартую", size=10, pad=9,
                           fill="#fdecea", stroke=POS, sw=1.9, color=POS, bold=True, min_w=150)
    p.append(arrow(t0 + 596 + 18, ylo, t1 + 44 - qbw / 2 - 4, ylo, color=POS, sw=1.8))
    p.append(qb)

    # висновок
    p.append(text(W / 2, H - 18, "детермінований крах → цикл рестарту → карантин (не вічний рестарт); сусід ізольований",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(OUT, "poison-restart.svg"), W, H, *p,
           title="Отрута: рестарт лікує збій, але не отруту — межа інтенсивності й карантин")


if __name__ == "__main__":
    fig_shared_vs_mailboxes()
    fig_supervision_tree()
    fig_mailbox_growth()
    fig_lineage_timeline()
    fig_actor_loop()
    fig_poison_restart()
    print("OK: figures written to", OUT)
