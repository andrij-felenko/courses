# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_svd_xml_hierarchy():
    W, H = 860, 520
    p = []

    # Заголовок / фонова панель
    p.append(rect(10, 10, W - 20, H - 20, fill="#fcfdfd", stroke="#d0d7de", sw=1, rx=8))

    # Корінь: <device>
    p.append(fitbox(30, 30, 220, 54,
                    "<device>\n[name, width, resetValue]",
                    size=12, bold=True, fill="#e8f0fe", stroke=NEG, sw=1.8))

    # CPU блок
    p.append(fitbox(300, 30, 200, 54,
                    "<cpu>\n[name, endian, fpuPresent]",
                    size=11, bold=True, fill="#eef9f1", stroke=FIELD, sw=1.5))
    p.append(arrow(250, 57, 298, 57, color=LINE, sw=1.5))

    # Контейнер <peripherals>
    p.append(fitbox(30, 120, 220, 44,
                    "<peripherals>",
                    size=12, bold=True, fill="#f3f4f6", stroke=INK, sw=1.5))
    p.append(arrow(140, 84, 140, 118, color=LINE, sw=1.5))

    # Вузол <peripheral> Базовий (USART1)
    p.append(fitbox(30, 195, 230, 72,
                    "<peripheral>\nname=\"USART1\"\nbaseAddress=0x40013800\ngroupName=\"USART\"",
                    size=10, bold=True, fill="#fff8e1", stroke="#f59e0b", sw=1.8))
    p.append(arrow(140, 164, 140, 193, color=LINE, sw=1.5))

    # Вузол <peripheral> Похідний (USART2 derivedFrom)
    p.append(fitbox(310, 195, 230, 72,
                    "<peripheral derivedFrom=\"USART1\">\nname=\"USART2\"\nbaseAddress=0x40004400\n[успадковує регістри]",
                    size=10, bold=True, fill="#fef3c7", stroke="#d97706", sw=1.5))
    p.append(arrow(260, 231, 308, 231, color="#d97706", sw=1.5))
    p.append(text(285, 218, "derived", size=9, color="#b45309", bold=True))

    # Вузли переривання та блоків адрес для USART1
    p.append(fitbox(30, 300, 135, 46,
                    "<addressBlock>\noffset=0, size=0x400",
                    size=9, fill="#f9fafb", stroke=MUTED, sw=1))
    p.append(fitbox(175, 300, 125, 46,
                    "<interrupt>\nname=USART1_IRQ",
                    size=9, fill="#fdf2f8", stroke=POS, sw=1.2))
    p.append(line(80, 267, 80, 298, color=LINE, sw=1.2))
    p.append(line(220, 267, 220, 298, color=LINE, sw=1.2))

    # Вузол <registers>
    p.append(fitbox(580, 70, 250, 46,
                    "<registers>\n[контейнер регістрів периферії]",
                    size=11, bold=True, fill="#eef2ff", stroke="#6366f1", sw=1.5))
    p.append(arrow(260, 215, 578, 93, color=LINE, sw=1.5))

    # Вузол <register>
    p.append(fitbox(580, 145, 250, 70,
                    "<register>\nname=\"CR1\"\naddressOffset=0x00, size=32\naccess=read-write, resetVal=0",
                    size=10, bold=True, fill="#f5f3ff", stroke="#7c3aed", sw=1.8))
    p.append(arrow(705, 116, 705, 143, color=LINE, sw=1.5))

    # Вузол <fields>
    p.append(fitbox(580, 245, 250, 40,
                    "<fields> [бітові поля регістра]",
                    size=11, bold=True, fill="#f3f4f6", stroke=INK, sw=1.4))
    p.append(arrow(705, 215, 705, 243, color=LINE, sw=1.5))

    # Вузли <field>
    p.append(fitbox(580, 310, 250, 60,
                    "<field>\nname=\"UE\" (USART Enable)\nbitOffset=0, bitWidth=1\naccess=read-write",
                    size=10, bold=True, fill="#ecfdf5", stroke=FIELD, sw=1.5))
    p.append(fitbox(580, 395, 250, 60,
                    "<field>\nname=\"M\" (Word Length)\nbitOffset=12, bitWidth=1\naccess=read-write",
                    size=10, bold=True, fill="#ecfdf5", stroke=FIELD, sw=1.5))
    p.append(arrow(705, 285, 705, 308, color=LINE, sw=1.5))
    p.append(line(705, 370, 705, 393, color=LINE, sw=1.5))

    # Вузол <enumeratedValues> для поля M
    p.append(fitbox(290, 395, 250, 80,
                    "<enumeratedValues>\n• M_8BIT (0): 8 Data bits\n• M_9BIT (1): 9 Data bits\n[значення для розкодування]",
                    size=9, bold=False, fill="#eff6ff", stroke=NEG, sw=1.2))
    p.append(arrow(580, 425, 542, 425, color=NEG, sw=1.5))

    render(os.path.join(OUT, "svd-xml-hierarchy-structure.svg"), W, H, *p,
           title="Ієрархічна структура XML-документа специфікації CMSIS-SVD 1.3")


def fig_svd_to_header_transform():
    W, H = 860, 470
    p = []

    p.append(rect(10, 10, W - 20, H - 20, fill="#fafbfc", stroke="#d0d7de", sw=1, rx=8))

    # Вхідний файл SVD
    p.append(fitbox(30, 175, 170, 100,
                    "Файл CMSIS-SVD\n(device.svd)\n\n• XML розмітка\n• Карта адрес\n• Біти, маски, енуми",
                    size=10, bold=True, fill="#e8f0fe", stroke=NEG, sw=2))

    # Ядро синтаксичного аналізу й валідації
    p.append(fitbox(240, 125, 220, 200,
                    "Семантичний процесор SVD\n\n1. XML парсинг та XSD перевірка\n2. Розкриття derivedFrom\n3. Сортування зміщень регістрів\n4. Розрахунок прогалин (padding)\n5. Валідація прав (RO/WO/RW)\n6. Генерація моделі периферії",
                    size=9.5, bold=False, fill="#fffbeb", stroke="#f59e0b", sw=1.8))
    p.append(arrow(200, 225, 238, 225, color=LINE, sw=2))

    # Вихідні генератори / споживачі
    # 1. C99 CMSIS заголовок
    p.append(fitbox(500, 25, 330, 95,
                    "C99 CMSIS Header (svd2c / svdconv)\n\n• typedef struct { ... } Periph_TypeDef\n• uint8_t RESERVED_0x[N] вирівнювання\n• #define PERIPH_REG_FIELD_Pos / _Msk\n• _Static_assert(offsetof(...) == offset)",
                    size=9.5, bold=False, fill="#f0fdf4", stroke=FIELD, sw=1.5))
    p.append(arrow(460, 180, 498, 72, color=FIELD, sw=1.8))

    # 2. C++20 Type-Safe заголовок
    p.append(fitbox(500, 135, 330, 100,
                    "C++20 Type-Safe Regs\n\n• Шаблонні обгортки Register<Addr, Policy>\n• Строгі enum class для бітових полів\n• Concepts (Readable / Writable / ClearOnRead)\n• static_assert валідація зміщень",
                    size=9.5, bold=False, fill="#eef2ff", stroke="#6366f1", sw=1.5))
    p.append(arrow(460, 225, 498, 185, color="#6366f1", sw=1.8))

    # 3. Rust PAC (svd2rust)
    p.append(fitbox(500, 250, 330, 85,
                    "Rust PAC Crate (svd2rust)\n\n• Type-state токени володіння (Ownership)\n• Safe Modify / Read / Write проксі\n• Zero-cost бітові мутатори",
                    size=9.5, bold=False, fill="#fff7ed", stroke="#ea580c", sw=1.5))
    p.append(arrow(460, 270, 498, 292, color="#ea580c", sw=1.8))

    # 4. Відлагоджувач IDE
    p.append(fitbox(500, 350, 330, 90,
                    "IDE Debugger (GDB / Ozone / VSCode)\n\n• Live Peripherals древоподібний перегляд\n• Декодування значень полів у бітові описи\n• Безпечний моніторинг без side-effects",
                    size=9.5, bold=False, fill="#fdf2f8", stroke=POS, sw=1.5))
    p.append(arrow(460, 295, 498, 395, color=POS, sw=1.8))

    render(os.path.join(OUT, "svd-to-c-header-transformation.svg"), W, H, *p,
           title="Трансформація опису SVD у системні заголовки C/C++, Rust та структури відлагоджувача")


if __name__ == "__main__":
    fig_svd_xml_hierarchy()
    fig_svd_to_header_transform()
    print("Figures generated successfully.")
