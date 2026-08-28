#include "cmsis_compiler.h"   // CMSIS: __get_PRIMASK / __disable_irq / __set_PRIMASK

void *pool_alloc(void) {
    uint32_t primask = __get_PRIMASK();  // запам'ятали: переривання зараз дозволені чи вже ні
    __disable_irq();                     // глушимо ВСІ переривання — нас ніхто не перерве
    void *blk = pool_alloc_unsafe();     // три присвоєння в цілковитій тиші
    __set_PRIMASK(primask);              // повертаємо РІВНО той стан, що був на вході
    return blk;
}

bool pool_free(void *blk) {
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    bool ok = pool_free_unsafe(blk);
    __set_PRIMASK(primask);
    return ok;
}
