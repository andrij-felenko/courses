/*
 * Селективне маскування за пріоритетом (BASEPRI).
 *
 * BASEPRI є лише на ядрах з архітектурою ARMv7-M і ARMv8-M Mainline —
 * Cortex-M3/M4/M7/M33. Ознаку дає компілятор із -mcpu, тому на збірці під
 * Cortex-M0 файл згортається в порожній об'єктний модуль, а не ламає збірку.
 */

#include "cortex_m.inc"

#if defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || \
    defined(__ARM_ARCH_8M_MAIN__)

/* uint32_t cs_get_basepri(void) */
CS_FUNC cs_get_basepri
    mrs     r0, BASEPRI
    bx      lr
CS_ENDF cs_get_basepri

/* void cs_set_basepri(uint32_t value) — беззастережний запис. */
CS_FUNC cs_set_basepri
    msr     BASEPRI, r0
    bx      lr
CS_ENDF cs_set_basepri

/*
 * void cs_set_basepri_max(uint32_t value)
 *
 * Апаратура сама відкидає запис, який послабив би маскування: нове значення
 * лягає тільки якщо воно ненульове й чисельно менше за чинне (менше число —
 * вищий пріоритет), або якщо чинне дорівнює нулю. Саме тому вкладений блок
 * зі слабшим порогом безпечний і не потребує жодної перевірки в коді.
 */
CS_FUNC cs_set_basepri_max
    msr     BASEPRI_MAX, r0
    bx      lr
CS_ENDF cs_set_basepri_max

/*
 * uint32_t cs_prio_enter(uint32_t threshold)
 *
 * Поріг подається вже зміщеним у старші біти поля пріоритету (див.
 * cs_prio_encode). Повертає попереднє значення BASEPRI.
 *
 * Переривання з пріоритетом, вищим за поріг, і далі виконуються: саме на це
 * розраховують швидкі обробники прямого керування апаратурою. Тому все, до
 * чого такі обробники дотягуються, цією секцією НЕ захищене.
 */
CS_FUNC cs_prio_enter
    mrs     r1, BASEPRI
    msr     BASEPRI_MAX, r0
    mov     r0, r1
    bx      lr
CS_ENDF cs_prio_enter

/* void cs_prio_exit(uint32_t saved) */
CS_FUNC cs_prio_exit
    msr     BASEPRI, r0
    bx      lr
CS_ENDF cs_prio_exit

/*
 * uint32_t cs_prio_bits(void)
 *
 * Скільки бітів пріоритету кристал реалізував насправді. Архітектура дозволяє
 * від 3 до 8; STM32 дає 4, Nordic — 3. Число не прочитати з регістра, тому
 * його виявляють дослідом: записати в байт пріоритету одиниці й подивитись,
 * що повернеться. Нереалізовані молодші біти читаються нулями.
 *
 * Псуємо й одразу повертаємо IPR[0] (пріоритет нульового переривання), тож
 * кличемо це на старті, до налаштування NVIC, і під маскою.
 */
CS_FUNC cs_prio_bits
    CS_LDIMM32 r1, NVIC_IPR0
    mrs     r3, PRIMASK
    cpsid   i                       @ поки міряємо, поле пріоритету наше
    ldrb    r2, [r1]                @ зберегти чинний пріоритет
    movs    r0, #0xFF
    strb    r0, [r1]
    dsb
    ldrb    r0, [r1]                @ повернуться лише реалізовані біти
    strb    r2, [r1]                @ покласти як було
    dsb
    msr     PRIMASK, r3
    cbz     r0, .Lbits_none
    rbit    r0, r0
    clz     r0, r0                  @ скільки молодших нулів у прочитаному
    rsb     r0, r0, #8              @ реалізовано = 8 - хвіст нулів
    bx      lr
.Lbits_none:
    bx      lr                      @ 0 — поле пріоритету не пишеться взагалі
CS_ENDF cs_prio_bits

/*
 * uint32_t cs_prio_encode(uint32_t level)
 *
 * Логічний рівень (0 — найвищий) у значення для BASEPRI. При чотирьох
 * реалізованих бітах рівень 5 дає 0x50 — те саме число, що стоїть у
 * прикладах PRIORITY_BLOCK і PriorityGuard.
 *
 * Рівень 0 навмисно не відсіюємо: BASEPRI = 0 означає «не маскуємо», і
 * викликач мусить знати, що просив саме цього. Перевірку робить шар вище —
 * у C++ це static_assert у BasepriLockPolicy.
 */
CS_FUNC cs_prio_encode
    push    {r4, lr}
    mov     r4, r0
    bl      cs_prio_bits
    rsb     r1, r0, #8              @ зсув = 8 - реалізовані біти
    lsl     r0, r4, r1
    uxtb    r0, r0                  @ BASEPRI — восьмибітове поле
    pop     {r4, pc}
CS_ENDF cs_prio_encode

#endif /* ARMv7-M / ARMv8-M Mainline */
