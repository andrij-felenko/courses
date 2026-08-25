# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *
import math

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "Consolas, 'DejaVu Sans Mono', monospace"


def mono(x, y, s, size=12, color=INK, anchor="middle", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


# ── one-firmware: один образ → багато апаратів через FRAME_CLASS ───────────────
# Ідея: той самий двійковий образ Copter стає квадро/гекса/окто/три лише числом
# параметра FRAME_CLASS; код описує ВСІ можливості, параметр обирає одну.

def fig_one_firmware():
    W, H = 760, 340
    p = []
    # центр — один образ
    core, cw, ch = textbox(W / 2, 92, "ArduCopter\nодин двійковий образ (той самий код)",
                           size=12, bold=True, fill="#eafaf0", stroke=FIELD, sw=1.8, pad=12)
    p.append(core)

    apparats = [
        (110, "Квадро", "×4 мотори", "FRAME_CLASS = 1"),
        (300, "Гекса", "×6 моторів", "FRAME_CLASS = 2"),
        (490, "Окто", "×8 моторів", "FRAME_CLASS = 3"),
        (660, "Трикоптер", "×3 + серво", "FRAME_CLASS = 7"),
    ]
    by, bw, bh = 198, 150, 92
    for cx, name, motors, par in apparats:
        # стрілка від образу вниз до апарата
        p.append(line(W / 2, 92 + ch / 2, cx, by - 4, color=MUTED, sw=1.4))
        p.append(rect(cx - bw / 2, by, bw, bh, fill=BG, stroke=INK, sw=1.4))
        p.append(text(cx, by + 24, name, size=13, color=INK, bold=True))
        p.append(text(cx, by + 44, motors, size=11, color=MUTED))
        p.append(rect(cx - bw / 2 + 10, by + 58, bw - 20, 24, fill="#f4f6f8", stroke=MUTED, sw=1.0))
        p.append(mono(cx, by + 74, par, size=10.5, color=INK, bold=True))

    p.append(text(W / 2, H - 16,
                  "традиційний гелікоптер — окремий образ із суфіксом -heli (керування геть інше)",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "one-firmware.svg"), W, H, *p,
           title="Одна прошивка — багато апаратів: вирішує параметр FRAME_CLASS")


# ── param-anatomy: ім'я параметра як адреса з груп ────────────────────────────
# Ідея: ATC_RAT_RLL_P читається зліва направо як адреса (група → контур → вісь →
# коефіцієнт); значення живе окремо, у незалежній пам'яті.

def fig_param_anatomy():
    W, H = 760, 400
    p = []
    segs = [
        ("ATC", "група: керування орієнтацією", NEG, 96),
        ("RAT", "контур кутової швидкості", FIELD, 80),
        ("RLL", "вісь крену (Roll)", "#d98a00", 80),
        ("P", "пропорційний коеф.", POS, 56),
    ]
    x = 120
    top = 92
    for code, desc, col, w in segs:
        p.append(rect(x, top, w, 40, fill=BG, stroke=col, sw=1.7))
        p.append(mono(x + w / 2, top + 26, code, size=15, color=col, bold=True))
        p.append(line(x + w / 2, top + 40, x + w / 2, top + 62, color=col, sw=1.1))
        p.append(text(x + w / 2, top + 78, desc, size=10, color=col))
        x += w + 8
    p.append(mono(x + 6, top + 26, "= 0.135", size=15, color=INK, anchor="start", bold=True))
    p.append(text(x + 96, top + 26, "← значення", size=12, color=MUTED, anchor="start"))

    # рядок про незалежну пам'ять
    p.append(text(120, 212,
                  "Значення живе в незалежній пам'яті (AP_Param) — переживає перезавантаження.",
                  size=11.5, color=INK, anchor="start"))

    # таблиця прикладів
    p.append(text(120, 250, "Інші параметри читаються так само:", size=12.5, color=INK, anchor="start", bold=True))
    rows = [
        ("FRAME_CLASS = 1", "тип рами: квадрокоптер"),
        ("ANGLE_MAX = 3000", "макс. нахил = 30.00° (у сотих градуса)"),
        ("BATT_LOW_VOLT = 14.0", "поріг низького заряду → failsafe"),
        ("FS_THR_ENABLE = 1", "реакція на втрату RC-зв'язку"),
    ]
    ry = 268
    for name, desc in rows:
        p.append(rect(120, ry, 250, 28, fill="#f4f6f8", stroke=MUTED, sw=1.0))
        p.append(mono(132, ry + 19, name, size=11.5, color=INK, anchor="start", bold=True))
        p.append(rect(378, ry, 262, 28, fill=BG, stroke=MUTED, sw=1.0))
        p.append(text(390, ry + 19, desc, size=11, color=INK, anchor="start"))
        ry += 32

    render(os.path.join(OUT, "param-anatomy.svg"), W, H, *p,
           title="Будова параметра: ім'я кодує сенс, значення — поведінку")


# ── gcs-roles: п'ять ролей наземної станції + межа з контуром ─────────────────
# Ідея: станція й контролер говорять по MAVLink (двобічно); станція робить п'ять
# речей, але всі вони — взаємодія з готовою системою, а не керування моторами.

def fig_gcs_roles():
    W, H = 760, 360
    p = []
    # дві коробки + двобічний MAVLink
    sb, sbw, sbh = (110, 78), 220, 64
    p.append(rect(sb[0], sb[1], sbw, sbh, fill="#fff5e6", stroke="#d98a00", sw=1.8))
    p.append(text(sb[0] + sbw / 2, sb[1] + 26, "НАЗЕМНА СТАНЦІЯ", size=13, color="#d98a00", bold=True))
    p.append(text(sb[0] + sbw / 2, sb[1] + 46, "Mission Planner · QGroundControl", size=10, color=INK))

    fb = (430, 78)
    p.append(rect(fb[0], fb[1], sbw, sbh, fill="#eafaf0", stroke=FIELD, sw=1.8))
    p.append(text(fb[0] + sbw / 2, fb[1] + 26, "ПОЛІТНИЙ КОНТРОЛЕР", size=12.5, color=FIELD, bold=True))
    p.append(text(fb[0] + sbw / 2, fb[1] + 46, "на апараті", size=11, color=INK))

    mx1, mx2 = sb[0] + sbw, fb[0]
    p.append(arrow(mx1 + 2, sb[1] + 24, mx2 - 2, sb[1] + 24, color=INK, sw=1.8))
    p.append(arrow(mx2 - 2, sb[1] + 42, mx1 + 2, sb[1] + 42, color=INK, sw=1.8))
    p.append(text((mx1 + mx2) / 2, sb[1] + 16, "MAVLink", size=10.5, color=INK, bold=True))
    p.append(text((mx1 + mx2) / 2, sb[1] + 60, "радіо / USB", size=9.5, color=MUTED))

    # п'ять ролей
    p.append(text(60, 188, "П'ять ролей станції:", size=12.5, color=INK, anchor="start", bold=True))
    roles = [
        (60, "Налаштувати", "параметри + калібрування"),
        (300, "Спланувати", "місія з точок"),
        (540, "Стежити", "HUD: крен, висота, заряд"),
        (180, "Аналізувати", "журнали польоту"),
        (420, "Командувати", "зброїти · режим · RTL"),
    ]
    rw, rh = 200, 50
    ys = [206, 206, 206, 268, 268]
    for (rx, title, desc), ry in zip(roles, ys):
        p.append(rect(rx, ry, rw, rh, fill=BG, stroke="#d98a00", sw=1.4))
        p.append(text(rx + rw / 2, ry + 22, title, size=12.5, color=INK, bold=True))
        p.append(text(rx + rw / 2, ry + 40, desc, size=10, color=MUTED))

    p.append(text(W / 2, H - 16,
                  "станція дивиться й велить — летить апарат сам; вона НЕ в контурі керування",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "gcs-roles.svg"), W, H, *p,
           title="Наземна станція: кокпіт оператора на землі")


# ── mission: місія як ланцюг точок ────────────────────────────────────────────
# Ідея: впорядкований список точок із діями; станція планує й вантажить, апарат
# проходить точку за точкою сам; уставку тепер дає список, а не пілот.

def fig_mission():
    W, H = 760, 380
    p = []
    p.append(rect(40, 70, 680, 268, fill="#f7faf7", stroke=MUTED, sw=1.3))

    # точки маршруту
    home = (130, 290)
    wps = [(130, 150), (330, 100), (560, 150), (620, 270)]
    # лінія маршруту
    path_pts = [home] + wps
    poly = " ".join("%.0f,%.0f" % (x, y) for x, y in path_pts)
    p.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.4" '
             'stroke-linejoin="round"/>' % (poly, INK))
    # RTL пунктиром від останньої до дому
    p.append(line(wps[-1][0], wps[-1][1], home[0] + 14, home[1] - 6,
                  color="#d98a00", sw=2.0, dash="7 5"))
    p.append(text(400, 326, "RTL → повернення додому й посадка",
                  size=11, color="#d98a00", anchor="middle", bold=True))

    labels = ["1 · Зліт", "2 · Точка", "3 · Очікування", "4 · Точка"]
    lw = 150  # ширина підпису

    def label_box(x, y, text_s, stroke):
        # підпис праворуч від точки, а якщо вилазить за праву межу — ліворуч
        if x + 20 + lw <= 720:
            bx, tx, anch = x + 20, x + 28, "start"
        else:
            bx, tx, anch = x - 20 - lw, x - 28, "end"
        p.append(rect(bx, y - 13, lw, 26, fill=BG, stroke=stroke, sw=1.2))
        p.append(text(tx, y + 5, text_s, size=10.5, color=INK, anchor=anch))

    # дім
    p.append(circle(home[0], home[1], 14, fill=FIELD, stroke=INK, sw=1.6))
    label_box(home[0], home[1], "ДІМ — зліт / посадка", FIELD)
    for (x, y), lab in zip(wps, labels):
        p.append(circle(x, y, 14, fill=NEG, stroke=INK, sw=1.6))
        p.append(text(x, y + 5, lab.split(" ")[0], size=12, color=BG, bold=True))
        label_box(x, y, lab, NEG)

    p.append(text(W / 2, H - 16,
                  "той самий контур — лише бажаний стан тепер задає список точок, а не пілот",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "mission.svg"), W, H, *p,
           title="Місія — це впорядкований список точок із діями")


# ── calibration: сира сфера компаса проти центрованої ─────────────────────────
# Ідея: сирі виміри малюють зміщену й стиснуту «сферу» (hard/soft iron);
# калібрування знаходить зсув і масштаб — сфера центрується на нулі.

def fig_calibration():
    W, H = 760, 380
    p = []
    n = 18

    def panel(ox, label, color, cx_off, cy_off, rx, ry, sub):
        # рамка панелі
        p.append(rect(ox, 86, 300, 210, fill=BG, stroke=INK, sw=1.4))
        p.append(text(ox + 150, 78, label, size=12.5, color=INK, bold=True))
        cx, cy = ox + 150, 196
        # осі
        p.append(line(cx - 92, cy, cx + 92, cy, color=MUTED, sw=1.0))
        p.append(line(cx, cy - 92, cx, cy + 92, color=MUTED, sw=1.0))
        p.append(text(cx - 12, cy - 78, "0", size=10, color=MUTED, anchor="start"))
        # кільце вимірів
        for i in range(n):
            a = 2 * math.pi * i / n
            px = cx + cx_off + rx * math.cos(a)
            py = cy + cy_off + ry * math.sin(a)
            p.append(circle(px, py, 3.4, fill=color, stroke="none", sw=0))
        p.append(text(cx, cy + 84, sub, size=10.5, color=color))

    # ліворуч: сирий — зміщений центр (hard iron) + еліпс (soft iron)
    panel(50, "Сирий компас (до)", POS, 24, 18, 70, 56, "зсув (hard iron) + стиск (soft iron)")
    # стрілка зсуву
    p.append(line(200, 196, 224, 214, color=POS, sw=1.8, dash="4 3"))

    # праворуч: відкалібрований — центровано, круг
    panel(410, "Після калібрування", FIELD, 0, 0, 64, 64, "центровано на 0, кругла сфера")

    p.append(text(W / 2, 326,
                  "«танець» компасом: обертаєш апарат у всі боки — давач описує сферу",
                  size=11.5, color=INK, anchor="middle"))
    p.append(text(W / 2, H - 16,
                  "поправки лягають у параметри COMPASS_OFS_* — і оцінювач знову довіряє курсу",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "calibration.svg"), W, H, *p,
           title="Калібрування компаса: від спотвореної сфери до чесної")


if __name__ == "__main__":
    fig_one_firmware()
    fig_param_anatomy()
    fig_gcs_roles()
    fig_mission()
    fig_calibration()
    print("OK: figures written to", OUT)
