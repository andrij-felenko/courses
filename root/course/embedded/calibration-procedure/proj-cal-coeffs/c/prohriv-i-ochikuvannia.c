#define WARMUP_STABLE_CODES   40    // |Δ| між сусідніми відліками — стабільно
#define WARMUP_POLL_MS        1000u // як часто дивимось на дрейф
#define WARMUP_MAX_MS         300000u // 5 хв — стеля; далі грітись марно

static int32_t warmup_prev;
static uint32_t warmup_last_poll;

static void warmup_step(uint32_t t)
{
    if (t - cal.t_enter > WARMUP_MAX_MS) {  // запобіжник: не гріється вічно
        cal_abort(CAL_ERR_NOISY);           // нуль так і не вгамувався — щось не так
        return;
    }
    if (t - warmup_last_poll < WARMUP_POLL_MS) return;
    warmup_last_poll = t;

    int32_t now = sensor_read_raw();
    int32_t drift = now - warmup_prev;
    warmup_prev = now;
    if (drift < 0) drift = -drift;

    if (drift < WARMUP_STABLE_CODES && (t - cal.t_enter) > 3 * WARMUP_POLL_MS) {
        cal.state = CAL_WAIT_LOW;           // нуль устаканився — можна знімати опори
        ui_prompt("Поставте НИЖНЮ опору (тару) і натисніть «зняти»");
    }
}
