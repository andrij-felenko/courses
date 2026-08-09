# -*- coding: utf-8 -*-
"""Фігури до теми «dma-buf: спільний буфер між драйверами»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, 'img')
os.makedirs(IMG, exist_ok=True)


def fig_one_memory_many_addresses():
    """Одна й та сама пам'ять кадру має різний вигляд для процесора й для кожного пристрою."""
    W, H = 1020, 470
    f = []

    lab_x = 24          # ліва колонка підписів
    col_x = 300         # права колонка вмісту
    col_w = 690

    # ── ряд 1: фізична пам'ять ────────────────────────────────────────────
    y1 = 56
    f.append(text(lab_x, y1 + 14, "Фізична пам'ять", size=14, bold=True, anchor="start"))
    f.append(text(lab_x, y1 + 36, "сторінки кадру розкидані", size=12, color=MUTED, anchor="start"))
    cellw, gap = 42, 6
    owned = {1, 2, 5, 8, 9, 12}
    for i in range(14):
        cx = col_x + i * (cellw + gap)
        fill = "#dceffe" if i in owned else FILL
        stroke = NEG if i in owned else "#b9bfc7"
        f.append(rect(cx, y1, cellw, 46, fill=fill, stroke=stroke, sw=1.5, rx=4))
    f.append(text(col_x, y1 + 68, "шість сторінок буфера серед чужих — суцільного шматка ніхто не обіцяв",
                  size=12, color=MUTED, anchor="start"))

    # ── ряд 2: процес ─────────────────────────────────────────────────────
    y2 = 176
    f.append(text(lab_x, y2 + 14, "Процес", size=14, bold=True, anchor="start"))
    f.append(text(lab_x, y2 + 36, "після mmap на дескриптор", size=12, color=MUTED, anchor="start"))
    f.append(fitbox(col_x, y2, col_w, 46, "суцільний віртуальний діапазон", size=13))
    f.append(text(col_x, y2 + 68, "таблиці сторінок зшивають розкидане в один діапазон",
                  size=12, color=MUTED, anchor="start"))

    # ── ряд 3: пристрій за IOMMU ──────────────────────────────────────────
    y3 = 296
    f.append(text(lab_x, y3 + 14, "Пристрій за IOMMU", size=14, bold=True, anchor="start"))
    f.append(text(lab_x, y3 + 36, "камера, GPU", size=12, color=MUTED, anchor="start"))
    f.append(fitbox(col_x, y3, col_w, 46, "суцільний діапазон адрес шини", size=13,
                    fill="#eaf7ee", stroke=FIELD))
    f.append(text(col_x, y3 + 68, "свої таблиці трансляції на кожен пристрій — адреси різні",
                  size=12, color=MUTED, anchor="start"))

    # ── ряд 4: пристрій без IOMMU ─────────────────────────────────────────
    y4 = 400
    f.append(text(lab_x, y4 + 14, "Пристрій без IOMMU", size=14, bold=True, anchor="start"))
    f.append(text(lab_x, y4 + 36, "простий контролер", size=12, color=MUTED, anchor="start"))
    seg = [(0, 130), (150, 90), (270, 200), (500, 190)]
    for sx, sw_ in seg:
        f.append(rect(col_x + sx, y4, sw_, 46, fill="#fdecea", stroke=POS, sw=1.5, rx=4))
    f.append(text(col_x, y4 + 68, "список шматків: адреса й довжина кожного окремо",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'one-memory-many-addresses.svg'), W, H, *f)


def fig_export_import():
    """Життєвий цикл спільного буфера: від dma_buf_fd() до detach."""
    W, H = 1020, 520
    f = []

    EX, US, IM = 175, 505, 845

    f.append(fitbox(EX - 145, 24, 290, 44, "Драйвер-власник (експортер)", size=13, bold=True))
    f.append(fitbox(US - 110, 24, 220, 44, "Простір користувача", size=13, bold=True))
    f.append(fitbox(IM - 145, 24, 290, 44, "Драйвер-споживач (імпортер)", size=13, bold=True))

    # лінії життя: у користувача — коротка, лише поки він тримає дескриптор
    f.append(line(EX, 68, EX, 470, color=MUTED, sw=1.2, dash="5,5"))
    f.append(line(IM, 68, IM, 470, color=MUTED, sw=1.2, dash="5,5"))
    f.append(line(US, 68, US, 178, color=MUTED, sw=1.2, dash="5,5"))

    def step(y, x1, x2, label, color=LINE, dash=False):
        f.append(arrow(x1, y, x2, y, color=color))
        if dash:
            f.append(line(x1, y, x2, y, color=BG, sw=3))
            f.append(line(x1, y, x2, y, color=color, sw=1.6, dash="6,5"))
            f.append(arrow(x2 - 14, y, x2, y, color=color))
        f.append(text((x1 + x2) / 2, y - 12, label, size=12, color=color))

    step(110, EX, US, "dma_buf_fd(): буфер стає дескриптором 7", color=NEG)
    step(160, US, IM, "ioctl: працюй із дескриптором 7", color=NEG)
    step(230, IM, EX, "dma_buf_attach(): ось мій пристрій і його обмеження")
    step(285, EX, IM, "згода або відмова; буфер може переїхати", color=MUTED, dash=True)
    step(345, IM, EX, "dma_buf_map_attachment_unlocked()")
    step(400, EX, IM, "sg_table: адреси в просторі ЦЬОГО пристрою", color=FIELD, dash=True)
    step(455, IM, EX, "unmap і detach, коли пристрій відпрацював")

    f.append(text(24, 502,
                  "Пам'ять живе, доки живий бодай один дескриптор: close() на останньому — і власник її звільняє.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'export-import.svg'), W, H, *f)


def fig_fence_handoff():
    """Спільна пам'ять без спільного часу нічого не варта: передача за огорожами."""
    W, H = 1020, 400
    f = []

    f.append(fitbox(150, 40, 800, 40, "той самий буфер — жодної копії за весь шлях кадру",
                    size=13, fill="#eaf7ee", stroke=FIELD))

    lanes = [
        (130, "Камера", 170, 380, "пише кадр DMA"),
        (215, "GPU", 440, 640, "читає й малює поверх"),
        (300, "Дисплей", 700, 940, "виводить на екран"),
    ]
    for y, name, x1, x2, what in lanes:
        f.append(text(24, y + 22, name, size=14, bold=True, anchor="start"))
        f.append(fitbox(x1, y, x2 - x1, 42, what, size=12))

    # огорожі між смугами
    def fence(x, y_from, y_to, x_to, label):
        f.append(circle(x, y_from, 9, fill="#fdecea", stroke=POS, sw=2))
        f.append(arrow(x + 12, y_from + 6, x_to, y_to, color=POS))
        f.append(text((x + x_to) / 2 + 30, (y_from + y_to) / 2 + 26, label, size=12, color=POS))

    fence(380, 151, 215, 440, "огорожа спрацювала")
    fence(640, 236, 300, 700, "огорожа спрацювала")

    f.append(text(24, 360,
                  "Кожен наступний починає DMA не за годинником, а за сигналом попереднього: інакше він побачить недописаний кадр.",
                  size=12, color=MUTED, anchor="start"))

    render(os.path.join(IMG, 'fence-handoff.svg'), W, H, *f)


def fig_two_processes_one_buffer():
    """Дослід: дескриптор іде сокетом, позначка Б повертається до А тією ж пам'яттю."""
    W, H = 1000, 600
    f = []

    ax, bx, lw = 30, 640, 330
    acx, bcx = ax + lw / 2, bx + lw / 2

    f.append(text(acx, 44, "процес А — виділяє й пише", size=14, bold=True))
    f.append(text(bcx, 44, "процес Б — окремий запуск", size=14, bold=True))

    # ── ліва доріжка ──────────────────────────────────────────────────────
    f.append(fitbox(ax, 64, lw, 44, "1 · alloc із купи system → дескриптор", size=13))
    f.append(fitbox(ax, 118, lw, 44, "2 · mmap: буфер видно процесові А", size=13))
    f.append(fitbox(ax, 172, lw, 44, "3 · SYNC WRITE ▸ візерунок ▸ END", size=13))
    f.append(fitbox(ax, 408, lw, 44, "9 · SYNC READ ▸ бачить позначку Б", size=13,
                    fill="#dceffe", stroke=NEG))

    # ── права доріжка ─────────────────────────────────────────────────────
    f.append(fitbox(bx, 228, lw, 44, "5 · recvmsg → свій номер дескриптора", size=13))
    f.append(fitbox(bx, 282, lw, 44, "6 · lseek → розмір, далі mmap", size=13))
    f.append(fitbox(bx, 336, lw, 44, "7 · SYNC READ ▸ звірка ▸ WRITE ▸ позначка", size=13))

    # ── передача дескриптора туди й відповідь назад ───────────────────────
    f.append(arrow(ax + lw, 250, bx, 250, color=NEG))
    f.append(text(500, 236, "4 · дескриптор сокетом", size=12, color=NEG))
    f.append(text(500, 274, "SCM_RIGHTS + довжина, зерно", size=12, color=MUTED))

    f.append(arrow(bx, 430, ax + lw, 430, color=POS))
    f.append(text(500, 416, "8 · байт «звірено»", size=12, color=POS))

    # ── спільна пам'ять унизу ─────────────────────────────────────────────
    f.append(arrow(acx - 45, 458, acx - 45, 516))
    f.append(arrow(bcx - 45, 386, bcx - 45, 516))
    f.append(fitbox(30, 520, 940, 52, "одні й ті самі фізичні сторінки: жодного байта не скопійовано",
                    size=14, fill="#eafaf1", stroke=FIELD))
    f.append(text(500, 592, "числа дескрипторів різні, адреси після mmap різні — пам'ять одна",
                  size=12, color=MUTED))

    render(os.path.join(IMG, 'two-processes-one-buffer.svg'), W, H, *f)


if __name__ == '__main__':
    fig_one_memory_many_addresses()
    fig_export_import()
    fig_fence_handoff()
    fig_two_processes_one_buffer()
    print("ok")
