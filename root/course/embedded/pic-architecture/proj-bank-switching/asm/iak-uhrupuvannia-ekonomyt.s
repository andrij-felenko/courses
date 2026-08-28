tick:
    BANKSEL ctr             ; → банк структури, ОДИН раз на всю функцію
    incf    ctr+0, F        ; count_lo++   (ctr+0 — зміщення поля в банку)
    btfss   STATUS, Z
    return
    incf    ctr+1, F        ; count_hi++   — БЕЗ перемикання: той самий банк
    btfss   STATUS, Z
    return
    movlw   1
    movwf   ctr+2           ; overflow_flag = 1 — теж без перемикання
    return
