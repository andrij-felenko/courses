// baro.h — інтерфейс барометра: абстракція, від якої залежать ОБИДВІ сторони.
// Клієнт бачить лише цей файл; полів реалізацій тут немає (непрозорий стан).
#ifndef BARO_H
#define BARO_H

#include <stdint.h>

typedef struct baro baro_t;          // непрозорий: поля приховані в .c реалізації

// Коди контракту — спільні для ВСІХ реалізацій (узгодження помилок, див. пастки).
typedef enum {
    BARO_OK        = 0,   // out_pa містить чинний тиск
    BARO_ERR_BUS   = -1,  // збій шини (немає ACK, таймаут, обрив)
    BARO_ERR_RANGE = -2,  // давач відповів, але значення поза фізичним діапазоном
    BARO_ERR_NODEV = -3,  // на місці давача не той чип (chip-id не збігся)
} baro_status_t;

// Таблиця методів (рукотворна vtable). Кожна реалізація заповнює її своїми функціями.
typedef struct {
    // Прочитати тиск у паскалях. Повертає BARO_OK або код помилки.
    // КОНТРАКТ: не блокує надовго; out_pa чіпає лише при BARO_OK.
    baro_status_t (*read)(baro_t *self, uint32_t *out_pa);
    // Відпустити ресурси (шину, пам'ять). Після close self недійсний.
    void (*close)(baro_t *self);
} baro_vtable_t;

// База, яку реалізація кладе ПЕРШИМ полем своєї структури (див. крок 2).
struct baro {
    const baro_vtable_t *vt;   // вказівник на таблицю методів цієї реалізації
};

// Тонкі обгортки, щоб політика писала baro_read(b, &pa), а не b->vt->read(b, &pa).
static inline baro_status_t baro_read(baro_t *b, uint32_t *out_pa) {
    return b->vt->read(b, out_pa);
}
static inline void baro_close(baro_t *b) { b->vt->close(b); }

#endif // BARO_H
