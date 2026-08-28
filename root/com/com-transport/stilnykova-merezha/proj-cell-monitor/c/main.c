#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>

typedef enum {
    REG_NOT_REGISTERED = 0,
    REG_HOME           = 1,
    REG_SEARCHING      = 2,
    REG_DENIED         = 3,
    REG_UNKNOWN        = 4,
    REG_ROAMING        = 5
} cell_reg_status_t;

typedef enum {
    ACT_GSM    = 0,
    ACT_UTRAN  = 2,
    ACT_LTE    = 7,
    ACT_NR_5G  = 12
} cell_act_t;

typedef struct {
    bool valid;
    int16_t rsrp_dbm;     /* -140 .. -44 dBm, 0x7FFF = unknown */
    float   rsrq_db;      /* -19.5 .. -3.0 dB, NAN = unknown */
    uint32_t cell_id;     /* E-UTRAN Cell Identifier (28 bit) */
    uint16_t tac;         /* Tracking Area Code */
    cell_reg_status_t reg;
    cell_act_t act;
    char oper_name[32];
} cell_metrics_t;

typedef struct {
    cell_metrics_t current;
    uint32_t last_cell_id;
    bool handover_occurred;
} cell_monitor_t;

void cell_monitor_init(cell_monitor_t *mon) {
    if (!mon) return;
    memset(mon, 0, sizeof(*mon));
    mon->current.rsrp_dbm = -140;
    mon->current.rsrq_db = -20.0f;
    mon->current.reg = REG_NOT_REGISTERED;
}

bool cell_parse_cesq(const char *line, cell_metrics_t *out) {
    if (!line || !out) return false;
    const char *prefix = "+CESQ: ";
    const char *p = strstr(line, prefix);
    if (!p) return false;
    p += strlen(prefix);

    int rxlev, ber, rscp, ecno, rsrq_raw, rsrp_raw;
    if (sscanf(p, "%d,%d,%d,%d,%d,%d", 
               &rxlev, &ber, &rscp, &ecno, &rsrq_raw, &rsrp_raw) != 6) {
        return false;
    }

    if (rsrp_raw >= 0 && rsrp_raw <= 97) {
        out->rsrp_dbm = (int16_t)(-140 + rsrp_raw);
        out->valid = true;
    } else {
        out->rsrp_dbm = -140;
    }

    if (rsrq_raw >= 0 && rsrq_raw <= 34) {
        out->rsrq_db = -19.5f + (float)rsrq_raw * 0.5f;
    } else {
        out->rsrq_db = -20.0f;
    }

    return true;
}

bool cell_parse_cereg(const char *line, cell_metrics_t *out, cell_monitor_t *mon) {
    if (!line || !out) return false;
    const char *prefix = "+CEREG: ";
    const char *p = strstr(line, prefix);
    if (!p) return false;
    p += strlen(prefix);

    int n = 0, stat = 0, act = 7;
    char tac_str[16] = {0};
    char ci_str[16] = {0};

    int matched = sscanf(p, "%d,%d,\"%15[^\"]\",\"%15[^\"]\",%d", 
                         &n, &stat, tac_str, ci_str, &act);
    if (matched < 2) {
        matched = sscanf(p, "%d,\"%15[^\"]\",\"%15[^\"]\",%d", 
                         &stat, tac_str, ci_str, &act);
    }

    if (matched >= 1) {
        out->reg = (cell_reg_status_t)stat;
    }

    if (matched >= 3 && strlen(ci_str) > 0) {
        uint32_t new_ci = (uint32_t)strtoul(ci_str, NULL, 16);
        out->tac = (uint16_t)strtoul(tac_str, NULL, 16);
        out->act = (cell_act_t)act;

        if (mon && mon->last_cell_id != 0 && mon->last_cell_id != new_ci) {
            mon->handover_occurred = true;
        }
        out->cell_id = new_ci;
        if (mon) {
            mon->last_cell_id = new_ci;
        }
    }

    return true;
}

void cell_monitor_process_line(cell_monitor_t *mon, const char *line) {
    if (!mon || !line) return;

    if (cell_parse_cesq(line, &mon->current)) {
        printf("[METRICS] RSRP: %d dBm, RSRQ: %.1f dB\n", 
               mon->current.rsrp_dbm, mon->current.rsrq_db);
    } else if (cell_parse_cereg(line, &mon->current, mon)) {
        printf("[REG] Status: %d, TAC: 0x%04X, Cell ID: 0x%07X\n", 
               mon->current.reg, mon->current.tac, mon->current.cell_id);
        if (mon->handover_occurred) {
            printf("[EVENT] Handover detected! New Cell ID: 0x%07X\n", 
                   mon->current.cell_id);
            mon->handover_occurred = false;
        }
    }
}
