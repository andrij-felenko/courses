@ Лістинг: arm-none-eabi-g++ -O2 -mcpu=cortex-m4 -mthumb -S cpp/navigation.cpp
@ Метод NavigationManager<PrimaskLockPolicy>::update(NavigationData const&)
@ Розкладка об'єкта: data_ 0..23, has_fix_ 24, updates_ 28

_ZN6flight17NavigationManagerIN8embedded4sync17PrimaskLockPolicyEE6updateERKNS_14NavigationDataE:
        push    {r4, r5}
        mrs     r12, PRIMASK      @ конструктор вартового: зберегти маску (1 такт)
        cpsid   i                 @ вимкнути масковані переривання (1 такт)

        @ --- тіло критичної секції ---
        ldrd    r4, r5, [r1, #16] @ timestamp_us вхідної структури
        ldr     r2, [r1, #0]
        ldr     r3, [r1, #4]
        str     r2, [r0, #0]      @ latitude
        str     r3, [r0, #4]      @ longitude
        ldr     r2, [r1, #8]
        str     r2, [r0, #8]      @ altitude_mm
        strd    r4, r5, [r0, #16] @ timestamp_us — один 64-бітний запис
        movs    r3, #1
        strb    r3, [r0, #24]     @ has_fix_ = true
        ldr     r2, [r0, #28]     @ ++updates_ — volatile, тому рівно
        adds    r2, r2, #1        @   одне читання й один запис,
        str     r2, [r0, #28]     @   без LDREX/STREX: маска вже тримає

        @ --- деструктор вартового ---
        msr     PRIMASK, r12      @ відновити попередній стан маски (1 такт)
        pop     {r4, r5}
        bx      lr

@ Написаний руками двійник цієї функції — src/nav_update.S; він же показує,
@ у що обертається достроковий вихід, коли деструктора немає.
@ Виміряти три такти на живому кристалі — cs_measure_enter_exit().
