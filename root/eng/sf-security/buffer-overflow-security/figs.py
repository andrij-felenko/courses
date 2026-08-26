# -*- coding: utf-8 -*-
"""Генерація SVG-ілюстрацій для теми 'Переповнення буфера як вразливість'."""
import sys, os

# 4 рівні вгору від root/eng/sf-security/buffer-overflow-security до scripts/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG_DIR, exist_ok=True)

def fig_stack_frame_anatomy():
    """Фігура 1: Анатомія стекового кадру x86-64 та механіка переповнення."""
    w, h = 900, 540
    frags = []

    # Заголовок
    frags.append(text(450, 28, "Анатомія стекового кадру x86-64 та перезапис адреси повернення", size=17, bold=True))

    # Ліва колонка: Нормальний стан стекового кадру
    frags.append(rect(45, 60, 350, 450, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(220, 85, "Штатний стековий кадр функції", size=14, bold=True, color="#1e293b"))
    frags.append(text(220, 105, "(Стек росте вниз: від 0x7fffffffe000 до 0x7fffffffd000)", size=11, color=MUTED))

    # Блоки пам'яті ліворуч (від високих адрес до низьких)
    b_ret_ok, _, _ = textbox(220, 150, "Адреса повернення (Saved RIP)\n[8 байтів: адреса в caller]", size=11, pad=8, fill="#e2e8f0", stroke="#475569", min_w=300)
    b_sfp_ok, _, _ = textbox(220, 225, "Збережений покажчик кадру (Saved RBP)\n[8 байтів: база стека caller]", size=11, pad=8, fill="#e2e8f0", stroke="#475569", min_w=300)
    b_canary_ok, _, _ = textbox(220, 300, "Канарка стека (Stack Canary)\n[8 байтів: секретне число з %fs:0x28]", size=11, pad=8, fill="#dcfce7", stroke=FIELD, min_w=300)
    b_buf_ok, _, _ = textbox(220, 395, "Локальний буфер (char buf[64])\n[64 байти під вхідні дані]\nЗаповнюється знизу вгору ↑", size=11, pad=10, fill="#eff6ff", stroke=NEG, min_w=300)
    b_rsp_ok, _, _ = textbox(220, 475, "Поточний покажчик стека (%rsp)", size=11, pad=6, fill=BG, stroke=LINE, min_w=300)

    frags.extend([b_ret_ok, b_sfp_ok, b_canary_ok, b_buf_ok, b_rsp_ok])

    # Права колонка: Атака переповнення буфера
    frags.append(rect(505, 60, 350, 450, fill="#fff5f5", stroke=POS, sw=2, rx=8))
    frags.append(text(680, 85, "Руйнування стека через strcpy / gets", size=14, bold=True, color=POS))
    frags.append(text(680, 105, "(Неконтрольований запис 88 байтів)", size=11, color=POS))

    b_ret_bad, _, _ = textbox(680, 150, "ПЕРЕЗАПИСАНА АДРЕСА ПОВЕРНЕННЯ\n[0x7ffff7a34560 -> шеллкод / ROP]", size=11, pad=8, fill="#fee2e2", stroke=POS, bold=True, min_w=300)
    b_sfp_bad, _, _ = textbox(680, 225, "Перезаписаний Saved RBP\n[0x4141414141414141 -> сміття]", size=11, pad=8, fill="#fee2e2", stroke=POS, min_w=300)
    b_canary_bad, _, _ = textbox(680, 300, "Пошкоджена канарка (0x4141414141414141)\n[Якщо захист вимкнено/обійдено]", size=11, pad=8, fill="#fee2e2", stroke=POS, min_w=300)
    b_buf_bad, _, _ = textbox(680, 395, "Тіло пейлоаду зловмисника (64 байти)\nNOP-sled (\\x90\\x90...) або шеллкод\nЗапис іде за межі буфера!", size=11, pad=10, fill="#fee2e2", stroke=POS, min_w=300)
    b_ret_ctrl, _, _ = textbox(680, 475, "ret передає керування шеллкоду!", size=11, pad=6, fill="#fee2e2", stroke=POS, bold=True, min_w=300)

    frags.extend([b_ret_bad, b_sfp_bad, b_canary_bad, b_buf_bad, b_ret_ctrl])

    # Стрілки напрямків
    frags.append(arrow(22, 140, 22, 470, color="#64748b", sw=2))
    frags.append(text(22, 305, "Ріст стека (↓)", size=10, color="#64748b", anchor="middle"))

    frags.append(arrow(878, 470, 878, 140, color=POS, sw=2.5))
    frags.append(text(878, 305, "Запис буфера (↑)", size=10, color=POS, anchor="middle"))

    # Центральна стрілка вторгнення
    frags.append(arrow(405, 395, 495, 395, color=POS, sw=2))

    out_path = os.path.join(IMG_DIR, "stack-frame-anatomy-and-overflow.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def fig_stack_canary():
    """Фігура 2: Життєвий цикл перевірки стекової канарки (Stack Smashing Protector)."""
    w, h = 900, 490
    frags = []

    frags.append(text(450, 28, "Механізм захисту стека канаркою (Stack Smashing Protector / SSP)", size=17, bold=True))

    # Етап 1: Пролог
    frags.append(rect(30, 65, 260, 400, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(160, 90, "1. Пролог функції", size=14, bold=True, color="#1e293b"))
    frags.append(text(160, 110, "(Встановлення вартового)", size=11, color=MUTED))

    p1, _, _ = textbox(160, 165, "Регістр сегмента TLS\n%fs:0x28 (x86-64)\n[Випадкове значення з ядра]", size=11, pad=8, fill="#eaf0fd", stroke=NEG, min_w=230)
    p2, _, _ = textbox(160, 260, "Команда компілятора:\nmov %fs:0x28, %rax\nmov %rax, -0x8(%rbp)\nxor %eax, %eax", size=11, pad=8, fill="#ffffff", stroke=LINE, min_w=230)
    p3, _, _ = textbox(160, 375, "Канарка зберігається на стеку\nміж локальними змінними\nта збереженим Saved RBP", size=11, pad=8, fill="#dcfce7", stroke=FIELD, min_w=230)
    frags.extend([p1, p2, p3])
    frags.append(arrow(160, 205, 160, 225, color=LINE, sw=1.5))
    frags.append(arrow(160, 315, 160, 335, color=LINE, sw=1.5))

    # Етап 2: Виконання тіла
    frags.append(rect(320, 65, 260, 400, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(text(450, 90, "2. Спроба атаки", size=14, bold=True, color=POS))
    frags.append(text(450, 110, "(Переповнення буфера)", size=11, color=POS))

    a1, _, _ = textbox(450, 165, "Виклик небезпечної функції\nstrcpy(buf, payload)\n[Довжина > розміру buf]", size=11, pad=8, fill=BG, stroke=POS, min_w=230)
    a2, _, _ = textbox(450, 265, "Пейлоад перетирає пам'ять:\n[buf] -> [CANARY] -> [RBP] -> [RIP]\nКанарку спотворено:\n0x4141414141414141", size=11, pad=8, fill="#fee2e2", stroke=POS, bold=True, min_w=230)
    a3, _, _ = textbox(450, 375, "Зловмисник не знає 64-біт\nвипадкового значення канарки\nперший байт є нульовим (0x00)", size=11, pad=8, fill=BG, stroke=LINE, min_w=230)
    frags.extend([a1, a2, a3])
    frags.append(arrow(450, 210, 450, 225, color=POS, sw=1.5))
    frags.append(arrow(450, 320, 450, 340, color=POS, sw=1.5))

    # Етап 3: Епілог і вирок
    frags.append(rect(610, 65, 260, 400, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(740, 90, "3. Епілог функції", size=14, bold=True, color="#1e293b"))
    frags.append(text(740, 110, "(Звірення вартового)", size=11, color=MUTED))

    e1, _, _ = textbox(740, 160, "Звірення значення:\nmov -0x8(%rbp), %rax\nxor %fs:0x28, %rax\nje .L_normal_ret", size=11, pad=8, fill="#ffffff", stroke=LINE, min_w=230)
    e_pass, _, _ = textbox(740, 265, "Рівні (XOR == 0):\nБезпечний вихід через ret", size=11, pad=6, fill="#dcfce7", stroke=FIELD, min_w=230)
    e_fail, _, _ = textbox(740, 375, "Нерівні (XOR != 0):\nВиклик __stack_chk_fail()\nАварійна зупинка SIGABRT!\nЕксплуатація зірвана", size=11, pad=8, fill="#fee2e2", stroke=POS, bold=True, min_w=230)
    frags.extend([e1, e_pass, e_fail])
    frags.append(arrow(740, 210, 740, 240, color=FIELD, sw=1.5))
    frags.append(arrow(740, 295, 740, 335, color=POS, sw=2))

    # Міжблочні переходи
    frags.append(arrow(290, 260, 320, 260, color=LINE, sw=1.5))
    frags.append(arrow(580, 260, 610, 260, color=POS, sw=1.5))

    out_path = os.path.join(IMG_DIR, "stack-canary-protection-mechanism.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def fig_heap_chunk_corruption():
    """Фігура 3: Структура чанка glibc malloc, пошкодження метаданих та Safe Unlinking."""
    w, h = 900, 520
    frags = []

    frags.append(text(450, 28, "Переповнення в кучі (Heap Overflow) та захисне вилучення (Safe Unlinking)", size=17, bold=True))

    # Верхня частина: Анатомія чанка
    frags.append(rect(40, 55, 820, 195, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(450, 78, "Анатомія суміжних чанків алокатора glibc (ptmalloc2)", size=13, bold=True, color="#1e293b"))

    c1_meta, _, _ = textbox(170, 135, "Чанк A: Заголовок\nprev_size (8B) | size (8B)\nПрапорці: A|M|P (PREV_INUSE)", size=10, pad=6, fill="#e2e8f0", stroke="#475569", min_w=220)
    c1_data, _, _ = textbox(370, 135, "Чанк A: Користувацькі дані\nВиділено: malloc(64)\nБуфер під дані програми", size=10, pad=6, fill="#eff6ff", stroke=NEG, min_w=160)
    c2_meta, _, _ = textbox(570, 135, "Чанк B: Заголовок\nprev_size (8B) | size (8B)\nfd (8B) | bk (8B) [якщо free]", size=10, pad=6, fill="#fef3c7", stroke="#d97706", min_w=180)
    c2_data, _, _ = textbox(760, 135, "Чанк B: Дані / Free Body\nКорисне навантаження або\nвузол зв'язного списку", size=10, pad=6, fill="#f8fafc", stroke=LINE, min_w=160)

    frags.extend([c1_meta, c1_data, c2_meta, c2_data])

    # Стрілка переповнення між чанками
    frags.append(arrow(450, 135, 480, 135, color=POS, sw=3))
    b_ovf, _, _ = textbox(450, 205, "Переповнення з чанка A руйнує метадані чанка B (size, fd, bk)", size=11, pad=5, fill="#fee2e2", stroke=POS, bold=True, min_w=420)
    frags.append(b_ovf)

    # Нижня частина: Safe Unlinking
    frags.append(rect(40, 265, 820, 235, fill="#f8fafc", stroke="#94a3b8", sw=1.5, rx=8))
    frags.append(text(450, 290, "Механізм перевірки Safe Unlinking під час злиття блоків", size=13, bold=True, color="#1e293b"))

    b_unlink_classic, _, _ = textbox(240, 380, "Класичний Unlink (вразливий):\nP->fd->bk = P->bk;\nP->bk->fd = P->fd;\n\nДозволяв довільний запис\n(Arbitrary Write / Write-What-Where)\nза адресою, підробленою в fd/bk", size=11, pad=8, fill="#fee2e2", stroke=POS, min_w=360)

    b_unlink_safe, _, _ = textbox(650, 380, "Безпечний Unlink (Safe Unlinking):\nif (P->fd->bk != P || P->bk->fd != P)\n    malloc_printerr(\"corrupted double-linked list\");\n\nПеревіряє двоспрямовану цілісність списку!\nЗламані покажчики викликають негайний аварійний abort()", size=11, pad=8, fill="#dcfce7", stroke=FIELD, min_w=390)

    frags.extend([b_unlink_classic, b_unlink_safe])

    out_path = os.path.join(IMG_DIR, "heap-chunk-corruption-and-unlink.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

def fig_intel_cet_shadow_stack():
    """Фігура 4: Тіньовий стек Intel CET (Shadow Stack) проти атак ROP."""
    w, h = 900, 520
    frags = []

    frags.append(text(450, 28, "Апаратний тіньовий стек (Intel CET / ARM Shadow Stack)", size=17, bold=True))

    # Ліва частина: Звичайний стек даних
    frags.append(rect(40, 60, 370, 360, fill="#fff5f5", stroke=POS, sw=1.5, rx=8))
    frags.append(text(225, 85, "Стек даних програми (RSP)", size=14, bold=True, color=POS))
    frags.append(text(225, 105, "(Доступний на читання й запис процесу)", size=11, color=MUTED))

    d1, _, _ = textbox(225, 155, "Локальні змінні та буфери\n(char buf[64])", size=11, pad=8, fill="#fee2e2", stroke=POS, min_w=320)
    d2, _, _ = textbox(225, 250, "Перезаписана адреса повернення:\n[0x00007ffff7de1234 -> ROP gadget]\nПідмінена атакуючим через переповнення!", size=11, pad=8, fill="#fee2e2", stroke=POS, bold=True, min_w=320)
    d3, _, _ = textbox(225, 360, "Інструкція RET зчитує адресу:\npop %rip -> 0x7ffff7de1234", size=11, pad=8, fill=BG, stroke=LINE, min_w=320)
    frags.extend([d1, d2, d3])

    # Права частина: Тіньовий стек
    frags.append(rect(490, 60, 370, 360, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(675, 85, "Апаратний тіньовий стек (SSP)", size=14, bold=True, color=FIELD))
    frags.append(text(675, 105, "(Захищений MMU: звичайний запис заборонено)", size=11, color=MUTED))

    s1, _, _ = textbox(675, 155, "Мікрокод CPU при інструкції CALL:\nАвтоматично записує оригінальний RIP\nу захищену пам'ять Shadow Stack", size=11, pad=8, fill="#dcfce7", stroke=FIELD, min_w=320)
    s2, _, _ = textbox(675, 250, "Оригінальна адреса повернення:\n[0x0000555555555189 -> main+45]\nНЕДОСЯЖНА для переповнення буфера!", size=11, pad=8, fill="#dcfce7", stroke=FIELD, bold=True, min_w=320)
    s3, _, _ = textbox(675, 360, "Інструкція RET зчитує з тіньового стека:\nshadow_rip -> 0x555555555189", size=11, pad=8, fill=BG, stroke=LINE, min_w=320)
    frags.extend([s1, s2, s3])

    # Порівняння внизу по центру (нижче обох панелей)
    b_cmp, _, _ = textbox(450, 465, "Апаратне порівняння CPU: data_rip != shadow_rip -> Виняток #CP (Control Protection Fault)", size=11, pad=8, fill="#fee2e2", stroke=POS, bold=True, min_w=650)
    frags.append(b_cmp)

    frags.append(arrow(225, 395, 350, 445, color=POS, sw=2))
    frags.append(arrow(675, 395, 550, 445, color=FIELD, sw=2))

    out_path = os.path.join(IMG_DIR, "intel-cet-shadow-stack.svg")
    render(out_path, w, h, *frags)
    print("Generated:", out_path)

if __name__ == '__main__':
    fig_stack_frame_anatomy()
    fig_stack_canary()
    fig_heap_chunk_corruption()
    fig_intel_cet_shadow_stack()
