# -*- coding: utf-8 -*-
"""Фігури для теми koly-tvii-vyrib-uzhe-klonuvaly.
svgkit імпортуємо зі scripts/, вивід у ./img/

    python figs.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *  # noqa: E402,F403

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── 1. clone-vectors: джерела витоку і бар'єр захисту ─────────────────────────
def fig_clone_vectors():
    W, H = 760, 330
    p = []

    # Тло двох зон: вразливе залізо і захищена екосистема
    p.append(rect(20, 20, 340, 290, fill="#fff5f5", stroke="#e0b4b4", sw=1.2, rx=8))
    p.append(rect(400, 20, 340, 290, fill="#f0f9f4", stroke="#a3d9b8", sw=1.2, rx=8))

    p.append(text(190, 46, "Вразливий рівень: голе залізо", size=12, color=POS, bold=True))
    p.append(text(570, 46, "Стійкий рівень: екосистема і криптографія", size=12, color=FIELD, bold=True))

    # Картки ліворуч (де залізо копіюють) - один textbox на картку, щоб не було перекриття rect
    cards_left = [
        (190, 100, "1. Витік з фабрики (Gerber / BOM)\nФабрика виготовляє «третю зміну»\nза вашою оригінальною топологією"),
        (190, 175, "2. Реверс друкованої плати\nПошарове шліфування, рентген,\nвідтворення схеми й трасування"),
        (190, 250, "3. Зчитування Flash / пам'яті\nДамп незахищеного мікроконтролера\nі пряме заливання коду в клон"),
    ]
    for cx, cy, text_content in cards_left:
        b, _, _ = textbox(cx, cy, text_content, size=10, color=INK, fill="#ffffff", stroke="#d99b9b", sw=1.0, min_w=310)
        p.append(b)

    # Картки праворуч (що клонери не можуть просто скопіювати)
    cards_right = [
        (570, 100, "1. Апаратний корінь (Secure Element)\nУнікальні приватні ключі на екземпляр,\nфізично недоступні для зчитування"),
        (570, 175, "2. Віддалена атестація у хмарі\nБекенд перевіряє криптопідпис сесії,\nмиттєво відсікаючи дублікати ключів"),
        (570, 250, "3. Регулярні сервіси та оновлення\nХмарні функції, аналітика, OTA,\nгарантія, сервіс і технічна підтримка"),
    ]
    for cx, cy, text_content in cards_right:
        b, _, _ = textbox(cx, cy, text_content, size=10, color=INK, fill="#ffffff", stroke="#8cd1a4", sw=1.0, min_w=310)
        p.append(b)

    # Стрілка між зонами
    p.append(arrow(362, 165, 396, 165, color=MUTED, sw=2.0))

    render(os.path.join(OUT, "clone-vectors.svg"), W, H, *p,
           title="Шляхи копіювання заліза та перенесення захисту на рівень екосистеми")


# ── 2. cloud-attestation-gate: фільтрація пристроїв на бекенді ─────────────────
def fig_cloud_attestation_gate():
    W, H = 760, 340
    p = []

    # Пристрої зліва
    # Оригінал
    b_orig, _, _ = textbox(110, 80, "Оригінальний пристрій\nУнікальний ключ у Secure Element\nВалідний ланцюг сертифікатів",
                           size=10, bold=False, color=FIELD, fill="#f0faf4", stroke=FIELD, sw=1.4, min_w=180)
    p.append(b_orig)

    # Клон
    b_clone, _, _ = textbox(110, 240, "Клонований пристрій\nСкопійований спільний ключ / MAC\nДублікат сертифіката чи ID",
                            size=10, bold=False, color=POS, fill="#fdf2f2", stroke=POS, sw=1.4, min_w=180)
    p.append(b_clone)

    # Центральний шлюз (Бекенд)
    p.append(rect(270, 30, 220, 280, fill="#f4f6f8", stroke=LINE, sw=1.5, rx=8))
    p.append(text(380, 58, "Хмарний шлюз автентифікації", size=11, bold=True, color=INK))

    p.append(rect(285, 80, 190, 48, fill="#ffffff", stroke="#b0bec5", sw=1.0, rx=4))
    p.append(text(380, 100, "1. Перевірка mTLS", size=10, bold=True, color=INK))
    p.append(text(380, 116, "Сертифікат у довіреному CA?", size=9, color=MUTED))

    p.append(rect(285, 145, 190, 52, fill="#ffffff", stroke="#b0bec5", sw=1.0, rx=4))
    p.append(text(380, 164, "2. Крипточелендж", size=10, bold=True, color=INK))
    p.append(text(380, 180, "Підпис випадкового nonce", size=9, color=MUTED))
    p.append(text(380, 192, "захищеним ключем", size=9, color=MUTED))

    p.append(rect(285, 215, 190, 52, fill="#ffffff", stroke="#b0bec5", sw=1.0, rx=4))
    p.append(text(380, 234, "3. Аналіз аномалій", size=10, bold=True, color=INK))
    p.append(text(380, 250, "Колізії UUID, географія IP,", size=9, color=MUTED))
    p.append(text(380, 262, "частота сесій та запитів", size=9, color=MUTED))

    # Стрілки від пристроїв до шлюзу
    p.append(arrow(202, 80, 268, 80, color=FIELD, sw=1.5))
    p.append(text(235, 70, "mTLS", size=9, color=FIELD, bold=True))

    p.append(arrow(202, 240, 268, 240, color=POS, sw=1.5))
    p.append(text(235, 230, "Запит", size=9, color=POS, bold=True))

    # Виходи праворуч
    # Зелений вихід (Повний доступ)
    b_ok, _, _ = textbox(630, 80, "Повний доступ до сервісів\n• Хмарні обчислення та сховище\n• Оновлення прошивки (OTA)\n• Гарантійна підтримка",
                         size=10, bold=False, color=FIELD, fill="#e8f8f0", stroke=FIELD, sw=1.4, min_w=200)
    p.append(b_ok)
    p.append(arrow(492, 80, 528, 80, color=FIELD, sw=1.5))

    # Жовтий / червоний вихід (Деградація або блокування)
    b_bad, _, _ = textbox(630, 240, "Керована деградація / бан\n• Базовий режим без аналітики\n• Повідомлення про неоригінальність\n• Відхилення від хмарних функцій",
                          size=10, bold=False, color=POS, fill="#fff2f2", stroke=POS, sw=1.4, min_w=200)
    p.append(b_bad)
    p.append(arrow(492, 240, 528, 240, color=POS, sw=1.5))

    render(os.path.join(OUT, "cloud-attestation-gate.svg"), W, H, *p,
           title="Схема криптографічної атестації та відсікання клонованих пристроїв на бекенді")


# ── 3. legal-levers: юридичні інструменти захисту ─────────────────────────────
def fig_legal_levers():
    W, H = 760, 320
    p = []

    levers = [
        (105, "1. DMCA / Takedown", "Швидкість: 2–7 днів\nВартість: низька\nОб'єкт: фото, лого,\nкопія сторінки,\nпрямий дамп коду", FIELD, "#f0faf4"),
        (285, "2. Торговельні марки", "Швидкість: 1–3 тижні\nВартість: середня\nОб'єкт: назва, бренд,\nлоготип на корпусі чи\nв описі товару", "#2457d6", "#f0f4ff"),
        (470, "3. Митний реєстр", "Швидкість: 1–2 місяці\nВартість: середня\nОб'єкт: зупинення\nфізичних партій\nна кордоні імпорту", "#d97706", "#fffbeb"),
        (650, "4. Судовий позов", "Швидкість: 1–3 роки\nВартість: висока\nОб'єкт: патенти,\nвідшкодування збитків,\nзаборона продажів", POS, "#fdf2f2"),
    ]

    for cx, title, body, col, fill in levers:
        ht, _, _ = textbox(cx, 45, title, size=11, bold=True, color=col, fill=fill, stroke=col, sw=1.4, min_w=160)
        p.append(ht)
        bt, _, _ = textbox(cx, 160, body, size=10, color=INK, fill="#ffffff", stroke="#c9d3dc", sw=1.0, min_w=160)
        p.append(bt)

    p.append(line(30, 250, 730, 250, color=MUTED, sw=1.2))
    p.append(arrow(30, 275, 730, 275, color=MUTED, sw=1.4))
    p.append(text(40, 295, "Найшвидші та найдешевші важелі (онлайн-блокування)", size=10, color=FIELD, anchor="start", bold=True))
    p.append(text(720, 295, "Найдовші та найдорожчі (судові справи)", size=10, color=POS, anchor="end", bold=True))

    render(os.path.join(OUT, "legal-levers.svg"), W, H, *p,
           title="Юридичні інструменти захисту від копіювання за швидкістю та витратами")


# ── 4. response-matrix: матриця реакцій на клонування ─────────────────────────
def fig_response_matrix():
    W, H = 760, 320
    p = []

    # 4 квадранти
    # Верхній лівий: Нескінченна гонка заліза
    p.append(rect(30, 30, 335, 125, fill="#fffbf0", stroke="#e0c285", sw=1.2, rx=6))
    p.append(text(197, 55, "Гонка озброєнь у залізі (помилка)", size=11, bold=True, color="#b45309"))
    p.append(text(197, 78, "Постійні дрібні зміни плати без криптографії.", size=10, color=INK))
    p.append(text(197, 96, "Клонери повторюють ревізію за 2–4 тижні.", size=10, color=INK))
    p.append(text(197, 114, "Витрати R&D не окупаються.", size=10, color=POS, italic=True))

    # Верхній правий: Системний захист (Правильна стратегія)
    p.append(rect(395, 30, 335, 125, fill="#f0faf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(562, 55, "Системний підхід (стратегія успіху)", size=11, bold=True, color=FIELD))
    p.append(text(562, 78, "Апаратні ключі + хмарна атестація сесій.", size=10, color=INK))
    p.append(text(562, 96, "Юридичні блокування на маркетплейсах.", size=10, color=INK))
    p.append(text(562, 114, "Цінність у софті, сервісах та спільноті.", size=10, color=FIELD, bold=True))

    # Нижній лівий: Пасивне ігнорування
    p.append(rect(30, 170, 335, 125, fill="#f4f6f8", stroke="#b0bec5", sw=1.2, rx=6))
    p.append(text(197, 195, "Пасивне ігнорування (ризик)", size=11, bold=True, color=MUTED))
    p.append(text(197, 218, "Відсутність моніторингу та захисту бренду.", size=10, color=INK))
    p.append(text(197, 236, "Клони витісняють оригінал низькою ціною.", size=10, color=INK))
    p.append(text(197, 254, "Втрата репутації через ненадійні підробки.", size=10, color=POS, italic=True))

    # Нижній правий: Деструктивна помста (FTDIgate)
    p.append(rect(395, 170, 335, 125, fill="#fdf2f2", stroke=POS, sw=1.5, rx=6))
    p.append(text(562, 195, "Деструктивні контрзаходи / Bricking (табу)", size=11, bold=True, color=POS))
    p.append(text(562, 218, "Навмисне спалення чіпів чи стирання EEPROM.", size=10, color=INK))
    p.append(text(562, 236, "Ураження кінцевих користувачів (false positives).", size=10, color=INK))
    p.append(text(562, 254, "Репутаційна катастрофа та судові ризики.", size=10, color=POS, bold=True))

    render(os.path.join(OUT, "response-matrix.svg"), W, H, *p,
           title="Матриця стратегій реакції на появу клонованого пристрою")


def main():
    fig_clone_vectors()
    fig_cloud_attestation_gate()
    fig_legal_levers()
    fig_response_matrix()
    print("Всі 4 фігури згенеровано успішно.")


if __name__ == "__main__":
    main()
