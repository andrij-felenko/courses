# -*- coding: utf-8 -*-
import sys, os

# 4 levels up to scripts/ from book/programming/languages/preprocessor-macros
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. translation-phases.svg ──────────────────────────────────────────────────
# Візуалізація 8 фаз трансляції C/C++: перші 4 фази (препроцесор) перетворюють
# текст у чисту одиницю трансляції (TU), фази 5-8 (компілятор і лінкер) будують бінарник.

def fig_translation_phases():
    W, H = 840, 360
    p = []
    
    # Заголовок / контекст
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Зона 1: Препроцесор (Фази 1–4)
    p.append(rect(25, 40, 385, 255, fill="#f0f7ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(217, 65, "ФАЗИ 1–4: ПРЕПРОЦЕСОР (ТЕКСТ)", size=12, color=NEG, bold=True))
    
    phases_pp = [
        ("Фаза 1–2", "Відображення символів, зшивання рядків (\\)"),
        ("Фаза 3", "Лексика на pp-токени, заміна коментарів на пробіл"),
        ("Фаза 4", "Виконання директив (#include, #if), розгортання макросів"),
    ]
    for i, (title, desc) in enumerate(phases_pp):
        y_box = 85 + i * 62
        b = fitbox(40, y_box, 355, 52, f"{title}: {desc}", size=11, fill="#ffffff", stroke="#c8d9f1", sw=1.2, color=INK)
        p.append(b)
        if i < len(phases_pp) - 1:
            p.append(arrow(217, y_box + 52, 217, y_box + 62, color=NEG, sw=1.5))
            
    # Центральний місток: Одиниця трансляції
    p.append(arrow(410, 167, 445, 167, color=INK, sw=2.2))
    
    # Зона 2: Семантична компіляція (Фази 5–8)
    p.append(rect(445, 40, 370, 255, fill="#f2faf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(630, 65, "ФАЗИ 5–8: КОМПІЛЯТОР І ЛІНКЕР (СИНТАКСИС)", size=12, color=FIELD, bold=True))
    
    phases_comp = [
        ("Фаза 5–6", "Конвертація рядків у цільове кодування, склеювання"),
        ("Фаза 7", "Синтаксичний аналіз, AST, типи, оптимізація, .o"),
        ("Фаза 8", "Лінкування: збирання об'єктних файлів у бінарник"),
    ]
    for i, (title, desc) in enumerate(phases_comp):
        y_box = 85 + i * 62
        b = fitbox(460, y_box, 340, 52, f"{title}: {desc}", size=11, fill="#ffffff", stroke="#c2e6cd", sw=1.2, color=INK)
        p.append(b)
        if i < len(phases_comp) - 1:
            p.append(arrow(630, y_box + 52, 630, y_box + 62, color=FIELD, sw=1.5))

    p.append(text(W / 2, 325, "На стику фаз 4 і 5: чиста одиниця трансляції без жодних коментарів і директив «#»", size=12, color=INK, bold=True))
    render(os.path.join(OUT, "translation-phases.svg"), W, H, *p, title="Фази трансляції C/C++")


# ── 2. macro-expansion-prescan.svg ─────────────────────────────────────────────
# Механізм розгортання функціонального макросу: Prescan аргументів vs винятки (# та ##)

def fig_macro_expansion_prescan():
    W, H = 820, 340
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Вхід
    p.append(fitbox(30, 40, 200, 50, "Виклик макросу:\nFOO(BAR, 42)", size=11, fill="#f4f6f8", stroke="#4b5563", sw=1.5, bold=True))
    
    p.append(arrow(130, 90, 130, 120, color=INK, sw=1.8))
    
    # Розгалуження: чи аргумент іде під # або ## ?
    p.append(fitbox(30, 120, 200, 60, "Перевірка параметрів:\nчи є оператори # або ## ?", size=11, fill="#fff8e6", stroke="#d97706", sw=1.5))
    
    # Гілка ТАК (Виняток: без попереднього розгортання)
    p.append(arrow(230, 140, 310, 140, color=POS, sw=1.8))
    p.append(text(270, 130, "ТАК (#, ##)", size=10, color=POS, bold=True))
    p.append(fitbox(310, 115, 230, 55, "Без Prescan: аргумент береться\nбуквально як сирі токени", size=11, fill="#fdecea", stroke=POS, sw=1.5, color=POS))
    
    # Гілка НІ (Стандартний Prescan)
    p.append(arrow(130, 180, 130, 210, color=FIELD, sw=1.8))
    p.append(text(175, 195, "НІ (звичайне)", size=10, color=FIELD, bold=True))
    p.append(fitbox(30, 210, 200, 60, "Argument Prescan:\nрозгортання вкладених\nмакросів у аргументі", size=11, fill="#eef6ef", stroke=FIELD, sw=1.5, color=FIELD))
    
    # Злиття у підстановку в тіло макросу
    p.append(arrow(230, 240, 310, 240, color=INK, sw=1.8))
    p.append(fitbox(310, 215, 230, 55, "Підстановка токенів\nу тіло заміни макросу", size=11, fill="#f0f7ff", stroke=NEG, sw=1.5, color=NEG))
    
    p.append(arrow(425, 170, 425, 215, color=INK, sw=1.5))
    
    # Фінальне пересканування (Rescan)
    p.append(arrow(540, 240, 590, 240, color=INK, sw=1.8))
    p.append(fitbox(590, 205, 200, 75, "Rescan (повторне сканування):\nрозгортання інших макросів.\nПоточний макрос заблоковано\n(захист від нескінченної рекурсії)", size=10, fill="#fdf4ff", stroke="#9333ea", sw=1.5, color="#581c87"))
    
    p.append(text(W / 2, 312, "Оператори # та ## блокують Prescan — тому для розгортання потрібен двоетапний макрос (STR / XSTR)", size=11, color=INK, italic=True))
    
    render(os.path.join(OUT, "macro-expansion-prescan.svg"), W, H, *p, title="Етапи розгортання макросів та Prescan")


# ── 3. macro-hazards-comparison.svg ────────────────────────────────────────────
# Порівняння: небезпека багаторазового обчислення у макросах vs безпечна функція

def fig_macro_hazards_comparison():
    W, H = 820, 320
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Ліва колонка: Текстовий макрос (Пастка)
    p.append(rect(25, 35, 375, 240, fill="#fff5f5", stroke=POS, sw=1.5, rx=6))
    p.append(text(212, 60, "МАКРОС: #define SQUARE(x) ((x) * (x))", size=11, color=POS, bold=True))
    
    p.append(fitbox(40, 80, 345, 45, "Виклик: int y = SQUARE(i++);", size=12, fill="#ffffff", stroke="#fca5a5", sw=1.2))
    p.append(arrow(212, 125, 212, 145, color=POS, sw=1.5))
    p.append(fitbox(40, 145, 345, 55, "Результат підстановки в текст:\nint y = ((i++) * (i++));", size=11, fill="#fee2e2", stroke=POS, sw=1.2, color=POS, bold=True))
    
    p.append(fitbox(40, 210, 345, 50, "Наслідок: i інкрементується ДВІЧІ,\nневизначена або спотворена поведінка!", size=10, fill="#ffffff", stroke=POS, sw=1.2, color=POS))
    
    # Права колонка: Типізована функція (C++ constexpr / inline)
    p.append(rect(420, 35, 375, 240, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(607, 60, "ФУНКЦІЯ: constexpr auto square(auto x)", size=11, color=FIELD, bold=True))
    
    p.append(fitbox(435, 80, 345, 45, "Виклик: int y = square(i++);", size=12, fill="#ffffff", stroke="#86efac", sw=1.2))
    p.append(arrow(607, 125, 607, 145, color=FIELD, sw=1.5))
    p.append(fitbox(435, 145, 345, 55, "Семантика передачі аргументу:\nаргумент обчислюється рівно 1 раз", size=11, fill="#dcfce7", stroke=FIELD, sw=1.2, color=FIELD, bold=True))
    
    p.append(fitbox(435, 210, 345, 50, "Наслідок: i інкрементується ОДИН раз,\nповноцінна перевірка типів компілятором", size=10, fill="#ffffff", stroke=FIELD, sw=1.2, color=FIELD))
    
    p.append(text(W / 2, 298, "Текстова підстановка дублює вирази з побічними ефектами; функції гарантують одиничне обчислення", size=11, color=INK, italic=True))
    
    render(os.path.join(OUT, "macro-hazards-comparison.svg"), W, H, *p, title="Порівняння побічних ефектів у макросах та функціях")


# ── 4. x-macro-pipeline.svg ────────────────────────────────────────────────────
# Архітектура X-Macro: єдина таблиця-генератор створює Enum, масив рядків та парсер

def fig_x_macro_pipeline():
    W, H = 840, 350
    p = []
    
    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#d0d7de", sw=1.2, rx=8))
    
    # Центральна майстер-таблиця
    p.append(fitbox(25, 120, 240, 100, "МАЙСТЕР-ТАБЛИЦЯ (X-Macro)\n#define CMD_TABLE(X) \\\n  X(START, 0, \"start\") \\\n  X(STOP,  1, \"stop\")  \\\n  X(RESET, 2, \"reset\")", size=10, fill="#eff6ff", stroke=NEG, sw=1.8, bold=True, color=NEG))
    
    # Три розгалуження для різних генерацій
    # 1. Генерація Enum
    p.append(arrow(265, 140, 350, 65, color=INK, sw=1.8))
    p.append(fitbox(350, 35, 220, 60, "1. Визначення X(name, id, str):\n#define X(n, i, s) CMD_##n = i,\nenum Command { CMD_TABLE(X) };", size=10, fill="#ffffff", stroke="#93c5fd", sw=1.2))
    p.append(arrow(570, 65, 620, 65, color=FIELD, sw=1.8))
    p.append(fitbox(620, 42, 195, 46, "Згенеровано:\nenum { CMD_START=0, ... }", size=10, fill="#f0fdf4", stroke=FIELD, sw=1.2, color=FIELD, bold=True))
    
    # 2. Генерація масиву рядків
    p.append(arrow(265, 170, 350, 170, color=INK, sw=1.8))
    p.append(fitbox(350, 140, 220, 60, "2. Перевизначення X:\n#define X(n, i, s) s,\nconst char* names[] = {\n  CMD_TABLE(X) };", size=10, fill="#ffffff", stroke="#93c5fd", sw=1.2))
    p.append(arrow(570, 170, 620, 170, color=FIELD, sw=1.8))
    p.append(fitbox(620, 147, 195, 46, "Згенеровано:\n{\"start\", \"stop\", \"reset\"}", size=10, fill="#f0fdf4", stroke=FIELD, sw=1.2, color=FIELD, bold=True))
    
    # 3. Генерація Switch / Parser
    p.append(arrow(265, 200, 350, 275, color=INK, sw=1.8))
    p.append(fitbox(350, 245, 220, 60, "3. Перевизначення X:\n#define X(n, i, s) \\\n  if (!strcmp(str, s)) return CMD_##n;\nCMD_TABLE(X)", size=10, fill="#ffffff", stroke="#93c5fd", sw=1.2))
    p.append(arrow(570, 275, 620, 275, color=FIELD, sw=1.8))
    p.append(fitbox(620, 252, 195, 46, "Згенеровано:\nФункція парсингу рядка", size=10, fill="#f0fdf4", stroke=FIELD, sw=1.2, color=FIELD, bold=True))
    
    p.append(text(W / 2, 328, "Єдине джерело правди: додавання одного рядка в CMD_TABLE автоматично оновлює всі три структури", size=11, color=INK, bold=True))
    
    render(os.path.join(OUT, "x-macro-pipeline.svg"), W, H, *p, title="Конвеєр генерації коду через X-Macros")


if __name__ == "__main__":
    fig_translation_phases()
    fig_macro_expansion_prescan()
    fig_macro_hazards_comparison()
    fig_x_macro_pipeline()
    print("All figures generated successfully.")
