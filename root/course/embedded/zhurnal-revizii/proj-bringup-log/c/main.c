#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define STM32_UID_BASE          0x1FFF7A10U
#define STM32_VREFINT_CAL_ADDR  0x1FFF7A2AU
#define STM32_TS_CAL1_ADDR      0x1FFF7A2CU
#define STM32_TS_CAL2_ADDR      0x1FFF7A2EU

#define VREFINT_CAL_VREF_MV     3300U
#define TS_CAL1_TEMP_C          30
#define TS_CAL2_TEMP_C          110

typedef struct {
    uint32_t uid[3];
    uint16_t vrefint_cal;
    uint16_t ts_cal1;
    uint16_t ts_cal2;
    uint16_t adc_vref_raw;
    uint16_t adc_temp_raw;
    uint32_t calculated_vdda_mv;
    int32_t  calculated_core_temp_c;
} board_telemetry_t;

void board_telemetry_read_hardware_ids(board_telemetry_t *telem) {
    const uint32_t *uid_ptr = (const uint32_t *)STM32_UID_BASE;
    telem->uid[0] = uid_ptr[0];
    telem->uid[1] = uid_ptr[1];
    telem->uid[2] = uid_ptr[2];

    telem->vrefint_cal = *(const uint16_t *)STM32_VREFINT_CAL_ADDR;
    telem->ts_cal1     = *(const uint16_t *)STM32_TS_CAL1_ADDR;
    telem->ts_cal2     = *(const uint16_t *)STM32_TS_CAL2_ADDR;
}

void board_telemetry_calculate_analog(board_telemetry_t *telem, uint16_t raw_vref, uint16_t raw_temp) {
    telem->adc_vref_raw = raw_vref;
    telem->adc_temp_raw = raw_temp;

    if (raw_vref > 0) {
        telem->calculated_vdda_mv = (VREFINT_CAL_VREF_MV * (uint32_t)telem->vrefint_cal) / (uint32_t)raw_vref;
    } else {
        telem->calculated_vdda_mv = 0;
    }

    if (telem->ts_cal2 > telem->ts_cal1) {
        int32_t temp_num = ((int32_t)raw_temp * (int32_t)telem->calculated_vdda_mv / (int32_t)VREFINT_CAL_VREF_MV) - (int32_t)telem->ts_cal1;
        int32_t temp_den = (int32_t)telem->ts_cal2 - (int32_t)telem->ts_cal1;
        telem->calculated_core_temp_c = TS_CAL1_TEMP_C + (temp_num * (TS_CAL2_TEMP_C - TS_CAL1_TEMP_C)) / temp_den;
    } else {
        telem->calculated_core_temp_c = 0;
    }
}

static void uint32_to_hex_str(uint32_t val, char *out) {
    const char hex_digits[] = "0123456789ABCDEF";
    for (int i = 7; i >= 0; --i) {
        out[i] = hex_digits[val & 0x0F];
        val >>= 4;
    }
    out[8] = '\0';
}

void board_telemetry_format_json(const board_telemetry_t *telem, const char *serial_id, char *buf, size_t max_len) {
    char u0[9], u1[9], u2[9];
    uint32_to_hex_str(telem->uid[0], u0);
    uint32_to_hex_str(telem->uid[1], u1);
    uint32_to_hex_str(telem->uid[2], u2);

    /* Форматування спрощеним копіюванням без залучення важкого sprintf */
    const char *header = "{\"board_serial\":\"";
    size_t pos = 0;
    
    #define APPEND_STR(s) do { \
        size_t len = strlen(s); \
        if (pos + len < max_len) { memcpy(&buf[pos], (s), len); pos += len; } \
    } while(0)

    APPEND_STR(header);
    APPEND_STR(serial_id);
    APPEND_STR("\",\"uid\":\"");
    APPEND_STR(u0);
    APPEND_STR("-");
    APPEND_STR(u1);
    APPEND_STR("-");
    APPEND_STR(u2);
    APPEND_STR("\",\"vdda_mv\":");
    
    /* Друк цілого числа VDDA */
    char num_buf[16];
    uint32_t v = telem->calculated_vdda_mv;
    int idx = 0;
    if (v == 0) { num_buf[idx++] = '0'; }
    else {
        char rev[16];
        int r_idx = 0;
        while (v > 0) { rev[r_idx++] = (char)('0' + (v % 10)); v /= 10; }
        while (r_idx > 0) { num_buf[idx++] = rev[--r_idx]; }
    }
    num_buf[idx] = '\0';
    APPEND_STR(num_buf);

    APPEND_STR(",\"temp_c\":");
    int32_t t = telem->calculated_core_temp_c;
    idx = 0;
    if (t < 0) { num_buf[idx++] = '-'; t = -t; }
    if (t == 0) { num_buf[idx++] = '0'; }
    else {
        char rev[16];
        int r_idx = 0;
        while (t > 0) { rev[r_idx++] = (char)('0' + (t % 10)); t /= 10; }
        while (r_idx > 0) { num_buf[idx++] = rev[--r_idx]; }
    }
    num_buf[idx] = '\0';
    APPEND_STR(num_buf);
    APPEND_STR("}\r\n");

    if (pos < max_len) {
        buf[pos] = '\0';
    } else if (max_len > 0) {
        buf[max_len - 1] = '\0';
    }
    #undef APPEND_STR
}
