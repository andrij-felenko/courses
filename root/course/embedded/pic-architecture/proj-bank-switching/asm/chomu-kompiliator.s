tick:
    BANKSEL count_lo        ; → банк 0
    incf    count_lo, F     ; count_lo++   (F: результат назад у комірку)
    btfss   STATUS, Z       ; перекотився? (Z=1 ⇒ count_lo став 0) — якщо так, пропусти RETURN
    return                  ; ні — виходимо
    BANKSEL count_hi        ; → банк 1   ← ПЕРЕМИКАННЯ
    incf    count_hi, F     ; count_hi++
    btfss   STATUS, Z       ; і він перекотився?
    return
    BANKSEL overflow_flag   ; → банк 2   ← ЩЕ ОДНЕ ПЕРЕМИКАННЯ
    movlw   1
    movwf   overflow_flag   ; overflow_flag = 1
    return
