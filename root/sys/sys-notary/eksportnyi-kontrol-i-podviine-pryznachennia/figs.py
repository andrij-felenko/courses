# -*- coding: utf-8 -*-
"""figs.py — генератор ілюстрацій для теми eksportnyi-kontrol-i-podviine-pryznachennia (sys-notary).
Генерує 2 SVG-схеми в ./img/ за допомогою спільного svgkit.
"""
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)
sys.path.insert(0, os.path.join(SCRIPT_DIR, '..', '..', '..', '..', 'scripts'))
from svgkit import *

os.makedirs(os.path.join(SCRIPT_DIR, "img"), exist_ok=True)


# ── Фігура 1: Дерево рішень експортного контролю ──────────────────────────────
def fig_dual_use_decision_tree():
    W, H = 1000, 620
    P = []
    P.append(text(W / 2, 28, "Дерево ухвалення рішень експортного контролю: ITAR, EAR та EAR99", size=16, bold=True))

    # Крок 1: Військове призначення чи цивільне
    P.append(rect(40, 60, 420, 110, fill="#fef2f2", stroke="#ef4444", sw=1.8, rx=8))
    P.append(text(250, 85, "1. Оцінка юрисдикції: ITAR чи EAR?", size=12.5, bold=True, color="#991b1b"))
    P.append(mtext(250, 110, "Чи розроблено виріб/ПЗ спеціально для військових\nсистем за переліком озброєнь США (USML)?\n(Правило повного контролю «see-through»)", size=10.5, color=INK, lh=1.3))

    # Гілка ТАК -> ITAR
    P.append(arrow(460, 115, 540, 115, color="#dc2626", sw=2))
    P.append(text(500, 105, "ТАК", size=11, bold=True, color="#dc2626"))

    P.append(rect(550, 60, 410, 110, fill="#fee2e2", stroke="#b91c1c", sw=2, rx=8))
    P.append(text(755, 85, "Юрисдикція ITAR (USML / Держдепартамент)", size=12.5, bold=True, color="#7f1d1d"))
    P.append(mtext(755, 110, "• Військовий виріб або компонент зброї / космосу\n• Сувора заборона передачі без ліцензії DDTC\n• Будь-який іноземний доступ = кримінальний злочин", size=10.5, color="#7f1d1d", lh=1.3))

    # Гілка НІ -> EAR
    P.append(arrow(250, 170, 250, 220, color="#2563eb", sw=2))
    P.append(text(275, 195, "НІ", size=11, bold=True, color="#2563eb"))

    # Крок 2: Перевірка CCL (Commerce Control List)
    P.append(rect(40, 220, 420, 110, fill="#eff6ff", stroke="#3b82f6", sw=1.8, rx=8))
    P.append(text(250, 245, "2. Перевірка контрольного списку (CCL)", size=12.5, bold=True, color="#1e40af"))
    P.append(mtext(250, 270, "Чи підпадають параметри виробу під конкретний\n5-значний номер ECCN (наприклад, 3A001, 5A002, 7A002)\nчерез високі інженерні характеристики?", size=10.5, color=INK, lh=1.3))

    # Гілка НІ -> EAR99
    P.append(arrow(460, 275, 540, 275, color="#059669", sw=2))
    P.append(text(500, 265, "НІ", size=11, bold=True, color="#059669"))

    P.append(rect(550, 220, 410, 110, fill="#ecfdf5", stroke="#10b981", sw=2, rx=8))
    P.append(text(755, 245, "Кошик EAR99 (Комерційні вироби)", size=12.5, bold=True, color="#065f46"))
    P.append(mtext(755, 270, "• Товари загального комерційного призначення\n• За замовчуванням експорт без ліцензії (NLR)\n• Перевірка лише ембарго та санкційних списків", size=10.5, color="#065f46", lh=1.3))

    # Гілка ТАК -> ECCN подвійного призначення
    P.append(arrow(250, 330, 250, 380, color="#d97706", sw=2))
    P.append(text(275, 355, "ТАК", size=11, bold=True, color="#d97706"))

    # Крок 3: Аналіз порогових параметрів та винятків
    P.append(rect(40, 380, 420, 110, fill="#fffbeb", stroke="#f59e0b", sw=1.8, rx=8))
    P.append(text(250, 405, "3. Аналіз критеріїв ECCN та винятків", size=12.5, bold=True, color="#92400e"))
    P.append(mtext(250, 430, "• Криптографія: масовий ринок Note 4 / 5A992.c?\n• Температура, АЦП, дрейф гіроскопа, радіація?\n• Чи діють винятки з ліцензування (наприклад, ENC)?", size=10.5, color=INK, lh=1.3))

    # Гілка до Винятків
    P.append(arrow(460, 435, 540, 435, color="#4f46e5", sw=2))
    P.append(text(500, 425, "Виняток", size=10.5, bold=True, color="#4f46e5"))

    P.append(rect(550, 380, 410, 110, fill="#eef2ff", stroke="#6366f1", sw=2, rx=8))
    P.append(text(755, 405, "Винятки з ліцензування (License Exceptions)", size=12.5, bold=True, color="#3730a3"))
    P.append(mtext(755, 430, "• 5A992.c / ENC: споживча криптографія масового ринку\n• LVS (обмежена вартість), TMP (тимчасовий вивіз)\n• Спрощене декларування без індивідуальної ліцензії", size=10.5, color="#3730a3", lh=1.3))

    # Крок 4: Перевірка країни та кінцевого користувача (KYC)
    P.append(arrow(250, 490, 250, 520, color="#475569", sw=2))
    P.append(rect(40, 520, 920, 75, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=8))
    P.append(text(500, 545, "4. Фінальний комплаєнс: Країна (Country Chart) + Кінцевий користувач (Entity List / KYC)", size=12, bold=True, color="#1e293b"))
    P.append(mtext(500, 570, "Перевірка отримувача за базами Denied Persons, Entity List, військового кінцевого використання (MEU)\nРозрахунок правила De Minimis (10% для країн ембарго, 25% загальне) -> Рішення: Ліцензія BIS або NLR", size=10, color=INK, lh=1.25))

    render(os.path.join(SCRIPT_DIR, "img", "dual-use-decision-tree.svg"), W, H, *P)


# ── Фігура 2: Матриця порогових інженерних параметрів ─────────────────────────
def fig_export_compliance_matrix():
    W, H = 1000, 580
    P = []
    P.append(text(W / 2, 28, "Матриця технічних порогових показників експортного контролю (ECCN / CCL)", size=16, bold=True))

    cols = [
        ("Апаратна криптографія", "Категорія 5 (Part 2)", [
            ("Комерційний / Масовий ринок", "Симетрична <= 56 біт,\nасиметрична <= 512 біт.\nЗагальнодоступні протоколи\nTLS/SSH/Wi-Fi (Note 4 / ENC).\nКласифікація: 5A992 / EAR99.", "#ecfdf5", "#059669"),
            ("Подвійне призначення (5A002)", "Апаратні AES-128/256,\nRSA > 512, ECC > 112 біт.\nВласні криптопротоколи,\nприскорювачі шифрування,\nінструменти криптоаналізу.", "#fef2f2", "#dc2626")
        ]),
        ("Швидкодіючі АЦП та ЦАП", "Категорія 3 (3A001.a.5)", [
            ("Стандартні промислові", "Аудіокодеки, промислова\nтелеметрія та вимірювання.\nЧастота < 100 MSPS при 12-16 біт.\nКласифікація: 3A991 / EAR99.", "#ecfdf5", "#059669"),
            ("Високошвидкісні (3A001)", "Частота >= 1 GSPS при\nроздільності ENOB > 10–12 біт.\nБагатоканальні АЦП для SDR,\nрадарів з ФАР та станцій РЕБ.", "#fef2f2", "#dc2626")
        ]),
        ("Температурний діапазон", "Категорія 3 (3A001.a.2)", [
            ("Commercial / Industrial", "Комерційний: 0 °C .. +70 °C\nПромисловий: -40 °C .. +85 °C\nСтандартний кремній для ПЗ\nта побутової електроніки.\nКласифікація: EAR99.", "#ecfdf5", "#059669"),
            ("Military / Space (3A001)", "Повний діапазон:\nвід -55 °C до +125 °C і вище.\nСтійкість до екстремальних\nтермоударів ракетних пусків\nі перевантажень (MIL-STD-883).", "#fef2f2", "#dc2626")
        ]),
        ("Радіаційна стійкість", "Категорія 3 (3A001.a.1)", [
            ("Цивільний кремній", "Звичайні комерційні ІС.\nБез гарантованої стійкості\nдо сумарної дози радіації\n(TID < 5 крад).\nКласифікація: EAR99.", "#ecfdf5", "#059669"),
            ("Rad-Hard (3A001.a.1)", "Сумарна доза (TID):\n> 5×10³ Гр(Si) (500 крад(Si)).\nСтійкість до замикання (SEL)\nпри LET > 80 МеВ·см²/мг.\nКосмічні та військові системи.", "#fef2f2", "#dc2626")
        ]),
        ("MEMS-гіроскопи (IMU)", "Категорія 7 (7A002 / 7A102)", [
            ("Споживчі / Автомобільні", "Дрейф нуля (In-run bias):\n> 5..10 °/год (смартфони, авто).\nНепридатні для тривалого\nавтономного счислення шляху.\nКласифікація: 7A994 / EAR99.", "#ecfdf5", "#059669"),
            ("Навігаційні (7A002/7A102)", "Дрейф нуля < 0.1..0.5 °/год.\nВисока стабільність масштабного\nкоефіцієнта (< 500 ppm).\nАвтономна навігація ракет\nта БПЛА без сигналів GNSS.", "#fef2f2", "#dc2626")
        ])
    ]

    cw = 176
    gap = 14
    x_start = 30

    for i, (col_title, col_sub, cards) in enumerate(cols):
        cx = x_start + i * (cw + gap)

        # Заголовок колонки
        P.append(rect(cx, 60, cw, 55, fill="#f1f5f9", stroke="#94a3b8", sw=1.5, rx=6))
        P.append(text(cx + cw / 2, 80, col_title, size=10.5, bold=True, color="#0f172a"))
        P.append(text(cx + cw / 2, 100, col_sub, size=9.5, color="#64748b"))

        # Картка 1: Цивільний рівень
        top_c = cards[0]
        P.append(rect(cx, 125, cw, 195, fill=top_c[2], stroke=top_c[3], sw=1.5, rx=6))
        P.append(text(cx + cw / 2, 145, top_c[0], size=10, bold=True, color=top_c[3]))
        P.append(mtext(cx + cw / 2, 172, top_c[1], size=9, color=INK, lh=1.3))

        # Картка 2: Подвійне призначення
        bot_c = cards[1]
        P.append(rect(cx, 330, cw, 225, fill=bot_c[2], stroke=bot_c[3], sw=1.8, rx=6))
        P.append(text(cx + cw / 2, 350, bot_c[0], size=10, bold=True, color=bot_c[3]))
        P.append(mtext(cx + cw / 2, 377, bot_c[1], size=9, color=INK, lh=1.3))

    render(os.path.join(SCRIPT_DIR, "img", "export-compliance-matrix.svg"), W, H, *P)


if __name__ == "__main__":
    fig_dual_use_decision_tree()
    fig_export_compliance_matrix()
    print("OK: 2 figures generated in img/")
