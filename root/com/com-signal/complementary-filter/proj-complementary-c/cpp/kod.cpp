#include <math.h>

typedef struct {
    /* параметри */
    float alpha;        /* базовий коеф. довіри гіроскопу (напр. 0.98f)   */
    float g;            /* очікувана норма прискорення спокою, м/с² (9.81)*/
    float acc_band;     /* допуск |a|−g, за яким акселерометру не вірити  */
    /* стан (живе між тактами) */
    float roll, pitch;  /* поточні оцінки кутів, рад                      */
    int   seeded;       /* чи засіяно стартову оцінку                     */
} Comp;

void comp_init(Comp *c, float alpha, float g, float acc_band)
{
    c->alpha = alpha;  c->g = g;  c->acc_band = acc_band;
    c->roll = 0.0f;  c->pitch = 0.0f;  c->seeded = 0;
}
