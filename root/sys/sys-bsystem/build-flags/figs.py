# -*- coding: utf-8 -*-
"""Фігури до теми «Прапорці збірки: оптимізація, налагоджувальні символи, попередження»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
if not os.path.isdir(IMG):
    os.makedirs(IMG)

DIRTY = "#fdecea"     # червонуватий акцент
CLEAN = "#eaf7ef"     # зеленуватий акцент
BLUE_BG = "#eef4ff"   # синій акцент


def node(cx, cy, label, fill=FILL, stroke=LINE, bold=False, size=14, sw=1.5, min_w=0):
    frag, w, h = textbox(cx, cy, label, size=size, fill=fill, stroke=stroke,
                         bold=bold, sw=sw, min_w=min_w)
    return frag, (cx, cy, w, h)


def down_arr(a, b, color=LINE, sw=1.8):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return arrow(ax, ay + ah / 2 + 3, bx, by - bh / 2 - 5, color=color, sw=sw)


def right_arr(a, b, color=LINE, sw=1.8):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return arrow(ax + aw / 2 + 3, ay, bx - bw / 2 - 5, by, color=color, sw=sw)


# ── 1. Конвеєр оптимізації: -O0 проти -O2/-O3 ────────────────────────────────
def fig_opt_pipeline():
    W, H = 980, 520
    parts = []

    # Заголовки гілок
    parts.append(rect(45, 60, 420, 420, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(255, 88, "Рівень -O0 (без оптимізацій)", size=16, bold=True, color=POS))

    parts.append(rect(515, 60, 420, 420, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(725, 88, "Рівень -O2 / -O3 (конвеєр перетворень)", size=16, bold=True, color=FIELD))

    # Ліва колонка (-O0)
    s1, g_s1 = node(255, 135, "Вихідний код (C / C++)", size=13.5, fill=BG, stroke=MUTED)
    s2, g_s2 = node(255, 215, "AST → Пряма генерація IR\n(кожна змінна живе на стеку)", size=13, fill=DIRTY, stroke=POS)
    s3, g_s3 = node(255, 305, "Відсутність проходів оптимізації\n(пасивний SSA, нуль спрощень)", size=13, fill=BG, stroke=MUTED)
    s4, g_s4 = node(255, 410, "Машинний код: надлишковий стек,\nпостійні звернення до RAM (mov/ldr)", size=13, fill=DIRTY, stroke=POS, bold=True)

    parts += [s1, s2, s3, s4]
    parts += [down_arr(g_s1, g_s2), down_arr(g_s2, g_s3), down_arr(g_s3, g_s4, color=POS)]

    # Права колонка (-O2/-O3)
    o1, g_o1 = node(725, 135, "Вихідний код (C / C++)", size=13.5, fill=BG, stroke=MUTED)
    o2, g_o2 = node(725, 215, "Канонічний SSA IR\n(скалярні проходи: CSE, DSE, LICM)", size=13, fill=BLUE_BG, stroke=NEG)
    o3, g_o3 = node(725, 305, "Циклові та міжпроцедурні оптимізації\n(інлайнінг, розгортання, SIMD-векторизація)", size=13, fill=CLEAN, stroke=FIELD)
    o4, g_o4 = node(725, 410, "Машинний код: регістровий розподіл,\nконвеєрна векторизація (AVX/NEON)", size=13, fill=CLEAN, stroke=FIELD, bold=True)

    parts += [o1, o2, o3, o4]
    parts += [down_arr(g_o1, g_o2), down_arr(g_o2, g_o3, color=NEG), down_arr(g_o3, g_o4, color=FIELD)]

    render(os.path.join(IMG, "optimization-pipeline.svg"), W, H, *parts,
           title="Трансформація коду під час компіляції: наївний переклад проти графа оптимізацій")


# ── 2. Організація налагоджувальної інформації ──────────────────────────────
def fig_debug_layout():
    W, H = 1040, 520
    parts = []

    # Панель 1: Монолітний DWARF (-g)
    parts.append(rect(40, 65, 300, 420, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(190, 92, "Монолітний DWARF (-g)", size=14.5, bold=True, color=POS))
    
    m1, g_m1 = node(190, 145, "file.o\n[Код + .debug_* секції]", size=12.5, fill=DIRTY, stroke=POS)
    m_lnk, g_mlnk = node(190, 245, "Лінкер (ld / lld)\nважке копіювання таблиць", size=12.5, fill=BG, stroke=MUTED)
    m2, g_m2 = node(190, 360, "app (ELF)\nвеличезний бінарник\n(до 80% — налагодження)", size=12.5, fill=DIRTY, stroke=POS, bold=True)
    parts += [m1, m_lnk, m2, down_arr(g_m1, g_mlnk), down_arr(g_mlnk, g_m2, color=POS)]
    parts.append(text(190, 455, "Повільне лінкування", size=12.5, color=POS, italic=True))

    # Панель 2: Split DWARF (-gsplit-dwarf)
    parts.append(rect(370, 65, 300, 420, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(520, 92, "Split DWARF (-gsplit-dwarf)", size=14.5, bold=True, color=FIELD))
    
    s_o, g_so = node(520, 145, "file.o [Код + скелет]", size=12.5, fill=CLEAN, stroke=FIELD)
    s_dwo, g_sdwo = node(520, 225, "file.dwo [Окремі DWARF-дані]", size=12.5, fill=BLUE_BG, stroke=NEG)
    s_lnk, g_slnk = node(520, 310, "Швидкий лінкер\n(обробляє лише .o)", size=12.5, fill=BG, stroke=MUTED)
    s_elf, g_self = node(520, 400, "app (ELF) компактний\n+ gdb читає .dwo при запуску", size=12, fill=CLEAN, stroke=FIELD, bold=True)
    parts += [s_o, s_dwo, s_lnk, s_elf, down_arr(g_so, g_sdwo), down_arr(g_sdwo, g_slnk), down_arr(g_slnk, g_self, color=FIELD)]
    parts.append(text(520, 455, "Лінкування прискорено в рази", size=12.5, color=FIELD, italic=True))

    # Панель 3: MSVC PDB (/Zi)
    parts.append(rect(700, 65, 300, 420, fill="#f8fafc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(850, 92, "MSVC PDB (/Zi)", size=14.5, bold=True, color=NEG))
    
    p_obj, g_pobj = node(850, 145, "file.obj\n[Машинний код без відладки]", size=12.5, fill=CLEAN, stroke=FIELD)
    p_srv, g_psrv = node(850, 235, "mspdbsrv.exe\n(сервер запису символів)", size=12.5, fill=BLUE_BG, stroke=NEG)
    p_pdb, g_ppdb = node(850, 325, "vc140.pdb / app.pdb\n[Окремий каталог символів]", size=12, fill=BLUE_BG, stroke=NEG, bold=True)
    p_exe, g_pexe = node(850, 405, "app.exe (чистий образ)", size=12.5, fill=CLEAN, stroke=FIELD)
    parts += [p_obj, p_srv, p_pdb, p_exe, down_arr(g_pobj, g_psrv), down_arr(g_psrv, g_ppdb, color=NEG), down_arr(g_ppdb, g_pexe, color=FIELD)]
    parts.append(text(850, 455, "Символи суворо відокремлені", size=12.5, color=NEG, italic=True))

    render(os.path.join(IMG, "debug-info-layout.svg"), W, H, *parts,
           title="Архітектура налагоджувальних символів: монолітний DWARF, Split DWARF та зовнішній PDB")


# ── 3. Адресація в позиційно-незалежному коді (PIC/PIE) ──────────────────────
def fig_pic_pie_got():
    W, H = 1000, 460
    parts = []

    # Ліва панель: Абсолютна адресація (Non-PIC)
    parts.append(rect(45, 60, 425, 360, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(257, 88, "Пряма адресація (Non-PIC)", size=15, bold=True, color=POS))

    np_code, g_npc = node(257, 145, "Код: mov eax, [0x00405000]\n(абсолютна адреса зашита в .text)", size=13, fill=DIRTY, stroke=POS)
    np_rel, g_npr = node(257, 240, "Секція .text модифікується під час завантаження\n(Text Relocations — сторінки пам'яті 'брудні')", size=12.5, fill=BG, stroke=POS)
    np_mem, g_npm = node(257, 345, "Неможливо розділити .text між процесами;\nASLR блокується або вимагає копіювання", size=12.5, fill=DIRTY, stroke=POS, bold=True)

    parts += [np_code, np_rel, np_mem, down_arr(g_npc, g_npr, color=POS), down_arr(g_npr, g_npm, color=POS)]

    # Права панель: PIC/PIE через GOT
    parts.append(rect(530, 60, 425, 360, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(742, 88, "Позиційно-незалежний код (-fPIC / -fPIE)", size=15, bold=True, color=FIELD))

    p_code, g_pc = node(742, 145, "Код: mov rax, [rip + offset_GOT]\n(RIP-відносна адресація до слота)", size=13, fill=CLEAN, stroke=FIELD)
    p_got, g_pg = node(742, 240, "Таблиця GOT (.got у секції даних)\nдинамічний лінкер оновлює лише покажчики", size=12.5, fill=BLUE_BG, stroke=NEG)
    p_mem, g_pm = node(742, 345, "Секція .text лишається незмінною (Read-Only),\nспільною для сотень процесів; повний захист ASLR", size=12.5, fill=CLEAN, stroke=FIELD, bold=True)

    parts += [p_code, p_got, p_mem, down_arr(g_pc, g_pg, color=NEG), down_arr(g_pg, g_pm, color=FIELD)]

    render(os.path.join(IMG, "pic-pie-got.svg"), W, H, *parts,
           title="Механізм адресації даних: жорсткі зміщення проти таблиці глобальних зсувів (GOT)")


# ── 4. Конвеєр Link-Time Optimization (LTO) ─────────────────────────────────
def fig_lto_pipeline():
    W, H = 1000, 490
    parts = []

    # Верхній конвеєр: Традиційна збірка
    parts.append(rect(45, 60, 910, 185, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(190, 85, "Традиційна ізольована збірка", size=14.5, bold=True, color=POS))

    t_src, g_ts = node(155, 145, "a.cpp  |  b.cpp", size=13, fill=BG, stroke=MUTED)
    t_obj, g_to = node(420, 145, "a.o  |  b.o\n(Машинний код)", size=13, fill=DIRTY, stroke=POS)
    t_lnk, g_tl = node(680, 145, "Лінкер: зшивання символів\n(міжмодульний інлайнінг неможливий)", size=12.5, fill=BG, stroke=MUTED)
    t_bin, g_tb = node(885, 145, "Бінарник", size=13, fill=DIRTY, stroke=POS, bold=True)

    parts += [t_src, t_obj, t_lnk, t_bin, right_arr(g_ts, g_to), right_arr(g_to, g_tl), right_arr(g_tl, g_tb, color=POS)]

    # Нижній конвеєр: LTO
    parts.append(rect(45, 270, 910, 195, fill="#fafbfc", stroke=MUTED, sw=1.2, rx=8))
    parts.append(text(215, 295, "Оптимізація на етапі лінкування (-flto / /GL)", size=14.5, bold=True, color=FIELD))

    l_src, g_ls = node(155, 365, "a.cpp  |  b.cpp", size=13, fill=BG, stroke=MUTED)
    l_obj, g_lo = node(420, 365, "a.o  |  b.o\n(Проміжне представлення IR)", size=13, fill=BLUE_BG, stroke=NEG)
    l_lnk, g_ll = node(680, 365, "LTO-плагін лінкера:\nміжмодульний аналіз, інлайнінг,\nдевіртуалізація, видалення DSE/DCE", size=12, fill=CLEAN, stroke=FIELD)
    l_bin, g_lb = node(885, 365, "Оптимальний\nбінарник", size=13, fill=CLEAN, stroke=FIELD, bold=True)

    parts += [l_src, l_obj, l_lnk, l_bin, right_arr(g_ls, g_lo), right_arr(g_lo, g_ll, color=NEG), right_arr(g_ll, g_lb, color=FIELD)]

    render(os.path.join(IMG, "lto-pipeline.svg"), W, H, *parts,
           title="Робота LTO: збереження проміжного представлення (IR) усуває межі між одиницями трансляції")


if __name__ == "__main__":
    fig_opt_pipeline()
    fig_debug_layout()
    fig_pic_pie_got()
    fig_lto_pipeline()
    print("All figures generated successfully.")
