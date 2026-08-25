# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

WARN_FILL, WARN_STROKE = "#fff6e0", "#caa24a"
GOOD_FILL, GOOD_STROKE = "#eef6ef", FIELD
NEW_FILL, NEW_STROKE = "#eaf0fd", NEG
ERR_FILL, ERR_STROKE = "#fdecea", POS
PURPLE_FILL, PURPLE_STROKE = "#f5eefb", "#7d3c98"


# ── 1. Спектр ідентифікованості та класифікація атрибутів ───────────────────────
def fig_taxonomy_continuum():
    W, H = 820, 360
    p = []
    
    # 4 колонки: Прямі PII, Квазі-ідентифікатори, Чутливі дані, Неідентифіковні дані
    cols = [
        ("Прямі ідентифікатори (PII)",
         "• Номер паспорта / РНОКПП\n• Адреса ел. пошти\n• Номер банківської картки\n• ПІБ, біометричний зліпок\n\nРизик: однозначна ідентифікація\nМетод: токенізація, хешування",
         ERR_FILL, ERR_STROKE, POS),
        ("Квазі-ідентифікатори (QI)",
         "• Поштовий індекс (ZIP)\n• Дата народження, вік\n• Стать, посада, місто\n• Часова мітка транзакції\n\nРизик: атака зведенням (Linkage)\nМетод: k-анонімність, узагальнення",
         WARN_FILL, WARN_STROKE, "#9a6700"),
        ("Чутливі атрибути (Sensitive)",
         "• Медичний діагноз / рецепт\n• Рівень доходу / баланс\n• Політичні / релігійні погляди\n• Генетичні / судові дані\n\nРизик: дискримінація, шкода\nМетод: l-різноманітність, шифрування",
         PURPLE_FILL, PURPLE_STROKE, "#5b2c6f"),
        ("Неідентифіковні дані",
         "• Агреговані лічильники\n• Узагальнені діапазони\n• Системні логи без ID\n• Статистичні зведення\n\nРизик: мінімальний (без фону)\nМетод: диференційна приватність",
         GOOD_FILL, GOOD_STROKE, FIELD)
    ]
    
    bw = 180
    bh = 270
    xs = [20, 220, 420, 620]
    y_top = 45
    
    for i, (hdr, desc, fill_c, strk_c, txt_c) in enumerate(cols):
        bx = xs[i]
        p.append(rect(bx, y_top, bw, bh, fill=fill_c, stroke=strk_c, sw=1.5, rx=6))
        p.append(text(bx + bw / 2, y_top + 22, hdr, size=11, color=txt_c, bold=True))
        p.append(line(bx + 8, y_top + 34, bx + bw - 8, y_top + 34, color=strk_c, sw=0.8))
        
        lines = desc.split("\n")
        curr_y = y_top + 52
        for ln in lines:
            if not ln.strip():
                curr_y += 8
                continue
            is_hdr_line = ln.startswith("Ризик:") or ln.startswith("Метод:")
            clr = txt_c if is_hdr_line else INK
            is_bold = is_hdr_line
            p.append(text(bx + 12, curr_y, ln, size=10, color=clr, anchor="start", bold=is_bold))
            curr_y += 16
            
    # Нижня стрілка градієнта ідентифікуючої сили
    p.append(arrow(780, 335, 40, 335, color=POS, sw=2))
    p.append(text(410, 350, "Зростання однозначності прямої ідентифікації особи", size=11, color=POS, bold=True))
    
    return render(os.path.join(OUT, "taxonomy-continuum.svg"), W, H, *p)


# ── 2. Анатомія атаки зведенням (Linkage Attack) ───────────────────────────────
def fig_linkage_attack():
    W, H = 820, 380
    p = []
    
    # Ліва таблиця: Відкритий реєстр виборців
    p.append(rect(20, 30, 300, 200, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(rect(20, 30, 300, 32, fill=NEW_FILL, stroke=NEW_STROKE, sw=1.5, rx=6))
    p.append(text(170, 52, "Публічний реєстр виборців", size=12, color=NEG, bold=True))
    
    p.append(text(35, 80, "ПІБ", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(125, 80, "Індекс", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(180, 80, "Дата нар.", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(270, 80, "Стать", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(line(25, 90, 315, 90, color="#d0d7de", sw=1))
    
    voter_rows = [
        ("Вільям Велд", "02138", "1945-07-31", "Ч", True),
        ("Джон Сміт", "02138", "1960-03-12", "Ч", False),
        ("Еліс Браун", "02139", "1975-11-04", "Ж", False),
        ("Марія Дейвіс", "02138", "1982-08-22", "Ж", False)
    ]
    for i, (name, zip_c, dob, sex, target) in enumerate(voter_rows):
        ry = 110 + i * 28
        if target:
            p.append(rect(22, ry - 14, 296, 24, fill=ERR_FILL, stroke=ERR_STROKE, sw=1.2, rx=4))
        p.append(text(35, ry, name, size=10, color=POS if target else INK, bold=target, anchor="start"))
        p.append(text(125, ry, zip_c, size=10, color=POS if target else INK, bold=target, anchor="start"))
        p.append(text(180, ry, dob, size=10, color=POS if target else INK, bold=target, anchor="start"))
        p.append(text(270, ry, sex, size=10, color=POS if target else INK, bold=target, anchor="start"))

    # Права таблиця: «Знеособлені» медичні картки GIC
    p.append(rect(500, 30, 300, 200, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(rect(500, 30, 300, 32, fill=WARN_FILL, stroke=WARN_STROKE, sw=1.5, rx=6))
    p.append(text(650, 52, "«Знеособлені» медичні дані GIC", size=12, color="#9a6700", bold=True))
    
    p.append(text(515, 80, "Індекс", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(570, 80, "Дата нар.", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(650, 80, "Стать", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(710, 80, "Діагноз", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(line(505, 90, 795, 90, color="#d0d7de", sw=1))
    
    med_rows = [
        ("02139", "1975-11-04", "Ж", "Астма", False),
        ("02138", "1945-07-31", "Ч", "Діабет-II", True),
        ("02138", "1980-05-19", "Ч", "Гіпертонія", False),
        ("02142", "1960-03-12", "Ж", "Артрит", False)
    ]
    for i, (zip_c, dob, sex, diag, target) in enumerate(med_rows):
        ry = 110 + i * 28
        if target:
            p.append(rect(502, ry - 14, 296, 24, fill=ERR_FILL, stroke=ERR_STROKE, sw=1.2, rx=4))
        p.append(text(515, ry, zip_c, size=10, color=POS if target else INK, bold=target, anchor="start"))
        p.append(text(570, ry, dob, size=10, color=POS if target else INK, bold=target, anchor="start"))
        p.append(text(650, ry, sex, size=10, color=POS if target else INK, bold=target, anchor="start"))
        p.append(text(710, ry, diag, size=10, color=POS if target else INK, bold=target, anchor="start"))

    # Центральна область: зведення за квазі-ідентифікатором
    p.append(rect(340, 95, 140, 75, fill=ERR_FILL, stroke=ERR_STROKE, sw=1.5, rx=6))
    p.append(text(410, 115, "ЗВЕДЕННЯ (JOIN)", size=11, color=POS, bold=True))
    p.append(text(410, 132, "Квазі-ID тріада:", size=9, color=INK))
    p.append(text(410, 148, "(02138, 1945-07-31, Ч)", size=9, color=POS, bold=True))
    p.append(text(410, 162, "Унікальний збіг (1:1)", size=9, color=POS))
    
    p.append(arrow(320, 135, 340, 135, color=POS, sw=1.5))
    p.append(arrow(500, 135, 480, 135, color=POS, sw=1.5))
    
    # Нижній блок: Результат атаки
    p.append(rect(140, 260, 540, 95, fill=ERR_FILL, stroke=ERR_STROKE, sw=1.5, rx=6))
    p.append(text(410, 285, "РЕЗУЛЬТАТ ДЕАНОНІМІЗАЦІЇ", size=13, color=POS, bold=True))
    p.append(text(410, 310, "Губернатор Вільям Велд = (02138, 1945-07-31, Ч) = Діагноз: Діабет-II", size=11, color=POS, bold=True))
    p.append(text(410, 335, "Видалення ПІБ не захищає: 87% громадян США однозначно визначаються тріадою (ZIP, DOB, Sex)", size=10, color=INK))
    
    p.append(arrow(410, 170, 410, 255, color=POS, sw=1.8))
    
    return render(os.path.join(OUT, "linkage-attack-anatomy.svg"), W, H, *p)


# ── 3. Трансформація таблиці: Генералізація до k-анонімності та l-різноманітності ─
def fig_k_anonymity():
    W, H = 820, 390
    p = []
    
    # Ліва таблиця: Сирі дані (k=1, вразливі)
    p.append(rect(20, 30, 370, 300, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(rect(20, 30, 370, 32, fill=ERR_FILL, stroke=ERR_STROKE, sw=1.5, rx=6))
    p.append(text(205, 52, "Сирі дані (k=1: кожен рядок унікальний)", size=11, color=POS, bold=True))
    
    p.append(text(35, 80, "Індекс", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(105, 80, "Вік", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(160, 80, "Стать", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(225, 80, "Діагноз (чутливий)", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(line(25, 90, 385, 90, color="#d0d7de", sw=1))
    
    raw_data = [
        ("02138", "29", "Ч", "Грип"),
        ("02139", "25", "Ч", "Астма"),
        ("02138", "27", "Ж", "Гастрит"),
        ("02142", "43", "Ж", "Діабет"),
        ("02141", "48", "Ж", "Гіпертонія"),
        ("02142", "45", "Ч", "Артрит"),
        ("02215", "62", "Ч", "Ішемія"),
        ("02215", "67", "Ж", "Інсульт")
    ]
    for i, (zc, age, sx, dg) in enumerate(raw_data):
        ry = 112 + i * 25
        p.append(text(35, ry, zc, size=10, color=INK, anchor="start"))
        p.append(text(105, ry, age, size=10, color=INK, anchor="start"))
        p.append(text(160, ry, sx, size=10, color=INK, anchor="start"))
        p.append(text(225, ry, dg, size=10, color=POS, anchor="start"))
        
    # Права таблиця: Анонімізовані дані (k=3, l=2)
    p.append(rect(430, 30, 370, 300, fill="#ffffff", stroke="#d0d7de", sw=1.5, rx=6))
    p.append(rect(430, 30, 370, 32, fill=GOOD_FILL, stroke=GOOD_STROKE, sw=1.5, rx=6))
    p.append(text(615, 52, "Узагальнення: 3-анонімність та 3-різноманітність", size=11, color=FIELD, bold=True))
    
    p.append(text(445, 80, "Індекс", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(515, 80, "Вік", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(570, 80, "Стать", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(text(635, 80, "Діагноз (l ≥ 2)", size=10, color=MUTED, bold=True, anchor="start"))
    p.append(line(435, 90, 795, 90, color="#d0d7de", sw=1))
    
    # Клас 1: 0213*, 20-29
    p.append(rect(432, 95, 366, 75, fill="#f4fbf5", stroke=FIELD, sw=1, rx=4))
    anon_c1 = [
        ("0213*", "20–29", "*", "Грип"),
        ("0213*", "20–29", "*", "Астма"),
        ("0213*", "20–29", "*", "Гастрит")
    ]
    for i, (zc, age, sx, dg) in enumerate(anon_c1):
        ry = 112 + i * 24
        p.append(text(445, ry, zc, size=10, color=FIELD, bold=True, anchor="start"))
        p.append(text(515, ry, age, size=10, color=FIELD, bold=True, anchor="start"))
        p.append(text(570, ry, sx, size=10, color=FIELD, bold=True, anchor="start"))
        p.append(text(635, ry, dg, size=10, color=INK, anchor="start"))

    # Клас 2: 0214*, 40-49
    p.append(rect(432, 175, 366, 75, fill="#f4fbf5", stroke=FIELD, sw=1, rx=4))
    anon_c2 = [
        ("0214*", "40–49", "*", "Діабет"),
        ("0214*", "40–49", "*", "Гіпертонія"),
        ("0214*", "40–49", "*", "Артрит")
    ]
    for i, (zc, age, sx, dg) in enumerate(anon_c2):
        ry = 192 + i * 24
        p.append(text(445, ry, zc, size=10, color=FIELD, bold=True, anchor="start"))
        p.append(text(515, ry, age, size=10, color=FIELD, bold=True, anchor="start"))
        p.append(text(570, ry, sx, size=10, color=FIELD, bold=True, anchor="start"))
        p.append(text(635, ry, dg, size=10, color=INK, anchor="start"))
        
    # Придушений рядок (Suppressed)
    p.append(rect(432, 255, 366, 50, fill=WARN_FILL, stroke=WARN_STROKE, sw=1, rx=4))
    p.append(text(445, 275, "* (придушено)", size=10, color="#9a6700", bold=True, anchor="start"))
    p.append(text(515, 275, "*", size=10, color="#9a6700", anchor="start"))
    p.append(text(570, 275, "*", size=10, color="#9a6700", anchor="start"))
    p.append(text(635, 275, "Рядки віку 60+ вилучено (N=2 < 3)", size=9, color="#9a6700", anchor="start"))

    # Стрілка між таблицями
    p.append(arrow(395, 180, 425, 180, color=FIELD, sw=2))
    
    # Нижній підсумок
    p.append(rect(20, 345, 780, 35, fill="#f8fafc", stroke="#cbd5e1", sw=1.2, rx=6))
    p.append(text(410, 367, "Інваріант: кожен кортеж квазі-ID розділяють ≥ 3 особи; кожен клас містить ≥ 3 різні хвороби", size=10, color=INK, bold=True))
    
    return render(os.path.join(OUT, "k-anonymity-generalization.svg"), W, H, *p)


# ── 4. Конвеєр класифікації, токенізації та динамічного маскування ─────────────
def fig_pipeline_architecture():
    W, H = 820, 370
    p = []
    
    # 5 блоків конвеєра:
    # 1. Вхідний потік -> 2. Інспекція схем -> 3. Vault / HMAC Токенізація -> 4. Зашифроване сховище -> 5. Gateway маскування
    blocks = [
        ("1. Вхідний запис", "Raw JSON / SQL Row\n• Email, ІПН, Картка\n• Вік, ZIP, Діагноз\n(Відкритий текст)", "#ffffff", "#d0d7de", INK),
        ("2. Класифікатор схем", "Розмітка атрибутів:\n• DIRECT_PII\n• QUASI_ID\n• SENSITIVE_DATA", NEW_FILL, NEW_STROKE, NEG),
        ("3. Токенізатор / FPE", "Псевдонімізація:\n• HMAC-SHA256(Email)\n• FPE(CardNumber)\n• Сховище відповідностей", PURPLE_FILL, PURPLE_STROKE, "#5b2c6f"),
        ("4. Безпечне сховище", "База даних / Data Lake\n• Токени замість PII\n• Шифрування чутливих\n• Ізольований ключ", GOOD_FILL, GOOD_STROKE, FIELD),
        ("5. Шлюз вибірки", "Динамічне маскування:\n• Адмін -> повний доступ\n• Аналітик -> jo***@dom.com\n• Аудит -> лише токени", WARN_FILL, WARN_STROKE, "#9a6700")
    ]
    
    bw = 140
    bh = 135
    xs = [15, 175, 335, 495, 655]
    y_box = 50
    
    for i, (hdr, desc, fill_c, strk_c, txt_c) in enumerate(blocks):
        bx = xs[i]
        p.append(rect(bx, y_box, bw, bh, fill=fill_c, stroke=strk_c, sw=1.5, rx=6))
        p.append(text(bx + bw / 2, y_box + 20, hdr, size=10, color=txt_c, bold=True))
        p.append(line(bx + 6, y_box + 30, bx + bw - 6, y_box + 30, color=strk_c, sw=0.8))
        
        lines = desc.split("\n")
        for l_idx, ln in enumerate(lines):
            p.append(text(bx + bw / 2, y_box + 48 + l_idx * 16, ln, size=9, color=INK))
            
        if i < 4:
            p.append(arrow(bx + bw + 2, y_box + bh / 2, xs[i+1] - 4, y_box + bh / 2, color=LINE, sw=1.5))
            
    # Нижній блок: Керування ключами та політиками
    p.append(rect(175, 230, 460, 110, fill="#f8fafc", stroke="#64748b", sw=1.5, rx=6))
    p.append(text(405, 255, "ПЛОЩИНА КЕРУВАННЯ ТА БЕЗПЕКИ (HSM / POLICY REGISTRY)", size=11, color=INK, bold=True))
    p.append(line(190, 267, 620, 267, color="#cbd5e1", sw=1))
    
    p.append(text(405, 287, "• Ротація перцю і солі (Pepper/Salt) кожні 90 днів для детермінованих токенів", size=9, color=MUTED))
    p.append(text(405, 305, "• Знищення ключів користувача (Crypto-Shredding) за запитом на видалення (GDPR Art. 17)", size=9, color=MUTED))
    p.append(text(405, 323, "• RBAC/ABAC політики для розкриття демаскованих значень через Audit Trail", size=9, color=MUTED))
    
    p.append(arrow(335 + bw/2, 230, 335 + bw/2, y_box + bh + 4, color="#64748b", sw=1.4))
    p.append(arrow(495 + bw/2, 230, 495 + bw/2, y_box + bh + 4, color="#64748b", sw=1.4))
    
    return render(os.path.join(OUT, "tokenization-masking-pipeline.svg"), W, H, *p)


if __name__ == "__main__":
    fig_taxonomy_continuum()
    fig_linkage_attack()
    fig_k_anonymity()
    fig_pipeline_architecture()
    print("Figures generated successfully.")
