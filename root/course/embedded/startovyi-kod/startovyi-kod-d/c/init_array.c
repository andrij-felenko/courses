#include "startup.h"

typedef void (*init_fn_t)(void);

/* Межі таблиць покажчиків розставляє лінкер. У .preinit_array складають
   ініціалізацію, яка мусить відпрацювати ДО конструкторів, у
   .init_array — самі конструктори глобальних об'єктів C++. */
extern init_fn_t __preinit_array_start[];
extern init_fn_t __preinit_array_end[];
extern init_fn_t __init_array_start[];
extern init_fn_t __init_array_end[];

static void run_table(init_fn_t *begin, init_fn_t *end)
{
    for (init_fn_t *slot = begin; slot < end; ++slot) {
        /* Порожній запис лишає лінкер, коли викидає невикористаний
           об'єктний файл: викликати нуль означало б стрибок у нікуди. */
        if (*slot != NULL) {
            (*slot)();
        }
    }
}

void startup_run_init_array(void)
{
    run_table(__preinit_array_start, __preinit_array_end);
    run_table(__init_array_start, __init_array_end);
}
