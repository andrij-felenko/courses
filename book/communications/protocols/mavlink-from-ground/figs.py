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


if __name__ == "__main__":
    fig_heartbeat_discovery()
    fig_telemetry_stream()
    fig_command_ack()
    fig_mission_upload()
    print("OK: 4 figures -> img/")
