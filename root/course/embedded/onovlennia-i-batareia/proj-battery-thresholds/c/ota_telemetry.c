#include "ota_telemetry.h"

/* Формат пакета (big-endian, як усе на цьому каналі):
     'O' 'T' 'A' версія | код | прапорці | retry_after (4 байти)
     далі TLV: тег(1) довжина(1) значення
   Сервер, що не знає тега, просто перестрибує його за довжиною. */
#define TELEMETRY_VERSION 0x01u
#define FLAG_SERVICE      0x01u

#define TAG_TEMP     0x01u
#define TAG_SOC      0x02u
#define TAG_ESR      0x03u
#define TAG_IDLE     0x04u
#define TAG_LOAD     0x05u
#define TAG_FORECAST 0x06u
#define TAG_FAULTS   0x07u

#define HOUR_S 3600u

typedef struct {
    uint8_t *buf;
    size_t   cap;
    size_t   len;
    bool     overflow;
} writer_t;

static void put_u8(writer_t *w, uint8_t v)
{
    if (w->len + 1u > w->cap) {
        w->overflow = true;
        return;
    }
    w->buf[w->len++] = v;
}

static void put_u16(writer_t *w, uint16_t v)
{
    put_u8(w, (uint8_t)(v >> 8));
    put_u8(w, (uint8_t)(v & 0xFFu));
}

static void put_u32(writer_t *w, uint32_t v)
{
    put_u16(w, (uint16_t)(v >> 16));
    put_u16(w, (uint16_t)(v & 0xFFFFu));
}

static void put_tlv_u8(writer_t *w, uint8_t tag, uint8_t v)
{
    put_u8(w, tag);
    put_u8(w, 1u);
    put_u8(w, v);
}

static void put_tlv_u16(writer_t *w, uint8_t tag, uint16_t v)
{
    put_u8(w, tag);
    put_u8(w, 2u);
    put_u16(w, v);
}

const char *ota_telemetry_code_name(ota_telemetry_code_t code)
{
    switch (code) {
    case OTA_RETRY_COLD:        return "OTA_RETRY_COLD";
    case OTA_RETRY_HOT:         return "OTA_RETRY_HOT";
    case OTA_RETRY_LOW_SOC:     return "OTA_RETRY_LOW_SOC";
    case OTA_ALERT_HIGH_ESR:    return "OTA_ALERT_HIGH_ESR";
    case OTA_ALERT_SENSOR_FAIL: return "OTA_ALERT_SENSOR_FAIL";
    case OTA_ALERT_POWER_FAULT: return "OTA_ALERT_POWER_FAULT";
    }
    return "OTA_UNKNOWN";
}

bool ota_telemetry_summarize(const ota_gate_report_t *report,
                             const ota_limits_t *lim,
                             ota_deny_summary_t *out)
{
    if (report == NULL || lim == NULL || out == NULL) {
        return false;
    }

    out->service_required = false;

    switch (report->verdict) {
    case OTA_DENY_COLD: {
        /* Чекаємо денного прогріву. Глибокий мінус — довше вікно: сонце
           має встигнути витягти комірку в робочий коридор. */
        bool deep = report->has_temp
                 && report->temp_c < (int16_t)(lim->temp_min_c - 5);
        out->code = OTA_RETRY_COLD;
        out->retry_after_s = deep ? 8u * HOUR_S : 6u * HOUR_S;
        return true;
    }
    case OTA_DENY_HOT:
        out->code = OTA_RETRY_HOT;
        out->retry_after_s = 4u * HOUR_S; /* до вечірнього спаду температури */
        return true;
    case OTA_DENY_LOW_SOC:
        out->code = OTA_RETRY_LOW_SOC;
        out->retry_after_s = 2u * HOUR_S; /* час на підзарядку від панелі */
        return true;
    case OTA_DENY_HIGH_ESR:
        /* Опір комірки сам не впаде: далі не пробуємо взагалі, а сервер
           заводить сервісну задачу на заміну батареї. */
        out->code = OTA_ALERT_HIGH_ESR;
        out->retry_after_s = 0u;
        out->service_required = true;
        return true;
    case OTA_DENY_POWER_FAULT:
        out->code = OTA_ALERT_POWER_FAULT;
        out->retry_after_s = 0u;
        out->service_required = true;
        return true;
    case OTA_DENY_SENSOR_FAIL:
        out->code = OTA_ALERT_SENSOR_FAIL;
        out->retry_after_s = 1u * HOUR_S;
        out->service_required = true;
        return true;
    default:
        return false; /* дозвіл — відмовної телеметрії немає */
    }
}

int ota_telemetry_encode(const ota_gate_report_t *report,
                         const ota_limits_t *lim,
                         uint8_t *buf,
                         size_t cap)
{
    ota_deny_summary_t summary;
    if (buf == NULL || !ota_telemetry_summarize(report, lim, &summary)) {
        return -1;
    }

    writer_t w = { .buf = buf, .cap = cap, .len = 0, .overflow = false };

    put_u8(&w, 'O');
    put_u8(&w, 'T');
    put_u8(&w, 'A');
    put_u8(&w, TELEMETRY_VERSION);
    put_u8(&w, (uint8_t)summary.code);
    put_u8(&w, summary.service_required ? FLAG_SERVICE : 0u);
    put_u32(&w, summary.retry_after_s);

    if (report->has_temp) {
        put_tlv_u16(&w, TAG_TEMP, (uint16_t)report->temp_c); /* доповняльний код */
    }
    if (report->has_soc) {
        put_tlv_u8(&w, TAG_SOC, report->soc_percent);
    }
    if (report->has_idle) {
        put_tlv_u16(&w, TAG_IDLE, report->v_idle_mv);
    }
    if (report->has_pulse) {
        put_tlv_u16(&w, TAG_LOAD, report->v_load_mv);
        put_tlv_u16(&w, TAG_ESR, report->esr_mohm);
        put_tlv_u16(&w, TAG_FORECAST, report->v_forecast_mv);
    }
    put_tlv_u8(&w, TAG_FAULTS, report->power_faults);

    return w.overflow ? -1 : (int)w.len;
}
