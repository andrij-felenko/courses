#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint16_t igp_number;       /* Номер вузла сітки IGP (1..201) */
    double   delay_vertical_m; /* Вертикальна затримка в метрах (0.125 м LSB) */
    uint8_t  givei;            /* Індекс помилки цілісності (0..15) */
    double   sigma_give_m;     /* Декодоване СКО помилки в метрах */
    bool     is_monitored;     /* Прапорець активного моніторингу */
} sbas_igp_point_t;

/* Двовимірна картографічна інтерполяція в осередку IGP */
typedef struct {
    sbas_igp_point_t corners[4]; /* 4 кутові вузли сітки навколо IPP */
    bool is_valid_quad;          /* Чи всі 4 вузли придатні для інтерполяції */
} sbas_igp_cell_t;
