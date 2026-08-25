# -*- coding: utf-8 -*-
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts')); from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори шарів (тримаємо палітру svgkit, додаємо м'які заливки для смуг)
AMBER  = "#b8860b"     # навігація / служби
F_NAV  = "#fbf3e0"
F_VEH  = "#eef0f4"
F_CTRL = "#eafaf0"
F_EST  = "#f3f4f6"
F_DRV  = "#eef3ff"
F_HAL  = "#e3effb"


# ── layers: стос шарів знизу (HAL) вгору (апарат і режими), служби збоку ───────
# Ідея: вертикальний стос полиць — кожна спирається лише на сусідню знизу;
# наскрізна стрілка «потік даних» збоку та окрема панель наскрізних служб.

def fig_layers():
    W, H = 960, 540
    p = []
    lx, lw = 60, 580          # ліва межа й ширина смуг шарів
    top = 70
    bh, gap = 66, 8           # висота смуги й проміжок
    # зверху вниз у малюнку = від вершини стосу до фундаменту
    rows = [
        ("Апарат і режими", "ArduCopter · ArduPlane · Rover — головний цикл, мікшер", F_VEH, INK),
        ("Навігація", "AP_Mission · AC_WPNav · режими (Auto/RTL/Loiter) → уставка", F_NAV, AMBER),
        ("Керування", "AC_AttitudeControl · AC_PosControl · AC_PID", F_CTRL, FIELD),
        ("Оцінювач стану", "AP_AHRS + EKF3 → орієнтація, положення, швидкість", F_EST, INK),
        ("Драйвери давачів", "AP_InertialSensor · AP_GPS · AP_Baro · AP_Compass", F_DRV, NEG),
        ("HAL — апаратна абстракція", "AP_HAL: UART · I2C · SPI · GPIO · RCOut · Scheduler", F_HAL, NEG),
    ]
    y = top
    for title, sub, fill, col in rows:
        p.append(rect(lx, y, lw, bh, fill=fill, stroke=col, sw=1.7, rx=9))
        p.append(text(lx + 16, y + 26, title, size=13, color=col, anchor="start", bold=True))
        p.append(text(lx + 16, y + 48, sub, size=11, color=INK, anchor="start"))
        y += bh + gap
    stack_bottom = y - gap

    # стрілка «потік даних» збоку (вниз = наміри, вгору = виміри): показуємо вгору
    ax = lx - 16
    p.append(arrow(ax, stack_bottom - 6, ax, top + 6, color=MUTED, sw=2.0))
    p.append(text(ax - 12, (top + stack_bottom) / 2, "потік", size=10, color=MUTED, anchor="middle"))

    # панель наскрізних служб справа
    sx = lx + lw + 30
    sw_panel = 250
    p.append(rect(sx, top, sw_panel, stack_bottom - top, fill="#fbfbfd", stroke=MUTED, sw=1.5, rx=12))
    p.append(text(sx + sw_panel / 2, top + 26, "НАСКРІЗНІ СЛУЖБИ", size=12, color=INK, bold=True))
    svc = [
        ("AP_Scheduler", "темпи задач"),
        ("GCS_MAVLink", "зв'язок із землею"),
        ("AP_Logger", "журнали польоту"),
        ("AP_Param", "параметри"),
    ]
    cy = top + 56
    ch = (stack_bottom - top - 56 - 16) / len(svc)
    for name, desc in svc:
        p.append(rect(sx + 16, cy, sw_panel - 32, ch - 12, fill=BG, stroke=MUTED, sw=1.1, rx=8))
        p.append(text(sx + 30, cy + (ch - 12) / 2 - 4, name, size=12, color=NEG, anchor="start", bold=True))
        p.append(text(sx + 30, cy + (ch - 12) / 2 + 15, desc, size=10, color=MUTED, anchor="start"))
        cy += ch

    p.append(text(W / 2, H - 18,
                  "Кожен шар спирається лише на сусідній знизу — тому шар можна замінити, не чіпаючи решти.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "layers.svg"), W, H, *p,
           title="Шари ArduPilot: знизу — залізо, згори — місія")


# ── modules: чотириланковий контур з іменами модулів під кожним блоком ─────────
# Ідея: знайома замкнена петля давачі→оцінювач→керування→виконання, але кожен
# блок підписано реальною бібліотекою; уставку згори дає навігація.

def fig_modules():
    W, H = 960, 400
    p = []
    y, bh = 188, 96
    blocks = [
        (40, 196, "ДАВАЧІ", ["AP_InertialSensor", "AP_GPS · AP_Baro", "AP_Compass"], NEG, F_DRV),
        (276, 168, "ОЦІНЮВАЧ", ["AP_AHRS", "EKF3"], INK, F_EST),
        (484, 188, "КЕРУВАННЯ", ["AC_AttitudeControl", "AC_PosControl", "AC_PID"], FIELD, F_CTRL),
        (712, 196, "ВИКОНАННЯ", ["AP_Motors", "SRV_Channels"], AMBER, F_NAV),
    ]
    centers = []
    for x, w, title, libs, col, fill in blocks:
        p.append(rect(x, y, w, bh, fill=fill, stroke=col, sw=1.7, rx=11))
        p.append(text(x + w / 2, y + 22, title, size=13, color=col, bold=True))
        ly = y + 44
        for lib in libs:
            p.append(text(x + w / 2, ly, lib, size=11, color=INK))
            ly += 16
        centers.append((x, x + w))

    labels = ["вимір", "стан", "команди"]
    for i in range(3):
        x1 = centers[i][1]
        x2 = centers[i + 1][0]
        p.append(arrow(x1 + 3, y + bh / 2, x2 - 3, y + bh / 2, color=INK, sw=2.0))
        p.append(text((x1 + x2) / 2, y - 10, labels[i], size=10.5, color=MUTED))

    # навігація згори дає уставку керуванню
    nx, nw = 470, 216
    ny, nh = 78, 56
    p.append(rect(nx, ny, nw, nh, fill=F_NAV, stroke=AMBER, sw=1.5, rx=9))
    p.append(text(nx + nw / 2, ny + 22, "Навігація / режими", size=12, color=AMBER, bold=True))
    p.append(text(nx + nw / 2, ny + 42, "AP_Mission · AC_WPNav", size=11, color=INK))
    ctrl_cx = (blocks[2][0] + blocks[2][0] + blocks[2][1]) / 2
    p.append(arrow(ctrl_cx, ny + nh, ctrl_cx, y - 2, color=AMBER, sw=2.0))
    p.append(text(ctrl_cx + 58, (ny + nh + y) / 2, "уставка", size=10.5, color=AMBER, anchor="start", italic=True))

    # замикання петлі: виконання → апарат рухається → давачі міряють знову
    out_cx = (blocks[3][0] + blocks[3][1] + blocks[3][0]) / 2
    in_cx = (blocks[0][0] + blocks[0][1]) / 2
    loop_y = y + bh + 54
    p.append(line(out_cx, y + bh, out_cx, loop_y, color=INK, sw=2.0))
    p.append(line(out_cx, loop_y, in_cx, loop_y, color=INK, sw=2.0))
    p.append(arrow(in_cx, loop_y, in_cx, y + bh + 2, color=INK, sw=2.0))
    p.append(text((out_cx + in_cx) / 2, loop_y - 8, "апарат рухається → давачі міряють знову",
                  size=11, color=INK))

    p.append(text(W / 2, H - 16,
                  "Упізнавши ці імена у вихідниках, одразу знаєш, яку ланку контуру читаєш.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "modules.svg"), W, H, *p,
           title="Той самий контур — з іменами модулів ArduPilot")


# ── hal: AP_HAL як спільний інтерфейс над різними бекендами ────────────────────
# Ідея: один блок політного коду → тонка смуга AP_HAL → чотири бекенди (ChibiOS,
# Linux, ESP32, SITL); SITL виділено як симулятор.

def fig_hal():
    W, H = 940, 430
    p = []
    # політний код
    p.append(rect(70, 76, 800, 64, fill=F_CTRL, stroke=FIELD, sw=1.8, rx=12))
    p.append(text(470, 104, "Політний код ArduPilot", size=14, color=FIELD, bold=True))
    p.append(text(470, 126, "єдиний, незалежний від плати (оцінювач, керування, навігація)",
                  size=11.5, color=INK))
    # смуга HAL
    p.append(rect(70, 160, 800, 44, fill=F_EST, stroke=INK, sw=1.6, rx=10))
    p.append(text(470, 187, "AP_HAL — однаковий інтерфейс: UART · I2C · SPI · GPIO · RCOut · Scheduler",
                  size=12, color=INK, bold=True))
    # бекенди
    backs = [
        ("ChibiOS", "STM32: Pixhawk, Cube…", NEG, F_HAL),
        ("Linux", "одноплатники", NEG, F_HAL),
        ("ESP32", "Wi-Fi мікроконтролери", NEG, F_HAL),
        ("SITL", "симуляція на ПК", FIELD, F_CTRL),
    ]
    bw, by, bh = 185, 252, 74
    gap = (800 - 4 * bw) / 3
    x = 70
    for name, desc, col, fill in backs:
        p.append(arrow(x + bw / 2, 204, x + bw / 2, by - 2, color=MUTED, sw=1.6))
        p.append(rect(x, by, bw, bh, fill=fill, stroke=col, sw=1.7, rx=11))
        p.append(text(x + bw / 2, by + 30, name, size=13, color=col, bold=True))
        p.append(text(x + bw / 2, by + 52, desc, size=11, color=INK))
        x += bw + gap

    p.append(text(470, 372, "SITL — увесь стек на комп'ютері проти змодельованої фізики:",
                  size=12, color=FIELD, bold=True))
    p.append(text(470, 392, "«розбивай» дрон тисячу разів безпечно, перш ніж торкнутися заліза.",
                  size=12, color=FIELD))

    render(os.path.join(OUT, "hal.svg"), W, H, *p,
           title="HAL: один код — десятки плат і навіть симулятор")


# ── scheduler: таблиця задач з частотами й точками відносної густини ───────────
# Ідея: рядок на задачу; колонка частоти з точками = відносна густина запусків;
# fast_loop найгустіший (критичний), службове — раз на секунду.

def fig_scheduler():
    W, H = 940, 430
    p = []
    cols = [(40, 200), (250, 160), (420, 480)]   # (x, width) для трьох колонок
    head = ["Задача", "Частота", "Що робить"]
    hy, hh = 80, 34
    for (x, w), t in zip(cols, head):
        p.append(rect(x, hy, w, hh, fill=INK, stroke=INK, sw=1.6, rx=7))
        p.append(text(x + 14, hy + 23, t, size=12, color=BG, anchor="start", bold=True))

    rows = [
        ("fast_loop", "400 Гц", "IMU → оцінювач → контур орієнтації", 12, FIELD, F_CTRL),
        ("update_GPS", "50 Гц", "оновити положення з GNSS", 5, NEG, BG),
        ("update_nav", "10–50 Гц", "контур положення, навігація", 4, NEG, "#fafafa"),
        ("gcs_update", "50 Гц", "обмін MAVLink із землею", 5, NEG, BG),
        ("update_logging", "25–400 Гц", "писати журнали польоту", 8, NEG, "#fafafa"),
        ("one_hz_loop", "1 Гц", "перевірки здоров'я, службове", 1, NEG, BG),
    ]
    ry, rh = hy + hh, 46
    for name, freq, what, dots, dotcol, fill in rows:
        for (x, w) in cols:
            p.append(rect(x, ry, w, rh, fill=fill, stroke=MUTED, sw=1.0, rx=8))
        p.append(text(cols[0][0] + 14, ry + 28, name, size=12, color=dotcol if name == "fast_loop" else INK,
                      anchor="start", bold=True))
        p.append(text(cols[1][0] + 14, ry + 20, freq, size=12, color=INK, anchor="start", bold=True))
        # точки відносної густини
        dx = cols[1][0] + 16
        for i in range(dots):
            p.append(circle(dx + i * 11, ry + 34, 3, fill=dotcol, stroke=dotcol, sw=1.0))
        p.append(text(cols[2][0] + 14, ry + 28, what, size=11.5, color=INK, anchor="start"))
        ry += rh

    p.append(text(W / 2, H - 14,
                  "Точки = відносна густина запусків. fast_loop — критичний внутрішній контур: мусить устигати кожні 2.5 мс.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "scheduler.svg"), W, H, *p,
           title="Планувальник: кожна задача — у своєму темпі")


# ── tree: карта дерева вихідників ArduPilot ───────────────────────────────────
# Ідея: дерево тек із підписами ролей справа; легенда префіксів AP_/AC_ унизу.

def fig_tree():
    W, H = 940, 500
    p = []
    p.append(rect(50, 76, 840, 350, fill="#fbfbfd", stroke=MUTED, sw=1.5, rx=12))
    MONO = INK
    rows = [
        ("ardupilot/", "", INK, False),
        ("├─ ArduCopter/  ArduPlane/  Rover/  ArduSub/", "код апаратів: режими, головний цикл", INK, False),
        ("├─ libraries/", "", INK, False),
        ("│    ├─ AP_HAL*/", "HAL і бекенди (плата, SITL)", NEG, True),
        ("│    ├─ AP_InertialSensor/ AP_GPS/ AP_Baro/", "драйвери давачів", NEG, True),
        ("│    ├─ AP_AHRS/  AP_NavEKF3/", "оцінювач стану", INK, True),
        ("│    ├─ AC_AttitudeControl/ AC_PID/ AC_WPNav/", "керування й навігація", FIELD, True),
        ("│    └─ GCS_MAVLink/ AP_Logger/ AP_Param/", "наскрізні служби", AMBER, True),
        ("└─ Tools/", "SITL, autotest, скрипти", INK, False),
    ]
    ty = 112
    for code, role, col, bold in rows:
        p.append(text(70, ty, code, size=13, color=col, anchor="start", bold=bold))
        if role:
            p.append(text(556, ty, "← " + role, size=11.5, color=MUTED, anchor="start"))
        ty += 34

    # легенда префіксів
    p.append(rect(70, 388, 800, 30, fill=F_DRV, stroke=NEG, sw=1.3, rx=8))
    p.append(text(84, 408, "AP_*  — спільні бібліотеки ArduPilot   ·   AC_*  — родом з ArduCopter",
                  size=12, color=NEG, anchor="start", bold=True))

    p.append(text(W / 2, H - 14,
                  "За префіксом і текою одразу видно, яку ланку контуру реалізує гілка коду.",
                  size=11, color=MUTED, italic=True))

    render(os.path.join(OUT, "tree.svg"), W, H, *p,
           title="Де що шукати: карта вихідників ArduPilot")


if __name__ == "__main__":
    fig_layers()
    fig_modules()
    fig_hal()
    fig_scheduler()
    fig_tree()
    print("OK: figures written to", OUT)
