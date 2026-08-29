#ifndef ALTITUDE_H
#define ALTITUDE_H

#include <stdbool.h>

/* Комплементарний фільтр висоти: швидкість інтегруємо з акселерометра
   (швидко, але спливає), позицію підтягуємо барометром (повільно, зате
   без дрейфу). На виході — висота й вертикальна швидкість. */
typedef struct {
    float alt;          /* м */
    float climb;        /* м/с */
    float k_alt;        /* підтяжка висоти барометром */
    float k_climb;      /* підтяжка швидкості барометром */
    float spike_limit;  /* м, поріг відкидання викидів баро */
    bool  primed;
    unsigned rejected;
} alt_filter_t;

void  alt_filter_init(alt_filter_t *f, float k_alt, float k_climb);
/* baro_alt = NAN, коли свіжого відліку барометра нема. */
void  alt_filter_update(alt_filter_t *f, float baro_alt, float acc_up, float dt);
float alt_filter_altitude(const alt_filter_t *f);
float alt_filter_climb(const alt_filter_t *f);

#endif /* ALTITUDE_H */
