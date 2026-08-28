#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <math.h>

#define CIC_DECIMATION_RATE 10
#define CIC_ORDER           3
#define WINDOW_SAMPLES      100

/* Стан 3-каскадного CIC дециматора */
typedef struct {
    int32_t integrators[CIC_ORDER];
    int32_t combs[CIC_ORDER];
    int32_t comb_delays[CIC_ORDER];
    uint16_t sample_count;
} CicDecimator;

/* Статистичний акумулятор вікна за алгоритмом Велфорда */
typedef struct {
    uint32_t count;
    float mean;
    float M2;
    float min_val;
    float max_val;
} WelfordAccumulator;

/* Стан алгоритму Swing Door Trending (SDT) */
typedef struct {
    float y0;
    uint32_t t0;
    float s_upper;
    float s_lower;
    float prev_y;
    uint32_t prev_t;
    float tolerance;
    bool has_pending_pivot;
} SdtCompressor;

/* 20-байтовий вихідний бінарний пакет */
typedef struct __attribute__((packed)) {
    uint32_t timestamp;
    uint8_t  status_flags;
    int16_t  pivot_baseline;
    int16_t  mean_val;
    uint16_t rms_val;
    uint16_t peak_to_peak;
    uint8_t  crest_factor_x10;
    uint16_t sdt_point1;
    uint16_t sdt_point2;
    uint16_t crc16;
} SensorPayloadPacket;

/* Ініціалізація компонентів конвеєра */
void cic_init(CicDecimator *cic) {
    memset(cic, 0, sizeof(CicDecimator));
}

void welford_init(WelfordAccumulator *acc) {
    acc->count = 0;
    acc->mean = 0.0f;
    acc->M2 = 0.0f;
    acc->min_val = 1e30f;
    acc->max_val = -1e30f;
}

void sdt_init(SdtCompressor *sdt, float tolerance, uint32_t start_time, float start_val) {
    sdt->tolerance = tolerance;
    sdt->t0 = start_time;
    sdt->y0 = start_val;
    sdt->prev_t = start_time;
    sdt->prev_y = start_val;
    sdt->s_upper = 1e30f;
    sdt->s_lower = -1e30f;
    sdt->has_pending_pivot = false;
}

/* Обробка відліку в CIC дециматорі: повертає true, коли готовий проріджений відлік */
bool cic_process_sample(CicDecimator *cic, int16_t in_sample, int32_t *out_sample) {
    int32_t x = (int32_t)in_sample;

    /* Секція інтеграторів (працює на високій частоті F_in) */
    cic->integrators[0] += x;
    cic->integrators[1] += cic->integrators[0];
    cic->integrators[2] += cic->integrators[1];

    cic->sample_count++;
    if (cic->sample_count < CIC_DECIMATION_RATE) {
        return false;
    }
    cic->sample_count = 0;

    /* Секція дециматора та гребінчастих фільтрів (на частоті F_in / M) */
    int32_t stage_in = cic->integrators[2];
    for (int i = 0; i < CIC_ORDER; i++) {
        int32_t diff = stage_in - cic->comb_delays[i];
        cic->comb_delays[i] = stage_in;
        stage_in = diff;
    }

    /* Масштабування результату з урахуванням підсилення фільтра G = M^N = 10^3 = 1000 */
    *out_sample = stage_in / (CIC_DECIMATION_RATE * CIC_DECIMATION_RATE * CIC_DECIMATION_RATE);
    return true;
}

/* Оновлення статистичного акумулятора новим відліком (алгоритм Велфорда) */
void welford_push(WelfordAccumulator *acc, float val) {
    acc->count++;
    float delta = val - acc->mean;
    acc->mean += delta / (float)acc->count;
    float delta2 = val - acc->mean;
    acc->M2 += delta * delta2;

    if (val < acc->min_val) acc->min_val = val;
    if (val > acc->max_val) acc->max_val = val;
}

/* Обробка точки алгоритмом Swing Door Trending */
bool sdt_push(SdtCompressor *sdt, uint32_t t_now, float y_now, uint32_t *pivot_t, float *pivot_y) {
    if (t_now <= sdt->t0) {
        sdt->prev_t = t_now;
        sdt->prev_y = y_now;
        return false;
    }

    float dt = (float)(t_now - sdt->t0);
    float slope_up = (y_now - (sdt->y0 + sdt->tolerance)) / dt;
    float slope_low = (y_now - (sdt->y0 - sdt->tolerance)) / dt;

    if (slope_up < sdt->s_upper) sdt->s_upper = slope_up;
    if (slope_low > sdt->s_lower) sdt->s_lower = slope_low;

    /* Перевірка закриття дверей (схрещення променів) */
    if (sdt->s_lower > sdt->s_upper) {
        *pivot_t = sdt->prev_t;
        *pivot_y = sdt->prev_y;

        /* Фіксація нової опорної точки */
        sdt->t0 = sdt->prev_t;
        sdt->y0 = sdt->prev_y;
        dt = (float)(t_now - sdt->t0);
        sdt->s_upper = (dt > 0.0f) ? ((y_now - (sdt->y0 + sdt->tolerance)) / dt) : 1e30f;
        sdt->s_lower = (dt > 0.0f) ? ((y_now - (sdt->y0 - sdt->tolerance)) / dt) : -1e30f;
        sdt->prev_t = t_now;
        sdt->prev_y = y_now;
        return true;
    }

    sdt->prev_t = t_now;
    sdt->prev_y = y_now;
    return false;
}

/* ZigZag перетворення для знакових 16-бітних чисел */
static inline uint16_t zigzag_encode16(int16_t val) {
    return (uint16_t)((val << 1) ^ (val >> 15));
}

/* Розрахунок контрольної суми CRC-16-CCITT */
uint16_t crc16_ccitt(const uint8_t *data, size_t len) {
    uint16_t crc = 0xFFFF;
    for (size_t i = 0; i < len; i++) {
        crc ^= (uint16_t)data[i] << 8;
        for (int b = 0; b < 8; b++) {
            if (crc & 0x8000) {
                crc = (crc << 1) ^ 0x1021;
            } else {
                crc <<= 1;
            }
        }
    }
    return crc;
}

/* Формування підсумкового 20-байтового пакета */
void build_payload(SensorPayloadPacket *pkt, uint32_t timestamp, uint8_t status,
                   const WelfordAccumulator *acc, const SdtCompressor *sdt,
                   uint16_t sdt_p1, uint16_t sdt_p2) {
    pkt->timestamp = timestamp;
    pkt->status_flags = status;
    pkt->pivot_baseline = (int16_t)lroundf(sdt->y0);
    pkt->mean_val = (int16_t)lroundf(acc->mean);

    float variance = (acc->count > 1) ? (acc->M2 / (float)(acc->count - 1)) : 0.0f;
    float rms = sqrtf(acc->mean * acc->mean + variance);
    pkt->rms_val = (uint16_t)lroundf(rms);

    float p2p = (acc->max_val > acc->min_val) ? (acc->max_val - acc->min_val) : 0.0f;
    pkt->peak_to_peak = (uint16_t)lroundf(p2p);

    float peak = fmaxf(fabsf(acc->min_val), fabsf(acc->max_val));
    float crest_factor = (rms > 1e-4f) ? (peak / rms) : 1.0f;
    if (crest_factor > 25.5f) crest_factor = 25.5f;
    pkt->crest_factor_x10 = (uint8_t)lroundf(crest_factor * 10.0f);

    pkt->sdt_point1 = sdt_p1;
    pkt->sdt_point2 = sdt_p2;

    /* Розрахунок CRC16 по перших 18 байтах */
    pkt->crc16 = crc16_ccitt((const uint8_t *)pkt, sizeof(SensorPayloadPacket) - sizeof(uint16_t));
}
