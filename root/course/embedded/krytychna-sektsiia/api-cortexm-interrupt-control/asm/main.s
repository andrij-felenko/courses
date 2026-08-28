; --- 1. Швидке глобальне керування через CPS (Change Processor State) ---
CPSID   i             ; Встановити PRIMASK = 1 (вимкнути всі масковані переривання)
CPSIE   i             ; Скинути PRIMASK = 0   (увімкнути всі переривання)

CPSID   f             ; Встановити FAULTMASK = 1 (вимкнути всі виключення, крім NMI)
CPSIE   f             ; Скинути FAULTMASK = 0   (дозволити аварійні виключення)

; --- 2. Універсальний доступ до спеціальних регістрів через MRS / MSR ---
MRS     r0, PRIMASK   ; Зчитати PRIMASK у регістр r0 (1 такт)
MSR     PRIMASK, r0   ; Записати значення r0 у PRIMASK (1 такт)

MRS     r0, BASEPRI   ; Зчитати поточний поріг BASEPRI в r0
MSR     BASEPRI, r0   ; Записати новий поріг у BASEPRI

MSR     BASEPRI_MAX, r0 ; Умовний запис: оновлює BASEPRI тільки якщо r0 підвищує пріоритет маски

MRS     r0, FAULTMASK ; Зчитати поточний стан FAULTMASK
MSR     FAULTMASK, r0 ; Відновити FAULTMASK

MRS     r0, IPSR      ; Зчитати номер поточного виключення для діагностики контексту
