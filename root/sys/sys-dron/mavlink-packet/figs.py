# -*- coding: utf-8 -*-
"""Фігури до теми «Пакет MAVLink».
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Локальні відтінки понад палітру svgkit
HDR  = "#2457d6"   # поля заголовка (холодне)
PAY  = "#27ae60"   # корисні дані (зелене)
CRCC = "#b9770e"   # контрольна сума (тепле)
STXC = "#c0392b"   # стартовий байт (гаряче)


# ── 1. Кадр MAVLink v1: байт за байтом ──────────────────────────────────────
def fig_frame():
    W, H = 820, 300
    f = [text(W / 2, 28, "Кадр MAVLink v1: вісім службових байтів навколо даних", size=15, bold=True)]

    # стрічка байтів: STX | LEN SEQ SYS COMP MSGID | PAYLOAD | CRC
    y = 90
    bh = 56
    # ширини пропорційні (службові — по одному байту, payload — широкий)
    cells = [
        ("STX",     1, STXC, "0xFE"),
        ("LEN",     1, HDR,  "1 Б"),
        ("SEQ",     1, HDR,  "1 Б"),
        ("SYS",     1, HDR,  "1 Б"),
        ("COMP",    1, HDR,  "1 Б"),
        ("MSG ID",  1, HDR,  "1 Б"),
        ("PAYLOAD", 5, PAY,  "0–255 Б"),
        ("CRC",     2, CRCC, "2 Б"),
    ]
    total = sum(c[1] for c in cells)
    x = 30
    span = W - 60
    for name, wt, col, sub in cells:
        w = span * wt / total
        f.append(rect(x, y, w, bh, fill=BG, stroke=col, sw=2.2))
        f.append(text(x + w / 2, y + 24, name, size=12.5, color=col, bold=True))
        f.append(text(x + w / 2, y + 42, sub, size=10, color=MUTED, italic=True))
        x += w

    # фігурні дужки під трьома частинами
    yb = y + bh + 16
    # заголовок (STX..MSGID = 6 байтів)
    hx0, hx1 = 30, 30 + span * 6 / total
    f.append(line(hx0, yb, hx1, yb, color=INK, sw=1.4))
    f.append(text((hx0 + hx1) / 2, yb + 18, "стартовий байт + заголовок 5 Б", size=10.5, color=INK))
    # payload
    px0, px1 = hx1, hx1 + span * 5 / total
    f.append(line(px0, yb, px1, yb, color=PAY, sw=1.4))
    f.append(text((px0 + px1) / 2, yb + 18, "корисні дані", size=10.5, color=PAY))
    # crc
    cx0, cx1 = px1, 30 + span
    f.append(line(cx0, yb, cx1, yb, color=CRCC, sw=1.4))
    f.append(text((cx0 + cx1) / 2, yb + 18, "перевірка", size=10.5, color=CRCC))

    # підсумок overhead
    f.append(text(W / 2, yb + 54,
                  "Службового — 8 байтів (1 + 5 + 2); решта кадру — самі дані.",
                  size=11.5, color=MUTED, italic=True))

    render(os.path.join(IMG, "frame.svg"), W, H, *f)


# ── 2. Що робить кожне поле (роль, не розмір) ────────────────────────────────
def fig_fields():
    W, H = 760, 360
    f = [text(W / 2, 28, "Роль кожного поля заголовка", size=15, bold=True)]

    rows = [
        ("STX",    "маркер «тут починається пакет» — за ним парсер ловить початок", STXC),
        ("LEN",    "скільки байтів даних читати далі", HDR),
        ("SEQ",    "лічильник; за розривом у нумерації видно загублений пакет", HDR),
        ("SYS",    "від якого апарата (дрон №1, №2 …)", HDR),
        ("COMP",   "від якого вузла всередині апарата", HDR),
        ("MSG ID", "тип повідомлення — за ним відомо, як читати дані", HDR),
        ("PAYLOAD","самі дані обраного типу", PAY),
        ("CRC",    "контрольна сума: чи не спотворилося в ефірі", CRCC),
    ]
    y = 58
    rh = 36
    lblw = 100
    for name, desc, col in rows:
        f.append(rect(30, y, lblw, rh - 8, fill=BG, stroke=col, sw=2))
        f.append(text(30 + lblw / 2, y + (rh - 8) / 2 + 5, name, size=12, color=col, bold=True))
        f.append(text(30 + lblw + 16, y + (rh - 8) / 2 + 5, desc, size=11.5, color=INK, anchor="start"))
        y += rh

    render(os.path.join(IMG, "fields.svg"), W, H, *f)


# ── 3. HEARTBEAT: пульс на лінії ─────────────────────────────────────────────
def fig_heartbeat():
    W, H = 760, 330
    f = [text(W / 2, 28, "HEARTBEAT (ID 0): пульс, що йде ~1 раз на секунду", size=15, bold=True)]

    # кардіограма
    y0 = 92
    pts = []
    x = 40
    import math
    while x < W - 40:
        # рівна лінія з періодичними піками
        ph = (x - 40) % 150
        if 60 <= ph <= 90:
            t = (ph - 60) / 30.0
            dy = -46 * math.sin(math.pi * t)
        else:
            dy = 0
        pts.append("%.1f,%.1f" % (x, y0 + dy))
        x += 3
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>'
             % (" ".join(pts), STXC))
    f.append(text(W / 2, y0 + 40, "поки б'ється — апарат живий; зникло — лінк мертвий → failsafe",
                  size=11, color=MUTED, italic=True))

    # що несе payload
    y = 168
    f.append(text(40, y, "У даних HEARTBEAT:", size=12.5, bold=True, anchor="start"))
    items = [
        ("type", "тип апарата — квадрокоптер, літак, ровер …"),
        ("autopilot", "який автопілот — PX4, ArduPilot …"),
        ("base_mode / custom_mode", "режим польоту, чи апарат armed"),
        ("system_status", "загальний стан системи"),
        ("mavlink_version", "версія протоколу"),
    ]
    yy = y + 26
    for k, v in items:
        f.append(text(56, yy, "•", size=12, color=PAY, anchor="start", bold=True))
        f.append(text(72, yy, k, size=11.5, color=HDR, anchor="start", bold=True))
        f.append(text(72 + text_width(k, 11.5, True) + 12, yy, "— " + v,
                      size=11.5, color=INK, anchor="start"))
        yy += 26

    render(os.path.join(IMG, "heartbeat.svg"), W, H, *f)


# ── 4. XML → згенерований кодек на обох кінцях ───────────────────────────────
def fig_xml():
    W, H = 800, 320
    f = [text(W / 2, 28, "Один XML — два згенеровані кодеки, що завжди збігаються", size=15, bold=True)]

    # центральний XML-блок
    cx, cy = W / 2, 130
    box, bw, bh = textbox(cx, cy, "common.xml\nATTITUDE = ID 30\nroll, pitch, yaw : float",
                          size=12, pad=14, stroke=INK, fill=FILL, bold=False)
    f.append(box)
    f.append(text(cx, cy - bh / 2 - 10, "опис повідомлень (схема)", size=11, color=MUTED, italic=True))

    # стрілки вниз до двох кодеків
    ly, ry = cy + bh / 2, 232
    lx, rx = W * 0.27, W * 0.73
    f.append(arrow(cx - 30, ly, lx, ry - 22, color=HDR, sw=1.8))
    f.append(arrow(cx + 30, ly, rx, ry - 22, color=HDR, sw=1.8))
    f.append(text(W / 2, (ly + ry) / 2, "автогенерація", size=10.5, color=HDR, italic=True))

    lb, lw, lh = textbox(lx, ry, "C-кодек\n(прошивка)", size=12, pad=12, stroke=PAY)
    rb, rw, rh = textbox(rx, ry, "pymavlink\n(скрипти)", size=12, pad=12, stroke=PAY)
    f.append(lb)
    f.append(rb)

    f.append(text(W / 2, H - 24,
                  "Пакують і розпаковують поля однаково, бо зроблені з тих самих визначень.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "xml-codegen.svg"), W, H, *f)


# ── 5. CRC_EXTRA: одна перевірка ловить дві біди ─────────────────────────────
def fig_crc():
    W, H = 800, 360
    f = [text(W / 2, 28, "CRC_EXTRA: одна сума стереже і цілість, і сумісність", size=15, bold=True)]

    # що входить у CRC
    y = 70
    f.append(text(W / 2, y, "CRC рахується по:", size=12.5, bold=True))
    chips = [("заголовок", HDR), ("дані", PAY), ("CRC_EXTRA", CRCC)]
    cw = 150
    gap = 24
    tot = len(chips) * cw + (len(chips) - 1) * gap
    x = (W - tot) / 2
    yy = y + 18
    for name, col in chips:
        f.append(rect(x, yy, cw, 38, fill=BG, stroke=col, sw=2))
        f.append(text(x + cw / 2, yy + 24, name, size=12, color=col, bold=True))
        x += cw + gap
    f.append(text(W / 2, yy + 60,
                  "CRC_EXTRA — байт-«відбиток» зі структури полів повідомлення (імена + типи).",
                  size=11, color=MUTED, italic=True))

    # дві сторони з різними XML → суми не збігаються
    y2 = 210
    lx, rx = W * 0.26, W * 0.74
    lb, lw, lh = textbox(lx, y2, "Передавач\nMSG 30: roll,pitch,yaw\nCRC_EXTRA = 39",
                         size=11.5, pad=12, stroke=INK)
    rb, rw, rh = textbox(rx, y2, "Приймач\nMSG 30: roll,pitch,yaw,extra\nCRC_EXTRA = 71",
                         size=11.5, pad=12, stroke=INK)
    f.append(lb)
    f.append(rb)
    # блискавка-незбіг між ними
    midx = W / 2
    f.append(line(lx + lw / 2, y2, midx - 18, y2, color=MUTED, sw=1.4, dash="4 3"))
    f.append(line(rx - rw / 2, y2, midx + 18, y2, color=MUTED, sw=1.4, dash="4 3"))
    f.append(text(midx, y2 - 6, "≠", size=22, color=STXC, bold=True))

    f.append(text(W / 2, y2 + lh / 2 + 34,
                  "Різні визначення → різні CRC_EXTRA → CRC не зійдеться → пакет відкинуто.",
                  size=11.5, color=STXC, bold=True))

    render(os.path.join(IMG, "crc-extra.svg"), W, H, *f)


# ── 6. Адресація SYS / COMP ──────────────────────────────────────────────────
def fig_addressing():
    W, H = 800, 340
    f = [text(W / 2, 28, "SYS / COMP: багато апаратів і вузлів на одній лінії", size=15, bold=True)]

    # одна лінія-шина
    by = 96
    f.append(line(40, by, W - 40, by, color=MUTED, sw=2.4))
    f.append(text(W - 40, by - 10, "одна радіолінія", size=10.5, color=MUTED, anchor="end", italic=True))

    # два апарати, у кожного по кілька вузлів
    drones = [
        ("SYS 1", W * 0.30, [("COMP 1", "автопілот"), ("COMP 100", "камера"), ("COMP 154", "підвіс")]),
        ("SYS 2", W * 0.70, [("COMP 1", "автопілот"), ("COMP 191", "борт-комп.")]),
    ]
    for sysname, dx, comps in drones:
        # стовбур до апарата
        f.append(line(dx, by, dx, by + 24, color=HDR, sw=1.8))
        sb, sw_, sh = textbox(dx, by + 44, sysname, size=12.5, pad=10, stroke=HDR, bold=True)
        f.append(sb)
        # вузли під апаратом
        n = len(comps)
        cw = 150
        gap = 12
        tot = n * cw + (n - 1) * gap
        x = dx - tot / 2
        cy = by + 120
        for cname, role in comps:
            f.append(line(dx, by + 44 + sh / 2, x + cw / 2, cy - 19, color=MUTED, sw=1.2))
            f.append(rect(x, cy - 19, cw, 38, fill=BG, stroke=PAY, sw=1.8))
            f.append(text(x + cw / 2, cy - 2, cname, size=11, color=PAY, bold=True))
            f.append(text(x + cw / 2, cy + 13, role, size=9.5, color=MUTED, italic=True))
            x += cw + gap

    f.append(text(W / 2, H - 22,
                  "Кожне повідомлення несе SYS+COMP — і завжди відомо, від кого воно.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "addressing.svg"), W, H, *f)


# ── 7. v1 vs v2 ──────────────────────────────────────────────────────────────
def fig_v1v2():
    W, H = 800, 330
    f = [text(W / 2, 28, "v1 і v2: той самий кадр, ширші можливості", size=15, bold=True)]

    cols = [
        ("v1", "0xFE", STXC, [
            "ID типу — 1 байт (до 256 типів)",
            "заголовок 5 байтів",
            "службового — 8 байтів",
            "без підпису",
        ]),
        ("v2", "0xFD", PAY, [
            "ID типу — 24 біти (мільйони)",
            "прапорці сумісності",
            "підпис (signing) — 13 байтів, за потреби",
            "нульові хвости даних обрізає",
        ]),
    ]
    bw = 330
    gap = 60
    x0 = (W - (2 * bw + gap)) / 2
    for i, (name, stx, col, feats) in enumerate(cols):
        x = x0 + i * (bw + gap)
        y = 64
        f.append(rect(x, y, bw, 200, fill=FILL, stroke=col, sw=2.2))
        f.append(text(x + bw / 2, y + 28, name, size=16, color=col, bold=True))
        f.append(text(x + bw / 2, y + 50, "старт " + stx, size=11.5, color=MUTED, italic=True))
        yy = y + 80
        for ft in feats:
            f.append(text(x + 18, yy, "•", size=12, color=col, anchor="start", bold=True))
            f.append(text(x + 34, yy, ft, size=11, color=INK, anchor="start"))
            yy += 28

    f.append(text(W / 2, H - 22,
                  "Суть незмінна: старт → заголовок → дані → CRC. Зрозумів v1 — розумієш v2.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(IMG, "v1-v2.svg"), W, H, *f)


if __name__ == "__main__":
    fig_frame()
    fig_fields()
    fig_heartbeat()
    fig_xml()
    fig_crc()
    fig_addressing()
    fig_v1v2()
    print("OK: 7 figs ->", IMG)
