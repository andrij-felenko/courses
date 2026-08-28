#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    uint16_t dist_mm;   // виміряна відстань, мм
    uint16_t strength;  // сила відлуння (напр. 0..1023); 0 = нема луни
    uint32_t t_ms;      // мітка часу САМОГО виміру, мс
    bool     valid;     // чи відлуння взагалі прийшло
} Sample;

typedef enum {
    RF_FRESH,   // свіжий достовірний вимір
    RF_HELD,    // тримаємо старе (короткий пропуск або відкинутий стрибок)
    RF_LOST     // надто довго наосліп — відстань НЕВІДОМА (для уникання = небезпека)
} RangeStatus;

typedef struct {
    RangeStatus status;
    uint16_t    mm;      // згладжена за довірою оцінка
    uint16_t    med_mm;  // гейтований медіан — крайо-зберігаючий, для безпекових рішень
    float       conf;    // довіра до цього виміру, 0..1
} RangeResult;

typedef struct {
    uint16_t ring[3];        // кільцевий буфер сирих відстаней для медіани-3
    uint8_t  head, fill;     // куди писати; скільки вже лягло (0..3)

    uint16_t last_mm;        // останнє ПРИЙНЯТЕ значення — опора воріт
    uint32_t last_ms;
    bool     have_last;

    float    est;            // згладжена оцінка
    bool     have_est;

    uint16_t vmax_mm_s;      // найгірша швидкість ЗБЛИЖЕННЯ, мм/с
    uint16_t margin_mm;      // запас воріт на шум самого виміру
    uint16_t floor, full;    // межі сили: нижче floor — dropout, вище full — повна довіра
    float    base_alpha;     // базова жвавість злиття при повній довірі
    uint8_t  max_drops;      // скільки пропусків поспіль тримати старе, тоді LOST
    uint8_t  max_rejects;    // скільки «неможливих» стрибків поспіль терпіти, тоді пере-захопити
    uint8_t  drops, rejects; // поточні лічильники
} RangeFilter;
