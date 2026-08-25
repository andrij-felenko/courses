# -*- coding: utf-8 -*-
"""Фігури теми «Кабель як антена завад» (com/com-medium/cable-emi).
svgkit імпортуємо зі scripts/ — НЕ переписуємо (AUTHORING §5).

    python figs.py        # генерує всі SVG теми у ./img/
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "..", "scripts"))
from svgkit import (render, text, mtext, rect, line, arrow, circle, textbox,
                    fitbox, INK, MUTED, POS, NEG, FIELD, FILL, LINE, BG, FONT)

IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 1 — Протифазне (DM) та синфазне (CM) випромінювання кабелю
# ════════════════════════════════════════════════════════════════════════════
def fig_cm_dm_radiation():
    W, H = 820, 390
    el = []

    # ── Ліва панель: Протифазний режим (DM) — мале випромінювання петлі ──
    cx1 = 205
    el.append(rect(15, 20, 380, 350, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    el.append(text(cx1, 48, "Протифазний режим (Differential Mode)", size=13, bold=True, color=INK))

    # Джерело і приймач DM
    el.append(rect(35, 95, 55, 120, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    el.append(text(62, 160, "Джерело", size=11, bold=True))
    el.append(rect(320, 95, 55, 120, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    el.append(text(347, 160, "Приймач", size=11, bold=True))

    # Провідники лінії
    el.append(line(90, 120, 320, 120, color=POS, sw=2.5))
    el.append(line(90, 190, 320, 190, color=NEG, sw=2.5))

    # Стрілки струмів
    el.append(arrow(150, 120, 200, 120, color=POS, sw=2.2))
    el.append(arrow(250, 190, 200, 190, color=NEG, sw=2.2))
    el.append(text(205, 110, "I_DM (прямий)", size=11, color=POS, bold=True))
    el.append(text(205, 208, "I_DM (зворотний)", size=11, color=NEG, bold=True))

    # Позначення площі петлі s * L
    el.append(line(120, 125, 120, 185, color=MUTED, sw=1.2, dash="3,3"))
    el.append(text(108, 155, "s", size=12, color=MUTED, bold=True))
    el.append(line(90, 80, 320, 80, color=MUTED, sw=1.2))
    el.append(text(205, 74, "Довжина L (площа петлі A = s · L)", size=11, color=MUTED))

    # Магнітне поле від протилежних струмів скасовується
    el.append(text(205, 240, "Поля B протилежні → взаємне скасування", size=11, color=FIELD, bold=True))
    b1, _, _ = textbox(cx1, 305, "Магнітний диполь: мала площа s · L\nВипромінювання: E_DM ~ f² · A · I_DM\n(для випромінювання потрібні сотні мА)",
                       size=11, fill="#eafaf0", stroke=FIELD, color="#1e7a46")
    el.append(b1)

    # ── Права панель: Синфазний режим (CM) — потужна дипольна антена ──
    cx2 = 615
    el.append(rect(415, 20, 390, 350, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    el.append(text(cx2, 48, "Синфазний режим (Common Mode)", size=13, bold=True, color=INK))

    # Джерело і приймач CM
    el.append(rect(435, 95, 55, 120, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    el.append(text(462, 160, "Блок 1", size=11, bold=True))
    el.append(rect(730, 95, 55, 120, fill="#e2e8f0", stroke=LINE, sw=1.5, rx=4))
    el.append(text(757, 160, "Блок 2", size=11, bold=True))

    # Провідники зі спільним напрямком струму
    el.append(line(490, 120, 730, 120, color=POS, sw=2.5))
    el.append(line(490, 190, 730, 190, color=POS, sw=2.5))

    # Стрілки струмів в один бік
    el.append(arrow(570, 120, 620, 120, color=POS, sw=2.2))
    el.append(arrow(570, 190, 620, 190, color=POS, sw=2.2))
    el.append(text(610, 110, "I_CM / 2", size=11, color=POS, bold=True))
    el.append(text(610, 180, "I_CM / 2", size=11, color=POS, bold=True))

    # Замикання струму через паразитну ємність і землю
    el.append(line(435, 260, 785, 260, color=LINE, sw=2))
    el.append(text(610, 275, "Опорна земля / шасі (струм замикання)", size=11, color=LINE, bold=True))

    # Ємнісні зв'язки C_stray
    el.append(line(550, 190, 550, 220, color=MUTED, sw=1.2, dash="3,3"))
    el.append(line(540, 220, 560, 220, color=MUTED, sw=1.8))
    el.append(line(540, 225, 560, 225, color=MUTED, sw=1.8))
    el.append(line(550, 225, 550, 260, color=MUTED, sw=1.2, dash="3,3"))
    el.append(text(585, 225, "C_паразитна", size=10, color=MUTED))

    el.append(arrow(680, 260, 540, 260, color=POS, sw=2))
    el.append(text(610, 248, "I_CM (через простір)", size=10, color=POS))

    b2, _, _ = textbox(cx2, 318, "Електричний диполь довжиною L\nВипромінювання: E_CM ~ f · L · I_CM\n(всього 5–10 мкА порушують норми FCC/CISPR)",
                       size=11, fill="#fdecea", stroke=POS, color="#a3271b")
    el.append(b2)

    render(out("fig-cm-dm-radiation.svg"), W, H, *el)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 2 — Перетворення мод (DM → CM): асиметрія провідників і земель
# ════════════════════════════════════════════════════════════════════════════
def fig_mode_conversion():
    W, H = 820, 360
    el = []

    el.append(text(410, 30, "Механізми виникнення синфазного струму (перетворення DM → CM)", size=14, bold=True))

    # Блок передавача
    el.append(rect(30, 70, 160, 200, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=6))
    el.append(text(110, 95, "Диференційний", size=12, bold=True))
    el.append(text(110, 112, "драйвер", size=12, bold=True))

    # Виходи драйвера
    el.append(circle(190, 130, 4, fill=POS, stroke=LINE, sw=1))
    el.append(circle(190, 210, 4, fill=NEG, stroke=LINE, sw=1))
    el.append(text(150, 134, "+V_sig / 2", size=10, color=POS, bold=True))
    el.append(text(150, 214, "-V_sig / 2", size=10, color=NEG, bold=True))

    # Провідники лінії з асиметрією довжини ΔL
    el.append(line(190, 130, 600, 130, color=POS, sw=2.2))
    # Нижній провідник має звивину (фазовий зсув Δt)
    el.append(line(190, 210, 350, 210, color=NEG, sw=2.2))
    el.append(line(350, 210, 365, 230, color=NEG, sw=2.2))
    el.append(line(365, 230, 395, 230, color=NEG, sw=2.2))
    el.append(line(395, 230, 410, 210, color=NEG, sw=2.2))
    el.append(line(410, 210, 600, 210, color=NEG, sw=2.2))

    # Позначення фазового перекосу
    el.append(rect(340, 195, 80, 45, fill="none", stroke=POS, sw=1.2, rx=4))
    el.append(text(380, 185, "Асиметрія ΔL (перекіс фаз)", size=10, color=POS, bold=True))

    # Незбалансована ємність на землю
    el.append(line(270, 130, 270, 155, color=MUTED, sw=1.2, dash="3,3"))
    el.append(line(260, 155, 280, 155, color=MUTED, sw=1.6))
    el.append(line(260, 160, 280, 160, color=MUTED, sw=1.6))
    el.append(line(270, 160, 270, 290, color=MUTED, sw=1.2, dash="3,3"))
    el.append(text(295, 160, "C₁", size=11, color=MUTED, bold=True))

    el.append(line(500, 210, 500, 235, color=MUTED, sw=1.2, dash="3,3"))
    el.append(line(490, 235, 510, 235, color=MUTED, sw=1.6))
    el.append(line(490, 240, 510, 240, color=MUTED, sw=1.6))
    el.append(line(500, 240, 500, 290, color=MUTED, sw=1.2, dash="3,3"))
    el.append(text(525, 240, "C₂ ≠ C₁", size=11, color=POS, bold=True))

    # Блок приймача
    el.append(rect(600, 70, 170, 200, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=6))
    el.append(text(685, 95, "Диференційний", size=12, bold=True))
    el.append(text(685, 112, "приймач", size=12, bold=True))

    # Навантаження Z_L1, Z_L2
    el.append(rect(630, 120, 40, 20, fill="#fff", stroke=LINE, sw=1.2))
    el.append(text(650, 134, "Z_L1", size=10))
    el.append(rect(630, 200, 40, 20, fill="#fff", stroke=LINE, sw=1.2))
    el.append(text(650, 214, "Z_L2", size=10))
    el.append(line(670, 130, 710, 130, color=INK, sw=1.5))
    el.append(line(670, 210, 710, 210, color=INK, sw=1.5))
    el.append(line(710, 130, 710, 210, color=INK, sw=1.5))

    # Земляна шина зі скінченним імпедансом (Ground Bounce)
    el.append(line(30, 290, 770, 290, color=LINE, sw=2))
    el.append(text(110, 310, "Земля TX", size=11, bold=True))
    el.append(text(685, 310, "Земля RX", size=11, bold=True))

    # Паразитний імпеданс землі
    el.append(rect(360, 280, 80, 20, fill="#fff", stroke=POS, sw=1.4))
    el.append(text(400, 294, "Z_gnd (L_gnd)", size=10, color=POS, bold=True))
    el.append(text(400, 325, "Зсув потенціалу землі (Ground Bounce) генерує V_CM", size=11, color=POS, bold=True))

    render(out("fig-mode-conversion.svg"), W, H, *el)


# ════════════════════════════════════════════════════════════════════════════
# Фігура 3 — Екранування: 360-градусний контакт проти «поросячого хвостика»
# ════════════════════════════════════════════════════════════════════════════
def fig_shield_pigtail():
    W, H = 820, 370
    el = []

    # ── Ліва панель: Ідеальне заземлення екрана на 360° ──
    cx1 = 205
    el.append(rect(15, 20, 380, 335, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    el.append(text(cx1, 46, "Правильно: 360° круговий контакт (Backshell)", size=12, bold=True, color=FIELD))

    # Металевий корпус
    el.append(rect(40, 75, 45, 175, fill="#cbd5e1", stroke=LINE, sw=1.5))
    el.append(text(62, 160, "Шасі", size=11, bold=True))

    # Екранований кабель (зовнішня оболонка / екран)
    el.append(rect(115, 110, 240, 80, fill="#94a3b8", stroke=LINE, sw=1.5, rx=3))
    el.append(text(235, 126, "Екран кабелю (обплетення)", size=10, bold=True, color="#fff"))

    # Внутрішня сигнальна жила
    el.append(line(85, 150, 355, 150, color=POS, sw=3))
    el.append(text(235, 165, "Сигнальна жила всередині", size=10, bold=True, color="#fff"))

    # Кругове обтискання / муфта
    el.append(rect(85, 95, 30, 110, fill="#64748b", stroke=FIELD, sw=2, rx=2))
    el.append(text(100, 85, "360° муфта", size=10, color=FIELD, bold=True))

    # Струм екрана стікає рівномірно на шасі
    el.append(arrow(200, 102, 125, 102, color=FIELD, sw=2))
    el.append(arrow(125, 102, 85, 102, color=FIELD, sw=2))
    el.append(text(215, 92, "I_екран стікає на шасі", size=10, color=FIELD, bold=True))

    b1, _, _ = textbox(cx1, 290, "Нульова внутрішня апертура\nZ_T мінімальний, паразитні індуктивності відсутні\nВипромінювання та наведення придушені (> 60-80 дБ)",
                       size=10, fill="#eafaf0", stroke=FIELD, color="#1e7a46")
    el.append(b1)

    # ── Права панель: «Поросячий хвостик» (Pigtail) — руйнування екрана ──
    cx2 = 615
    el.append(rect(415, 20, 390, 335, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8))
    el.append(text(cx2, 46, "Помилка: заземлення через «хвостик» (Pigtail)", size=12, bold=True, color=POS))

    # Металевий корпус
    el.append(rect(440, 75, 45, 175, fill="#cbd5e1", stroke=LINE, sw=1.5))
    el.append(text(462, 160, "Шасі", size=11, bold=True))

    # Екранований кабель обрізаний далі від корпусу
    el.append(rect(540, 110, 220, 80, fill="#94a3b8", stroke=LINE, sw=1.5, rx=3))
    el.append(text(650, 126, "Екран кабелю", size=10, bold=True, color="#fff"))

    # Оголена сигнальна жила
    el.append(line(485, 150, 760, 150, color=POS, sw=3))
    el.append(text(510, 140, "Оголена жила", size=10, color=POS, bold=True))

    # Скручений тонкий провідник (хвостик) до клеми
    el.append(line(540, 115, 515, 95, color="#475569", sw=2.5))
    el.append(line(515, 95, 500, 115, color="#475569", sw=2.5))
    el.append(line(500, 115, 485, 100, color="#475569", sw=2.5))
    el.append(line(485, 100, 485, 85, color="#475569", sw=2.5))
    el.append(circle(485, 85, 3, fill=POS, stroke=LINE, sw=1))
    el.append(text(545, 85, "L_pigtail ≈ 10–50 нГн", size=10, color=POS, bold=True))

    # Магнітне поле від хвостика проникає в сигнальну петлю
    el.append(text(515, 175, "Апертура витоку", size=10, color=POS))
    el.append(circle(510, 155, 16, fill="none", stroke=POS, sw=1.2))

    b2, _, _ = textbox(cx2, 290, "Паразитна індуктивність L_pigtail створює напругу V = jω·L·I\nНа частоті 100 МГц опір 25 нГн становить 15.7 Ом!\nЕкран перетворюється на випромінювальну антену",
                       size=10, fill="#fdecea", stroke=POS, color="#a3271b")
    el.append(b2)

    render(out("fig-shield-pigtail.svg"), W, H, *el)


if __name__ == "__main__":
    fig_cm_dm_radiation()
    fig_mode_conversion()
    fig_shield_pigtail()
    print("Фігури успішно згенеровано в img/")
