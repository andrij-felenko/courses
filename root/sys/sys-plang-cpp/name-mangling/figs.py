# -*- coding: utf-8 -*-
"""Фігури до теми «Спотворення імен: як символ несе сигнатуру» (reference/cpp-standards/language)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

CLR_SRC = "#eef4ff"
CLR_COMP = "#fef9e7"
CLR_SYM = "#eaf7ee"
CLR_LINK = "#fdecea"


# ── 1. Конвеєр від вихідного коду до компонувальника ─────────────────────────
def fig_mangling_pipeline():
    W, H = 960, 360
    f = []

    # 4 блоки конвеєра
    b1, w1, h1 = textbox(130, 160, ["Вихідний код C++", "math::add(int, int)", "math::add(double, double)"],
                         size=13, pad=12, fill=CLR_SRC, stroke=NEG)
    b2, w2, h2 = textbox(380, 160, ["Компілятор C++", "Розв'язання типів", "Генерація символів"],
                         size=13, pad=12, fill=CLR_COMP, stroke=LINE)
    b3, w3, h3 = textbox(630, 160, ["Таблиця .symtab (ELF/COFF)", "_ZN4math3addEii -> 0x1040", "_ZN4math3addEdd -> 0x1080"],
                         size=13, pad=12, fill=CLR_SYM, stroke=FIELD)
    b4, w4, h4 = textbox(865, 160, ["Компонувальник", "Пошук за рядком", "strcmp(sym1, sym2)"],
                         size=13, pad=12, fill=CLR_LINK, stroke=POS)
    f += [b1, b2, b3, b4]

    # Стрілки між етапами
    f.append(arrow(130 + w1 / 2 + 6, 160, 380 - w2 / 2 - 6, 160, color=LINE))
    f.append(arrow(380 + w2 / 2 + 6, 160, 630 - w3 / 2 - 6, 160, color=LINE))
    f.append(arrow(630 + w3 / 2 + 6, 160, 865 - w4 / 2 - 6, 160, color=LINE))

    # Підписи під стрілками
    f.append(text((130 + w1 / 2 + 380 - w2 / 2) / 2, 142, "семантика", size=12, color=MUTED))
    f.append(text((380 + w2 / 2 + 630 - w3 / 2) / 2, 142, "mangling", size=12, color=MUTED))
    f.append(text((630 + w3 / 2 + 865 - w4 / 2) / 2, 142, "зв'язування", size=12, color=MUTED))

    # Додаткові пояснювальні примітки зверху та знизу
    f.append(text(W / 2, 50, "Ієрархія C++ відображається в плоский список унікальних ASCII-рядків",
                  size=15, bold=True, color=INK))
    f.append(text(W / 2, 275, "Компонувальник не знає про типи й класи: для нього символ — це просто масив байтів",
                  size=13, color=MUTED))
    f.append(text(W / 2, 305, "Унікальність кожного перевантаження гарантується кодуванням сигнатури в саме ім'я",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "fig-mangling-pipeline.svg"), W, H, *f,
           title="Конвеєр спотворення імен C++")


# ── 2. Анатомія Itanium C++ ABI ──────────────────────────────────────────────
def fig_itanium_anatomy():
    W, H = 960, 340
    f = []

    f.append(text(W / 2, 45, "Анатомія символу Itanium ABI: _ZN7physics6Engine12apply_forceERK6Vector",
                  size=15, bold=True, color=INK))

    # Ряд токенів символу
    tokens = [
        ("_Z", "Префікс C++", "#eaf0fd", NEG),
        ("N", "Вкладене ім'я", "#fef9e7", LINE),
        ("7physics", "Простір (довжина 7)", "#f4f6f8", LINE),
        ("6Engine", "Клас (довжина 6)", "#f4f6f8", LINE),
        ("12apply_force", "Метод (довжина 12)", "#f4f6f8", LINE),
        ("E", "Кінець області", "#fef9e7", LINE),
        ("R", "Посиланя &", "#eaf7ee", FIELD),
        ("K", "const", "#fdecea", POS),
        ("6Vector", "Тип Vector", "#f4f6f8", LINE),
    ]

    x_start = 55
    y_pos = 140
    box_w = 94
    gap = 8

    for i, (tok, label, fill_c, strk_c) in enumerate(tokens):
        cx = x_start + i * (box_w + gap) + box_w / 2
        b, _, _ = textbox(cx, y_pos, tok, size=13, pad=8, fill=fill_c, stroke=strk_c, bold=True, min_w=box_w)
        f.append(b)
        
        # Лінія-виноска вниз
        f.append(line(cx, y_pos + 25, cx, y_pos + 55, color=strk_c, sw=1.2))
        
        # Підпис значення
        lbl_box, _, _ = textbox(cx, y_pos + 85, label, size=11, pad=5, fill="#ffffff", stroke=strk_c, min_w=box_w)
        f.append(lbl_box)

    f.append(text(W / 2, 290, "Префікс довжини перед кожним ідентифікатором усуває потребу в розділювачах між словами",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "fig-itanium-anatomy.svg"), W, H, *f,
           title="Анатомія символу Itanium ABI")


# ── 3. Порівняння Itanium ABI та MSVC ABI ───────────────────────────────────
def fig_itanium_vs_msvc():
    W, H = 960, 400
    f = []

    f.append(text(W / 2, 45, "Порівняння кодування однієї функції: public: int MathHelper::calculate(int, double)",
                  size=15, bold=True, color=INK))

    # Блок Itanium
    f.append(rect(40, 80, 880, 120, fill="#f8faff", stroke=NEG, sw=1.5, rx=8))
    f.append(text(60, 110, "Itanium C++ ABI (GCC / Clang / Linux / macOS)", size=14, bold=True, color=NEG, anchor="start"))
    f.append(text(60, 142, "Символ: _ZN10MathHelper9calculateEid", size=15, bold=True, color=INK, anchor="start"))
    f.append(text(60, 175, "• _Z: префікс • N..E: вкладене • 10MathHelper • 9calculate • e: float / i: int / d: double (без повернення)",
                  size=12, color=MUTED, anchor="start"))

    # Блок MSVC
    f.append(rect(40, 225, 880, 135, fill="#fffaf5", stroke=POS, sw=1.5, rx=8))
    f.append(text(60, 255, "MSVC ABI (Microsoft Visual C++ / Windows)", size=14, bold=True, color=POS, anchor="start"))
    f.append(text(60, 287, "Символ: ?calculate@MathHelper@@QEAAHHN@Z", size=15, bold=True, color=INK, anchor="start"))
    f.append(text(60, 320, "• ?: префікс • @: розділювач • @@: кінець області • Q: public non-static • EAA: __cdecl • H: повертає int • H: int • N: double • @Z: кінець",
                  size=12, color=MUTED, anchor="start"))

    f.append(text(W / 2, 382, "MSVC на відміну від Itanium кодує тип повернення, конвенцію виклику та модифікатор доступу",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "fig-itanium-vs-msvc.svg"), W, H, *f,
           title="Порівняння Itanium ABI та MSVC ABI")


# ── 4. Межа двійкової сумісності (ABI Boundary) ──────────────────────────────
def fig_abi_boundary_risk():
    W, H = 960, 360
    f = []

    f.append(text(W / 2, 45, "Двійковий кордон динамічних бібліотек (.so / .dll)", size=15, bold=True, color=INK))

    # Верхня гілка: чистий C++
    b_cpp_lib, _, _ = textbox(180, 125, ["Бібліотека на C++", "GCC 13 (libA.so)", "std::string / методи"],
                              size=13, pad=10, fill=CLR_SRC, stroke=NEG)
    b_cpp_app, _, _ = textbox(780, 125, ["Програма на C++", "MSVC або Clang", "Несумісні символи / vtable"],
                              size=13, pad=10, fill=CLR_LINK, stroke=POS)
    f += [b_cpp_lib, b_cpp_app]

    f.append(arrow(310, 125, 630, 125, color=POS, sw=2))
    f.append(text(470, 110, "Прямий C++ експорт", size=13, bold=True, color=POS))
    f.append(text(470, 145, "✗ Збій лінкування або падіння пам'яті", size=12, color=POS))

    # Нижня гілка: extern "C" міст
    b_c_lib, _, _ = textbox(180, 245, ["Реалізація C++", "Всередині бібліотеки", "Складні класи / шаблони"],
                            size=13, pad=10, fill=CLR_SRC, stroke=NEG)
    b_c_bridge, _, _ = textbox(470, 245, ["extern \"C\" Міст (C ABI)", "Плоскі назви функцій", "Непрозорі вказівники (Opaque Ptrs)"],
                               size=13, pad=10, fill=CLR_SYM, stroke=FIELD)
    b_c_app, _, _ = textbox(780, 245, ["Клієнт (будь-який компілятор)", "C++, Rust, Python, Go, C#", "Стабільне зв'язування"],
                            size=13, pad=10, fill=CLR_SYM, stroke=FIELD)
    f += [b_c_lib, b_c_bridge, b_c_app]

    f.append(arrow(290, 245, 335, 245, color=FIELD, sw=1.8))
    f.append(arrow(605, 245, 650, 245, color=FIELD, sw=1.8))

    f.append(text(W / 2, 330, "extern \"C\" пригнічує спотворення імен і створює нейтральний двійковий інтерфейс",
                  size=13, color=MUTED))

    render(os.path.join(IMG, "fig-abi-boundary-risk.svg"), W, H, *f,
           title="Межа двійкової сумісності C++")


if __name__ == "__main__":
    fig_mangling_pipeline()
    fig_itanium_anatomy()
    fig_itanium_vs_msvc()
    fig_abi_boundary_risk()
    print("Всі фігури згенеровано успішно.")
