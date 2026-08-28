typedef enum {
    BAL_IDLE,        // спокій: силова частина вимкнена
    BAL_MEASURE,     // зняти виміри, вирішити
    BAL_BALANCE,     // перенос/розряд триває
    BAL_COOLDOWN,    // силовий вузол охолоджується
} bal_state_t;

typedef struct {
    bal_state_t  state;
    const chem_cfg_t *chem;     // профіль хімії пакета

    int      src, dst;          // індекси: з якої комірки в яку переносимо
    uint16_t spread_mv;         // поточний розкид у шкалі критерію (U-мВ або SOC-‰)
    uint32_t t_state_ms;        // скільки вже в поточному стані
    uint32_t t_balance_ms;      // загальний час безперервного балансу
} balancer_t;

// Граничні часи й періоди — теж під свій силовий вузол.
#define MEASURE_PERIOD_MS   2000     // як часто прокидатись дивитись на пакет
#define BAL_MAX_MS          60000    // максимум безперервного балансу (захист від перегріву за часом)
#define COOLDOWN_MS         15000    // скільки остигати перед новим заходом
#define TICK_MS             100      // період виклику balancer_tick()
