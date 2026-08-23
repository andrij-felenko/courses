# -*- coding: utf-8 -*-
"""Генератор SVG-фігур для теми «Як читати цифри пам'яті й не обманутися»."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "scripts"))
from svgkit import *

IMG_DIR = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(IMG_DIR, exist_ok=True)


def fig_metrics_layering():
    """Фігура 1: Шари обліку пам'яті: від віртуального простору до USS і брудних сторінок."""
    w, h = 880, 440
    frags = []

    # Заголовок зверху
    frags.append(text(w / 2, 28, "Шари метрик пам'яті: від віртуальної карти до вартості звільнення", size=16, bold=True))

    # Ліва колонка: Віртуальний адресний простір (VSZ / VIRT)
    frags.append(rect(40, 60, 250, 340, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(165, 85, "Віртуальний простір (VSZ / VIRT)", size=13, bold=True, color=INK))
    frags.append(text(165, 103, "Дозволені діапазони адрес (VMA)", size=11, color=MUTED))

    # Складові VSZ, що не в RSS
    frags.append(fitbox(55, 120, 220, 50, "Арени алокатора (по 64 МіБ)\nСтеки потоків (по 8 МіБ)", size=11, fill="#edf2f7", stroke="#cbd5e1"))
    frags.append(fitbox(55, 180, 220, 50, "Сторожові сторінки PROT_NONE\nРозріджені відображення mmap", size=11, fill="#edf2f7", stroke="#cbd5e1"))
    frags.append(fitbox(55, 240, 220, 50, "Тіньова пам'ять (ASan/санітайзери)\nНезаселені сторінки в карті", size=11, fill="#edf2f7", stroke="#cbd5e1"))

    # Вкладена заселена частина (RSS)
    frags.append(rect(55, 300, 220, 85, fill="#e0f2fe", stroke=NEG, sw=1.8, rx=6))
    frags.append(text(165, 325, "Заселена пам'ять (RSS / RES)", size=12, bold=True, color=NEG))
    frags.append(text(165, 345, "Сторінки з чинним записом у PTE", size=11, color=INK))
    frags.append(text(165, 365, "Фізично присутні в RAM кадри", size=11, color=MUTED))

    # Стрілка між VSZ і RSS
    frags.append(arrow(295, 342, 335, 342, color=NEG, sw=2))

    # Середня колонка: Структура RSS (Спільне vs Приватне / PSS)
    frags.append(rect(345, 60, 260, 340, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(475, 85, "Розкладка RSS: PSS і USS", size=13, bold=True, color=FIELD))
    frags.append(text(475, 103, "Поділ за винятковістю володіння", size=11, color=MUTED))

    # Спільна частина
    frags.append(rect(360, 120, 230, 95, fill="#fef9c3", stroke="#ca8a04", sw=1.5, rx=6))
    frags.append(text(475, 142, "Спільні кадри (Shared / PSS)", size=12, bold=True, color="#854d0e"))
    frags.append(text(475, 162, "Код libc, виконуваний бінарник", size=11, color=INK))
    frags.append(text(475, 180, "Спільна пам'ять, fork COW до запису", size=11, color=MUTED))
    frags.append(text(475, 198, "У PSS входить як: 1/N кадру", size=11, bold=True, color="#854d0e"))

    # Приватна частина (USS)
    frags.append(rect(360, 230, 230, 155, fill="#eff6ff", stroke=NEG, sw=1.5, rx=6))
    frags.append(text(475, 255, "Виняткова пам'ять (USS)", size=12, bold=True, color=NEG))
    frags.append(text(475, 273, "Кадри, де mapcount == 1 (лише цей процес)", size=10, color=MUTED))

    # Вкладені Private Clean vs Dirty
    frags.append(fitbox(370, 285, 210, 42, "Private_Clean (файловий код/mmap)\nЗвільнення: миттєве (диск є)", size=10, fill="#ffffff", stroke="#93c5fd"))
    frags.append(fitbox(370, 335, 210, 42, "Private_Dirty (купа, стек, анонімні)\nЗвільнення: лише через своп/смерть", size=10, fill="#fee2e2", stroke=POS, bold=True, color=POS))

    # Стрілка між USS і правою колонкою
    frags.append(arrow(610, 356, 645, 356, color=POS, sw=2))

    # Права колонка: Системні компоненти поза процесом
    frags.append(rect(655, 60, 190, 340, fill="#fdf4ff", stroke="#9333ea", sw=1.5, rx=8))
    frags.append(text(750, 85, "Системний контекст", size=13, bold=True, color="#9333ea"))
    frags.append(text(750, 103, "Пам'ять поза RSS процесів", size=11, color=MUTED))

    frags.append(fitbox(665, 120, 170, 55, "Кеш сторінок (Page Cache)\nЧисті сторінки файлів\n(MemAvailable)", size=10, fill="#f3e8ff", stroke="#d8b4fe"))
    frags.append(fitbox(665, 185, 170, 55, "Своп (Swap / zram)\nАнонімні сторінки на диску\n(не входить у RSS)", size=10, fill="#f3e8ff", stroke="#d8b4fe"))
    frags.append(fitbox(665, 250, 170, 65, "Пам'ять ядра:\nSReclaimable (dentry/inode)\nSUnreclaim + PageTables\nСтеки ядра + сокети", size=10, fill="#f3e8ff", stroke="#d8b4fe"))
    frags.append(fitbox(665, 325, 170, 60, "Реальна ціна OOM:\nЗвільняється лише:\nUSS + PageTables + Swap\n(НЕ повний RSS!)", size=10, fill="#fee2e2", stroke=POS, bold=True, color=POS))

    render(os.path.join(IMG_DIR, "metrics-layering.svg"), w, h, *frags)


def fig_reclaim_watermarks_psi():
    """Фігура 2: Водяні знаки витіснення (min/low/high), kswapd, прямий відбір і тиск PSI."""
    w, h = 880, 420
    frags = []

    frags.append(text(w / 2, 28, "Шкала вільної пам'яті: водяні знаки, kswapd, прямий відбір і PSI", size=16, bold=True))

    # Стовпчик шкали пам'яті
    frags.append(rect(60, 65, 260, 320, fill="#f8fafc", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(190, 90, "Шкала вільної RAM (Zone)", size=13, bold=True))

    # Зони шкали
    # 1. Достаток (> high)
    frags.append(rect(75, 105, 230, 55, fill="#dcfce7", stroke=FIELD, sw=1.5, rx=4))
    frags.append(text(190, 128, "Зона спокою (> high)", size=12, bold=True, color=FIELD))
    frags.append(text(190, 146, "Виділення миттєве, kswapd спить", size=10, color=INK))

    # Лінія high
    frags.append(line(50, 160, 320, 160, color=FIELD, sw=2, dash="4,4"))
    frags.append(text(45, 164, "high", size=11, bold=True, color=FIELD, anchor="end"))

    # 2. Фоновий відбір (low .. high)
    frags.append(rect(75, 165, 230, 65, fill="#fef9c3", stroke="#ca8a04", sw=1.5, rx=4))
    frags.append(text(190, 188, "Фоновий відбір (low .. high)", size=12, bold=True, color="#854d0e"))
    frags.append(text(190, 206, "kswapd прокидається й чистить кеш", size=10, color=INK))
    frags.append(text(190, 222, "Затримка процесів: 0 мкс", size=10, bold=True, color="#854d0e"))

    # Лінія low
    frags.append(line(50, 230, 320, 230, color="#ca8a04", sw=2, dash="4,4"))
    frags.append(text(45, 234, "low", size=11, bold=True, color="#ca8a04", anchor="end"))

    # 3. Прямий відбір (min .. low)
    frags.append(rect(75, 235, 230, 75, fill="#fed7aa", stroke="#ea580c", sw=1.5, rx=4))
    frags.append(text(190, 258, "Прямий відбір (min .. low)", size=12, bold=True, color="#c2410c"))
    frags.append(text(190, 276, "direct reclaim: процес чистить сам собі", size=10, color=INK))
    frags.append(text(190, 294, "Стрибок затримок allocstall!", size=10, bold=True, color=POS))

    # Лінія min
    frags.append(line(50, 310, 320, 310, color=POS, sw=2, dash="4,4"))
    frags.append(text(45, 314, "min", size=11, bold=True, color=POS, anchor="end"))

    # 4. Резерв ядра та OOM (< min)
    frags.append(rect(75, 315, 230, 55, fill="#fee2e2", stroke=POS, sw=1.5, rx=4))
    frags.append(text(190, 338, "Резерв ядра / OOM (< min)", size=12, bold=True, color=POS))
    frags.append(text(190, 356, "Пам'ять вичерпано → OOM Killer", size=10, color=POS))

    # Права частина: Метрики, що фіксують стан
    frags.append(rect(360, 65, 480, 320, fill="#ffffff", stroke=LINE, sw=1.5, rx=8))
    frags.append(text(600, 90, "Що видно в метриках і лічильниках ядра", size=13, bold=True))

    # Блок vmstat / procfs
    frags.append(fitbox(380, 110, 440, 75, "/proc/vmstat: темп і характер відбору\n• pgscan_kswapd / pgsteal_kswapd — фонова чистка (норма)\n• pgscan_direct / pgsteal_direct — прямий відбір (критично)\n• allocstall_normal — кількість потоків, що застрягли у виділенні", size=11, fill="#f8fafc", stroke="#cbd5e1"))

    # Блок PSI
    frags.append(fitbox(380, 195, 440, 95, "/proc/pressure/memory (PSI): справжня ціна затримки\nsome avg10=... — частка часу, коли ПРИНАЙМНІ ОДИН потік\nстоїть в очікуванні пам'яті (прямий відбір, читання свопу/коду)\nfull avg10=... — частка часу, коли ВСІ активні потоки\nзаблоковані на пам'яті (пробуксовування, непродуктивність 100%)", size=11, fill="#fef2f2", stroke=POS, color=INK))

    # Блок реакції
    frags.append(fitbox(380, 300, 440, 70, "Поріг втручання наглядачів (systemd-oomd / earlyoom):\nРеагують не на free=0, а на PSI some > 25% або full > 10%:\nжертву вбивають завчасно, поки ядро ще не заклякло намертво.", size=11, fill="#f0fdf4", stroke=FIELD))

    render(os.path.join(IMG_DIR, "reclaim-watermarks-psi.svg"), w, h, *frags)


def fig_oom_badness_score():
    """Фігура 3: Розрахунок oom_badness, поправка oom_score_adj і захист через cgroups v2."""
    w, h = 880, 430
    frags = []

    frags.append(text(w / 2, 28, "Математика OOM-score: парадокс бази, поправка adj та ізоляція cgroups", size=16, bold=True))

    # Ліва панель: Глобальний OOM (без cgroups)
    frags.append(rect(40, 60, 380, 345, fill="#fef2f2", stroke=POS, sw=1.5, rx=8))
    frags.append(text(230, 85, "Глобальний OOM (традиційна модель)", size=13, bold=True, color=POS))
    frags.append(text(230, 103, "Формула oom_badness = RSS + Swap + PageTables", size=10, color=MUTED))

    # Приклад 1: База
    frags.append(rect(55, 120, 350, 85, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(230, 140, "Служба PostgreSQL (1 процес)", size=12, bold=True, color=INK))
    frags.append(text(230, 160, "RSS = 6 ГіБ (1 572 864 стор.) · PageTables = 12 МіБ", size=10, color=INK))
    frags.append(text(230, 178, "oom_score_adj = 0  →  Бал badness = 1 575 936", size=10, bold=True, color=POS))
    frags.append(text(230, 195, "ВИРОК: OOM-killer вбиває базу! (найбільший бал)", size=10, bold=True, color=POS))

    # Приклад 2: 32 компілятори
    frags.append(rect(55, 215, 350, 85, fill="#ffffff", stroke=LINE, sw=1.2, rx=6))
    frags.append(text(230, 235, "Збірка make -j32 (32 процеси cc1)", size=12, bold=True, color=INK))
    frags.append(text(230, 255, "Кожен cc1: RSS = 350 МіБ (89 600 стор.)", size=10, color=INK))
    frags.append(text(230, 273, "Сумарно: 11.2 ГіБ пам'яті з'їдено збіркою!", size=10, color=MUTED))
    frags.append(text(230, 290, "Бал кожного cc1 = 89 856  →  Усі cc1 виживають!", size=10, bold=True, color=FIELD))

    # Вплив поправки
    frags.append(fitbox(55, 310, 350, 80, "Поправка oom_score_adj для бази:\nВиставляємо postgres oom_score_adj = -800:\nпоправка = -800 · (totalpages/1000) = -3 355 200 сторінок.\nБал badness стає від'ємним (-1.7M) → база захищена!", size=10, fill="#f0fdf4", stroke=FIELD, color=INK))

    # Права панель: cgroups v2 (модель контрольних груп)
    frags.append(rect(460, 60, 380, 345, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    frags.append(text(650, 85, "cgroups v2: облік і OOM на рівні групи", size=13, bold=True, color=FIELD))
    frags.append(text(650, 103, "Межа memory.max та прапорець memory.oom.group", size=10, color=MUTED))

    # Група build.slice
    frags.append(rect(475, 120, 350, 125, fill="#ffffff", stroke="#ea580c", sw=1.2, rx=6))
    frags.append(text(650, 140, "Контрольна група: build.slice", size=12, bold=True, color="#c2410c"))
    frags.append(text(650, 160, "memory.max = 8 ГіБ · memory.current = 8.1 ГіБ", size=10, color=INK))
    frags.append(text(650, 180, "memory.oom.group = 1 (вбити всю групу разом)", size=10, bold=True, color=INK))
    frags.append(text(650, 200, "1. Прямий відбір і OOM локалізовані всередині build.slice", size=10, color=MUTED))
    frags.append(text(650, 220, "2. Усі 32 cc1 гинуть разом, база postgres НЕ зачеплена!", size=10, bold=True, color=FIELD))

    # Переваги моделі cgroup
    frags.append(fitbox(475, 255, 350, 135, "Чому cgroups v2 вирішує проблему назавжди:\n• Чесний облік: кожен кадр належить рівно одній групі\n• Включає кеш сторінок, dentry/inode і пам'ять ядра\n• memory.events (oom, oom_kill) фіксує точні події\n• Захищає сусідні служби без ручного підбору oom_score_adj", size=10, fill="#f8fafc", stroke="#cbd5e1", color=INK))

    render(os.path.join(IMG_DIR, "oom-badness-score.svg"), w, h, *frags)


if __name__ == "__main__":
    fig_metrics_layering()
    fig_reclaim_watermarks_psi()
    fig_oom_badness_score()
    print("All figures generated successfully.")
