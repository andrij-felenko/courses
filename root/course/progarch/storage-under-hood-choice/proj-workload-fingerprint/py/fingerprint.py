"""fingerprint.py — знімає профіль навантаження з лічильників Postgres
і називає клас рушія (B-дерево vs LSM), що лягає під нього.

Не оракул, а рамка: друкує, КУДИ тисне профіль і ЧОМУ — з поправкою
на пастки (коротке вікно, append-ключі, кеш маскує диск)."""

import time
from dataclasses import dataclass
from math import log10

# ── Пороги рішення (відкрито, а не з-під поли) ───────────────────────────────
MIN_WINDOW_S = 900       # коротше 15 хв — вибірка не репрезентативна
MIN_OPS      = 10_000    # менше подій — не вір пропорціям
HIT_FITS     = 0.90      # кеш-влучність, вище якої робочий набір «влазить» у RAM
HIT_WIDTH    = 0.09      # ширина переходу навколо порога
RANGE_DECADE = 2.0       # рядків/запит: 10² = 100 і більше — виразний діапазон

SQL_A = """SELECT s.relname AS tbl, s.n_tup_ins AS ins, s.n_tup_upd AS upd,
       s.n_tup_del AS del, s.seq_scan + s.idx_scan AS scans,
       s.seq_tup_read + s.idx_tup_fetch AS rows_read, s.n_dead_tup AS dead,
       io.heap_blks_read AS disk_blks, io.heap_blks_hit AS cache_blks,
       pg_table_size(s.relid) AS size_bytes
FROM pg_stat_user_tables s JOIN pg_statio_user_tables io USING (relid)
WHERE s.relname = ANY (%(tables)s)"""

SQL_B = """SELECT t.tbl, sum(s.wal_bytes) AS wal_bytes
FROM pg_stat_statements s JOIN unnest(%(tables)s) AS t(tbl)
     ON s.query ILIKE '%%' || t.tbl || '%%'
GROUP BY t.tbl"""

SQL_C = """SELECT tablename AS tbl, correlation AS corr, attname AS key_col
FROM pg_stats WHERE (tablename, attname) IN %(keys)s"""


@dataclass
class Delta:
    """Різниця лічильників між двома знімками — НЕ кумулятив від reset."""
    tbl: str
    window_s: float
    ins: int; upd: int; del_: int         # модифікації рядків
    scans: int; rows_read: int            # сканування й віддані ними рядки
    disk_blks: int; cache_blks: int       # сторінки купи з диска / з кешу
    corr: float; key_col: str             # розкид провідної колонки ключа
    wal_mb: float                         # тиск запису в WAL за вікно
    size_gb: float                        # абсолютний розмір таблиці


def clamp(x, lo=-1.0, hi=1.0):
    return max(lo, min(hi, x))


def derive(d: Delta) -> dict:
    """Сирі лічильники → частки, з яких читається профіль."""
    writes = d.ins + d.upd + d.del_
    reads  = d.scans
    total  = writes + reads
    blks   = d.cache_blks + d.disk_blks
    return {
        "writes": writes, "reads": reads, "total": total,
        "write_share":   writes / total if total else 0.0,
        "rows_per_read": d.rows_read / reads if reads else 1.0,
        "churn":         (d.upd + d.del_) / writes if writes else 0.0,
        "cache_hit":     d.cache_blks / blks if blks else 1.0,
    }


def scorecard(d: Delta, m: dict) -> list[tuple[str, float]]:
    """П'ять сигналів. + тягне до LSM, − до B-дерева. Вага — у множнику."""
    s_write   = (2 * m["write_share"] - 1) * 3            # запис домінує → LSM
    s_range   = -clamp(log10(max(m["rows_per_read"], 1)) / RANGE_DECADE, 0, 1) * 2
    s_ram     = clamp((HIT_FITS - m["cache_hit"]) / HIT_WIDTH, -1, 1) * 2
    s_scatter = (1 - 2 * abs(d.corr)) * m["write_share"] * 2   # зважено обсягом запису
    s_churn   = -m["churn"] * 1                            # багато правок → на місці
    return [("запис домінує",           s_write),
            ("читання діапазоном",       s_range),
            ("робочий набір > RAM",      s_ram),
            ("ключ урозкид",             s_scatter),
            ("правки на місці (churn)",  s_churn)]


def verdict(d: Delta, m: dict, card):
    """Сума → рушій і впевненість. Жорсткі гейти б'ють по довірі,
    м'які застереження лишають вердикт, але просять пильності."""
    total = sum(v for _, v in card)
    hard, soft = [], []
    if d.window_s < MIN_WINDOW_S:
        hard.append(f"вікно {d.window_s:.0f} с < {MIN_WINDOW_S} с — надто коротке")
    if m["total"] < MIN_OPS:
        hard.append(f"лише {m['total']} операцій у вибірці — замало")
    if m["cache_hit"] >= 0.995 and m["reads"] > m["writes"]:
        soft.append("кеш ~100%: читання дешеві, ПОКИ набір влазить у RAM — стеж за ростом")
    if abs(d.corr) >= 0.95 and m["write_share"] > 0.5:
        soft.append(f"ключ {d.key_col} майже впорядкований (corr={d.corr:+.2f}) — "
                    "виграш LSM на записі менший, ніж каже гола теорія")
    if hard:               band = "НЕ ДОВІРЯЙ — мало даних"
    elif abs(total) >= 4:  band = "впевнено"
    elif abs(total) >= 2:  band = "схиляється"
    else:                  band = "нерішуче — числа майже рівні"
    engine = "LSM (журнальне)" if total > 0 else "B-дерево (на місці)"
    arrow  = "▶" if total > 0 else "◀"
    return total, engine, arrow, band, hard, soft


def fmt(v):                                   # −0.00 читається як помилка — гасимо
    return f"{v:+.2f}" if abs(v) >= 0.005 else " 0.00"


def report(d: Delta):
    m = derive(d)
    card = scorecard(d, m)
    total, engine, arrow, band, hard, soft = verdict(d, m, card)
    shape = "точкові" if m["rows_per_read"] < 3 else "діапазон"
    fits  = "влазить у RAM" if m["cache_hit"] >= HIT_FITS else "НЕ влазить у RAM"
    print(f"\n━━━ {d.tbl} " + "━" * max(3, 56 - len(d.tbl)))
    print(f"  вікно {d.window_s:.0f} с · {m['total']:,} операцій · {d.size_gb:.1f} ГБ на диску"
          .replace(",", " "))
    print(f"  запис/читання ......... {m['write_share']*100:4.1f}% запис"
          f"   ({m['writes']:,} змін : {m['reads']:,} читань, ≈{d.wal_mb:.0f} МБ WAL)".replace(",", " "))
    print(f"  форма читань .......... {shape} — {m['rows_per_read']:.1f} рядків/запит")
    print(f"  правки (upd+del) ...... {m['churn']*100:4.1f}% від запису")
    print(f"  кеш купи .............. {m['cache_hit']*100:5.1f}% влучень → набір {fits}")
    print(f"  розкид ключа .......... corr({d.key_col}) = {d.corr:+.2f}")
    print("  ── скоркарта (+ до LSM · − до B-дерева) " + "─" * 20)
    for name, v in card:
        print(f"    {name:.<26} {fmt(v)}")
    print(f"    {'СУМА':.<26} {fmt(total)}")
    print(f"  ВЕРДИКТ {arrow} {engine} — {band}")
    for w in hard: print(f"    ⛔ {w}")
    for w in soft: print(f"    ⚠  {w}")


def measure(conn, tables, keys, window_s):
    """Два знімки з паузою → Delta по кожній таблиці (тут для повноти; у статті
    нижче годуємо вже зняті різниці, щоб скрипт бігав і без живої бази)."""
    def snap():
        with conn.cursor() as cur:
            cur.execute(SQL_A, {"tables": tables})
            a = {r[0]: r for r in cur.fetchall()}
            cur.execute(SQL_B, {"tables": tables})
            b = {r[0]: r for r in cur.fetchall()}
            cur.execute(SQL_C, {"keys": tuple(keys)})
            c = {r[0]: r for r in cur.fetchall()}
        return time.time(), a, b, c
    t0, a0, b0, _ = snap()
    time.sleep(window_s)
    t1, a1, b1, c1 = snap()
    out = []
    for t in tables:
        p, q = a0[t], a1[t]                       # p — раніше, q — тепер
        out.append(Delta(t, t1 - t0,
            q[1]-p[1], q[2]-p[2], q[3]-p[3], q[4]-p[4], q[5]-p[5],
            q[7]-p[7], q[8]-p[8], c1[t][1], c1[t][2],
            (b1[t][1]-b0[t][1]) / 1e6, q[9] / 1e9))
    return out
