    ; a у r0, n у r1.  sum := r2, покажчик іде по r0.
    movs r2, #0             ; sum := 0
    cmp  r1, #0
    beq  .Ldone
    lsls r3, r1, #1        ; r3 := n * 2
    adds r3, r3, r0        ; r3 := a + n*2  (адреса-межа)
.Lloop:
    ldrh r1, [r0], #2      ; LOAD: a[i] (16-біт) → r1, потім r0 += 2
    adds r2, r2, r1        ; sum += a[i]  — ОДИН крок, регістр 32-бітний
    cmp  r0, r3            ; дійшли межі?
    bne  .Lloop           ; ні → назад
.Ldone:
    movs r0, r2            ; результат у r0 (AAPCS)
    bx   lr                ; повернення
