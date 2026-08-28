# Півкрокові стани
R_START       = const(0x0)
R_CCW_BEGIN   = const(0x1)
R_CW_BEGIN    = const(0x2)
R_START_M     = const(0x3)
R_CW_BEGIN_M  = const(0x4)
R_CCW_BEGIN_M = const(0x5)

TTABLE_HALF = (
    # R_START
    (R_START_M,           R_CW_BEGIN,    R_CCW_BEGIN,   R_START),
    # R_CCW_BEGIN
    (R_START_M | DIR_CCW, R_START,       R_CCW_BEGIN,   R_START),
    # R_CW_BEGIN
    (R_START_M | DIR_CW,  R_CW_BEGIN,    R_START,       R_START),
    # R_START_M (проміжний «спокій» усередині циклу)
    (R_START_M,           R_CCW_BEGIN_M, R_CW_BEGIN_M,  R_START),
    # R_CW_BEGIN_M
    (R_START_M,           R_START_M,     R_CW_BEGIN_M,  R_START | DIR_CW),
    # R_CCW_BEGIN_M
    (R_START_M,           R_CCW_BEGIN_M, R_START_M,     R_START | DIR_CCW),
)
