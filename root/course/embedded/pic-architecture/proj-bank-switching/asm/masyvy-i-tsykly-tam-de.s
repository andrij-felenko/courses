sum_buf:
    movlw   buf             ; W ← адреса початку масиву buf
    movwf   FSR             ; FSR ← W   (покажчик на buf[0])
    clrf    sum_lo          ; s = 0
    clrf    sum_hi
    movlw   16
    movwf   i               ; лічильник = 16
loop:
    movf    INDF, W         ; W ← *(FSR)  — узяти buf[поточний], БЕЗ BANKSEL
    addwf   sum_lo, F       ; sum_lo += W
    btfsc   STATUS, C       ; був перенос?
    incf    sum_hi, F       ; так — наростити старший байт суми
    incf    FSR, F          ; FSR++   — посунути покажчик на наступний елемент
    decfsz  i, F            ; i-- ; пропусти goto, коли стало 0
    goto    loop
    return
