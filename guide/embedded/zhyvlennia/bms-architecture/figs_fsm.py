# -*- coding: utf-8 -*-
"""Фігури до вставки «proj-bms-state-machine» (скінченний автомат прошивки BMS).
Окремий генератор у теці теми (поряд із figs.py), щоб не конфліктувати з ним.
Запуск:  python figs_fsm.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

C_OK  = FIELD
C_BAD = POS
C_LOW = NEG
GOLD  = "#caa24a"


# ── 1. Скінченний автомат прошивки BMS ──────────────────────────────────────
def fig_fsm():
    """Стани прошивки: OFF → PRECHARGE → ON, і спільна «червона шина» в FAULT
    від будь-якої аварії. FAULT — пастка, вихід лише через скидання."""
    W, H = 820, 480
    f = [text(W / 2, 30, "Автомат BMS: OFF → PRECHARGE → ON, будь-яка біда → FAULT", size=15, bold=True)]
    states = [("OFF", "контактори\nрозімкнені", C_OK, 140),
              ("PRECHARGE", "резистор\nзаряджає C", GOLD, 410),
              ("ON", "головний\nзамкнений", FIELD, 680)]
    sy = 135
    rw, rh = 150, 78
    cxs = []
    for name, sub, col, cx in states:
        cxs.append(cx)
        f.append(rect(cx - rw / 2, sy - rh / 2, rw, rh, fill="#fff", stroke=col, sw=2.2))
        f.append(text(cx, sy - 10, name, size=15, color=col, bold=True))
        f.append(mtext(cx, sy + 14, sub, size=10, color=MUTED))
    # переходи вперед
    f.append(arrow(cxs[0] + rw / 2, sy, cxs[1] - rw / 2, sy, color=INK, sw=2))
    f.append(text((cxs[0] + cxs[1]) / 2, sy - 16, "команда «увімкнути»", size=9.5, color=INK, bold=True))
    f.append(text((cxs[0] + cxs[1]) / 2, sy + 28, "замкни «−», передзаряд", size=9, color=MUTED))
    f.append(arrow(cxs[1] + rw / 2, sy, cxs[2] - rw / 2, sy, color=INK, sw=2))
    f.append(text((cxs[1] + cxs[2]) / 2, sy - 16, "ΔU < поріг", size=9.5, color=INK, bold=True))
    f.append(text((cxs[1] + cxs[2]) / 2, sy + 28, "замкни головний", size=9, color=MUTED))
    # штатний зворотний шлях ON → OFF
    f.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
             % (cxs[2], sy - rh / 2, cxs[2] - 100, sy - 92, cxs[0] + 100, sy - 92, cxs[0], sy - rh / 2, MUTED))
    f.append(text((cxs[0] + cxs[2]) / 2, sy - 98, "команда «вимкнути» (штатно)", size=9, color=MUTED, bold=True))
    # FAULT
    fy = 370
    fcx = W / 2
    f.append(rect(fcx - 135, fy - 40, 270, 80, fill="#fdf3f2", stroke=C_BAD, sw=2.4))
    f.append(text(fcx, fy - 12, "FAULT", size=16, color=C_BAD, bold=True))
    f.append(mtext(fcx, fy + 12, "безпечний стан: усе розімкнено,\nвідмова зафіксована (latched)", size=10, color=C_BAD))
    for cx in cxs:
        f.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" stroke="%s" stroke-width="1.8" marker-end="url(#arrow)"/>'
                 % (cx, sy + rh / 2, cx, sy + 120, fcx + (cx - fcx) * 0.22, fy - 62, fcx + (cx - fcx) * 0.38, fy - 40, C_BAD))
    f.append(text(W / 2, sy + 118, "будь-яка з двох ліній захисту · таймаут передзаряду · залиплий контактор · провал живлення",
                  size=9.5, color=C_BAD, bold=True))
    # вихід із FAULT — лише скидання
    f.append('<path d="M%.0f %.0f C %.0f %.0f, %.0f %.0f, %.0f %.0f" fill="none" stroke="%s" stroke-width="1.6" marker-end="url(#arrow)"/>'
             % (fcx - 135, fy, 55, fy, 55, sy, cxs[0] - rw / 2, sy + rh / 4, MUTED))
    f.append(mtext(95, (sy + fy) / 2 + 8, "лише\nскидання", size=9, color=MUTED, bold=True))
    render(os.path.join(IMG, "fsm.svg"), W, H, *f)


# ── 2. Часова діаграма послідовності контакторів ─────────────────────────────
def fig_contactor_timing():
    """Хто коли замкнений: «−» → передзарядний → (ΔU спадає) → головний →
    розмикання передзарядного. Внизу — крива напруги на навантаженні."""
    W, H = 820, 480
    f = [text(W / 2, 28, "Хореографія контакторів у часі (частки секунди)", size=15, bold=True)]
    lab_x = 175
    t0, t1 = 200, 720
    rows = [("«−» контактор", NEG, 80),
            ("передзарядний", GOLD, 130),
            ("головний «+»", POS, 180)]
    tA = 250   # замкнули «−»
    tB = 300   # замкнули передзарядний
    tC = 560   # ΔU мала → замкнули головний
    tD = 610   # розімкнули передзарядний
    for name, col, y in rows:
        f.append(text(lab_x, y + 4, name, size=11, color=col, bold=True, anchor="end"))
        f.append(line(t0, y, t1, y, color="#dfe3e8", sw=1))
    bh = 16
    f.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" fill-opacity="0.85"/>' % (tA, int(80 - bh / 2), t1 - tA, bh, NEG))
    f.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" fill-opacity="0.85"/>' % (tB, int(130 - bh / 2), tD - tB, bh, GOLD))
    f.append('<rect x="%d" y="%d" width="%d" height="%d" rx="4" fill="%s" fill-opacity="0.85"/>' % (tC, int(180 - bh / 2), t1 - tC, bh, POS))
    steps = [(tA, "1"), (tB, "2"), (tC, "4"), (tD, "5")]
    for tx, n in steps:
        f.append(line(tx, 60, tx, 250, color=MUTED, sw=1, dash="3 4"))
        f.append(circle(tx, 60, 11, fill="#fff", stroke=INK, sw=1.6))
        f.append(text(tx, 64, n, size=11, color=INK, bold=True))
    f.append('<rect x="%d" y="%d" width="%d" height="20" rx="4" fill="%s" fill-opacity="0.12"/>' % (tB, 232, tC - tB, FIELD))
    f.append(text((tB + tC) / 2, 246, "3. чекаємо, поки ΔU спаде (вимір, не таймер)", size=9.5, color=FIELD, bold=True))
    # графік напруги на навантаженні
    gy = 360
    gx0, gx1 = t0, t1
    f.append(line(gx0, gy, gx1, gy, color=INK, sw=1.4))
    f.append(line(gx0, gy, gx0, gy - 110, color=INK, sw=1.4))
    f.append(text(gx0 - 8, gy - 110, "U навант.", size=9, color=MUTED, anchor="end"))
    f.append(text(gx1 + 6, gy + 4, "час", size=9, color=MUTED, anchor="start"))
    f.append(line(gx0, gy - 96, gx1, gy - 96, color=MUTED, sw=1, dash="4 4"))
    f.append(text(gx1 - 4, gy - 100, "U пакета", size=9, color=MUTED, anchor="end"))
    pts = []
    for i in range(0, 61):
        tt = tB + (tC - tB) * i / 60.0
        frac = 1 - math.exp(-3.2 * i / 60.0)
        pts.append("%.0f,%.0f" % (tt, gy - 96 * frac))
    pts.append("%.0f,%.0f" % (tC, gy - 96))
    pts.append("%.0f,%.0f" % (gx1, gy - 96))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts), GOLD))
    f.append(line(gx0, gy, tB, gy, color=GOLD, sw=2.6))
    f.append(text(tC + 6, gy - 84, "ΔU мала → замикаємо головний", size=9.5, color=POS, bold=True, anchor="start"))
    f.append(mtext((tB + tC) / 2, gy - 34, "заряд крізь резистор\n(стала часу R·C)", size=9, color=GOLD, bold=True))
    f.append(fitbox(40, 412, W - 80, 50,
                    "Перекриття на кроках 4–5 навмисне: головний замикають ПЕРШ, ніж розімкнути передзарядний, інакше струм рвався б крізь резистор.\nКрок 3 — не пауза за таймером, а очікування виміряної умови ΔU < поріг; не дочекались за відведений час → FAULT.",
                    size=10, fill=FILL, stroke=MUTED, sw=1.3))
    render(os.path.join(IMG, "contactor-timing.svg"), W, H, *f)


# ── 3. Дребезг сигналу й часовий фільтр ──────────────────────────────────────
def fig_debounce():
    """Сирий сигнал захисту дребезжить на порозі; рішення приймаємо лише
    коли стан протримався N зчитувань поспіль (підтвердження в часі)."""
    W, H = 820, 360
    f = [text(W / 2, 28, "Дребезг порога: підтверджуй стан у часі, не за одним зчитуванням", size=14.5, bold=True)]
    gx0, gx1 = 150, 760
    ry = 110
    f.append(mtext(gx0 - 12, ry - 6, "сире\nзчитування", size=10, color=MUTED, anchor="end"))
    raw = [0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    seg = (gx1 - gx0) / float(len(raw))
    amp = 34
    py = lambda v: ry - v * amp
    pts = []
    for i, v in enumerate(raw):
        x = gx0 + i * seg
        pts.append("%.0f,%.0f" % (x, py(v)))
        pts.append("%.0f,%.0f" % (x + seg, py(v)))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2"/>' % (" ".join(pts), C_BAD))
    f.append(line(gx0, ry - amp / 2, gx1, ry - amp / 2, color=MUTED, sw=1, dash="4 4"))
    f.append(text(gx1 + 4, ry - amp / 2 + 3, "поріг", size=9, color=MUTED, anchor="start"))
    fy = 240
    f.append(mtext(gx0 - 12, fy - 6, "рішення\n(N поспіль)", size=10, color=FIELD, anchor="end"))
    N = 4
    cnt = 0
    dec = []
    for v in raw:
        cnt = cnt + 1 if v == 1 else 0
        dec.append(1 if cnt >= N else 0)
    pts2 = []
    for i, v in enumerate(dec):
        x = gx0 + i * seg
        col_y = fy - v * amp
        pts2.append("%.0f,%.0f" % (x, col_y))
        pts2.append("%.0f,%.0f" % (x + seg, col_y))
    f.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.6"/>' % (" ".join(pts2), FIELD))
    trip_i = dec.index(1)
    tx = gx0 + (trip_i + 1) * seg
    f.append(line(tx, 78, tx, 280, color=INK, sw=1.2, dash="2 4"))
    f.append(text(tx, 300, "тут підтверджено", size=9.5, color=INK, bold=True))
    f.append(fitbox(40, 318, W - 80, 32,
                    "Рубали б за першою одиницею — кожна голка на порозі давала б хибну аварію. Лічильник N однакових зчитувань поспіль глушить дребезг ціною малої затримки.",
                    size=10, fill=FILL, stroke=FIELD, sw=1.3))
    render(os.path.join(IMG, "debounce.svg"), W, H, *f)


if __name__ == "__main__":
    fig_fsm()
    fig_contactor_timing()
    fig_debounce()
    print("OK: 3 figures ->", IMG)
