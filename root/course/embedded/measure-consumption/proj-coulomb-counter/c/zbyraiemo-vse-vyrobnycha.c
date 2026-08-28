#include <stdint.h>
#include <stdbool.h>

// ── Конфіг тракту: визначається схемою й компонентами ────────────────────────
typedef struct {
    int32_t r_shunt_mohm;   // опір шунта у мілліомах (0.1 Ом = 100)
    int32_t vref_uv;        // опора АЦП у мікровольтах (3.3 В = 3 300 000)
    int32_t adc_max;        // повна шкала АЦП (12 біт = 4095)
    int32_t gain_csa;       // підсилення підсилювача струму (×50 → 50)
} cc_config_t;

// ── Стан лічильника ──────────────────────────────────────────────────────────
typedef struct {
    cc_config_t cfg;
    int32_t  offset_nA;     // приведений зсув тракку (калібрування нуля)
    int64_t  charge_pC;     // накопичений заряд у пікокулонах (знаковий, 64 біт)
    int64_t  time_us;       // сумарний облікований час у мікросекундах
    bool     saturated;     // прапорець: лічильник уперся у стелю int64
} coulomb_counter_t;

// Межа знакового 64-бітного лічильника (INT64_MAX).
#define CC_CHARGE_MAX  9223372036854775807LL

// ── Код АЦП → струм у наноамперах (усе через int64, з відніманням зсуву) ─────
static int32_t cc_code_to_nA(const coulomb_counter_t *cc, uint16_t code)
{
    const cc_config_t *c = &cc->cfg;
    // V_adc[мкВ] = code·Vref/adc_max  — int64, бо добуток великий
    int64_t v_adc_uv  = (int64_t)code * c->vref_uv / c->adc_max;
    // V_shunt[нВ] = V_adc·1000/gain  — тут int32 переповнився б: тримаємо int64
    int64_t v_shunt_nv = v_adc_uv * 1000 / c->gain_csa;
    // I[нА] = V_shunt·1000/R[мОм]
    int64_t i_nA = v_shunt_nv * 1000 / c->r_shunt_mohm;
    // віднімаємо калібрований зсув — результат може бути від'ємним, тому знаковий
    return (int32_t)(i_nA - cc->offset_nA);
}

// ── Калібрування нуля: DUT знеструмлено, усереднюємо багато вибірок ───────────
// read_adc() — платформна функція одного зчитування АЦП струмового каналу.
void cc_calibrate_zero(coulomb_counter_t *cc, uint16_t (*read_adc)(void),
                       uint32_t n_samples)
{
    cc->offset_nA = 0;               // рахуємо сирий струм без старої поправки
    int64_t acc_nA = 0;
    for (uint32_t i = 0; i < n_samples; i++)
        acc_nA += cc_code_to_nA(cc, read_adc());
    cc->offset_nA = (int32_t)(acc_nA / (int64_t)n_samples);   // середнє = зсув
}

// ── Ініціалізація ────────────────────────────────────────────────────────────
void cc_init(coulomb_counter_t *cc, cc_config_t cfg)
{
    cc->cfg       = cfg;
    cc->offset_nA = 0;
    cc->charge_pC = 0;
    cc->time_us   = 0;
    cc->saturated = false;
}

// ── Насичувальне додавання заряду: замість тихого обгортання — впертися у стелю
static void cc_add_charge(coulomb_counter_t *cc, int64_t dQ_pC)
{
    // додатний внесок, що переповнив би стелю → фіксуємо насичення
    if (dQ_pC > 0 && cc->charge_pC > CC_CHARGE_MAX - dQ_pC) {
        cc->charge_pC = CC_CHARGE_MAX;
        cc->saturated = true;
        return;
    }
    cc->charge_pC += dQ_pC;
}

// ── Крок активної фази: викликати рівно раз на dt_us мікросекунд ──────────────
void cc_step_active(coulomb_counter_t *cc, uint16_t adc_code, uint32_t dt_us)
{
    int32_t i_nA = cc_code_to_nA(cc, adc_code);
    // dQ[пКл] = I[нА]·dt[мкс]/1000  — добуток у int64
    int64_t dQ_pC = (int64_t)i_nA * (int64_t)dt_us / 1000;
    cc_add_charge(cc, dQ_pC);
    cc->time_us += dt_us;
}

// ── Один доданок за весь сон: струм сну відомий (даташит/окремий вимір) ───────
void cc_add_sleep(coulomb_counter_t *cc, int32_t i_sleep_nA, uint64_t t_sleep_us)
{
    // весь сон — один прямокутник Рімана, без семплування
    int64_t dQ_pC = (int64_t)i_sleep_nA * (int64_t)t_sleep_us / 1000;
    cc_add_charge(cc, dQ_pC);
    cc->time_us += (int64_t)t_sleep_us;
}

// ── Середній струм за весь облікований час, у наноамперах ─────────────────────
// I_сер = Q/T;  пКл/мкс = 10⁻¹²Кл / 10⁻⁶с = 10⁻⁶ А = мкА → ·1000 → нА
int32_t cc_average_nA(const coulomb_counter_t *cc)
{
    if (cc->time_us == 0) return 0;
    return (int32_t)((cc->charge_pC * 1000) / cc->time_us);
}

// ── Накопичений заряд у мА·год, для порівняння з ємністю батареї ──────────────
// 1 мА·год = 3.6 Кл = 3.6·10¹² пКл
int32_t cc_charge_mAh_milli(const coulomb_counter_t *cc)
{
    // повертаємо тисячні частки мА·год (мкА·год), щоб не втратити дно при діленні
    return (int32_t)(cc->charge_pC / 3600000000LL);   // пКл / (3.6·10⁹) = мкА·год
}
