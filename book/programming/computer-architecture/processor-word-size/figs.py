# -*- coding: utf-8 -*-
"""Фігури до теми «Розрядність процесора» (processor-word-size).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)

# Палітра під байти та розрядність
RED_BG    = "#fdecea"
BLUE_BG   = "#eaf0fd"
GREEN_BG  = "#eaf6ee"
AMBER_BG  = "#fdf6e3"
PURPLE_BG = "#f3e8fd"
PURPLE    = "#8e44ad"
MONO      = "Consolas, 'DejaVu Sans Mono', monospace"

def out(name, *a, **k):
    render(os.path.join(IMG, name), *a, **k)

def mono(x, y, s, size=13, color=INK, anchor="start", bold=False):
    w = ' font-weight="700"' if bold else ''
    return ('<text x="%.1f" y="%.1f" font-family="%s" font-size="%d" fill="%s" '
            'text-anchor="%s"%s>%s</text>' % (x, y, MONO, size, color, anchor, w, esc(s)))


# ── 1. Чотири аспекти розрядності процесора ─────────────────────────────────
def fig_word_size_elements():
    W, H = 900, 480
    f = []
    
    # 4 блоки підсистем
    # 1. Регістри GPR
    b1, _, _ = textbox(230, 90, "Регістри GPR (РОП)\nШирина операндів у ядрах\n(8, 16, 32, 64 біти)", size=12, pad=10, fill=BLUE_BG, stroke=NEG, bold=True)
    f.append(b1)
    
    # 2. АЛП (ALU)
    b2, _, _ = textbox(670, 90, "Арифметико-логічний пристрій\nРозрядність суматора й логіки\n(обробка за 1 такт)", size=12, pad=10, fill=GREEN_BG, stroke=FIELD, bold=True)
    f.append(b2)
    
    # 3. Шина даних
    b3, _, _ = textbox(230, 260, "Шина даних (Data Bus)\nВнутрішня / зовнішня шина\n(пропускна здатність за такт)", size=12, pad=10, fill=AMBER_BG, stroke=POS, bold=True)
    f.append(b3)
    
    # 4. Адресна шина
    b4, _, _ = textbox(670, 260, "Адресна шина (Address Bus)\nФізичні адресні лінії до RAM\n(максимальний обсяг пам'яті)", size=12, pad=10, fill=PURPLE_BG, stroke=PURPLE, bold=True)
    f.append(b4)
    
    # Стрілки взаємодії між ними
    f.append(arrow(230, 140, 230, 210, color=LINE, sw=1.5))
    f.append(arrow(670, 140, 670, 210, color=LINE, sw=1.5))
    f.append(arrow(360, 90, 520, 90, color=LINE, sw=1.5))
    f.append(arrow(360, 260, 520, 260, color=LINE, sw=1.5))
    
    # Приклади розв'язки в історії (нижня панель)
    f.append(rect(40, 335, 820, 120, fill=FILL, stroke=LINE, sw=1.5, rx=8))
    f.append(text(450, 360, "Приклади розділення розрядностей в реальних процесорах", size=13, color=INK, bold=True))
    f.append(mono(60, 390, "Intel 8088:   16-бітні GPR  |  16-бітний ALU  |  8-бітна шина даних  |  20-бітна адреса (1 МБ)", size=11, color=INK))
    f.append(mono(60, 415, "Motorola 68k: 32-бітні GPR  |  16-бітний ALU  |  16-бітна шина даних |  24-бітна адреса (16 МБ)", size=11, color=INK))
    f.append(mono(60, 440, "x86-64 сучасні: 64-бітні GPR  |  64-бітний ALU  |  64/128-біт шина пам'яті | 48/57-біт віртуальна адреса", size=11, color=INK))

    out("word-size-elements.svg", W, H, *f)


# ── 2. Зростання адресного простору ──────────────────────────────────────────
def fig_address_space_growth():
    W, H = 900, 450
    f = []
    
    rows = [
        ("8-біт", "2⁸ = 256 Б (внутрішня) / 64 КБ (16-біт шина)", "64 КБ", BLUE_BG, NEG),
        ("16-біт", "2¹⁶ = 64 КБ (лінійний сегмент) / 1 МБ (8086)", "1 МБ", BLUE_BG, NEG),
        ("32-біт", "2³² = 4 294 967 296 байтів = 4 ГБ", "4 ГБ (фізична межа)", AMBER_BG, POS),
        ("48-біт", "2⁴⁸ = 281 474 976 710 656 байтів = 256 ТБ", "256 ТБ (канонічна x86-64)", GREEN_BG, FIELD),
        ("57-біт", "2⁵⁷ = 144 115 188 075 855 872 байтів = 128 ПБ", "128 ПБ (5-level paging)", PURPLE_BG, PURPLE),
        ("64-біт", "2⁶⁴ = 18 446 744 073 709 551 616 байтів = 16 ЕБ", "16 ЕБ (теоретичний максимум)", FILL, LINE)
    ]
    
    f.append(text(450, 30, "Еволюція адресного простору залежно від розрядності адреси", size=14, color=INK, bold=True))
    
    y = 60
    for arch, formula, desc, bg, st in rows:
        f.append(rect(50, y, 110, 48, fill=bg, stroke=st, sw=1.5, rx=6))
        f.append(text(105, y + 29, arch, size=13, color=st, bold=True))
        
        f.append(rect(175, y, 430, 48, fill=FILL, stroke=LINE, sw=1.2, rx=6))
        f.append(mono(190, y + 29, formula, size=11, color=INK))
        
        f.append(rect(620, y, 230, 48, fill=bg, stroke=st, sw=1.2, rx=6))
        f.append(text(735, y + 29, desc, size=11, color=st, bold=True))
        y += 62

    out("address-space-growth.svg", W, H, *f)


# ── 3. Канонічна адреса x86-64 (48 бітів і 57 бітів) ───────────────────────
def fig_canonical_address_layout():
    W, H = 920, 440
    f = []
    
    f.append(text(460, 25, "Схема 48-бітної канонічної адреси в x86-64 та знакове розширення", size=14, color=INK, bold=True))
    
    # Верхня діаграма: бітова розкладка 64-бітного покажчика
    f.append(rect(50, 50, 300, 50, fill=RED_BG, stroke=POS, sw=1.5, rx=4))
    f.append(text(200, 72, "Біти 63 .. 48 (16 бітів)", size=12, color=POS, bold=True))
    f.append(text(200, 90, "Копія біта 47 (знакове розширення)", size=10, color=MUTED))
    
    f.append(rect(350, 50, 60, 50, fill=AMBER_BG, stroke=POS, sw=1.5, rx=4))
    f.append(text(380, 72, "Біт 47", size=11, color=POS, bold=True))
    f.append(text(380, 90, "знак", size=10, color=MUTED))
    
    f.append(rect(410, 50, 460, 50, fill=GREEN_BG, stroke=FIELD, sw=1.5, rx=4))
    f.append(text(640, 72, "Біти 46 .. 0 (47 бітів)", size=12, color=FIELD, bold=True))
    f.append(text(640, 90, "Фізичний індекс сторінки + зміщення", size=10, color=MUTED))
    
    # Діапазони пам'яті: User, Hole, Kernel
    y0 = 135
    # 1. Kernel Space
    f.append(rect(60, y0, 800, 65, fill=RED_BG, stroke=POS, sw=1.5, rx=6))
    f.append(text(190, y0 + 26, "Простір ядра (Kernel Space)", size=13, color=POS, bold=True))
    f.append(mono(190, y0 + 50, "0xFFFF_8000_0000_0000 .. 0xFFFF_FFFF_FFFF_FFFF", size=11, color=POS))
    f.append(text(720, y0 + 38, "128 ТБ (біт 47 = 1)", size=12, color=POS, bold=True))
    
    # 2. Неканонічна діра
    y1 = y0 + 78
    f.append(rect(60, y1, 800, 95, fill="#f8f9fa", stroke=MUTED, sw=1.5, rx=6))
    f.append(text(460, y1 + 25, "НЕКАНОНІЧНА ДІРА (Non-canonical Address Hole)", size=13, color=POS, bold=True))
    f.append(mono(460, y1 + 50, "0x0000_8000_0000_0000 .. 0xFFFF_7FFF_FFFF_FFFF", size=11, color=MUTED))
    f.append(text(460, y1 + 75, "Будь-яке звернення до цієї зони викликає апаратне виключення #GP (General Protection)", size=11, color=POS))
    
    # 3. User Space
    y2 = y1 + 108
    f.append(rect(60, y2, 800, 65, fill=BLUE_BG, stroke=NEG, sw=1.5, rx=6))
    f.append(text(190, y2 + 26, "Простір користувача (User Space)", size=13, color=NEG, bold=True))
    f.append(mono(190, y2 + 50, "0x0000_0000_0000_0000 .. 0x0000_7FFF_FFFF_FFFF", size=11, color=NEG))
    f.append(text(720, y2 + 38, "128 ТБ (біт 47 = 0)", size=12, color=NEG, bold=True))

    out("canonical-address-layout.svg", W, H, *f)


# ── 4. Багаторівневі сторінкові таблиці (Paging 4-level) ─────────────────────
def fig_paging_levels():
    W, H = 920, 500
    f = []
    
    f.append(text(460, 25, "4-рівнева трансляція 48-бітної адреси в x86-64 (PML4 -> PDPT -> PD -> PT)", size=14, color=INK, bold=True))
    
    # Розбиття віртуальної адреси на 5 частин
    # 47..39 (9b PML4), 38..30 (9b PDPT), 29..21 (9b PD), 20..12 (9b PT), 11..0 (12b Offset)
    parts = [
        (60, 140, "PML4 [47:39]", "9 бітів", RED_BG, POS),
        (215, 140, "PDPT [38:30]", "9 бітів", AMBER_BG, POS),
        (370, 140, "PD [29:21]", "9 бітів", BLUE_BG, NEG),
        (525, 140, "PT [20:12]", "9 бітів", GREEN_BG, FIELD),
        (680, 175, "Зміщення [11:0]", "12 бітів (4 КБ)", FILL, LINE),
    ]
    
    for x, w, title, sub, bg, st in parts:
        f.append(rect(x, 50, w, 46, fill=bg, stroke=st, sw=1.5, rx=4))
        f.append(text(x + w / 2, 70, title, size=11, color=st, bold=True))
        f.append(text(x + w / 2, 86, sub, size=10, color=MUTED))
        
    # Таблиці в пам'яті
    # PML4 table
    f.append(rect(80, 140, 100, 180, fill=RED_BG, stroke=POS, sw=1.5, rx=6))
    f.append(text(130, 160, "PML4", size=12, color=POS, bold=True))
    f.append(text(130, 180, "512 записів", size=10, color=MUTED))
    f.append(rect(90, 210, 80, 24, fill=BG, stroke=POS, sw=1))
    f.append(mono(130, 226, "запис i", size=10, color=POS, anchor="middle"))
    
    # PDPT table
    f.append(rect(235, 170, 100, 180, fill=AMBER_BG, stroke=POS, sw=1.5, rx=6))
    f.append(text(285, 190, "PDPT", size=12, color=POS, bold=True))
    f.append(text(285, 210, "512 записів", size=10, color=MUTED))
    f.append(rect(245, 240, 80, 24, fill=BG, stroke=POS, sw=1))
    f.append(mono(285, 256, "запис j", size=10, color=POS, anchor="middle"))
    
    # PD table
    f.append(rect(390, 200, 100, 180, fill=BLUE_BG, stroke=NEG, sw=1.5, rx=6))
    f.append(text(440, 220, "PD", size=12, color=NEG, bold=True))
    f.append(text(440, 240, "512 записів", size=10, color=MUTED))
    f.append(rect(400, 270, 80, 24, fill=BG, stroke=NEG, sw=1))
    f.append(mono(440, 286, "запис k", size=10, color=NEG, anchor="middle"))
    
    # PT table
    f.append(rect(545, 230, 100, 180, fill=GREEN_BG, stroke=FIELD, sw=1.5, rx=6))
    f.append(text(595, 250, "PT", size=12, color=FIELD, bold=True))
    f.append(text(595, 270, "512 записів", size=10, color=MUTED))
    f.append(rect(555, 300, 80, 24, fill=BG, stroke=FIELD, sw=1))
    f.append(mono(595, 316, "запис m", size=10, color=FIELD, anchor="middle"))
    
    # Фізична сторінка 4 КБ
    f.append(rect(710, 270, 140, 180, fill=FILL, stroke=LINE, sw=1.5, rx=6))
    f.append(text(780, 295, "Фізична сторінка", size=12, color=INK, bold=True))
    f.append(text(780, 315, "4096 байтів (RAM)", size=10, color=MUTED))
    f.append(rect(725, 360, 110, 28, fill=GREEN_BG, stroke=FIELD, sw=1))
    f.append(mono(780, 378, "Байт [offset]", size=11, color=FIELD, anchor="middle"))
    
    # Стрілки зв'язку
    f.append(arrow(130, 96, 130, 140, color=POS, sw=1.5))
    f.append(arrow(170, 222, 235, 250, color=POS, sw=1.5))
    f.append(arrow(325, 252, 390, 280, color=POS, sw=1.5))
    f.append(arrow(480, 282, 545, 310, color=NEG, sw=1.5))
    f.append(arrow(635, 312, 710, 370, color=FIELD, sw=1.5))
    f.append(arrow(767, 96, 767, 355, color=LINE, sw=1.5))
    
    # Підпис знизу
    f.append(text(460, 480, "Кожен крок трансляції (при TLB-miss) вимагає окремого читання з пам'яті (4 звернення в DRAM)", size=11, color=POS, italic=True))

    out("paging-levels.svg", W, H, *f)


# ── 5. Моделі даних C/C++: ILP32, LP64, LLP64 ───────────────────────────────
def fig_data_models():
    W, H = 900, 420
    f = []
    
    f.append(text(450, 25, "Порівняння моделей даних мов C/C++ у 32-бітних та 64-бітних ОС", size=14, color=INK, bold=True))
    
    # Заголовок таблиці
    headers = [
        (50, 160, "Тип даних"),
        (220, 140, "ILP32 (32-біт)\nx86, ARM32"),
        (370, 240, "LP64 (64-біт Unix)\nLinux, macOS, BSD"),
        (620, 230, "LLP64 (64-біт Windows)\nWindows x64 / ARM64"),
    ]
    for x, w, htext in headers:
        f.append(rect(x, 50, w, 44, fill=FILL, stroke=LINE, sw=1.5, rx=4))
        f.append(mtext(x + w / 2, 68, htext, size=11, color=INK, bold=True))
        
    rows = [
        ("short", "2 байти (16b)", "2 байти (16b)", "2 байти (16b)", False),
        ("int", "4 байти (32b)", "4 байти (32b)", "4 байти (32b)", False),
        ("long", "4 байти (32b)", "8 байтів (64b)", "4 байти (32b)", True),
        ("long long", "8 байтів (64b)", "8 байтів (64b)", "8 байтів (64b)", False),
        ("покажчик (void*)", "4 байти (32b)", "8 байтів (64b)", "8 байтів (64b)", True),
        ("size_t / uintptr_t", "4 байти (32b)", "8 байтів (64b)", "8 байтів (64b)", True)
    ]
    
    y = 102
    for name, ilp, lp, llp, diff in rows:
        st_bg = AMBER_BG if diff else BG
        st_c = POS if diff else INK
        
        # Назва
        f.append(rect(50, y, 160, 38, fill=FILL, stroke=LINE, sw=1, rx=4))
        f.append(mono(130, y + 24, name, size=11, color=INK, anchor="middle", bold=True))
        
        # ILP32
        f.append(rect(220, y, 140, 38, fill=BG, stroke=LINE, sw=1, rx=4))
        f.append(text(290, y + 24, ilp, size=11, color=INK))
        
        # LP64
        f.append(rect(370, y, 240, 38, fill=st_bg, stroke=st_c if diff else LINE, sw=1.5 if diff else 1, rx=4))
        f.append(text(490, y + 24, lp, size=11, color=st_c, bold=diff))
        
        # LLP64
        f.append(rect(620, y, 230, 38, fill=st_bg, stroke=st_c if diff else LINE, sw=1.5 if diff else 1, rx=4))
        f.append(text(735, y + 24, llp, size=11, color=st_c, bold=diff))
        
        y += 44
        
    f.append(text(450, 395, "Головна пастка переносимості: sizeof(long) == 8 у Linux, але sizeof(long) == 4 у Windows x64", size=12, color=POS, bold=True))

    out("data-models.svg", W, H, *f)


# ── 6. Щільність кешу та роздування покажчиків (64B Cache Line) ─────────────
def fig_cache_pointer_density():
    W, H = 900, 460
    f = []
    
    f.append(text(450, 25, "Вплив розрядності покажчиків на щільність кеш-лінії L1 (64 байти)", size=14, color=INK, bold=True))
    
    # 1. 32-бітний режим (16 покажчиків у лінії)
    f.append(rect(50, 55, 800, 160, fill=BLUE_BG, stroke=NEG, sw=1.5, rx=8))
    f.append(text(190, 80, "32-бітний режим (ILP32 / x32 ABI): 4 байти на покажчик", size=12, color=NEG, bold=True))
    f.append(text(720, 80, "16 покажчиків у 64B кеш-лінії", size=12, color=NEG, bold=True))
    
    # 16 блоків
    bx = 65
    bw = 46
    for i in range(16):
        f.append(rect(bx + i * (bw + 2), 100, bw, 50, fill=BG, stroke=NEG, sw=1.2, rx=3))
        f.append(mono(bx + i * (bw + 2) + bw / 2, 122, f"p{i}", size=10, color=NEG, anchor="middle"))
        f.append(text(bx + i * (bw + 2) + bw / 2, 140, "4B", size=9, color=MUTED, anchor="middle"))
    f.append(text(450, 195, "Висока просторова локальність: 16 вузлів списку / елементів дерева на один запит до DRAM", size=11, color=INK))
    
    # 2. 64-бітний режим (8 покажчиків у лінії)
    f.append(rect(50, 240, 800, 160, fill=RED_BG, stroke=POS, sw=1.5, rx=8))
    f.append(text(190, 265, "64-бітний режим (LP64 / LLP64): 8 байтів на покажчик", size=12, color=POS, bold=True))
    f.append(text(720, 265, "Лише 8 покажчиків у 64B кеш-лінії", size=12, color=POS, bold=True))
    
    # 8 блоків
    bx = 65
    bw = 94
    for i in range(8):
        f.append(rect(bx + i * (bw + 4), 285, bw, 50, fill=BG, stroke=POS, sw=1.2, rx=3))
        f.append(mono(bx + i * (bw + 4) + bw / 2, 307, f"ptr_{i}", size=11, color=POS, anchor="middle"))
        f.append(text(bx + i * (bw + 4) + bw / 2, 325, "8 байтів", size=9, color=MUTED, anchor="middle"))
    f.append(text(450, 380, "Кеш-тиск зростає вдвічі: 50% падіння щільності, вдвічі більше L1/L2 miss на обхід структури", size=11, color=POS, bold=True))

    out("cache-pointer-density.svg", W, H, *f)


if __name__ == "__main__":
    fig_word_size_elements()
    fig_address_space_growth()
    fig_canonical_address_layout()
    fig_paging_levels()
    fig_data_models()
    fig_cache_pointer_density()
    print("Усі 6 фігур згенеровано успішно.")
