# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)

# ── 1. scope-vs-lifetime: фундаментальна різниця ─────────────────────────────
def fig_scope_vs_lifetime():
    W, H = 780, 390
    p = []

    # Заголовок осі вимірів
    p.append(fitbox(20, 20, 360, 45, "ОБЛАСТЬ ВИДИМОСТІ (Scope)\nСтатичний простір коду, де ім'я є дійсним",
                    size=11, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))
    p.append(fitbox(400, 20, 360, 45, "ТРИВАЛІСТЬ ЖИТТЯ (Lifetime)\nДинамічний інтервал часу, коли об'єкт існує в пам'яті",
                    size=11, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD))

    # 4 квадранти
    # Квадрант 1: Локальна змінна
    p.append(fitbox(20, 80, 360, 60, "1. Локальна змінна (int x = 10; у блоці)\n• Видимість: виключно всередині поточного блоку {}\n• Пам'ять: автоматична (виділяється на стеку при вході)",
                    size=10, bold=False, fill=FILL, stroke=LINE))
    p.append(fitbox(400, 80, 360, 60, "Тривалість: Автоматична (Automatic)\n• Об'єкт створюється в момент оголошення\n• Знищується автоматично при виході за межі блоку",
                    size=10, bold=False, fill="#ffffff", stroke=FIELD))

    # Квадрант 2: Статична локальна змінна
    p.append(fitbox(20, 150, 360, 60, "2. Статична локальна (static int count = 0;)\n• Видимість: локальна (тільки всередині однієї функції)\n• Зовнішній код не може звернутися до імені count",
                    size=10, bold=False, fill=FILL, stroke=LINE))
    p.append(fitbox(400, 150, 360, 60, "Тривалість: Статична (Static / .data / .bss)\n• Об'єкт живе весь час роботи програми\n• Зберігає значення між повторними викликами функції",
                    size=10, bold=False, fill="#ffffff", stroke=FIELD))

    # Квадрант 3: Глобальна змінна
    p.append(fitbox(20, 220, 360, 60, "3. Глобальна змінна (int g_system_state;)\n• Видимість: глобальна / файлова (через extern)\n• Ім'я доступне в будь-якому місці програми",
                    size=10, bold=False, fill=FILL, stroke=LINE))
    p.append(fitbox(400, 220, 360, 60, "Тривалість: Статична (Static)\n• Ініціалізується до старту main()\n• Звільняється лише після завершення процесу",
                    size=10, bold=False, fill="#ffffff", stroke=FIELD))

    # Квадрант 4: Динамічний об'єкт у купі
    p.append(fitbox(20, 290, 360, 60, "4. Динамічний об'єкт (*ptr = malloc / new Node)\n• Видимість: імені в об'єкта немає (анонімний)\n• Доступний через покажчик, поки покажчик у видимості",
                    size=10, bold=False, fill=FILL, stroke=LINE))
    p.append(fitbox(400, 290, 360, 60, "Тривалість: Динамічна (Dynamic / Heap)\n• Створюється вручну за запитом у купі\n• Живе, поки не викличуть free() або не збере GC",
                    size=10, bold=False, fill="#ffffff", stroke=POS))

    p.append(text(W / 2, 370, "Область видимості визначається текстом програми, а тривалість життя — часом виконання",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "scope-vs-lifetime.svg"), W, H, *p,
           title="Область видимості проти тривалості життя об'єкта")


# ── 2. lexical-vs-dynamic-lookup: пошук ідентифікатора ────────────────────────
def fig_lexical_vs_dynamic():
    W, H = 780, 370
    p = []

    # Колонка 1: Лексична видимість
    p.append(fitbox(25, 20, 350, 40, "ЛЕКСИЧНА ВИДИМІСТЬ (Lexical Scope)\nПошук за структурою сирцевого тексту (AST)",
                    size=11, bold=True, fill="#eaf0fd", stroke=NEG, color=NEG))

    p.append(fitbox(25, 70, 350, 75, "var x = 10; // глобальний x\nfunction bar() { print(x); }\nfunction foo() { var x = 20; bar(); }\nfoo();",
                    size=10, bold=True, fill=FILL, stroke=LINE))

    p.append(fitbox(25, 155, 350, 160, "Шлях розв'язання імені x:\n1. bar() шукає x у власному блоці -> не знайдено\n2. bar() підіймається до лексичного предка: Global\n3. Знайдено global x = 10\n\nРезультат: print(x) друкує 10\n(визначено місцем написання функції)",
                    size=10, bold=False, fill="#ffffff", stroke=FIELD))

    # Стрілка між колонками
    p.append(arrow(385, 180, 395, 180, color=MUTED, sw=1.5))

    # Колонка 2: Динамічна видимість
    p.append(fitbox(405, 20, 350, 40, "ДИНАМІЧНА ВИДИМІСТЬ (Dynamic Scope)\nПошук за стеком активних викликів (Call Stack)",
                    size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))

    p.append(fitbox(405, 70, 350, 75, "global x = 10;\ndef bar(): print(x)\ndef foo(): x = 20; bar()\nfoo()",
                    size=10, bold=True, fill=FILL, stroke=LINE))

    p.append(fitbox(405, 155, 350, 160, "Шлях розв'язання імені x:\n1. bar() шукає x у власному фреймі -> не знайдено\n2. bar() перевіряє фрейм того, хто викликав: foo()\n3. У фреймі foo() знайдено x = 20\n\nРезультат: print(x) друкує 20\n(залежить від динамічного ланцюга викликів)",
                    size=10, bold=False, fill="#ffffff", stroke=POS))

    p.append(text(W / 2, 345, "Лексичний пошук спирається на розташування в коді; динамічний — на стек поточних викликів",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "lexical-vs-dynamic-lookup.svg"), W, H, *p,
           title="Лексичний проти динамічного пошуку ідентифікатора")


# ── 3. scope-hierarchy-shadowing: вкладеність і затінення ─────────────────────
def fig_scope_hierarchy():
    W, H = 780, 390
    p = []

    # Вкладені прямокутники областей видимості
    # Global Scope
    p.append(rect(25, 20, 420, 320, fill="#f8f9fa", stroke="#495057", sw=1.5, rx=8))
    p.append(text(85, 42, "Глобальна область (Global)", size=11, bold=True, color="#495057"))
    p.append(text(85, 62, "int x = 1; // [A] Global", size=10, bold=True, color=MUTED))

    # Namespace / Module Scope
    p.append(rect(45, 80, 380, 245, fill="#edf2ff", stroke=NEG, sw=1.5, rx=6))
    p.append(text(120, 102, "Простір імен (Namespace app)", size=11, bold=True, color=NEG))
    p.append(text(120, 122, "int x = 2; // [B] Namespace", size=10, bold=True, color=MUTED))

    # Function Scope
    p.append(rect(65, 140, 340, 170, fill="#ebfbee", stroke=FIELD, sw=1.5, rx=6))
    p.append(text(130, 162, "Функція (Function run)", size=11, bold=True, color=FIELD))
    p.append(text(130, 182, "int x = 3; // [C] Local", size=10, bold=True, color=MUTED))

    # Block Scope
    p.append(rect(85, 200, 300, 95, fill="#fff9db", stroke="#f59f00", sw=1.5, rx=6))
    p.append(text(140, 222, "Вкладений блок (Block { ... })", size=11, bold=True, color="#d97706"))
    p.append(text(140, 242, "int x = 4; // [D] Inner Block", size=10, bold=True, color="#b45309"))
    p.append(text(140, 265, "Використання x -> бачить [D] (x = 4)", size=10, bold=True, color=INK))

    # Права панель: Як розв'язати конфлікт (Scope Resolution)
    p.append(fitbox(465, 20, 290, 320, "Оператори розв'язання:\n\n• Без префікса: x -> [D] (4)\n  (найближчий блок затінює решту)\n\n• C++ глобальний scope: ::x -> [A] (1)\n\n• C++ простір імен: app::x -> [B] (2)\n\n• Python nonlocal: зв'язує з [C] (3)\n\n• Python global: зв'язує з [A] (1)\n\nЗатінення (Shadowing) ховає зовнішні\nімена, але не знищує їх у пам'яті",
                    size=10, bold=False, fill=FILL, stroke=LINE))

    p.append(text(W / 2, 365, "Пошук імені йде зсередини назовні до першого збігу; внутрішнє ім'я затінює однойменні зовнішні",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "scope-hierarchy-shadowing.svg"), W, H, *p,
           title="Ієрархія областей видимості та затінення змінних")


# ── 4. closure-capture-lifetime: замикання й подовження життя ────────────────
def fig_closure_capture():
    W, H = 780, 370
    p = []

    # Ліва колонка: Захоплення за посиланням у C++ (небезпека висячого посилання)
    p.append(fitbox(25, 20, 350, 40, "ЗАХОПЛЕННЯ ЗА ПОСИЛАННЯМ [&]\nСтековий кадр знищується при виході з функції",
                    size=11, bold=True, fill="#fdecea", stroke=POS, color=POS))

    p.append(fitbox(25, 70, 350, 80, "auto make_callback() {\n    int val = 42; // на стеку make_callback\n    return [&]() { return val; }; // небезпечно!\n}\n// виклик: auto fn = make_callback(); fn();",
                    size=10, bold=True, fill=FILL, stroke=LINE))

    p.append(fitbox(25, 160, 350, 155, "Стан пам'яті:\n1. make_callback завершується -> стек вивільнено\n2. Лямбда зберігає покажчик на &val у мертвому стеку\n3. Виклик fn() призводить до читання сміття / UB\n\nРезультат: Dangling Reference (висяче посилання)",
                    size=10, bold=False, fill="#ffffff", stroke=POS))

    # Права колонка: Просування змінної в купу (Heap Promotion / Захоплення за значенням)
    p.append(fitbox(405, 20, 350, 40, "ПРОСУВАННЯ В КУПУ (Heap Promotion)\nЗмінна переноситься в купу для подовження життя",
                    size=11, bold=True, fill="#eafaf0", stroke=FIELD, color=FIELD))

    p.append(fitbox(405, 70, 350, 80, "function makeCounter() {\n    let count = 0; // захоплюється замиканням\n    return () => ++count;\n}\n// JS / Python / Go переносять count у Heap",
                    size=10, bold=True, fill=FILL, stroke=LINE))

    p.append(fitbox(405, 160, 350, 155, "Стан пам'яті:\n1. Компілятор бачить ескейп замикання (Escape Analysis)\n2. Створюється об'єкт оточення (Environment Record) у купі\n3. Замикання володіє посиланням на цей об'єкт\n\nРезультат: count живе стільки, скільки живе лямбда",
                    size=10, bold=False, fill="#ffffff", stroke=FIELD))

    p.append(text(W / 2, 345, "Якщо замикання переживає свій лексичний блок, захоплені змінні вимагають копіювання або перенесення в купу",
                  size=11, color=INK, italic=True))

    render(os.path.join(OUT, "closure-capture-lifetime.svg"), W, H, *p,
           title="Захоплення змінних у замиканні та керування пам'яттю")


if __name__ == "__main__":
    fig_scope_vs_lifetime()
    fig_lexical_vs_dynamic()
    fig_scope_hierarchy()
    fig_closure_capture()
    print("Figures generated successfully in", OUT)
