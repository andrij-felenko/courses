navigation_update:
    MRS     r12, PRIMASK      ; r12 = зберегти поточний стан PRIMASK (1 такт)
    CPSID   i                 ; Глобально вимкнути масковані переривання (1 такт)
    
    ; --- Тіло критичної секції ---
    LDR     r3, =g_nav_data
    STR     r0, [r3, #0]      ; latitude
    STR     r1, [r3, #4]      ; longitude
    STR     r2, [r3, #8]      ; altitude_mm
    STRD    r4, r5, [r3, #16] ; timestamp_us (64-бітний запис)
    
    ; --- Вихід з критичної секції (деструктор RAII) ---
    MSR     PRIMASK, r12      ; Відновити попередній стан маски (1 такт)
    BX      LR                ; Повернення з функції
