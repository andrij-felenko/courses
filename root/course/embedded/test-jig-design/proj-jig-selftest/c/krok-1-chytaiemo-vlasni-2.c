// Коефіцієнти дільників (×1000, щоб рахувати цілими).
// Напр. дільник 2:1 (однакові резистори) множить назад на 2.000 → 2000.
#define DIV_5V_X1000    2000u      // шина 5 В поділена навпіл
#define DIV_3V3_X1000   1000u      // 3.3 В заведена прямо (в межах Vref)

typedef struct {
    uint16_t v33_mv;
    uint16_t v5_mv;
    uint16_t vref_measured_mv;   // сама опорна — теж поле рапорту, корисно бачити
} rails_t;

void read_rails(rails_t *r) {
    uint16_t vref = measure_vref_mv();
    r->vref_measured_mv = vref;

    uint16_t raw33 = adc_read_avg(ADC_CH_RAIL_3V3);
    uint16_t raw5  = adc_read_avg(ADC_CH_RAIL_5V);

    // спочатку у мілівольти на вході АЦП, тоді назад через коефіцієнт дільника
    r->v33_mv = (uint16_t)((uint32_t)adc_to_mv(raw33, vref) * DIV_3V3_X1000 / 1000u);
    r->v5_mv  = (uint16_t)((uint32_t)adc_to_mv(raw5,  vref) * DIV_5V_X1000  / 1000u);
}
