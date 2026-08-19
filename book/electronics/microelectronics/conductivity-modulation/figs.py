# -*- coding: utf-8 -*-
"""Фігури до теми «Модуляція провідності у силових приладах» (book/electronics/microelectronics/conductivity-modulation)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), "img"), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), "img")


def fig_unipolar_vs_modulated():
    w, h = 880, 440
    frags = []

    # Заголовки двох колонок
    t1, _, _ = textbox(220, 30, "Уніполярний дрейф (MOSFET / Шотткі)\nСтрум лише основних носіїв", size=13, bold=True, pad=8)
    frags.append(t1)

    t2, _, _ = textbox(660, 30, "Модуляція провідності (PIN / IGBT)\nЗатоплення електронно-дірковою плазмою", size=13, bold=True, pad=8)
    frags.append(t2)

    # ── Ліва частина: Уніполярний дрейф ──
    # Структура кристала
    frags.append(rect(40, 75, 360, 150, fill="#f8f9fa", stroke="#7f8c8d", sw=1.5, rx=4))
    frags.append(rect(40, 75, 50, 150, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=0))
    frags.append(text(65, 155, "n⁺", size=14, bold=True, color="#1e7e34"))

    frags.append(rect(90, 75, 260, 150, fill="#fff3cd", stroke="#e0a800", sw=1.2, rx=0))
    frags.append(text(220, 105, "Слабколегована дрейфова n⁻ база", size=12, bold=True, color="#856404"))
    frags.append(text(220, 130, "N_D ≈ 10¹⁴ см⁻³  (товщина W_d ≈ 100 мкм)", size=11, color="#856404"))
    frags.append(text(220, 160, "Питомий опір ρ ≈ 45 Ом·см", size=12, bold=True, color=POS))
    frags.append(text(220, 190, "n(x) = N_D  (лише електрони легування)", size=11, color="#555555"))

    frags.append(rect(350, 75, 50, 150, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=0))
    frags.append(text(375, 155, "n⁺", size=14, bold=True, color="#1e7e34"))

    # Графік падіння напруги
    frags.append(rect(40, 240, 360, 170, fill="none", stroke="#ced4da", sw=1.2, rx=4))
    frags.append(line(80, 380, 370, 380, color=LINE, sw=1.5))  # вісь X
    frags.append(line(80, 260, 80, 380, color=LINE, sw=1.5))   # вісь V
    frags.append(text(70, 265, "V(x)", size=11, color=INK, bold=True))
    frags.append(text(370, 395, "x (координата бази)", size=10, color=MUTED))

    # Лінійний спад напруги з величезним нахилом
    frags.append(line(80, 275, 360, 375, color=POS, sw=2.5))
    frags.append(circle(80, 275, 3, fill=POS, stroke=POS))
    frags.append(circle(360, 375, 3, fill=POS, stroke=POS))

    tb_v1, _, _ = textbox(220, 305, "Величезне омічне падіння напруги\nΔV_drift = I · R_drift ≈ 45 В (при 100 А)\nP_втрат = 4.5 кВт  (кристал плавиться)", size=11, color=POS, fill="#fdecea", stroke=POS, pad=6)
    frags.append(tb_v1)

    # Розділювач
    frags.append(line(440, 20, 440, 420, color="#d0d7de", sw=1.5, dash="5,5"))

    # ── Права частина: Модуляція провідності ──
    # Структура кристала
    frags.append(rect(480, 75, 360, 150, fill="#f8f9fa", stroke="#7f8c8d", sw=1.5, rx=4))
    frags.append(rect(480, 75, 50, 150, fill="#f8d7da", stroke="#dc3545", sw=1.5, rx=0))
    frags.append(text(505, 135, "p⁺", size=14, bold=True, color="#721c24"))
    frags.append(text(505, 165, "Анод", size=10, color="#721c24"))

    # Модульована база
    frags.append(rect(530, 75, 260, 150, fill="#d1ecf1", stroke="#17a2b8", sw=1.2, rx=0))
    frags.append(text(660, 100, "Затоплена плазмою n⁻ база", size=12, bold=True, color="#0c5460"))
    frags.append(text(660, 125, "n(x) ≈ p(x) ≈ 10¹⁷ см⁻³ >> N_D", size=12, bold=True, color=FIELD))
    frags.append(text(660, 150, "Питомий опір падає: ρ ≈ 0.03 Ом·см", size=11, bold=True, color="#0c5460"))

    # Стрілки інжекції носіїв
    frags.append(arrow(535, 180, 600, 180, color=POS, sw=2))
    frags.append(text(575, 172, "Дірки p(x)", size=10, color=POS, bold=True))

    frags.append(arrow(785, 180, 720, 180, color=NEG, sw=2))
    frags.append(text(745, 172, "Електрони n(x)", size=10, color=NEG, bold=True))

    frags.append(rect(790, 75, 50, 150, fill="#d4edda", stroke="#27ae60", sw=1.5, rx=0))
    frags.append(text(815, 135, "n⁺", size=14, bold=True, color="#1e7e34"))
    frags.append(text(815, 165, "Катод", size=10, color="#1e7e34"))

    # Графік падіння напруги
    frags.append(rect(480, 240, 360, 170, fill="none", stroke="#ced4da", sw=1.2, rx=4))
    frags.append(line(520, 380, 810, 380, color=LINE, sw=1.5))  # вісь X
    frags.append(line(520, 260, 520, 380, color=LINE, sw=1.5))  # вісь V
    frags.append(text(510, 265, "V(x)", size=11, color=INK, bold=True))
    frags.append(text(810, 395, "x (координата бази)", size=10, color=MUTED))

    # Стрибки на p-n переходах і плаский спад у базі
    frags.append(line(520, 310, 545, 345, color=FIELD, sw=2))
    frags.append(line(545, 345, 785, 355, color=FIELD, sw=2.5))
    frags.append(line(785, 355, 805, 375, color=FIELD, sw=2))

    tb_v2, _, _ = textbox(660, 305, "Опір бази колапсує у 1000+ разів!\nΔV_base ≈ 0.3 В  (при 100 А)\nV_F = V_j1 + ΔV_base + V_j2 ≈ 1.3 В\nP_втрат ≈ 130 Вт  (нормальне охолодження)", size=11, color="#0c5460", fill="#e8f4f8", stroke="#17a2b8", pad=6)
    frags.append(tb_v2)

    render(os.path.join(IMG, "fig-unipolar-vs-modulated.svg"), w, h, *frags)


def fig_plasma_profile():
    w, h = 880, 460
    frags = []

    t_title, _, _ = textbox(440, 25, "Розподіл електронно-діркової плазми p(x) у дрейфовій базі PIN-структури", size=14, bold=True, pad=8)
    frags.append(t_title)

    # Три інформаційні блоки вгорі (поза графіком)
    tb_leg1, _, _ = textbox(170, 75, "d / L_a = 1.0 (W_B = 2 L_a)\nПовне рівномірне затоплення\np_min >> N_D → Мінімальне V_F", size=10, color="#1e7e34", fill="#d4edda", stroke="#27ae60", pad=5)
    frags.append(tb_leg1)

    tb_leg2, _, _ = textbox(440, 75, "d / L_a = 2.5 (W_B = 5 L_a)\nПомірний провал у центрі бази\np(0) падає у 10 разів, V_F зростає", size=10, color="#004085", fill="#cce5ff", stroke="#004085", pad=5)
    frags.append(tb_leg2)

    tb_leg3, _, _ = textbox(710, 75, "d / L_a = 5.0 (W_B = 10 L_a)\nРекомбінація не пускає носії в центр\np(0) ≈ N_D → катастрофічний стрибок V_F", size=10, color="#721c24", fill="#f8d7da", stroke="#dc3545", pad=5)
    frags.append(tb_leg3)

    # Координатна сітка графіка
    ox, oy, gw, gh = 90, 410, 700, 270
    frags.append(rect(ox - 30, oy - gh - 15, gw + 50, gh + 50, fill="none", stroke="#ced4da", sw=1.2, rx=4))

    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    frags.append(line(ox, oy - gh, ox, oy, color=LINE, sw=1.8))

    frags.append(text(ox - 10, oy - gh + 15, "Концентрація носіїв p(x), см⁻³ (log scale)", size=11, color=INK, bold=True, anchor="start"))
    frags.append(text(ox + gw / 2, oy + 25, "Координата у товщі дрейфової бази x (від анода -d до катода +d)", size=11, color=INK))

    # Мітки меж
    frags.append(line(ox + 50, oy, ox + 50, oy - gh, color="#27ae60", sw=1.2, dash="4,3"))
    frags.append(text(ox + 50, oy + 15, "x = -d (p⁺ анод)", size=10, bold=True, color="#721c24"))

    frags.append(line(ox + gw - 50, oy, ox + gw - 50, oy - gh, color="#27ae60", sw=1.2, dash="4,3"))
    frags.append(text(ox + gw - 50, oy + 15, "x = +d (n⁺ катод)", size=10, bold=True, color="#1e7e34"))

    frags.append(line(ox + gw / 2, oy, ox + gw / 2, oy - gh, color="#d0d7de", sw=1, dash="3,3"))
    frags.append(text(ox + gw / 2, oy + 12, "x = 0 (центр)", size=9, color=MUTED))

    # Рівень фонового легування N_D
    frags.append(line(ox, oy - 30, ox + gw, oy - 30, color="#7f8c8d", sw=1.5, dash="6,4"))
    frags.append(text(ox + gw - 60, oy - 36, "Фонове легування N_D ≈ 10¹⁴ см⁻³", size=10, color="#555555", anchor="end"))

    # Крива 1: Оптимальне затоплення d / L_a = 1 (W_B = 2 L_a)
    path_opt = (
        "M %d %d " % (ox + 50, oy - 230)
        + "Q %d %d %d %d " % (ox + 200, oy - 200, ox + gw / 2, oy - 195)
        + "Q %d %d %d %d" % (ox + gw - 200, oy - 200, ox + gw - 50, oy - 225)
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_opt, FIELD))
    frags.append(circle(ox + gw / 2, oy - 195, 4, fill=FIELD, stroke=FIELD))
    frags.append(text(ox + gw / 2 + 55, oy - 205, "d / L_a = 1.0", size=10, bold=True, color=FIELD))

    # Крива 2: Середнє виснаження центру d / L_a = 2.5 (W_B = 5 L_a)
    path_mid = (
        "M %d %d " % (ox + 50, oy - 230)
        + "Q %d %d %d %d " % (ox + 180, oy - 120, ox + gw / 2, oy - 105)
        + "Q %d %d %d %d" % (ox + gw - 180, oy - 120, ox + gw - 50, oy - 225)
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="6,2"/>' % (path_mid, NEG))
    frags.append(circle(ox + gw / 2, oy - 105, 4, fill=NEG, stroke=NEG))
    frags.append(text(ox + gw / 2 + 55, oy - 115, "d / L_a = 2.5", size=10, bold=True, color=NEG))

    # Крива 3: Катастрофічний провал d / L_a = 5 (W_B = 10 L_a)
    path_bad = (
        "M %d %d " % (ox + 50, oy - 230)
        + "Q %d %d %d %d " % (ox + 150, oy - 45, ox + gw / 2, oy - 35)
        + "Q %d %d %d %d" % (ox + gw - 150, oy - 45, ox + gw - 50, oy - 225)
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-dasharray="3,3"/>' % (path_bad, POS))
    frags.append(circle(ox + gw / 2, oy - 35, 4, fill=POS, stroke=POS))
    frags.append(text(ox + gw / 2 + 55, oy - 48, "d / L_a = 5.0", size=10, bold=True, color=POS))

    render(os.path.join(IMG, "fig-plasma-profile.svg"), w, h, *frags)


def fig_turn_off_tail():
    w, h = 880, 440
    frags = []

    t1, _, _ = textbox(220, 28, "Зворотне відновлення PIN-діода\nРозсмоктування заряду плазми Q_rr", size=13, bold=True, pad=8)
    frags.append(t1)

    t2, _, _ = textbox(660, 28, "Хвостовий струм IGBT при вимиканні\nЕкстракція залишкових дірок у базі", size=13, bold=True, pad=8)
    frags.append(t2)

    # ── Ліва частина: Зворотне відновлення діода ──
    ox1, oy1, gw1, gh1 = 60, 250, 340, 160
    frags.append(rect(ox1 - 20, 60, gw1 + 35, 360, fill="none", stroke="#ced4da", sw=1.2, rx=4))

    # Осі
    frags.append(line(ox1, oy1, ox1 + gw1, oy1, color=LINE, sw=1.5))  # вісь I = 0
    frags.append(line(ox1 + 30, 75, ox1 + 30, 400, color=LINE, sw=1.5))  # вісь t
    frags.append(text(ox1 + 35, 85, "Струм i_D(t)", size=11, color=INK, bold=True, anchor="start"))
    frags.append(text(ox1 + gw1 - 10, oy1 - 8, "t", size=12, color=MUTED))

    # Прямий струм I_F
    frags.append(line(ox1 + 30, oy1 - 100, ox1 + 80, oy1 - 100, color="#27ae60", sw=2.5))
    frags.append(text(ox1 + 55, oy1 - 110, "+I_F (прямий)", size=10, bold=True, color="#27ae60"))

    # Спад струму через di/dt
    frags.append(line(ox1 + 80, oy1 - 100, ox1 + 175, oy1 + 95, color=POS, sw=2.5))
    frags.append(text(ox1 + 140, oy1 - 20, "-di/dt", size=11, bold=True, color=POS))

    # Пік зворотного струму I_rr
    frags.append(circle(ox1 + 175, oy1 + 95, 3.5, fill=POS, stroke=POS))
    frags.append(text(ox1 + 175, oy1 + 115, "-I_rr,peak", size=11, bold=True, color=POS))

    # Відновлення струму до нуля
    path_rec = (
        "M %d %d " % (ox1 + 175, oy1 + 95)
        + "Q %d %d %d %d" % (ox1 + 220, oy1 + 30, ox1 + 310, oy1)
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_rec, POS))

    # Фази t_a та t_b
    frags.append(line(ox1 + 135, oy1, ox1 + 135, oy1 + 55, color=MUTED, sw=1, dash="2,2"))
    frags.append(line(ox1 + 175, oy1, ox1 + 175, oy1 + 95, color=MUTED, sw=1, dash="2,2"))
    frags.append(line(ox1 + 310, oy1, ox1 + 310, oy1 + 40, color=MUTED, sw=1, dash="2,2"))

    frags.append(line(ox1 + 135, oy1 + 45, ox1 + 175, oy1 + 45, color=MUTED, sw=1.2))
    frags.append(text(ox1 + 155, oy1 + 38, "t_a", size=10, bold=True, color=MUTED))

    frags.append(line(ox1 + 175, oy1 + 45, ox1 + 310, oy1 + 45, color=MUTED, sw=1.2))
    frags.append(text(ox1 + 245, oy1 + 38, "t_b (спад)", size=10, bold=True, color=MUTED))

    # Заштрихований заряд Q_rr
    tb_qrr, _, _ = textbox(ox1 + 245, oy1 + 85, "Заряд Q_rr = ∫ i_rr dt\nФактор м'якості S = t_b / t_a", size=10, color=POS, fill="#fff3cd", stroke="#e0a800", pad=5)
    frags.append(tb_qrr)

    tb_dnote, _, _ = textbox(220, 395, "Різкий спад (S << 1) викликає L·(di/dt) перенапругу!", size=10, color=POS, fill="#fdecea", stroke=POS, pad=4)
    frags.append(tb_dnote)

    # Розділювач
    frags.append(line(440, 20, 440, 425, color="#d0d7de", sw=1.5, dash="5,5"))

    # ── Права частина: Хвостовий струм IGBT ──
    ox2, oy2, gw2, gh2 = 500, 330, 340, 240
    frags.append(rect(ox2 - 20, 60, gw2 + 35, 360, fill="none", stroke="#ced4da", sw=1.2, rx=4))

    frags.append(line(ox2, oy2, ox2 + gw2, oy2, color=LINE, sw=1.5))
    frags.append(line(ox2 + 25, 75, ox2 + 25, oy2, color=LINE, sw=1.5))
    frags.append(text(ox2 + 30, 85, "i_C(t) та v_CE(t)", size=11, color=INK, bold=True, anchor="start"))
    frags.append(text(ox2 + gw2 - 10, oy2 + 15, "t", size=12, color=MUTED))

    # Напруга V_CE (швидко наростає до шини живлення V_DC)
    path_vce = (
        "M %d %d " % (ox2 + 30, oy2 - 15)
        + "L %d %d " % (ox2 + 80, oy2 - 15)
        + "L %d %d " % (ox2 + 125, oy2 - 190)
        + "L %d %d" % (ox2 + gw2 - 10, oy2 - 190)
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_vce, NEG))
    frags.append(text(ox2 + gw2 - 20, oy2 - 200, "v_CE(t) → V_DC", size=11, bold=True, color=NEG, anchor="end"))

    # Струм колектора i_C: швидкий спад МОН-каналу + повільний хвіст
    frags.append(line(ox2 + 30, oy2 - 210, ox2 + 80, oy2 - 210, color=POS, sw=2.5))
    frags.append(line(ox2 + 80, oy2 - 210, ox2 + 125, oy2 - 70, color=POS, sw=2.5))  # закриття каналу

    # Хвіст струму дірок (повільна рекомбінація)
    path_tail = (
        "M %d %d " % (ox2 + 125, oy2 - 70)
        + "Q %d %d %d %d" % (ox2 + 190, oy2 - 35, ox2 + gw2 - 20, oy2 - 5)
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_tail, POS))

    # Виділення області хвостового струму
    tb_tail, _, _ = textbox(ox2 + 225, oy2 - 110, "Хвостовий струм I_tail(t)\nЗалишкові дірки у базі\nP(t) = V_DC · I_tail(t)  →  Втрати E_off!", size=10, color="#721c24", fill="#f8d7da", stroke="#dc3545", pad=6)
    frags.append(tb_tail)

    tb_inote, _, _ = textbox(660, 395, "Для скорочення хвоста застосовують радіаційне вбивство часу життя τ", size=10, color="#0c5460", fill="#d1ecf1", stroke="#17a2b8", pad=4)
    frags.append(tb_inote)

    render(os.path.join(IMG, "fig-turn-off-tail.svg"), w, h, *frags)


def fig_tradeoff_technology():
    w, h = 880, 420
    frags = []

    t_title, _, _ = textbox(440, 25, "Технологічний компроміс Баліги: Пряме падіння V_F проти енергії вимикання E_off", size=14, bold=True, pad=8)
    frags.append(t_title)

    ox, oy, gw, gh = 100, 340, 680, 270
    frags.append(rect(ox - 30, oy - gh - 15, gw + 50, gh + 60, fill="none", stroke="#ced4da", sw=1.2, rx=4))

    frags.append(line(ox, oy, ox + gw, oy, color=LINE, sw=1.8))
    frags.append(line(ox, oy - gh, ox, oy, color=LINE, sw=1.8))

    frags.append(text(ox - 15, oy - gh + 15, "Енергія вимикання E_off (або t_rr, Q_rr)", size=12, color=INK, bold=True, anchor="start"))
    frags.append(text(ox + gw / 2, oy + 25, "Пряме падіння напруги провідності V_F, В", size=12, color=INK, bold=True))

    # Стрілка напрямку збільшення часу життя
    frags.append(arrow(ox + 160, oy - 230, ox + 320, oy - 230, color=MUTED, sw=1.5))
    frags.append(text(ox + 240, oy - 240, "Збільшення часу життя носіїв τ_HL", size=10, color=MUTED))

    # 1. Традиційна крива однорідного легування (Au, Pt, e-beam)
    path_conv = (
        "M %d %d " % (ox + 80, oy - 210)
        + "Q %d %d %d %d " % (ox + 140, oy - 80, ox + 380, oy - 45)
        + "L %d %d" % (ox + 500, oy - 35)
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_conv, POS))
    frags.append(text(ox + 490, oy - 50, "Однорідне вбивство часу життя (Au, e-beam)", size=11, bold=True, color=POS, anchor="end"))

    # 2. Покращена крива: Локальне протонне опромінення (H⁺ / He²⁺)
    path_prot = (
        "M %d %d " % (ox + 70, oy - 150)
        + "Q %d %d %d %d " % (ox + 120, oy - 55, ox + 350, oy - 30)
        + "L %d %d" % (ox + 460, oy - 22)
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5" stroke-dasharray="6,2"/>' % (path_prot, NEG))
    frags.append(text(ox + 470, oy - 26, "Локальне аксіальне профілювання (H⁺ / He²⁺)", size=11, bold=True, color=NEG, anchor="start"))

    # 3. Сучасна крива: Field-Stop Trench IGBT + ультратонкий кристал
    path_fs = (
        "M %d %d " % (ox + 60, oy - 100)
        + "Q %d %d %d %d " % (ox + 100, oy - 40, ox + 280, oy - 18)
        + "L %d %d" % (ox + 400, oy - 12)
    )
    frags.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.5"/>' % (path_fs, FIELD))
    frags.append(text(ox + 410, oy - 14, "Field-Stop Trench + тонка база (нова межа)", size=11, bold=True, color=FIELD, anchor="start"))

    # Зони оптимізації
    tb_lowf, _, _ = textbox(ox + 130, oy - 170, "Низькочастотні прилади (50-400 Гц):\nМаксимальний τ_HL, мінімальний V_F\n(Мережеві випрямлячі, тягові приводи)", size=10, color="#1e7e34", fill="#d4edda", stroke="#27ae60", pad=5)
    frags.append(tb_lowf)

    tb_highf, _, _ = textbox(ox + 500, oy - 150, "Високочастотні прилади (20-100 кГц):\nМінімальний τ_HL, мінімальний E_off\n(Імпульсні перетворювачі, SMPS)", size=10, color="#721c24", fill="#f8d7da", stroke="#dc3545", pad=5)
    frags.append(tb_highf)

    render(os.path.join(IMG, "fig-tradeoff-technology.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_unipolar_vs_modulated()
    fig_plasma_profile()
    fig_turn_off_tail()
    fig_tradeoff_technology()
    print("All figures generated successfully.")
