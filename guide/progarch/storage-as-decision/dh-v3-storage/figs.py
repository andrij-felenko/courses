# -*- coding: utf-8 -*-
"""Фігури до кроку «DH v3: сховище стає рішенням» (модуль storage-as-decision, курс progarch).
Запуск:  python figs.py   → пише SVG у ./img/
Стиль і помічники — зі спільного svgkit (НЕ переписувати тут)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'scripts'))
from svgkit import *

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

GREEN_T = "#eafaf0"
RED_T   = "#fdecea"
AMBER   = "#d08a2e"
AMBER_T = "#fdf3e0"
HEAD_T  = "#eef1f6"


def dashed_rect(x, y, w, h, color=MUTED, sw=1.8, rx=8):
    return ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" fill="none" '
            'stroke="%s" stroke-width="%.1f" stroke-dasharray="7,5"/>'
            % (x, y, w, h, rx, color, sw))


# ───────── Фіг. 1: де живе правда в кожній версії дому ─────────
def fig_truth_across_versions():
    W, H = 1120, 400
    f = []

    cols = [
        ("v0", "додав:\nодин давач, без стану",
         "правда — у СВІТІ\n(реле, давач)", FIELD, GREEN_T),
        ("v1", "додав:\nрозклав на модулі",
         "правда — досі у світі,\nтрохи в RAM", FIELD, GREEN_T),
        ("v2", "додав:\nформу — порти й адаптери",
         "правда осіла в RAM\n⚠ крихка: рестарт стирає", POS, RED_T),
        ("v3", "додав:\nтривке реляційне сховище",
         "правда — на диску,\nза ACID (тривка)", FIELD, GREEN_T),
    ]

    L = 30
    cw, gap = 247, 24
    for i, (ver, added, truth, accent, tint) in enumerate(cols):
        x = L + i * (cw + gap)
        f.append(fitbox(x, 64, cw, 40, ver, size=16, bold=True,
                        fill=HEAD_T, stroke=MUTED, color=INK))
        f.append(fitbox(x, 112, cw, 66, added, size=13, fill=FILL, stroke="#d7dbe0", color=INK))
        f.append(fitbox(x, 188, cw, 82, truth, size=13.5, bold=True,
                        fill=tint, stroke=accent, color=INK, sw=1.8))

    # стрілка міграції правди попід колонками
    ay = 306
    f.append(text(W / 2, 292, "правда мігрує з версії у версію", size=12.5, bold=True, color=MUTED))
    f.append(arrow(L + 40, ay, W - L - 40, ay, color=INK, sw=1.8))

    # нижній банер
    f.append(fitbox(L, 328, W - 2 * L, 52,
                    "Світ → RAM → тривкий диск. v3 не вигадує правду наново — він переселяє накопичене з крихкої памʼяті туди, де його не зжере рестарт.",
                    size=13.5, bold=True, fill="#fbfbe8", stroke="#c9b458", color=INK, sw=2))

    render(os.path.join(IMG, "truth-across-versions.svg"), W, H, *f,
           title="Де живе правда в кожній версії Digital Homes")


# ───────── Фіг. 2: схема v3 — агрегат є межею транзакції ─────────
def fig_schema_aggregate():
    W, H = 1040, 470
    f = []

    # пунктирна межа агрегату
    ax, ay, aw, ah = 48, 62, 520, 356
    f.append(dashed_rect(ax, ay, aw, ah, color=FIELD, sw=2))
    f.append(text(ax + aw / 2, ay + 24, "агрегат «дім» = межа транзакції",
                  size=13.5, bold=True, color=FIELD))

    # home — корінь
    hx, hy, hw, hh = 92, ay + 42, 432, 116
    f.append(fitbox(hx, hy, hw, hh,
                    "home  —  корінь агрегату\n\nid (PK) · owner_id\nplan · device_cap · used_slots · threshold",
                    size=13, bold=True, fill=GREEN_T, stroke=FIELD, color=INK, sw=1.8))

    # device — дитина
    dx, dy, dw, dh = 92, hy + hh + 44, 432, 116
    f.append(fitbox(dx, dy, dw, dh,
                    "device\n\nid (PK) · home_id → home(id)\nkind · room · state · paired_at",
                    size=13, bold=True, fill=FILL, stroke="#d7dbe0", color=INK, sw=1.6))

    # зовнішній ключ: device.home_id → home.id
    fkx = hx + hw / 2
    f.append(arrow(fkx, dy, fkx, hy + hh, color=NEG, sw=1.8))
    f.append(text(fkx + 96, (hy + hh + dy) / 2 + 4, "зовнішній ключ", size=11.5, color=NEG))

    # measurement — ПОЗА агрегатом
    mx, my, mw, mh = 636, 150, 372, 120
    f.append(fitbox(mx, my, mw, mh,
                    "measurement  —  телеметрія\n\ndevice_id · ts · value\nPRIMARY KEY (device_id, ts)",
                    size=13, bold=True, fill=AMBER_T, stroke=AMBER, color=INK, sw=1.8))
    f.append(fitbox(mx, my + mh + 16, mw, 60,
                    "інший профіль запису:\nпотік вставок — окремий слот,\nПОЗА транзакцією реєстру",
                    size=12.5, fill=FILL, stroke="#d7dbe0", color=MUTED))

    render(os.path.join(IMG, "schema-aggregate.svg"), W, H, *f,
           title="Схема DH v3: межа агрегату стає межею транзакції")


# ───────── Фіг. 3: два профілі — свідоме записане рішення ─────────
def fig_two_profiles_decision():
    W, H = 1040, 424
    f = []

    # шапка ADR
    f.append(fitbox(30, 56, W - 60, 34,
                    "ADR-013 · Сховище Digital Homes v3 — профіль диктує сховище",
                    size=13.5, bold=True, fill=HEAD_T, stroke=MUTED, color=INK))

    lx, rx, cw = 40, 530, 470

    # ── ліва колонка: реєстр → реляційне ЗАРАЗ ──
    f.append(fitbox(lx, 104, cw, 40, "Реєстр · конфіг · власники",
                    size=14, bold=True, fill=GREEN_T, stroke=FIELD, color=INK, sw=1.8))
    f.append(fitbox(lx, 150, cw, 52,
                    "профіль: точкові транзакційні\nчитання · джерело правди",
                    size=13, fill=FILL, stroke="#d7dbe0", color=INK))
    f.append(fitbox(lx, 210, cw, 88,
                    "РІШЕННЯ: реляційне сховище ЗАРАЗ\nB-дерево · тривке · джерело правди",
                    size=13.5, bold=True, fill=GREEN_T, stroke=FIELD, color=INK, sw=2))

    # ── права колонка: телеметрія → LSM ПІЗНІШЕ (пунктир = відкладено) ──
    f.append(fitbox(rx, 104, cw, 40, "Телеметрія",
                    size=14, bold=True, fill=AMBER_T, stroke=AMBER, color=INK, sw=1.8))
    f.append(fitbox(rx, 150, cw, 52,
                    "профіль: потік вставок ·\nчитання діапазоном за часом",
                    size=13, fill=FILL, stroke="#d7dbe0", color=INK))
    f.append(fitbox(rx, 210, cw, 88,
                    "РІШЕННЯ: за портом TelemetrySink\nокреме LSM-сховище — ПІЗНІШЕ,\nколи міряний масштаб змусить",
                    size=13, bold=True, fill=AMBER_T, stroke=AMBER_T, color=INK, sw=1))
    f.append(dashed_rect(rx, 210, cw, 88, color=AMBER, sw=2))

    # нижній банер
    f.append(fitbox(30, 328, W - 60, 66,
                    "Профіль діагностовано, рішення записано в ADR, розкол відкладено до останнього відповідального моменту.\nНе два сховища зараз — один нудний реляційний ТЕПЕР + дешевий шов (порт) на майбутнє.",
                    size=13, bold=True, fill="#fbfbe8", stroke="#c9b458", color=INK, sw=2))

    render(os.path.join(IMG, "two-profiles-decision.svg"), W, H, *f,
           title="Свідоме рішення: один реляційний тепер, шов на місці розлому")


# ───────── Фіг. hist: найбільша присутність — найменша команда ─────────
def fig_sqlite_ubiquity():
    W, H = 1060, 476
    f = []

    # ── ЛІВА панель (велика): всюдисущість ──
    lx, lw = 40, 576
    f.append(fitbox(lx, 60, lw, 42, "Найпоширеніша база на Землі",
                    size=16, bold=True, fill=HEAD_T, stroke=MUTED, color=INK))
    f.append(fitbox(lx, 110, lw, 118,
                    "у кожному телефоні · браузері · ОС\n"
                    "у Airbus A350, авто, телевізорах\n"
                    "> 1 трильйон живих баз",
                    size=15, bold=True, fill=GREEN_T, stroke=FIELD, color=INK, sw=2))
    f.append(fitbox(lx, 236, lw, 74,
                    "«ужитку більше, ніж усіх інших\nбаз даних разом узятих»",
                    size=14.5, bold=True, fill=GREEN_T, stroke=FIELD, color=INK, sw=1.8))

    # ── ПРАВА панель (мала): хто це тримає ──
    rx, rw = 648, 372
    f.append(fitbox(rx, 60, rw, 42, "Хто це тримає",
                    size=16, bold=True, fill=HEAD_T, stroke=MUTED, color=INK))
    f.append(fitbox(rx, 110, rw, 62,
                    "троє людей\nсторонніх латок не беруть",
                    size=14, bold=True, fill=FILL, stroke="#d7dbe0", color=INK))
    f.append(fitbox(rx, 180, rw, 130,
                    "суспільне надбання\n(public domain)\n\nнічия власність ·\nжодної ліцензії",
                    size=14, bold=True, fill=AMBER_T, stroke=AMBER, color=INK, sw=2))

    # ── нижній банер: теза ──
    f.append(fitbox(40, 336, W - 80, 112,
                    "Найсерйозніше сховище на Землі — найнудніше:\n"
                    "передбачуване, вивірене до останньої гілки (100% MC/DC, DO-178B), нічого не просить.\n"
                    "Всюдисущість здобуло нудне, а не екзотичне. Спершу профіль — тоді рушій.",
                    size=14, bold=True, fill="#fbfbe8", stroke="#c9b458", color=INK, sw=2))

    render(os.path.join(IMG, "sqlite-ubiquity.svg"), W, H, *f,
           title="Найбільша присутність у світі — найменша команда")


# ───────── proj-1: накатник міграцій — у схеми зʼявляється історія ─────────
def fig_migration_ladder():
    W, H = 1120, 472
    f = []

    # ── стрічка з трьох карток-міграцій ──
    L, cw, gap, cy, ch = 45, 330, 22, 66, 100
    cards = [
        ("міграція 001\nреєстр: RAM → диск\n(home, device)", GREEN_T, FIELD, False),
        ("міграція 002\nтелеметрія: measurement\n(порт TelemetrySink)", GREEN_T, FIELD, False),
        ("міграція 003 (майбутня)\ndevice.last_seen\nще не накочено", AMBER_T, AMBER, True),
    ]
    xs = []
    for i, (label, tint, edge, dashed) in enumerate(cards):
        x = L + i * (cw + gap)
        xs.append(x)
        f.append(fitbox(x, cy, cw, ch, label, size=14, bold=True,
                        fill=tint, stroke=(tint if dashed else edge), color=INK, sw=2))
        if dashed:
            f.append(dashed_rect(x, cy, cw, ch, color=edge, sw=2))
        tag = "накочено" if not dashed else "у черзі"
        f.append(text(x + cw / 2, cy + ch + 20, tag, size=12, bold=True,
                      color=(FIELD if not dashed else AMBER)))

    # стрілка «порядок за номером»
    ay = cy + ch + 40
    f.append(arrow(xs[0] + 30, ay, xs[2] + cw - 30, ay, color=INK, sw=1.8))
    f.append(text(W / 2, ay - 8, "порядок накату — за номером, залізно", size=12.5,
                  bold=True, color=MUTED))

    # ── schema_version: память бази про себе ──
    sx, sy, sw_, sh = 45, 226, 470, 150
    f.append(fitbox(sx, sy, sw_, 30, "таблиця schema_version — память бази про себе",
                    size=12.5, bold=True, fill=HEAD_T, stroke=MUTED, color=INK))
    f.append(fitbox(sx + 12, sy + 40, sw_ - 24, 30,
                    "version 1 · реєстр на диск · applied",
                    size=12.5, bold=True, fill=GREEN_T, stroke=FIELD, color=INK))
    f.append(fitbox(sx + 12, sy + 76, sw_ - 24, 30,
                    "version 2 · телеметрія · applied",
                    size=12.5, bold=True, fill=GREEN_T, stroke=FIELD, color=INK))
    f.append(text(sx + sw_ / 2, sy + 134, "current = MAX(version) = 2",
                  size=12.5, bold=True, color=INK))

    # ── накатник: правила ──
    ax_, ay_, aw_, ah_ = 560, 226, 515, 150
    f.append(fitbox(ax_, ay_, aw_, 30, "накатник run_migrations",
                    size=12.5, bold=True, fill=HEAD_T, stroke=MUTED, color=INK))
    f.append(fitbox(ax_, ay_ + 40, aw_, 100,
                    "бере лише version > current\n"
                    "накочені кроки пропускає — повторний запуск no-op (ідемпотентно)\n"
                    "кожен крок — своя транзакція: зміна схеми + відмітка версії разом",
                    size=13, fill=FILL, stroke="#d7dbe0", color=INK))

    # ── нижній банер ──
    f.append(fitbox(45, 392, W - 90, 60,
                    "Схема — не застиглий камінь, а живий контракт із лінійною історією: дописується лише з хвоста,\n"
                    "тож копії бази — і в розробника, і в проді — сходяться до однієї форми.",
                    size=13, bold=True, fill="#fbfbe8", stroke="#c9b458", color=INK, sw=2))

    render(os.path.join(IMG, "migration-ladder.svg"), W, H, *f,
           title="Накатник міграцій: у схеми зʼявляється історія")


# ───────── proj-2: збірка v3 — реєстр переселився, порт не зрушив ─────────
def fig_v3_wiring():
    W, H = 1080, 540
    f = []

    # HubService — незмінний
    f.append(fitbox(340, 52, 400, 46, "HubService — не змінився ні на літеру",
                    size=14, bold=True, fill=GREEN_T, stroke=FIELD, color=INK, sw=2))
    # стрілки залежності вниз до портів
    f.append(arrow(460, 100, 300, 138, color=INK, sw=1.6))
    f.append(arrow(620, 100, 790, 138, color=INK, sw=1.6))

    # ── лівий порт: DeviceRepository ──
    lx, ly, lw, lh = 60, 140, 460, 212
    f.append(dashed_rect(lx, ly, lw, lh, color=MUTED, sw=1.6))
    f.append(fitbox(lx + 12, ly + 10, lw - 24, 32, "порт  DeviceRepository",
                    size=13.5, bold=True, fill=HEAD_T, stroke=MUTED, color=INK))
    # InMemory — v2, знято (− значок, без лінії поверх тексту)
    f.append(fitbox(lx + 56, ly + 54, lw - 86, 40,
                    "InMemoryDeviceRepository · v2, знято",
                    size=12.5, fill=FILL, stroke="#d7dbe0", color=MUTED))
    f.append(minus(lx + 36, ly + 74))
    # Sqlite — v3, активна (+ значок)
    f.append(fitbox(lx + 56, ly + 104, lw - 86, 40,
                    "SqliteDeviceRepository · v3",
                    size=12.5, bold=True, fill=GREEN_T, stroke=FIELD, color=INK, sw=1.8))
    f.append(plus(lx + 36, ly + 124))
    f.append(fitbox(lx + 30, ly + 154, lw - 60, 44,
                    "порт не зрушив — змінився\nлише адаптер (один рядок)",
                    size=12.5, fill=FILL, stroke="#d7dbe0", color=MUTED))

    # ── правий порт: TelemetrySink ──
    rx, ry, rw, rh = 560, 140, 460, 212
    f.append(dashed_rect(rx, ry, rw, rh, color=MUTED, sw=1.6))
    f.append(fitbox(rx + 12, ry + 10, rw - 24, 32, "порт  TelemetrySink",
                    size=13.5, bold=True, fill=HEAD_T, stroke=MUTED, color=INK))
    f.append(fitbox(rx + 30, ry + 54, rw - 60, 40,
                    "SqliteTelemetrySink — реляційно, зараз",
                    size=12.5, bold=True, fill=GREEN_T, stroke=FIELD, color=INK, sw=1.8))
    f.append(fitbox(rx + 30, ry + 104, rw - 60, 40, "LSM-сховище — пізніше",
                    size=12.5, bold=True, fill=AMBER_T, stroke=AMBER_T, color=INK))
    f.append(dashed_rect(rx + 30, ry + 104, rw - 60, 40, color=AMBER, sw=2))
    f.append(fitbox(rx + 30, ry + 154, rw - 60, 44,
                    "шов на місці розлому —\nреєстру не чіпає",
                    size=12.5, fill=FILL, stroke="#d7dbe0", color=MUTED))

    # ── точка збірки build ──
    bx, by, bw, bh = 250, 386, 580, 64
    f.append(fitbox(bx, by, bw, bh,
                    "build(path):  connect(FULL)  →  run_migrations(001, 002)  →  підставити конкретні адаптери",
                    size=12.5, bold=True, fill=HEAD_T, stroke=MUTED, color=INK))
    f.append(arrow(bx + 120, by, lx + lw / 2, ly + lh, color=NEG, sw=1.5))
    f.append(arrow(bx + bw - 120, by, rx + rw / 2, ry + rh, color=NEG, sw=1.5))

    # банер
    f.append(fitbox(45, 466, W - 90, 58,
                    "Форма з v2 прийняла сховище в наготовану комірку: порт DeviceRepository не зрушив,\n"
                    "SQLite стала за нього одним рядком, а ядро домену спить незворушно.",
                    size=13, bold=True, fill="#fbfbe8", stroke="#c9b458", color=INK, sw=2))

    render(os.path.join(IMG, "v3-wiring.svg"), W, H, *f,
           title="Точка збірки v3: реєстр переселився, порт не зрушив")


# ───────── proj-3: три докази зібраного v3 ─────────
def fig_three_proofs():
    W, H = 1120, 446
    f = []

    c1x, c1w = 40, 250
    c2x, c2w = 300, 430
    c3x, c3w = 740, 340

    # шапка колонок
    hy = 50
    f.append(fitbox(c1x, hy, c1w, 32, "обіцянка", size=13, bold=True,
                    fill=HEAD_T, stroke=MUTED, color=INK))
    f.append(fitbox(c2x, hy, c2w, 32, "як доводимо", size=13, bold=True,
                    fill=HEAD_T, stroke=MUTED, color=INK))
    f.append(fitbox(c3x, hy, c3w, 32, "що доведено", size=13, bold=True,
                    fill=HEAD_T, stroke=MUTED, color=INK))

    rows = [
        ("1 · Реєстр переживає\nрестарт",
         "save_home → close → reopen\nнад тим самим файлом → load",
         "пристрої на місці після смерті процесу;\nrun_migrations на 2-му старті — no-op"),
        ("2 · Агрегат лягає\nатомарно",
         "save_home із пристроєм, що ламає\nCHECK(kind) посеред циклу",
         "rollback усього: конфіг незмінний,\nжодного пристрою напівзаписаного"),
        ("3 · Тариф не\nперевищити",
         "8 процесів навперейми add_device\nна device_cap = 5",
         "used_slots == 5 рівно, ніколи більше;\nвартовий судить у мить запису"),
    ]
    ry, rh, rgap = 92, 90, 6
    for i, (name, method, proof) in enumerate(rows):
        y = ry + i * (rh + rgap)
        f.append(fitbox(c1x, y, c1w, rh, name, size=13.5, bold=True,
                        fill=GREEN_T, stroke=FIELD, color=INK, sw=1.8))
        f.append(fitbox(c2x, y, c2w, rh, method, size=13,
                        fill=FILL, stroke="#d7dbe0", color=INK))
        f.append(fitbox(c3x, y, c3w, rh, proof, size=13, bold=True,
                        fill=GREEN_T, stroke=FIELD, color=INK, sw=1.6))

    f.append(fitbox(40, ry + 3 * (rh + rgap) + 6, W - 80, 44,
                    "Доказ — зелений тест на СПРАВЖНІЙ зібраній системі, а не рядок у статті.",
                    size=13.5, bold=True, fill="#fbfbe8", stroke="#c9b458", color=INK, sw=2))

    render(os.path.join(IMG, "three-proofs.svg"), W, H, *f,
           title="Три докази зібраного DH v3")


if __name__ == "__main__":
    fig_truth_across_versions()
    fig_schema_aggregate()
    fig_two_profiles_decision()
    fig_sqlite_ubiquity()
    fig_migration_ladder()
    fig_v3_wiring()
    fig_three_proofs()
    print("OK: truth-across-versions.svg, schema-aggregate.svg, two-profiles-decision.svg, "
          "sqlite-ubiquity.svg, migration-ladder.svg, v3-wiring.svg, three-proofs.svg")
