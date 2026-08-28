#include <libdlm.h>
#include <stdint.h>

/* Системна структура LKSB з бібліотеки libdlm */
struct dlm_lksb {
    int      sb_status;  /* Результат операції (0 — успіх, або стандартний errno) */
    uint32_t sb_lkid;    /* Унікальний числовий ідентифікатор блокування (Lock ID) */
    char     sb_flags;   /* Прапорці зворотного зв'язку від ядра */
    char    *sb_lvbptr;  /* Покажчик на 32-байтовий або 64-байтовий буфер LVB */
};
