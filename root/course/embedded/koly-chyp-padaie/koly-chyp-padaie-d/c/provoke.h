#ifndef PROVOKE_H
#define PROVOKE_H

/*
 * П'ять типових аварій, кожна з відомим наперед відбитком у регістрах.
 * Це навчальний стенд: викликаєш функцію — читаєш звіт обробника й звіряєш
 * побачені біти з тим, що обіцяє теорія.
 */

void provoke_null_write(void);          /* BFSR.PRECISERR, BFAR = 0x00000000 */
void provoke_unclocked_peripheral(void); /* BFSR.IMPRECISERR (або PRECISERR при DISDEFWBUF) */
void provoke_unaligned(void);            /* UFSR.UNALIGNED */
void provoke_stack_overflow(void);       /* UFSR.UNDEFINSTR або INVSTATE / MMFSR.MSTKERR */
void provoke_bad_function_pointer(void); /* UFSR.INVSTATE */
void provoke_divide_by_zero(void);       /* UFSR.DIVBYZERO */
void provoke_watchdog_hang(void);        /* без скидання IWDG: RCC->CSR.IWDGRSTF */

#endif /* PROVOKE_H */
