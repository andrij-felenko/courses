# -*- coding: utf-8 -*-
"""figs.py — ілюстрації до теми «Магнітне коло».
Генерує SVG-фігури у підтеку ./img/ за допомогою svgkit.
"""
import sys, os, math

# Додаємо scripts/ до шляху пошуку модулів (4 рівні вгору від book/electronics/components/magnetic-circuit/)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)


def rect_dash(x, y, w, h, fill="none", stroke=LINE, sw=1.5, rx=6, dash="4,3"):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" '
            'fill="%s" stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>' %
            (x, y, w, h, rx, fill, stroke, sw, dash))


# ── 1. Порівняння електричного та магнітного кіл ──────────────────────────────
def fig_analogy():
    W, H = 840, 430
    p = []
    p.append(text(W / 2, 26, "Аналогія та межі порівняння електричного й магнітного кіл", size=16, bold=True))
    p.append(text(W / 2, 46, "Закон Ома проти закону Гопкінсона, фізичні відмінності та розсіювання полів", size=12, color=MUTED, italic=True))

    # Ліва колонка: Електричне коло
    p.append(rect(30, 65, 375, 345, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(rect(45, 78, 345, 32, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=6))
    p.append(text(217, 99, "Електричне коло (Закон Ома)", size=13.5, bold=True, color=INK))

    # Схема електричного кола
    p.append(rect(65, 122, 100, 48, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(115, 144, "Джерело ЕРС", size=10.5, bold=True, color=NEG))
    p.append(text(115, 159, "E [Вольти, В]", size=10, color=MUTED))

    p.append(line(165, 146, 215, 146, color=NEG, sw=2))
    p.append(arrow(185, 146, 205, 146, color=NEG, sw=2))
    p.append(text(195, 138, "I", size=11, bold=True, color=NEG))

    p.append(rect(215, 122, 160, 48, fill="#eff6ff", stroke=NEG, sw=1.5, rx=4))
    p.append(text(295, 144, "Опір R = l / (σ · A)", size=10.5, bold=True, color=NEG))
    p.append(text(295, 159, "Оми [Ом], провідність G = σ·A/l", size=9.5, color=MUTED))

    p.append(line(295, 170, 295, 185, color=NEG, sw=1.5))
    p.append(line(295, 185, 115, 185, color=NEG, sw=1.5))
    p.append(line(115, 185, 115, 170, color=NEG, sw=1.5))

    # Параметри електричного кола
    el_rows = [
        ("Рушійна сила:", "ЕРС: E [В] (інтеграл поля E · dl)"),
        ("Потік носіїв:", "Струм: I [А] (рух реальних зарядів)"),
        ("Густина потоку:", "Густина струму: J = σ · E [А/м²]"),
        ("Опір проходженню:", "Опір: R = l / (σ · A) [Ом]"),
        ("Енергетика:", "Дисипація: P = I² · R [Вт, тепло]"),
        ("Ізоляція середовища:", "σ_мідь / σ_повітря ≈ 10²⁴ (витік відсутній)"),
    ]
    y_el = 214
    for label, val in el_rows:
        p.append(text(48, y_el, label, size=11, bold=True, anchor="start", color=INK))
        p.append(text(175, y_el, val, size=10.5, anchor="start", color="#1e293b"))
        y_el += 31

    # Права колонка: Магнітне коло
    p.append(rect(435, 65, 375, 345, fill="#f0fdf4", stroke="#bbf7d0", sw=1.2, rx=8))
    p.append(rect(450, 78, 345, 32, fill="#dcfce7", stroke="#86efac", sw=1, rx=6))
    p.append(text(622, 99, "Магнітне коло (Закон Гопкінсона)", size=13.5, bold=True, color="#14532d"))

    # Схема магнітного кола
    p.append(rect(470, 122, 100, 48, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(520, 144, "Джерело МРС", size=10.5, bold=True, color=FIELD))
    p.append(text(520, 159, "F = N · I [А-вит]", size=10, color=MUTED))

    p.append(line(570, 146, 620, 146, color=FIELD, sw=2))
    p.append(arrow(590, 146, 610, 146, color=FIELD, sw=2))
    p.append(text(600, 138, "Φ", size=11, bold=True, color=FIELD))

    p.append(rect(620, 122, 160, 48, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(700, 144, "Релюктанс Rm = l / (μ · A)", size=10.5, bold=True, color=FIELD))
    p.append(text(700, 159, "1/Гн, пермеанс Pm = μ·A/l", size=9.5, color=MUTED))

    p.append(line(700, 170, 700, 185, color=FIELD, sw=1.5))
    p.append(line(700, 185, 520, 185, color=FIELD, sw=1.5))
    p.append(line(520, 185, 520, 170, color=FIELD, sw=1.5))

    # Параметри магнітного кола
    mag_rows = [
        ("Рушійна сила:", "МРС: F = N · I [А-витки] (ампер-витки)"),
        ("Потік поля:", "Магнітний потік: Φ [Вб] (стан простору)"),
        ("Густина потоку:", "Індукція: B = μ · H [Тл] (Вб/м²)"),
        ("Опір проходженню:", "Релюктанс: Rm = l / (μ · A) [1/Гн]"),
        ("Енергетика:", "Накопичення: W = 0.5 · Φ · F [Дж, поле]"),
        ("Ізоляція середовища:", "μ_ферит / μ_повітря ≈ 10³..10⁴ (є випучування)"),
    ]
    y_mag = 214
    for label, val in mag_rows:
        p.append(text(453, y_mag, label, size=11, bold=True, anchor="start", color=INK))
        p.append(text(580, y_mag, val, size=10.5, anchor="start", color="#064e3b"))
        y_mag += 31

    render(os.path.join(IMG, "magnetic-circuit-analogy.svg"), W, H, *p)


# ── 2. Осердя з повітряним зазором та розподіл енергії ────────────────────────
def fig_core_gap():
    W, H = 840, 410
    p = []
    p.append(text(W / 2, 26, "Магнітне коло з немагнітним зазором та концентрація енергії", size=16, bold=True))
    p.append(text(W / 2, 46, "Падіння МРС на ділянках кола та локалізація енергії магнітного поля", size=12, color=MUTED, italic=True))

    # Ліва частина: рисунок осердя з зазором
    p.append(rect(30, 65, 380, 325, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(220, 88, "Фізична геометрія осердя", size=13, bold=True, color=INK))

    # Феритове C-осердя
    # Зовнішній контур
    p.append('<path d="M 90 120 L 320 120 L 320 190 L 270 190 L 270 160 L 140 160 L 140 310 L 270 310 L 270 230 L 320 230 L 320 350 L 90 350 Z" '
             'fill="#94a3b8" stroke="#475569" stroke-width="2"/>')

    # Повітряний зазор
    p.append(rect(270, 190, 50, 40, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=2))
    p.append(text(295, 214, "Зазор lg", size=10.5, bold=True, color="#854d0e"))

    # Обмотка на лівому керні
    for wy in range(180, 290, 18):
        p.append(rect(72, wy, 16, 12, fill="#f97316", stroke="#c2410c", sw=1.2, rx=2))
        p.append(rect(142, wy, 16, 12, fill="#ea580c", stroke="#9a3412", sw=1.2, rx=2))
    p.append(text(60, 240, "N витків", size=11, bold=True, color="#c2410c", anchor="end"))
    p.append(text(60, 255, "Струм I", size=10, color=MUTED, anchor="end"))

    # Пунктирна середня магнітна лінія потоку
    p.append('<path d="M 115 140 L 295 140 L 295 190 M 295 230 L 295 330 L 115 330 Z" '
             'fill="none" stroke=FIELD stroke-width="2" stroke-dasharray="5,4"/>')
    p.append(text(205, 134, "Потік Φ", size=11, bold=True, color=FIELD))

    p.append(text(205, 372, "Феромагнітне осердя (довжина le, μr ≈ 2000)", size=10.5, color="#334155"))

    # Права частина: Еквівалентна схема та енергетичний баланс
    p.append(rect(430, 65, 380, 325, fill="#faf5ff", stroke="#e9d5ff", sw=1.2, rx=8))
    p.append(text(620, 88, "Еквівалентна схема та енергія", size=13, bold=True, color="#581c87"))

    # Еквівалентне коло
    # Джерело F
    p.append(rect(460, 115, 90, 42, fill="#f3e8ff", stroke="#7e22ce", sw=1.5, rx=4))
    p.append(text(505, 133, "МРС F", size=11, bold=True, color="#6b21a8"))
    p.append(text(505, 147, "N · I", size=10, color=MUTED))

    p.append(line(550, 136, 580, 136, color="#7e22ce", sw=1.8))
    p.append(arrow(555, 136, 575, 136, color="#7e22ce", sw=1.8))

    # Опір фериту
    p.append(rect(580, 115, 95, 42, fill="#e2e8f0", stroke="#475569", sw=1.5, rx=4))
    p.append(text(627, 133, "R_core", size=11, bold=True, color="#1e293b"))
    p.append(text(627, 147, "~9% опору", size=9.5, color=MUTED))

    p.append(line(675, 136, 700, 136, color="#7e22ce", sw=1.8))

    # Опір зазору
    p.append(rect(700, 115, 95, 42, fill="#fef08a", stroke="#ca8a04", sw=1.5, rx=4))
    p.append(text(747, 133, "R_gap", size=11, bold=True, color="#854d0e"))
    p.append(text(747, 147, "~91% опору", size=9.5, color=MUTED))

    # Зворотний провід кола
    p.append(line(747, 157, 747, 175, color="#7e22ce", sw=1.5))
    p.append(line(747, 175, 505, 175, color="#7e22ce", sw=1.5))
    p.append(line(505, 175, 505, 157, color="#7e22ce", sw=1.5))

    # Порівняльна діаграма накопиченої енергії
    p.append(text(450, 205, "Розподіл магнітної енергії W = 0.5 · B² / μ · V:", size=11, bold=True, anchor="start", color=INK))

    # Стовпчик густини енергії
    p.append(rect(450, 220, 340, 26, fill="#e2e8f0", stroke="#94a3b8", sw=1, rx=4))
    p.append(rect(450, 220, 310, 26, fill="#fef08a", stroke="#ca8a04", sw=1, rx=4))
    p.append(text(600, 237, "Енергія в зазорі: W_gap ≈ 91% (w_gap = B² / 2μ0)", size=10, bold=True, color="#854d0e"))

    # Пояснювальні пункти
    notes = [
        ("•", "R_gap = lg / (μ0 · Ae) домінує над R_core = le / (μ0·μr·Ae)"),
        ("•", "Густина енергії w_gap у μr (2000×) разів вища за w_core"),
        ("•", "Зазор захищає осердя від насичення (I_sat зростає в рази)"),
        ("•", "Індуктивність L = N² / (R_core + R_gap) стабілізується"),
    ]
    ny = 275
    for bullet, ntxt in notes:
        p.append(text(452, ny, bullet, size=12, bold=True, anchor="start", color="#6b21a8"))
        p.append(text(468, ny, ntxt, size=10.5, anchor="start", color="#334155"))
        ny += 26

    render(os.path.join(IMG, "magnetic-circuit-gap.svg"), W, H, *p)


# ── 3. Випучування магнітного потоку (Fringing Flux) ──────────────────────────
def fig_fringing():
    W, H = 840, 400
    p = []
    p.append(text(W / 2, 26, "Ефект випучування магнітного потоку (Fringing Flux)", size=16, bold=True))
    p.append(text(W / 2, 46, "Збільшення ефективної площі Aeff та вихровий нагрів сусідніх витків міді", size=12, color=MUTED, italic=True))

    # Ліва зона: геометрія зазору та лінії поля
    p.append(rect(30, 65, 430, 315, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(245, 88, "Спотворення поля на краях зазору", size=13, bold=True, color=INK))

    # Верхній полюс осердя
    p.append(rect(140, 110, 160, 60, fill="#94a3b8", stroke="#475569", sw=1.5, rx=3))
    p.append(text(220, 145, "Верхній керн осердя", size=11, bold=True, color="#f8fafc"))

    # Нижній полюс осердя
    p.append(rect(140, 240, 160, 60, fill="#94a3b8", stroke="#475569", sw=1.5, rx=3))
    p.append(text(220, 275, "Нижній керн осердя", size=11, bold=True, color="#f8fafc"))

    # Зазор між ними: висота 70px (lg)
    p.append(line(130, 170, 130, 240, color="#b45309", sw=1.2))
    p.append(line(125, 170, 135, 170, color="#b45309", sw=1.2))
    p.append(line(125, 240, 135, 240, color="#b45309", sw=1.2))
    p.append(text(120, 210, "lg", size=11, bold=True, color="#b45309", anchor="end"))

    # Прямі лінії потоку всередині
    for lx in (170, 195, 220, 245, 270):
        p.append(line(lx, 170, lx, 240, color=FIELD, sw=1.8))
        p.append(arrow(lx, 195, lx, 215, color=FIELD, sw=1.8))

    # Випучені дугові лінії зліва та справа
    # Лівий бік
    p.append('<path d="M 148 170 Q 100 205 148 240" fill="none" stroke="#16a34a" stroke-width="1.8"/>')
    p.append('<path d="M 155 170 Q 70 205 155 240" fill="none" stroke="#16a34a" stroke-width="1.5" stroke-dasharray="4,3"/>')

    # Правий бік
    p.append('<path d="M 292 170 Q 340 205 292 240" fill="none" stroke="#16a34a" stroke-width="1.8"/>')
    p.append('<path d="M 285 170 Q 370 205 285 240" fill="none" stroke="#16a34a" stroke-width="1.5" stroke-dasharray="4,3"/>')

    # Витки обмотки біля зазору (гаряча точка!)
    p.append(rect(345, 185, 20, 40, fill="#fee2e2", stroke=POS, sw=1.5, rx=3))
    p.append(circle(355, 205, 6, fill=POS, stroke="#991b1b", sw=1))
    p.append(text(372, 202, "Мідний виток", size=10, bold=True, color=POS, anchor="start"))
    p.append(text(372, 217, "Вихровий перегрів!", size=9.5, bold=True, color="#991b1b", anchor="start"))

    p.append(text(245, 335, "Геометричний переріз A_core = a · b", size=10.5, color="#475569"))
    p.append(text(245, 355, "Ефективний переріз A_eff = (a + lg) · (b + lg) > A_core", size=10.5, bold=True, color="#15803d"))

    # Права зона: Наслідки та інженерні рішення
    p.append(rect(480, 65, 330, 315, fill="#fffbeb", stroke="#fde68a", sw=1.2, rx=8))
    p.append(text(645, 88, "Наслідки та захист", size=13, bold=True, color="#92400e"))

    cons_items = [
        ("1. Зниження релюктансу:", "Через розширення трубки потоку A_eff > A_core реальний опір зазору менший за 1D-розрахунок (коефіцієнт F_fringe > 1)."),
        ("2. Локальний перегрів:", "Радіальні лінії випучування перетинають мідні провідники обмотки перпендикулярно, наводячи потужні вихрові струми."),
        ("3. Руйнування ізоляції:", "Температура дроту поблизу зазору може перевищити 150°C, спричиняючи міжвиткове коротке замикання."),
    ]
    cy = 118
    for ctitle, cdesc in cons_items:
        p.append(text(495, cy, ctitle, size=11, bold=True, anchor="start", color="#78350f"))
        cy += 18
        # Текст із переносом
        p.append(mtext(495, cy, cdesc, size=10, color="#451a03", anchor="start", lh=1.25))
        cy += 48

    p.append(rect(495, 290, 300, 75, fill="#fef3c7", stroke="#d97706", sw=1.2, rx=6))
    p.append(text(645, 310, "Правило проектування:", size=10.5, bold=True, color="#92400e"))
    p.append(text(645, 328, "Тримати обмотку на відстані ≥ 2·lg від зазору,", size=10, color="#78350f"))
    p.append(text(645, 345, "або застосовувати розподілений зазор (порошкові осердя)", size=9.5, color="#78350f"))

    render(os.path.join(IMG, "fringing-flux.svg"), W, H, *p)


# ── 4. Закони Кірхгофа для розгалужених магнітних кіл ─────────────────────────
def fig_kirchhoff():
    W, H = 840, 420
    p = []
    p.append(text(W / 2, 26, "Закони Кірхгофа для розгалуженого магнітного кола", size=16, bold=True))
    p.append(text(W / 2, 46, "Тристержневе Ш-осердя, баланс потоків у вузлах та падіння МРС у контурах", size=12, color=MUTED, italic=True))

    # Ліва частина: Тристержневе осердя
    p.append(rect(30, 65, 380, 335, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=8))
    p.append(text(220, 88, "Тристержневе Ш-подібне осердя", size=13, bold=True, color=INK))

    # Ш-подібний магнітопровід
    # Зовнішня рамка осердя
    p.append(rect(60, 115, 320, 170, fill="#94a3b8", stroke="#475569", sw=2, rx=4))
    # Два вікна
    p.append(rect(115, 145, 75, 110, fill="#f8fafc", stroke="#475569", sw=1.5, rx=2))
    p.append(rect(250, 145, 75, 110, fill="#f8fafc", stroke="#475569", sw=1.5, rx=2))

    # Центральний керн з обмоткою
    p.append(rect(190, 170, 60, 60, fill="#fed7aa", stroke="#ea580c", sw=1.2, rx=3))
    p.append(text(220, 195, "Обмотка", size=10.5, bold=True, color="#9a3412"))
    p.append(text(220, 212, "N · I", size=10, color="#9a3412"))

    # Стрілки потоків
    # Центральний потік Φ1 вгору
    p.append(line(220, 245, 220, 130, color=FIELD, sw=2.2))
    p.append(arrow(220, 160, 220, 135, color=FIELD, sw=2.2))
    p.append(text(220, 126, "Φ1 (Центр)", size=10.5, bold=True, color=FIELD))

    # Вузол поділу зверху
    p.append(circle(220, 130, 4, fill=FIELD, stroke="#14532d", sw=1.5))
    p.append(text(220, 108, "Вузол A", size=11, bold=True, color="#14532d"))

    # Лівий потік Φ2
    p.append(line(220, 130, 87, 130, color=FIELD, sw=1.8))
    p.append(line(87, 130, 87, 270, color=FIELD, sw=1.8))
    p.append(line(87, 270, 220, 270, color=FIELD, sw=1.8))
    p.append(arrow(87, 180, 87, 220, color=FIELD, sw=1.8))
    p.append(text(75, 205, "Φ2", size=11, bold=True, color=FIELD, anchor="end"))

    # Правий потік Φ3
    p.append(line(220, 130, 353, 130, color=FIELD, sw=1.8))
    p.append(line(353, 130, 353, 270, color=FIELD, sw=1.8))
    p.append(line(353, 270, 220, 270, color=FIELD, sw=1.8))
    p.append(arrow(353, 180, 353, 220, color=FIELD, sw=1.8))
    p.append(text(365, 205, "Φ3", size=11, bold=True, color=FIELD, anchor="start"))

    p.append(text(220, 310, "1-й закон (Вузол A):  Φ1 = Φ2 + Φ3", size=11.5, bold=True, color="#1e293b"))
    p.append(text(220, 332, "Для симетричного осердя: Φ2 = Φ3 = Φ1 / 2", size=10.5, color="#475569"))
    p.append(text(220, 352, "Площа центрального керна A_c = 2 · A_side", size=10, color=MUTED))

    # Права частина: Еквівалентна магнітна схема
    p.append(rect(430, 65, 380, 335, fill="#f0fdf4", stroke="#bbf7d0", sw=1.2, rx=8))
    p.append(text(620, 88, "Еквівалентна магнітна схема", size=13, bold=True, color="#14532d"))

    # Схема з релюктансами
    # Вузол Top (A) і Bottom (B)
    p.append(circle(620, 125, 4.5, fill="#15803d", stroke="#14532d", sw=1.5))
    p.append(text(620, 115, "Вузол A", size=10.5, bold=True, color="#14532d"))

    p.append(circle(620, 275, 4.5, fill="#15803d", stroke="#14532d", sw=1.5))
    p.append(text(620, 292, "Вузол B", size=10.5, bold=True, color="#14532d"))

    # Центральна гілка (Джерело F + Rc)
    p.append(line(620, 125, 620, 150, color=FIELD, sw=1.8))
    p.append(rect(585, 150, 70, 35, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    p.append(text(620, 168, "F = N·I", size=10.5, bold=True, color="#166534"))

    p.append(line(620, 185, 620, 205, color=FIELD, sw=1.8))
    p.append(rect(585, 205, 70, 35, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=4))
    p.append(text(620, 226, "R_c", size=11, bold=True, color="#1e293b"))
    p.append(line(620, 240, 620, 275, color=FIELD, sw=1.8))
    p.append(arrow(620, 145, 620, 130, color=FIELD, sw=2))

    # Ліва гілка (R_left)
    p.append(line(620, 125, 480, 125, color=FIELD, sw=1.8))
    p.append(line(480, 125, 480, 180, color=FIELD, sw=1.8))
    p.append(rect(445, 180, 70, 40, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=4))
    p.append(text(480, 205, "R_left", size=11, bold=True, color="#1e293b"))
    p.append(line(480, 220, 480, 275, color=FIELD, sw=1.8))
    p.append(line(480, 275, 620, 275, color=FIELD, sw=1.8))
    p.append(arrow(480, 145, 480, 165, color=FIELD, sw=1.8))

    # Права гілка (R_right)
    p.append(line(620, 125, 760, 125, color=FIELD, sw=1.8))
    p.append(line(760, 125, 760, 180, color=FIELD, sw=1.8))
    p.append(rect(725, 180, 70, 40, fill="#f1f5f9", stroke="#475569", sw=1.5, rx=4))
    p.append(text(760, 205, "R_right", size=11, bold=True, color="#1e293b"))
    p.append(line(760, 220, 760, 275, color=FIELD, sw=1.8))
    p.append(line(760, 275, 620, 275, color=FIELD, sw=1.8))
    p.append(arrow(760, 145, 760, 165, color=FIELD, sw=1.8))

    # 2-й закон Кірхгофа формули
    p.append(text(450, 320, "2-й закон (Контур 1): F = Φ1 · Rc + Φ2 · R_left", size=11, bold=True, anchor="start", color="#14532d"))
    p.append(text(450, 342, "2-й закон (Контур 2): F = Φ1 · Rc + Φ3 · R_right", size=11, bold=True, anchor="start", color="#14532d"))
    p.append(text(450, 368, "Еквівалентний опір: R_total = Rc + (R_left || R_right)", size=10.5, anchor="start", color="#334155"))

    render(os.path.join(IMG, "kirchhoff-magnetic-network.svg"), W, H, *p)


if __name__ == '__main__':
    fig_analogy()
    fig_core_gap()
    fig_fringing()
    fig_kirchhoff()
    print("SVG figures generated successfully in %s" % IMG)
