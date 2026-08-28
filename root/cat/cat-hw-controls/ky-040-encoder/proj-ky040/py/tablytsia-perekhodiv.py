# прапорці напряму — у старших бітах результату
DIR_NONE = 0x00   # цикл ще не завершено
DIR_CW   = 0x10   # завершено крок за годинниковою
DIR_CCW  = 0x20   # завершено крок проти годинникової

# стани самого автомата (проміжні кроки обходу кільця)
R_START     = 0x0
R_CW_FINAL  = 0x1
R_CW_BEGIN  = 0x2
R_CW_NEXT   = 0x3
R_CCW_BEGIN = 0x4
R_CCW_FINAL = 0x5
R_CCW_NEXT  = 0x6

# повнокрокова таблиця: рядок = стан, стовпець = зчитане (CLK<<1)|DT ∈ {0,1,2,3}
TTABLE = (
    # R_START:      00           01           10           11
    (R_START,     R_CW_BEGIN,  R_CCW_BEGIN, R_START),
    # R_CW_FINAL
    (R_CW_NEXT,   R_START,     R_CW_FINAL,  R_START | DIR_CW),
    # R_CW_BEGIN
    (R_CW_NEXT,   R_CW_BEGIN,  R_START,     R_START),
    # R_CW_NEXT
    (R_CW_NEXT,   R_CW_BEGIN,  R_CW_FINAL,  R_START),
    # R_CCW_BEGIN
    (R_CCW_NEXT,  R_START,     R_CCW_BEGIN, R_START),
    # R_CCW_FINAL
    (R_CCW_NEXT,  R_CCW_FINAL, R_START,     R_START | DIR_CCW),
    # R_CCW_NEXT
    (R_CCW_NEXT,  R_CCW_FINAL, R_CCW_BEGIN, R_START),
)
