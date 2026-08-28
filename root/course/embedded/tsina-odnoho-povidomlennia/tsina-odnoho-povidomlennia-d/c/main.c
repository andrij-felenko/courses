#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BATCH_MAX_SAMPLES 16
#define BATCH_MAGIC       0xD7

typedef struct {
    uint32_t timestamp;  /* Повний Unix-час */
    int16_t  temperature; /* T * 100 */
    uint16_t voltage_mv;  /* Напруга в мВ */
} SamplePoint;

typedef struct {
    SamplePoint samples[BATCH_MAX_SAMPLES];
    size_t count;
} BatchBuffer;

void batch_init(BatchBuffer *buf) {
    if (buf) {
        buf->count = 0;
    }
}

bool batch_add(BatchBuffer *buf, uint32_t ts, int16_t temp, uint16_t mv) {
    if (!buf || buf->count >= BATCH_MAX_SAMPLES) {
        return false;
    }
    buf->samples[buf->count].timestamp = ts;
    buf->samples[buf->count].temperature = temp;
    buf->samples[buf->count].voltage_mv = mv;
    buf->count++;
    return true;
}

/* Пакування батчу з дельта-стисненням:
   - Байт 0: Magic + Count
   - Байти 1..4: Base Timestamp
   - Байти 5..6: Base Temperature
   - Байти 7..8: Base Voltage
   - Наступні точки (i > 0):
     - int8_t delta_temp = (temp[i] - temp[i-1])
     - uint8_t delta_ts_div_10 = (ts[i] - ts[i-1]) / 10
     - int8_t delta_v_div_10 = (v[i] - v[i-1]) / 10
*/
size_t batch_serialize_delta(const BatchBuffer *buf, uint8_t *out, size_t out_max) {
    if (!buf || !out || buf->count == 0 || out_max < 9) {
        return 0;
    }

    out[0] = (BATCH_MAGIC & 0xF0) | ((uint8_t)buf->count & 0x0F);

    /* Базова точка */
    uint32_t base_ts = buf->samples[0].timestamp;
    out[1] = (uint8_t)(base_ts >> 24);
    out[2] = (uint8_t)(base_ts >> 16);
    out[3] = (uint8_t)(base_ts >> 8);
    out[4] = (uint8_t)(base_ts);

    int16_t base_temp = buf->samples[0].temperature;
    out[5] = (uint8_t)(base_temp >> 8);
    out[6] = (uint8_t)(base_temp);

    uint16_t base_v = buf->samples[0].voltage_mv;
    out[7] = (uint8_t)(base_v >> 8);
    out[8] = (uint8_t)(base_v);

    size_t offset = 9;

    for (size_t i = 1; i < buf->count; ++i) {
        if (offset + 3 > out_max) {
            return 0; /* Переповнення вихідного буфера */
        }

        uint32_t dt = buf->samples[i].timestamp - buf->samples[i-1].timestamp;
        int16_t  dtemp = buf->samples[i].temperature - buf->samples[i-1].temperature;
        int32_t  dv = (int32_t)buf->samples[i].voltage_mv - (int32_t)buf->samples[i-1].voltage_mv;

        /* Обмеження дельт до розміру int8_t */
        int8_t dt_byte = (dt <= 2550) ? (int8_t)(dt / 10) : 127;
        int8_t dtemp_byte = (dtemp >= -128 && dtemp <= 127) ? (int8_t)dtemp : (dtemp > 0 ? 127 : -128);
        int8_t dv_byte = (dv >= -1280 && dv <= 1270) ? (int8_t)(dv / 10) : (dv > 0 ? 127 : -128);

        out[offset++] = (uint8_t)dt_byte;
        out[offset++] = (uint8_t)dtemp_byte;
        out[offset++] = (uint8_t)dv_byte;
    }

    return offset;
}
