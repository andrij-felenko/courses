# Надрукувати позначення з a, яких немає в b, під заданим кодом і підписом.
def report_diff(a, b, code, msg):
    # зробимо вивід упорядкованим, щоб звіт був стабільний між запусками
    missing = sorted(a - b)
    for x in missing:
        print("[E%d] %s: %s" % (code, msg, x))
    return len(missing)

# Надрукувати позначення, що трапилися в списку БІЛЬШЕ одного разу — дублікат на платі
# чи у схемі, який множина сховала б. Мапа лічильників це якраз показує.
def report_dups(counts, source):
    dups = sorted(r for r, n in counts.items() if n > 1)
    for x in dups:
        print("[E%d] позначення %s трапляється %s більше одного разу"
              % (BomError.ERR_DUP_REFDES, x, source))
    return len(dups)

# Повна перевірка: повертає 0, якщо все чисто, або кількість проблем.
def check_consistency(bom_rows, schem_counts, board_counts):
    problems = 0

    # 1) внутрішні перевірки BOM + збір мапи «позначення → рядок» (ловить дублікати BOM)
    bom_map = {}                                          # позначення → рядок
    problems += check_bom_internal(bom_rows, bom_map)

    # 2) дублікати НА ПЛАТІ та У СХЕМІ — те, що множина сама сховала б
    problems += report_dups(board_counts, "на платі")
    problems += report_dups(schem_counts, "у схемі")

    # 3) зводимо кожне джерело до множини позначень
    bom   = set(bom_map)                                  # множина позначень BOM
    schem = set(schem_counts)
    board = set(board_counts)

    # 4) різниці множин — кожна під своїм кодом
    problems += report_diff(board, bom,   BomError.ERR_ORPHAN_BOARD,  "є на платі, нема в BOM")
    problems += report_diff(bom,   board, BomError.ERR_ORPHAN_BOM,    "є в BOM, нема на платі")
    problems += report_diff(bom,   schem, BomError.ERR_BOM_NOT_SCHEM, "є в BOM, нема в схемі")
    problems += report_diff(schem, board, BomError.ERR_SCHEM_NOT_BRD, "є в схемі, нема на платі")

    return problems
