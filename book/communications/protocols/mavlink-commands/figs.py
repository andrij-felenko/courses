# -*- coding: utf-8 -*-
"""figs.py — фігури до статті «Команди MAVLink».
svgkit імпортуємо зі scripts/ (НЕ копіюємо), вивід у ./img/."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs("img", exist_ok=True)


# ── Фігура 1: кадр повідомлення MAVLink ──────────────────────────────────────
# Головна структурна ідея: повідомлення — це заголовок + payload + CRC, де ID
# вирішує, ЯК читати payload. Показуємо стрічку байтів зліва направо й окремо
# виносимо, що означає поле ID (ключ до розбору) і що означає CRC (перевірка).
def fig_frame():
    W, H = 940, 430
    parts = []

    # стрічка байтів: групи заголовок / ID / payload / CRC
    y = 110
    h = 64
    x = 60
    cells = [
        ("STX", "старт", "#eef2f7", INK, 70),
        ("LEN", "довжина", "#eef2f7", INK, 80),
        ("SEQ", "лічильник", "#eef2f7", INK, 90),
        ("SYS·COMP", "адреса", "#eef2f7", INK, 120),
        ("MSG ID", "тип", "#e9f7ef", FIELD, 100),
        ("PAYLOAD", "самі дані", "#fff6e5", "#b7791f", 200),
        ("CRC", "перевірка", "#eaf0fd", NEG, 90),
    ]
    xs = []
    for name, sub, fill, col, w in cells:
        parts.append(rect(x, y, w, h, fill=fill, stroke=col, sw=2, rx=6))
        parts.append(text(x + w / 2, y + 28, name, size=13, bold=True, color=col))
        parts.append(text(x + w / 2, y + 48, sub, size=11, color=MUTED))
        xs.append((x, w))
        x += w + 4

    # дужки під групами
    def brace(x0, x1, label, col, yy):
        parts.append(line(x0, yy, x1, yy, color=col, sw=1.6))
        parts.append(line(x0, yy - 5, x0, yy, color=col, sw=1.6))
        parts.append(line(x1, yy - 5, x1, yy, color=col, sw=1.6))
        parts.append(text((x0 + x1) / 2, yy + 18, label, size=12, color=col, bold=True))

    hy = y + h + 16
    hx0 = xs[0][0]
    hx1 = xs[3][0] + xs[3][1]
    brace(hx0, hx1, "заголовок (службові поля)", INK, hy)
    px0 = xs[5][0]
    px1 = xs[5][0] + xs[5][1]
    brace(px0, px1, "корисні дані", "#b7791f", hy)

    # виноска 1: ID — ключ до розбору payload
    box1 = fitbox(70, 280, 360, 110,
                  "MSG ID каже, ЩО це за повідомлення\n(heartbeat? висота? положення?)\n→ за ним приймач знає, ЯК\nрозкласти байти payload на поля",
                  size=13, fill="#e9f7ef", stroke=FIELD, sw=2)
    parts.append(box1)
    parts.append(arrow(xs[4][0] + xs[4][1] / 2, y + h, 250, 280, color=FIELD, sw=1.8))

    # виноска 2: CRC — цілісність + сумісність
    box2 = fitbox(W - 430, 280, 360, 110,
                  "CRC = остача від ділення всього\nпакета на поліном (контрольна сума).\nНе зійшлася → пакет викидають:\nабо шум у каналі, або різні версії",
                  size=13, fill="#eaf0fd", stroke=NEG, sw=2)
    parts.append(box2)
    parts.append(arrow(xs[6][0] + xs[6][1] / 2, y + h, W - 250, 280, color=NEG, sw=1.8))

    render("img/frame.svg", W, H, *parts,
           title="Кадр повідомлення MAVLink: заголовок · ID · дані · CRC")


# ── Фігура 2: команда й підтвердження (COMMAND_LONG / COMMAND_ACK) ───────────
# Серце статті про КОМАНДИ: одноразова дія потребує гарантії, що її прийняли.
# Показуємо діалог: станція шле COMMAND_LONG, дрон відповідає COMMAND_ACK із
# результатом; якщо ACK не прийшов — повторна відправка з тим самим лічильником.
def fig_command_ack():
    W, H = 900, 470
    parts = []

    lx, rx = 180, W - 180          # дві «доріжки» учасників
    top = 70

    # учасники
    parts.append(rect(lx - 110, top - 36, 220, 30, fill="#eef2f7", stroke=INK, sw=2, rx=6))
    parts.append(text(lx, top - 15, "наземна станція", size=13, bold=True))
    parts.append(rect(rx - 80, top - 36, 160, 30, fill="#eef2f7", stroke=INK, sw=2, rx=6))
    parts.append(text(rx, top - 15, "дрон", size=13, bold=True))

    # вертикальні лінії життя
    parts.append(line(lx, top, lx, H - 40, color=MUTED, sw=1.2, dash="3,5"))
    parts.append(line(rx, top, rx, H - 40, color=MUTED, sw=1.2, dash="3,5"))

    # 1) команда йде, але губиться
    y1 = top + 50
    parts.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="2.2" '
                 'stroke-dasharray="2,4"/>' % (lx, y1, (lx + rx) / 2 + 40, y1 + 28, POS))
    parts.append(text(lx + 14, y1 - 8, "COMMAND_LONG  (взліт, confirmation=0)",
                      size=12, color=POS, anchor="start", bold=True))
    parts.append(text((lx + rx) / 2 + 70, y1 + 42, "✗ загубилось у каналі",
                      size=11.5, color=MUTED, anchor="start"))

    # 2) тайм-аут → повтор
    y2 = y1 + 90
    parts.append(text(lx - 14, y2 - 8, "тайм-аут → повтор", size=11.5, color=MUTED, anchor="end"))
    parts.append(arrow(lx, y2, rx, y2 + 18, color=POS, sw=2.2))
    parts.append(text(lx + 14, y2 + 30, "COMMAND_LONG  (та сама, confirmation=1)",
                      size=12, color=POS, anchor="start", bold=True))

    # дрон виконує
    parts.append(rect(rx - 6, y2 + 18, 12, 44, fill="#fff6e5", stroke="#b7791f", sw=2, rx=3))
    parts.append(text(rx + 16, y2 + 44, "перевіряє\nй виконує", size=11, color="#b7791f", anchor="start"))

    # 3) відповідь ACK
    y3 = y2 + 92
    parts.append(arrow(rx, y3, lx, y3 + 18, color=FIELD, sw=2.2))
    parts.append(text(rx - 14, y3 - 8, "COMMAND_ACK  (result = ACCEPTED)",
                      size=12, color=FIELD, anchor="end", bold=True))
    parts.append(text(lx + 14, y3 + 34, "✓ станція певна: команду прийнято",
                      size=11.5, color=FIELD, anchor="start"))

    # підсумок
    box, bw, bh = textbox(W / 2, H - 26,
                          "разова дія = «надіслав → чекай ACK → не прийшов → повтори». Це надійність поверх ненадійного каналу",
                          size=12.5, pad=11, fill=FILL, bold=True)
    parts.append(box)

    render("img/command-ack.svg", W, H, *parts,
           title="Команда й підтвердження: COMMAND_LONG → COMMAND_ACK")


# ── Фігура 3: потоки телеметрії проти команд ─────────────────────────────────
# Друга половина протоколу: телеметрія — це НЕ запити, а підписка на потік, що
# сам тече із заданою частотою. Контраст із командою (рідкісна, з ACK).
# Зліва — команда (одинична подія + ACK), справа — потік (рівномірні пакети).
def fig_telemetry_streams():
    W, H = 920, 440
    parts = []

    midx = W / 2
    parts.append(line(midx, 60, midx, H - 60, color=MUTED, sw=1.2, dash="4,6"))

    # ── ліворуч: команда (рідко, важливо, з підтвердженням) ──
    parts.append(text(midx / 2, 56, "КОМАНДА — рідкісна разова дія", size=14, bold=True, color=POS))
    cy = 150
    parts.append(rect(60, cy - 22, 260, 44, fill="#fdecea", stroke=POS, sw=2, rx=8))
    parts.append(text(190, cy + 5, "«злети», «йди в точку»", size=13, color=POS, bold=True))
    parts.append(arrow(190, cy + 22, 190, cy + 64, color=POS, sw=2))
    parts.append(rect(95, cy + 64, 190, 36, fill="#e9f7ef", stroke=FIELD, sw=2, rx=8))
    parts.append(text(190, cy + 87, "ACK: прийнято?", size=12, color=FIELD, bold=True))
    parts.append(text(190, cy + 132, "по потребі · з гарантією\n(надіслав і пересвідчився)",
                      size=12, color=MUTED))

    # ── праворуч: потік телеметрії (часто, сам тече) ──
    parts.append(text(midx + midx / 2, 56, "ТЕЛЕМЕТРІЯ — безперервний потік", size=14, bold=True, color=NEG))
    bx0 = midx + 60
    ty = 150
    # серія однакових пакетів, що течуть рівномірно
    for i in range(6):
        x = bx0 + i * 52
        parts.append(rect(x, ty - 16, 38, 32, fill="#eaf0fd", stroke=NEG, sw=1.8, rx=5))
    parts.append(arrow(bx0 - 8, ty, bx0 + 6 * 52 + 6, ty, color=NEG, sw=1.6))
    parts.append(text((bx0 + bx0 + 6 * 52) / 2, ty - 34,
                      "ATTITUDE · GPS · BATTERY … щосекунди й частіше",
                      size=12, color=NEG))
    parts.append(text((bx0 + bx0 + 6 * 52) / 2, ty + 40, "час →", size=11, color=MUTED))

    # як задають частоту
    box = fitbox(midx + 60, ty + 70, midx - 120, 96,
                 "Частоту замовляють раз командою\nSET_MESSAGE_INTERVAL:\nparam1 = ID повідомлення,\nparam2 = період у мкс (1 000 000 = 1 Гц)",
                 size=12.5, fill="#f0f4fb", stroke=NEG, sw=1.8)
    parts.append(box)

    # підсумок знизу
    box2, bw, bh = textbox(W / 2, H - 26,
                           "дві природи трафіку: команди — рідко й надійно (з ACK); телеметрія — часто й потоком (підписка на частоту)",
                           size=12.5, pad=11, fill=FILL, bold=True)
    parts.append(box2)

    render("img/telemetry-streams.svg", W, H, *parts,
           title="Дві природи обміну: команди проти потоків телеметрії")


if __name__ == "__main__":
    fig_frame()
    fig_command_ack()
    fig_telemetry_streams()
    print("OK: frame, command-ack, telemetry-streams")
