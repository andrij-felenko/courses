/* telemetry_optimizer.h & telemetry_optimizer.c — Чистий C (C99) */
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define TELEMETRY_MAX_BATCH_SAMPLES  32
#define TELEMETRY_PAYLOAD_MAX_BYTES  256

typedef enum {
    TELEM_OK = 0,
    TELEM_DROPPED_NOISE = 1,
    TELEM_BUFFERED = 2,
    TELEM_BATCH_READY = 3,
    TELEM_ERR_OVERFLOW = -1,
    TELEM_ERR_PARAM = -2
} telem_status_t;

/* Структура одного вимірювання */
typedef struct {
    uint32_t timestamp_sec;
    int32_t  value_fixed;   /* Фіксована кома (наприклад, градуси × 100) */
} telem_sample_t;

/* Конфігурація зони нечутливості (Deadband) */
typedef struct {
    int32_t  deadband_abs;      /* Мінімальна абсолютна дельта для запису */
    uint32_t max_interval_sec;  /* Примусовий інтервал запису (Heartbeat) */
} telem_filter_config_t;

/* Стан оптимізатора */
typedef struct {
    telem_filter_config_t cfg;
    telem_sample_t        last_saved_sample;
    bool                  has_baseline;
    
    /* Кільцевий буфер накопичення */
    telem_sample_t        sample_buffer[TELEMETRY_MAX_BATCH_SAMPLES];
    uint16_t              sample_count;
    
    /* Діагностичні прапорці здоров'я вузла */
    uint16_t              system_health_flags;
} telem_optimizer_t;

void telem_init(telem_optimizer_t *opt, const telem_filter_config_t *cfg) {
    if (!opt || !cfg) return;
    memset(opt, 0, sizeof(telem_optimizer_t));
    opt->cfg = *cfg;
    opt->has_baseline = false;
    opt->sample_count = 0;
    opt->system_health_flags = 0;
}

void telem_set_health_flag(telem_optimizer_t *opt, uint16_t flag_mask, bool active) {
    if (!opt) return;
    if (active) {
        opt->system_health_flags |= flag_mask;
    } else {
        opt->system_health_flags &= ~flag_mask;
    }
}

/* Перевірка необхідності збереження вимірювання */
static bool telem_should_save(telem_optimizer_t *opt, const telem_sample_t *s) {
    if (!opt->has_baseline) return true;

    /* Примусовий запис за максимальним тайм-аутом */
    if ((s->timestamp_sec - opt->last_saved_sample.timestamp_sec) >= opt->cfg.max_interval_sec) {
        return true;
    }

    /* Фільтрація Deadband */
    int32_t diff = s->value_fixed - opt->last_saved_sample.value_fixed;
    if (diff < 0) diff = -diff;

    return (diff >= opt->cfg.deadband_abs);
}

/* Запис нового вимірювання в оптимізатор */
telem_status_t telem_push_sample(telem_optimizer_t *opt, uint32_t ts, int32_t val) {
    if (!opt) return TELEM_ERR_PARAM;

    telem_sample_t current = { .timestamp_sec = ts, .value_fixed = val };

    if (!telem_should_save(opt, &current)) {
        return TELEM_DROPPED_NOISE;
    }

    if (opt->sample_count >= TELEMETRY_MAX_BATCH_SAMPLES) {
        return TELEM_ERR_OVERFLOW;
    }

    opt->sample_buffer[opt->sample_count++] = current;
    opt->last_saved_sample = current;
    opt->has_baseline = true;

    if (opt->sample_count >= TELEMETRY_MAX_BATCH_SAMPLES) {
        return TELEM_BATCH_READY;
    }

    return TELEM_BUFFERED;
}

/* Серіалізація батчу у компактний бінарний кадр */
int32_t telem_serialize_batch(telem_optimizer_t *opt, uint8_t *out_buf, uint16_t max_len) {
    if (!opt || !out_buf || opt->sample_count == 0) return TELEM_ERR_PARAM;

    /* Оцінка необхідного розміру: заголовок (6Б) + базова точка (8Б) + дельти (4Б/точка) */
    uint16_t required_len = 6 + 8 + (opt->sample_count - 1) * 4;
    if (max_len < required_len) return TELEM_ERR_OVERFLOW;

    uint16_t ptr = 0;

    /* 1. Заголовок кадру */
    out_buf[ptr++] = 0xAA; /* Magic byte */
    out_buf[ptr++] = 0x01; /* Версія протоколу */
    out_buf[ptr++] = (uint8_t)opt->sample_count;
    
    /* Прапорці здоров'я (2 байти) */
    out_buf[ptr++] = (uint8_t)(opt->system_health_flags & 0xFF);
    out_buf[ptr++] = (uint8_t)((opt->system_health_flags >> 8) & 0xFF);
    out_buf[ptr++] = 0x00; /* Зарезервовано */

    /* 2. Базова точка (повна мітка часу та повне значення) */
    telem_sample_t base = opt->sample_buffer[0];
    memcpy(&out_buf[ptr], &base.timestamp_sec, sizeof(uint32_t));
    ptr += sizeof(uint32_t);
    memcpy(&out_buf[ptr], &base.value_fixed, sizeof(int32_t));
    ptr += sizeof(int32_t);

    /* 3. Дельта-кодовані точки (Δt у секундах uint16_t, Δv у фіксованих одиницях int16_t) */
    for (uint16_t i = 1; i < opt->sample_count; ++i) {
        uint32_t dt = opt->sample_buffer[i].timestamp_sec - base.timestamp_sec;
        int32_t  dv = opt->sample_buffer[i].value_fixed - base.value_fixed;

        uint16_t dt_u16 = (dt > 0xFFFF) ? 0xFFFF : (uint16_t)dt;
        int16_t  dv_i16 = (dv > 32767) ? 32767 : ((dv < -32768) ? -32768 : (int16_t)dv);

        memcpy(&out_buf[ptr], &dt_u16, sizeof(uint16_t));
        ptr += sizeof(uint16_t);
        memcpy(&out_buf[ptr], &dv_i16, sizeof(int16_t));
        ptr += sizeof(int16_t);
    }

    /* Скидання буфера після успішної серіалізації */
    opt->sample_count = 0;
    return (int32_t)ptr;
}
