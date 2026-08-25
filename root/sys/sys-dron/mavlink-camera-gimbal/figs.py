# -*- coding: utf-8 -*-
"""Фігури до теми «Протоколи камери й підвісу MAVLink»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def tb(cx, cy, s, **kw):
    body, _w, _h = textbox(cx, cy, s, **kw)
    return body


# ── 1. Компоненти на одному апараті ────────────────────────────────────────
def fig_components():
    W, H = 1000, 470
    f = []
    # наземна станція
    f.append(tb(140, 250, "Наземна станція\nsysid 255\ncompid 190", size=14, min_w=190))
    # апарат — зовнішня рамка
    f.append(rect(360, 90, 600, 340, fill="#ffffff", stroke=MUTED, sw=2, rx=12))
    f.append(text(660, 120, "Апарат — sysid 1", size=15, bold=True, color=MUTED))
    colA, colB = 500, 820
    f.append(tb(colA, 190, "Автопілот\ncompid 1", size=13, min_w=200))
    f.append(tb(colA, 285, "Камера\ncompid 100", size=13, min_w=200))
    f.append(tb(colA, 380, "Підвіс\ncompid 154", size=13, min_w=200))
    f.append(tb(colB, 190, "Бортовий комп'ютер\ncompid 191", size=13, min_w=210))
    f.append(tb(colB, 285, "Друга камера\ncompid 101", size=13, min_w=210))
    f.append(tb(colB, 380, "Другий підвіс\ncompid 171", size=13, min_w=210))
    # радіолінія
    f.append(arrow(228, 250, 352, 250))
    f.append(arrow(352, 268, 228, 268))
    f.append(text(290, 225, "MAVLink", size=13, color=MUTED))
    render(os.path.join(OUT, 'components.svg'), W, H, *f,
           title="Адреса в MAVLink — це пара (sysid, compid)")


# ── 2. Знімки як нумерований журнал подій ──────────────────────────────────
def fig_capture_log():
    W, H = 960, 540
    xs, xc = 150, 770
    f = []
    f.append(tb(xs, 62, "Наземна станція", size=13))
    f.append(tb(xc, 62, "Камера (compid 100)", size=13))
    f.append(line(xs, 92, xs, 510, color=MUTED, dash="5,5"))
    f.append(line(xc, 92, xc, 510, color=MUTED, dash="5,5"))

    def msg(y, label, to_camera=True, color=LINE, dash=False):
        out = []
        if dash:
            out.append(line(xc, y, xs, y, color=color, sw=1.6, dash="7,6"))
        elif to_camera:
            out.append(arrow(xs, y, xc, y, color=color))
        else:
            out.append(arrow(xc, y, xs, y, color=color))
        out.append(text((xs + xc) / 2, y - 11, label, size=13, color=color))
        return "".join(out)

    f.append(msg(150, "MAV_CMD_IMAGE_START_CAPTURE — інтервал 2 с, 4 кадри", True))
    f.append(msg(200, "COMMAND_ACK: ACCEPTED  («прийняв», а не «зняв»)", False))
    f.append(msg(258, "CAMERA_IMAGE_CAPTURED   image_index 41", False))
    f.append(msg(303, "CAMERA_IMAGE_CAPTURED   image_index 42", False))
    f.append(msg(348, "CAMERA_IMAGE_CAPTURED   image_index 43", False,
                 color=POS, dash=True))
    f.append(text((xs + xc) / 2, 370, "загублено в радіоканалі", size=12, color=POS))
    f.append(msg(410, "CAMERA_IMAGE_CAPTURED   image_index 44", False))
    f.append(text((xs + xc) / 2, 432, "станція бачить дірку в нумерації", size=12, color=MUTED))
    f.append(msg(468, "MAV_CMD_REQUEST_MESSAGE (263, index 43)", True))
    f.append(msg(508, "CAMERA_IMAGE_CAPTURED   image_index 43", False))
    render(os.path.join(OUT, 'capture-log.svg'), W, H, *f,
           title="Втрачений кадр добирають за індексом, а не повтором усього потоку")


# ── 3. Два шари підвісу: менеджер і пристрій ───────────────────────────────
def fig_gimbal_layers():
    W, H = 1000, 500
    f = []
    src = [(180, "Наземна станція\n(пілот, джойстик)"),
           (500, "Бортовий комп'ютер\n(стеження за ціллю)"),
           (820, "Місія автопілота\n(команда в маршруті)")]
    for cx, s in src:
        f.append(tb(cx, 115, s, size=13, min_w=230))
        f.append(arrow(cx, 152, cx, 208))
    # менеджер
    f.append(rect(150, 215, 700, 105, fill=FILL, stroke=LINE, sw=2, rx=8))
    f.append(mtext(500, 248, ["Gimbal manager",
                              "приймає SET_ATTITUDE · SET_PITCHYAW · SET_MANUAL_CONTROL",
                              "первинний: 255/190 · вторинний: 1/191"], size=13))
    # донизу — команди пристрою, догори — стан
    f.append(arrow(420, 325, 420, 392))
    f.append(arrow(600, 392, 600, 325))
    f.append(text(230, 362, "GIMBAL_DEVICE_SET_ATTITUDE", size=12, color=MUTED))
    f.append(text(790, 362, "GIMBAL_DEVICE_ATTITUDE_STATUS", size=12, color=MUTED))
    f.append(tb(500, 425, "Gimbal device — залізо підвісу\n(мотори, датчики кута, межі осей)",
                size=13, min_w=420))
    render(os.path.join(OUT, 'gimbal-layers.svg'), W, H, *f,
           title="Керувати пристроєм має право лише менеджер")


# ── 4. Рискання: у рамці апарата чи в рамці землі ──────────────────────────
def fig_yaw_frames():
    W, H = 960, 430
    f = []
    cells = [(180, "До розвороту\n(апарат носом на північ)"),
             (480, "Апарат розвернувся на схід\nYAW_IN_VEHICLE_FRAME (follow)"),
             (790, "Апарат розвернувся на схід\nYAW_IN_EARTH_FRAME (lock)")]
    for cx, cap in cells:
        f.append(tb(cx, 100, cap, size=13, min_w=250))
        f.append(circle(cx, 250, 15))
    # компас
    f.append(arrow(50, 265, 50, 215, color=MUTED))
    f.append(text(50, 288, "Пн", size=13, color=MUTED))
    # 1: ніс і камера — на північ
    f.append(arrow(180 - 22, 234, 180 - 22, 180, color=MUTED))
    f.append(arrow(180 + 22, 234, 180 + 22, 180, color=POS, sw=2.4))
    # 2: follow — обидва на схід
    f.append(arrow(480 + 18, 234, 480 + 78, 234, color=MUTED))
    f.append(arrow(480 + 18, 268, 480 + 78, 268, color=POS, sw=2.4))
    # 3: lock — ніс на схід, камера лишилась на північ
    f.append(arrow(790 + 18, 250, 790 + 78, 250, color=MUTED))
    f.append(arrow(790 - 22, 234, 790 - 22, 180, color=POS, sw=2.4))
    # підписи станів
    f.append(text(180, 330, "початок", size=13, color=MUTED))
    f.append(text(480, 330, "кадр поїхав за корпусом", size=13, color=MUTED))
    f.append(text(790, 330, "кадр стоїть на місці", size=13, color=MUTED))
    # легенда
    f.append(line(230, 385, 280, 385, color=MUTED, sw=2))
    f.append(text(360, 390, "ніс апарата", size=13, color=MUTED, anchor="start"))
    f.append(line(560, 385, 610, 385, color=POS, sw=2.6))
    f.append(text(690, 390, "куди дивиться камера", size=13, color=POS, anchor="start"))
    render(os.path.join(OUT, 'yaw-frames.svg'), W, H, *f,
           title="Один і той самий кут рискання означає різне в різних рамках")


# ── 5. Геометрія наведення на географічну точку ────────────────────────────
def fig_aim_geometry():
    W, H = 1000, 440
    f = []

    # --- панель А: вигляд згори ---
    f.append(text(345, 55, "Вигляд згори", size=15, bold=True, color=MUTED))
    ox, oy = 250, 300
    tx, ty = 415, 165
    f.append(arrow(ox, oy, ox, 108, color=MUTED))
    f.append(text(ox, 96, "Пн", size=13, color=MUTED))
    f.append(arrow(ox, oy, 480, oy, color=MUTED))
    f.append(text(497, 305, "Сх", size=13, color=MUTED))
    f.append(line(ox, ty, tx, ty, color=MUTED, sw=1.2, dash="5,5"))
    f.append(line(tx, ty, tx, oy, color=MUTED, sw=1.2, dash="5,5"))
    f.append(line(ox, oy, tx, ty, color=POS, sw=2.4))
    f.append(circle(ox, oy, 8))
    f.append(circle(tx, ty, 7, fill=POS, stroke=POS))
    f.append(text(445, 152, "ціль", size=12, color=POS, anchor="start"))
    f.append(text(250, 330, "апарат", size=12, color=MUTED))
    f.append(text(332, 150, "north = Δφ · M", size=13, color=MUTED))
    f.append(text(345, 358, "east = Δλ · N · cos φ", size=13, color=MUTED))
    f.append(text(297, 216, "ψ", size=16, bold=True, color=POS))

    # --- панель Б: вигляд збоку ---
    f.append(text(760, 55, "Вигляд збоку", size=15, bold=True, color=MUTED))
    bx, by = 620, 170
    ex, ey = 870, 310
    f.append(line(bx, by, ex, by, color=MUTED, sw=1.2, dash="5,5"))
    f.append(line(ex, by, ex, ey, color=MUTED, sw=1.2, dash="5,5"))
    f.append(line(bx, by, ex, ey, color=POS, sw=2.4))
    f.append(circle(bx, by, 8))
    f.append(circle(ex, ey, 7, fill=POS, stroke=POS))
    f.append(text(620, 143, "апарат", size=12, color=MUTED))
    f.append(text(870, 336, "ціль", size=12, color=POS))
    f.append(text(745, 157, "√(north² + east²)", size=13, color=MUTED))
    f.append(text(884, 245, "Δh", size=13, color=MUTED, anchor="start"))
    f.append(text(700, 198, "θ", size=16, bold=True, color=POS))

    f.append(text(500, 405,
                  "ψ = atan2(east, north) — рискання від півночі   ·   "
                  "θ = atan2(Δh, √(north² + east²)) — тангаж від горизонту",
                  size=13, color=MUTED))
    render(os.path.join(OUT, 'aim-geometry.svg'), W, H, *f,
           title="Два кути на ціль виводяться з тієї самої трійки зміщень")


fig_components()
fig_capture_log()
fig_gimbal_layers()
fig_yaw_frames()
fig_aim_geometry()
print("ok")
