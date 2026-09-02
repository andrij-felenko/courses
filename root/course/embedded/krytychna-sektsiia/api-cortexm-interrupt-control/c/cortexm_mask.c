#include "cortexm_mask.h"
#include "nvic_priority.h"

/*
 * Самоперевірка масок. Писана не заради «тестового покриття», а тому що
 * кожен із трьох пунктів нижче — реальна аварія з практики: поріг, який
 * мовчки не увімкнувся; вкладена секція, яка розмаскувала переривання;
 * і два різні уявлення про номер активного виключення.
 *
 * Викликати з main() ДО дозволу переривань периферії.
 */
bool cortexm_mask_selftest(void)
{
    if (cortexm_in_isr()) {
        return false;   /* тест міняє маски — з обробника це небезпечно */
    }

    bool ok = true;

#if !defined(__ARM_ARCH_6M__)
    const uint32_t entry_basepri = __get_BASEPRI();
    const cortexm_state_t primask = cortexm_primask_enter();

    /* 1. Сире число пріоритету в BASEPRI не працює: апаратура відкидає
     *    молодші біти, і в регістрі лишається нуль, тобто «фільтр вимкнено». */
    __set_BASEPRI(0U);
    __set_BASEPRI(5U);
    ok = ok && (__get_BASEPRI() == 0U);

    /* 2. Закодований байт лягає в регістр як є. */
    __set_BASEPRI(NVIC_BASEPRI(5U));
    ok = ok && (__get_BASEPRI() == NVIC_BASEPRI(5U));

    /* 3. BASEPRI_MAX із СЛАБШИМ порогом не робить нічого... */
    __set_BASEPRI_MAX(NVIC_BASEPRI(7U));
    ok = ok && (__get_BASEPRI() == NVIC_BASEPRI(5U));

    /*    ...а із суворішим — оновлює регістр. Саме на цьому тримається
     *    безпечна вкладеність секцій. */
    __set_BASEPRI_MAX(NVIC_BASEPRI(3U));
    ok = ok && (__get_BASEPRI() == NVIC_BASEPRI(3U));

    __set_BASEPRI(entry_basepri);
    cortexm_primask_exit(primask);
#endif

    /* 4. Вкладена PRIMASK-секція: вихід із внутрішньої НЕ вмикає переривання. */
    const cortexm_state_t outer = cortexm_primask_enter();
    const cortexm_state_t inner = cortexm_primask_enter();
    ok = ok && (inner == 1U);                 /* внутрішній бачить уже маску */
    cortexm_primask_exit(inner);
    ok = ok && (__get_PRIMASK() == 1U);       /* маска на місці */
    cortexm_primask_exit(outer);

    /* 5. Асемблерний примітив і CMSIS-інтрінсик читають той самий регістр. */
    ok = ok && (mask_active_exception() == __get_IPSR());

    return ok;
}

/*
 * Інкремент спільного 32-бітного лічильника без вимкнення переривань.
 * LDREX/STREX дешевші за секцію, але ексклюзивний монітор губить резервацію
 * на кожному вході в обробник: під щільним потоком переривань цикл здатен
 * крутитися довго. Тому лічильник спроб є, і після нього — чесна секція.
 */
uint32_t cortexm_atomic_inc(volatile uint32_t *counter)
{
#if !defined(__ARM_ARCH_6M__)
    uint32_t attempts = 0U;
    uint32_t value;

    do {
        if (++attempts > 64U) {
            __CLREX();                    /* знімаємо зависле резервування */
            const cortexm_state_t saved = cortexm_primask_enter();
            value = *counter + 1U;
            *counter = value;
            cortexm_primask_exit(saved);
            return value;
        }
        value = __LDREXW(counter) + 1U;
    } while (__STREXW(value, counter) != 0U);

    __DMB();                              /* результат видно решті системи */
    return value;
#else
    /* ARMv6-M ексклюзивного доступу не має — лише глобальна секція. */
    const cortexm_state_t saved = cortexm_primask_enter();
    const uint32_t value = *counter + 1U;
    *counter = value;
    cortexm_primask_exit(saved);
    return value;
#endif
}

/*
 * 64 біти на 32-бітному ядрі читаються двома інструкціями LDR. Переривання
 * між ними дає «розірване» значення: старша половина нова, молодша стара.
 * Поріг threshold закриває лише тих, хто цю змінну пише.
 */
uint64_t cortexm_read_u64(const volatile uint64_t *src, uint32_t threshold)
{
    const cortexm_state_t saved = cortexm_basepri_enter(threshold);
    const uint64_t value = *src;
    cortexm_basepri_exit(saved);
    return value;
}
