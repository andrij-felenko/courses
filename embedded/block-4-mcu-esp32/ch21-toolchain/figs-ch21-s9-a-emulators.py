# -*- coding: utf-8 -*-
"""
Фігури для вставки ch21-s9-a-emulators (⚙️ Емулятори МК).
Чистий Python, без сторонніх залежностей. Вивід → ./img/.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '_tools'))
from svgkit import *

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
os.makedirs(OUT, exist_ok=True)


def fig_emulator_stack():
    """
    Рис. 4.2.9a.1.
    Ліворуч — внутрішній стек емулятора (три яруси знизу-вгору):
      ядро CPU → карта пам'яті → модель периферії; зі стрілкою .elf зверху.
    Праворуч — вісь-сходинки: Шар 1 (хост) → Шар 2 (моки) → Емулятор → Шар 3 (залізо),
      з підписами осей «швидше/масштабованіше ↔ точніше/ближче до заліза».
    """
    W, H = 820, 420

    # ── колір-акценти (з palette svgkit) ────────────────────────────────────
    LAYER_FILL  = "#e8f4fd"   # ніжно-блакитний для ярусів стека
    LAYER_STR   = "#2457d6"   # NEG — синій контур
    EMU_FILL    = "#fff6e0"   # жовтуватий — виділення «емулятор» на осі
    EMU_STR     = "#c0392b"   # POS — червоний контур
    AXIS_COLOR  = "#6b7280"   # MUTED

    elems = []

    # ════════════════════════════════════════════════════════════════════════
    # ЛІВА ЧАСТИНА — стек емулятора (x: 40..390)
    # ════════════════════════════════════════════════════════════════════════
    left_cx = 215   # центр X лівої частини

    # Заголовок лівої панелі
    elems.append(text(left_cx, 32, "Стек емулятора", size=16, color=INK,
                      anchor="middle", bold=True))

    # Три яруси знизу-вгору
    # Ярус 1 (дно): ядро CPU
    b1_y = 310; b_h = 72; b_w = 300
    b1x = left_cx - b_w / 2
    box1, _, _ = textbox(left_cx, b1_y + b_h / 2,
                         "ядро CPU\n(виконує машинні інструкції .elf)",
                         size=13, pad=12, fill=LAYER_FILL, stroke=LAYER_STR, sw=2.0)
    elems.append(box1)

    # Ярус 2: карта пам'яті
    b2_y = b1_y - b_h - 14
    box2, _, _ = textbox(left_cx, b2_y + b_h / 2,
                         "карта пам'яті\n(масив = Flash/RAM за адресами)",
                         size=13, pad=12, fill=LAYER_FILL, stroke=LAYER_STR, sw=2.0)
    elems.append(box2)

    # Ярус 3 (вершина стека): модель периферії
    b3_y = b2_y - b_h - 14
    box3, _, _ = textbox(left_cx, b3_y + b_h / 2,
                         "модель периферії\n(перехоплює записи в регістри:\nUART / ADC / GPIO)",
                         size=13, pad=12, fill=LAYER_FILL, stroke=LAYER_STR, sw=2.0)
    elems.append(box3)

    # Вертикальні з'єднувальні стрілки між ярусами (знизу-вгору)
    arrow_x = left_cx
    # між ярусом 1 і 2
    elems.append(arrow(arrow_x, b1_y - 2, arrow_x, b2_y + b_h + 2, color=LAYER_STR, sw=2.0))
    # між ярусом 2 і 3
    elems.append(arrow(arrow_x, b2_y - 2, arrow_x, b3_y + b_h + 2, color=LAYER_STR, sw=2.0))

    # Стрілка «той самий .elf» зверху вниз — входить у стек
    elf_y_top = b3_y - 52
    elf_y_bot = b3_y
    elems.append(arrow(arrow_x, elf_y_top + 2, arrow_x, elf_y_bot - 2,
                       color=EMU_STR, sw=2.5))
    b_elf, _, _ = textbox(left_cx, elf_y_top - 12,
                          "той самий .elf, що й у чіп",
                          size=12, pad=8, fill="#fdecea", stroke=EMU_STR, sw=1.8)
    elems.append(b_elf)

    # Підпис знизу
    elems.append(text(left_cx, H - 14,
                      "прошивка виконується на ПІДРОБЛЕНИХ регістрах — рівень нижче, ніж мок-функція",
                      size=11, color=AXIS_COLOR, anchor="middle"))

    # ════════════════════════════════════════════════════════════════════════
    # ВЕРТИКАЛЬНИЙ РОЗДІЛЬНИК
    # ════════════════════════════════════════════════════════════════════════
    div_x = 420
    elems.append(line(div_x, 18, div_x, H - 10, color="#cccccc", sw=1.2, dash="4 4"))

    # ════════════════════════════════════════════════════════════════════════
    # ПРАВА ЧАСТИНА — вісь-сходинки (x: 430..810)
    # ════════════════════════════════════════════════════════════════════════
    right_cx = 620
    elems.append(text(right_cx, 32, "Місце на піраміді тестів", size=16, color=INK,
                      anchor="middle", bold=True))

    # Горизонтальна вісь «швидко ↔ точно»
    ax_y   = H - 48
    ax_x1  = 438
    ax_x2  = 806
    # Ліворуч — «швидше / масштабованіше»
    elems.append(text(ax_x1 + 2, ax_y + 22, "швидше / масштабованіше →",
                      size=11, color=AXIS_COLOR, anchor="start"))
    # Праворуч — «точніше / ближче до заліза»
    elems.append(text(ax_x2 - 2, ax_y + 22, "← точніше / ближче до заліза",
                      size=11, color=AXIS_COLOR, anchor="end"))
    # Сама вісь (горизонтальна)
    elems.append(arrow(ax_x2, ax_y, ax_x1, ax_y, color=AXIS_COLOR, sw=1.5))
    elems.append(arrow(ax_x1, ax_y, ax_x2, ax_y, color=AXIS_COLOR, sw=1.5))

    # Чотири рівні на осі (сходинки зліва-направо = швидко→точно)
    steps = [
        ("Шар 1\nхост-тести\n(x86, не .elf)", "#eef6ef", FIELD, False),
        ("Шар 2\nмоки\n(хост + mock-функції)", "#eef6ef", FIELD, False),
        ("Емулятор\n(той самий .elf\nна підробленому чипі)", EMU_FILL, EMU_STR, True),
        ("Шар 3\nзалізо\n(реальний чіп)", "#fdecea", "#c0392b", False),
    ]
    n_steps = len(steps)
    step_w = 82
    step_gap = (ax_x2 - ax_x1 - n_steps * step_w) / (n_steps - 1)
    step_h = [80, 110, 140, 170]  # висота колонки (сходинки ростуть)

    for i, (label, sfill, sstroke, is_emu) in enumerate(steps):
        sx = ax_x1 + i * (step_w + step_gap)
        sh = step_h[i]
        sy = ax_y - sh
        sw_val = 2.5 if is_emu else 1.8
        fbox = fitbox(sx, sy, step_w, sh, label, size=11,
                      fill=sfill, stroke=sstroke, sw=sw_val)
        elems.append(fbox)

    # Підпис «↕ пропущена сходинка» між Шаром 2 і Емулятором
    gap_cx = ax_x1 + (step_w + step_gap) * 1.5 + step_w / 2
    elems.append(text(gap_cx, ax_y - 155, "↕ пропущена", size=10, color=EMU_STR, anchor="middle", bold=True))
    elems.append(text(gap_cx, ax_y - 143, "сходинка", size=10, color=EMU_STR, anchor="middle", bold=True))

    path = os.path.join(OUT, "fig-21-9a-1-emulator-stack.svg")
    render(path, W, H, *elems)
    print("wrote fig-21-9a-1-emulator-stack.svg")


if __name__ == "__main__":
    fig_emulator_stack()
