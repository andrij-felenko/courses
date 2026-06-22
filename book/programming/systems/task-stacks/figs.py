# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── stack-contents: що лежить у стеку задачі ──────────────────────────────────
# Ідея: стек задачі — стос блоків, що росте з кожним вкладеним викликом: знизу
# локальні тіла задачі, далі кадри викликів, зверху — збережений контекст.

def fig_stack_contents():
    W, H = 720, 380
    p = []
    bx, bw = 250, 230
    rows = [
        ("збережений контекст", "регістри, лічильник команд", "#fdecea", POS),
        ("кадр виклику C", "локальні C, адреса повернення", "#eaf0fd", NEG),
        ("кадр виклику B", "локальні B, адреса повернення", "#eaf0fd", NEG),
        ("кадр виклику A", "локальні A, адреса повернення", "#eaf0fd", NEG),
        ("локальні задачі", "змінні самого тіла задачі", "#eafaf0", FIELD),
    ]
    rh, top = 50, 70
    for i, (lab, sub, fill, col) in enumerate(rows):
        y = top + i * rh
        p.append(rect(bx, y, bw, rh, fill=fill, stroke=col, sw=1.6, rx=0))
        p.append(text(bx + bw / 2, y + 21, lab, size=12, color=col, bold=True))
        p.append(text(bx + bw / 2, y + 37, sub, size=9, color=MUTED))

    # вісь верх/низ
    ax = bx - 26
    p.append(line(ax, top + 4, ax, top + len(rows) * rh - 4, color=INK, sw=1.4))
    p.append(text(ax - 6, top + 12, "верх", size=10, color=MUTED, anchor="end"))
    p.append(text(ax - 6, top + len(rows) * rh - 2, "низ", size=10, color=MUTED, anchor="end"))

    # стрілка росту
    gx = bx + bw + 22
    p.append(text(gx, top + 100, "росте з кожним", size=11, color=INK, anchor="start"))
    p.append(text(gx, top + 116, "вкладеним викликом", size=11, color=INK, anchor="start", bold=True))
    p.append(arrow(gx + 8, top + 130, gx + 8, top + 30, color=INK, sw=1.7))

    render(os.path.join(OUT, "stack-contents.svg"), W, H, *p,
           title="Стек задачі: локальні, кадри викликів, збережений контекст")


# ── overflow: задача переходить межу й псує сусідню пам'ять ────────────────────
# Ідея: два сусідні блоки RAM; задача A «вилазить» за свою межу і пише в стек B,
# тож збій спливе в B, хоч винна A.

def fig_overflow():
    W, H = 720, 320
    p = []
    bx, bw = 120, 220
    top, bh = 80, 150
    gap = 60

    # стек A
    p.append(rect(bx, top, bw, bh, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(text(bx + bw / 2, top + 22, "стек задачі A", size=12, color=FIELD, bold=True))
    # «переповнення» — червона заливка, що вилазить за нижню межу A в зону B
    over_h = 70
    p.append(rect(bx + 18, top + bh - 30, bw - 36, over_h, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(bx + bw / 2, top + bh + 6, "вихід за межу", size=10, color=POS, bold=True))

    # стек B (сусід)
    bx2 = bx + bw + gap
    p.append(rect(bx2, top, bw, bh, fill="#eaf0fd", stroke=NEG, sw=1.8))
    p.append(text(bx2 + bw / 2, top + 22, "стек задачі B", size=12, color=NEG, bold=True))
    p.append(text(bx2 + bw / 2, top + bh / 2, "затерто «сміттям»", size=11, color=POS, bold=True))
    p.append(text(bx2 + bw / 2, top + bh / 2 + 18, "від задачі A", size=10, color=MUTED))

    # стрілка A → B
    p.append(arrow(bx + bw - 6, top + bh - 6, bx2 + 14, top + bh / 2 + 4, color=POS, sw=2.0))

    # підпис-висновок
    f = fitbox(120, top + bh + 38, bw * 2 + gap, 44,
               "Винна A, а падає B: причина й симптом — у різних місцях",
               size=12, fill="#fff6e0", stroke="#caa24a", sw=1.4, bold=True)
    p.append(f)

    render(os.path.join(OUT, "overflow.svg"), W, H, *p,
           title="Переповнення: задача псує сусідню пам'ять")


# ── ram-budget: уся RAM — один бюджет ─────────────────────────────────────────
# Ідея: одна смуга RAM, поділена на глобальні, стеки задач і купу; кожен зайвий
# кілобайт стека — кілобайт, якого бракуватиме деінде.

def fig_ram_budget():
    W, H = 720, 250
    p = []
    bx, by, bw, bh = 60, 100, 600, 60
    segs = [
        ("глобальні", 0.16, "#eef4ff"),
        ("стек A", 0.12, "#eafaf0"),
        ("стек B", 0.12, "#eafaf0"),
        ("стек C", 0.12, "#eafaf0"),
        ("купа", 0.30, "#fdf6e3"),
        ("вільно", 0.18, "#efefef"),
    ]
    p.append(text(bx, by - 16, "уся RAM чипа — один спільний бюджет", size=12, color=INK, anchor="start", bold=True))
    x = bx
    for lab, frac, fill in segs:
        w = bw * frac
        col = POS if lab == "вільно" else INK
        p.append(rect(x, by, w, bh, fill=fill, stroke=INK, sw=1.4, rx=0))
        p.append(text(x + w / 2, by + bh / 2 + 4, lab, size=10, color=col, bold=(lab == "вільно")))
        x += w

    p.append(text(W / 2, by + bh + 36,
                  "кожен зайвий кілобайт стека — кілобайт, якого бракуватиме деінде",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "ram-budget.svg"), W, H, *p,
           title="Бюджет RAM: усі стеки + купа + глобальні мусять уміститися")


# ── high-water: водяний знак показує найглибший прихід ────────────────────────
# Ідея: блок стека; затерта частина (використано) і незаймана (вільно);
# межа між ними — водяний знак; над ним лишають розумний запас.

def fig_high_water():
    W, H = 720, 350
    p = []
    bx, bw = 230, 240
    top, bh = 70, 200

    # увесь блок стека
    p.append(rect(bx, top, bw, bh, fill=BG, stroke=INK, sw=1.6))

    # використана (найглибший прихід) — згори вниз затерто
    used_h = bh * 0.66
    p.append(rect(bx, top, bw, used_h, fill="#fdecea", stroke="none", sw=0))
    p.append(text(bx + bw / 2, top + used_h / 2, "найглибше", size=12, color=POS, bold=True))
    p.append(text(bx + bw / 2, top + used_h / 2 + 18, "використання", size=11, color=POS))

    # незаймана — вільний запас
    p.append(text(bx + bw / 2, top + used_h + (bh - used_h) / 2 - 4, "так і не чіпали", size=11, color=FIELD, bold=True))
    p.append(text(bx + bw / 2, top + used_h + (bh - used_h) / 2 + 14, "(вільний запас)", size=10, color=MUTED))

    # лінія водяного знаку
    wy = top + used_h
    p.append(line(bx - 14, wy, bx + bw + 14, wy, color=NEG, sw=2.2, dash="7 4"))
    p.append(text(bx + bw + 22, wy + 4, "водяний знак", size=11, color=NEG, anchor="start", bold=True))

    # підпис рамок
    p.append(text(bx - 18, top + 12, "верх", size=9, color=MUTED, anchor="end"))
    p.append(text(bx - 18, top + bh - 2, "низ", size=9, color=MUTED, anchor="end"))

    # висновок
    f = fitbox(bx - 60, top + bh + 24, bw + 120, 40,
               "погнав під навантаженням → глянув знак → лишив запас над ним",
               size=11, fill="#fff6e0", stroke="#caa24a", sw=1.4, bold=True)
    p.append(f)

    render(os.path.join(OUT, "high-water.svg"), W, H, *p,
           title="Водяний знак: найглибше використання за весь час")


# ── big-array: великий локальний масив рве стек ───────────────────────────────
# Ідея: маленький стек і величезний buf[4096], що в нього не влазить; вихід —
# винести буфер у static або купу.

def fig_big_array():
    W, H = 720, 320
    p = []

    # лівий стовпець: ✗ масив на стеку
    lx, lw = 110, 200
    top, bh = 80, 160
    p.append(rect(lx, top, lw, bh, fill=BG, stroke=INK, sw=1.6))
    p.append(text(lx + lw / 2, top - 12, "стек задачі (4 КБ)", size=11, color=INK, bold=True))
    # буфер вилазить
    p.append(rect(lx + 16, top - 30, lw - 32, bh + 30, fill="#fdecea", stroke=POS, sw=1.8))
    p.append(text(lx + lw / 2, top + bh / 2 - 4, "char buf[4096]", size=12, color=POS, bold=True))
    p.append(text(lx + lw / 2, top + bh / 2 + 14, "не влазить — рве", size=10, color=POS))
    p.append(text(lx + lw / 2, top + bh + 30, "✗ буфер на стеку", size=11, color=POS, bold=True))

    # права колонка: ✓ винесений буфер
    rx, rw = 410, 200
    p.append(rect(rx, top, rw, bh, fill="#eafaf0", stroke=FIELD, sw=1.6))
    p.append(text(rx + rw / 2, top - 12, "стек задачі (4 КБ)", size=11, color=INK, bold=True))
    p.append(text(rx + rw / 2, top + bh / 2, "вільний — буфер", size=11, color=FIELD, bold=True))
    p.append(text(rx + rw / 2, top + bh / 2 + 18, "живе окремо", size=10, color=MUTED))
    # окремий блок static/купа
    p.append(rect(rx + 30, top + bh + 16, rw - 60, 40, fill="#eef4ff", stroke=NEG, sw=1.6))
    p.append(text(rx + rw / 2, top + bh + 40, "static / купа", size=11, color=NEG, bold=True))
    p.append(text(rx + rw / 2, top + bh + 74, "✓ буфер зі стека", size=11, color=FIELD, bold=True))

    # стрілка-перенесення
    p.append(arrow(lx + lw + 8, top + bh / 2, rx - 8, top + bh / 2, color=INK, sw=1.8))
    p.append(text((lx + lw + rx) / 2, top + bh / 2 - 10, "винести", size=10, color=INK, bold=True))

    render(os.path.join(OUT, "big-array.svg"), W, H, *p,
           title="Великий локальний масив рве стек — виносьте буфери")


# ── stack-vs-heap: стек у кожної задачі свій, купа — спільна ───────────────────
# Ідея: ліворуч кілька окремих стеків задач (фіксовані), праворуч один спільний
# пул купи (динамічний); обидва — в одній RAM.

def fig_stack_vs_heap():
    W, H = 720, 330
    p = []

    # ліва половина — стеки
    p.append(text(190, 64, "СТЕК — у кожної задачі свій", size=12, color=FIELD, bold=True))
    sx, sw, sh = 70, 70, 150
    for i in range(3):
        x = sx + i * (sw + 18)
        p.append(rect(x, 84, sw, sh, fill="#eafaf0", stroke=FIELD, sw=1.6))
        p.append(text(x + sw / 2, 84 + sh / 2 - 6, "стек", size=11, color=FIELD, bold=True))
        p.append(text(x + sw / 2, 84 + sh / 2 + 12, "задачі %d" % (i + 1), size=10, color=MUTED))
    p.append(text(190, 84 + sh + 22, "фіксований при створенні", size=10, color=MUTED))
    p.append(text(190, 84 + sh + 38, "локальні + виклики", size=10, color=MUTED))

    # роздільник
    p.append(line(W / 2, 80, W / 2, 252, color=MUTED, sw=1.2, dash="5 4"))

    # права половина — купа
    p.append(text(W / 2 + 170, 64, "КУПА — спільний пул", size=12, color=NEG, bold=True))
    hx, hw, hh = W / 2 + 40, 250, 150
    p.append(rect(hx, 84, hw, hh, fill="#eef4ff", stroke=NEG, sw=1.6))
    p.append(text(hx + hw / 2, 84 + 28, "malloc / new — динамічно", size=11, color=NEG, bold=True))
    p.append(text(hx + hw / 2, 84 + 56, "об'єкти RTOS: задачі,", size=10, color=MUTED))
    p.append(text(hx + hw / 2, 84 + 72, "черги, семафори", size=10, color=MUTED))
    p.append(text(hx + hw / 2, 84 + 104, "коли наперед не відомо,", size=10, color=MUTED))
    p.append(text(hx + hw / 2, 84 + 120, "скільки пам'яті треба", size=10, color=MUTED))

    # підпис — обидва в одній RAM
    f = fitbox(120, 268, W - 240, 40,
               "І стеки, і купа живуть в одній RAM; на ESP32 розмір стека задають у БАЙТАХ",
               size=11, fill="#fff6e0", stroke="#caa24a", sw=1.4, bold=True)
    p.append(f)

    render(os.path.join(OUT, "stack-vs-heap.svg"), W, H, *p,
           title="Стек (у кожної задачі свій) проти купи (спільної)")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки proj-stack-overflow.md (ловимо переповнення)
# ════════════════════════════════════════════════════════════════════════════

# ── paint-and-watermark: фарбування 0xA5 і водяний знак ───────────────────────
# Ідея: два блоки стека — «нормальний запас» (патерн майже цілий) і «майже
# переповнення» (патерн затерто майже дощенту); незаймана зона 0xA5 = watermark.

def fig_paint_and_watermark():
    W, H = 760, 420
    p = []
    top, bh = 80, 250
    bw = 180

    def stack(bx, used_frac, label, sub, col):
        out = [rect(bx, top, bw, bh, fill=BG, stroke=col, sw=2)]
        uh = bh * used_frac
        # затерта (використана) частина — згори
        out.append(rect(bx, top, bw, uh, fill=("#fdecea" if col == POS else "#eaf0fd"), stroke="none", sw=0))
        out.append(text(bx + bw / 2, top + uh / 2 - 4, "кадри викликів,", size=9, color=col))
        out.append(text(bx + bw / 2, top + uh / 2 + 10, "локальні змінні", size=9, color=col))
        # незаймана 0xA5
        for k in range(4):
            yy = top + uh + (bh - uh) * (k + 0.5) / 4
            if yy < top + bh - 4:
                out.append(text(bx + bw / 2, yy, "0xA5", size=9, color=FIELD, italic=True))
        # лінія watermark
        wy = top + uh
        out.append(line(bx - 12, wy, bx + bw + 12, wy, color=NEG, sw=2.0, dash="6 3"))
        # підписи
        out.append(text(bx - 16, top + 10, "межа", size=9, color=INK, anchor="end", bold=True))
        out.append(text(bx - 16, top + bh - 2, "дно", size=9, color=MUTED, anchor="end"))
        out.append(text(bx + bw / 2, top + bh + 22, label, size=11, color=col, bold=True))
        out.append(text(bx + bw / 2, top + bh + 38, sub, size=9, color=MUTED))
        return out, wy

    # лівий: нормальний запас
    frags, wy1 = stack(150, 0.55, "нормальний запас", "watermark далеко від межі", NEG)
    p += frags
    p.append(text(150 + bw + 18, wy1 + 4, "watermark", size=10, color=NEG, anchor="start", bold=True))

    # правий: майже переповнення
    frags, wy2 = stack(470, 0.94, "майже переповнення", "патерну майже не лишилось", POS)
    p += frags
    p.append(text(470 + bw + 18, wy2 + 4, "watermark ≈ 0", size=10, color=POS, anchor="start", bold=True))

    render(os.path.join(OUT, "paint-and-watermark.svg"), W, H, *p,
           title="Фарбування стека 0xA5: незайманий хвіст і є водяний знак")


# ── freertos-check-methods: метод 1 проти методу 2 ────────────────────────────
# Ідея: дві колонки; метод 1 звіряє лише SP (пропускає вистрибок між
# перемиканнями), метод 2 додатково перевіряє смугу патерну й ловить прокол.

def fig_freertos_check_methods():
    W, H = 760, 360
    p = []

    def panel(bx, title_txt, sub, miss, col, fill):
        out = []
        bw = 320
        out.append(fitbox(bx, 70, bw, 50, title_txt + "\n" + sub, size=10, fill=fill, stroke=col, sw=1.8, bold=True, color=col))
        # «осцилограма» SP із вистрибком за межу
        gx, gy, gw, gh = bx, 140, bw, 150
        out.append(rect(gx, gy, gw, gh, fill="#f6f8f6", stroke=MUTED, sw=1.0))
        base = gy + gh * 0.45      # рівень «SP норма»
        peak = gy + 16             # вершина вистрибка (за межу)
        x0 = gx + 10
        x1 = gx + gw * 0.42
        x2 = gx + gw * 0.50
        x3 = gx + gw * 0.58
        x4 = gx + gw - 10
        pts = "%.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f %.0f,%.0f" % (
            x0, base, x1, base, x2, peak, x2 + 2, peak, x3, base, x4, base)
        out.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>' % (pts, POS))
        out.append(line(gx + 6, base, gx + gw - 6, base, color=NEG, sw=1.4, dash="4 3"))
        out.append(text(gx + gw - 8, base - 6, "SP норма", size=9, color=NEG, anchor="end"))
        out.append(text(x2, peak - 6, "вистрибок", size=9, color=POS, bold=True))
        # смуга патерну біля дна
        out.append(rect(gx, gy + gh - 26, gw, 26, fill=("#fdecea" if miss else "#eafaf0"),
                        stroke=(POS if miss else FIELD), sw=1.2))
        out.append(text(gx + gw / 2, gy + gh - 9,
                        ("0xA5 затерто → ловить ✓" if not miss else "патерн не перевіряє"),
                        size=9, color=(FIELD if not miss else MUTED), bold=(not miss)))
        # вердикт
        out.append(text(bx + bw / 2, gy + gh + 22,
                        ("пропускає вистрибок ✗" if miss else "ловить прокол ✓"),
                        size=11, color=(POS if miss else FIELD), bold=True))
        return out

    p += panel(40, "Метод 1: лише SP", "configCHECK_FOR_STACK_OVERFLOW = 1", True, NEG, "#eaf0fd")
    p += panel(400, "Метод 2: SP + патерн", "configCHECK_FOR_STACK_OVERFLOW = 2", False, FIELD, "#eafaf0")

    # роздільник + загальний підпис
    p.append(line(W / 2, 130, W / 2, 300, color="#e4e4e4", sw=1.5))
    f = fitbox(40, 318, W - 80, 34,
               "Обидва спрацьовують при перемиканні контексту; на час налагодження лишають метод 2",
               size=10, fill="#fff6e0", stroke="#caa24a", sw=1.4, bold=True)
    p.append(f)

    render(os.path.join(OUT, "freertos-check-methods.svg"), W, H, *p,
           title="Два методи перевірки стека FreeRTOS")


# ════════════════════════════════════════════════════════════════════════════
#  Фігури вставки proj-no-free.md (пул фіксованих блоків)
# ════════════════════════════════════════════════════════════════════════════

# ── pool-freelist: масив блоків + список вільних ──────────────────────────────
# Ідея: статичний масив N×S; вільні блоки зшиті в ланцюг (кожен тримає вказівник
# на наступний вільний), голова freeList; alloc — зняти з голови, free — вернути.

def fig_pool_freelist():
    W, H = 760, 430
    p = []
    n = 8
    bx0, by, bw, bh, gap = 60, 110, 76, 50, 8
    free = {0, 1, 3, 5, 7}     # вільні блоки

    p.append(text(W / 2, 72, "static uint8_t pool[N][S]  —  N=8 блоків × S байтів", size=12, color=INK, bold=True))

    centers = []
    for i in range(n):
        x = bx0 + i * (bw + gap)
        isfree = i in free
        col = FIELD if isfree else NEG
        fill = "#eafaf0" if isfree else "#eaf0fd"
        p.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=2))
        p.append(text(x + bw / 2, by + 20, "pool[%d]" % i, size=11, color=col, bold=True))
        p.append(text(x + bw / 2, by + 37, ("→ ptr" if isfree else "(дані)"),
                      size=9, color=("#8a5fb0" if isfree else MUTED), italic=True))
        centers.append((x + bw / 2, x, x + bw))

    # ланцюг вільних: стрілки між сусідніми вільними блоками
    fl = sorted(free)
    for a, b in zip(fl, fl[1:]):
        xa = centers[a][2]
        xb = centers[b][1]
        ymid = by - 6
        p.append('<path d="M %.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>' % (
            xa, ymid, (xa + xb) / 2, by - 40, (xa + xb) / 2, by - 40, xb, ymid, "#8a5fb0"))
    p.append(text(centers[fl[-1]][2] + 16, by + 28, "NULL", size=11, color="#8a5fb0", anchor="start", bold=True))

    # голова freeList
    hx = centers[fl[0]][0]
    p.append(rect(hx - 45, by + bh + 28, 90, 38, fill="#fff6e0", stroke="#d06c00", sw=2))
    p.append(text(hx, by + bh + 52, "freeList", size=11, color="#d06c00", bold=True))
    p.append(arrow(hx, by + bh + 26, hx, by + bh + 2, color="#d06c00", sw=2))

    # легенда
    p.append(rect(60, by + bh + 90, 14, 14, fill="#eafaf0", stroke=FIELD, sw=1.5))
    p.append(text(80, by + bh + 101, "вільний блок (у free list)", size=10, color=FIELD, anchor="start"))
    p.append(rect(300, by + bh + 90, 14, 14, fill="#eaf0fd", stroke=NEG, sw=1.5))
    p.append(text(320, by + bh + 101, "зайнятий (у задачі)", size=10, color=NEG, anchor="start"))

    # alloc / free
    af = fitbox(60, by + bh + 124, 320, 56,
                "ALLOC — O(1): зняти з голови\np = freeList; freeList = *p",
                size=10, fill="#eafaf0", stroke=FIELD, sw=1.6, bold=True, color=FIELD)
    p.append(af)
    ff = fitbox(400, by + bh + 124, 300, 56,
                "FREE — O(1): повернути в голову\n*p = freeList; freeList = p",
                size=10, fill="#fdecea", stroke=POS, sw=1.6, bold=True, color=POS)
    p.append(ff)

    render(os.path.join(OUT, "pool-freelist.svg"), W, H, *p,
           title="Пул фіксованих блоків і список вільних")


# ── heap-vs-pool: купа фрагментується, пул — ні ───────────────────────────────
# Ідея: ліворуч купа з дірками між зайнятими блоками (фрагменти), праворуч
# рівний пул однакових блоків; внизу — підсумок переваг пулу.

def fig_heap_vs_pool():
    W, H = 760, 450
    p = []
    top = 80

    # ── купа ──
    hx, hw = 60, 300
    p.append(rect(hx, top, hw, 270, fill="#fff8f8", stroke=POS, sw=2))
    p.append(text(hx + hw / 2, top + 22, "Купа (heap)", size=14, color=POS, bold=True))
    rows = [("зайнято A", 38, True), ("дірка", 22, False), ("зайнято B", 48, True),
            ("дірка", 18, False), ("зайнято C", 56, True), ("дірка", 28, False)]
    y = top + 36
    for lab, hh, busy in rows:
        x = hx + 16
        w = hw - 32
        if busy:
            p.append(rect(x, y, w, hh, fill="#fbeaea", stroke=POS, sw=1.4, rx=2))
            p.append(text(x + w / 2, y + hh / 2 + 4, lab, size=10, color=POS, bold=True))
        else:
            p.append(rect(x, y, w, hh, fill=FILL, stroke=MUTED, sw=1.0, rx=2))
            p.append(text(x + w / 2, y + hh / 2 + 4, lab + " ←", size=9, color=MUTED, italic=True))
        y += hh + 4

    # ── пул ──
    px, pw = 400, 300
    p.append(rect(px, top, pw, 270, fill="#f0f8f2", stroke=FIELD, sw=2))
    p.append(text(px + pw / 2, top + 22, "Пул (fixed-size pool)", size=14, color=FIELD, bold=True))
    y = top + 36
    for i in range(6):
        x = px + 16
        w = pw - 32
        busy = i in (2, 4)
        col = NEG if busy else FIELD
        fill = "#e9eefb" if busy else "#eef6ef"
        p.append(rect(x, y, w, 34, fill=fill, stroke=col, sw=1.4, rx=2))
        p.append(text(x + w / 2, y + 21, "блок %d%s" % (i, " (у задачі)" if busy else ""),
                      size=10, color=col, bold=busy))
        y += 38
    p.append(text(px + pw / 2, y + 10, "N×S байтів — відомо НАПЕРЕД", size=10, color=FIELD, bold=True))

    # VS
    p.append(text(W / 2, top + 150, "VS", size=24, color=MUTED, bold=True))

    # підсумки
    lf = fitbox(60, top + 286, hw, 64,
                "рваний час malloc/free\nNULL зненацька через тижні\nфрагменти є — запит не влазить",
                size=9, fill="#fbeaea", stroke=POS, sw=1.6, color=POS, bold=True)
    p.append(lf)
    rf = fitbox(400, top + 286, pw, 64,
                "O(1) завжди — сталий час\nнуль фрагментації\nстеля пам'яті відома наперед",
                size=9, fill="#e8f6eb", stroke=FIELD, sw=1.6, color=FIELD, bold=True)
    p.append(rf)

    render(os.path.join(OUT, "heap-vs-pool.svg"), W, H, *p,
           title="Купа фрагментується, пул — ні")


if __name__ == "__main__":
    fig_stack_contents()
    fig_overflow()
    fig_ram_budget()
    fig_high_water()
    fig_big_array()
    fig_stack_vs_heap()
    fig_paint_and_watermark()
    fig_freertos_check_methods()
    fig_pool_freelist()
    fig_heap_vs_pool()
    print("OK: figures written to", OUT)
