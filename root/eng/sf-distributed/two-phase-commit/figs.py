# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

OUT = os.path.join(os.path.dirname(__file__), "img")
os.makedirs(OUT, exist_ok=True)


# ── Фіг. 1: послідовність повідомлень 2PC: успіх та відкат ─────────────────────
def fig_two_phase_flow():
    W, H = 980, 520
    p = []

    def panel(px, title, is_commit):
        out = []
        pw, ph = 460.0, 480.0
        py = 20.0
        accent = FIELD if is_commit else POS
        out.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=10))
        out.append(text(px + pw / 2, py + 26, title, size=15, color=accent, bold=True))

        # вертикальні лінії вузлів: Координатор (C), Учасник 1 (P1), Учасник 2 (P2)
        cx = px + 70.0
        p1x = px + 230.0
        p2x = px + 390.0

        # заголовки вузлів
        out.append(fitbox(cx - 50, py + 46, 100, 32, "Координатор", size=12, fill="#eef2f7", stroke=LINE, bold=True))
        out.append(fitbox(p1x - 45, py + 46, 90, 32, "Вузол A", size=12, fill="#eef2f7", stroke=LINE, bold=True))
        out.append(fitbox(p2x - 45, py + 46, 90, 32, "Вузол B", size=12, fill="#eef2f7", stroke=LINE, bold=True))

        top_y = py + 86
        bot_y = py + ph - 25
        out.append(line(cx, top_y, cx, bot_y, color="#9aa5b1", sw=1.5, dash="4,4"))
        out.append(line(p1x, top_y, p1x, bot_y, color="#9aa5b1", sw=1.5, dash="4,4"))
        out.append(line(p2x, top_y, p2x, bot_y, color="#9aa5b1", sw=1.5, dash="4,4"))

        # Фаза 1: Підготовка
        y1 = py + 115
        out.append(rect(px + 12, y1 - 12, pw - 24, 20, fill="#f0f4f8", stroke="#d0d7de", sw=1.0, rx=4))
        out.append(text(px + pw / 2, y1 + 2, "Фаза 1: Голосування (Prepare)", size=11, color=MUTED, bold=True))

        y2 = y1 + 28
        out.append(arrow(cx, y2, p1x, y2 + 15, color=LINE, sw=1.5))
        out.append(arrow(cx, y2 + 5, p2x, y2 + 30, color=LINE, sw=1.5))
        b1, _, _ = textbox(px + 145, y2 + 2, "PREPARE", size=10.5, pad=4, fill="#ffffff", stroke="#8c9ba5")
        out.append(b1)

        y3 = y2 + 58
        if is_commit:
            out.append(arrow(p1x, y3, cx, y3 + 15, color=FIELD, sw=1.6))
            out.append(arrow(p2x, y3 + 10, cx, y3 + 25, color=FIELD, sw=1.6))
            b2, _, _ = textbox(px + 150, y3 + 2, "VOTE_COMMIT (так)", size=10, pad=4, fill="#eef8f0", stroke=FIELD, color=FIELD, bold=True)
            b3, _, _ = textbox(px + 295, y3 + 14, "VOTE_COMMIT (так)", size=10, pad=4, fill="#eef8f0", stroke=FIELD, color=FIELD, bold=True)
            out.append(b2); out.append(b3)
        else:
            out.append(arrow(p1x, y3, cx, y3 + 15, color=FIELD, sw=1.6))
            out.append(arrow(p2x, y3 + 10, cx, y3 + 25, color=POS, sw=1.6))
            b2, _, _ = textbox(px + 150, y3 + 2, "VOTE_COMMIT (так)", size=10, pad=4, fill="#eef8f0", stroke=FIELD, color=FIELD, bold=True)
            b3, _, _ = textbox(px + 295, y3 + 14, "VOTE_ABORT (ні / збій)", size=10, pad=4, fill="#fdf0ee", stroke=POS, color=POS, bold=True)
            out.append(b2); out.append(b3)

        # Фаза 2: Рішення
        y4 = y3 + 68
        out.append(rect(px + 12, y4 - 12, pw - 24, 20, fill="#f0f4f8", stroke="#d0d7de", sw=1.0, rx=4))
        out.append(text(px + pw / 2, y4 + 2, "Фаза 2: Рішення (Decision)", size=11, color=MUTED, bold=True))

        # Запис у WAL координатора
        y5 = y4 + 28
        wal_text = "WAL: COMMIT" if is_commit else "WAL: ABORT"
        wal_fill = "#eef8f0" if is_commit else "#fdf0ee"
        b_wal, _, _ = textbox(cx, y5, wal_text, size=10.5, pad=5, fill=wal_fill, stroke=accent, color=accent, bold=True)
        out.append(b_wal)

        y6 = y5 + 34
        if is_commit:
            out.append(arrow(cx, y6, p1x, y6 + 15, color=FIELD, sw=1.6))
            out.append(arrow(cx, y6 + 5, p2x, y6 + 30, color=FIELD, sw=1.6))
            b4, _, _ = textbox(px + 145, y6 + 2, "GLOBAL_COMMIT", size=10, pad=4, fill="#eef8f0", stroke=FIELD, color=FIELD, bold=True)
            out.append(b4)
        else:
            out.append(arrow(cx, y6, p1x, y6 + 15, color=POS, sw=1.6))
            out.append(arrow(cx, y6 + 5, p2x, y6 + 30, color=POS, sw=1.6))
            b4, _, _ = textbox(px + 145, y6 + 2, "GLOBAL_ABORT", size=10, pad=4, fill="#fdf0ee", stroke=POS, color=POS, bold=True)
            out.append(b4)

        y7 = y6 + 55
        out.append(arrow(p1x, y7, cx, y7 + 15, color=LINE, sw=1.4))
        out.append(arrow(p2x, y7 + 10, cx, y7 + 25, color=LINE, sw=1.4))
        b5, _, _ = textbox(px + 225, y7 + 6, "ACK (підтвердження)", size=10, pad=4, fill="#ffffff", stroke="#8c9ba5")
        out.append(b5)

        # Кінець транзакції
        y8 = y7 + 42
        b_end, _, _ = textbox(cx, y8, "WAL: END", size=10, pad=4, fill="#f4f6f8", stroke="#8c9ba5", color=MUTED)
        out.append(b_end)

        return out

    p.extend(panel(20, "Успішна транзакція (Усі проголосували «Так»)", True))
    p.extend(panel(500, "Відкат транзакції (Хоч один відповів «Ні»)", False))

    render(os.path.join(OUT, "two-phase-flow.svg"), W, H, *p,
           title="Послідовність повідомлень протоколу двофазного коміту")


# ── Фіг. 2: скінченні автомати станів координатора й учасника ──────────────────
def fig_state_machine():
    W, H = 960, 480
    p = []

    def panel_coord(px, py, pw, ph):
        out = []
        out.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=10))
        out.append(text(px + pw / 2, py + 26, "Автомат Координатора", size=15, color=INK, bold=True))

        # Стан 1: INIT
        out.append(fitbox(px + 30, py + 60, 110, 42, "INIT (Початок)", size=12, fill="#eef2f7", stroke=LINE, bold=True))
        out.append(arrow(px + 140, py + 81, px + 220, py + 81, color=LINE, sw=1.6))
        b1, _, _ = textbox(px + 180, py + 68, "PREPARE", size=10, pad=3, fill="#fff", stroke="#8c9ba5")
        out.append(b1)

        # Стан 2: PREPARING (Очікування голосів)
        out.append(fitbox(px + 220, py + 60, 180, 42, "PREPARING (Очікування)", size=12, fill="#fff8e6", stroke="#d97706", bold=True))

        # Гілка успіху: до COMMITTED
        out.append(arrow(px + 370, py + 102, px + 370, py + 190, color=FIELD, sw=1.6))
        b2, _, _ = textbox(px + 280, py + 146, "Усі VOTE_COMMIT\nWAL: COMMIT", size=10, pad=4, fill="#eef8f0", stroke=FIELD, color=FIELD, bold=True)
        out.append(b2)

        out.append(fitbox(px + 220, py + 190, 180, 42, "COMMITTED (Зафіксовано)", size=12, fill="#eef8f0", stroke=FIELD, color=FIELD, bold=True))

        # Гілка відкату: до ABORTED
        out.append(arrow(px + 220, py + 95, px + 95, py + 190, color=POS, sw=1.6))
        b3, _, _ = textbox(px + 135, py + 130, "Хоч один VOTE_ABORT\nабо таймаут → WAL: ABORT", size=9.5, pad=3, fill="#fdf0ee", stroke=POS, color=POS, bold=True)
        out.append(b3)

        out.append(fitbox(px + 30, py + 190, 150, 42, "ABORTED (Відкочено)", size=12, fill="#fdf0ee", stroke=POS, color=POS, bold=True))

        # Перехід до DONE після отримання всіх ACK
        out.append(arrow(px + 310, py + 232, px + 250, py + 320, color=LINE, sw=1.5))
        out.append(arrow(px + 105, py + 232, px + 160, py + 320, color=LINE, sw=1.5))
        b4, _, _ = textbox(px + 205, py + 276, "Отримано всі ACK\nWAL: END", size=10, pad=4, fill="#fff", stroke="#8c9ba5")
        out.append(b4)

        out.append(fitbox(px + 130, py + 320, 150, 42, "DONE (Завершено)", size=12, fill="#eef2f7", stroke="#6b7280", bold=True))

        return out

    def panel_part(px, py, pw, ph):
        out = []
        out.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=10))
        out.append(text(px + pw / 2, py + 26, "Автомат Учасника (Ресурсного менеджера)", size=15, color=INK, bold=True))

        # Стан 1: INIT
        out.append(fitbox(px + 30, py + 60, 110, 42, "INIT (Робота)", size=12, fill="#eef2f7", stroke=LINE, bold=True))

        # Перехід при PREPARE + готовність
        out.append(arrow(px + 140, py + 81, px + 215, py + 81, color=FIELD, sw=1.6))
        b1, _, _ = textbox(px + 175, py + 62, "PREPARE", size=9.5, pad=2, fill="#eef8f0", stroke=FIELD, color=FIELD, bold=True)
        out.append(b1)

        # Стан 2: PREPARED — Вікно невизначеності
        out.append(fitbox(px + 215, py + 60, 205, 52, "PREPARED (Підготовлено)\nВтрата автономії! In-Doubt", size=11, fill="#fff3cd", stroke="#eab308", color="#854d0e", bold=True))

        # Відмова на стадії INIT: стрілка ліворуч
        out.append(arrow(px + 45, py + 102, px + 45, py + 190, color=POS, sw=1.6))
        b2, _, _ = textbox(px + 105, py + 146, "Локальний збій\nVOTE_ABORT", size=9.5, pad=3, fill="#fdf0ee", stroke=POS, color=POS, bold=True)
        out.append(b2)

        out.append(fitbox(px + 30, py + 190, 140, 42, "ABORTED (Відкат)", size=12, fill="#fdf0ee", stroke=POS, color=POS, bold=True))

        # Переходи зі стану PREPARED:
        # 1) до COMMITTED: стрілка праворуч
        out.append(arrow(px + 395, py + 112, px + 395, py + 190, color=FIELD, sw=1.6))
        b3, _, _ = textbox(px + 310, py + 150, "GLOBAL_COMMIT\nWAL: COMMIT → ACK", size=9, pad=3, fill="#eef8f0", stroke=FIELD, color=FIELD, bold=True)
        out.append(b3)

        out.append(fitbox(px + 235, py + 190, 185, 42, "COMMITTED (Фіксація)", size=12, fill="#eef8f0", stroke=FIELD, color=FIELD, bold=True))

        # 2) до ABORTED: стрілка в обхід
        out.append(arrow(px + 215, py + 105, px + 150, py + 190, color=POS, sw=1.6))
        b4, _, _ = textbox(px + 215, py + 146, "GLOBAL_ABORT\nWAL: ABORT", size=9, pad=3, fill="#fdf0ee", stroke=POS, color=POS, bold=True)
        out.append(b4)

        # Пояснювальний блок про замки
        out.append(rect(px + 25, py + 265, pw - 50, 95, fill="#faf5ff", stroke="#c084fc", sw=1.2, rx=6))
        out.append(text(px + pw / 2, py + 288, "У стані PREPARED учасник НЕ МОЖЕ:", size=11.5, color="#6b21a8", bold=True))
        out.append(text(px + pw / 2, py + 308, "• самовільно відкотити транзакцію (раптом інші закомітять)", size=11, color=INK))
        out.append(text(px + pw / 2, py + 326, "• самовільно зафіксувати зміни (раптом координатор скасував)", size=11, color=INK))
        out.append(text(px + pw / 2, py + 345, "• зняти блокування з рядків (тримає замки до рішення)", size=11, color=POS, bold=True))

        return out

    p.extend(panel_coord(20, 20, 440, 440))
    p.extend(panel_part(490, 20, 450, 440))

    render(os.path.join(OUT, "state-machine.svg"), W, H, *p,
           title="Скінченні автомати станів координатора та учасників у 2PC")


# ── Фіг. 3: падіння координатора та блокування учасників ──────────────────────
def fig_coordinator_crash():
    W, H = 940, 440
    p = []

    # Фон і заголовок
    p.append(rect(20, 20, 900, 400, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=10))

    # Координатор зверху
    p.append(fitbox(380, 45, 180, 50, "Координатор", size=14, fill="#fdf0ee", stroke=POS, color=POS, bold=True))
    p.append(text(470, 115, "⚡ ЗБІЙ ЖИВЛЕННЯ / ПАДІННЯ СЕРВЕРА ⚡", size=13, color=POS, bold=True))
    p.append(text(470, 134, "(після отримання всіх VOTE_COMMIT, до розсилки рішень)", size=11.5, color=MUTED))

    # Учасники знизу
    p.append(fitbox(80, 220, 230, 80, "Учасник A (Shard 1)\nСтан: PREPARED\nТримає замки на рахунку Аліси", size=12, fill="#fff3cd", stroke="#eab308", color="#854d0e", bold=True))
    p.append(fitbox(630, 220, 230, 80, "Учасник B (Shard 2)\nСтан: PREPARED\nТримає замки на рахунку Боба", size=12, fill="#fff3cd", stroke="#eab308", color="#854d0e", bold=True))

    # Стрілки з хрестиками зв'язку
    p.append(line(430, 145, 200, 220, color=POS, sw=2.0, dash="6,6"))
    p.append(line(510, 145, 740, 220, color=POS, sw=2.0, dash="6,6"))
    p.append(text(300, 175, "❌ Зв'язок втрачено", size=12, color=POS, bold=True))
    p.append(text(640, 175, "❌ Зв'язок втрачено", size=12, color=POS, bold=True))

    # Двостороння стрілка між учасниками (спроба кооперативного вирішення)
    p.append(line(310, 260, 630, 260, color=LINE, sw=1.8, dash="4,4"))
    b_coop, _, _ = textbox(470, 260, "Питання між учасниками: «Ти отримав рішення?»\nОбидва відповідають: «Ні, я в стані PREPARED»", size=11, pad=6, fill="#f8fafc", stroke="#64748b", color=INK)
    p.append(b_coop)

    # Підсумок — глухий кут
    p.append(rect(140, 325, 660, 75, fill="#fdf2f2", stroke=POS, sw=1.5, rx=8))
    p.append(text(470, 348, "ГЛУХИЙ КУТ: БЛОКУВАННЯ ВСІЄЇ СИСТЕМИ", size=13, color=POS, bold=True))
    p.append(text(470, 368, "Жоден учасник не має права ні підтвердити, ні скасувати транзакцію.", size=11.5, color=INK))
    p.append(text(470, 386, "Усі рядки заблоковані. Черга нових транзакцій росте, доки координатор не відновиться.", size=11.5, color=INK))

    render(os.path.join(OUT, "coordinator-crash.svg"), W, H, *p,
           title="Блокувальний стан невизначеності при падінні координатора")


# ── Фіг. 4: 2PC проти консенсусу (Raft) та сучасна гібридна архітектура ────────
def fig_consensus_vs_2pc():
    W, H = 960, 460
    p = []

    def subpanel_2pc(px, py, pw, ph):
        out = []
        out.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=8))
        out.append(text(px + pw / 2, py + 24, "2PC: Атомарний коміт (100% вузлів)", size=13, color=INK, bold=True))
        out.append(text(px + pw / 2, py + 42, "Мета: неподільність операції між різними даними", size=11, color=MUTED))

        # 3 вузли
        for i in range(3):
            nx = px + 45 + i * 85
            ny = py + 70
            is_dead = (i == 2)
            col = POS if is_dead else FIELD
            bg = "#fdf0ee" if is_dead else "#eef8f0"
            out.append(fitbox(nx, ny, 70, 45, "Вузол %d\n%s" % (i + 1, "ЗБІЙ" if is_dead else "OK"), size=10, fill=bg, stroke=col, color=col, bold=True))

        out.append(rect(px + 20, py + 135, pw - 40, 48, fill="#fdf2ee", stroke=POS, sw=1.2, rx=6))
        out.append(text(px + pw / 2, py + 155, "Правило: Потрібні ВСІ (N з N)", size=11, color=POS, bold=True))
        out.append(text(px + pw / 2, py + 172, "1 збій = вся транзакція скасовується/блокується", size=10.5, color=INK))
        return out

    def subpanel_raft(px, py, pw, ph):
        out = []
        out.append(rect(px, py, pw, ph, fill="#fbfdff", stroke="#dfe4ea", sw=1.4, rx=8))
        out.append(text(px + pw / 2, py + 24, "Raft/Paxos: Консенсус (Більшість)", size=13, color=INK, bold=True))
        out.append(text(px + pw / 2, py + 42, "Мета: висока доступність копій тих самих даних", size=11, color=MUTED))

        # 3 вузли
        for i in range(3):
            nx = px + 45 + i * 85
            ny = py + 70
            is_dead = (i == 2)
            col = POS if is_dead else FIELD
            bg = "#fdf0ee" if is_dead else "#eef8f0"
            out.append(fitbox(nx, ny, 70, 45, "Репліка %d\n%s" % (i + 1, "ЗБІЙ" if is_dead else "OK"), size=10, fill=bg, stroke=col, color=col, bold=True))

        out.append(rect(px + 20, py + 135, pw - 40, 48, fill="#eef8f0", stroke=FIELD, sw=1.2, rx=6))
        out.append(text(px + pw / 2, py + 155, "Правило: Достатньо більшості (2 з 3)", size=11, color=FIELD, bold=True))
        out.append(text(px + pw / 2, py + 172, "1 збій = система ПРОДОВЖУЄ писати без затримок", size=10.5, color=INK))
        return out

    p.extend(subpanel_2pc(20, 20, 300, 195))
    p.extend(subpanel_raft(340, 20, 300, 195))

    # Правий огляд
    p.append(rect(660, 20, 280, 195, fill="#f8fafc", stroke="#cbd5e1", sw=1.4, rx=8))
    p.append(text(800, 44, "Чому 2PC ≠ Консенсус", size=13, color=INK, bold=True))
    p.append(text(800, 72, "• 2PC вимагає 100% згоди", size=11, color=INK))
    p.append(text(800, 92, "  бо кожен вузол володіє СВОЇМИ", size=10.5, color=MUTED))
    p.append(text(800, 110, "  унікальними даними (шардом)", size=10.5, color=MUTED))
    p.append(text(800, 134, "• Raft вимагає лише більшості", size=11, color=INK))
    p.append(text(800, 154, "  бо всі вузли дублюють ТОЙ САМИЙ", size=10.5, color=MUTED))
    p.append(text(800, 172, "  журнал подій (реплікація)", size=10.5, color=MUTED))

    # Нижня частина: Сучасний синтез — 2PC поверх Raft (Spanner, CockroachDB)
    p.append(rect(20, 230, 920, 210, fill="#fbfdff", stroke="#3b82f6", sw=1.5, rx=10))
    p.append(text(480, 255, "Сучасне вирішення (Spanner / CockroachDB / TiDB): 2PC поверх Raft-груп", size=14, color="#1d4ed8", bold=True))

    # Шард 1 (Raft група)
    p.append(rect(50, 275, 390, 115, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=8))
    p.append(text(245, 296, "Шард 1: Рахунки А-К (Raft-група з 3 реплік)", size=11.5, color=FIELD, bold=True))
    p.append(fitbox(70, 312, 105, 34, "Лідер (Raft)", size=10.5, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True))
    p.append(fitbox(190, 312, 105, 34, "Фоловер 1", size=10.5, fill="#ffffff", stroke="#86efac", color=MUTED))
    p.append(fitbox(310, 312, 105, 34, "Фоловер 2", size=10.5, fill="#ffffff", stroke="#86efac", color=MUTED))
    p.append(text(245, 372, "Падіння лідера вирішується виборами Raft за мілісекунди", size=10, color=MUTED))

    # Шард 2 (Raft група)
    p.append(rect(520, 275, 390, 115, fill="#f0fdf4", stroke=FIELD, sw=1.2, rx=8))
    p.append(text(715, 296, "Шард 2: Рахунки Л-Я (Raft-група з 3 реплік)", size=11.5, color=FIELD, bold=True))
    p.append(fitbox(540, 312, 105, 34, "Лідер (Raft)", size=10.5, fill="#dcfce7", stroke=FIELD, color=FIELD, bold=True))
    p.append(fitbox(660, 312, 105, 34, "Фоловер 1", size=10.5, fill="#ffffff", stroke="#86efac", color=MUTED))
    p.append(fitbox(780, 312, 105, 34, "Фоловер 2", size=10.5, fill="#ffffff", stroke="#86efac", color=MUTED))
    p.append(text(715, 372, "Учасник 2PC ніколи не вмирає: група Raft завжди доступна", size=10, color=MUTED))

    # Стрілка 2PC між лідерами
    p.append(arrow(175, 329, 540, 329, color="#2563eb", sw=2.2))
    p.append(arrow(540, 335, 175, 335, color="#2563eb", sw=2.2))
    b_cross, _, _ = textbox(480, 332, "2PC між шардами", size=11, pad=6, fill="#eff6ff", stroke="#2563eb", color="#1d4ed8", bold=True)
    p.append(b_cross)

    p.append(text(480, 422, "Синтез: Raft захищає від збоїв заліза, а 2PC забезпечує атомарність між різними таблицями/шардами.", size=11, color=INK, italic=True))

    render(os.path.join(OUT, "consensus-vs-2pc.svg"), W, H, *p,
           title="Відмінність 2PC від алгоритмів консенсусу та їхній сучасний синтез")


if __name__ == "__main__":
    fig_two_phase_flow()
    fig_state_machine()
    fig_coordinator_crash()
    fig_consensus_vs_2pc()
    print("All figures generated.")
