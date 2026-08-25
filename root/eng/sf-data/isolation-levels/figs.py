# -*- coding: utf-8 -*-
"""Фігури теми «Рівні ізоляції транзакцій та феномени аномалій». Вивід — ./img/*.svg"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

IMG = os.path.join(os.path.dirname(__file__), 'img')
os.makedirs(IMG, exist_ok=True)
out = lambda name: os.path.join(IMG, name)


# ── 1. Матриця ANSI SQL-92 vs Розширена модель Бернштейна-Ґрея ───────────────
def fig_ansi_vs_berenson_matrix():
    W, H = 1040, 560
    f = []

    f.append(text(520, 30, "Матриця феноменів та рівнів ізоляції: ANSI SQL-92 проти розширення 1995 року",
                  size=15, bold=True, color=INK))

    # Стовпці таблиці
    cols = [
        ("Рівень ізоляції", 160),
        ("P0\nDirty Write", 90),
        ("P1\nDirty Read", 90),
        ("P4\nLost Update", 95),
        ("P2\nFuzzy Read", 95),
        ("A5A\nRead Skew", 95),
        ("P3\nPhantom", 90),
        ("A5B\nWrite Skew", 95),
    ]
    xs = [50]
    for _, w in cols:
        xs.append(xs[-1] + w)

    # Заголовок таблиці
    y_head = 60
    f.append(rect(xs[0], y_head, xs[-1] - xs[0], 50, fill="#f1f5f9", stroke=LINE, sw=1.5, rx=4))
    for i, (name, _) in enumerate(cols):
        cx = (xs[i] + xs[i+1]) / 2
        f.append(mtext(cx, y_head + 20, name, size=11, bold=True, color=INK))

    # Рядки
    rows_data = [
        ("Read Uncommitted\n(ANSI SQL-92)", [("Захист", FIELD), ("Аномалія", POS), ("Аномалія", POS), ("Аномалія", POS), ("Аномалія", POS), ("Аномалія", POS), ("Аномалія", POS)], "#ffffff"),
        ("Read Committed\n(ANSI SQL-92)", [("Захист", FIELD), ("Захист", FIELD), ("Аномалія", POS), ("Аномалія", POS), ("Аномалія", POS), ("Аномалія", POS), ("Аномалія", POS)], "#f8fafc"),
        ("Repeatable Read\n(ANSI SQL-92)", [("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD), ("Аномалія", POS), ("Аномалія", POS)], "#ffffff"),
        ("Snapshot Isolation\n(Berenson et al. 1995)", [("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD), ("Аномалія", POS)], "#eff6ff"),
        ("Serializable (2PL / SSI)\n(Строга серіалізовність)", [("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD), ("Захист", FIELD)], "#ecfdf5"),
    ]

    y_cur = y_head + 50
    row_h = 64
    for r_idx, (r_title, r_cells, r_fill) in enumerate(rows_data):
        f.append(rect(xs[0], y_cur, xs[-1] - xs[0], row_h, fill=r_fill, stroke=LINE, sw=1.2, rx=0))
        # Назва рівня
        f.append(mtext(xs[0] + 80, y_cur + 26, r_title, size=11, bold=True, color=INK))
        # Комірки аномалій
        for c_idx, (val, col) in enumerate(r_cells):
            cx = (xs[c_idx+1] + xs[c_idx+2]) / 2
            bg_col = "#dcfce7" if col == FIELD else "#fee2e2"
            b_cell, _, _ = textbox(cx, y_cur + 32, val, size=10, pad=5, fill=bg_col, stroke=col, sw=1, color=col, bold=True)
            f.append(b_cell)
        y_cur += row_h

    # Підсумкова примітка внизу
    b_note, _, _ = textbox(520, y_cur + 45,
                           "Ключовий висновок Бернштейна-Ґрея: Snapshot Isolation захищає від фантомів (P3), але допускає Write Skew (A5B),\nтому НЕ є еквівалентом Serializable всупереч спрощеним критеріям класичного стандарту ANSI SQL-92.",
                           size=11, fill="#fffbeb", stroke="#d97706", sw=1.2, pad=8, color="#92400e")
    f.append(b_note)

    render(out("ansi-vs-berenson-matrix.svg"), W, H, *f,
           title="Порівняльна матриця феноменів та рівнів ізоляції")


# ── 2. Часова діаграма аномалії Write Skew (Зсув запису) ──────────────────────
def fig_write_skew_timeline():
    W, H = 1020, 520
    f = []

    f.append(text(510, 30, "Феномен аномалії Write Skew (Зсув запису) під Snapshot Isolation",
                  size=15, bold=True, color=INK))

    # Ліва колонка: Транзакція 1 (Лікар Аліса)
    f.append(text(220, 70, "Транзакція T1 (Аліса)", size=14, bold=True, color=NEG))
    f.append(text(220, 88, "Хоче знятися з чергування", size=11, color=MUTED))

    # Права колонка: Транзакція 2 (Лікар Боб)
    f.append(text(800, 70, "Транзакція T2 (Боб)", size=14, bold=True, color=POS))
    f.append(text(800, 88, "Хоче знятися з чергування", size=11, color=MUTED))

    # Центральна колонка: Спільний інваріант бази
    f.append(text(510, 70, "Спільний стан (Таблиця OnCall)", size=13, bold=True, color=INK))
    f.append(text(510, 88, "Інваріант: count(active) >= 1", size=11, bold=True, color=FIELD))

    # Вісь часу вниз
    f.append(arrow(60, 105, 60, 460, color=MUTED, sw=1.5))
    f.append(text(45, 280, "Час", size=12, color=MUTED))

    # Час t0: Початковий стан
    b_init, _, _ = textbox(510, 125, "Стан Snapshot: Аліса=ON (1), Боб=ON (1)\nВсього на чергуванні: 2 лікарі",
                           size=11, fill="#f8fafc", stroke=LINE, sw=1.2, pad=8)
    f.append(b_init)

    # Час t1: T1 читає кількість активних
    b_t1_r, _, _ = textbox(220, 195, "t1: SELECT count(*) FROM OnCall\nWHERE on_call = true;\n→ Отримує: 2 (>= 2, знятися можна)",
                           size=11, fill="#eff6ff", stroke=NEG, sw=1.2, pad=8)
    f.append(b_t1_r)

    # Час t2: T2 читає той самий знімок
    b_t2_r, _, _ = textbox(800, 195, "t2: SELECT count(*) FROM OnCall\nWHERE on_call = true;\n→ Отримує: 2 (>= 2, знятися можна)",
                           size=11, fill="#fee2e2", stroke=POS, sw=1.2, pad=8)
    f.append(b_t2_r)

    # Час t3: T1 оновлює свій статус і фіксується
    b_t1_w, _, _ = textbox(220, 300, "t3: UPDATE OnCall SET on_call=false\nWHERE name = 'Alice';\nCOMMIT (успіх, рядок Боба не зачеплено)",
                           size=11, fill="#eff6ff", stroke=NEG, sw=1.2, pad=8)
    f.append(b_t1_w)
    f.append(arrow(360, 300, 430, 300, color=NEG, sw=1.5))

    # Час t4: T2 оновлює свій статус і фіксується (немає конфлікту рядків!)
    b_t2_w, _, _ = textbox(800, 375, "t4: UPDATE OnCall SET on_call=false\nWHERE name = 'Bob';\nCOMMIT (успіх, рядок Аліси не зачеплено!)",
                           size=11, fill="#fee2e2", stroke=POS, sw=1.2, pad=8)
    f.append(b_t2_w)
    f.append(arrow(660, 375, 590, 375, color=POS, sw=1.5))

    # Час t5: Підсумок порушення інваріанта
    b_err, _, _ = textbox(510, 450, "Кінцевий стан бази: Аліса = OFF (0), Боб = OFF (0) → count(active) = 0!\nІНВАРІАНТ ПОРУШЕНО: Жоден лікар не чергує. Обидві транзакції успішні через неперетинні множини запису.",
                          size=11, fill="#fef2f2", stroke=POS, sw=1.8, pad=10, bold=True)
    f.append(b_err)

    render(out("write-skew-timeline.svg"), W, H, *f,
           title="Часова діаграма аномалії Write Skew під Snapshot Isolation")


# ── 3. Граф залежностей DSG та виявлення небезпечних циклів у SSI ────────────
def fig_ssi_dependency_cycle():
    W, H = 1020, 540
    f = []

    f.append(text(510, 30, "Граф прямих залежностей (DSG) та виявлення небезпечної структури в SSI",
                  size=15, bold=True, color=INK))

    # Вузол T1: Аліса
    b_t1, _, _ = textbox(240, 160, "Транзакція T1 (Аліса)\n• Читає стан Боба (r_1[Bob])\n• Записує стан Аліси (w_1[Alice])\n• Фіксується (c_1)",
                         size=11, fill="#eff6ff", stroke=NEG, sw=1.8, pad=10, bold=True)
    f.append(b_t1)

    # Вузол T2: Боб
    b_t2, _, _ = textbox(780, 160, "Транзакція T2 (Боб)\n• Читає стан Аліси (r_2[Alice])\n• Записує стан Боба (w_2[Bob])\n• Фіксується (c_2)",
                         size=11, fill="#fee2e2", stroke=POS, sw=1.8, pad=10, bold=True)
    f.append(b_t2)

    # Стрілка rw-антизалежності від T1 до T2
    f.append(arrow(370, 130, 645, 130, color=POS, sw=2))
    b_rw1, _, _ = textbox(510, 110, "rw-антизалежність (r_1[Bob] ──rw──> w_2[Bob])\nT1 прочитала версію до запису T2",
                          size=10, fill="#ffffff", stroke=POS, pad=5, bold=True)
    f.append(b_rw1)

    # Стрілка rw-антизалежності від T2 до T1
    f.append(arrow(645, 190, 370, 190, color=POS, sw=2))
    b_rw2, _, _ = textbox(510, 210, "rw-антизалежність (r_2[Alice] ──rw──> w_1[Alice])\nT2 прочитала версію до запису T1",
                          size=10, fill="#ffffff", stroke=POS, pad=5, bold=True)
    f.append(b_rw2)

    # Нижня частина: Механізм SSI (Serializable Snapshot Isolation)
    b_ssi_title, _, _ = textbox(510, 300, "Теорема Фекете-Кехіла (2008): Кожен несеріалізовний цикл у Snapshot Isolation\nмістить небезпечну структуру (Dangerous Structure) з двох послідовних rw-антизалежностей:",
                                size=11, fill="#f8fafc", stroke=LINE, sw=1.2, pad=8, bold=True)
    f.append(b_ssi_title)

    # Ланцюжок Pivot Transaction
    b_piv1, _, _ = textbox(200, 395, "Попередня транзакція\nT_in", size=11, fill="#eff6ff", stroke=NEG, pad=8)
    f.append(b_piv1)

    b_pivot, _, _ = textbox(510, 395, "PIVOT ТРАНЗАКЦІЯ T_p\nВхідний rw-конфлікт (inConflict=true)\nВихідний rw-конфлікт (outConflict=true)",
                            size=11, fill="#fef2f2", stroke=POS, sw=2, pad=10, bold=True)
    f.append(b_pivot)

    b_piv2, _, _ = textbox(820, 395, "Наступна транзакція\nT_out", size=11, fill="#ecfdf5", stroke=FIELD, pad=8)
    f.append(b_piv2)

    f.append(arrow(295, 395, 365, 395, color=POS, sw=2))
    f.append(text(330, 380, "rw-edge", size=10, color=POS, bold=True))

    f.append(arrow(655, 395, 725, 395, color=POS, sw=2))
    f.append(text(690, 380, "rw-edge", size=10, color=POS, bold=True))

    # Дія SSI
    b_ssi_act, _, _ = textbox(510, 485, "Рішення SSI в СУБД (PostgreSQL): При виявленні двох суміжних rw-ребер рушій аварійно відкочує\nтранзакцію-півот (Pivot) з помилкою 40001 (serialization_failure), розриваючи потенційний цикл без важких блокувань.",
                              size=11, fill="#dcfce7", stroke=FIELD, sw=1.5, pad=8, color="#166534", bold=True)
    f.append(b_ssi_act)

    render(out("ssi-dependency-cycle.svg"), W, H, *f,
           title="Граф серіалізовності та виявлення конфліктів у SSI")


# ── 4. Порівняння механізмів: 2PL (Блокування) vs MVCC (Версії рядків) ────────
def fig_locking_vs_mvcc_mechanisms():
    W, H = 1040, 540
    f = []

    f.append(text(520, 30, "Порівняння архітектур: Двофазне блокування (2PL) проти Багатоверсійності (MVCC)",
                  size=15, bold=True, color=INK))

    # Ліва колонка: 2PL
    f.append(rect(40, 60, 460, 430, fill="#f8fafc", stroke=NEG, sw=1.5, rx=8))
    f.append(text(270, 88, "Двофазне блокування (2PL / Strict 2PL)", size=13, bold=True, color=NEG))

    b_2pl_desc, _, _ = textbox(270, 145, "Песимістичний підхід (Pessimistic Concurrency)\n• Читач бере Shared Lock (S-lock)\n• Письменник бере Exclusive Lock (X-lock)\n• Читачі блокують письменників, письменники — читачів",
                               size=10, fill="#ffffff", stroke=LINE, pad=8)
    f.append(b_2pl_desc)

    b_2pl_diag, _, _ = textbox(270, 260, "Конфліктна матриця блокувань:\n• S-lock + S-lock  ──►  СУМІСНІ (одночасне читання)\n• S-lock + X-lock  ──►  КОНФЛІКТ (читач/письменник чекає)\n• X-lock + X-lock  ──►  КОНФЛІКТ (взаємне очікування / Deadlock)",
                               size=10, fill="#fee2e2", stroke=POS, pad=8)
    f.append(b_2pl_diag)

    b_2pl_pros, _, _ = textbox(270, 390, "Переваги: Абсолютна простота математичних гарантій.\nЦіна: Низька пропускна здатність на високому навантаженні,\nнебезпека взаємних блокувань (Deadlocks), простої черг.",
                               size=10, fill="#ffffff", stroke=MUTED, pad=8)
    f.append(b_2pl_pros)

    # Права колонка: MVCC
    f.append(rect(540, 60, 460, 430, fill="#f0fdf4", stroke=FIELD, sw=1.5, rx=8))
    f.append(text(770, 88, "Багатоверсійність (MVCC + Snapshot)", size=13, bold=True, color=FIELD))

    b_mvcc_desc, _, _ = textbox(770, 145, "Оптимістичний підхід зі знімками стану\n• Читачі НЕ блокують письменників\n• Письменники НЕ блокують читачів\n• Кожен запис створює нову версію кортежу (xmin / xmax)",
                                size=10, fill="#ffffff", stroke=LINE, pad=8)
    f.append(b_mvcc_desc)

    b_mvcc_diag, _, _ = textbox(770, 260, "Механіка знімка (Snapshot Visibility):\n• Транзакція T бачить версії з xmin < T.snapshot_id\n• Читання повертає історичний знімок на момент старту\n• Конфлікт виникає лише при паралельному записі (Write-Write)",
                                size=10, fill="#dcfce7", stroke=FIELD, pad=8)
    f.append(b_mvcc_diag)

    b_mvcc_pros, _, _ = textbox(770, 390, "Переваги: Колосальна швидкість читання без затримок.\nЦіна: Накопичення мертвих версій (потрібен VACUUM / GC),\nскладність виявлення аномалій (потрібен SSI для строгості).",
                                size=10, fill="#ffffff", stroke=MUTED, pad=8)
    f.append(b_mvcc_pros)

    # Нижнє порівняльне гасло
    b_slogan, _, _ = textbox(520, 505, "Головний закон сучасних СУБД: Readers never block Writers, and Writers never block Readers (MVCC).",
                             size=11, fill="#eff6ff", stroke=NEG, sw=1.2, pad=6, bold=True)
    f.append(b_slogan)

    render(out("locking-vs-mvcc-mechanisms.svg"), W, H, *f,
           title="Порівняння архітектури 2PL та MVCC")


if __name__ == "__main__":
    fig_ansi_vs_berenson_matrix()
    fig_write_skew_timeline()
    fig_ssi_dependency_cycle()
    fig_locking_vs_mvcc_mechanisms()
    print("Всі 4 фігури успішно згенеровано у ./img/")
