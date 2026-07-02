# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «MAVLink із землі».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: виявлення апарата й обрив за серцебиттям ───────────────────────
# Ідея: ритмічний HEARTBEAT = апарат живий на мапі; пропуск кількох поспіль =
# мертвий лінк → станція гасить індикатори, борт іде у failsafe. Той самий
# потік дає і появу, і зникнення.
def fig_heartbeat_discovery():
    W, H = 940, 430
    P = []
    P.append(text(W / 2, 30, "HEARTBEAT: поява, опис і обрив — з одного потоку",
                  size=17, bold=True))

    # вісь часу
    ax_y = 150
    ax_x0, ax_x1 = 70, W - 60
    P.append(line(ax_x0, ax_y, ax_x1, ax_y, color=MUTED, sw=1.5))
    P.append(text(ax_x1, ax_y + 26, "час →", size=12, color=MUTED, anchor="end"))

    # серцебиття раз на секунду: спочатку ритмічно, потім пропуски
    beats = [0, 1, 2, 3, 4]          # прийшли
    missed = [5, 6, 7]               # пропущені
    step = (ax_x1 - ax_x0 - 40) / 8.0
    bx = ax_x0 + 30

    def pulse(x, alive=True):
        col = FIELD if alive else MUTED
        # маленький імпульс-«пік» над віссю
        s = (line(x - 9, ax_y, x - 4, ax_y, color=col, sw=2) +
             line(x - 4, ax_y, x, ax_y - 34, color=col, sw=2) +
             line(x, ax_y - 34, x + 4, ax_y, color=col, sw=2) +
             line(x + 4, ax_y, x + 9, ax_y, color=col, sw=2))
        return s

    for i in beats:
        x = bx + i * step
        P.append(pulse(x, True))
        P.append(text(x, ax_y + 20, "1с", size=10, color=MUTED))
    for i in missed:
        x = bx + i * step
        # пунктир туди, де серцебиття мало б бути
        P.append(line(x, ax_y - 34, x, ax_y, color=POS, sw=1.4, dash="3,4"))
        P.append(text(x, ax_y - 42, "✕", size=15, color=POS, bold=True))

    # підписи фаз
    fr, w1, h1 = textbox(bx + 2 * step, ax_y + 60, "ритмічно →\nапарат живий",
                         size=12, color=FIELD, bold=True, fill="#e9f7ef", stroke=FIELD)
    P.append(fr)
    fr, w2, h2 = textbox(bx + 6 * step, ax_y + 60, "пропуск 2–3 поспіль →\nлінк мертвий",
                         size=12, color=POS, bold=True, fill="#fdecea", stroke=POS)
    P.append(fr)

    # наслідки внизу: дві сторони
    by = 320
    fr, w, h = textbox(W * 0.27, by, "на ЗЕМЛІ:\nгасне мітка на мапі,\nстанція б'є на сполох",
                       size=12.5, fill="#eef2f7", stroke=INK)
    P.append(fr)
    fr, w, h = textbox(W * 0.73, by, "на БОРТУ:\nне чує серцебиття GCS →\nfailsafe (RTL / посадка)",
                       size=12.5, fill="#eef2f7", stroke=INK)
    P.append(fr)
    P.append(arrow(bx + 6 * step, ax_y + 90, W * 0.27, by - 34, color=POS))
    P.append(arrow(bx + 6 * step, ax_y + 90, W * 0.73, by - 34, color=POS))

    render("img/heartbeat-discovery.svg", W, H, *P)


# ── Фігура 2: потік телеметрії — різні швидкості за замовленням станції ──────
# Ідея: станція ОДИН раз замовляє швидкості; борт сам ллє кожен тип зі своєю
# частотою. Швидке/критичне — часто; повільне — рідко. Вузький канал не тоне.
def fig_telemetry_stream():
    W, H = 940, 470
    P = []
    P.append(text(W / 2, 30, "Телеметрія вниз: кожен тип — зі своєю частотою",
                  size=17, bold=True))

    # ліворуч — борт, праворуч — станція; одне замовлення вгору
    bx, sx = 110, W - 110
    by = 250
    fr, w, h = textbox(bx, by, "БОРТ\n(автопілот)", size=13, bold=True,
                       fill="#eef2f7", stroke=INK, min_w=130)
    P.append(fr)
    fr, w, h = textbox(sx, by, "НАЗЕМНА\nСТАНЦІЯ", size=13, bold=True,
                       fill="#eef2f7", stroke=INK, min_w=130)
    P.append(fr)

    # одноразове замовлення (вгору)
    P.append(arrow(sx - 70, by - 70, bx + 70, by - 70, color=NEG))
    P.append(text(W / 2, by - 80, "1 раз: «замовляю швидкості потоків»",
                  size=12, color=NEG, bold=True))

    # чотири потоки вниз із різною «щільністю» крапок = частотою
    rows = [
        ("ATTITUDE — кути крену/тангажу", "~10–50/с", FIELD, 14),
        ("GLOBAL_POSITION — координати", "~3–5/с", INK, 7),
        ("SYS_STATUS — заряд, напруга", "~1–2/с", MUTED, 3),
        ("HEARTBEAT — я живий + режим", "~1/с", POS, 2),
    ]
    y0 = by + 60
    lane_x0, lane_x1 = bx + 80, sx - 80
    for i, (name, rate, col, n) in enumerate(rows):
        y = y0 + i * 42
        P.append(line(lane_x0, y, lane_x1, y, color="#d0d5dd", sw=1.2))
        # крапки-пакети: що частіше, то більше
        for k in range(n):
            px = lane_x0 + 12 + k * (lane_x1 - lane_x0 - 24) / max(1, n - 1) if n > 1 else (lane_x0 + lane_x1) / 2
            P.append(circle(px, y, 4.5, fill=col, stroke=col))
        # стрілка напрямку (вниз = до станції, тобто ліворуч→праворуч тут)
        P.append(text(lane_x0 - 8, y + 4, "▶", size=11, color=col, anchor="end"))
        P.append(text(lane_x0 + 6, y - 12, name, size=11.5, color=INK, anchor="start"))
        P.append(text(lane_x1, y - 12, rate, size=11.5, color=col, bold=True, anchor="end"))

    P.append(text(W / 2, H - 24,
                  "часто й критичне — густо; повільне — зрідка → вузький канал не захлинається",
                  size=12.5, color=MUTED))
    render("img/telemetry-stream.svg", W, H, *P)


# ── Фігура 3: команда без / з підтвердженням ────────────────────────────────
# Ідея: сліпий постріл (втрата → оператор не знає) проти діалогу (ACK + повтор
# по таймауту). Підтвердження робить разову дію надійною на дірявому каналі.
def fig_command_ack():
    W, H = 960, 470
    P = []
    P.append(text(W / 2, 30, "Разова команда: чому потрібне підтвердження",
                  size=17, bold=True))

    midx = W / 2
    P.append(line(midx, 55, midx, H - 30, color="#d0d5dd", sw=1.2, dash="5,5"))

    # ── ліва панель: наївно ──
    lx_g, lx_b = 80, midx - 80      # GCS / борт колонки зліва
    P.append(text((lx_g + lx_b) / 2, 60, "наївно: вистрелив і забув",
                  size=13.5, bold=True, color=POS))
    P.append(text(lx_g, 92, "GCS", size=12, bold=True))
    P.append(text(lx_b, 92, "борт", size=12, bold=True))
    P.append(line(lx_g, 100, lx_g, H - 60, color=MUTED, sw=1.2))
    P.append(line(lx_b, 100, lx_b, H - 60, color=MUTED, sw=1.2))
    # команда, що губиться
    P.append(line(lx_g, 150, (lx_g + lx_b) / 2 + 10, 185, color=NEG, sw=2))
    P.append(text(lx_g + 14, 142, "COMMAND_LONG (arm)", size=11, color=NEG, anchor="start"))
    P.append(text((lx_g + lx_b) / 2 + 26, 195, "✕ втрата", size=12, color=POS, bold=True, anchor="start"))
    fr, w, h = textbox((lx_g + lx_b) / 2, 300,
                       "оператор бачить\nТИШУ:\nдійшло? ні?\nневідомо",
                       size=12, fill="#fdecea", stroke=POS, color=POS, bold=True)
    P.append(fr)

    # ── права панель: з ACK ──
    rx_g, rx_b = midx + 80, W - 80
    P.append(text((rx_g + rx_b) / 2, 60, "як треба: команда + ACK",
                  size=13.5, bold=True, color=FIELD))
    P.append(text(rx_g, 92, "GCS", size=12, bold=True))
    P.append(text(rx_b, 92, "борт", size=12, bold=True))
    P.append(line(rx_g, 100, rx_g, H - 40, color=MUTED, sw=1.2))
    P.append(line(rx_b, 100, rx_b, H - 40, color=MUTED, sw=1.2))
    # команда →
    P.append(arrow(rx_g, 140, rx_b, 165, color=NEG))
    P.append(text(rx_g + 12, 132, "COMMAND_LONG (arm)", size=11, color=NEG, anchor="start"))
    # ACK ←
    P.append(arrow(rx_b, 205, rx_g, 230, color=FIELD))
    P.append(text(rx_b - 12, 197, "COMMAND_ACK: ACCEPTED", size=11, color=FIELD, anchor="end", bold=True))
    # таймаут-повтор
    P.append(line(rx_g, 285, rx_g - 40, 285, color=POS, sw=1.6, dash="3,4"))
    P.append(line(rx_g - 40, 285, rx_g - 40, 330, color=POS, sw=1.6, dash="3,4"))
    P.append(arrow(rx_g - 40, 330, rx_g, 330, color=POS))
    P.append(text(rx_g - 44, 312, "немає ACK за таймаут →\nповторюю ТУ САМУ команду",
                  size=10.5, color=POS, anchor="end"))
    fr, w, h = textbox((rx_g + rx_b) / 2, 410,
                       "діалог: знаю результат,\nповтор не зашкодить",
                       size=12, fill="#e9f7ef", stroke=FIELD, color=FIELD, bold=True)
    P.append(fr)

    render("img/command-ack.svg", W, H, *P)


# ── Фігура 4: завантаження місії — рукостискання й номери ───────────────────
# Ідея: борт САМ тягне точки за номерами; втрата → повтор останнього кроку;
# порядок гарантовано індексами; фінальний ACK = весь маршрут цілий.
def fig_mission_upload():
    W, H = 960, 560
    P = []
    P.append(text(W / 2, 30, "Завантаження місії: борт тягне точки за номерами",
                  size=17, bold=True))

    gx, bx = 150, W - 150
    P.append(text(gx, 70, "НАЗЕМНА СТАНЦІЯ", size=12.5, bold=True))
    P.append(text(bx, 70, "БОРТ", size=12.5, bold=True))
    P.append(line(gx, 80, gx, H - 50, color=MUTED, sw=1.4))
    P.append(line(bx, 80, bx, H - 50, color=MUTED, sw=1.4))

    y = 112
    dy = 48

    def msg(yy, x1, x2, label, col, italic=False):
        out = arrow(x1, yy, x2, yy, color=col)
        anchor = "start" if x1 < x2 else "end"
        tx = (x1 + x2) / 2
        out += text(tx, yy - 9, label, size=11.5, color=col,
                    anchor="middle", bold=True, italic=italic)
        return out

    # послідовність обміну
    P.append(msg(y, gx, bx, "MISSION_COUNT = 10", NEG)); y += dy
    P.append(msg(y, bx, gx, "MISSION_REQUEST #0", FIELD)); y += dy
    P.append(msg(y, gx, bx, "MISSION_ITEM #0", NEG)); y += dy
    P.append(msg(y, bx, gx, "MISSION_REQUEST #1", FIELD)); y += dy
    P.append(msg(y, gx, bx, "MISSION_ITEM #1", NEG)); y += dy
    # «по черзі …»
    P.append(text(W / 2, y, "…  кожну точку — окремо, за її номером  …",
                  size=12, color=MUTED, italic=True)); y += dy
    P.append(msg(y, bx, gx, "MISSION_REQUEST #9", FIELD)); y += dy
    P.append(msg(y, gx, bx, "MISSION_ITEM #9", NEG)); y += dy
    P.append(msg(y, bx, gx, "MISSION_ACK = ACCEPTED ✓", FIELD, italic=False)); y += 6

    # бічні виноски — ЧОМУ це надійно
    fr, w, h = textbox(W / 2, H - 40,
                       "ініціативу тягне борт · номер у кожній точці · "
                       "втрата → повтор кроку · фінальний ACK = маршрут цілий",
                       size=11.5, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/mission-upload.svg", W, H, *P)


# ── Фігура 5 (detailed): кадр MAVLink v2 і що покриває контрольна сума ────────
# Ідея: показати рівно межу, на якій станція ухвалює «мій пакет / чужий /
# биток»: магічний байт → довжина → адреси/ID → корисні дані → CRC. Сама CRC
# рахується від LEN до кінця даних ПЛЮС невидимий CRC_EXTRA (підпис визначення).
def fig_frame_anatomy():
    W, H = 1010, 440
    P = []
    P.append(text(W / 2, 30, "Кадр MAVLink v2: що бачить парсер землі і що покриває CRC",
                  size=16, bold=True))

    # стрічка байтів
    y = 120
    hh = 60
    x0 = 40
    cells = [
        ("0xFD", "магія\n(v2)", 60, POS),
        ("LEN", "довжина\nданих", 66, INK),
        ("INC", "incompat\nflags", 70, MUTED),
        ("CMP", "compat\nflags", 68, MUTED),
        ("SEQ", "лічильник\n0..255", 70, NEG),
        ("SYS", "system\nid", 58, NEG),
        ("COMP", "component\nid", 78, NEG),
        ("MSGID", "тип, 3 Б\n(24 біт)", 80, FIELD),
        ("PAYLOAD", "корисні дані\n(0..255 Б)", 150, INK),
        ("CRC", "16 біт\nMCRF4XX", 78, POS),
    ]
    xs = []
    x = x0
    for lab, sub, w, col in cells:
        xs.append((x, w))
        fill = "#fdecea" if col is POS else ("#eaf0fd" if col is NEG else
               ("#e9f7ef" if col is FIELD else "#eef2f7"))
        P.append(rect(x, y, w, hh, fill=fill, stroke=col, sw=1.6))
        P.append(text(x + w / 2, y + 24, lab, size=12.5, bold=True, color=col))
        P.append(mtext(x + w / 2, y + 40, sub, size=9.5, color=MUTED, lh=1.15))
        x += w + 4

    # дужка «покрито CRC»: від LEN до кінця PAYLOAD
    (xl, wl) = xs[1]           # LEN
    (xp, wp) = xs[8]           # PAYLOAD
    cov_x0, cov_x1 = xl, xp + wp
    cby = y + hh + 26
    P.append(line(cov_x0, cby, cov_x1, cby, color=INK, sw=1.6))
    P.append(line(cov_x0, cby, cov_x0, cby - 8, color=INK, sw=1.6))
    P.append(line(cov_x1, cby, cov_x1, cby - 8, color=INK, sw=1.6))
    P.append(text((cov_x0 + cov_x1) / 2, cby + 18,
                  "CRC рахується від LEN до кінця PAYLOAD", size=12, color=INK, bold=True))

    # невидимий CRC_EXTRA, що домішується в кінці
    (xc, wc) = xs[9]
    extra_cx = W / 2 + 60
    fr, w, h = textbox(extra_cx, y + hh + 120,
                       "…+ CRC_EXTRA:\nневидимий байт-підпис ВИЗНАЧЕННЯ повідомлення.\n"
                       "різні поля/порядок у борту й станції → CRC не зійдеться",
                       size=11, fill="#fdecea", stroke=POS, color=POS, bold=True)
    P.append(line(xc + wc / 2, cby + 8, extra_cx, y + hh + 120 - h / 2,
                  color=POS, sw=1.4, dash="4,4"))
    P.append(fr)

    # магія зліва — точка синхронізації
    P.append(text(xs[0][0] + xs[0][1] / 2, y - 14, "точка старту", size=10,
                  color=POS, bold=True))
    P.append(text(W / 2, H - 16,
                  "v1 починався з 0xFE й ніс 1-байтовий MSGID; v2 — 0xFD, 3-байтовий MSGID + прапорці сумісності",
                  size=11.5, color=MUTED))
    render("img/frame-anatomy.svg", W, H, *P)


# ── Фігура 6 (detailed): скінченний автомат приймача землі ───────────────────
# Ідея: земля не «читає пакет», а веде АВТОМАТ побайтно: шукає магію → лічить
# довжину → набирає заголовок і дані → звіряє CRC (+CRC_EXTRA) → лише тоді
# віддає повідомлення. Биток чи чужий байт — назад у пошук магії, без аварії.
def fig_parser_fsm():
    W, H = 960, 430
    P = []
    P.append(text(W / 2, 30, "Приймач землі — це автомат побайтно, а не «читання пакета»",
                  size=16, bold=True))

    y = 150
    states = [
        ("ПОШУК\nмагії", 95, INK),
        ("ЧИТАЮ\nзаголовок", 260, NEG),
        ("НАБИРАЮ\nдані (LEN)", 435, INK),
        ("ЗВІРЯЮ\nCRC+EXTRA", 620, POS),
        ("ГОТОВО:\nвіддаю\nповідомлення", 830, FIELD),
    ]
    cx_list = []
    for lab, cx, col in states:
        fill = ("#e9f7ef" if col is FIELD else "#eaf0fd" if col is NEG else
                "#fdecea" if col is POS else "#eef2f7")
        fr, w, h = textbox(cx, y, lab, size=12, bold=True, fill=fill, stroke=col,
                           color=col, min_w=118)
        P.append(fr)
        cx_list.append((cx, w))

    # переходи вперед
    labels = ["0xFD", "усі 9 Б", "усі LEN Б", "CRC збіглась"]
    for i in range(4):
        x1 = cx_list[i][0] + cx_list[i][1] / 2
        x2 = cx_list[i + 1][0] - cx_list[i + 1][1] / 2
        P.append(arrow(x1, y, x2, y, color=INK))
        P.append(text((x1 + x2) / 2, y - 12, labels[i], size=10, color=INK, bold=True))

    # відкати назад у «пошук магії» — при битку чи чужому байті
    home = cx_list[0][0]
    for i in (1, 2, 3):
        cx, w = cx_list[i]
        P.append(line(cx, y + 34, cx, y + 78, color=POS, sw=1.4, dash="4,4"))
        P.append(line(cx, y + 78, home, y + 78, color=POS, sw=1.4, dash="4,4"))
    P.append(arrow(home, y + 78, home, y + 34, color=POS))
    P.append(text((home + cx_list[3][0]) / 2, y + 96,
                  "биток / збій CRC / чужий байт → назад у пошук магії (кадр викинуто, аварії немає)",
                  size=11.5, color=POS, bold=True))

    # SEQ-контроль над «готово»
    gx = cx_list[4][0]
    fr, w, h = textbox(gx, y - 78,
                       "заразом: розрив SEQ\n(напр. 41→44) →\nпорахувати втрачені кадри",
                       size=10.5, fill="#eef2f7", stroke=NEG, color=NEG)
    P.append(fr)
    P.append(arrow(gx, y - 78 + h / 2, gx, y - 22, color=NEG))

    render("img/parser-fsm.svg", W, H, *P)


# ── Фігура 7 (detailed): повтор команди, таймаут і поле confirmation ─────────
# Ідея: небезпека не в втраті, а в НЕВИЗНАЧЕНОСТІ «дійшло, а ACK пропав».
# Повтор ТІЄЇ САМОЇ команди з confirmation=1 дає борту розрізнити перший
# постріл від дубля — і не виконати неідемпотентну дію двічі.
def fig_command_retry():
    W, H = 960, 500
    P = []
    P.append(text(W / 2, 30, "Повтор команди: таймаут, confirmation і небезпека дубля",
                  size=16, bold=True))

    gx, bx = 150, W - 150
    P.append(text(gx, 66, "НАЗЕМНА СТАНЦІЯ", size=12.5, bold=True))
    P.append(text(bx, 66, "БОРТ", size=12.5, bold=True))
    P.append(line(gx, 76, gx, H - 40, color=MUTED, sw=1.4))
    P.append(line(bx, 76, bx, H - 40, color=MUTED, sw=1.4))

    def send(y, x1, x2, label, col, lost=False, italic=False):
        if lost:
            xm = (x1 + x2) / 2 + 30
            out = line(x1, y, xm, y + 12, color=col, sw=2)
            out += text(xm + 8, y + 18, "✕ втрата", size=11, color=POS, bold=True, anchor="start")
        else:
            out = arrow(x1, y, x2, y, color=col)
        anchor = "start" if x1 < x2 else "end"
        tx = x1 + (14 if x1 < x2 else -14)
        out += text(tx, y - 8, label, size=11, color=col, anchor=anchor, bold=True, italic=italic)
        return out

    y = 110
    # 1) команда дійшла, але ACK загубився
    P.append(send(y, gx, bx, "COMMAND_LONG (arm), confirmation=0", NEG));
    P.append(text(bx + 10, y + 16, "борт ВИКОНАВ arm", size=10.5, color=FIELD, anchor="start")); y += 40
    P.append(send(y, bx, gx, "COMMAND_ACK: ACCEPTED", FIELD, lost=True)); y += 48

    # таймаут
    P.append(line(gx, y, gx + 46, y, color=POS, sw=1.5, dash="3,4"))
    P.append(line(gx + 46, y, gx + 46, y + 34, color=POS, sw=1.5, dash="3,4"))
    P.append(arrow(gx + 46, y + 34, gx, y + 34, color=POS))
    P.append(text(gx + 52, y + 18, "немає ACK за таймаут", size=10, color=POS, anchor="start"))
    y += 60

    # 2) повтор ТІЄЇ САМОЇ команди з confirmation=1
    P.append(send(y, gx, bx, "COMMAND_LONG (arm), confirmation=1", NEG))
    P.append(text(bx + 10, y + 16, "той самий наказ →\nповторно НЕ шкодить", size=10.5,
                  color=INK, anchor="start")); y += 46
    P.append(send(y, bx, gx, "COMMAND_ACK: ACCEPTED", FIELD)); y += 40

    # висновок-рамка
    fr, w, h = textbox(W / 2, H - 52,
                       "confirmation росте 0→1→2… — борт бачить, що це ДУБЛЬ того самого пострілу.\n"
                       "ідемпотентний наказ (arm) безпечно повторювати; неідемпотентний\n"
                       "борт розрізняє саме за цим полем",
                       size=11, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/command-retry.svg", W, H, *P)


# ── Фігура 8 (proj): чому один таймер на всіх бреше ──────────────────────────
# Ідея: автопілот (1,1) б'ється справно, підвіс (1,154) замовк. Спільний
# «останній HEARTBEAT будь-звідки» оновлюється автопілотом і показує «лінк
# живий» — а підвіс уже мертвий і цього НЕ видно. Пер-джерельний час ловить.
def fig_per_source_timer():
    W, H = 960, 470
    P = []
    P.append(text(W / 2, 30, "Один таймер на всіх бреше: пер-джерельний час ловить мовчуна",
                  size=16, bold=True))

    ax_x0, ax_x1 = 160, W - 210
    step = (ax_x1 - ax_x0) / 8.0
    now_x = ax_x0 + 8 * step

    def pulse(x, y, col, alive=True):
        c = col if alive else MUTED
        return (line(x - 8, y, x - 4, y, color=c, sw=2) +
                line(x - 4, y, x, y - 26, color=c, sw=2) +
                line(x, y - 26, x + 4, y, color=c, sw=2) +
                line(x + 4, y, x + 8, y, color=c, sw=2))

    # два джерела
    lanes = [
        ("(SYS 1, COMP 1)\nавтопілот", 120, FIELD, [0, 1, 2, 3, 4, 5, 6, 7], []),
        ("(SYS 1, COMP 154)\nпідвіс камери", 250, POS, [0, 1, 2], [3, 4, 5, 6, 7]),
    ]
    for name, y, col, beats, gap in lanes:
        fr, w, h = textbox(70, y, name, size=11, bold=True, fill="#eef2f7", stroke=INK, min_w=120)
        P.append(fr)
        P.append(line(ax_x0, y, ax_x1, y, color="#d0d5dd", sw=1.2))
        for i in beats:
            P.append(pulse(ax_x0 + i * step, y, col, True))
        for i in gap:
            x = ax_x0 + i * step
            P.append(text(x, y - 12, "✕", size=12, color=MUTED, bold=True))
        if gap:
            g0 = ax_x0 + gap[0] * step
            P.append(text((g0 + ax_x1) / 2, y + 22, "мовчить кілька секунд",
                          size=10.5, color=POS, italic=True))

    # «зараз»
    P.append(line(now_x, 90, now_x, 300, color=NEG, sw=1.4, dash="4,4"))
    P.append(text(now_x, 82, "зараз", size=11, color=NEG, bold=True))

    # праворуч — два присуди
    fr, w, h = textbox(W - 100, 120, "живий ✓", size=12.5, bold=True,
                       fill="#e9f7ef", stroke=FIELD, color=FIELD, min_w=110)
    P.append(fr)
    fr, w, h = textbox(W - 100, 250, "ВТРАЧЕНО", size=12.5, bold=True,
                       fill="#fdecea", stroke=POS, color=POS, min_w=110)
    P.append(fr)

    # унизу — дві оцінки
    by = 380
    fr, w, h = textbox(W * 0.30, by,
                       "ОДИН таймер:\n«останній удар будь-звідки»\nоновив автопілот →\nбачу «все живе» (ХИБА)",
                       size=11, fill="#fdecea", stroke=POS, color=POS, bold=True)
    P.append(fr)
    fr, w, h = textbox(W * 0.72, by,
                       "ПЕР-ДЖЕРЕЛЬНИЙ час:\nу (1,154) годинник стоїть →\nпідвіс помічено мертвим,\nавтопілот лишається живим",
                       size=11, fill="#e9f7ef", stroke=FIELD, color=FIELD, bold=True)
    P.append(fr)

    render("img/per-source-timer.svg", W, H, *P)


# ── Фігура 9 (proj): машина станів присутності з гістерезисом ────────────────
# Ідея: живий → (тиша > поріг) → втрачено → (новий удар) → відновлено → живий.
# Поріг на втрату (кілька ударів) — не той самий, що на повернення (один удар):
# гістерезис проти «блимання» на межі й проти джитера прибуття.
def fig_presence_fsm():
    W, H = 940, 420
    P = []
    P.append(text(W / 2, 30, "Машина станів присутності: живий → втрачено → відновлено",
                  size=16, bold=True))

    y = 175
    states = [
        ("ЖИВИЙ\nмітка яскрава", 190, FIELD),
        ("ВТРАЧЕНО\nмітка згасла", 490, POS),
        ("ВІДНОВЛЕНО\n(мить)", 790, NEG),
    ]
    cx_list = []
    for lab, cx, col in states:
        fill = ("#e9f7ef" if col is FIELD else "#fdecea" if col is POS else "#eaf0fd")
        fr, w, h = textbox(cx, y, lab, size=12.5, bold=True, fill=fill, stroke=col,
                           color=col, min_w=150)
        P.append(fr)
        cx_list.append((cx, w))

    # живий → втрачено
    x1 = cx_list[0][0] + cx_list[0][1] / 2
    x2 = cx_list[1][0] - cx_list[1][1] / 2
    P.append(arrow(x1, y - 12, x2, y - 12, color=POS))
    P.append(mtext((x1 + x2) / 2, y - 30, ["тиша > порогу", "(N ударів ≈ кілька с)"],
                   size=10.5, color=POS, bold=True))

    # втрачено → відновлено
    x1 = cx_list[1][0] + cx_list[1][1] / 2
    x2 = cx_list[2][0] - cx_list[2][1] / 2
    P.append(arrow(x1, y - 12, x2, y - 12, color=NEG))
    P.append(mtext((x1 + x2) / 2, y - 30, ["новий HEARTBEAT", "(1 удар вистачає)"],
                   size=10.5, color=NEG, bold=True))

    # відновлено → живий (назад згори)
    xr = cx_list[2][0]
    xl = cx_list[0][0]
    P.append(line(xr, y - 34, xr, y - 78, color=FIELD, sw=1.6))
    P.append(line(xr, y - 78, xl, y - 78, color=FIELD, sw=1.6))
    P.append(arrow(xl, y - 78, xl, y - 34, color=FIELD))
    P.append(text((xl + xr) / 2, y - 88, "подія «повернувся» → знову звичайний облік",
                  size=10.5, color=FIELD, bold=True))

    # петля «живий»: кожен удар лише освіжає час
    P.append(line(xl, y + 34, xl - 40, y + 60, color=FIELD, sw=1.4))
    P.append(line(xl - 40, y + 60, xl + 40, y + 60, color=FIELD, sw=1.4))
    P.append(arrow(xl + 40, y + 60, xl, y + 34, color=FIELD))
    P.append(text(xl, y + 78, "кожен удар — освіжаю last_seen", size=10, color=FIELD))

    # петля «втрачено»: далі мовчить — лишаюсь мертвим
    xm = cx_list[1][0]
    P.append(line(xm, y + 34, xm - 40, y + 60, color=POS, sw=1.4, dash="4,4"))
    P.append(line(xm - 40, y + 60, xm + 40, y + 60, color=POS, sw=1.4, dash="4,4"))
    P.append(arrow(xm + 40, y + 60, xm, y + 34, color=POS))
    P.append(text(xm, y + 78, "далі тиша — лишаюсь втраченим", size=10, color=POS))

    # виноска про гістерезис
    fr, w, h = textbox(W / 2, H - 34,
                       "поріг на ВТРАТУ (N ударів) ≠ поріг на ПОВЕРНЕННЯ (1 удар): "
                       "гістерезис проти блимання на межі й джитера прибуття",
                       size=11, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/presence-fsm.svg", W, H, *P)


# ── Фігура (proj): скінченний автомат командного циклу ───────────────────────
# Ідея: цикл — це три стани (IDLE → WAITING → done/fail) з двома годинниками
# всередині WAITING. Показати переходи: постріл, ACK-фінал, ACK-IN_PROGRESS
# (подовжити таймаут, лишитись), таймаут (повтор, confirmation++), вичерпання
# спроб (провал). Це кістяк усього коду вставки.
def fig_command_loop_fsm():
    W, H = 960, 470
    P = []
    P.append(text(W / 2, 30, "Командний цикл як автомат: постріл → чекання → підсумок",
                  size=17, bold=True))

    # три вузли
    idle = (150, 150)
    wait = (480, 150)
    done = (820, 90)
    fail = (820, 250)

    def node(cx, cy, label, sub, fill, stroke):
        fr, w, h = textbox(cx, cy, label + "\n" + sub, size=12, bold=True,
                           fill=fill, stroke=stroke, min_w=150)
        return fr

    P.append(node(*idle, "IDLE", "нема наказу", "#eef2f7", INK))
    P.append(node(*wait, "WAITING_ACK", "attempt, deadline", "#eafaf0", FIELD))
    P.append(node(*done, "DONE", "ACCEPTED / кінець", "#eafaf0", FIELD))
    P.append(node(*fail, "FAILED", "спроби вичерпано\nабо DENIED", "#fdecea", POS))

    # IDLE -> WAITING: постріл
    P.append(arrow(idle[0] + 78, idle[1], wait[0] - 88, wait[1], color=NEG, sw=2))
    P.append(text((idle[0] + wait[0]) / 2, wait[1] - 16,
                  "send(confirmation=0)", size=11, color=NEG))
    P.append(text((idle[0] + wait[0]) / 2, wait[1] + 22,
                  "засікти deadline", size=10, color=MUTED))

    # WAITING -> DONE: фінальний ACK
    P.append(arrow(wait[0] + 90, wait[1] - 14, done[0] - 96, done[1] + 10, color=FIELD, sw=2))
    P.append(text((wait[0] + done[0]) / 2 + 10, wait[1] - 40,
                  "ACK ACCEPTED", size=11, color=FIELD))

    # WAITING -> FAILED: DENIED/UNSUPPORTED/FAILED або спроби скінчились
    P.append(arrow(wait[0] + 90, wait[1] + 14, fail[0] - 96, fail[1] - 14, color=POS, sw=2))
    P.append(text((wait[0] + fail[0]) / 2 + 6, fail[1] + 4,
                  "ACK DENIED / вичерпано", size=11, color=POS))

    # петля таймауту: WAITING -> WAITING (повтор)
    lx, ly = wait[0], wait[1] + 64
    P.append(line(wait[0] - 40, wait[1] + 26, lx - 40, ly, color=INK, sw=1.6))
    P.append(line(lx - 40, ly, lx + 40, ly, color=INK, sw=1.6))
    P.append(arrow(lx + 40, ly, wait[0] + 40, wait[1] + 26, color=INK, sw=1.6))
    P.append(text(lx, ly + 18, "таймаут: send(confirmation++), attempt++",
                  size=10, color=INK))

    # петля IN_PROGRESS: WAITING -> WAITING (подовжити deadline)
    ux, uy = wait[0], wait[1] - 66
    P.append(line(wait[0] - 44, wait[1] - 26, ux - 44, uy, color=FIELD, sw=1.6, dash="5,4"))
    P.append(line(ux - 44, uy, ux + 44, uy, color=FIELD, sw=1.6, dash="5,4"))
    P.append(arrow(ux + 44, uy, wait[0] + 44, wait[1] - 26, color=FIELD, sw=1.6))
    P.append(text(ux, uy - 8, "ACK IN_PROGRESS: deadline += довго",
                  size=10, color=FIELD))

    # виноска: два годинники живуть у WAITING
    fr, w, h = textbox(W / 2, H - 32,
                       "у стані WAITING два лічильники: deadline (коли повторити) "
                       "і attempt (скільки ще можна); IN_PROGRESS лише зсуває deadline, "
                       "не витрачаючи спробу",
                       size=11, fill="#eef2f7", stroke=INK)
    P.append(fr)

    render("img/command-loop-fsm.svg", W, H, *P)


# ── Фігура (proj): фільтр відповідності ACK — свій проти чужого ───────────────
# Ідея: у каналі ACK-и від багатьох компонентів; наш цикл мусить прийняти лише
# той, де (SYS,COMP джерела) == той, кого ми наказували, І command == наш.
# Інакше — переплутаємо чужу відповідь зі своєю. Це головна пастка вставки.
def fig_ack_match_filter():
    W, H = 940, 430
    P = []
    P.append(text(W / 2, 30, "Приймаємо лише СВІЙ ACK: фільтр за джерелом і командою",
                  size=17, bold=True))

    # ліворуч — потік вхідних ACK від різних відправників
    x0 = 60
    rows = [
        ("ACK  src=(1,1)  cmd=400", True,  "той борт, та команда — це наш"),
        ("ACK  src=(1,1)  cmd=176", False, "той борт, ЧУЖА команда (режим)"),
        ("ACK  src=(1,158) cmd=400", False, "камера (COMP 158), не автопілот"),
        ("ACK  src=(2,1)  cmd=400", False, "інший борт у мережі (SYS 2)"),
    ]
    y = 90
    dy = 66
    for label, ok, why in rows:
        col = FIELD if ok else MUTED
        fr, w, h = textbox(x0 + 150, y, label, size=12, fill="#f4f6f8",
                           stroke=col, sw=2 if ok else 1.4, min_w=250)
        P.append(fr)
        P.append(text(x0 + 150, y + 26, why, size=10, color=col))
        # стрілка до фільтра
        P.append(arrow(x0 + 280, y, 545, y, color=col, sw=1.6,
                       ) if ok else line(x0 + 280, y, 545, y, color=col, sw=1.2, dash="4,4"))
        y += dy

    # рамка-фільтр посередині
    fx, fy, fw, fh = 545, 78, 170, dy * 4 - 20
    P.append(rect(fx, fy, fw, fh, fill="#eef2f7", stroke=INK, sw=1.8))
    P.append(mtext(fx + fw / 2, fy + fh / 2 - 22,
                   ["ФІЛЬТР", "src.sys == target.sys", "src.comp == target.comp",
                    "ack.command == sent"],
                   size=11, bold=False, color=INK))

    # праворуч — тільки свій проходить
    P.append(arrow(fx + fw, fy + fh / 2, 830, fy + fh / 2, color=FIELD, sw=2.2))
    fr, w, h = textbox(870, fy + fh / 2, "обробити\nрезультат", size=12, bold=True,
                       fill="#eafaf0", stroke=FIELD, min_w=110)
    P.append(fr)

    # виноска
    fr, w, h = textbox(W / 2, H - 26,
                       "пастка: узяти ПЕРШИЙ-ліпший COMMAND_ACK — легко сплутати відповідь "
                       "камери чи сусіднього апарата зі своєю; звіряй джерело І номер команди",
                       size=11, fill="#fdecea", stroke=POS)
    P.append(fr)

    render("img/ack-match-filter.svg", W, H, *P)


# ── Фігура (hist): народження MAVLink — часова вісь від задачі до стандарту ────
# Ідея: побічний продукт (протокол) пережив свою мету (виграти EMAV 2009) і
# переріс її, ставши галузевим стандартом. Показуємо це віхами на одній осі:
# ліворуч — вузька задача, посередині — досягнута й вичерпана мета, праворуч —
# зростання в стандарт. Зелене — те, що зробило переростання можливим.
def fig_mavlink_birth_timeline():
    W, H = 960, 470
    P = []
    P.append(text(W / 2, 30, "Побічний продукт переріс свою мету: шлях MAVLink",
                  size=17, bold=True))

    # горизонтальна вісь часу
    ax_y = 250
    ax_x0, ax_x1 = 60, W - 60
    P.append(line(ax_x0, ax_y, ax_x1, ax_y, color=MUTED, sw=2))
    P.append(text(ax_x1, ax_y + 30, "час →", size=12, color=MUTED, anchor="end"))

    # віхи: (x, рік, підпис угорі/внизу, «вгору»?, колір, деталь)
    milestones = [
        (140, "2008", "ETH Zürich:\nхочу автономний\nполіт по зору", True,  MUTED,
         "задача, не протокол"),
        (300, "поч.\n2009", "MAVLink v1\nвипущено\n(LGPL)", False, FIELD,
         "вільний + компактний"),
        (470, "верес.\n2009", "EMAV 2009, Делфт:\nPIXHAWK виграв\nindoor-автономію", True, POS,
         "МЕТУ досягнуто\nй вичерпано"),
        (660, "2011–14", "ArduPilot і PX4\nодним протоколом;\nDronecode (2014)", False, FIELD,
         "де-факто стандарт"),
        (850, "2017", "MAVLink 2:\nпідпис, розширення,\n280 Б", True,  INK,
         "зрілий стандарт"),
    ]

    for x, yr, label, up, col, detail in milestones:
        # вузол на осі
        P.append(circle(x, ax_y, 8, fill=col, stroke=INK, sw=1.6))
        # рік просто біля осі
        P.append(mtext(x, ax_y - 16 if not up else ax_y + 22, yr, size=12,
                       bold=True, color=INK))
        det_lines = detail.split("\n")
        if up:
            # виносний підпис вгору
            P.append(line(x, ax_y - 8, x, ax_y - 60, color=col, sw=1.4, dash="3,3"))
            fr, w, h = textbox(x, ax_y - 100, label, size=11, fill="#f4f6f8",
                               stroke=col, sw=1.8, min_w=150)
            P.append(fr)
            for i, dl in enumerate(det_lines):
                P.append(text(x, ax_y - 100 + h / 2 + 16 + i * 12, dl, size=9.5,
                              color=col, italic=True))
        else:
            P.append(line(x, ax_y + 8, x, ax_y + 60, color=col, sw=1.4, dash="3,3"))
            fr, w, h = textbox(x, ax_y + 100, label, size=11, fill="#eafaf0",
                               stroke=col, sw=1.8, min_w=150)
            P.append(fr)
            for i, dl in enumerate(det_lines):
                P.append(text(x, ax_y + 100 + h / 2 + 16 + i * 12, dl, size=9.5,
                              color=col, italic=True))

    # дуга «переростання»: від мети (EMAV) далі вправо
    P.append(text(660, ax_y - 150, "мету вичерпано — а протокол житиме далі →",
                  size=12, color=POS, italic=True))

    # нижня виноска — головна думка
    fr, w, h = textbox(W / 2, H - 30,
                       "стандарт рідко проєктують як стандарт: він виростає з простого, "
                       "вільного інструмента, що розв'язав спільний біль",
                       size=11.5, fill="#eef2f7", stroke=INK, min_w=560)
    P.append(fr)

    render("img/mavlink-birth-timeline.svg", W, H, *P)


if __name__ == "__main__":
    fig_heartbeat_discovery()
    fig_telemetry_stream()
    fig_command_ack()
    fig_mission_upload()
    fig_frame_anatomy()
    fig_parser_fsm()
    fig_command_retry()
    fig_per_source_timer()
    fig_presence_fsm()
    fig_command_loop_fsm()
    fig_ack_match_filter()
    fig_mavlink_birth_timeline()
    print("OK: 12 figures -> img/")
