// ТЗ вузла живлення як незмінна структура. Усі межі — у явних полях,
// напруги в мілівольтах, струми в міліамперах (ціле — без сюрпризів float).
typedef struct {
    uint16_t vin_min_mv;     // сіла батарея — найгірше для дотягування
    uint16_t vin_max_mv;     // повна батарея — найгірше за нагрівом
    uint16_t vin_absmax_mv;  // гранично-допустимий вхід (викиди!)
    uint16_t vout_mv;        // номінал виходу
    uint8_t  vout_tol_pct;   // допуск виходу, відсотки
    uint16_t iout_typ_ma;    // середній струм — нагрів і автономність
    uint16_t iout_peak_ma;   // піковий струм — вибір перетворювача
    int8_t   ta_min_c;       // нижня межа температури середовища
    int8_t   ta_max_c;       // верхня межа — точка дератингу
} power_spec_t;

static const power_spec_t logic_5v = {
    .vin_min_mv    = 12000,  .vin_max_mv = 16800,  .vin_absmax_mv = 28000,
    .vout_mv       = 5000,   .vout_tol_pct = 2,
    .iout_typ_ma   = 300,    .iout_peak_ma = 3000,
    .ta_min_c      = -10,    .ta_max_c   = 70,
};
