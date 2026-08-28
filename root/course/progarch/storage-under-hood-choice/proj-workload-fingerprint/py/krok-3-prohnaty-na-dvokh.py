# Різниці, які SQL зняв за годинне вікно на проді DH (два знімки, віднято):
measurement = Delta("measurement", window_s=3600,
    ins=24_000_000, upd=0, del_=0,              # майже чистий потік вставок
    scans=40_000, rows_read=10_000_000,         # 250 рядків на запит — діапазони за часом
    disk_blks=22_000_000, cache_blks=28_000_000,# кеш ловить лиш 56% — набір величезний
    corr=0.03, key_col="device_id",             # тисячі сенсорів упереміш → врозкид
    wal_mb=2900, size_gb=800)

device = Delta("device", window_s=3600,
    ins=20, upd=3_000, del_=50,                 # мало пишуть: нові пристрої, зміни власника
    scans=2_000_000, rows_read=2_000_000,       # 1 рядок на запит — точкові пошуки
    disk_blks=1_200, cache_blks=40_000_000,     # майже все з кешу — набір малий
    corr=0.98, key_col="id",                    # id-лічильник упорядкований (та запису мало)
    wal_mb=1, size_gb=0.4)

for d in (measurement, device):
    report(d)
