#include <stdint.h>
#include <string.h>
#include "core_cm7.h"   // CMSIS: __DSB, __ISB, SCB_* — кеш-операції

// ram_func мусить бути вирівняний на РОЗМІР ЛІНІЇ КЕШУ (32 байти на M7),
// інакше службова операція зачепить сусідні дані в тій самій лінії.
extern uint8_t ram_func[] __attribute__((aligned(32)));
extern const uint8_t new_body[];
extern const uint32_t new_body_size;

typedef int (*fn_t)(int);

int patch_and_call_m7(int arg)
{
    // 1. Записуємо нове тіло — воно осідає в D-Cache (як дані).
    memcpy(ram_func, new_body, new_body_size);

    // 2. Вигнати нове тіло з D-Cache у саму RAM (clean = flush dirty-ліній).
    //    CMSIS усередині цієї функції робить DSB → запис у регістр кешу →
    //    DSB → ISB, тож дані гарантовано опиняються в RAM.
    SCB_CleanDCache_by_Addr((uint32_t *)ram_func, (int32_t)new_body_size);

    // 3. Викинути СТАРЕ тіло з I-Cache — інакше вибірка команд і далі
    //    віддаватиме старий код із кешу команд, ігноруючи оновлену RAM.
    SCB_InvalidateICache();

    // 4. Про всяк випадок замкнути пару бар'єрів (CMSIS-функції вже містять
    //    свої DSB/ISB усередині; цей рядок — явна страховка на стику).
    __DSB();
    __ISB();

    fn_t fn = (fn_t)((uintptr_t)ram_func | 1u);
    return fn(arg);
}
