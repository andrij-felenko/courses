# -*- coding: utf-8 -*-
"""Генератор діаграм для теми «Функції як значення першого класу»."""

import os
import sys

# Підключаємо спільний svgkit із scripts/
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "..", "scripts"
        )
    ),
)
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_first_class_ops():
    """1. Операції над значеннями першого класу."""
    w, h = 820, 360
    body = []

    # Тло та секції
    body.append(
        text(
            w / 2,
            30,
            "Три базові права значення першого класу",
            size=16,
            bold=True,
        )
    )

    # 1. Передача як аргумент
    b1_bg = rect(30, 60, 230, 260, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8)
    b1_t = text(145, 88, "1. Передача як аргумент", size=14, bold=True)
    f_box, _, _ = textbox(
        145, 130, "Функція-аргумент\nfn(x)", size=12, fill="#eaf0fd", stroke=NEG
    )
    arr1 = arrow(145, 160, 145, 195, color=LINE, sw=1.5)
    hof_box, _, _ = textbox(
        145,
        235,
        "Функція вищого порядку\nmap(fn, list)\nfilter(fn, list)",
        size=12,
        fill="#fdf6e2",
        stroke="#d97706",
    )
    b1_note = text(
        145, 295, "Параметризація алгоритму", size=11, color=MUTED, italic=True
    )
    body.extend([b1_bg, b1_t, f_box, arr1, hof_box, b1_note])

    # 2. Повернення з функції
    b2_bg = rect(295, 60, 230, 260, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8)
    b2_t = text(410, 88, "2. Повернення з функції", size=14, bold=True)
    fact_box, _, _ = textbox(
        410,
        130,
        "Фабрика / Генератор\nmake_adder(step)",
        size=12,
        fill="#fdf6e2",
        stroke="#d97706",
    )
    arr2 = arrow(410, 160, 410, 195, color=LINE, sw=1.5)
    ret_box, _, _ = textbox(
        410,
        235,
        "Породжена функція\nadd_step(x)\n[із власним станом]",
        size=12,
        fill="#eaf0fd",
        stroke=NEG,
    )
    b2_note = text(
        410,
        295,
        "Спеціалізація поведінки",
        size=11,
        color=MUTED,
        italic=True,
    )
    body.extend([b2_bg, b2_t, fact_box, arr2, ret_box, b2_note])

    # 3. Збереження в структурах
    b3_bg = rect(560, 60, 230, 260, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8)
    b3_t = text(675, 88, "3. Збереження в пам'яті", size=14, bold=True)
    var_box, _, _ = textbox(
        675, 130, "Змінна або поле\nhandler = fn", size=12, fill=FILL, stroke=LINE
    )
    arr3 = arrow(675, 160, 675, 195, color=LINE, sw=1.5)
    tbl_box, _, _ = textbox(
        675,
        235,
        "Таблиця диспетчеризації\ntable['get'] = on_get\ntable['post'] = on_post",
        size=12,
        fill="#e8f8f0",
        stroke=FIELD,
    )
    b3_note = text(
        675,
        295,
        "Динамічна маршрутизація",
        size=11,
        color=MUTED,
        italic=True,
    )
    body.extend([b3_bg, b3_t, var_box, arr3, tbl_box, b3_note])

    render(os.path.join(IMG_DIR, "first-class-ops.svg"), w, h, *body)


def fig_fat_pointer():
    """2. Машинне представлення замикання: товстий покажчик."""
    w, h = 820, 360
    body = []

    body.append(
        text(
            w / 2,
            30,
            "Внутрішня будова замикання: товстий покажчик (Fat Pointer)",
            size=16,
            bold=True,
        )
    )

    # Ліворуч: Товстий покажчик (Fat Pointer / Closure Struct)
    fp_bg = rect(50, 80, 240, 220, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8)
    fp_title = text(170, 110, "Замикання (Fat Pointer)", size=14, bold=True)

    code_ptr_rect = rect(
        70, 140, 200, 50, fill="#eaf0fd", stroke=NEG, sw=1.5, rx=6
    )
    code_ptr_txt = mtext(
        170,
        160,
        "code_ptr (8 байтів)\nПокажчик на машинний код",
        size=12,
        color=INK,
        bold=False,
    )

    env_ptr_rect = rect(
        70, 215, 200, 50, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=6
    )
    env_ptr_txt = mtext(
        170,
        235,
        "env_ptr (8 байтів)\nПокажчик на оточення",
        size=12,
        color=INK,
        bold=False,
    )

    body.extend([
        fp_bg,
        fp_title,
        code_ptr_rect,
        code_ptr_txt,
        env_ptr_rect,
        env_ptr_txt,
    ])

    # Праворуч угорі: Сегмент коду (.text)
    code_block_bg = rect(
        460, 70, 310, 115, fill="#f0f4ff", stroke=NEG, sw=1.5, rx=8
    )
    code_block_title = text(
        615, 95, "Сегмент коду (.text / Flash)", size=13, color=NEG, bold=True
    )
    code_asm = mtext(
        615,
        120,
        "fn_impl(env, args...):\n  MOV rax, [rdi + 8]   ; читання env->x\n  ADD rax, rsi         ; додавання аргументу\n  RET",
        size=11,
        color=INK,
    )
    body.extend([code_block_bg, code_block_title, code_asm])

    # Праворуч унизу: Оточення захоплення (Heap / Stack block)
    env_block_bg = rect(
        460, 210, 310, 115, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8
    )
    env_block_title = text(
        615, 235, "Захоплене оточення (RAM / Купа)", size=13, color=FIELD, bold=True
    )
    env_vars = mtext(
        615,
        260,
        "struct Env_Record {\n  uint32_t ref_count;   ; керування пам'яттю\n  int captured_x = 42;  ; захоплена змінна\n}",
        size=11,
        color=INK,
    )
    body.extend([env_block_bg, env_block_title, env_vars])

    # Стрілки зв'язку
    arr_code = arrow(270, 165, 455, 125, color=NEG, sw=2.0)
    arr_env = arrow(270, 240, 455, 265, color=FIELD, sw=2.0)
    body.extend([arr_code, arr_env])

    render(os.path.join(IMG_DIR, "fat-pointer.svg"), w, h, *body)


def fig_funarg_escape():
    """3. Проблема funarg та аналіз втечі на купу (Escape Analysis)."""
    w, h = 820, 360
    body = []

    body.append(
        text(
            w / 2,
            30,
            "Проблема funarg: передача вниз проти повернення вгору",
            size=16,
            bold=True,
        )
    )

    # Ліва половина: Downward Funarg (Низхідний funarg)
    down_bg = rect(30, 60, 360, 270, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8)
    down_t = text(210, 88, "Downward Funarg (Низхідний)", size=14, bold=True)
    down_sub = text(
        210,
        108,
        "Замикання передається як аргумент углиб стека",
        size=11,
        color=MUTED,
        italic=True,
    )

    stk_f1 = rect(60, 130, 300, 40, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4)
    stk_f1_t = text(
        210, 155, "Кадр caller(): локальна змінна x", size=12, color=INK
    )

    stk_f2 = rect(60, 180, 300, 40, fill="#eaf0fd", stroke=NEG, sw=1.2, rx=4)
    stk_f2_t = text(
        210, 205, "Кадр sort(arr, predicate) [виконується]", size=12, color=INK
    )

    down_res = rect(60, 240, 300, 65, fill="#e8f8f0", stroke=FIELD, sw=1.5, rx=6)
    down_res_t = mtext(
        210,
        262,
        "Безпечно на стеку (Stack Allocation)\nЧас життя predicate коротший за caller.\nНакладні витрати = 0 байтів на купі.",
        size=11,
        color=FIELD,
        bold=True,
    )

    body.extend([
        down_bg,
        down_t,
        down_sub,
        stk_f1,
        stk_f1_t,
        stk_f2,
        stk_f2_t,
        down_res,
        down_res_t,
    ])

    # Права половина: Upward Funarg (Висхідний funarg)
    up_bg = rect(430, 60, 360, 270, fill="#f8fafc", stroke=LINE, sw=1.2, rx=8)
    up_t = text(610, 88, "Upward Funarg (Висхідний)", size=14, bold=True)
    up_sub = text(
        610,
        108,
        "Замикання повертається назовні або зберігається",
        size=11,
        color=MUTED,
        italic=True,
    )

    up_f1 = rect(460, 130, 300, 40, fill="#fdecea", stroke=POS, sw=1.2, rx=4)
    up_f1_t = text(
        610,
        155,
        "Кадр factory(): знищується під час RET!",
        size=12,
        color=POS,
        bold=True,
    )

    up_arrow = arrow(610, 175, 610, 210, color=POS, sw=1.8)

    up_res = rect(460, 215, 300, 90, fill="#fef2f2", stroke=POS, sw=1.5, rx=6)
    up_res_t = mtext(
        610,
        238,
        "Втеча на купу (Heap Escape)\nЯкщо зберегти на стеку — висячий покажчик!\nКомпілятор переносить оточення на купу\n(malloc / new / garbage collection).",
        size=11,
        color=POS,
        bold=False,
    )

    body.extend(
        [up_bg, up_t, up_sub, up_f1, up_f1_t, up_arrow, up_res, up_res_t]
    )

    render(os.path.join(IMG_DIR, "funarg-escape.svg"), w, h, *body)


if __name__ == "__main__":
    fig_first_class_ops()
    fig_fat_pointer()
    fig_funarg_escape()
    print("All figures generated successfully.")
