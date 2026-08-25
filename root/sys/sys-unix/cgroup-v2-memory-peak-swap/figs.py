# -*- coding: utf-8 -*-
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


def fig_memory_limits():
    W, H = 1000, 680
    p = []

    # Заголовок блоку cgroup
    p.append(fitbox(50, 40, 900, 44,
                    "Ієрархічна структура межових рівнів контролера пам'яті Cgroups v2",
                    size=14.5, fill="#f4f6f8", stroke=INK, sw=1.5, bold=True))

    # Контейнер Cgroup
    p.append(rect(120, 110, 420, 490, fill="#f8fafc", stroke="#64748b", sw=1.8, rx=6))
    p.append(text(330, 138, "Cgroup: /system.slice/db.service", size=15, color=INK, bold=True))

    # Шкала рівнів
    # 1. memory.max (Жорстка стеля)
    p.append(line(100, 180, 560, 180, color="#dc2626", sw=2.2, dash="6 4"))
    p.append(fitbox(580, 160, 360, 40,
                    "memory.max (Жорсткий ліміт) -> OOM Killer якщо reclaim не звільнив RAM",
                    size=12.5, fill="#fef2f2", stroke="#dc2626", sw=1.4))

    # 2. memory.high (М'який ліміт гальмування)
    p.append(line(100, 260, 560, 260, color="#ea580c", sw=2.0, dash="6 4"))
    p.append(fitbox(580, 240, 360, 40,
                    "memory.high (М'яке гальмо) -> Штрафний сон при виділенні та посилений reclaim",
                    size=12.5, fill="#fff7ed", stroke="#ea580c", sw=1.4))

    # 3. memory.peak (Вотермарка піка)
    p.append(line(140, 215, 520, 215, color="#9333ea", sw=2.0))
    p.append(fitbox(580, 195, 360, 38,
                    "memory.peak (Пікове споживання) -> Історичний максимум memory.current",
                    size=12.5, fill="#faf5ff", stroke="#9333ea", sw=1.4))

    # 4. Поточний обсяг memory.current
    p.append(rect(160, 310, 340, 270, fill="#dbeafe", stroke="#2563eb", sw=1.6, rx=4))
    p.append(text(330, 340, "memory.current (Поточна RAM)", size=13.5, color="#1e40af", bold=True))

    # 5. memory.low (М'який захист)
    p.append(line(100, 440, 560, 440, color="#16a34a", sw=2.0, dash="6 4"))
    p.append(fitbox(580, 420, 360, 40,
                    "memory.low (М'яка гарантія) -> Захист кешу від витіснення (best-effort)",
                    size=12.5, fill="#f0fdf4", stroke="#16a34a", sw=1.4))

    # 6. memory.min (Тверда гарантія)
    p.append(line(100, 520, 560, 520, color="#0284c7", sw=2.2, dash="6 4"))
    p.append(fitbox(580, 500, 360, 40,
                    "memory.min (Тверда гарантія) -> Абсолютна недоторканність при reclaim",
                    size=12.5, fill="#f0f9ff", stroke="#0284c7", sw=1.4))

    # 7. Swap — окремий простір ПІД групою, а не рівень усередині шкали RAM
    p.append(line(100, 610, 560, 610, color="#7e22ce", sw=2.0, dash="4 4"))
    p.append(rect(160, 615, 340, 50, fill="#f3e8ff", stroke="#7e22ce", sw=1.4, rx=4))
    p.append(text(330, 645, "Простір підкачки Swap", size=12, color="#6b21a8"))
    p.append(fitbox(580, 615, 360, 50,
                    "memory.swap.max / high -> Ліміт анонімних сторінок, витіснених із цієї групи",
                    size=12.5, fill="#faf5ff", stroke="#7e22ce", sw=1.4))

    render(os.path.join(OUT, "cgroup-memory-limits.svg"), W, H, *p,
           title="Обмеження, гарантії та піки споживання пам'яті у Cgroups v2")


def fig_throttling_flow():
    W, H = 1040, 720
    p = []

    p.append(fitbox(50, 40, 940, 44,
                    "Алгоритм зворотного тиску (Backpressure) та обробки лімітів у mem_cgroup",
                    size=14.5, fill="#f4f6f8", stroke=INK, sw=1.5, bold=True))

    # Крок 1: Запит на виділення пам'яті
    p.append(fitbox(370, 105, 300, 54,
                    ["Процес викликає alloc_pages()", "Заряджання сторінки в mem_cgroup"],
                    size=13, fill="#eef3fb", stroke="#1d4ed8", sw=1.5))
    p.append(arrow(520, 160, 520, 190))

    # Перевірка memory.max
    p.append(fitbox(320, 195, 400, 54,
                    ["Перевірка: memory.current > memory.max ?"],
                    size=13.5, fill="#fef2f2", stroke="#dc2626", sw=1.6, bold=True))

    # Гілка ТАК (перевищено max)
    p.append(arrow(720, 222, 820, 222))
    p.append(text(760, 212, "ТАК", size=12, color="#dc2626", bold=True))
    p.append(fitbox(825, 195, 175, 54,
                    ["Direct Reclaim", "Спроба звільнити RAM"],
                    size=12.5, fill="#fff7ed", stroke="#ea580c", sw=1.4))

    p.append(arrow(912, 250, 912, 290))
    p.append(fitbox(810, 295, 205, 58,
                    ["Reclaim неуспішний?", "memory.swap.max досягнуто?"],
                    size=12.5, fill="#fef2f2", stroke="#dc2626", sw=1.5))

    p.append(arrow(912, 354, 912, 395))
    p.append(fitbox(805, 400, 215, 60,
                    ["cgroup OOM Killer", "memory.oom.group: уся група"],
                    size=13, fill="#dc2626", stroke="#7f1d1d", sw=1.8, color="#ffffff", bold=True))

    # Гілка НІ (під max)
    p.append(arrow(520, 250, 520, 295))
    p.append(text(530, 275, "НІ", size=12, color="#16a34a", bold=True))

    # Перевірка memory.high
    p.append(fitbox(320, 300, 400, 54,
                    ["Перевірка: memory.current > memory.high ?"],
                    size=13.5, fill="#fff7ed", stroke="#ea580c", sw=1.6, bold=True))

    # Гілка ТАК (перевищено high)
    p.append(arrow(320, 327, 210, 327))
    p.append(text(250, 317, "ТАК", size=12, color="#ea580c", bold=True))
    p.append(fitbox(50, 295, 155, 64,
                    ["Асинхронний Reclaim", "mem_cgroup_handle_over_high"],
                    size=12.5, fill="#fff7ed", stroke="#ea580c", sw=1.4))

    p.append(arrow(127, 360, 127, 405))
    p.append(fitbox(30, 410, 195, 64,
                    ["Обчислення penalty sleep", "Затримка виходу з ядра"],
                    size=12.5, fill="#fef3c7", stroke="#d97706", sw=1.5))

    p.append(arrow(127, 475, 127, 520))
    p.append(fitbox(30, 525, 195, 60,
                    ["Throttling потоку", "Зворотний тиск на alloc"],
                    size=12.5, fill="#fff7ed", stroke="#ea580c", sw=1.5, bold=True))

    # Гілка НІ (під high)
    p.append(arrow(520, 355, 520, 530))
    p.append(text(530, 420, "НІ", size=12, color="#16a34a", bold=True))

    # Успішне виділення
    p.append(arrow(127, 586, 520, 586))
    p.append(fitbox(370, 560, 300, 52,
                    ["Виділення успішне", "Повернення в простір користувача"],
                    size=13.5, fill="#f0fdf4", stroke="#16a34a", sw=1.6, bold=True))

    # Примітка знизу
    p.append(fitbox(50, 640, 940, 56,
                    ["Захист memory.min та memory.low враховується під час Reclaim: сторінки захищених груп",
                     "пропускаються під час вибору кандидатів на витіснення."],
                    size=12.5, fill="#f4f6f8", stroke=INK, sw=1.3))

    render(os.path.join(OUT, "cgroup-throttling-flow.svg"), W, H, *p,
           title="Послідовність обробки memory.high та memory.max у ядрі")


fig_memory_limits()
fig_throttling_flow()
print("SVG figures generated successfully.")
