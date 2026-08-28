# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми shcho-musyt-buty-vydno-zavzhdy."""

import sys
import os

# scripts/ у корені репо (4 рівні вгору)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# ФІГУРА 1: Золотий квадрант критичного статусу оператора
# ─────────────────────────────────────────────────────────────────────────────
def gen_golden_quadrant():
    W, H = 840, 460
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill='#ffffff', stroke='#d0d7de', sw=1.5, rx=8))
    frags.append(text(W / 2, 36, 'ЗОЛОТИЙ КВАДРАНТ КРИТИЧНОГО СТАТУСУ ОПЕРАТОРА', size=16, bold=True, color='#1f2328'))
    frags.append(text(W / 2, 54, 'Чотири базові групи параметрів, які ніколи не зникають з поля зору', size=11, color='#656d76'))

    qw = 390
    qh = 155
    x1 = 22
    x2 = 428
    y1 = 72
    y2 = 245

    # Квадрант 1: ПРОСТОРОВИЙ СТАН
    frags.append(rect(x1, y1, qw, qh, fill='#f0f8ff', stroke='#0969da', sw=1.8, rx=6))
    frags.append(rect(x1, y1, qw, 30, fill='#ddf4ff', stroke='#0969da', sw=1.2, rx=6))
    frags.append(text(x1 + 15, y1 + 20, '1. ПРОСТОРОВИЙ СТАН (STATE)', size=12, bold=True, color='#0969da', anchor='start'))
    
    state_lines = [
        '• Просторове положення: крен, тангаж, рискання (Attitude)',
        '• Швидкість: повітряна (IAS) та шляхова над ґрунтом (GS)',
        '• Висота: абсолютна (Baro/AMSL) та над рельєфом (AGL)',
        '• Вертикальна динаміка: швидкість підйому / спуску (VSI)'
    ]
    frags.append(mtext(x1 + 15, y1 + 50, state_lines, size=11, color='#1f2328', anchor='start', lh=1.4))
    frags.append(text(x1 + 15, y1 + 142, 'Питання: «Де саме перебуває апарат і куди він рухається?»', size=10, italic=True, color='#57606a', anchor='start'))

    # Квадрант 2: РЕЖИМ КЕРУВАННЯ
    frags.append(rect(x2, y1, qw, qh, fill='#fcf8e3', stroke='#9a6700', sw=1.8, rx=6))
    frags.append(rect(x2, y1, qw, 30, fill='#fff8c5', stroke='#9a6700', sw=1.2, rx=6))
    frags.append(text(x2 + 15, y1 + 20, '2. РЕЖИМ КЕРУВАННЯ (MODE)', size=12, bold=True, color='#9a6700', anchor='start'))

    mode_lines = [
        '• Активний автопілотний режим: MANUAL / ALTHOLD / AUTO',
        '• Стан виконавчої готовності: DISARMED / ARMED / EMERGENCY',
        '• Джерело навігаційних уставок: RC / Місія / ШІ-супутник',
        '• Фаза навігаційної задачі: Takeoff / Waypoint / Hold / RTL'
    ]
    frags.append(mtext(x2 + 15, y1 + 50, mode_lines, size=11, color='#1f2328', anchor='start', lh=1.4))
    frags.append(text(x2 + 15, y1 + 142, 'Питання: «Хто керує апаратом і яка логіка активна зараз?»', size=10, italic=True, color='#57606a', anchor='start'))

    # Квадрант 3: ЗДОРОВ\'Я ПЛАТФОРМИ
    frags.append(rect(x1, y2, qw, qh, fill='#fdf2f2', stroke='#cf222e', sw=1.8, rx=6))
    frags.append(rect(x1, y2, qw, 30, fill='#ffebe9', stroke='#cf222e', sw=1.2, rx=6))
    frags.append(text(x1 + 15, y2 + 20, '3. ЗДОРОВ\'Я ПЛАТФОРМИ (HEALTH)', size=12, bold=True, color='#cf222e', anchor='start'))

    health_lines = [
        '• Батарейна шина: напруга під навантаженням (V_bat), розкид',
        '• Енергетика: струм споживання (I_load), витрачена ємність',
        '• Тепловий стан: температура силових ключів (ESC), АКБ',
        '• Бортові ресурси: навантаження MCU/CPU (%), вільна пам\'ять'
    ]
    frags.append(mtext(x1 + 15, y2 + 50, health_lines, size=11, color='#1f2328', anchor='start', lh=1.4))
    frags.append(text(x1 + 15, y2 + 142, 'Питання: «Скільки енергії та робочого ресурсу лишилося?»', size=10, italic=True, color='#57606a', anchor='start'))

    # Квадрант 4: КАНАЛИ ЗВ\'ЯЗКУ
    frags.append(rect(x2, y2, qw, qh, fill='#f6f8fa', stroke='#1a7f37', sw=1.8, rx=6))
    frags.append(rect(x2, y2, qw, 30, fill='#dafbe1', stroke='#1a7f37', sw=1.2, rx=6))
    frags.append(text(x2 + 15, y2 + 20, '4. СТАН КАНАЛІВ ЗВ\'ЯЗКУ (LINK)', size=12, bold=True, color='#1a7f37', anchor='start'))

    link_lines = [
        '• Енергетика радіолінка: рівень RSSI (дБм), співвідношення SNR',
        '• Якість потоку пакетів: Link Quality (LQ %) у ковзному вікні',
        '• Кругова затримка зв\'язку: Round-Trip Time (RTT, мс)',
        '• Вік останнього кадру: Packet Age / Staleness (мс / с)'
    ]
    frags.append(mtext(x2 + 15, y2 + 50, link_lines, size=11, color='#1f2328', anchor='start', lh=1.4))
    frags.append(text(x2 + 15, y2 + 142, 'Питання: «Чи актуальні дані й чи пройде керівна команда?»', size=10, italic=True, color='#57606a', anchor='start'))

    # Центральний маркер синтезу
    cx, cy = W / 2, (y1 + qh + y2) / 2
    c_box, c_w, c_h = textbox(cx, cy, 'СИТУАЦІЙНА ОБІЗНАНІСТЬ\n(100% фіксовані координати)', size=11, bold=True, fill='#24292f', stroke='#1f2328', color='#ffffff', pad=8)
    frags.append(c_box)

    frags.append(rect(22, H - 42, W - 44, 26, fill='#f6f8fa', stroke='#d0d7de', sw=1, rx=4))
    frags.append(text(W / 2, H - 25, 'Правило: жоден параметр із цих чотирьох груп не може бути прихований чи заміщений', size=11, bold=True, color='#24292f'))

    render(os.path.join(IMG_DIR, 'golden-quadrant.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# ФІГУРА 2: Архітектура шарів GUI та принцип незмінного закріплення (Sticky Bar)
# ─────────────────────────────────────────────────────────────────────────────
def gen_sticky_layers():
    W, H = 840, 450
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill='#ffffff', stroke='#d0d7de', sw=1.5, rx=8))
    frags.append(text(W / 2, 34, 'АРХІТЕКТУРА ШАРІВ GUI: НЕЗМІННЕ ЗАКРІПЛЕННЯ СТАТУС-БАРУ', size=16, bold=True, color='#1f2328'))
    frags.append(text(W / 2, 52, 'Ієрархія Z-order: критичний шар заблокований поверх будь-яких діалогів та вікон', size=11, color='#656d76'))

    layers = [
        {
            'name': 'ШАР 0: ФОН ТА ПЕРВИННИЙ КОНТЕНТ (Background / Primary Plane)',
            'desc': 'Відеопотік з FPV-камери (1080p60) • Векторна карта рельєфу • Штучний горизонт PFD',
            'color': '#0969da', 'fill': '#f0f8ff', 'y': 72, 'h': 65, 'z': 'Z = 0 (Нижній шар)'
        },
        {
            'name': 'ШАР 1: РОБОЧІ ВІДЖЕТИ ТА ІНСТРУМЕНТИ (Work Widgets / Tools)',
            'desc': 'Таблиця точок місії • Графіки телеметрії • Панелі налаштування PID-регуляторів',
            'color': '#57606a', 'fill': '#f6f8fa', 'y': 147, 'h': 65, 'z': 'Z = 10 (Робочий простір)'
        },
        {
            'name': 'ШАР 2: МОДАЛЬНІ ВІКНА ТА ДІАЛОГИ (Modal Dialogs / Popups)',
            'desc': 'Спливаючі підтвердження («Slide to Arm») • Повідомлення про калібрування • Меню конфігурації',
            'color': '#9a6700', 'fill': '#fff8c5', 'y': 222, 'h': 65, 'z': 'Z = 50 (Спливаючі вікна)'
        },
        {
            'name': 'ШАР 3: НЕПЕРЕКРИВНИЙ ОВЕРЛЕЙ (LOCKED TOP OVERLAY STATUS BAR)',
            'desc': 'Критичний статусний бар • Анонсатор режимів • Індикатори батареї та зв\'язку • Постійна сітка',
            'color': '#cf222e', 'fill': '#ffebe9', 'y': 297, 'h': 75, 'z': 'Z = 100 (Абсолютний пріоритет)'
        }
    ]

    for l in layers:
        frags.append(rect(25, l['y'], 645, l['h'], fill=l['fill'], stroke=l['color'], sw=1.8, rx=6))
        frags.append(text(40, l['y'] + 22, l['name'], size=11, bold=True, color=l['color'], anchor='start'))
        frags.append(text(40, l['y'] + 45, l['desc'], size=10, color='#1f2328', anchor='start'))
        frags.append(rect(685, l['y'], 130, l['h'], fill=l['fill'], stroke=l['color'], sw=1.5, rx=6))
        frags.append(text(750, l['y'] + l['h']/2 + 4, l['z'], size=10, bold=True, color=l['color']))

    frags.append(line(675, 355, 675, 95, color='#656d76', sw=2, dash='4,4'))
    frags.append(arrow(675, 130, 675, 85, color='#cf222e', sw=2.5))
    frags.append(text(675, 75, 'Z-ORDER RENDER', size=9, bold=True, color='#cf222e'))

    frags.append(rect(25, 390, 790, 32, fill='#24292f', stroke='#1f2328', sw=1, rx=4))
    frags.append(text(W / 2, 410, 'Заборона оклюзії: модальне вікно затемнює шар 1 і 0, але НІКОЛИ не накриває шар 3', size=11, bold=True, color='#ffffff'))

    render(os.path.join(IMG_DIR, 'sticky-layers-zorder.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# ФІГУРА 3: Семантичні колірні переходи та гістерезис захисту від мерехтіння
# ─────────────────────────────────────────────────────────────────────────────
def gen_color_hysteresis():
    W, H = 840, 440
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill='#ffffff', stroke='#d0d7de', sw=1.5, rx=8))
    frags.append(text(W / 2, 34, 'СЕМАНТИЧНІ КОЛІРНІ ПЕРЕХОДИ ТА ГІСТЕРЕЗИС ПЕРЕМИКАННЯ', size=16, bold=True, color='#1f2328'))
    frags.append(text(W / 2, 52, 'Запобігання мерехтінню кольору на граничних значеннях через зону нечутливості та дебаунс', size=11, color='#656d76'))

    gx, gy, gw, gh = 35, 75, 770, 180

    h_green = 55
    h_yellow = 65
    h_red = 60

    # 3 окремі суцільні прямокутники зон
    frags.append(rect(gx, gy, gw, h_green, fill='#dafbe1', stroke='#1a7f37', sw=1, rx=0))
    frags.append(text(gx + 15, gy + 32, 'НОРМА (ЗЕЛЕНИЙ): V_bat ≥ 14.8 В (≥ 3.7 В/комірку)', size=11, bold=True, color='#1a7f37', anchor='start'))
    frags.append(text(gx + gw - 15, gy + 32, 'Зона повної функціональності', size=10, italic=True, color='#1a7f37', anchor='end'))

    frags.append(rect(gx, gy + h_green, gw, h_yellow, fill='#fff8c5', stroke='#9a6700', sw=1, rx=0))
    frags.append(text(gx + 15, gy + h_green + 38, 'УВАГА / ДЕГРАДАЦІЯ (ЖОВТИЙ): 14.0 В ≤ V_bat < 14.8 В', size=11, bold=True, color='#9a6700', anchor='start'))
    frags.append(text(gx + gw - 15, gy + h_green + 38, 'Повернення в норму: V ≥ 15.05 В (+0.25 В гістерезис)', size=10, bold=True, color='#9a6700', anchor='end'))

    frags.append(rect(gx, gy + h_green + h_yellow, gw, h_red, fill='#ffebe9', stroke='#cf222e', sw=1, rx=0))
    frags.append(text(gx + 15, gy + h_green + h_yellow + 38, 'КРИТИЧНО (ЧЕРВОНИЙ): V_bat < 14.0 В (< 3.5 В/комірку — аварійна посадка)', size=11, bold=True, color='#cf222e', anchor='start'))
    frags.append(text(gx + gw - 15, gy + h_green + h_yellow + 38, 'Повернення в жовтий: V ≥ 14.25 В', size=10, bold=True, color='#cf222e', anchor='end'))

    # Межі гістерезису позначимо лініями пунктиру
    frags.append(line(gx, gy + h_green, gx + gw, gy + h_green, color='#d97706', sw=1.5, dash='5,5'))
    frags.append(line(gx, gy + h_green + h_yellow, gx + gw, gy + h_green + h_yellow, color='#dc2626', sw=1.5, dash='5,5'))

    # Сигнал напруги
    pts = [
        (gx + 20, gy + 22), (gx + 70, gy + 27), (gx + 120, gy + 20),
        (gx + 160, gy + 45), (gx + 190, gy + 60), (gx + 220, gy + 56),
        (gx + 260, gy + 80), (gx + 300, gy + 90), (gx + 340, gy + 82),
        (gx + 380, gy + 110), (gx + 420, gy + 122), (gx + 450, gy + 114),
        (gx + 490, gy + 142), (gx + 530, gy + 152), (gx + 570, gy + 132),
        (gx + 610, gy + 108), (gx + 650, gy + 100), (gx + 720, gy + 92)
    ]
    for i in range(len(pts) - 1):
        frags.append(line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], color='#1f2328', sw=2.2))

    sy = 275
    bw, bh = 220, 80

    frags.append(rect(35, sy, bw, bh, fill='#dafbe1', stroke='#1a7f37', sw=1.8, rx=6))
    frags.append(text(145, sy + 25, 'СТАН: НОРМА [ЗЕЛЕНИЙ]', size=11, bold=True, color='#1a7f37'))
    frags.append(text(145, sy + 45, 'Показники стабільні', size=10, color='#1f2328'))
    frags.append(text(145, sy + 63, 'Фільтр оновлення: 5 Гц', size=9, color='#57606a'))

    frags.append(rect(310, sy, bw, bh, fill='#fff8c5', stroke='#9a6700', sw=1.8, rx=6))
    frags.append(text(420, sy + 25, 'СТАН: ДЕГРАДАЦІЯ [ЖОВТИЙ]', size=11, bold=True, color='#9a6700'))
    frags.append(text(420, sy + 45, 'Дебаунс входу: 200 мс', size=10, color='#1f2328'))
    frags.append(text(420, sy + 63, 'Вихід: V ≥ V_warn + ΔV (1.5 с)', size=9, color='#57606a'))

    frags.append(rect(585, sy, bw, bh, fill='#ffebe9', stroke='#cf222e', sw=1.8, rx=6))
    frags.append(text(695, sy + 25, 'СТАН: ВІДМОВА [ЧЕРВОНИЙ]', size=11, bold=True, color='#cf222e'))
    frags.append(text(695, sy + 45, 'Миттєвий вхід (0 мс)', size=10, color='#1f2328'))
    frags.append(text(695, sy + 63, 'Вихід: V ≥ V_crit + ΔV (3.0 с)', size=9, color='#57606a'))

    frags.append(arrow(255, sy + 30, 310, sy + 30, color='#9a6700', sw=1.8))
    frags.append(arrow(310, sy + 55, 255, sy + 55, color='#1a7f37', sw=1.8))
    frags.append(arrow(530, sy + 30, 585, sy + 30, color='#cf222e', sw=1.8))
    frags.append(arrow(585, sy + 55, 530, sy + 55, color='#9a6700', sw=1.8))

    frags.append(text(W / 2, H - 20, 'Принцип асиметрії: перехід у гірший стан — швидкий, повернення в кращий — лише з підтвердженим гістерезисом', size=11, bold=True, color='#1f2328'))

    render(os.path.join(IMG_DIR, 'color-state-hysteresis.svg'), W, H, *frags)


# ─────────────────────────────────────────────────────────────────────────────
# ФІГУРА 4: Подвійне кодування (Redundant Encoding): Колір + Форма + Текст
# ─────────────────────────────────────────────────────────────────────────────
def gen_redundant_encoding():
    W, H = 840, 430
    frags = []

    frags.append(rect(10, 10, W - 20, H - 20, fill='#ffffff', stroke='#d0d7de', sw=1.5, rx=8))
    frags.append(text(W / 2, 34, 'ПОДВІЙНЕ КОДУВАННЯ: КОЛІР + ФОРМА ПІКТОГРАМИ + ТЕКСТОВИЙ МАРКЕР', size=16, bold=True, color='#1f2328'))
    frags.append(text(W / 2, 52, 'Читабельність для операторів із колірною сліпотою та в умовах яскравого сонячного засвічування', size=11, color='#656d76'))

    headers = [
        (30, 150, 'СИСТЕМНИЙ СТАН'),
        (190, 210, 'ПОВНОКОЛІРНИЙ ВИГЛЯД'),
        (410, 210, 'ДЕЙТЕРАНОПІЯ / СОНЦЕ'),
        (630, 180, 'ЕЛblockНТИ ДУБЛЮВАННЯ')
    ]

    hy = 72
    frags.append(rect(25, hy, 790, 28, fill='#f6f8fa', stroke='#d0d7de', sw=1, rx=4))
    for hx, hw, ht in headers:
        frags.append(text(hx + hw/2, hy + 18, ht, size=10, bold=True, color='#57606a'))

    rows = [
        {
            'state': 'НОРМАЛЬНИЙ\n(All Nominal)',
            'rgb_fill': '#dafbe1', 'rgb_stroke': '#1a7f37', 'rgb_txt': '16.2V  [OK]  ARM: AUTO  LQ:100%',
            'sim_fill': '#f0f0f0', 'sim_stroke': '#333333', 'sim_txt': '16.2V  [OK]  ARM: AUTO  LQ:100%',
            'elem': '• Символ галочки [OK]\n• Суцільна тонка рамка\n• Чіткий числовий стан',
            'y': 108, 'h': 65
        },
        {
            'state': 'ПОПblockДЖЕННЯ\n(Degraded Reserve)',
            'rgb_fill': '#fff8c5', 'rgb_stroke': '#9a6700', 'rgb_txt': '14.4V  [! LOW]  ALTHOLD  LQ:60%',
            'sim_fill': '#e5e5e5', 'sim_stroke': '#1f2328', 'sim_txt': '14.4V  [! LOW]  ALTHOLD  LQ:60%',
            'elem': '• Трикутник із знаком оклику [!]\n• Текстовий тег [LOW]\n• Жирний акцидентний шрифт',
            'y': 178, 'h': 65
        },
        {
            'state': 'КРИТИЧНА ВІДМОВА\n(Critical / Failsafe)',
            'rgb_fill': '#ffebe9', 'rgb_stroke': '#cf222e', 'rgb_txt': '13.7V  [X CRIT]  FAILSAFE: RTL',
            'sim_fill': '#d0d0d0', 'sim_stroke': '#000000', 'sim_txt': '13.7V  [X CRIT]  FAILSAFE: RTL',
            'elem': '• Знак оклику в рамці [X CRIT]\n• Інверсна підкладка та контур\n• Подвійна товста рамка 3px',
            'y': 248, 'h': 65
        },
        {
            'state': 'ЗАСТАРІЛІ ДАНІ\n(Telemetry Stale)',
            'rgb_fill': '#f1f5f9', 'rgb_stroke': '#64748b', 'rgb_txt': '15.1V  [⧗ STALE 2.4s]  LOST',
            'sim_fill': '#e2e8f0', 'sim_stroke': '#475569', 'sim_txt': '15.1V  [⧗ STALE 2.4s]  LOST',
            'elem': '• Піктограма пісочного годинника [⧗]\n• Таймер віку пакета [STALE Xs]\n• Перекреслення значень',
            'y': 318, 'h': 65
        }
    ]

    for r in rows:
        frags.append(rect(25, r['y'], 155, r['h'], fill='#ffffff', stroke='#d0d7de', sw=1, rx=4))
        frags.append(mtext(102, r['y'] + 28, r['state'], size=10, bold=True, color='#1f2328', lh=1.3))

        frags.append(rect(190, r['y'], 210, r['h'], fill=r['rgb_fill'], stroke=r['rgb_stroke'], sw=1.8, rx=4))
        frags.append(text(295, r['y'] + r['h']/2 + 4, r['rgb_txt'], size=9, bold=True, color=r['rgb_stroke']))

        frags.append(rect(410, r['y'], 210, r['h'], fill=r['sim_fill'], stroke=r['sim_stroke'], sw=1.8, rx=4))
        frags.append(text(515, r['y'] + r['h']/2 + 4, r['sim_txt'], size=9, bold=True, color='#000000'))

        frags.append(rect(630, r['y'], 185, r['h'], fill='#ffffff', stroke='#d0d7de', sw=1, rx=4))
        frags.append(mtext(640, r['y'] + 20, r['elem'], size=9, color='#24292f', anchor='start', lh=1.3))

    frags.append(text(W / 2, H - 15, 'Залізне правило UI: колір підсилює повідомлення, але форма й текст несуть його самостійно', size=11, bold=True, color='#cf222e'))

    render(os.path.join(IMG_DIR, 'redundant-visual-encoding.svg'), W, H, *frags)


if __name__ == '__main__':
    gen_golden_quadrant()
    gen_sticky_layers()
    gen_color_hysteresis()
    gen_redundant_encoding()
    print('All 4 figures generated successfully.')