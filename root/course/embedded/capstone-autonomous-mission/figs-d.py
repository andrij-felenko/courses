# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. Геометрія «влучив у вейпойнт»: радіус vs площина проходу ──────────────
def fig_waypoint_geometry():
    W, H = 960, 520
    p = []
    p.append(text(W / 2, 30,
                  "коли автопілот вважає вейпойнт «пройденим» — два різні критерії",
                  size=13, color=MUTED))

    # ЛІВА панель: критерій «радіус влучення»
    lx = 230
    ly = 210
    p.append(text(lx, 70, "критерій радіуса", size=14, color=INK, bold=True))
    # маршрут A -> WP
    ax = 40
    p.append(circle(ax, ly, 6, fill=NEG, stroke=NEG, sw=1))
    p.append(text(ax, ly + 26, "старт A", size=11.5, color=MUTED))
    # коло радіуса влучення
    r = 70
    p.append(circle(lx, ly, r, fill="none", stroke=FIELD, sw=1.8))
    p.append(circle(lx, ly, 5, fill=INK, stroke=INK, sw=1))
    p.append(text(lx, ly - r - 10, "WP #k", size=12, color=INK, bold=True))
    # лінія маршруту
    p.append(line(ax + 6, ly, lx, ly, color=LINE, sw=1.4, dash="5,4"))
    # радіус-стрілка
    p.append(line(lx, ly, lx + r * 0.7, ly - r * 0.72, color=FIELD, sw=1.4))
    p.append(text(lx + 30, ly - 46, "WP_RADIUS", size=11, color="#1e7d42", bold=True))
    # апарат, що кружляє й НЕ влучає (мала швидкість/великий радіус розвороту)
    import math
    cxs, cys = [], []
    for a in range(0, 360, 12):
        rr = r + 34 + 10 * math.sin(math.radians(a * 3))
        cxs.append(lx + rr * math.cos(math.radians(a)))
        cys.append(ly + rr * math.sin(math.radians(a)))
    pts = " ".join("%.1f,%.1f" % (x, y) for x, y in zip(cxs, cys))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.4" stroke-dasharray="3,3"/>' % (pts, POS))
    p.append(text(lx, ly + r + 60, "апарат кружляє ЗА колом →", size=11, color=POS))
    p.append(text(lx, ly + r + 76, "радіус не досягнуто → індекс СТОЇТЬ", size=11, color=POS, bold=True))

    # роздільник
    p.append(line(W / 2, 56, W / 2, H - 90, color="#dfe3e8", sw=1.2))

    # ПРАВА панель: критерій «площина проходу» (passed-plane)
    rx0 = W / 2 + 60
    rcx = rx0 + 190
    ry = 210
    p.append(text(rcx, 70, "критерій площини проходу", size=14, color=INK, bold=True))
    # старт
    p.append(circle(rx0, ry + 60, 6, fill=NEG, stroke=NEG, sw=1))
    p.append(text(rx0, ry + 86, "старт", size=11.5, color=MUTED))
    # WP
    p.append(circle(rcx, ry, 5, fill=INK, stroke=INK, sw=1))
    p.append(text(rcx, ry - 16, "WP #k", size=12, color=INK, bold=True))
    # лінія курсу до WP
    p.append(line(rx0 + 6, ry + 60, rcx, ry, color=LINE, sw=1.4, dash="5,4"))
    # площина, перпендикулярна курсу, через WP
    # напрям курсу
    dx, dy = rcx - rx0, ry - (ry + 60)
    L = (dx * dx + dy * dy) ** 0.5
    ux, uy = dx / L, dy / L        # уздовж курсу
    nx, ny = -uy, ux              # нормаль (площина)
    hl = 95
    p.append(line(rcx - nx * hl, ry - ny * hl, rcx + nx * hl, ry + ny * hl,
                  color=FIELD, sw=2.2))
    p.append(text(rcx + nx * hl + 4, ry + ny * hl + 4, "площина", size=11, color="#1e7d42", bold=True))
    p.append(text(rcx + nx * hl + 4, ry + ny * hl + 20, "через WP", size=11, color="#1e7d42"))
    # траєкторія, що проходить ПОВЗ WP але перетинає площину
    tx, ty = [], []
    for t in range(0, 101):
        s = t / 100.0
        # дуга, що проходить збоку від WP
        bx = rx0 + 60 + (rcx + 120 - (rx0 + 60)) * s
        by = ry + 60 - 150 * s + 40 * math.sin(math.radians(s * 180))
        tx.append(bx); ty.append(by)
    pts2 = " ".join("%.1f,%.1f" % (x, y) for x, y in zip(tx, ty))
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (pts2, POS))
    p.append(text(rcx + 40, ry + 70, "перетнув площину →", size=11, color=POS))
    p.append(text(rcx + 40, ry + 86, "вейпойнт зараховано, індекс ІДЕ", size=11, color=POS, bold=True))

    # нижня плашка-висновок
    b, bw, bh = textbox(W / 2, H - 46,
                        "коптер: критерій радіуса (треба фізично зайти в коло) · літак: часто площина проходу\n"
                        "(зарахувати, коли ніс перетнув лінію через точку) — інакше на розвороті він не влучив би НІКОЛИ",
                        size=12, pad=12, fill="#f7faf7", stroke=FIELD, color=INK)
    p.append(b)
    return render(os.path.join(OUT, "waypoint-geometry.svg"), W, H, *p)


# ── 2. Завантаження місії: таймаут, повтор, відкидання не по порядку ─────────
def fig_upload_timeline():
    W, H = 980, 600
    p = []
    p.append(text(W / 2, 28, "рукостискання місії в часі: таймаут 250 мс, повтор, відкидання не по порядку",
                  size=13, color=MUTED))

    gcs_x = 160
    veh_x = 830
    top = 66
    bot = H - 78
    # дві вертикалі-актори
    p.append(line(gcs_x, top, gcs_x, bot, color=LINE, sw=2))
    p.append(line(veh_x, top, veh_x, bot, color=LINE, sw=2))
    p.append(text(gcs_x, top - 12, "GCS (земля)", size=13, color=INK, bold=True))
    p.append(text(veh_x, top - 12, "борт", size=13, color=INK, bold=True))

    def msg(y, x1, x2, label, color=LINE, dash=None, bad=False):
        p.append(arrow(x1, y, x2, y, color=color, sw=1.8))
        midx = (x1 + x2) / 2
        p.append(text(midx, y - 8, label, size=11.5, color=color, bold=bad))

    y = top + 30
    dy = 40
    # COUNT
    msg(y, gcs_x, veh_x, "MISSION_COUNT = 6", color=NEG); y += dy
    # REQUEST 0
    msg(y, veh_x, gcs_x, "REQUEST_INT #0", color=INK); y += dy
    # ITEM 0
    msg(y, gcs_x, veh_x, "ITEM_INT #0  (TAKEOFF)", color=NEG); y += dy
    # REQUEST 1
    msg(y, veh_x, gcs_x, "REQUEST_INT #1", color=INK); y += dy
    # ITEM 1 — ГУБИТЬСЯ
    yl = y
    p.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="1.8" stroke-dasharray="6,4"/>'
             % (gcs_x, yl, (gcs_x + veh_x) / 2 + 40, yl - 6, POS))
    p.append(text((gcs_x + veh_x) / 2 + 70, yl - 12, "ITEM #1 ✕ загубився", size=11.5, color=POS, bold=True))
    p.append(text((gcs_x + veh_x) / 2 + 90, yl + 8, "✕", size=18, color=POS, bold=True)); y += dy
    # таймаут на борту
    p.append(text(veh_x + 4, y - 6, "⧗ таймаут 250 мс", size=11.5, color="#b56c12", bold=True, anchor="start"))
    p.append(line(veh_x - 8, y - 20, veh_x - 8, y + 6, color="#d98218", sw=3)); y += dy - 8
    # повторний REQUEST 1
    msg(y, veh_x, gcs_x, "REQUEST_INT #1  (повтор)", color="#b56c12", bad=True); y += dy
    # ITEM 1 знову
    msg(y, gcs_x, veh_x, "ITEM_INT #1  (WAYPOINT A)", color=NEG); y += dy
    # GCS помилково шле #3 замість #2
    yl = y
    msg(y, gcs_x, veh_x, "ITEM_INT #3  (не той seq!)", color=POS, bad=True); y += dy
    p.append(text(veh_x + 4, y - 14, "борт відкидає: чекав #2", size=11, color=POS, anchor="start"))
    # повторний REQUEST 2
    msg(y + 4, veh_x, gcs_x, "REQUEST_INT #2  (знову просить очікуване)", color=INK); y += dy + 4

    # фінал
    b, bw, bh = textbox(W / 2, bot + 34,
                        "надійність тримає ТОЙ, ХТО ЗБЕРІГАЄ РЕЗУЛЬТАТ: борт не рушить, поки не отримає КОЖЕН seq по порядку;\n"
                        "загубився пакет → повтор за таймаутом; прийшов не той номер → відкинути й перепитати очікуваний",
                        size=11.5, pad=11, fill="#f7faf7", stroke=FIELD, color=INK)
    p.append(b)
    return render(os.path.join(OUT, "upload-timeline.svg"), W, H, *p)


# ── 3. Драбина пріоритету: хто переможе, коли спрацювало кілька захистів ─────
def fig_priority_ladder():
    W, H = 900, 560
    p = []
    p.append(text(W / 2, 30, "коли одночасно кричать кілька захистів — виграє ВИЩИЙ пріоритет",
                  size=13, color=MUTED))

    rungs = [
        ("1", "КРИТИЧНА батарея / збій живлення",
         "сісти НЕГАЙНО там, де є — вище за все інше", POS, "#fdecea"),
        ("2", "GEOFENCE — вихід за межу",
         "дія межі (RTL або посадка) — перехоплює маршрут", "#b56c12", "#fff6e6"),
        ("3", "Втрата RC / телеметрії (failsafe лінка)",
         "RTL: набрати RTL_ALT і повернутися додому", NEG, "#eaf3ff"),
        ("4", "Збій давача / EKF (оцінка стану «попливла»)",
         "перейти в безпечніший режим (утримання/land)", "#7a5cb0", "#f1ecf7"),
        ("5", "МІСІЯ — звичайний крок #k",
         "виконувати список, поки жоден вищий шар мовчить", FIELD, "#eef7ee"),
    ]
    x = 60
    w = W - 120
    y = 70
    rh = 78
    gap = 14
    for i, (num, title, act, col, fill) in enumerate(rungs):
        p.append(rect(x, y, w, rh, fill=fill, stroke=col, sw=2, rx=10))
        # номер-пріоритет
        p.append(circle(x + 34, y + rh / 2, 20, fill=BG, stroke=col, sw=2.2))
        p.append(text(x + 34, y + rh / 2 + 6, num, size=18, color=col, bold=True))
        p.append(text(x + 70, y + 30, title, size=14, color=INK, bold=True, anchor="start"))
        p.append(text(x + 70, y + 54, act, size=12, color=MUTED, anchor="start"))
        # стрілка «вищий бере гору» — вниз пригнічує
        if i < len(rungs) - 1:
            p.append(arrow(x + w + 18, y + rh, x + w + 18, y + rh + gap, color=MUTED, sw=1.6))
        y += rh + gap
    return render(os.path.join(OUT, "priority-ladder.svg"), W, H, *p)


if __name__ == "__main__":
    fig_waypoint_geometry()
    fig_upload_timeline()
    fig_priority_ladder()
    print("ok")
