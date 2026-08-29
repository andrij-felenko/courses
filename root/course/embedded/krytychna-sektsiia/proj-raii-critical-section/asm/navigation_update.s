@ Лістинг: arm-none-eabi-g++ -O2 -mcpu=cortex-m4 -mthumb -S navigation.cpp
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
        ldr     r2, [r0, #28]
        adds    r2, r2, #1
        str     r2, [r0, #28]     @ ++updates_

        @ --- деструктор вартового ---
        msr     PRIMASK, r12      @ відновити попередній стан маски (1 такт)
        pop     {r4, r5}
        bx      lr
