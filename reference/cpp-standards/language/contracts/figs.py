# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

MONO = "Consolas, 'DejaVu Sans Mono', monospace"

def mono(x, y, s, size=12, color=INK, anchor="middle", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%s" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))

def monobox(x, y, w, h, lines, size=12, fill=FILL, stroke=LINE, sw=1.5, color=INK,
            lh=1.45, dash=None, anchor="middle"):
    out = rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=8)
    if dash:
        out = ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="8" fill="%s" '
               'stroke="%s" stroke-width="%.1f" stroke-dasharray="%s"/>'
               % (x, y, w, h, fill, stroke, sw, dash))
    n = len(lines)
    cy = y + h / 2 - (n - 1) * size * lh / 2 + size * 0.35
    px = x + w / 2 if anchor == "middle" else x + 16
    for i, ln in enumerate(lines):
        out += mono(px, cy + i * size * lh, ln, size=size, color=color, anchor=anchor)
    return out


# ── 1. Межі контракту: викликач, тіло, повернення та інваріанти ─────────────
def fig_contract_boundary():
    W, H = 1080, 480
    p = []

    # Загальний контур інваріанта класу
    p.append(rect(30, 30, 1020, 420, fill="#f8fafc", stroke=MUTED, sw=1.5, rx=12))
    p.append(text(540, 60, "Інваріант класу / системи (чинний до виклику і після повернення)",
                  size=14, bold=True, color=INK))

    # Ліва колонка: Викликач і преумови
    p.append(rect(60, 90, 280, 330, fill="#eff6ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(200, 120, "Зона викликача (Caller)", size=13.5, bold=True, color=NEG))
    p.append(monobox(75, 145, 250, 80,
                     ["pre: cond_1", "pre [name]: cond_2", "// Обов'язок викликача"],
                     size=11.5, fill="#ffffff", stroke=NEG, sw=1.4, color=NEG, anchor="start"))
    p.append(text(200, 255, "Гарантія на вході:", size=12, bold=True, color=INK))
    p.append(text(200, 280, "Аргументи відповідають", size=11.5, color=INK))
    p.append(text(200, 302, "допустимому діапазону;", size=11.5, color=INK))
    p.append(text(200, 324, "ресурси валідні й готові", size=11.5, color=INK))
    p.append(text(200, 380, "Порушення = помилка викликача", size=11.5, bold=True, color=POS))

    # Стрілка від преумов до тіла
    p.append(arrow(340, 240, 400, 240, color=NEG, sw=2.2))

    # Центральна колонка: Тіло функції
    p.append(rect(400, 90, 280, 330, fill="#ffffff", stroke=LINE, sw=1.8, rx=8))
    p.append(text(540, 120, "Тіло функції (Callee Body)", size=13.5, bold=True, color=INK))
    p.append(monobox(415, 145, 250, 80,
                     ["void compute() {", "  contract_assert: ok;", "  // Внутрішній стан", "}"],
                     size=11.5, fill="#fdfdfe", stroke=LINE, sw=1.4, color=INK, anchor="start"))
    p.append(text(540, 255, "Контрольні точки:", size=12, bold=True, color=INK))
    p.append(text(540, 280, "Перевірка локальних", size=11.5, color=INK))
    p.append(text(540, 302, "інваріантів алгоритму,", size=11.5, color=INK))
    p.append(text(540, 324, "цілісності проміжних даних", size=11.5, color=INK))
    p.append(text(540, 380, "Внутрішній самоконтроль", size=11.5, bold=True, color=MUTED))

    # Стрілка від тіла до постумов
    p.append(arrow(680, 240, 740, 240, color=FIELD, sw=2.2))

    # Права колонка: Функція, що повертає значення, і постумови
    p.append(rect(740, 90, 280, 330, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(880, 120, "Зона результату (Post)", size=13.5, bold=True, color=FIELD))
    p.append(monobox(755, 145, 250, 80,
                     ["post(r): r >= 0", "post: balance() == old", "// Обов'язок реалізації"],
                     size=11.5, fill="#ffffff", stroke=FIELD, sw=1.4, color=FIELD, anchor="start"))
    p.append(text(880, 255, "Гарантія на виході:", size=12, bold=True, color=INK))
    p.append(text(880, 280, "Результат r обчислено вірно;", size=11.5, color=INK))
    p.append(text(880, 302, "стан об'єкта узгоджений;", size=11.5, color=INK))
    p.append(text(880, 324, "ресурси збережено", size=11.5, color=INK))
    p.append(text(880, 380, "Порушення = помилка функції", size=11.5, bold=True, color=POS))

    render(os.path.join(OUT, "contract-boundary.svg"), W, H,
           title="Межі контракту: преумови, твердження та постумови", *p)


# ── 2. Семантика оцінки контрактів (ignore / observe / enforce) ─────────────
def fig_evaluation_semantics():
    W, H = 1080, 520
    p = []

    # Точка входу: оцінка контракту
    p.append(rect(400, 30, 280, 56, fill="#eef2ff", stroke=NEG, sw=1.8, rx=8))
    p.append(text(540, 64, "Точка контракту (pre / post / assert)", size=13, bold=True, color=NEG))

    # Стрілки вниз до трьох режимів
    p.append(arrow(470, 86, 180, 130, color=MUTED, sw=1.6))
    p.append(arrow(540, 86, 540, 130, color=MUTED, sw=1.6))
    p.append(arrow(610, 86, 900, 130, color=MUTED, sw=1.6))

    # Режим 1: IGNORE
    p.append(rect(50, 130, 260, 90, fill="#f8fafc", stroke=MUTED, sw=1.6, rx=8))
    p.append(text(180, 160, "Режим: ignore", size=13, bold=True, color=INK))
    p.append(text(180, 185, "Предикат НЕ обчислюється.", size=11.5, color=MUTED))
    p.append(text(180, 205, "0 тактів CPU, без перевірок", size=11, color=MUTED))

    # Стрілка від IGNORE прямо до продовження
    p.append(arrow(180, 220, 180, 440, color=FIELD, sw=1.8))

    # Режим 2: OBSERVE
    p.append(rect(410, 130, 260, 90, fill="#fffbeb", stroke="#d97706", sw=1.6, rx=8))
    p.append(text(540, 160, "Режим: observe", size=13, bold=True, color="#b45309"))
    p.append(text(540, 185, "Предикат обчислюється.", size=11.5, color=INK))
    p.append(text(540, 205, "Логування порушень", size=11, color=MUTED))

    # Режим 3: ENFORCE
    p.append(rect(770, 130, 260, 90, fill="#fef2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(900, 160, "Режим: enforce", size=13, bold=True, color=POS))
    p.append(text(900, 185, "Предикат обчислюється.", size=11.5, color=INK))
    p.append(text(900, 205, "Жорсткий контроль аварій", size=11, color=POS))

    # Блок обчислення для OBSERVE та ENFORCE
    p.append(arrow(540, 220, 540, 260, color=LINE, sw=1.6))
    p.append(arrow(900, 220, 900, 260, color=LINE, sw=1.6))

    p.append(rect(470, 260, 500, 50, fill="#f4f6f8", stroke=LINE, sw=1.4, rx=6))
    p.append(text(720, 290, "Предикат хибний (cond == false)?", size=12.5, bold=True, color=INK))

    # Якщо предикат істинний
    p.append(arrow(470, 285, 230, 440, color=FIELD, sw=1.6))
    p.append(text(330, 340, "cond == true", size=11, color=FIELD, bold=True))

    # Якщо предикат хибний -> Виклик Violation Handler
    p.append(arrow(720, 310, 720, 350, color=POS, sw=2.0))
    p.append(rect(470, 350, 500, 56, fill="#fef2f2", stroke=POS, sw=1.8, rx=8))
    p.append(text(720, 374, "Обробник порушень: handle_contract_violation()", size=12, bold=True, color=POS))
    p.append(text(720, 394, "Отримує std::contracts::contract_violation (файл, рядок, предикат)", size=10.5, color=MUTED))

    # Вихід із Violation Handler: observe -> продовжити, enforce -> terminate
    p.append(arrow(570, 406, 570, 440, color="#d97706", sw=1.8))
    p.append(arrow(870, 406, 870, 440, color=POS, sw=2.0))

    # Фінальні блоки
    p.append(rect(80, 440, 530, 50, fill="#f0fdf4", stroke=FIELD, sw=1.8, rx=8))
    p.append(text(345, 470, "Продовження виконання нормального потоку інструкцій", size=12, bold=True, color=FIELD))

    p.append(rect(750, 440, 240, 50, fill="#fef2f2", stroke=POS, sw=2.2, rx=8))
    p.append(text(870, 470, "std::terminate()", size=13, bold=True, color=POS))

    render(os.path.join(OUT, "evaluation-semantics.svg"), W, H,
           title="Семантика оцінки контрактів у C++26", *p)


# ── 3. Порівняння архітектури C++20 (P0542) та C++26 (P2900) ─────────────────
def fig_p0542_vs_p2900():
    W, H = 1080, 460
    p = []

    # Розділювач
    p.append(line(540, 30, 540, 430, color=MUTED, sw=1.4, dash="6 5"))

    # Ліва половина: C++20 P0542 (відхилено)
    p.append(rect(40, 30, 460, 400, fill="#fdf7f7", stroke=POS, sw=1.6, rx=10))
    p.append(text(270, 65, "Спроба C++20: P0542 (відхилено)", size=14, bold=True, color=POS))

    p.append(monobox(60, 90, 420, 66,
                     ["[[expects: x > 0]]", "[[ensures r: r >= 0]]", "[[assert: p != nullptr]]"],
                     size=11.5, fill="#ffffff", stroke=POS, sw=1.4, color=POS, anchor="start"))

    p.append(text(270, 185, "Проблеми та суперечності:", size=12.5, bold=True, color=INK))
    p.append(text(80, 215, "• Синтаксис атрибутів [[...]] — конфлікт семантики", size=11, color=INK, anchor="start"))
    p.append(text(80, 240, "• Рівні побудови: default / audit / axiom", size=11, color=INK, anchor="start"))
    p.append(text(80, 265, "• Небезпека UB: невиконаний контракт як припущення", size=11, color=POS, bold=True, anchor="start"))
    p.append(text(80, 290, "  компілятора (оптимізатор видаляє перевірки безпеки)", size=10.5, color=POS, anchor="start"))
    p.append(text(80, 315, "• Невизначеність щодо обробника порушень", size=11, color=INK, anchor="start"))
    p.append(text(80, 340, "• Розкол у комітеті в Кельні (2019) → вилучено", size=11, color=MUTED, anchor="start"))
    p.append(text(270, 400, "Підсумок: відсутність консенсусу, ризик UB", size=11.5, bold=True, color=POS))

    # Права половина: C++26 P2900 (прийнято)
    p.append(rect(580, 30, 460, 400, fill="#f6fbf7", stroke=FIELD, sw=1.6, rx=10))
    p.append(text(810, 65, "Консенсус C++26: P2900 (SG21)", size=14, bold=True, color=FIELD))

    p.append(monobox(600, 90, 420, 66,
                     ["pre: x > 0", "post(r): r >= 0", "contract_assert: p != nullptr"],
                     size=11.5, fill="#ffffff", stroke=FIELD, sw=1.4, color=FIELD, anchor="start"))

    p.append(text(810, 185, "Ключові досягнення консенсусу:", size=12.5, bold=True, color=INK))
    p.append(text(600, 215, "• Прямий синтаксис (першокласні елементи мови)", size=11, color=INK, anchor="start"))
    p.append(text(600, 240, "• Чіткі семантики: ignore / observe / enforce", size=11, color=INK, anchor="start"))
    p.append(text(600, 265, "• Жодного прихованого UB в режимі ignore:", size=11, color=FIELD, bold=True, anchor="start"))
    p.append(text(600, 290, "  контракт не перетворюється на небезпечну аксіому", size=10.5, color=FIELD, anchor="start"))
    p.append(text(600, 315, "• Стандартизований заголовок <contracts>", size=11, color=INK, anchor="start"))
    p.append(text(600, 340, "• Керований std::contracts::contract_violation", size=11, color=INK, anchor="start"))
    p.append(text(810, 400, "Підсумок: надійність інтерфейсів без дірок в оптимізації", size=11.5, bold=True, color=FIELD))

    render(os.path.join(OUT, "p0542-vs-p2900.svg"), W, H,
           title="Порівняння підходів P0542 та P2900", *p)


if __name__ == "__main__":
    fig_contract_boundary()
    fig_evaluation_semantics()
    fig_p0542_vs_p2900()
    print("Figures generated successfully in", OUT)
