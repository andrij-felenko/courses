from enum import IntEnum

# Коди проблем — стабільні числа, на які може зважати зовнішній скрипт.
class BomError(IntEnum):
    ERR_QTY_MISMATCH  = 1   # К-сть ≠ кількість перелічених позначень
    ERR_NO_MPN        = 2   # монтуємо (не DNP), але MPN немає
    ERR_DUP_REFDES    = 3   # те саме позначення трапляється двічі
    ERR_ORPHAN_BOARD  = 4   # є на платі, нема в BOM
    ERR_ORPHAN_BOM    = 5   # є в BOM, нема на платі
    ERR_BOM_NOT_SCHEM = 6   # є в BOM, нема в схемі
    ERR_SCHEM_NOT_BRD = 7   # є в схемі, нема на платі
