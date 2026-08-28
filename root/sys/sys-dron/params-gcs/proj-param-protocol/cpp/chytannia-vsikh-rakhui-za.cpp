#define PARAM_TIMEOUT_MS  1000     // тиша довша за це = потік завмер

static char    (*names)[16];       // таблиця імен, розмір param_count
static float    *values;
static bool     *got;              // got[i] — чи прийшов параметр i
static uint16_t  total;            // param_count з першого пакета
static uint16_t  have;             // скільки вже маємо
static uint32_t  last_rx_ms;       // коли прийшов останній PARAM_VALUE

// Викликається на КОЖЕН вхідний PARAM_VALUE:
void on_param_value(const mavlink_param_value_t *p) {
    if (total == 0) {                      // перший пакет задає розмір
        total  = p->param_count;
        names  = (char(*)[16]) calloc(total, 16);
        values = (float*)      calloc(total, sizeof(float));
        got    = (bool*)       calloc(total, sizeof(bool));
    }
    uint16_t i = p->param_index;
    if (i < total && !got[i]) {            // дублікати ігноруємо
        memcpy(names[i], p->param_id, 16);
        values[i] = p->param_value;
        got[i]    = true;
        have++;
    }
    last_rx_ms = now_ms();                 // потік живий — зсуваємо таймер
}
