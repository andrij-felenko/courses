# -*- coding: utf-8 -*-
"""Фігури до теми «Модель Зачдева-Є-Кітаєва (SYK model)».
Запуск: python figs.py -> пише SVG у ./img/
Стиль і помічники — зі спільного svgkit."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')

COLOR_PRIMARY = "#1e3a8a"    # Темно-синій для пропагаторів / блоків
COLOR_ACCENT = "#d97706"     # Янтарний для самоенергії / мелонів
COLOR_CHAOS = "#dc2626"      # Червоний для квантового хаосу / OTOC
COLOR_GRAVITY = "#7c3aed"    # Фіолетовий для JT-гравітації / AdS2
COLOR_BG = "#f8fafc"
COLOR_LINE = "#334155"
COLOR_MUTED = "#64748b"

def path(d, fill="none", stroke=COLOR_LINE, sw=1.5, dash=None):
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw:.1f}"{da}/>'


# ── Фігура 1: Мелонні діаграми та рівняння Швінгера-Дайсона ────────────────────
def fig_melonic_diagrams():
    W, H = 860, 430
    f = [text(W / 2, 28, "Мелонна діаграматика та самоузгодження Швінгера-Дайсона у границі N → ∞", size=16, bold=True, color=COLOR_PRIMARY)]

    # Верхній блок: Рівняння Швінгера-Дайсона для пропагатора G(τ)
    f.append(rect(30, 50, 800, 160, fill="#f0f9ff", stroke="#bae6fd", sw=1.5, rx=8))
    f.append(text(50, 75, "1. Рівняння Швінгера-Дайсона: G⁻¹ = G₀⁻¹ - Σ", size=14, bold=True, color=COLOR_PRIMARY, anchor="start"))

    # Схема G = G0 + G0 * Sigma * G
    # Ліва частина: Повний пропагатор G (жирна лінія)
    f.append(text(90, 130, "G(τ)", size=13, bold=True, color=COLOR_PRIMARY))
    f.append(line(60, 145, 140, 145, color=COLOR_PRIMARY, sw=4))
    f.append(circle(60, 145, 4, fill=COLOR_PRIMARY))
    f.append(circle(140, 145, 4, fill=COLOR_PRIMARY))

    # Знак "="
    f.append(text(165, 148, "=", size=18, bold=True, color=COLOR_LINE))

    # Вплив вільний пропагатор G0 (тонка лінія)
    f.append(text(215, 130, "G₀(τ)", size=13, bold=True, color=COLOR_MUTED))
    f.append(line(190, 145, 260, 145, color=COLOR_MUTED, sw=1.5))
    f.append(circle(190, 145, 3, fill=COLOR_MUTED))
    f.append(circle(260, 145, 3, fill=COLOR_MUTED))

    # Знак "+"
    f.append(text(285, 148, "+", size=18, bold=True, color=COLOR_LINE))

    # Комбінація G0 * Sigma * G
    f.append(line(310, 145, 360, 145, color=COLOR_MUTED, sw=1.5))
    # Вставка самоенергії (овал / мелон)
    f.append(f'<ellipse cx="395" cy="145" rx="35" ry="20" fill="#fef3c7" stroke="{COLOR_ACCENT}" stroke-width="2"/>')
    f.append(text(395, 149, "Σ(τ)", size=12, bold=True, color=COLOR_ACCENT))
    f.append(line(430, 145, 480, 145, color=COLOR_PRIMARY, sw=4))
    f.append(circle(310, 145, 3, fill=COLOR_MUTED))
    f.append(circle(480, 145, 4, fill=COLOR_PRIMARY))

    # Пояснювальна підписна лінія
    f.append(text(520, 135, "Інтегральне самоузгодження у часовому просторі:", size=12, bold=True, color=COLOR_LINE, anchor="start"))
    f.append(text(520, 160, "G(τ - τ') = G₀(τ - τ') + ∫ G₀(τ - τ'') Σ(τ'' - τ''') G(τ''' - τ') dτ'' dτ'''", size=11, color=COLOR_MUTED, anchor="start"))

    # Нижній блок: Структура мелонного графа для Σ(τ) при q=4
    f.append(rect(30, 230, 800, 170, fill="#fffbeb", stroke="#fde68a", sw=1.5, rx=8))
    f.append(text(50, 255, "2. Мелонна самоенергія Σ(τ) = J² · [G(τ)]³ (для q=4)", size=14, bold=True, color=COLOR_ACCENT, anchor="start"))

    # Малювання мелонного графа (3 внутрішні лінії G(τ))
    f.append(circle(140, 335, 5, fill=COLOR_LINE))
    f.append(circle(300, 335, 5, fill=COLOR_LINE))
    f.append(text(140, 365, "τ = 0", size=12, bold=True, color=COLOR_LINE))
    f.append(text(300, 365, "τ", size=12, bold=True, color=COLOR_LINE))

    # 3 внутрішні лінії (мелон / кавун)
    f.append(path("M 140 335 Q 220 270 300 335", stroke=COLOR_PRIMARY, sw=2.5))
    f.append(path("M 140 335 L 300 335", stroke=COLOR_PRIMARY, sw=2.5))
    f.append(path("M 140 335 Q 220 400 300 335", stroke=COLOR_PRIMARY, sw=2.5))

    # Пунктирне усреднення J_ijkl
    f.append(path("M 140 335 Q 220 240 300 335", stroke=COLOR_ACCENT, sw=1.5, dash="4,4"))
    f.append(text(220, 248, "⟨J_ijkl J_ijkl⟩ = 6 J² / N³", size=11, bold=True, color=COLOR_ACCENT))

    f.append(text(220, 290, "G(τ)", size=11, color=COLOR_PRIMARY))
    f.append(text(220, 325, "G(τ)", size=11, color=COLOR_PRIMARY))
    f.append(text(220, 360, "G(τ)", size=11, color=COLOR_PRIMARY))

    # Пояснення справа
    f.append(text(370, 300, "• У границі N → ∞ виживають ЛЕШЕ мелонні (плоскі) діаграми.", size=12, color=COLOR_LINE, anchor="start"))
    f.append(text(370, 325, "• Перехресні (non-nested) діаграми пригнічені як O(1/N²).", size=12, color=COLOR_LINE, anchor="start"))
    f.append(text(370, 350, "• Рівняння допускає точний аналітичний розв'язок у конформній межі.", size=12, color=COLOR_LINE, anchor="start"))

    render(os.path.join(IMG, "melonic-diagrams.svg"), W, H, *f)


# ── Фігура 2: Порушення конформної симетрії та Шварціан ───────────────────────
def fig_conformal_symmetry_breaking():
    W, H = 860, 400
    f = [text(W / 2, 28, "Спонтанне та явне порушення конформної симетрії в SYK моделі", size=16, bold=True, color=COLOR_PRIMARY)]

    # Схема каскаду симетрій
    # Блок 1: Висока температура / УФ (вільні ферміони)
    f.append(rect(40, 70, 230, 280, fill="#f1f5f9", stroke="#cbd5e1", sw=1.5, rx=8))
    f.append(text(155, 95, "Ультрафіолет (УФ)", size=14, bold=True, color=COLOR_LINE))
    f.append(text(155, 120, "J·τ ≪ 1 (короткі часи)", size=11, color=COLOR_MUTED))
    f.append(line(60, 140, 250, 140, color="#cbd5e1", sw=1))

    f.append(text(155, 170, "Вільний пропагатор:", size=12, bold=True, color=COLOR_LINE))
    f.append(text(155, 195, "G₀(τ) = 1/2 sgn(τ)", size=12, color=COLOR_PRIMARY))
    f.append(text(155, 235, "Домінує кінетичний терм", size=11, color=COLOR_MUTED))
    f.append(text(155, 255, "∂_τ у рівняннях", size=11, color=COLOR_MUTED))
    f.append(text(155, 305, "Немає конформності", size=12, bold=True, color=COLOR_CHAOS))

    # Стрілка перенормгрупи (РГ-потік)
    f.append(arrow(280, 210, 330, 210, color=COLOR_PRIMARY, sw=2.5))
    f.append(text(305, 195, "РГ-потік", size=11, bold=True, color=COLOR_PRIMARY))
    f.append(text(305, 230, "T ≪ J", size=11, color=COLOR_MUTED))

    # Блок 2: Конформна границя (ІЧ)
    f.append(rect(340, 70, 230, 280, fill="#eff6ff", stroke="#93c5fd", sw=1.5, rx=8))
    f.append(text(455, 95, "Конформний ІЧ режим", size=14, bold=True, color=COLOR_PRIMARY))
    f.append(text(455, 120, "J·τ ≫ 1 (довгі часи)", size=11, color=COLOR_MUTED))
    f.append(line(360, 140, 550, 140, color="#93c5fd", sw=1))

    f.append(text(455, 170, "Емерджентна симетрія:", size=12, bold=True, color=COLOR_LINE))
    f.append(text(455, 195, "Diff(S¹) репараметризація", size=12, bold=True, color=COLOR_PRIMARY))
    f.append(text(455, 230, "G_c(τ) ∝ sgn(τ)/|Jτ|^(1/2)", size=12, color=COLOR_PRIMARY))
    f.append(text(455, 270, "Спонтанне порушення:", size=12, bold=True, color=COLOR_ACCENT))
    f.append(text(455, 295, "Diff(S¹) → SL(2,ℝ)", size=13, bold=True, color=COLOR_ACCENT))

    # Стрілка виклику м'яких мод
    f.append(arrow(580, 210, 630, 210, color=COLOR_ACCENT, sw=2.5))
    f.append(text(605, 195, "Виправлення", size=11, bold=True, color=COLOR_ACCENT))
    f.append(text(605, 230, "1/(J·β)", size=11, color=COLOR_MUTED))

    # Блок 3: Шварціановий режим м'яких мод
    f.append(rect(640, 70, 180, 280, fill="#fff7ed", stroke="#fdba74", sw=1.5, rx=8))
    f.append(text(730, 95, "Шварціаніка", size=14, bold=True, color=COLOR_ACCENT))
    f.append(text(730, 120, "Явне порушення", size=11, color=COLOR_MUTED))
    f.append(line(660, 140, 800, 140, color="#fdba74", sw=1))

    f.append(text(730, 175, "Голдстоунівська мода:", size=12, bold=True, color=COLOR_LINE))
    f.append(text(730, 200, "f(τ) ∈ Diff(S¹)/SL(2,ℝ)", size=11, color=COLOR_PRIMARY))
    f.append(text(730, 240, "Ефективна дія:", size=12, bold=True, color=COLOR_ACCENT))
    f.append(text(730, 270, "S_eff = - α_S N/J", size=12, bold=True, color=COLOR_CHAOS))
    f.append(text(730, 295, "× ∫ {f(τ), τ} dτ", size=12, bold=True, color=COLOR_CHAOS))

    # Нижній загальний підпис
    f.append(text(W / 2, 380, "Похідна Шварца {f, τ} виникає як найнижчий оператор, що описує динаміку Голдстоунівських псевдонабутих мод.", size=12, color=COLOR_MUTED))

    render(os.path.join(IMG, "conformal-symmetry-breaking.svg"), W, H, *f)


# ── Фігура 3: Експоненційне зростання OTOC та квантовий хаос ──────────────────
def fig_otoc_chaos():
    W, H = 860, 420
    f = [text(W / 2, 28, "Динаміка нечасововпорядкованого корелятора (OTOC) та межа хаосу MSS", size=16, bold=True, color=COLOR_CHAOS)]

    # Ліва панель: Графік OTOC F(t) = <A(t) B(0) A(t) B(0)>
    f.append(rect(40, 60, 450, 310, fill="#fafafa", stroke="#e5e5e5", sw=1.5, rx=8))
    f.append(text(265, 85, "Зростання хаосу F(t) у часі t", size=13, bold=True, color=COLOR_LINE))

    # Осі
    f.append(line(80, 330, 460, 330, color=COLOR_LINE, sw=1.5))
    f.append(line(80, 330, 80, 110, color=COLOR_LINE, sw=1.5))
    f.append(text(465, 334, "t", size=13, bold=True, anchor="start"))
    f.append(text(78, 100, "F(t)", size=13, bold=True))

    # Лінія насичення 1.0
    f.append(line(80, 130, 450, 130, color=COLOR_MUTED, sw=1, dash="3,3"))
    f.append(text(70, 134, "1", size=11, color=COLOR_MUTED, anchor="end"))

    # Лінія нульового хаосу
    f.append(text(70, 334, "0", size=11, color=COLOR_MUTED, anchor="end"))

    # Крива OTOC: F(t) = 1 - (c/N) * exp(λ_L * t)
    f.append(path("M 80 135 L 200 140 Q 310 160 360 280 L 440 320", stroke=COLOR_CHAOS, sw=2.5))

    # Час скрамблінгу t*
    f.append(line(360, 330, 360, 110, color=COLOR_ACCENT, sw=1.5, dash="4,4"))
    f.append(text(360, 348, "t_* (Scrambling time)", size=11, bold=True, color=COLOR_ACCENT))

    # Позначки розпаду
    f.append(text(220, 175, "1 - (c/N) e^(λ_L t)", size=12, bold=True, color=COLOR_CHAOS))

    # Права панель: Пояснення показника Ляпунова та MSS-межі
    f.append(rect(510, 60, 320, 310, fill="#fff5f5", stroke="#fecaca", sw=1.5, rx=8))
    f.append(text(670, 88, "Межа хаосу MSS", size=14, bold=True, color=COLOR_CHAOS))
    f.append(text(670, 110, "(Maldacena-Shenker-Stanford)", size=11, color=COLOR_MUTED))

    f.append(line(530, 128, 810, 128, color="#fecaca", sw=1))

    f.append(text(530, 155, "Показник Ляпунова λ_L:", size=12, bold=True, color=COLOR_LINE, anchor="start"))
    f.append(rect(540, 170, 260, 45, fill="#ffffff", stroke=COLOR_CHAOS, sw=1.5, rx=6))
    f.append(text(670, 198, "λ_L = 2π k_B T / ℏ", size=15, bold=True, color=COLOR_CHAOS))

    f.append(text(530, 240, "• SYK є МАКСИМАЛЬНО хаотичною", size=12, color=COLOR_LINE, anchor="start"))
    f.append(text(545, 260, "квантовою системою.", size=12, color=COLOR_LINE, anchor="start"))

    f.append(text(530, 290, "• Час скрамблінгу інформації:", size=12, color=COLOR_LINE, anchor="start"))
    f.append(text(545, 310, "t_* = (ℏ / 2π k_B T) · ln N", size=12, bold=True, color=COLOR_ACCENT, anchor="start"))

    f.append(text(530, 345, "• Аналог насичення горизонту чорної діри.", size=11, color=COLOR_MUTED, anchor="start"))

    render(os.path.join(IMG, "otoc-chaos.svg"), W, H, *f)


# ── Фігура 4: Голографічна дуальність SYK ↔ AdS2 / JT-гравітація ─────────────
def fig_syk_ads_duality():
    W, H = 860, 420
    f = [text(W / 2, 28, "Голографічний дуалізм: 0+1D квантова модель SYK ↔ 1+1D JT-гравітація в AdS₂", size=16, bold=True, color=COLOR_PRIMARY)]

    # Лівий блок: 0+1D SYK модель на межі
    f.append(rect(40, 70, 340, 300, fill="#f0fdf4", stroke="#86efac", sw=1.5, rx=8))
    f.append(text(210, 100, "Квантова межа (0+1D)", size=14, bold=True, color="#166534"))
    f.append(text(210, 122, "Модель Зачдева-Є-Кітаєва (SYK)", size=12, color=COLOR_MUTED))
    f.append(line(60, 140, 360, 140, color="#86efac", sw=1))

    # Елементи SYK
    f.append(text(65, 170, "• N Майоранівських ферміонів χ_i", size=12, color=COLOR_LINE, anchor="start"))
    f.append(text(65, 200, "• Випадкова all-to-all взаємодія J_ijkl", size=12, color=COLOR_LINE, anchor="start"))
    f.append(text(65, 230, "• Емерджентна конформна симетрія", size=12, color=COLOR_LINE, anchor="start"))
    f.append(text(65, 260, "• Максимальний хаос λ_L = 2π T", size=12, color=COLOR_CHAOS, anchor="start"))
    f.append(text(65, 290, "• Залишкова ентропія S₀ = N · s₀", size=12, color=COLOR_ACCENT, anchor="start"))
    f.append(text(65, 335, "Динаміка описується дією Шварціана S[f]", size=11, bold=True, color="#166534", anchor="start"))

    # Двостороння голографічна стрілка
    f.append(arrow(400, 220, 460, 220, color=COLOR_GRAVITY, sw=3))
    f.append(arrow(460, 220, 400, 220, color=COLOR_GRAVITY, sw=3))
    f.append(text(430, 195, "AdS₂ / CFT₁", size=12, bold=True, color=COLOR_GRAVITY))
    f.append(text(430, 245, "Дуальність", size=12, bold=True, color=COLOR_GRAVITY))

    # Правий блок: 1+1D JT-гравітація в балці AdS2
    f.append(rect(480, 70, 340, 300, fill="#f5f3ff", stroke="#c4b5fd", sw=1.5, rx=8))
    f.append(text(650, 100, "Гравітаційний балк (1+1D)", size=14, bold=True, color=COLOR_GRAVITY))
    f.append(text(650, 122, "JT-гравітація Жакова-Тетельбойма", size=12, color=COLOR_MUTED))
    f.append(line(500, 140, 800, 140, color="#c4b5fd", sw=1))

    # Елементи JT-гравітації
    f.append(text(505, 170, "• Метрика простору AdS₂ зі зрізом", size=12, color=COLOR_LINE, anchor="start"))
    f.append(text(505, 200, "• Дилатонне поле Φ(x) та кривизна R = -2", size=12, color=COLOR_LINE, anchor="start"))
    f.append(text(505, 230, "• Динаміка межі (Boundary Graviton)", size=12, color=COLOR_LINE, anchor="start"))
    f.append(text(505, 260, "• 2D квантова чорна діра з горизонтом", size=12, color=COLOR_CHAOS, anchor="start"))
    f.append(text(505, 290, "• Термодинамічна ентропія Бетенштейна", size=12, color=COLOR_ACCENT, anchor="start"))
    f.append(text(505, 335, "Дія межі збігається з діянням Шварціана", size=11, bold=True, color=COLOR_GRAVITY, anchor="start"))

    render(os.path.join(IMG, "syk-ads-duality.svg"), W, H, *f)


if __name__ == "__main__":
    fig_melonic_diagrams()
    fig_conformal_symmetry_breaking()
    fig_otoc_chaos()
    fig_syk_ads_duality()
    print("Фігури SYK успішно згенеровано у ./img/")
