#include <stdint.h>
#include <stdbool.h>

typedef struct {
    double a_z0;            /* Ефективне значення сонячного потоку Az (SFU) */
    double a_z1;            /* Лінійний коефіцієнт за широтою MODIP */
    double a_z2;            /* Квадратичний коефіцієнт за широтою MODIP */
    uint8_t region_flags;   /* 5 біт регіональних прапорців іоносферного шторму */
    uint32_t issue_of_data; /* Ідентифікатор версії даних IODN (Issue of Data) */
    bool is_valid;
} galileo_nequick_broadcast_t;

/**
 * Ініціалізує структуру NeQuick-G за замовчуванням при відсутності супутникових поправок.
 */
static inline void galileo_nequick_set_default(galileo_nequick_broadcast_t* params) {
    params->a_z0 = 63.7;  /* Середнє значення сонячного потоку у спокійний період */
    params->a_z1 = 0.0;
    params->a_z2 = 0.0;
    params->region_flags = 0;
    params->issue_of_data = 0;
    params->is_valid = false;
}
