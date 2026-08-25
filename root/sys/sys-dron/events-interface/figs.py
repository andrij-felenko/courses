# -*- coding: utf-8 -*-
"""Фігури до теми «Інтерфейс подій: коди з борту як людські повідомлення»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
if not os.path.isdir(IMG):
    os.makedirs(IMG)


# ── 1. Шлях однієї події: де що народжується ────────────────────────────────
def fig_event_path():
    W, H = 1320, 700
    f = []

    # ── борт
    px, py, pw, ph = 70, 80, 480, 540
    f.append(rect(px, py, pw, ph, fill="#ffffff", stroke=INK, sw=2))
    f.append(text(px + pw / 2.0, py + 36, "Борт", size=17, bold=True))

    left = [
        ("виклик у коді", "events::send(ID(\"commander_rtl\"),\nLog::Info, \"Returning to launch\")"),
        ("що лишається від рядка", "ID 0x01352ce4\naргументи: до 40 байтів\nlog_levels: два рівні"),
        ("в ефір", "EVENT · CURRENT_EVENT_SEQUENCE"),
    ]
    lyc = []
    for i, (head, body) in enumerate(left):
        by = py + 78 + i * 156
        f.append(text(px + 26, by + 16, head, size=12, color=MUTED, anchor="start"))
        f.append(fitbox(px + 26, by + 30, pw - 52, 88, body, size=13))
        lyc.append(by + 74)
        if i:
            f.append(arrow(px + pw / 2.0, by - 34, px + pw / 2.0, by + 22))

    # ── станція
    qx, qy, qw, qh = 770, 80, 480, 540
    f.append(rect(qx, qy, qw, qh, fill="#ffffff", stroke=INK, sw=2))
    f.append(text(qx + qw / 2.0, qy + 36, "Станція", size=17, bold=True))

    right = [
        ("порядок", "ReceiveProtocol:\nномер, пропуск, перезапит"),
        ("значення", "Parser + метадані з борту:\nID → текст, аргументи в підстановки"),
        ("призначення", "група події вирішує:\nрядок статусу · звіт готовності"),
    ]
    ryc = []
    for i, (head, body) in enumerate(right):
        by = qy + 78 + i * 156
        f.append(text(qx + 26, by + 16, head, size=12, color=MUTED, anchor="start"))
        f.append(fitbox(qx + 26, by + 30, qw - 52, 88, body, size=13))
        ryc.append(by + 74)
        if i:
            f.append(arrow(qx + qw / 2.0, by - 34, qx + qw / 2.0, by + 22))

    # ── канал
    f.append(arrow(px + pw + 16, lyc[2], qx - 16, ryc[0]))
    f.append(text((px + pw + qx) / 2.0, lyc[2] - 26, "радіоканал", size=12, color=MUTED))
    f.append(text((px + pw + qx) / 2.0, ryc[0] + 44, "жодного\nсимвола тексту", size=12, color=POS))

    # ── метадані окремою дорогою
    f.append(text(W / 2.0, H - 34,
                  "опис подій їде окремо й один раз — як файл метаданих компонента",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'event-path.svg'), W, H, *f,
           title="Що саме летить в ефір, а що народжується на землі")


# ── 2. Відновлення пропущеної події ─────────────────────────────────────────
def fig_sequence_recovery():
    W, H = 1460, 700
    f = []

    cols = [
        ("EVENT\nsequence 42",
         "очікувала 42 → приймає\n_latest = 42\nтаймер вимкнено", FIELD, "#eaf3ea"),
        ("EVENT\nsequence 44",
         "очікувала 43 → відкидає\nпросить 43\nтаймер 100 мс", POS, "#fdecea"),
        ("RESPONSE_EVENT_ERROR\nsequence 43\noldest available 45",
         "43 на борту вже немає\nвтрачено 1 подію\n_latest = 44, просить 45", POS, "#fdecea"),
        ("EVENT\nsequence 45",
         "очікувала 45 → приймає\n_latest = 45\nтаймер вимкнено", FIELD, "#eaf3ea"),
        ("CURRENT_EVENT_SEQUENCE\nsequence 47",
         "45 старіше за 47 →\nпросить 46", NEG, "#eaf0fd"),
    ]

    x0, cw, gap = 60, 250, 28
    top_y, bot_y = 92, 380
    for i, (msg, act, col, fillc) in enumerate(cols):
        cx = x0 + i * (cw + gap)
        f.append(fitbox(cx, top_y, cw, 118, msg, size=13, bold=True))
        f.append(arrow(cx + cw / 2.0, top_y + 130, cx + cw / 2.0, bot_y - 12))
        f.append(fitbox(cx, bot_y, cw, 122, act, size=13, fill=fillc, stroke=col, sw=2))

    f.append(text(x0, top_y - 26, "що прийшло з борту", size=13, color=MUTED, anchor="start"))
    f.append(text(x0, bot_y - 30, "що зробила станція", size=13, color=MUTED, anchor="start"))

    f.append(line(x0, 560, x0 + 5 * cw + 4 * gap, 560, color=MUTED, sw=1.5, dash="6,5"))
    f.append(text(W / 2.0, 604,
                  "порядковий номер дає пропуск помітити, широкомовний номер — помітити його в тиші",
                  size=13, color=MUTED))
    f.append(text(W / 2.0, 640,
                  "нова подія ніколи не заповнює діру: станція бере лише те, що йде за _latest",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'sequence-recovery.svg'), W, H, *f,
           title="Як станція помічає й закриває пропуск у подіях")


# ── 3. Звіт готовності, зібраний із трьох різновидів подій ──────────────────
def fig_arming_report():
    W, H = 1360, 700
    f = []

    steps = [
        ("arming_check, тип summary",
         "номер порції · маски помилок\nі попереджень по вузлах ·\nдозвіл зброїтися по групах режимів"),
        ("N подій-перевірок",
         "коротке повідомлення · опис ·\nмаска вражених груп режимів ·\nномер вузла · рівень"),
        ("health, тип summary",
         "номер порції · присутність вузлів ·\nїхні помилки й попередження"),
    ]

    sx, sw_ = 70, 460
    ycs = []
    for i, (head, body) in enumerate(steps):
        sy = 96 + i * 176
        f.append(text(sx + 8, sy - 14, head, size=14, bold=True, anchor="start"))
        f.append(fitbox(sx, sy, sw_, 106, body, size=13))
        ycs.append(sy + 53)
        if i:
            f.append(arrow(sx + sw_ / 2.0, sy - 62, sx + sw_ / 2.0, sy - 10))

    f.append(text(sx + sw_ / 2.0, 96 + 3 * 176 - 40,
                  "порядок жорсткий: збився — порція відкидається", size=12, color=MUTED))

    # ── результат
    rx, ry, rw, rh = 760, 96, 530, 460
    f.append(rect(rx, ry, rw, rh, fill="#ffffff", stroke=INK, sw=2))
    f.append(text(rx + rw / 2.0, ry + 34, "Звіт для поточного режиму", size=16, bold=True))

    rows = [
        ("зброїтися зараз", "можна", FIELD, "#eaf3ea"),
        ("злетіти", "можна", FIELD, "#eaf3ea"),
        ("почати місію", "ні: точність позиції замала", POS, "#fdecea"),
        ("вузол «gps»", "жовтий", "#b8860b", "#fdf6e3"),
    ]
    for i, (label, verdict, col, fillc) in enumerate(rows):
        yy = ry + 66 + i * 92
        f.append(text(rx + 26, yy + 34, label, size=14, anchor="start"))
        f.append(fitbox(rx + 230, yy, 276, 62, verdict, size=13, fill=fillc, stroke=col, sw=2))

    f.append(arrow(sx + sw_ + 20, ycs[1], rx - 20, ry + rh / 2.0))

    f.append(text(W / 2.0, H - 46,
                  "одна перевірка забороняє не політ узагалі, а конкретні групи режимів",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'arming-report.svg'), W, H, *f,
           title="Зі серії подій — таблиця дозволів")


# ── 4. Коло номерів: беззнакова різниця і межа UINT16_MAX/2 ────────────────
def fig_sequence_ring():
    W, H = 1380, 780
    f = []

    cx, cy, r = 400.0, 430.0, 225.0
    top, bot = cy - r, cy + r

    # півкола: праворуч «новіше», ліворуч «старіше»
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f Z" fill="#fdecea"/>'
             % (cx, top, r, r, cx, bot))
    f.append('<path d="M %.1f %.1f A %.1f %.1f 0 0 1 %.1f %.1f Z" fill="#eaf0fd"/>'
             % (cx, bot, r, r, cx, top))
    f.append(circle(cx, cy, r, fill="none", stroke=INK, sw=2))
    f.append(line(cx, top, cx, bot, color=INK, sw=2, dash="7,5"))

    f.append(fitbox(cx + 30, cy - 55, 170, 110,
                    "новіше\n1 … 32767\nдіра в нумерації",
                    size=13, fill="#ffffff", stroke=POS, sw=2))
    f.append(fitbox(cx - 200, cy - 55, 170, 110,
                    "старіше\n32768 … 65535\nдублікат",
                    size=13, fill="#ffffff", stroke=NEG, sw=2))

    f.append(circle(cx, top, 8, fill=FIELD, stroke=FIELD, sw=2))
    f.append(text(cx, top - 22, "diff = 0 — рівно: приймаємо", size=14, bold=True))
    f.append(circle(cx, bot, 8, fill=INK, stroke=INK, sw=2))
    f.append(text(cx, bot + 34, "межа: UINT16_MAX / 2 = 32767", size=14, bold=True))
    f.append(text(cx, bot + 66,
                  "diff = incoming − expected, беззнакове 16-бітове",
                  size=13, color=MUTED))

    # ── праворуч: чотири випадки в числах
    px = 770.0
    f.append(text(px + 280, 96, "Ті самі два рядки на переході через нуль",
                  size=16, bold=True))

    cases = [
        ("прийнято 65533, прийшла 65534\n"
         "diff = 65534 − 65534 = 0\n"
         "рівно: приймаємо, таймер геть", FIELD, "#eafaf0"),
        ("прийнято 65535, прийшла 1\n"
         "diff = 1 − 0 = 1   (≤ 32767)\n"
         "новіше: пропущено 0, просимо повтор", POS, "#fdecea"),
        ("прийнято 2, прийшла 65535\n"
         "diff = 65535 − 3 = 65532   (> 32767)\n"
         "старіше: дублікат, відкидаємо", NEG, "#eaf0fd"),
        ("прийнято 65531, найстаріше доступне 2\n"
         "втрачено = 2 − 65531 − 1 = 6\n"
         "це 65532, 65533, 65534, 65535, 0, 1", INK, "#f4f6f8"),
    ]
    for i, (body, col, fillc) in enumerate(cases):
        f.append(fitbox(px, 130 + i * 145, 560, 112, body,
                        size=14, fill=fillc, stroke=col, sw=2))

    render(os.path.join(IMG, 'sequence-ring.svg'), W, H, *f,
           title="Циклічне порівняння номерів однією беззнаковою різницею")


# ── 5. Розкладка байтів: кадр EVENT, байт рівнів, 32-бітовий ID ────────────
def fig_wire_layout():
    W, H = 1400, 660
    f = []

    # ── смуга 1: корисний вантаж EVENT
    f.append(text(70, 62, "EVENT (410) — 53 байти корисного вантажу, порядок як у кадрі",
                  size=15, bold=True, anchor="start"))

    fields = [
        ("id", "uint32_t", "0–3", 150),
        ("event_time_boot_ms", "uint32_t", "4–7", 205),
        ("sequence", "uint16_t", "8–9", 150),
        ("destination_component", "uint8_t", "10", 200),
        ("destination_system", "uint8_t", "11", 180),
        ("log_levels", "uint8_t", "12", 150),
        ("arguments[40]", "uint8_t[40]", "13–52", 175),
    ]
    bx, by, bh = 70, 78, 74
    for name, typ, rng, bw in fields:
        last = name.startswith("arguments")
        f.append(fitbox(bx, by, bw, bh, name + "\n" + typ, size=13,
                        fill="#eaf3ea" if last else FILL,
                        stroke=FIELD if last else LINE, sw=1.8))
        f.append(text(bx + bw / 2.0, by + bh + 24, rng, size=12, color=MUTED))
        bx += bw + 8

    f.append(text(70, 204,
                  "поля йдуть не в порядку XML: генератор сортує їх за спаданням розміру типу",
                  size=12, color=MUTED, anchor="start"))

    # ── смуга 2: байт log_levels
    f.append(text(70, 254, "log_levels — один байт, два рівні важливості",
                  size=15, bold=True, anchor="start"))

    cw, cgap = 76, 6
    cx0 = (W - (8 * cw + 7 * cgap)) / 2.0
    bits = [0, 1, 1, 0, 0, 0, 1, 0]          # приклад 0x62
    for i, b in enumerate(bits):
        cx = cx0 + i * (cw + cgap)
        inner = i < 4
        f.append(fitbox(cx, 310, cw, 54, str(b), size=20, bold=True,
                        fill="#eaf0fd" if inner else "#fdecea",
                        stroke=NEG if inner else POS, sw=2))
        f.append(text(cx + cw / 2.0, 388, "біт %d" % (7 - i), size=12, color=MUTED))

    hi_l, hi_r = cx0, cx0 + 4 * cw + 3 * cgap
    lo_l, lo_r = cx0 + 4 * (cw + cgap), cx0 + 8 * cw + 7 * cgap
    for l, r, lbl, col in ((hi_l, hi_r, "внутрішній рівень — журнал борту", NEG),
                           (lo_l, lo_r, "зовнішній рівень — екран пілота", POS)):
        f.append(line(l, 298, r, 298, color=col, sw=2))
        f.append(line(l, 292, l, 304, color=col, sw=2))
        f.append(line(r, 292, r, 304, color=col, sw=2))
        f.append(text((l + r) / 2.0, 284, lbl, size=13, color=col))

    f.append(text(W / 2.0, 418,
                  "0x62 → внутрішній 6 (Info), зовнішній 2 (Critical)", size=13))

    # ── смуга 3: 32-бітовий ідентифікатор
    f.append(text(70, 466, "ID події — 32 біти", size=15, bold=True, anchor="start"))

    bar_x, bar_w, bar_y, bar_h = 120, 1160, 482, 62
    comp_w = bar_w * 8 / 32.0
    f.append(fitbox(bar_x, bar_y, comp_w, bar_h, "біти 31…24\nномер компонента",
                    size=13, fill="#eaf0fd", stroke=NEG, sw=2))
    f.append(fitbox(bar_x + comp_w, bar_y, bar_w - comp_w, bar_h,
                    "біти 23…0 — молодша частина ідентифікатора (у PX4 це FNV-1a від імені)",
                    size=13, fill="#eaf3ea", stroke=FIELD, sw=2))

    f.append(text(bar_x + comp_w / 2.0, bar_y + bar_h + 28, "0x01", size=13, color=NEG))
    f.append(text(bar_x + comp_w + (bar_w - comp_w) / 2.0, bar_y + bar_h + 28,
                  "0x352ce4", size=13, color=FIELD))

    f.append(text(W / 2.0, 612,
                  "ID = 0x01352ce4 · ключ у JSON-метаданих — десяткове 3484900",
                  size=13, color=MUTED))

    render(os.path.join(IMG, 'wire-layout.svg'), W, H, *f,
           title="Три розкладки, з яких складається контракт подій")


if __name__ == '__main__':
    fig_event_path()
    fig_sequence_recovery()
    fig_arming_report()
    fig_sequence_ring()
    fig_wire_layout()
    print("ok")
