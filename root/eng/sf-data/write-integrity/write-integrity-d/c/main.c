#include <stdint.h>
#include <string.h>

typedef struct {
    uint32_t version;     // лічильник; більший = новіший
    config_t data;        // самі налаштування
    uint32_t crc;         // CRC від version+data, записується ОСТАННІМ
} slot_t;

// CRC покриває все, крім самого поля crc (перші два члени структури)
static uint32_t slot_crc(const slot_t *s) {
    return crc32(s, offsetof(slot_t, crc));
}

static int slot_valid(const slot_t *s) {
    return s->crc == slot_crc(s);   // сходиться → слот цілий
}

// читаємо A і B із Flash у RAM, повертаємо чинний конфіг
config_t load_config(const slot_t *a, const slot_t *b) {
    int a_ok = slot_valid(a);
    int b_ok = slot_valid(b);

    if (a_ok && b_ok)
        return (a->version >= b->version) ? a->data : b->data;  // обидва цілі → новіший
    if (a_ok) return a->data;        // лише A цілий
    if (b_ok) return b->data;        // лише B цілий
    return config_defaults();        // жодного — перший старт або обидва биті
}
