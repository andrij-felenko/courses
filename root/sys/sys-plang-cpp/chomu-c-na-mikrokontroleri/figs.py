# -*- coding: utf-8 -*-
"""Фігури до теми «Чому C++ на мікроконтролері» (sys-plang-cpp/freestanding)."""
import sys, os

# Додаємо шлях до scripts/ у корені репозиторію
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

CLR_SRC = "#eef4ff"
CLR_COMP = "#fef9e7"
CLR_SYM = "#eaf7ee"
CLR_ERR = "#fdecea"
CLR_BARRIER = "#fff3cd"


# ── 1. Принцип нульових накладних витрат у MMIO ──────────────────────────────
def fig_zero_cost_abstractions():
    W, H = 960, 430
    f = []

    f.append(text(W / 2, 30, "Принцип нульових накладних витрат: трансляція C та C++ в інструкції MMIO",
                  size=15, bold=True, color=INK))

    # Ліва колонка: Класичний C (макроси та нетипізовані вказівники)
    f.append(text(240, 65, "Підхід C (макроси та сирі вказівники):", size=13, bold=True, color=POS))
    
    b1_c, w1_c, _ = textbox(240, 125, [
        "Код мовою C:",
        "#define GPIOA_MODER *((volatile uint32_t*)0x40020000)",
        "GPIOA_MODER |= (1U << 10);"
    ], size=11, pad=10, fill=CLR_SRC, stroke=LINE)

    b2_c, w2_c, _ = textbox(240, 230, [
        "Компілятор C:",
        "• Немає перевірки типу регістра",
        "• Немає контролю сумісності бітових масок",
        "• Пряма генерація маски 0x400"
    ], size=11, pad=10, fill=CLR_COMP, stroke=LINE)

    # Права колонка: Сучасний C++ (типізовані реєстри та constexpr)
    f.append(text(720, 65, "Підхід C++ (типізовані реєстри та constexpr):", size=13, bold=True, color=FIELD))

    b1_cpp, w1_cpp, _ = textbox(720, 125, [
        "Код мовою C++:",
        "using GpioA = GpioPort<0x40020000>;",
        "GpioA::Moder::set<Pin::P5, Mode::Output>();"
    ], size=11, pad=10, fill=CLR_SRC, stroke=LINE)

    b2_cpp, w2_cpp, _ = textbox(720, 230, [
        "Компілятор C++:",
        "• Повна перевірка типів та прав доступу",
        "• constexpr згортання зсуву та маски під час збирання",
        "• 100% інлайнінг шаблонних методів"
    ], size=11, pad=10, fill=CLR_SYM, stroke=LINE)

    f += [b1_c, b2_c, b1_cpp, b2_cpp]

    # Стрілки вниз до компілятора
    f.append(arrow(240, 125 + 32, 240, 230 - 38, color=LINE))
    f.append(arrow(720, 125 + 32, 720, 230 - 38, color=FIELD))

    # Спільний вихід: Машинний код ARM Cortex-M
    b_out, w_out, _ = textbox(480, 355, [
        "Результуючий машинний код (ARM Thumb-2):",
        "LDR  R0, =0x40020000     ; Завантаження адреси MMIO регістра",
        "LDR  R1, [R0]            ; Читання поточного значення",
        "ORR  R1, R1, #1024       ; Накладання маски біта 10 (0x400)",
        "STR  R1, [R0]            ; Запис результату назад у регістр",
        "Витрати Flash: 12 байтів | Витрати SRAM: 0 байтів | Накладні витрати: 0%"
    ], size=11, pad=12, fill=CLR_BARRIER, stroke=FIELD)
    f.append(b_out)

    # Стрілки від компіляторів до машинного коду
    f.append(arrow(240, 230 + 38, 400, 355 - 48, color=LINE))
    f.append(arrow(720, 230 + 38, 560, 355 - 48, color=FIELD))

    render(os.path.join(IMG, "zero-cost-abstractions.svg"), W, H, *f,
           title="Принцип нульових накладних витрат у C++ на мікроконтролері")


# ── 2. Стерильна типобезпека доступу до апаратури ─────────────────────────────
def fig_mmio_type_safety():
    W, H = 960, 410
    f = []

    f.append(text(W / 2, 30, "Типобезпека доступу до регістрів: перевірка на етапі компіляції",
                  size=15, bold=True, color=INK))

    # 3 блоки перевірки
    b1, w1, _ = textbox(165, 125, [
        "1. Перевірка адреси та порту",
        "using GpioA = Gpio<0x40020000>;",
        "using GpioB = Gpio<0x40020400>;",
        "Порти є різними типами.",
        "Неможливо передати пін",
        "порту B у драйвер порту A"
    ], size=11, pad=10, fill=CLR_SRC, stroke=LINE)

    b2, w2, _ = textbox(480, 125, [
        "2. Контроль прав доступу",
        "Register<0x40020010, Access::ReadOnly>",
        "Регістр вхідних даних (IDR).",
        "Метод write() відсутній у типі.",
        "Спроба запису викликає",
        "помилку компіляції"
    ], size=11, pad=10, fill=CLR_COMP, stroke=LINE)

    b3, w3, _ = textbox(795, 125, [
        "3. Ізоляція бітових полів",
        "enum class PinMode : uint32_t {",
        "  Input = 0b00, Output = 0b01",
        "};",
        "Строга типізація виключає",
        "запис випадкових бітових масок"
    ], size=11, pad=10, fill=CLR_SYM, stroke=LINE)

    f += [b1, b2, b3]

    # Нижній блок результату компіляції
    b_err, w_err, _ = textbox(280, 310, [
        "Помилковий код (помилка на етапі збирання):",
        "GpioA::Idr::write(0x1234);",
        "static_assert failure: 'Register is Read-Only!'",
        "Помилка виявлена за 0.05 с компілятором!"
    ], size=11, pad=10, fill=CLR_ERR, stroke=POS)

    b_ok, w_ok, _ = textbox(680, 310, [
        "Коректний типізований код:",
        "auto val = GpioA::Idr::read();",
        "GpioA::Moder::set(Pin::P5, PinMode::Output);",
        "Чистий машинний код без рантайм-перевірок!"
    ], size=11, pad=10, fill=CLR_SYM, stroke=FIELD)

    f += [b_err, b_ok]

    # Стрілки від правил до результатів
    f.append(arrow(480 - 100, 125 + 55, 280 + 30, 310 - 45, color=POS))
    f.append(arrow(480 + 100, 125 + 55, 680 - 30, 310 - 45, color=FIELD))

    render(os.path.join(IMG, "mmio-type-safety.svg"), W, H, *f,
           title="Типобезпека MMIO регістрів у C++")


# ── 3. Анатомія Freestanding C++ ─────────────────────────────────────────────
def fig_freestanding_cpp_anatomy():
    W, H = 960, 420
    f = []

    f.append(text(W / 2, 30, "Анатомія Freestanding C++: дозволені можливості та відсічений рантайм",
                  size=15, bold=True, color=INK))

    # Ліва колонка: Дозволено (0 байт оверхеду)
    f.append(text(245, 65, "Дозволено та ефективно (0 байт оверхеду):", size=13, bold=True, color=FIELD))

    b_allowed, _, _ = textbox(245, 225, [
        "Ядро мови та компіляція:",
        "• Шаблони класів та функцій (Templates, CRTP)",
        "• Обчислення під час збирання (constexpr / consteval)",
        "• Автоматичне управління ресурсами (RAII деструктори)",
        "• Строга типізація (enum class, concepts, static_assert)",
        "• Структури, методи та інлайнінг (zero-overhead wrapping)",
        "• Простори імен (namespaces), лямбди без захвату",
        "",
        "Freestanding стандартні заголовки:",
        "• <cstdint>, <cstddef>, <type_traits>, <concepts>",
        "• <array>, <span>, <string_view>, <optional>, <bit>"
    ], size=10.5, pad=12, fill=CLR_SYM, stroke=FIELD)
    f.append(b_allowed)

    # Права колонка: Відсікається прапорцями збірки
    f.append(text(715, 65, "Відсікається прапорцями компілятора:", size=13, bold=True, color=POS))

    b_forbidden, _, _ = textbox(715, 225, [
        "Динамічний рантайм (відсікається):",
        "• Винятки (-fno-exceptions):",
        "  - Заощаджує кілобайти таблиць розгортання стеку",
        "• Інформація про типи в рантаймі (-fno-rtti):",
        "  - Заощаджує пам'ять type_info та vtable-дескрипторів",
        "• Невикористовувані таблиці unwinding (-fno-unwind-tables)",
        "• Динамічна купа (malloc/new):",
        "  - Відмова від купи (heap) усуває фрагментацію RAM",
        "",
        "Результат збирання прошивки:",
        "Детермінована пам'ять, нульовий час ініціалізації",
        "та повний контроль над кожним байтом Flash і SRAM"
    ], size=10.5, pad=12, fill=CLR_ERR, stroke=POS)
    f.append(b_forbidden)

    render(os.path.join(IMG, "freestanding-cpp-anatomy.svg"), W, H, *f,
           title="Анатомія Freestanding C++ для мікроконтролерів")


if __name__ == "__main__":
    fig_zero_cost_abstractions()
    fig_mmio_type_safety()
    fig_freestanding_cpp_anatomy()
    print("All figures generated successfully.")
