# -*- coding: utf-8 -*-
"""Фігури до теми «Передачі й володіння як джерело затримки».
Запуск: python figs.py  → створює SVG у ./img/
Стиль і помічники — зі спільного svgkit.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(os.path.dirname(__file__), 'img'), exist_ok=True)
IMG = os.path.join(os.path.dirname(__file__), 'img')


def polyline(pts, color, sw=2.4, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    s = " ".join("%.1f,%.1f" % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (s, color, sw, d)


# ───────── Фіг. 1: Множник затримки передач та вибух черг ─────────
def fig_handoff_delay():
    W, H = 880, 480
    f = [text(W / 2, 30, "Вплив завантаженості й кількості передач на час доставки", size=16, bold=True)]

    L, R, TOP, BOT = 100, 760, 90, 390
    
    def wait_multiplier(rho):
        if rho >= 0.98:
            rho = 0.98
        return rho / (1.0 - rho)

    rhos = [i * 0.02 for i in range(46)] # 0.0 to 0.90
    
    pts_1 = [(L + rho * (R - L) / 0.90, BOT - (1.0 + wait_multiplier(rho)) * 24) for rho in rhos]
    pts_3 = [(L + rho * (R - L) / 0.90, BOT - (3.0 + 3.0 * wait_multiplier(rho)) * 24) for rho in rhos]
    pts_5 = [(L + rho * (R - L) / 0.90, BOT - (5.0 + 5.0 * wait_multiplier(rho)) * 24) for rho in rhos]

    pts_1 = [(x, max(TOP + 20, y)) for x, y in pts_1]
    pts_3 = [(x, max(TOP + 20, y)) for x, y in pts_3]
    pts_5 = [(x, max(TOP + 20, y)) for x, y in pts_5]

    # Осі
    f.append(arrow(L, BOT, R + 30, BOT, color=INK, sw=1.8))
    f.append(arrow(L, BOT, L, TOP - 20, color=INK, sw=1.8))
    f.append(text(L - 10, TOP - 30, "Час очікування та виконання (тижні)", size=12, color=MUTED, anchor="start"))
    f.append(text(R + 25, BOT + 25, "Утилізація команд (ρ) →", size=12, color=MUTED, anchor="end"))

    for r_val in [0.0, 0.3, 0.5, 0.7, 0.8, 0.85, 0.9]:
        x = L + r_val * (R - L) / 0.90
        f.append(line(x, BOT, x, BOT + 5, color=INK, sw=1.2))
        f.append(text(x, BOT + 20, "%.0f%%" % (r_val * 100), size=11, color=MUTED))

    # Зона небезпечного навантаження (>80%)
    x_80 = L + 0.80 * (R - L) / 0.90
    f.append(rect(x_80, TOP, R - x_80, BOT - TOP, fill="#fdf2f2", stroke="none"))
    f.append(line(x_80, TOP, x_80, BOT, color=POS, sw=1.5, dash="4,4"))
    f.append(text(x_80 + 60, TOP + 20, "Зона вибуху черг (ρ > 80%)", size=11, bold=True, color=POS, anchor="start"))

    f.append(polyline(pts_1, FIELD, sw=2.5))
    f.append(polyline(pts_3, NEG, sw=2.5))
    f.append(polyline(pts_5, POS, sw=3.0))

    # Легенда
    ly = TOP + 10
    f.append(line(L + 20, ly, L + 50, ly, color=FIELD, sw=2.5))
    f.append(text(L + 56, ly + 4, "1 передача (Stream-Aligned)", size=11, bold=True, color=INK, anchor="start"))

    f.append(line(L + 250, ly, L + 280, ly, color=NEG, sw=2.5))
    f.append(text(L + 286, ly + 4, "3 передачі (Dev → QA → Ops)", size=11, bold=True, color=INK, anchor="start"))

    f.append(line(L + 480, ly, L + 510, ly, color=POS, sw=3.0))
    f.append(text(L + 516, ly + 4, "5 передач (колодязна організація)", size=11, bold=True, color=INK, anchor="start"))

    f.append(text(W / 2, H - 20, "Заміна передач автоматизованими платформеними інтерфейсами усуває нелінійне зростання черг", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, "handoff-delay-multiplier.svg"), W, H, *f)


# ───────── Фіг. 2: Спектр моделей володіння кодом ─────────
def fig_ownership_spectrum():
    W, H = 920, 520
    f = [text(W / 2, 28, "Спектр моделей володіння кодом та їхні компроміси", size=16, bold=True)]

    col_w = 200
    gap = 18
    start_x = 35
    top_y = 65

    models = [
        {
            "title": "Колективне володіння",
            "subtitle": "(Collective Ownership)",
            "color": "#e74c3c",
            "bg": "#fdf2f2",
            "friction": "0 затримок",
            "quality": "Деградація",
            "context": "Нічий код",
            "desc": "Будь-хто править будь-що.\nМалі команди.\nНа масштабі — хаос."
        },
        {
            "title": "Слабке володіння",
            "subtitle": "(InnerSource / Weak)",
            "color": "#27ae60",
            "bg": "#eafaf0",
            "friction": "PR gates",
            "quality": "Хранитель",
            "context": "Контракт",
            "desc": "Хранитель ставить рамки.\nІнші команди надсилають PR.\nАвтоперевірка."
        },
        {
            "title": "Жорстке володіння",
            "subtitle": "(Strong Ownership)",
            "color": "#2457d6",
            "bg": "#ebf3fe",
            "friction": "Черги тикетів",
            "quality": "Висока local",
            "context": "Колодязь",
            "desc": "Править тільки власник.\nВисока якість коду,\nале величезні черги."
        },
        {
            "title": "Наскрізне володіння",
            "subtitle": "(Stream-Aligned)",
            "color": "#8e44ad",
            "bg": "#f5eef8",
            "friction": "Self-service",
            "quality": "Продуктова",
            "context": "Потік ценності",
            "desc": "Володіння фічею end-to-end.\nСкладні системи споживає\nчерез API платформи."
        }
    ]

    for i, m in enumerate(models):
        cx = start_x + i * (col_w + gap) + col_w / 2
        
        # Шапка картки
        card_box, _w, _h = textbox(cx, top_y + 35, "%s\n%s" % (m["title"], m["subtitle"]),
                                   size=12, pad=8, fill=m["bg"], stroke=m["color"], sw=2, bold=True, min_w=col_w)
        f.append(card_box)

        # Тіло параметрів
        param_y = top_y + 90
        param_box = rect(cx - col_w/2, param_y, col_w, 120, fill="#ffffff", stroke="#d1d5db", sw=1.2, rx=6)
        f.append(param_box)
        
        f.append(text(cx - col_w/2 + 10, param_y + 25, "Терення:", size=11, bold=True, color=MUTED, anchor="start"))
        f.append(text(cx + col_w/2 - 10, param_y + 25, m["friction"], size=11, bold=True, color=INK, anchor="end"))

        f.append(text(cx - col_w/2 + 10, param_y + 55, "Якість коду:", size=11, bold=True, color=MUTED, anchor="start"))
        f.append(text(cx + col_w/2 - 10, param_y + 55, m["quality"], size=11, bold=True, color=INK, anchor="end"))

        f.append(text(cx - col_w/2 + 10, param_y + 85, "Контекст:", size=11, bold=True, color=MUTED, anchor="start"))
        f.append(text(cx + col_w/2 - 10, param_y + 85, m["context"], size=11, bold=True, color=INK, anchor="end"))

        # Опис нижче
        desc_y = param_y + 135
        desc_box, _, _ = textbox(cx, desc_y + 40, m["desc"], size=11, pad=8, fill=FILL, stroke="#e5e7eb", sw=1, min_w=col_w)
        f.append(desc_box)

    f.append(text(W / 2, H - 18, "Перехід від колодязного володіння до InnerSource та Stream-Aligned зменшує час затримки в 3–5 разів", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, "ownership-spectrum.svg"), W, H, *f)


# ───────── Фіг. 3: Архітектурне усунення передач ─────────
def fig_decoupling_handoffs():
    W, H = 880, 490
    f = [text(W / 2, 28, "Трансформація: від ручних передач до автократичного Self-Service", size=16, bold=True)]

    # Лівий блок: Традиційна ручна модель (колодязі та квитки)
    f.append(text(220, 65, "ТРАДИЦІЙНА МОДЕЛЬ (Ручні передачі)", size=13, bold=True, color=POS))
    box_trad = rect(30, 85, 380, 340, fill="#fff5f5", stroke=POS, sw=1.5, rx=8)
    f.append(box_trad)

    trad_steps = [
        "1. Dev розробляє фічу",
        "2. Квиток у DBA (очікування 4 дні)",
        "3. Квиток у QA (очікування 5 днів)",
        "4. Квиток у Sec/Ops (очікування 3 дні)",
        "5. Ручний деплой у вікно релізу"
    ]
    for i, st in enumerate(trad_steps):
        sy = 120 + i * 58
        tb, _, _ = textbox(220, sy, st, size=11, pad=8, fill="#ffffff", stroke="#fca5a5", sw=1, min_w=340)
        f.append(tb)
        if i < len(trad_steps) - 1:
            f.append(arrow(220, sy + 18, 220, sy + 38, color=POS, sw=1.5))

    # Стрілка трансформації по центру
    f.append(arrow(425, 255, 465, 255, color=FIELD, sw=3.5))
    f.append(text(445, 235, "Автоматизація", size=11, bold=True, color=FIELD))
    f.append(text(445, 275, "& Контракти", size=11, bold=True, color=FIELD))

    # Правий блок: Сучасна автократична модель (Self-Service + Platform)
    f.append(text(660, 65, "СУЧАСНА МОДЕЛЬ (Stream-Aligned + Platform)", size=13, bold=True, color=FIELD))
    box_modern = rect(480, 85, 370, 340, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8)
    f.append(box_modern)

    modern_steps = [
        "1. Stream-Aligned команда володіє фічею",
        "2. Contract-First (OpenAPI / AsyncAPI stubs)",
        "3. Self-Service DB/Infra через API платформи",
        "4. Автоматичні CI/CD gates (Security & QA)",
        "5. Безперервний автоматичний деплой (CD)"
    ]
    for i, st in enumerate(modern_steps):
        sy = 120 + i * 58
        tb, _, _ = textbox(665, sy, st, size=11, pad=8, fill="#ffffff", stroke="#86efac", sw=1, min_w=330)
        f.append(tb)
        if i < len(modern_steps) - 1:
            f.append(arrow(665, sy + 18, 665, sy + 38, color=FIELD, sw=1.5))

    f.append(text(W / 2, H - 18, "Заміна людей-контролерів автоматизованими контрактами усуває 90% часу міжкомандного очікування", size=11, italic=True, color=MUTED))

    render(os.path.join(IMG, "decoupling-handoffs.svg"), W, H, *f)


if __name__ == '__main__':
    fig_handoff_delay()
    fig_ownership_spectrum()
    fig_decoupling_handoffs()
    print("Всі фігури згенеровано успішно.")
