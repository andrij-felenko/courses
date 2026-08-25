# -*- coding: utf-8 -*-
"""Фігури до теми «Кінцева узгодженість на практиці»."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), 'img')
if not os.path.isdir(OUT):
    os.makedirs(OUT)

WARM = "#fdecea"   # аномалія / застарілий стан / розбіжність
COOL = "#eaf0fd"   # нейтральні вузли / заголовки
GOOD = "#e8f6ee"   # актуальний збіжний стан
WARN_BG = "#fff9db" # проміжний стан / перевірка


# ── 1. Часова шкала розходження та збіжності реплік ──────────────────────────
def fig_convergence_divergence():
    W, H = 1180, 600
    f = []

    f.append(text(W / 2, 32, "Динаміка розходження реплік та досягнення збіжності (Eventual Convergence)",
                  size=16, bold=True))

    x0, x1 = 240.0, 1120.0
    span = x1 - x0

    # ── Доріжка 1: Репліка А (Регіон EU)
    yA = 125.0
    f.append(fitbox(20, yA - 26, 190, 52, "РЕПЛІКА A (EU)\nвузол Франкфурт", size=12, bold=True, fill=COOL))
    f.append(line(x0, yA, x1, yA, color=LINE, sw=2.0))
    f.append(arrow(x1 - 10, yA, x1 + 15, yA, color=LINE, sw=2.0))
    f.append(text(x1 + 25, yA + 4, "t", size=13, italic=True))

    # ── Доріжка 2: Репліка B (Регіон US)
    yB = 345.0
    f.append(fitbox(20, yB - 26, 190, 52, "РЕПЛІКА B (US)\nвузол Вірджинія", size=12, bold=True, fill=COOL))
    f.append(line(x0, yB, x1, yB, color=LINE, sw=2.0))
    f.append(arrow(x1 - 10, yB, x1 + 15, yB, color=LINE, sw=2.0))
    f.append(text(x1 + 25, yB + 4, "t", size=13, italic=True))

    # Стан 0: спільна початкова версія v0
    t_start = x0
    t_w1 = x0 + span * 0.18
    f.append(rect(t_start, yA - 12, t_w1 - t_start, 24, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(text((t_start + t_w1) / 2, yA + 4, "Стан v0 (узгоджено)", size=11, color=FIELD))
    f.append(rect(t_start, yB - 12, t_w1 - t_start, 24, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(text((t_start + t_w1) / 2, yB + 4, "Стан v0 (узгоджено)", size=11, color=FIELD))

    # Подія: Запис W1 на Репліці А
    f.append(circle(t_w1, yA, 7, fill=POS, stroke=POS, sw=2))
    f.append(arrow(t_w1, yA - 42, t_w1, yA - 10, color=POS, sw=2.0))
    f.append(text(t_w1, yA - 50, "Запис W1: x = 10", size=12, color=POS, bold=True))

    # Подія: Одночасний запис W2 на Репліці B
    t_w2 = x0 + span * 0.32
    f.append(circle(t_w2, yB, 7, fill=NEG, stroke=NEG, sw=2))
    f.append(arrow(t_w2, yB + 42, t_w2, yB + 10, color=NEG, sw=2.0))
    f.append(text(t_w2, yB + 56, "Запис W2: x = 20", size=12, color=NEG, bold=True))

    # Вікно розходження (Inconsistency Window)
    t_sync = x0 + span * 0.65
    f.append(rect(t_w1, yA - 12, t_sync - t_w1, 24, fill=WARM, stroke=POS, sw=1.2))
    f.append(text((t_w1 + t_sync) / 2, yA + 4, "Локальний стан v1 {A:1}", size=11, color=POS, bold=True))

    f.append(rect(t_w1, yB - 12, t_w2 - t_w1, 24, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(text((t_w1 + t_w2) / 2, yB + 4, "Стан v0 (застарілий)", size=10, color=MUTED))

    f.append(rect(t_w2, yB - 12, t_sync - t_w2, 24, fill=WARM, stroke=NEG, sw=1.2))
    f.append(text((t_w2 + t_sync) / 2, yB + 4, "Локальний стан v2 {B:1}", size=11, color=NEG, bold=True))

    # Тінь вікна незбіжності між доріжками
    f.append(rect(t_w1, yA + 20, t_sync - t_w1, (yB - 20) - (yA + 20), fill="#fff7e6", stroke="#d48806", sw=1.0, rx=4))
    f.append(text((t_w1 + t_sync) / 2, (yA + yB) / 2 - 12, "ВІКНО НЕЗБІЖНОСТІ (Δt)", size=12, color="#d48806", bold=True))
    f.append(text((t_w1 + t_sync) / 2, (yA + yB) / 2 + 10, "Читачі на A бачать x=10, читачі на B бачать x=20", size=10.5, color=MUTED))

    # Синхронізація (Anti-Entropy / Gossip / Read-Repair)
    t_conv = t_sync + span * 0.12
    f.append(line(t_sync, yA + 16, t_conv - 10, yB - 16, color=FIELD, sw=2.0, dash="5,4"))
    f.append(line(t_sync, yB - 16, t_conv - 10, yA + 16, color=FIELD, sw=2.0, dash="5,4"))
    f.append(arrow(t_conv - 15, yB - 24, t_conv - 5, yB - 14, color=FIELD, sw=2.0))
    f.append(arrow(t_conv - 15, yA + 24, t_conv - 5, yA + 14, color=FIELD, sw=2.0))

    f.append(fitbox(t_sync + 15, (yA + yB) / 2 - 24, 150, 48, "Фонова звірка\nAnti-Entropy / Gossip",
                    size=10.5, bold=True, fill=WARN_BG, stroke=FIELD, sw=1.5))

    # Фінальний збіжний стан (v3)
    f.append(rect(t_conv, yA - 12, x1 - t_conv, 24, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(text((t_conv + x1) / 2, yA + 4, "Збіжний стан v3 {A:1, B:1} (узгоджено)", size=11, color=FIELD, bold=True))

    f.append(rect(t_conv, yB - 12, x1 - t_conv, 24, fill=GOOD, stroke=FIELD, sw=1.2))
    f.append(text((t_conv + x1) / 2, yB + 4, "Збіжний стан v3 {A:1, B:1} (узгоджено)", size=11, color=FIELD, bold=True))

    # Пояснювальний підсумок внизу
    f.append(fitbox(W / 2 - 460, 500, 920, 56,
                    "Кінцева узгодженість допускає тимчасове розходження даних у вікні Δt заради миттєвої доступності запису.\n"
                    "Збіжність (Convergence) гарантує, що після завершення фонового обміну репліки набувають ідентичного стану.",
                    size=12, pad=8, fill=COOL, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "convergence-divergence-timeline.svg"), W, H, *f)


# ── 2. Таксономія сесійних гарантій ──────────────────────────────────────────
def fig_session_guarantees():
    W, H = 1180, 680
    f = []

    f.append(text(W / 2, 30, "Чотири сесійні гарантії поверх кінцево-узгодженого сховища",
                  size=16, bold=True))

    col_w = 265.0
    col_gap = 20.0
    start_x = 35.0

    cards = [
        ("1. ЧИТАЙ ВЛАСНІ ЗАПИСИ\n(Read-Your-Writes)",
         "Клієнт бачить власні оновлення",
         "Оновив аватар профілю,\nперезавантажив сторінку —\nі знову бачить старе фото,\nбо запит потрапив на репліку,\nяка ще не отримала запис.",
         "Читання після запису\nмаршрутизуються на лідер,\nабо клієнт передає токен\nверсії й чекає, поки репліка\nназдожене цей LSN.",
         POS),
        ("2. МОНОТОННЕ ЧИТАННЯ\n(Monotonic Reads)",
         "Час ніколи не йде назад",
         "Перший запит повернув\nсвіжий стан v2 зі швидкого\nвузла, а повторний запит\nповернув старий стан v1\nіз запізнілої репліки.",
         "Балансувальник зберігає\nсесійний токен версії\nі відхиляє вузли,\nу яких номер транзакції\nменший за вже бачений.",
         NEG),
        ("3. МОНОТОННИЙ ЗАПИС\n(Monotonic Writes)",
         "Записи клієнта впорядковані",
         "Запис W1 (створення)\nі запис W2 (редагування)\nпішли різними шляхами;\nW2 падає з помилкою,\nбо W1 ще не доставлено.",
         "Усі послідовні записи\nодного клієнта прив'язують\nдо одного шарду або черги,\nде порядок гарантується\nмонотонним лічильником.",
         FIELD),
        ("4. ПРИЧИННЕ СЛІДУВАННЯ\n(Writes-Follow-Reads)",
         "Відповідь після запитання",
         "Боб відповів на пост Аліси;\nсторонні читачі бачать\nвідповідь Боба раніше,\nніж вихідний пост Аліси,\nщо ламає контекст бесіди.",
         "Векторні годинники\nфіксують причинний зв'язок:\nподія не публікується,\nдоки всі її передумови\nне зафіксовані в сховищі.",
         "#d48806"),
    ]

    for i, (title, subtitle, defect, fix, accent) in enumerate(cards):
        x = start_x + i * (col_w + col_gap)
        y = 65.0

        # Рамка картки
        f.append(rect(x, y, col_w, 515, fill=FILL, stroke=LINE, sw=1.5, rx=6))

        # Шапка картки
        f.append(fitbox(x + 8, y + 8, col_w - 16, 56, title, size=11.5, bold=True, fill=COOL, stroke=accent, sw=1.5))
        f.append(fitbox(x + 8, y + 68, col_w - 16, 28, subtitle, size=10.5, italic=True, fill=BG, stroke=MUTED, sw=1.0))

        # Блок дефекту (Червоний / Аномалія)
        f.append(fitbox(x + 10, y + 104, col_w - 20, 165,
                        "АНАЛІЗ АНОМАЛІЇ:\n" + defect,
                        size=10.5, color=INK, fill=WARM, stroke=POS, sw=1.2))

        # Блок вирішення (Зелений / Інженерний рецепт)
        f.append(fitbox(x + 10, y + 278, col_w - 20, 185,
                        "ІНЖЕНЕРНИЙ ЗАХИСТ:\n" + fix,
                        size=10.5, color=INK, fill=GOOD, stroke=FIELD, sw=1.2))

        # Ключовий маркер внизу
        f.append(fitbox(x + 10, y + 472, col_w - 20, 30, "Гарантія на рівні сесії", size=10.5, bold=True, fill=WARN_BG, stroke=LINE, sw=1.0))

    f.append(fitbox(W / 2 - 470, 600, 940, 54,
                    "Сесійні гарантії не вимагають глобального синхронного консенсусу між усіма вузлами.\n"
                    "Вони будуються локально для кожного клієнта через сесійні токени версій та липку маршрутизацію.",
                    size=12, pad=6, fill=COOL, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "session-guarantees-taxonomy.svg"), W, H, *f)


# ── 3. Матриця компромісів PACELC ────────────────────────────────────────────
def fig_pacelc_matrix():
    W, H = 1180, 640
    f = []

    f.append(text(W / 2, 30, "Матриця PACELC: класифікація розподілених систем за компромісами",
                  size=16, bold=True))

    cx = W / 2
    cy = 320.0
    half_w = 460.0
    half_h = 200.0

    x0 = cx - half_w
    y0 = cy - half_h
    x1 = cx + half_w
    y1 = cy + half_h

    # Фон квадрантів
    f.append(rect(x0, y0, half_w, half_h, fill="#fdf2e9", stroke=LINE, sw=1.2, rx=4)) # Лівий верх: PA/EL
    f.append(rect(cx, y0, half_w, half_h, fill="#eafaf1", stroke=LINE, sw=1.2, rx=4)) # Правий верх: PC/EC
    f.append(rect(x0, cy, half_w, half_h, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4)) # Лівий низ: PA/EC
    f.append(rect(cx, cy, half_w, half_h, fill="#f4f6f8", stroke=LINE, sw=1.2, rx=4)) # Правий низ: PC/EL

    # Головні осі
    f.append(line(x0, cy, x1, cy, color=LINE, sw=2.5))
    f.append(line(cx, y0, cx, y1, color=LINE, sw=2.5))

    # Мітка осі зверху
    f.append(fitbox(cx - 180, y0 - 34, 360, 26, "ЗА НАЯВНОСТІ ПОДІЛУ МЕРЕЖІ (If Partition)", size=11, bold=True, fill=COOL))

    # Пояснення квадрантів
    # 1. PA / EL (Amazon Dynamo, Apache Cassandra, Couchbase, Riak)
    f.append(fitbox(x0 + 15, y0 + 15, half_w - 30, 46, "PA / EL: ДОСТУПНІСТЬ ТА НИЗЬКА ЛАТЕНТНІСТЬ\nКінцева узгодженість (Eventual Consistency)", size=11.5, bold=True, fill=WARM, stroke=POS, sw=1.5))
    f.append(fitbox(x0 + 15, y0 + 68, half_w - 30, 115,
                    "• При аварії мережі: обирають доступність (A), приймають записи у всіх сегментах.\n"
                    "• У штатному режимі: обирають низьку латентність (L), відповідають без синхронного кворуму.\n"
                    "• Системи: Amazon Dynamo, Apache Cassandra (ONE/LOCAL_QUORUM), Riak, Couchbase.",
                    size=11, pad=6, fill=BG, stroke=MUTED))

    # 2. PC / EC (Google Spanner, CockroachDB, Raft / Paxos, etcd)
    f.append(fitbox(cx + 15, y0 + 15, half_w - 30, 46, "PC / EC: СТРОГА ЛІНІЙНІСТЬ ТА АТОМАРНІСТЬ\nЛінеаризовність (Linearizability / Single-Copy)", size=11.5, bold=True, fill=GOOD, stroke=FIELD, sw=1.5))
    f.append(fitbox(cx + 15, y0 + 68, half_w - 30, 115,
                    "• При аварії мережі: блокують меншість заради захисту узгодженості (C).\n"
                    "• У штатному режимі: платять латентністю синхронного консенсусу (C) заради свіжості.\n"
                    "• Системи: Google Spanner, CockroachDB, etcd, Apache ZooKeeper, TiDB.",
                    size=11, pad=6, fill=BG, stroke=MUTED))

    # 3. PA / EC (MongoDB, PostgreSQL асинхронні репліки з перемиканням)
    f.append(fitbox(x0 + 15, cy + 15, half_w - 30, 42, "PA / EC: КОМПРОМІС СВІЖОСТІ ТА ДОСТУПНОСТІ", size=11.5, bold=True, fill=FILL, stroke=LINE))
    f.append(fitbox(x0 + 15, cy + 64, half_w - 30, 115,
                    "• При аварії: продовжують обслуговувати доступність (A) з локальних копій.\n"
                    "• У штатному режимі: підтримують строгу узгодженість (C) на первинному вузлі.\n"
                    "• Системи: MongoDB (з конфігурацією uncommitted reads), MySQL/PostgreSQL з асинхронним primary.",
                    size=11, pad=6, fill=BG, stroke=MUTED))

    # 4. PC / EL (VoltDB, H-Store, Megastore)
    f.append(fitbox(cx + 15, cy + 15, half_w - 30, 42, "PC / EL: ТЕОРЕТИЧНИЙ КОРИДОР ЕКСТРЕМАЛЬНОЇ ЛАТЕНТНОСТІ", size=11.5, bold=True, fill=FILL, stroke=LINE))
    f.append(fitbox(cx + 15, cy + 64, half_w - 30, 115,
                    "• При аварії: блокують роботу для запобігання аномаліям (C).\n"
                    "• У штатному режимі: оптимізують латентність (L) через in-memory однопотокове виконання.\n"
                    "• Системи: VoltDB / H-Store (локальні транзакції у пам'яті без блокувань).",
                    size=11, pad=6, fill=BG, stroke=MUTED))

    # Підсумок формули знизу
    f.append(fitbox(W / 2 - 470, 555, 940, 54,
                    "Теорема PACELC (Даніель Абаді): Якщо поділ (If Partition) → обирай між Доступністю (A) та Узгодженістю (C);\n"
                    "Інакше (Else) → обирай між Латентністю (L) та Узгодженістю (C). Кінцева узгодженість обирає клас PA/EL.",
                    size=12, pad=6, fill=COOL, stroke=LINE, sw=1.2))

    render(os.path.join(OUT, "pacelc-tradeoff-matrix.svg"), W, H, *f)


if __name__ == '__main__':
    fig_convergence_divergence()
    fig_session_guarantees()
    fig_pacelc_matrix()
    print("OK: generated 3 figures.")
