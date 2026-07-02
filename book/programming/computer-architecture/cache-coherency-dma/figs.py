import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)


def fig_two_paths():
    # CPU sees cache; DMA sees RAM directly -> two views of the same address
    W, H = 640, 300
    f = []
    # CPU
    f.append(rect(40, 40, 150, 60, rx=10))
    f.append(text(115, 75, "Процесор", 15, bold=True))
    # Cache
    f.append(rect(40, 150, 150, 80, rx=10))
    f.append(text(115, 178, "Кеш", 14, bold=True))
    f.append(text(115, 202, "адр X = 7", 13))
    # RAM
    f.append(rect(450, 95, 150, 90, rx=10))
    f.append(text(525, 128, "ОЗП", 14, bold=True))
    f.append(text(525, 152, "адр X = 3", 13))
    # DMA
    f.append(rect(450, 220, 150, 55, rx=10))
    f.append(text(525, 252, "DMA", 15, bold=True))

    # CPU <-> cache
    f.append(arrow(115, 100, 115, 150))
    f.append(arrow(115, 150, 115, 100))
    # cache <-> RAM (slow, dashed): the link that is stale
    f.append(line(190, 190, 450, 140, dash="6 5"))
    f.append(text(320, 152, "не оновлено", 12, color="#b23"))
    # DMA -> RAM (fresh write)
    f.append(arrow(525, 220, 525, 185))
    f.append(text(600, 205, "запис", 12, anchor="start"))
    # label of conflict
    f.append(text(320, 285, "процесор бачить 7, у пам'яті вже 3", 13, color="#b23", bold=True))
    render(os.path.join(OUT, 'two-views.svg'), W, H, *f, title="Два погляди на одну адресу")


def fig_clean_invalidate():
    # Two directions: clean (before TX), invalidate (after RX)
    W, H = 660, 340
    f = []
    # --- left: CLEAN (CPU -> peripheral) ---
    f.append(textbox(165, 32, "Віддати назовні: CLEAN", 14, fill="#eef4ff", stroke="#4a72c0", bold=True)[0])
    f.append(rect(70, 70, 90, 50, rx=8))
    f.append(text(115, 100, "Кеш", 13, bold=True))
    f.append(text(115, 118, "нове", 11, color="#2a7"))
    f.append(rect(70, 200, 90, 50, rx=8))
    f.append(text(115, 230, "ОЗП", 13, bold=True))
    f.append(arrow(115, 120, 115, 200))
    f.append(text(150, 165, "clean", 12, anchor="start", color="#2a7"))
    f.append(text(240, 165, "→ DMA читає", 12, anchor="start"))
    f.append(text(115, 285, "спершу зіштовхнути,", 11))
    f.append(text(115, 302, "потім пускати DMA", 11))

    # divider
    f.append(line(330, 55, 330, 310, dash="4 6"))

    # --- right: INVALIDATE (peripheral -> CPU) ---
    f.append(textbox(495, 32, "Прийняти ззовні: INVALIDATE", 13, fill="#fff0ee", stroke="#c0574a", bold=True)[0])
    f.append(rect(450, 70, 90, 50, rx=8))
    f.append(text(495, 100, "Кеш", 13, bold=True))
    f.append(text(495, 118, "старе ✗", 11, color="#b23"))
    f.append(rect(450, 200, 90, 50, rx=8))
    f.append(text(495, 224, "ОЗП", 13, bold=True))
    f.append(text(495, 242, "нове (DMA)", 10, color="#2a7"))
    f.append(arrow(495, 200, 495, 122))
    f.append(text(530, 165, "invalidate", 12, anchor="start", color="#b23"))
    f.append(text(495, 285, "викинути старе, щоб", 11))
    f.append(text(495, 302, "перечитати з ОЗП", 11))
    render(os.path.join(OUT, 'clean-invalidate.svg'), W, H, *f, title="Clean і invalidate")


def fig_line_granularity():
    # A cache line covers more than the buffer -> false sharing on invalidate
    W, H = 640, 250
    f = []
    f.append(text(320, 30, "Одна лінія кеша = 32 байти", 14, bold=True))
    x0, y0, cw = 60, 70, 65
    labels = ["сусід", "буфер", "буфер", "буфер", "сусід"]
    fills = ["#f2d9d5", "#d9ecdf", "#d9ecdf", "#d9ecdf", "#f2d9d5"]
    for i, (lab, fl) in enumerate(zip(labels, fills)):
        f.append(rect(x0 + i * cw, y0, cw, 55, fill=fl, rx=4))
        f.append(text(x0 + i * cw + cw / 2, y0 + 32, lab, 12))
    # bracket = one line
    f.append(line(x0, y0 + 75, x0 + 5 * cw, y0 + 75))
    f.append(line(x0, y0 + 70, x0, y0 + 80))
    f.append(line(x0 + 5 * cw, y0 + 70, x0 + 5 * cw, y0 + 80))
    f.append(text(x0 + 5 * cw / 2, y0 + 98, "invalidate стирає всю лінію", 12, color="#b23"))
    f.append(text(320, 200, "невирівняний буфер жертвує чужими даними у крайніх лініях", 12))
    f.append(text(320, 222, "→ буфер вирівнюють на 32 байти й доводять розмір до лінії", 12, bold=True))
    render(os.path.join(OUT, 'line-granularity.svg'), W, H, *f, title="Зернистість лінії")


def fig_dma_timeline():
    # DMA born 1950s; write-back cache (and thus the coherence problem) decades later
    W, H = 700, 300
    f = []
    f.append(text(W / 2, 28, "DMA — з 1950-х; проблема когерентності — набагато пізніше", 14, bold=True))
    # baseline axis
    ax_y = 150
    x0, x1 = 60, 640
    f.append(line(x0, ax_y, x1, ax_y, sw=2))
    # map a year to x (1950..2000)
    def X(year):
        return x0 + (x1 - x0) * (year - 1950) / (2000 - 1950)
    # DMA-era events (above axis)
    dma = [
        (1954, "DYSEAC\nпристрій → пам'ять\n+ переривання", FIELD),
        (1958, "IBM 709\nканали:\nспівпроцесор I/O", FIELD),
        (1979, "Intel 8237\n(IBM PC 1981)\nDMA всім", FIELD),
    ]
    for yr, lab, col in dma:
        x = X(yr)
        f.append(line(x, ax_y, x, ax_y - 20, color=col, sw=2))
        f.append(circle(x, ax_y - 20, 5, fill=col, stroke=col))
        f.append(textbox(x, ax_y - 62, lab, 10, fill="#eaf6ee", stroke=col)[0])
        f.append(text(x, ax_y + 20, str(yr), 11, bold=True))
    # the later problem (below axis): write-back cache -> coherence gap
    xc = X(1990)
    f.append(line(xc, ax_y, xc, ax_y + 24, color=POS, sw=2))
    f.append(circle(xc, ax_y + 24, 5, fill=POS, stroke=POS))
    f.append(textbox(xc, ax_y + 62, "кеш зі зворотним записом\n→ ось тут народжується\nпроблема когерентності", 10,
                     fill="#fdecea", stroke=POS)[0])
    # gap bracket
    f.append(text(W / 2, ax_y + 108, "десятиліття між винаходом DMA і появою проблеми на його стику з кешем",
                  11, color=MUTED))
    render(os.path.join(OUT, 'dma-timeline.svg'), W, H, *f, title=None)


if __name__ == '__main__':
    fig_two_paths()
    fig_clean_invalidate()
    fig_line_granularity()
    fig_dma_timeline()
    print("ok")
