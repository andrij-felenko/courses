#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

typedef struct {
    int16_t rsrp_dbm;
    float rsrq_db;
    uint32_t cell_id;
    bool valid;
} radio_cell_info_t;

bool parse_cesq_response(const char *response, radio_cell_info_t *info) {
    if (!response || !info) return false;
    const char *tag = "+CESQ: ";
    const char *pos = strstr(response, tag);
    if (!pos) return false;

    int rxlev, ber, rscp, ecno, rsrq_raw, rsrp_raw;
    if (sscanf(pos + strlen(tag), "%d,%d,%d,%d,%d,%d",
               &rxlev, &ber, &rscp, &ecno, &rsrq_raw, &rsrp_raw) == 6) {
        if (rsrp_raw >= 0 && rsrp_raw <= 97) {
            info->rsrp_dbm = (int16_t)(-140 + rsrp_raw);
            info->valid = true;
        }
        if (rsrq_raw >= 0 && rsrq_raw <= 34) {
            info->rsrq_db = -19.5f + (float)rsrq_raw * 0.5f;
        }
        return true;
    }
    return false;
}
