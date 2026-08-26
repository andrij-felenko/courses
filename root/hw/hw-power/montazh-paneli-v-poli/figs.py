# -*- coding: utf-8 -*-
"""Фігури до теми «Монтаж панелі в полі: кріплення, бруд, град, тварини».
Фігури:
  sun-geometry-tilt.svg       — Геометрія сонця: літній високий промінь vs зимовий низький промінь, крутий кут нахилу панелі для максимізації зимової генерації та сходу снігу.
  soiling-mud-lip.svg         — Забруднення панелі: смуга бруду біля нижньої рамки («mud lip»), що перекриває комірки, та дренажна кліпса для відведення води.
  wind-load-mechanics.svg     — Механічні сили на панель: вітровий тиск (downforce), підйомний відрив (uplift suction) та вигин кремнієвих пластин із мікротріщинами.
  cable-protection-drip-loop.svg — Захист проводки в полі: капельна петля (drip loop), подвійна ізоляція XLPE, захисний металорукав від зубів гризунів і заземлення рами через WEEB-шайбу.

Запуск: python figs.py  → пише SVG у ./img/
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

SUN_YEL = "#f39c12"
SUN_RAY = "#e67e22"
PANEL_BLUE = "#1f4e79"
PANEL_FRAME = "#7f8c8d"
EARTH_BRN = "#795548"
WARN_RED = "#c0392b"
OK_GRN = "#27ae60"


# ── 1. sun-geometry-tilt.svg ──────────────────────────────────────────────────
def fig_sun_geometry():
    W, H = 860, 360
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))

    # Ground line
    p.append(line(40, 300, 820, 300, color=EARTH_BRN, sw=3))
    p.append(text(50, 325, "Поверхня землі / опорна площина", size=13, color=MUTED, anchor="start", bold=True))

    # Vertical post / pole mount
    p.append(rect(390, 170, 20, 130, fill=PANEL_FRAME, stroke=LINE, sw=1.5, rx=2))
    p.append(circle(400, 175, 5, fill="#ffffff", stroke=LINE, sw=2))

    # Solar panel mounted at steep winter tilt (points south, leftwards)
    px1, py1 = 330, 260
    px2, py2 = 470, 90
    p.append(line(px1, py1, px2, py2, color=PANEL_BLUE, sw=12))
    p.append(line(px1, py1, px2, py2, color="#3498db", sw=4))
    p.append(circle(px1, py1, 6, fill=PANEL_FRAME, stroke=LINE, sw=1.5))
    p.append(circle(px2, py2, 6, fill=PANEL_FRAME, stroke=LINE, sw=1.5))

    # Tilt angle arc at ground/bracket
    p.append(line(px1, py1, px1 + 90, py1, color=MUTED, sw=1.5, dash="4,4"))
    p.append('<path d="M %d %d A 45 45 0 0 0 %d %d" fill="none" stroke="%s" stroke-width="2"/>' % (
        px1 + 45, py1, px1 + 22, py1 - 38, WARN_RED
    ))
    p.append(text(px1 + 55, py1 - 42, "β ≈ φ + 15° (55°–65°)", size=12, color=WARN_RED, anchor="start", bold=True))

    # Summer sun ray (high angle)
    p.append(circle(130, 55, 18, fill=SUN_YEL, stroke=SUN_RAY, sw=2))
    p.append(text(130, 61, "☀", size=18, color="#ffffff", bold=True))
    p.append(text(130, 88, "Літнє сонце (h ≈ 62°)", size=12, color=SUN_RAY, bold=True))
    p.append(arrow(160, 68, 350, 150, color=SUN_RAY, sw=2.5))
    p.append(text(275, 95, "Надлишок літньої енергії", size=11, color=MUTED, italic=True))

    # Winter sun ray (low angle)
    p.append(circle(90, 180, 18, fill="#f1c40f", stroke="#d35400", sw=2))
    p.append(text(90, 186, "☀", size=18, color="#ffffff", bold=True))
    p.append(text(90, 212, "Зимове сонце (h ≈ 18°)", size=12, color="#d35400", bold=True))
    p.append(arrow(125, 185, 365, 195, color="#d35400", sw=3))
    p.append(text(235, 172, "Перпендикулярний збір (max узимку)", size=11.5, color=OK_GRN, bold=True))

    # Right side explanation box
    tb, _, _ = textbox(650, 160,
                       "Автономний вузол (Off-Grid):\n"
                       "• Орієнтація суворо на географічний Південь\n"
                       "• Нахил β = широта + 15°..20°\n"
                       "• Мета: не допустити розряду батареї взимку\n"
                       "• Сходження снігу за гравітацією при β > 50°",
                       size=12, pad=12, fill="#f8fafc", stroke="#94a3b8", sw=1.5, bold=False, min_w=270)
    p.append(tb)

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
           '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>\n'
           '%s\n</svg>' % (W, H, W, H, INK, "\n".join(p)))
    with open(os.path.join(OUT, "sun-geometry-tilt.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


# ── 2. soiling-mud-lip.svg ────────────────────────────────────────────────────
def fig_soiling_mud_lip():
    W, H = 840, 360
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))

    # Sub-panel 1: Problem - Mud Lip without clip
    p.append(rect(30, 35, 375, 305, fill="#fffaf9", stroke="#fca5a5", sw=1.5, rx=6))
    p.append(text(217, 60, "Без дренажу: смуга бруду («mud lip»)", size=13.5, color=WARN_RED, bold=True))

    # Cross section of panel inclined: Glass + Aluminum bottom frame border
    p.append(rect(75, 135, 275, 18, fill="#e2e8f0", stroke="#64748b", sw=1.5)) # glass pane
    p.append(rect(50, 115, 25, 58, fill="#94a3b8", stroke="#475569", sw=2))   # aluminum bottom rim
    p.append(text(210, 125, "Скляна поверхня панелі", size=11, color=MUTED))

    # Water puddle & dried mud layer trapped by the protruding rim
    p.append(rect(75, 125, 60, 10, fill="#795548", stroke="#5d4037", sw=1))
    p.append(text(105, 112, "Застійний мул", size=10.5, color=WARN_RED, bold=True))

    # Solar cells underneath
    p.append(rect(80, 139, 38, 10, fill="#1e293b", stroke="#0f172a", sw=1)) # shaded cell
    p.append(rect(125, 139, 38, 10, fill=PANEL_BLUE, stroke="#0f172a", sw=1))
    p.append(rect(170, 139, 38, 10, fill=PANEL_BLUE, stroke="#0f172a", sw=1))
    p.append(rect(215, 139, 38, 10, fill=PANEL_BLUE, stroke="#0f172a", sw=1))

    # Warning text placed without overlapping arrows
    p.append(text(217, 185, "Затінення нижньої комірки під шаром мулу", size=11, color=WARN_RED, bold=True))
    p.append(line(217, 172, 100, 172, color=WARN_RED, sw=1.5))
    p.append(arrow(100, 172, 100, 155, color=WARN_RED, sw=1.8))

    p.append(text(217, 235, "Наслідки накопичення мулу:", size=12, color=INK, bold=True))
    p.append(text(217, 258, "• Локальне перекриття фотоелементів", size=11.5, color=INK))
    p.append(text(217, 278, "• Перегрів (Hot Spot) до 140 °C", size=11.5, color=WARN_RED))
    p.append(text(217, 298, "• Втрата до 30–100% потужності гілки", size=11.5, color=INK))

    # Sub-panel 2: Solution - Water Drain Clip
    p.append(rect(435, 35, 375, 305, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=6))
    p.append(text(622, 60, "З дренажною кліпсою (Water Drain Clip)", size=13.5, color=OK_GRN, bold=True))

    # Cross section with drainage clip attached
    p.append(rect(480, 135, 275, 18, fill="#e2e8f0", stroke="#64748b", sw=1.5)) # glass pane
    p.append(rect(455, 115, 25, 58, fill="#94a3b8", stroke="#475569", sw=2))   # aluminum frame
    p.append(text(615, 125, "Скляна поверхня панелі", size=11, color=MUTED))

    # Plastic siphon clip over the frame
    p.append('<path d="M 450 110 L 485 110 L 485 135 L 480 135 L 480 120 L 450 120 Z" fill="#2563eb" stroke="#1d4ed8" stroke-width="1.5"/>')
    p.append(text(540, 110, "Капілярна кліпса", size=10.5, color="#1d4ed8", anchor="start", bold=True))

    # Flowing water drops draining cleanly
    p.append(circle(442, 145, 3, fill="#38bdf8", stroke="#0284c7", sw=1))
    p.append(circle(440, 165, 4, fill="#38bdf8", stroke="#0284c7", sw=1))
    p.append(text(465, 185, "Вільний стік води з пилом", size=11, color=OK_GRN, anchor="start"))

    # Solar cells all clean
    p.append(rect(485, 139, 38, 10, fill=PANEL_BLUE, stroke="#0f172a", sw=1))
    p.append(rect(530, 139, 38, 10, fill=PANEL_BLUE, stroke="#0f172a", sw=1))
    p.append(rect(575, 139, 38, 10, fill=PANEL_BLUE, stroke="#0f172a", sw=1))
    p.append(rect(620, 139, 38, 10, fill=PANEL_BLUE, stroke="#0f172a", sw=1))

    p.append(text(622, 235, "Переваги активного відведення:", size=12, color=INK, bold=True))
    p.append(text(622, 258, "• Сифонний ефект знімає меніск води", size=11.5, color=INK))
    p.append(text(622, 278, "• Дощ повністю вимиває пил без застою", size=11.5, color=OK_GRN))
    p.append(text(622, 298, "• Відсутність локальних гарячих точок", size=11.5, color=INK))

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
           '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>\n'
           '%s\n</svg>' % (W, H, W, H, INK, "\n".join(p)))
    with open(os.path.join(OUT, "soiling-mud-lip.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


# ── 3. wind-load-mechanics.svg ────────────────────────────────────────────────
def fig_wind_load_mechanics():
    W, H = 840, 360
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))
    p.append(text(420, 35, "Механічні навантаження на модуль за стандартом IEC 61215", size=15, bold=True))

    # Left box: Downforce (Wind + Snow)
    p.append(rect(35, 55, 365, 285, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(217, 80, "Лобовий тиск (Downforce / Snow)", size=13.5, color=PANEL_BLUE, bold=True))

    p.append(rect(90, 200, 30, 20, fill=PANEL_FRAME, stroke=LINE, sw=1.5))
    p.append(rect(315, 200, 30, 20, fill=PANEL_FRAME, stroke=LINE, sw=1.5))
    p.append(text(105, 235, "Опора", size=11, color=MUTED))
    p.append(text(330, 235, "Опора", size=11, color=MUTED))

    p.append('<path d="M 105 200 Q 217 235 330 200" fill="none" stroke="#2563eb" stroke-width="8"/>')
    p.append(text(217, 255, "Вигин скла під тиском", size=11, color="#2563eb", italic=True))

    for x in [140, 180, 220, 260, 300]:
        p.append(arrow(x, 110, x, 175, color=WARN_RED, sw=2.2))
    p.append(text(217, 105, "Сніг + Вітер (до 5400 Па ≈ 550 кг/м²)", size=11.5, color=WARN_RED, bold=True))
    p.append(text(217, 285, "Ризик: мікротріщини в кремнії", size=12, color=WARN_RED, bold=True))
    p.append(text(217, 305, "та розрив струмознімних шин", size=11.5, color=INK))

    # Right box: Wind uplift / Suction
    p.append(rect(440, 55, 365, 285, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=6))
    p.append(text(622, 80, "Вітровий відрив (Uplift Suction)", size=13.5, color=WARN_RED, bold=True))

    p.append(rect(495, 200, 30, 20, fill=PANEL_FRAME, stroke=LINE, sw=1.5))
    p.append(rect(720, 200, 30, 20, fill=PANEL_FRAME, stroke=LINE, sw=1.5))
    p.append(text(510, 235, "Опора", size=11, color=MUTED))
    p.append(text(735, 235, "Опора", size=11, color=MUTED))

    p.append('<path d="M 490 200 Q 622 165 745 200" fill="none" stroke="#dc2626" stroke-width="8"/>')
    p.append(text(622, 150, "Вигин у зворотному напрямку", size=11, color="#dc2626", italic=True))

    for x in [545, 585, 625, 665, 705]:
        p.append(arrow(x, 260, x, 215, color="#dc2626", sw=2.2))
    p.append(text(622, 280, "Вітрове розрідження (до 2400 Па ≈ 245 кг/м²)", size=11.5, color="#dc2626", bold=True))
    p.append(text(622, 305, "Ризик: виривання притискачів,", size=12, color=WARN_RED, bold=True))
    p.append(text(622, 323, "аеродинамічний флатер і зрив панелі", size=11.5, color=INK))

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
           '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>\n'
           '%s\n</svg>' % (W, H, W, H, INK, "\n".join(p)))
    with open(os.path.join(OUT, "wind-load-mechanics.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


# ── 4. cable-protection-drip-loop.svg ─────────────────────────────────────────
def fig_cable_protection():
    W, H = 840, 360
    p = []
    p.append(rect(10, 10, W - 20, H - 20, fill="#ffffff", stroke="#d1d5db", sw=1.5, rx=8))

    # Junction box on back of panel
    p.append(rect(45, 60, 120, 75, fill="#334155", stroke="#1e293b", sw=2, rx=4))
    p.append(text(105, 90, "Розподільна", size=12, color="#ffffff", bold=True))
    p.append(text(105, 110, "коробка (J-Box)", size=11, color="#cbd5e1"))

    # Cable gland
    p.append(rect(165, 85, 25, 22, fill="#64748b", stroke="#334155", sw=1.5))
    p.append(text(205, 75, "Гермоввід IP68", size=10, color=MUTED, anchor="start", bold=True))

    # Drip loop path
    p.append('<path d="M 190 96 C 255 96, 235 250, 275 250 C 315 250, 325 160, 385 160" fill="none" stroke="#0f172a" stroke-width="8"/>')
    p.append('<path d="M 190 96 C 255 96, 235 250, 275 250 C 315 250, 325 160, 385 160" fill="none" stroke="#e2e8f0" stroke-width="2" stroke-dasharray="4,4"/>')

    # Water drops dripping off lowest point of the loop
    p.append(circle(275, 268, 3, fill="#38bdf8", stroke="#0284c7", sw=1))
    p.append(circle(275, 285, 4, fill="#38bdf8", stroke="#0284c7", sw=1))
    p.append(text(275, 315, "Капельна петля (Drip Loop):", size=12, color="#0284c7", bold=True))
    p.append(text(275, 335, "вода капає донизу, а не затікає у ввід", size=11, color=INK))

    # Metallic flexible conduit
    p.append(rect(385, 145, 130, 30, fill="#94a3b8", stroke="#475569", sw=2, rx=4))
    for cx in range(395, 510, 12):
        p.append(line(cx, 145, cx, 175, color="#475569", sw=1.5))
    p.append(text(450, 130, "Металорукав (AISI 304)", size=11, color=PANEL_BLUE, bold=True))
    p.append(text(450, 195, "Захист від зубів гризунів", size=11, color=WARN_RED, bold=True))
    p.append(text(450, 215, "Нержавіюча стяжка (не білий пластик!)", size=10, color=MUTED))

    # Enclosure / Controller on right
    p.append(rect(560, 75, 245, 230, fill="#f1f5f9", stroke="#475569", sw=2, rx=6))
    p.append(text(682, 105, "Гермобокс контролера / АКБ", size=13, color=PANEL_BLUE, bold=True))

    # Inside enclosure features
    p.append(rect(585, 130, 195, 60, fill="#ffffff", stroke="#cbd5e1", sw=1.5, rx=4))
    p.append(text(682, 155, "MPPT / Захист від імпульсів", size=11.5, color=INK, bold=True))
    p.append(text(682, 175, "TVS-діоди + плавний запобіжник", size=10.5, color=MUTED))

    # Grounding lug with WEEB washer
    p.append(circle(600, 235, 9, fill="#f59e0b", stroke="#b45309", sw=2))
    p.append(line(600, 244, 600, 275, color=OK_GRN, sw=3))
    p.append(line(585, 275, 615, 275, color=OK_GRN, sw=3))
    p.append(line(590, 280, 610, 280, color=OK_GRN, sw=2.5))
    p.append(line(595, 285, 605, 285, color=OK_GRN, sw=2))
    p.append(text(690, 245, "Захисне заземлення рами (WEEB)", size=11, color=OK_GRN, bold=True))
    p.append(text(690, 265, "Проколювання оксидного шару Al", size=10, color=MUTED))

    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n'
           '<defs><marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
           '<path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="%s"/></marker></defs>\n'
           '%s\n</svg>' % (W, H, W, H, INK, "\n".join(p)))
    with open(os.path.join(OUT, "cable-protection-drip-loop.svg"), "w", encoding="utf-8") as f:
        f.write(svg)


if __name__ == "__main__":
    fig_sun_geometry()
    fig_soiling_mud_lip()
    fig_wind_load_mechanics()
    fig_cable_protection()
    print("All figures generated successfully in", OUT)
