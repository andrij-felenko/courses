# -*- coding: utf-8 -*-
"""Фігури для теми mekhanichnyi-konvert (механічний конверт друкованої плати).
svgkit імпортуємо зі scripts/, НЕ переписуємо (AUTHORING §5)."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# Кольори
BOARD_FILL   = "#e2e8f0"   # основа плати
BOARD_STROKE = "#475569"   # контур плати
COPPER_PAD   = "#f59e0b"   # мідні площадки
COPPER_FILL  = "#fef3c7"   # світла мідь
KEEPOUT_FILL = "#fee2e2"   # зона заборони (червонувата)
KEEPOUT_LINE = "#ef4444"   # контур заборони
CONN_BODY    = "#93c5fd"   # корпус роз'єму
CONN_STROKE  = "#2563eb"
SCREW_FILL   = "#cbd5e1"   # метал гвинта
SCREW_STROKE = "#334155"


# ── 1. Креслення механічного конверта з допусками ─────────────────────────────
def fig_envelope_dimensions():
    W, H = 840, 520
    frags = []

    # Фонова панель
    frags.append(rect(10, 10, 820, 500, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))

    # Контур корпусу (пунктир)
    frags.append(rect(40, 50, 760, 420, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=12))
    frags.append(text(420, 72, "Внутрішній габарит корпусу (Enclosure Inner Envelope): 140.0 × 90.0 мм", size=13, color=MUTED, bold=True))

    # Контур друкованої плати (PCB Outline)
    # Розміри плати: X=110..670 (560px -> 120.0 мм), Y=110..430 (320px -> 70.0 мм)
    px, py, pw, ph = 110, 110, 560, 320
    frags.append(rect(px, py, pw, ph, fill=BOARD_FILL, stroke=BOARD_STROKE, sw=2.0, rx=10))

    # Внутрішній виріз (внутрішній паз фрезерування)
    frags.append(rect(px + 400, py, 70, 50, fill="#ffffff", stroke=BOARD_STROKE, sw=1.8, rx=8))
    frags.append(text(px + 435, py + 26, "Паз", size=11, color=BOARD_STROKE, bold=True))
    frags.append(text(px + 435, py + 42, "R ≥ 1.0 мм", size=9, color=POS, bold=True))

    # Зони заборони по периметру (Edge keepout)
    frags.append(rect(px + 4, py + 4, pw - 8, ph - 8, fill="none", stroke=KEEPOUT_LINE, sw=1.2, rx=8))

    # Кріпильні отвори (4 кутові отвори)
    holes = [
        (px + 30, py + 30, "H1"),
        (px + pw - 30, py + 30, "H2"),
        (px + 30, py + ph - 30, "H3"),
        (px + pw - 30, py + ph - 30, "H4")
    ]
    for hx, hy, name in holes:
        # Зона заборони компонентів навколо отвору (Keepout circle)
        frags.append(circle(hx, hy, 22, fill=KEEPOUT_FILL, stroke=KEEPOUT_LINE, sw=1.2))
        # Мідний майданчик (Annular ring)
        frags.append(circle(hx, hy, 14, fill=COPPER_FILL, stroke=COPPER_PAD, sw=1.5))
        # Сам отвір
        frags.append(circle(hx, hy, 7, fill="#ffffff", stroke=LINE, sw=1.5))

    # Роз'єм 1: USB-C з вильотом за плату (Overhang)
    # Розділяємо на дві частини по x=px, щоб уникнути конфлікту суцільних блоків:
    # 1) Частина на платі (вкладена в контур плати)
    frags.append(rect(px, py + 80, 30, 36, fill=CONN_BODY, stroke=CONN_STROKE, sw=1.8, rx=0))
    # 2) Виступ за межі плати (зовнішня частина)
    frags.append(rect(px - 18, py + 80, 18, 36, fill=CONN_BODY, stroke=CONN_STROKE, sw=1.8, rx=4))
    frags.append(text(px + 12, py + 102, "USB-C", size=10, color=CONN_STROKE, bold=True))
    # Стрілка вильоту (Overhang)
    frags.append(line(px - 18, py + 72, px, py + 72, color=POS, sw=1.5))
    frags.append(line(px - 18, py + 68, px - 18, py + 76, color=POS, sw=1.2))
    frags.append(line(px, py + 68, px, py + 76, color=POS, sw=1.2))
    frags.append(text(px - 9, py + 62, "1.4 ± 0.2", size=9, color=POS, bold=True))

    # Роз'єм 2: RJ45 на лівому боці
    frags.append(rect(px, py + 160, 40, 48, fill="#fed7aa", stroke="#ea580c", sw=1.8, rx=0))
    frags.append(rect(px - 12, py + 160, 12, 48, fill="#fed7aa", stroke="#ea580c", sw=1.8, rx=3))
    frags.append(text(px + 18, py + 188, "RJ45", size=11, color="#9a3412", bold=True))

    # Роз'єм 3: Клемник живлення (Terminal block) на правому боці
    frags.append(rect(px + pw - 24, py + 140, 24, 60, fill="#bbf7d0", stroke="#16a34a", sw=1.8, rx=0))
    frags.append(rect(px + pw, py + 140, 12, 60, fill="#bbf7d0", stroke="#16a34a", sw=1.8, rx=3))
    frags.append(text(px + pw - 10, py + 174, "Power", size=10, color="#15803d", bold=True))

    # Роз'єм 4: SMA RF Connector на правому боці з вильотом
    frags.append(rect(px + pw - 14, py + 240, 14, 28, fill="#e9d5ff", stroke="#9333ea", sw=1.8, rx=0))
    frags.append(rect(px + pw, py + 240, 18, 28, fill="#e9d5ff", stroke="#9333ea", sw=1.8, rx=2))
    frags.append(text(px + pw + 8, py + 258, "SMA", size=10, color="#7e22ce", bold=True))

    # Розмірні лінії плати
    dim_y = py - 30
    frags.append(line(px, dim_y, px + pw, dim_y, color=LINE, sw=1.5))
    frags.append(line(px, dim_y - 6, px, py + 10, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(line(px + pw, dim_y - 6, px + pw, py + 10, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(circle(px, dim_y, 2.5, fill=LINE, stroke=LINE))
    frags.append(circle(px + pw, dim_y, 2.5, fill=LINE, stroke=LINE))
    frags.append(text(px + pw/2, dim_y - 8, "Довжина плати: 120.0 ± 0.15 мм", size=12, color=INK, bold=True))

    # Відстань між отворами по горизонталі
    dim_h_y = py + ph + 30
    frags.append(line(px + 30, dim_h_y, px + pw - 30, dim_h_y, color=LINE, sw=1.5))
    frags.append(line(px + 30, py + ph - 10, px + 30, dim_h_y + 6, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(line(px + pw - 30, py + ph - 10, px + pw - 30, dim_h_y + 6, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(circle(px + 30, dim_h_y, 2.5, fill=LINE, stroke=LINE))
    frags.append(circle(px + pw - 30, dim_h_y, 2.5, fill=LINE, stroke=LINE))
    frags.append(text(px + pw/2, dim_h_y + 18, "Міжцентрова відстань кріплень: 110.0 ± 0.10 мм", size=11, color=INK, bold=True))

    # Вертикальний габарит праворуч: 70.0 ± 0.15 мм
    dim_x = px + pw + 55
    frags.append(line(dim_x, py, dim_x, py + ph, color=LINE, sw=1.5))
    frags.append(line(px + pw - 10, py, dim_x + 6, py, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(line(px + pw - 10, py + ph, dim_x + 6, py + ph, color=MUTED, sw=1.0, dash="3,3"))
    frags.append(circle(dim_x, py, 2.5, fill=LINE, stroke=LINE))
    frags.append(circle(dim_x, py + ph, 2.5, fill=LINE, stroke=LINE))
    frags.append(text(dim_x + 8, py + ph/2, "70.0 ± 0.15 мм", size=11, color=INK, anchor="start", bold=True))

    # Легенда внизу
    leg_y = H - 35
    frags.append(rect(110, leg_y - 12, 16, 16, fill=KEEPOUT_FILL, stroke=KEEPOUT_LINE, sw=1.2))
    frags.append(text(134, leg_y + 1, "Зона заборони деталей / трасування", size=10, color=INK, anchor="start"))

    frags.append(rect(360, leg_y - 12, 16, 16, fill=COPPER_FILL, stroke=COPPER_PAD, sw=1.2))
    frags.append(text(384, leg_y + 1, "Мідний майданчик заземлення", size=10, color=INK, anchor="start"))

    frags.append(circle(600, leg_y - 4, 7, fill="#ffffff", stroke=LINE, sw=1.5))
    frags.append(text(616, leg_y + 1, "Кріпильний отвір Ø3.2 мм (M3)", size=10, color=INK, anchor="start"))

    render(os.path.join(OUT, "envelope-dimensions.svg"), W, H, *frags)


# ── 2. Переріз кріпильного отвору та зони безпеки ──────────────────────────────
def fig_mounting_hole_cross_section():
    W, H = 840, 480
    frags = []

    # Фонова панель
    frags.append(rect(10, 10, 820, 460, fill="#ffffff", stroke="#cbd5e1", sw=1.0, rx=8))

    # Ліва половина: Вигляд згори (Top View)
    cx1, cy1 = 220, 230
    frags.append(text(cx1, 45, "Вигляд згори: радіальні зони безпеки", size=14, color=INK, bold=True))

    # Зона заборони компонентів SMD (Component Keepout, Ø11.0 мм -> R=95px)
    frags.append(circle(cx1, cy1, 95, fill="#fee2e2", stroke="#f87171", sw=1.5))
    frags.append(text(cx1, cy1 - 78, "Зона заборони компонентів (SMD Keepout)", size=9, color=POS, bold=True))

    # Зона проходу інструменту (Tool Clearance, Ø9.0 мм -> R=70px)
    frags.append(circle(cx1, cy1, 70, fill="#fffbeb", stroke="#f59e0b", sw=1.2))
    frags.append(text(cx1, cy1 - 54, "Зона головки гвинта й ключа (Ø8.0 мм)", size=9, color="#b45309", bold=True))

    # Мідна контактна площадка (Annular Ring / Pad, Ø6.5 мм -> R=48px)
    frags.append(circle(cx1, cy1, 48, fill="#fef08a", stroke="#ca8a04", sw=1.5))

    # Масив переходів заземлення шасі (Chassis ground via stitch)
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(angle)
        vx = cx1 + 36 * math.cos(rad)
        vy = cy1 + 36 * math.sin(rad)
        frags.append(circle(vx, vy, 4, fill="#ca8a04", stroke="#854d0e", sw=1.0))

    # Слід від шайби (Washer Contact Circle, Ø6.0 мм -> R=32px)
    frags.append(circle(cx1, cy1, 32, fill="none", stroke="#0284c7", sw=1.8))
    frags.append(text(cx1, cy1 + 22, "Контакт шайби", size=9, color="#0369a1", bold=True))

    # Металізований отвір (Plated Drill Hole, Ø3.2 мм -> R=18px)
    frags.append(circle(cx1, cy1, 18, fill="#ffffff", stroke="#0f172a", sw=2.0))
    frags.append(text(cx1, cy1 + 4, "Ø3.2", size=10, color="#0f172a", bold=True))

    # Розділювальна вертикальна лінія
    frags.append(line(430, 40, 430, 440, color="#e2e8f0", sw=1.5, dash="4,4"))

    # Права половина: Поперечний переріз у зборі (Cross Section Assembly)
    cx2, cy2 = 635, 230
    frags.append(text(cx2, 45, "Переріз вузла кріплення на стійці", size=14, color=INK, bold=True))

    # Шасі корпусу внизу
    frags.append(rect(cx2 - 140, 340, 280, 30, fill="#94a3b8", stroke="#475569", sw=1.5, rx=2))
    frags.append(text(cx2, 360, "Металеве шасі / корпус приладу", size=11, color="#1e293b", bold=True))

    # Металева різьбова стійка (Hex Standoff)
    frags.append(rect(cx2 - 50, 195, 100, 145, fill="#cbd5e1", stroke="#475569", sw=1.8, rx=2))
    frags.append(text(cx2 + 75, 260, "Латунна стійка", size=11, color="#1e293b", anchor="start", bold=True))
    frags.append(text(cx2 + 75, 276, "(Standoff H=8 мм)", size=9, color=MUTED, anchor="start"))

    # Плата PCB (FR-4 з мідними шарами)
    frags.append(rect(cx2 - 160, 145, 320, 50, fill=BOARD_FILL, stroke=BOARD_STROKE, sw=1.8, rx=2))
    frags.append(text(cx2 - 110, 173, "PCB (1.6 мм)", size=10, color=BOARD_STROKE, bold=True))

    # Мідні контактні площадки на платі (верх і низ, розбиті ліворуч і праворуч від отвору)
    frags.append(rect(cx2 - 50, 145, 28, 4, fill=COPPER_PAD, stroke="#b45309", sw=0.8, rx=0))
    frags.append(rect(cx2 + 22, 145, 28, 4, fill=COPPER_PAD, stroke="#b45309", sw=0.8, rx=0))
    frags.append(rect(cx2 - 50, 191, 28, 4, fill=COPPER_PAD, stroke="#b45309", sw=0.8, rx=0))
    frags.append(rect(cx2 + 22, 191, 28, 4, fill=COPPER_PAD, stroke="#b45309", sw=0.8, rx=0))

    # Металізована гільза отвору в платі
    frags.append(rect(cx2 - 22, 145, 44, 50, fill="#ffffff", stroke="#0f172a", sw=1.5, rx=0))

    # Шайба Гровера / пласка шайба
    frags.append(rect(cx2 - 45, 135, 90, 10, fill="#94a3b8", stroke="#334155", sw=1.5, rx=1))
    frags.append(text(cx2 + 75, 142, "Шайба Ø6 мм", size=9, color="#334155", anchor="start"))

    # Голівка гвинта M3 (з пазом під викрутку)
    frags.append(rect(cx2 - 40, 95, 80, 40, fill=SCREW_FILL, stroke=SCREW_STROKE, sw=1.8, rx=3))
    frags.append(line(cx2 - 15, 95, cx2 - 15, 110, color=SCREW_STROKE, sw=1.5))
    frags.append(line(cx2 + 15, 95, cx2 + 15, 110, color=SCREW_STROKE, sw=1.5))
    frags.append(text(cx2, 120, "Гвинт M3 (DIN 7985)", size=10, color=SCREW_STROKE, bold=True))

    # Стрижень гвинта: розбито на дві частини, щоб не було часткового перекриття з різними батьківськими блоками
    frags.append(rect(cx2 - 18, 145, 36, 50, fill="#e2e8f0", stroke="#64748b", sw=1.2, rx=0))
    frags.append(rect(cx2 - 18, 195, 36, 110, fill="#e2e8f0", stroke="#64748b", sw=1.2, rx=0))

    # Механічне напруження в текстоліті (конус стиску під голівкою)
    frags.append(line(cx2 - 45, 145, cx2 - 50, 195, color=POS, sw=1.8, dash="3,2"))
    frags.append(line(cx2 + 45, 145, cx2 + 50, 195, color=POS, sw=1.8, dash="3,2"))

    # Текст про механічне напруження
    frags.append(text(cx2, 420, "Конус стиску: виникає вигин текстоліту та зріз пайки SMD-деталей", size=10, color=POS, bold=True))
    frags.append(text(cx2, 436, "Мінімальний радіус до керамічних конденсаторів (MLCC): R ≥ 4.5 мм", size=9, color=MUTED))

    render(os.path.join(OUT, "mounting-hole-cross-section.svg"), W, H, *frags)


if __name__ == "__main__":
    fig_envelope_dimensions()
    fig_mounting_hole_cross_section()
    print("OK: generated 2 figures in img/")
