# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(OUT, exist_ok=True)

AMBER   = "#e08a1e"
RED_T   = "#fdecea"
AMBER_T = "#fdf0dd"
GREEN_T = "#e7f6ec"
BLUE_T  = "#eaf0fd"
NEUT    = "#eef2f6"

def polyline(pts, color=LINE, sw=1.5, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    points_str = ' '.join('%.1f,%.1f' % (x, y) for x, y in pts)
    return '<polyline points="%s" fill="none" stroke="%s" stroke-width="%.1f"%s/>' % (points_str, color, sw, d)


def fig_envelope_four_pillars():
    """Чотири фізичні стовпи оцінки ємності системи (Network, RAM, CPU, Disk IOPS)."""
    W, H = 1040, 440
    f = []

    # ── Заголовок блоку вхідного флоту ──
    f.append(fitbox(40, 40, 960, 44, "Флот Digital Homes: 200 000 активних хабів · 30 с інтервал телеметрії",
                    size=15, bold=True, fill=BLUE_T, stroke=NEG))

    # Стовпець 1: Мережа (Network)
    f.append(fitbox(40, 110, 225, 270,
                    "1. Мережева смуга\n\n• 6 667 msg/s baseline\n• 20 000 msg/s peak (3x)\n• Пакет: 500B + 100B framing\n• Смуга: 96 Mbps peak\n• Пакетний темп: 20k pps",
                    size=13, fill=NEUT, stroke="#b8bfc8"))
    f.append(fitbox(40, 390, 225, 36, "Ліміт: NGINX / L4 LB", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Стовпець 2: Пам'ять (RAM)
    f.append(fitbox(285, 110, 225, 270,
                    "2. Оперативна пам'ять\n\n• 200 000 TCP-сокетів\n• Kernel socket: 16 KB/сокет\n• Gateway state: 32 KB/сесія\n• Разом: ~9.6 GB RAM\n• Буфер шторму: +6.4 GB",
                    size=13, fill=NEUT, stroke="#b8bfc8"))
    f.append(fitbox(285, 390, 225, 36, "Ліміт: 16 GB Node RAM", size=12, bold=True, fill=GREEN_T, stroke=FIELD))

    # Стовпець 3: Процесор (CPU)
    f.append(fitbox(530, 110, 225, 270,
                    "3. Обчислення (CPU)\n\n• TLS crypto: 0.5 ms/handshake\n• Deserialization: 5 µs/msg\n• Steady state: ~0.1 core\n• Reconnect storm (1.6k/s):\n  ~0.9 CPU cores crypto",
                    size=13, fill=NEUT, stroke="#b8bfc8"))
    f.append(fitbox(530, 390, 225, 36, "Ліміт: Crypto Offload", size=12, bold=True, fill=AMBER_T, stroke=AMBER))

    # Стовпець 4: Диск та IOPS
    f.append(fitbox(775, 110, 225, 270,
                    "4. Дискова система\n\n• Сирі записи: 20 000 IOPS\n• Батчинг (100 ms flush):\n  10 записів/с по 1 MB\n• Throughput: 10 MB/s WAL\n• Збереження 30d: ~8.6 TB",
                    size=13, fill=NEUT, stroke="#b8bfc8"))
    f.append(fitbox(775, 390, 225, 36, "Ліміт: NVMe Sequential WAL", size=12, bold=True, fill=RED_T, stroke=POS))

    render(os.path.join(OUT, 'envelope-four-pillars.svg'), W, H, *f,
           title="Чотири фізичні виміри розрахунку ємності флоту з 200k пристроїв")


def fig_reconnect_storm_cpu():
    """Сплеск навантаження CPU та RAM під час шторму реконектів після блекауту."""
    W, H = 1020, 420
    f = []

    # Шкала часу та фази
    f.append(fitbox(40, 40, 280, 50, "Фаза 1: Нормальний режим\n200k підключень · Steady State",
                    size=13, bold=True, fill=GREEN_T, stroke=FIELD))
    f.append(fitbox(340, 40, 340, 50, "Фаза 2: Блекаут та повернення світла\n100k пристроїв одночасно у TLS-хендшейк",
                    size=13, bold=True, fill=RED_T, stroke=POS))
    f.append(fitbox(700, 40, 280, 50, "Фаза 3: Стабілізація\nСесії відновлено · Jitter згладив пік",
                    size=13, bold=True, fill=BLUE_T, stroke=NEG))

    # Графік CPU vs Network
    f.append(line(40, 360, 980, 360, color=LINE, sw=2))
    f.append(line(40, 110, 40, 360, color=LINE, sw=2))

    # Позначки осі Y
    f.append(text(30, 120, "100% CPU / 100k pps", size=11, color=MUTED, anchor="end"))
    f.append(text(30, 240, "50% CPU", size=11, color=MUTED, anchor="end"))
    f.append(text(30, 355, "0", size=11, color=MUTED, anchor="end"))

    # Пунктир критичної стелі CPU
    f.append(line(40, 140, 980, 140, color=POS, sw=1.5, dash="6 4"))
    f.append(fitbox(680, 115, 290, 24, "Критична стеля CPU (100% saturation)", size=11, fill=BG, stroke=POS, color=POS, bold=True))

    # Крива трафіку (синя)
    f.append(polyline([(40, 330), (320, 330), (360, 350), (420, 200), (550, 220), (700, 320), (980, 330)],
                      color=NEG, sw=3))
    f.append(fitbox(600, 210, 220, 28, "Мережевий потік (TLS Packets)", size=11, fill=BLUE_T, stroke=NEG, color=NEG, bold=True))

    # Крива криптографічного CPU (червона - сплеск TLS handshake)
    f.append(polyline([(40, 345), (320, 345), (340, 355), (390, 145), (460, 150), (620, 260), (700, 340), (980, 345)],
                      color=POS, sw=3, dash="4 2"))
    f.append(fitbox(380, 155, 250, 28, "CPU Сплеск (TLS 1.3 Handshakes)", size=11, fill=RED_T, stroke=POS, color=POS, bold=True))

    # Пояснювальний виклиок
    f.append(fitbox(460, 280, 360, 60, "Без TLS Session Resumption та Jitter\nсистема впадає у CPU Throttling і провалює ACK",
                    size=12, fill=AMBER_T, stroke=AMBER))

    render(os.path.join(OUT, 'reconnect-storm-cpu.svg'), W, H, *f,
           title="Динаміка навантаження CPU та мережі під час шторму реконектів")


def fig_iops_batching_transformation():
    """Трансформація хаотичних хаотичних IOPS у послідовний потоковий WAL через кольцевий буфер."""
    W, H = 1020, 380
    f = []

    # Вхідний хаотичний потік
    f.append(fitbox(40, 60, 240, 260,
                    "Вхідні події телеметрії\n\n20 000 msg/s peak\n500 B / повідомлення\n\nНесинхронізовані\nпотоки від 200k хабів",
                    size=13, fill=RED_T, stroke=POS))

    # Стрілка у кільцевий буфер
    f.append(arrow(280, 190, 340, 190, color=LINE, sw=2))
    f.append(fitbox(285, 155, 50, 24, "20k IOPS", size=10, fill=BG, stroke=LINE, color=MUTED))

    # Буфер у пам'яті (Ring Buffer / Batcher)
    f.append(fitbox(340, 60, 320, 260,
                    "Ring Buffer / In-Memory Batcher\n\n• Накопичення за 100 ms вікно\n• Агрегація у блок 1 MB\n• Сортування за пристроєм\n• Zero-allocation memory pool",
                    size=13, fill=AMBER_T, stroke=AMBER))

    # Стрілка на накопичений флаш
    f.append(arrow(660, 190, 720, 190, color=LINE, sw=2))
    f.append(fitbox(662, 155, 56, 24, "10 flush/s", size=10, fill=BG, stroke=FIELD, color=FIELD, bold=True))

    # Вихідний диск (Sequential WAL)
    f.append(fitbox(720, 60, 260, 260,
                    "Дисковий масив (WAL SSD)\n\n• 10 послідовних записів/с\n• 10 MB/s throughput\n• 10 IOPS замість 20 000!\n• Захист накопичувача від зносу",
                    size=13, fill=GREEN_T, stroke=FIELD))

    render(os.path.join(OUT, 'iops-batching-transformation.svg'), W, H, *f,
           title="Перетворення 20 000 поодиноких записів на 10 послідовних блоків дискового WAL")


if __name__ == '__main__':
    fig_envelope_four_pillars()
    fig_reconnect_storm_cpu()
    fig_iops_batching_transformation()
    print("Figures generated successfully.")
