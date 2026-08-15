# -*- coding: utf-8 -*-
"""Фігури до теми «Похідна Шварца».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

SCHW_COLOR = "#2457d6"  # синє для похідної Шварца
CRIT_COLOR = "#c0392b"  # червоне для критичних точок
ACC_COLOR  = "#27ae60"  # зелене для атракторів / осей
LINE_DARK  = "#1a1a1a"
GRID_COLOR = "#e1e8ed"

def path(d, fill="none", stroke=LINE, sw=1.5, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<path d="%s" fill="%s" stroke="%s" stroke-width="%.1f"%s/>'
            % (d, fill, stroke, sw, da))

# ── Фігура 1: Геометричний зміст негативної похідної Шварца ──────────────────
def fig_schwarzian_concept():
    W, H = 860, 420
    f = [text(W / 2, 28, "Геометричний ефект від'ємної похідної Шварца S(f) < 0", size=16, bold=True)]

    # Ліва панель: викривлення інтервалу при S(f) < 0
    f.append(text(220, 60, "Стискання внутрішніх підінтервалів (фокусування)", size=13, bold=True, color=SCHW_COLOR))
    f.append(rect(40, 75, 360, 280, fill="#f8fafc", stroke="#cbd5e1", sw=1.5, rx=8))

    # Осі
    f.append(line(70, 320, 370, 320, color=LINE_DARK, sw=1.5))
    f.append(line(70, 320, 70, 95, color=LINE_DARK, sw=1.5))
    f.append(text(380, 324, "x", size=13, bold=True, anchor="start"))
    f.append(text(66, 88, "f(x)", size=13, bold=True))

    # Пунктир рівності f(x)=x
    f.append(line(70, 320, 340, 95, color=MUTED, sw=1.2, dash="4,4"))

    # Крива з S(f) < 0 (о опукла вниз / з негативним Шварціаном)
    f.append(path("M 70 300 Q 200 120 340 100", stroke=SCHW_COLOR, sw=2.5))

    # Позначення стискання інтервалу
    f.append(circle(140, 230, 4, fill=CRIT_COLOR, stroke=CRIT_COLOR))
    f.append(circle(200, 155, 4, fill=CRIT_COLOR, stroke=CRIT_COLOR))
    f.append(circle(260, 118, 4, fill=CRIT_COLOR, stroke=CRIT_COLOR))

    f.append(line(140, 320, 140, 230, color=MUTED, sw=1, dash="2,2"))
    f.append(line(200, 320, 200, 155, color=MUTED, sw=1, dash="2,2"))
    f.append(line(260, 320, 260, 118, color=MUTED, sw=1, dash="2,2"))

    f.append(text(140, 336, "x₁", size=12))
    f.append(text(200, 336, "x₂", size=12))
    f.append(text(260, 336, "x₃", size=12))

    # Стрілки розтягу/стиску
    f.append(arrow(140, 348, 200, 348, color=CRIT_COLOR, sw=1.5))
    f.append(text(170, 362, "Δx₁", size=11, color=CRIT_COLOR))
    f.append(arrow(200, 348, 260, 348, color=CRIT_COLOR, sw=1.5))
    f.append(text(230, 362, "Δx₂", size=11, color=CRIT_COLOR))

    # Пояснення
    f.append(text(220, 395, "При S(f)<0 похідна |f'| зростає повільніше ніж середня", size=12, color=MUTED))

    # Права панель: графік похідної Шварца S(f)(x)
    f.append(text(640, 60, "Графік похідної Шварца S(f)(x) < 0", size=13, bold=True, color=CRIT_COLOR))
    f.append(rect(460, 75, 360, 280, fill="#fff5f5", stroke="#fca5a5", sw=1.5, rx=8))

    f.append(line(490, 140, 790, 140, color=LINE_DARK, sw=1.5))  # вісь 0
    f.append(line(640, 95, 640, 320, color=LINE_DARK, sw=1.5))   # вісь x=x_c

    f.append(text(800, 144, "x", size=13, bold=True, anchor="start"))
    f.append(text(638, 88, "S(f)", size=13, bold=True))

    # Крива S(f) прямує до -нескінченності в критичній точці
    f.append(path("M 500 170 Q 610 200 632 310", stroke=CRIT_COLOR, sw=2.5))
    f.append(path("M 780 170 Q 670 200 648 310", stroke=CRIT_COLOR, sw=2.5))

    f.append(line(640, 140, 640, 320, color=CRIT_COLOR, sw=1.2, dash="3,3"))
    f.append(text(640, 130, "x_c (f'=0)", size=12, color=CRIT_COLOR))

    f.append(text(640, 395, "В околі критичної точки S(f) прямує до -∞", size=12, color=MUTED))

    render(os.path.join(IMG, "schwarzian-concept.svg"), W, H, *f)

# ── Фігура 2: Інваріантність відносно перетворень Мьобіуса ────────────────────
def fig_mobius_invariance():
    W, H = 860, 380
    f = [text(W / 2, 28, "Інваріантність похідної Шварца відносно дробово-лінійних перетворень", size=16, bold=True)]

    # Блок 1: Початкова функція f(x)
    box1, w1, h1 = textbox(160, 140, "Функція f(x)\nS(f)(x) = q(x)", size=14, pad=14, fill="#eff6ff", stroke=SCHW_COLOR, bold=True)
    f.append(box1)

    # Перетворення Мьобіуса M(z)
    f.append(arrow(260, 140, 380, 140, color=LINE_DARK, sw=2))
    f.append(text(320, 125, "M(z) = (az+b)/(cz+d)", size=12, color=LINE_DARK))
    f.append(text(320, 160, "дробово-лінійне", size=11, color=MUTED))

    # Блок 2: Композиція M(f(x))
    box2, w2, h2 = textbox(500, 140, "Композиція M(f(x))\nS(M ∘ f)(x) = S(f)(x)", size=14, pad=14, fill="#f0fdf4", stroke=ACC_COLOR, bold=True)
    f.append(box2)

    # Нижня частина: зв'язок з диференціальним рівнянням y'' + q(x)y = 0
    f.append(rect(80, 230, 700, 110, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    f.append(text(430, 255, "Зв'язок з лінійними системними рівняннями 2-го порядку", size=14, bold=True, color=LINE_DARK))
    f.append(text(430, 282, "Якщо y₁ і y₂ — незалежні розв'язки y'' + q(x)y = 0, то відношення f(x) = y₁/y₂ має S(f) = 2 q(x)", size=13, color=SCHW_COLOR))
    f.append(text(430, 310, "Будь-яка інша пара розв'язків пов'язана матрицею SL(2,ℝ) і дає те саме S(f)", size=12, color=MUTED))

    render(os.path.join(IMG, "mobius-invariance.svg"), W, H, *f)

# ── Фігура 3: Теорема Сінґера для логістичного відображення ───────────────────
def fig_singer_attractor():
    W, H = 860, 440
    f = [text(W / 2, 28, "Теорема Сінґера: Захоплення критичної точки стійкою орбітою", size=16, bold=True)]

    # Графік параболи f(x) = r x (1 - x) та ламаної Ламерея (web diagram)
    f.append(rect(50, 65, 360, 320, fill="#fafafa", stroke="#d1d5db", sw=1.5, rx=8))
    f.append(text(230, 85, "Логістичне відображення f(x) = r·x·(1-x)", size=13, bold=True))

    # Осі
    f.append(line(80, 340, 380, 340, color=LINE_DARK, sw=1.5))
    f.append(line(80, 340, 80, 100, color=LINE_DARK, sw=1.5))
    f.append(line(80, 340, 350, 100, color=MUTED, sw=1.2, dash="3,3")) # y=x

    # Парабола
    f.append(path("M 80 340 Q 230 40 380 340", stroke=SCHW_COLOR, sw=2.5))

    # Критична точка x_c = 0.5
    f.append(line(230, 340, 230, 115, color=CRIT_COLOR, sw=1.5, dash="4,4"))
    f.append(circle(230, 115, 5, fill=CRIT_COLOR, stroke=CRIT_COLOR))
    f.append(text(230, 358, "x_c = 0.5 (f'=0)", size=12, color=CRIT_COLOR, bold=True))

    # Ламана Ламерея (траєкторія від x_c до 2-циклу)
    f.append(line(230, 115, 335, 115, color=ACC_COLOR, sw=1.6))
    f.append(line(335, 115, 335, 210, color=ACC_COLOR, sw=1.6))
    f.append(line(335, 210, 175, 210, color=ACC_COLOR, sw=1.6))
    f.append(line(175, 210, 175, 280, color=ACC_COLOR, sw=1.6))
    f.append(line(175, 280, 275, 280, color=ACC_COLOR, sw=1.6))
    f.append(line(275, 280, 275, 170, color=ACC_COLOR, sw=1.6))

    f.append(text(230, 405, "Траєкторія від x_c притягується до стійкого циклу", size=12, color=ACC_COLOR))

    # Правий блок: Наслідки для хаосу та біфуркацій
    f.append('<g transform="translate(0,0)">')
    f.append(rect(450, 65, 360, 320, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    f.append('</g>')
    f.append(text(630, 95, "Чому S(f) < 0 гарантує порядок:", size=14, bold=True, color=LINE_DARK))

    items = [
        "1. Максимум 1 стійкий цикл для 1 критичної точки",
        "2. Немає незримих закритих стійких середовищ",
        "3. Усі біфуркації подвоєння періоду є строго впорядкованими",
        "4. Відсутнє співіснування двох стійких циклів",
        "5. Універсальність каскаду Фейгенбаума δ ≈ 4.669"
    ]
    y_start = 145
    for it in items:
        box_item, _, _ = textbox(630, y_start, it, size=12, pad=8, fill="#ffffff", stroke="#cbd5e1", min_w=320)
        f.append(box_item)
        y_start += 48

    f.append(text(630, 405, "Singer (1978): S(f)<0 є основою нелінійної динаміки", size=12, color=MUTED))

    render(os.path.join(IMG, "singer-attractor.svg"), W, H, *f)

# ── Фігура 4: Шварціан у квантовій механіці та теорії поля ───────────────────
def fig_syk_schwarzian_action():
    W, H = 860, 380
    f = [text(W / 2, 28, "Шварціан у конформній теорії поля (CFT) та квантовій гравітації", size=16, bold=True)]

    # Схема межі AdS2 та диффеоморфізмів часу
    f.append(rect(50, 70, 360, 270, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    f.append(text(230, 95, "Гільбертів простір та межа AdS₂", size=13, bold=True, color=LINE_DARK))

    # Коптівське коло / межа
    f.append(circle(230, 200, 75, fill="#eff6ff", stroke=SCHW_COLOR, sw=2))
    f.append(text(230, 200, "AdS₂ bulk", size=13, color=MUTED))
    f.append(path("M 155 200 A 75 75 0 0 1 305 200", stroke=CRIT_COLOR, sw=2.5))
    f.append(text(230, 290, "Перепараметризація часу τ → f(τ)", size=12, color=CRIT_COLOR, bold=True))

    # Формули справа
    f.append(rect(450, 70, 360, 270, fill="#faf5ff", stroke="#d8b4fe", sw=1.5, rx=8))
    f.append(text(630, 95, "Поле / Квантова дія Шварціана", size=14, bold=True, color="#6b21a8"))

    box_a, _, _ = textbox(630, 150, "CFT тензор енергії-імпульсу:\nT'(z) = (f')² T(f) + (c/12) S(f)(z)", size=12, pad=10, fill="#ffffff", stroke="#c084fc")
    f.append(box_a)

    box_b, _, _ = textbox(630, 230, "Ефективна дія SYK / JT-гравітації:\nS_eff = -C ∫ {f(τ), τ} dτ", size=12, pad=10, fill="#ffffff", stroke="#c084fc")
    f.append(box_b)

    box_c, _, _ = textbox(630, 300, "{f, τ} ≡ S(f)(τ) — Шварціан порушення симетрії", size=11, pad=6, fill="#f3e8ff", stroke="#a855f7")
    f.append(box_c)

    f.append(text(W / 2, 360, "Оператор Шварца описує квантові аномалії та термальні флуктуації часу", size=12, color=MUTED))

    render(os.path.join(IMG, "syk-schwarzian-action.svg"), W, H, *f)

if __name__ == "__main__":
    fig_schwarzian_concept()
    fig_mobius_invariance()
    fig_singer_attractor()
    fig_syk_schwarzian_action()
    print("Всі 4 фігури згенеровано у ./img/")
