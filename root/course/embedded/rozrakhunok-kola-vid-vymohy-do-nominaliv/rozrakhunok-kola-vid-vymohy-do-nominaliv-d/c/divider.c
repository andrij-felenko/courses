#include "divider.h"

const divider_cal_t DIV_CAL_IDENTITY = { DIV_GAIN_UNITY, 0 };

/* Стеля суми плечей. Це і санітарна перевірка (дільник на гігаоми не буває),
   і гарантія, що чисельник нижче не переповнить 64 біти:
   65535 * 65535 * 1e8 ~ 4.3e17 < 1.8e19. */
#define DIV_RSUM_MAX 100000000u

/* Фізична стеля вузла: 1 кВ. Вище — не вимірювання, а помилка в паспорті. */
#define DIV_MV_MAX 1000000

/* Ділення з округленням до найближчого. Просте відкидання дробової частини
   на кожному кроці стабільно з'їдає до молодшого розряду АЦП. */
static uint64_t udiv_round(uint64_t num, uint64_t den)
{
    return (num + den / 2u) / den;
}

static int64_t sdiv_round(int64_t num, int64_t den)
{
    return (num >= 0) ? (num + den / 2) / den
                      : -(((-num) + den / 2) / den);
}

div_status_t divider_check_spec(const divider_spec_t *spec)
{
    if (spec == NULL) {
        return DIV_ERR_SPEC;
    }
    if (spec->r1_ohms == 0u || spec->r2_ohms == 0u) {
        return DIV_ERR_SPEC;
    }
    if (spec->vref_mv == 0u || spec->adc_max_code == 0u) {
        return DIV_ERR_SPEC;
    }
    if ((uint64_t)spec->r1_ohms + (uint64_t)spec->r2_ohms > (uint64_t)DIV_RSUM_MAX) {
        return DIV_ERR_SPEC;
    }
    return DIV_OK;
}

div_status_t divider_check_cal(const divider_cal_t *cal)
{
    if (cal == NULL) {
        return DIV_ERR_CAL_GAIN;
    }
    if (cal->gain_ppm < DIV_GAIN_MIN || cal->gain_ppm > DIV_GAIN_MAX) {
        return DIV_ERR_CAL_GAIN;
    }
    return DIV_OK;
}

/* Нескалібрована напруга за паспортними номіналами.
   Обидва множення й обидва ділення зведено в ОДИН дріб:
       Vin = raw * Vref * (R1 + R2) / (ADC_MAX * R2)
   Якби рахували в два кроки (спершу напруга на піні, потім масштаб дільника),
   перше округлення множилося б на коефіцієнт 1.5 і давало зайвий мілівольт. */
static int32_t divider_nominal_mv(const divider_spec_t *spec, uint16_t raw)
{
    uint64_t num = (uint64_t)raw * (uint64_t)spec->vref_mv
                 * ((uint64_t)spec->r1_ohms + (uint64_t)spec->r2_ohms);
    uint64_t den = (uint64_t)spec->adc_max_code * (uint64_t)spec->r2_ohms;
    uint64_t mv  = udiv_round(num, den);

    if (mv > (uint64_t)DIV_MV_MAX) {
        mv = (uint64_t)DIV_MV_MAX;
    }
    return (int32_t)mv;
}

div_status_t divider_raw_to_mv(const divider_spec_t *spec, const divider_cal_t *cal,
                               uint16_t raw, int32_t *out_mv)
{
    div_status_t st;
    int32_t nominal;
    int64_t scaled;

    if (out_mv == NULL) {
        return DIV_ERR_SPEC;
    }
    st = divider_check_spec(spec);
    if (st != DIV_OK) {
        return st;
    }
    st = divider_check_cal(cal);
    if (st != DIV_OK) {
        return st;
    }
    /* Код більший за роздільність — це не «трохи завелика напруга», а збій
       драйвера АЦП чи неузгоджене вирівнювання результату (ліве/праве). */
    if (raw > spec->adc_max_code) {
        return DIV_ERR_RAW_RANGE;
    }

    nominal = divider_nominal_mv(spec, raw);
    scaled  = sdiv_round((int64_t)nominal * (int64_t)cal->gain_ppm, (int64_t)DIV_GAIN_UNITY);
    scaled += (int64_t)cal->offset_mv;

    /* Зсув калібрування від'ємний, а на вході нуль — арифметика дає мінус.
       Від'ємної напруги на цьому вузлі бути не може: захисні діоди не пустять. */
    if (scaled < 0) {
        scaled = 0;
    }
    *out_mv = (int32_t)scaled;
    return DIV_OK;
}

div_status_t divider_fit_two_point(const divider_spec_t *spec,
                                   uint16_t raw_lo, int32_t ref_lo_mv,
                                   uint16_t raw_hi, int32_t ref_hi_mv,
                                   divider_cal_t *out_cal)
{
    div_status_t st;
    int32_t  nom_lo, nom_hi;
    uint64_t gain;
    int64_t  offset;

    if (out_cal == NULL) {
        return DIV_ERR_SPEC;
    }
    st = divider_check_spec(spec);
    if (st != DIV_OK) {
        return st;
    }
    if (raw_lo > spec->adc_max_code || raw_hi > spec->adc_max_code) {
        return DIV_ERR_RAW_RANGE;
    }
    if (ref_lo_mv < 0 || raw_hi <= raw_lo) {
        return DIV_ERR_CAL_POINTS;
    }
    if (ref_hi_mv - ref_lo_mv < DIV_CAL_MIN_SPAN_MV) {
        return DIV_ERR_CAL_POINTS;
    }

    nom_lo = divider_nominal_mv(spec, raw_lo);
    nom_hi = divider_nominal_mv(spec, raw_hi);
    if (nom_hi <= nom_lo) {
        return DIV_ERR_CAL_POINTS;
    }

    /* Нахил: у скільки разів справжня різниця напруг більша за паспортну.
       Сюди зібралися разом допуск R1 і R2, похибка опорної напруги
       й підсилення самого АЦП — розділяти їх нема ні потреби, ні змоги. */
    gain = udiv_round((uint64_t)(ref_hi_mv - ref_lo_mv) * (uint64_t)DIV_GAIN_UNITY,
                      (uint64_t)(nom_hi - nom_lo));
    if (gain < (uint64_t)DIV_GAIN_MIN || gain > (uint64_t)DIV_GAIN_MAX) {
        return DIV_ERR_CAL_GAIN;
    }

    /* Зсув: що лишилося в нижній точці після застосування нахилу.
       Це зсув нуля АЦП і струм витоку входу, який тече крізь плече дільника. */
    offset = (int64_t)ref_lo_mv
           - sdiv_round((int64_t)nom_lo * (int64_t)gain, (int64_t)DIV_GAIN_UNITY);
    if (offset < (int64_t)INT32_MIN || offset > (int64_t)INT32_MAX) {
        return DIV_ERR_CAL_POINTS;
    }

    out_cal->gain_ppm  = (uint32_t)gain;
    out_cal->offset_mv = (int32_t)offset;
    return DIV_OK;
}

const char *divider_status_str(div_status_t st)
{
    switch (st) {
    case DIV_OK:              return "ok";
    case DIV_ERR_SPEC:        return "хибні паспортні дані каналу";
    case DIV_ERR_RAW_RANGE:   return "код АЦП поза роздільністю";
    case DIV_ERR_CAL_GAIN:    return "нахил калібрування поза смугою";
    case DIV_ERR_CAL_POINTS:  return "непридатні еталонні точки";
    default:                  return "невідомий стан";
    }
}
