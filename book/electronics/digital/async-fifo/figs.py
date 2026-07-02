# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)

WCLK = "#c0392b"   # домен запису — теплий
RCLK = "#2457d6"   # домен читання — холодний


# ── Фігура 1: архітектура асинхронної FIFO ──────────────────────────────────
def fig_arch():
    W, H = 760, 430
    f = []

    # дві області тлом
    f.append(rect(20, 60, 340, 340, fill="#fdece9", stroke=WCLK, sw=1.5, rx=10))
    f.append(rect(400, 60, 340, 340, fill="#eaf0fd", stroke=RCLK, sw=1.5, rx=10))
    f.append(text(190, 84, "домен запису  ·  wr_clk", size=14, color=WCLK, bold=True))
    f.append(text(570, 84, "домен читання  ·  rd_clk", size=14, color=RCLK, bold=True))

    # спільна пам'ять по центру
    f.append(fitbox(300, 150, 160, 90,
                    "Двопортова\nпам'ять\n(RAM)", size=14, bold=True,
                    fill="#f4f6f8", stroke=INK, sw=2))
    f.append(text(380, 132, "спільна на обидва такти", size=11, color=MUTED))

    # порт запису
    f.append(fitbox(60, 160, 130, 70, "лічильник\nзапису\n(wr_ptr)",
                    size=13, bold=True, fill="#fff", stroke=WCLK, sw=1.8))
    f.append(arrow(190, 178, 300, 178, color=WCLK))
    f.append(text(245, 170, "адреса+дані", size=10, color=WCLK))

    # порт читання
    f.append(fitbox(570, 160, 130, 70, "лічильник\nчитання\n(rd_ptr)",
                    size=13, bold=True, fill="#fff", stroke=RCLK, sw=1.8))
    f.append(arrow(570, 178, 460, 178, color=RCLK))
    f.append(text(515, 170, "адреса", size=10, color=RCLK))

    # синхронізатори: wr_ptr -> домен читання
    f.append(fitbox(455, 275, 130, 56, "2 тригери\nsync", size=12,
                    fill="#fff", stroke=INK, sw=1.5))
    f.append(arrow(125, 230, 125, 355, color=WCLK))
    f.append(line(125, 355, 520, 355, color=WCLK, sw=1.8))
    f.append(arrow(520, 355, 520, 331, color=WCLK))
    f.append(text(300, 372, "wr_ptr у коді Грея  →  домен читання", size=11, color=WCLK))

    # синхронізатори: rd_ptr -> домен запису
    f.append(fitbox(175, 275, 130, 56, "2 тригери\nsync", size=12,
                    fill="#fff", stroke=INK, sw=1.5))
    f.append(arrow(635, 230, 635, 255, color=RCLK))
    f.append(line(635, 255, 240, 255, color=RCLK, sw=1.8))
    f.append(arrow(240, 255, 240, 275, color=RCLK))
    f.append(text(430, 248, "rd_ptr у коді Грея  →  домен запису", size=11, color=RCLK))

    # прапорці
    f.append(fitbox(60, 300, 105, 46, "ПОВНА?", size=13, bold=True,
                    fill="#fdece9", stroke=WCLK, sw=1.6))
    f.append(arrow(175, 303, 165, 313, color=INK, sw=1.4))
    f.append(fitbox(595, 300, 105, 46, "ПОРОЖНЯ?", size=13, bold=True,
                    fill="#eaf0fd", stroke=RCLK, sw=1.6))
    f.append(arrow(585, 303, 595, 313, color=INK, sw=1.4))

    render(os.path.join(IMG, 'arch.svg'), W, H, *f,
           title="Асинхронна FIFO: два лічильники, спільна пам'ять, вказівники навхрест")


# ── Фігура 2: кільцевий буфер, порожньо/повно й зайвий біт ───────────────────
def fig_ring():
    W, H = 760, 380
    f = []
    import math

    def wheel(cx, cy, r, filled, wp, rp, caption, sub):
        parts = []
        N = 8
        for i in range(N):
            a0 = -math.pi/2 + 2*math.pi*i/N
            a1 = -math.pi/2 + 2*math.pi*(i+1)/N
            am = (a0+a1)/2
            # сектор як проста «клітинка» — крапка + номер
            fx = cx + r*math.cos(am)
            fy = cy + r*math.sin(am)
            occupied = i in filled
            col = FIELD if occupied else "#dfe3e8"
            parts.append(circle(fx, fy, 15, fill=col, stroke=INK, sw=1.3))
            parts.append(text(fx, fy+4, str(i), size=11, color=INK if occupied else MUTED))
        # вказівники
        def ptr(idx, color, label, out):
            a = -math.pi/2 + 2*math.pi*idx/N
            rr = r + (34 if out else -34)
            px = cx + rr*math.cos(a)
            py = cy + rr*math.sin(a)
            tx = cx + (r-16)*math.cos(a)
            ty = cy + (r-16)*math.sin(a)
            hx = cx + (r+16)*math.cos(a)
            hy = cy + (r+16)*math.sin(a)
            parts.append(arrow(px, py, tx if out else hx, ty if out else hy, color=color, sw=2))
            parts.append(text(px, py-18 if out else py+22, label, size=12, color=color, bold=True))
        ptr(wp, WCLK, "W", True)
        ptr(rp, RCLK, "R", False)
        parts.append(text(cx, cy+r+56, caption, size=13, bold=True))
        parts.append(text(cx, cy+r+74, sub, size=11, color=MUTED))
        return parts

    # порожня: W == R (та сама клітинка, той самий зайвий біт)
    f += wheel(180, 150, 88, filled=set(), wp=2, rp=2,
               caption="ПОРОЖНЯ", sub="W = R повністю (і зайвий біт теж)")
    # повна: та сама адреса, але зайвий старший біт різний
    f += wheel(560, 150, 88, filled={2,3,4,5,6,7,0,1}, wp=2, rp=2,
               caption="ПОВНА", sub="адреса W = адреса R, але зайвий біт різний")

    # підпис про зайвий біт
    f.append(fitbox(210, 300, 340, 56,
                    "W наздогнав R «іззаду» на цілий круг — адреси збіглися,\n"
                    "та старший «оберт-біт» W уже інший. Ось як розрізнити повно й порожньо.",
                    size=11, fill="#f4f6f8", stroke=INK, sw=1.2))

    render(os.path.join(IMG, 'ring.svg'), W, H, *f,
           title="Кільцевий буфер: коли адреси W і R збіглися — це порожньо чи повно?")


# ── Фігура 3: лічильник у коді Грея через синхронізатор ──────────────────────
def fig_graysync():
    W, H = 760, 300
    f = []

    # двійковий проти Грея на переході
    rows = [
        ("двійковий wr_ptr", "0111 → 1000", "усі 4 біти разом", WCLK),
        ("код Грея wr_ptr",  "0100 → 1100", "рівно 1 біт",     FIELD),
    ]
    y = 78
    f.append(text(40, 56, "той самий крок вказівника (7→8):", size=13, bold=True, anchor="start"))
    for name, val, note, col in rows:
        f.append(text(50, y+5, name, size=12, anchor="start", color=INK))
        f.append(fitbox(230, y-18, 150, 40, val, size=14, bold=True,
                        fill="#fff", stroke=col, sw=1.8))
        f.append(text(405, y+5, note, size=12, anchor="start", color=col, bold=True))
        y += 66

    # синхронізатор
    f.append(line(40, 210, 720, 210, color=MUTED, sw=1, dash="4 4"))
    f.append(text(40, 236, "чому саме Грей рятує на межі:", size=13, bold=True, anchor="start"))
    f.append(fitbox(50, 250, 150, 40, "wr_ptr\n(Грей)", size=12, bold=True,
                    fill="#fdece9", stroke=WCLK, sw=1.6))
    f.append(arrow(200, 270, 250, 270, color=INK, sw=1.6))
    f.append(fitbox(250, 250, 90, 40, "тр.1", size=12, fill="#fff", stroke=INK))
    f.append(arrow(340, 270, 380, 270, color=INK, sw=1.6))
    f.append(fitbox(380, 250, 90, 40, "тр.2", size=12, fill="#fff", stroke=INK))
    f.append(arrow(470, 270, 520, 270, color=INK, sw=1.6))
    f.append(fitbox(520, 250, 190, 40,
                    "приймач бачить\nстаре АБО нове", size=11, bold=True,
                    fill="#eaf0fd", stroke=RCLK, sw=1.6))

    render(os.path.join(IMG, 'graysync.svg'), W, H, *f,
           title="Вказівник рахує в коді Грея — на межі домену міняється лише 1 біт")


# ════════════════════════════════════════════════════════════════════════════
# Фігури для вставки proj-ring-buffer.md — програмна FIFO між двома контекстами
# ════════════════════════════════════════════════════════════════════════════

PROD = WCLK   # продюсер / письменник — теплий
CONS = RCLK   # споживач / читач — холодний


# ── Контракт власності: один хазяїн на індекс ────────────────────────────────
def fig_sw_owner():
    W, H = 760, 380
    f = []

    f.append(rect(20, 60, 250, 250, fill="#fdece9", stroke=PROD, sw=1.5, rx=10))
    f.append(rect(490, 60, 250, 250, fill="#eaf0fd", stroke=CONS, sw=1.5, rx=10))
    f.append(text(145, 84, "ПРОДЮСЕР", size=14, color=PROD, bold=True))
    f.append(text(145, 102, "(напр. ISR давача)", size=11, color=MUTED))
    f.append(text(615, 84, "СПОЖИВАЧ", size=14, color=CONS, bold=True))
    f.append(text(615, 102, "(напр. main-цикл)", size=11, color=MUTED))

    N = 6
    cw = 34
    x0 = 380 - N*cw/2
    cy = 150
    for i in range(N):
        col = FIELD if i in (2, 3) else "#eef1f4"
        f.append(rect(x0 + i*cw, cy, cw, 34, fill=col, stroke=INK, sw=1.3, rx=4))
        f.append(text(x0 + i*cw + cw/2, cy + 22, str(i), size=11,
                      color=INK if i in (2, 3) else MUTED))
    f.append(text(380, cy - 14, "спільний масив buf[N]", size=12, bold=True))
    f.append(text(380, cy + 60, "зелене — зайняті слоти (дані є)", size=10, color=MUTED))

    f.append(fitbox(120, 190, 130, 46, "head\n(пише лише продюсер)",
                    size=11, bold=True, fill="#fff", stroke=PROD, sw=1.8))
    f.append(arrow(185, 190, x0 + 4*cw + cw/2, cy + 34, color=PROD, sw=2))

    f.append(fitbox(510, 190, 130, 46, "tail\n(пише лише споживач)",
                    size=11, bold=True, fill="#fff", stroke=CONS, sw=1.8))
    f.append(arrow(575, 190, x0 + 2*cw + cw/2, cy + 34, color=CONS, sw=2))

    f.append(fitbox(150, 300, 460, 56,
                    "Кожен індекс має РІВНО ОДНОГО хазяїна, що його змінює.\n"
                    "Чужий індекс кожен лише ЧИТАЄ — а читання вирівняного слова цілісне.\n"
                    "Звідси: замок не потрібен, гонки немає за побудовою.",
                    size=11, fill="#f4f6f8", stroke=INK, sw=1.2))

    render(os.path.join(IMG, 'sw-owner.svg'), W, H, *f,
           title="Програмна FIFO: один хазяїн на індекс — контракт SPSC")


# ── Порядок публікації: дані раніше за head ──────────────────────────────────
def fig_sw_order():
    W, H = 760, 340
    f = []

    def slot(x, y, val, col, sub):
        parts = [rect(x, y, 150, 44, fill="#fff", stroke=col, sw=1.8, rx=6)]
        parts.append(text(x + 75, y + 28, val, size=14, color=col, bold=True))
        parts.append(text(x + 75, y + 60, sub, size=10, color=MUTED))
        return parts

    f.append(text(40, 66, "ПРАВИЛЬНО — публікуй ОСТАННІМ:", size=13, bold=True, anchor="start", color=FIELD))
    f += slot(60, 82, "buf[head]=x", FIELD, "1) спершу дані")
    f.append(arrow(210, 104, 260, 104, color=INK, sw=1.6))
    f += slot(260, 82, "head = next", FIELD, "2) потім опублікувати")
    f.append(arrow(410, 104, 460, 104, color=INK, sw=1.6))
    f += slot(460, 82, "споживач бачить\nповний слот", FIELD, "дані вже на місці")

    f.append(line(40, 176, 720, 176, color=MUTED, sw=1, dash="4 4"))
    f.append(text(40, 206, "НЕПРАВИЛЬНО — переставив місцями:", size=13, bold=True, anchor="start", color=PROD))
    f += slot(60, 222, "head = next", PROD, "1) посунув head")
    f.append(arrow(210, 244, 260, 244, color=INK, sw=1.6))
    f += slot(260, 222, "(перемикання\nконтексту тут)", PROD, "споживача пустили")
    f.append(arrow(410, 244, 460, 244, color=INK, sw=1.6))
    f += slot(460, 222, "читає ПОРОЖНІЙ\nслот → сміття", PROD, "дані ще не лягли")

    render(os.path.join(IMG, 'sw-order.svg'), W, H, *f,
           title="Публікуй рух індексу ОСТАННІМ: спершу дані, потім head")


# ── Одне ядро vs два ядра: коли досить volatile, коли треба бар'єр ────────────
def fig_sw_barrier():
    W, H = 760, 330
    f = []

    f.append(rect(20, 56, 350, 240, fill="#f4f6f8", stroke=INK, sw=1.4, rx=10))
    f.append(text(195, 82, "ОДНЕ ЯДРО: ISR ⇄ main", size=14, bold=True))
    f.append(fitbox(50, 100, 290, 44,
                    "ISR витісняє main, але виконання СЕРІЙНЕ:\nодин потік команд, один порядок пам'яті",
                    size=11, fill="#fff", stroke=INK, sw=1.2))
    f.append(fitbox(70, 165, 250, 40, "досить: volatile", size=13, bold=True,
                    fill="#eafaf0", stroke=FIELD, sw=1.8))
    f.append(fitbox(50, 220, 290, 56,
                    "volatile забороняє КОМПІЛЯТОРУ кешувати індекс\n"
                    "і міняти місцями запис даних та публікацію.\n"
                    "Порядку інструкцій на одному ядрі — достатньо.",
                    size=10, fill="#fff", stroke=MUTED, sw=1))

    f.append(rect(390, 56, 350, 240, fill="#f4f6f8", stroke=INK, sw=1.4, rx=10))
    f.append(text(565, 82, "ДВА ЯДРА: core0 ∥ core1", size=14, bold=True))
    f.append(fitbox(420, 100, 290, 44,
                    "СПРАВЖНЯ паралельність: кожне ядро й пам'ять\nможуть переупорядкувати доступи одне щодо одного",
                    size=11, fill="#fff", stroke=INK, sw=1.2))
    f.append(fitbox(440, 165, 250, 40, "треба: release / acquire бар'єр", size=12, bold=True,
                    fill="#fdece9", stroke=PROD, sw=1.8))
    f.append(fitbox(420, 220, 290, 56,
                    "volatile мовчить про ІНШЕ ядро. Бар'єр release у\n"
                    "продюсера + acquire у споживача гарантують: дані\n"
                    "видно ДО того, як видно новий head. (Мова FIFO в софті.)",
                    size=10, fill="#fff", stroke=MUTED, sw=1))

    render(os.path.join(IMG, 'sw-barrier.svg'), W, H, *f,
           title="volatile проти бар'єра: одне ядро — порядок; два ядра — бар'єр")


# ════════════════════════════════════════════════════════════════════════════
# Фігури для вставки hist-cummings-fifo.md — історія канонічної конструкції
# ════════════════════════════════════════════════════════════════════════════


# ── Невідтворюваний баг «чесної» побітної синхронізації вказівника ────────────
def fig_hist_glitch():
    W, H = 760, 340
    f = []

    f.append(text(W/2, 52, "вказівник запису йде з 7 (0111) у 8 (1000): усі 4 біти разом",
                  size=13, bold=True))

    bits = [("b3", "0", "1"), ("b2", "1", "0"), ("b1", "1", "0"), ("b0", "1", "0")]
    x0, dx = 130, 120
    top_y = 96
    for i, (nm, old, new) in enumerate(bits):
        cx = x0 + i*dx
        f.append(text(cx, top_y - 12, nm, size=12, color=MUTED))
        f.append(fitbox(cx-44, top_y, 38, 34, old, size=15, bold=True,
                        fill="#fdece9", stroke=WCLK, sw=1.6))
        f.append(text(cx, top_y+22, "→", size=15, bold=True))
        f.append(fitbox(cx+6, top_y, 38, 34, new, size=15, bold=True,
                        fill="#eaf0fd", stroke=RCLK, sw=1.6))
        f.append(fitbox(cx-44, top_y+52, 88, 30, "свій sync", size=11,
                        fill="#fff", stroke=INK, sw=1.3))
        f.append(arrow(cx, top_y+40, cx, top_y+52, color=INK, sw=1.3))
        f.append(arrow(cx, top_y+82, cx, top_y+100, color=INK, sw=1.3))

    f.append(fitbox(x0-44, top_y+100, dx*3+88, 40,
                    "на нещасливому такті одні біти встигли, інші — ні",
                    size=12, bold=True, fill="#f4f6f8", stroke=MUTED, sw=1.3))

    f.append(text(W/2, top_y+168, "приймач бачить, наприклад:", size=12, color=INK))
    f.append(fitbox(W/2-70, top_y+178, 140, 38, "1111 = 15", size=16, bold=True,
                    fill="#fdf6d8", stroke=POS, sw=1.8))
    f.append(text(W/2, top_y+236,
                  "числа, якого не було — то губить байт, то ні: невідтворювано",
                  size=12, bold=True, color=POS))

    render(os.path.join(IMG, 'hist-glitch.svg'), W, H, *f,
           title="Чому «чесна» побітна синхронізація вказівника давала плавучі збої")


# ── Часова смуга: шматки лежали нарізно, тоді Каммінгс звів їх у канон ─────────
def fig_hist_timeline():
    W, H = 780, 300
    f = []

    y = 150
    f.append(line(60, y, 720, y, color=MUTED, sw=2))
    f.append(arrow(700, y, 722, y, color=MUTED, sw=2))

    marks = [
        (140, "1953", "код Грея", "патент Френка Грея,\nлабораторії Белла", FIELD, True),
        (330, "≈1969", "перша FIFO", "апаратна черга,\nПітер Альфке, Fairchild", INK, True),
        (500, "1990-ті", "розкол практик", "кожен свій обхід —\nневідтворювані баги", POS, False),
        (660, "2002", "канон", "SNUG: Каммінгс зводить\nшматки в один еталон", RCLK, True),
    ]
    for x, yr, ttl, sub, col, up in marks:
        f.append(circle(x, y, 8, fill=col, stroke=INK, sw=1.6))
        if up:
            f.append(text(x, y-58, yr, size=13, bold=True, color=col))
            f.append(fitbox(x-84, y-48, 168, 38, ttl, size=13, bold=True,
                            fill="#fff", stroke=col, sw=1.5))
            f.append(mtext(x, y-86, sub, size=10, color=MUTED))
            f.append(line(x, y-8, x, y-24, color=col, sw=1.4))
        else:
            f.append(text(x, y+74, yr, size=13, bold=True, color=col))
            f.append(fitbox(x-84, y+30, 168, 38, ttl, size=13, bold=True,
                            fill="#fdf0ee", stroke=col, sw=1.5))
            f.append(mtext(x, y+94, sub, size=10, color=MUTED))
            f.append(line(x, y+8, x, y+30, color=col, sw=1.4))

    render(os.path.join(IMG, 'hist-timeline.svg'), W, H, *f,
           title="Складники лежали нарізно десятиліттями — Каммінгс звів їх у канон")


if __name__ == '__main__':
    fig_arch()
    fig_ring()
    fig_graysync()
    fig_sw_owner()
    fig_sw_order()
    fig_sw_barrier()
    fig_hist_glitch()
    fig_hist_timeline()
    print("ok")
