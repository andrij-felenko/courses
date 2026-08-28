#include <stdint.h>
#include <stdbool.h>

/* Тип фізичного середовища кабелю */
typedef enum {
    CABLE_MEDIUM_COPPER_ACTIVE    = 0,
    CABLE_MEDIUM_OPTICAL_AOC       = 1,
    CABLE_MEDIUM_OPTICAL_ISOLATED  = 2
} cable_medium_t;

/* Структура розібраних параметрів активного кабелю */
typedef struct {
    uint16_t vbus_max_current_ma;
    uint16_t vconn_req_power_mw;
    uint8_t  latency_ns_code;
    uint8_t  usb4_max_speed_gbps;
    cable_medium_t medium;
    uint8_t  retimer_count;
    bool     sop_double_prime_present;
    bool     is_valid;
} active_cable_info_t;

/* Декодування слів Active Cable VDO 1 та VDO 2 */
bool pd_decode_active_cable_vdos(uint32_t vdo1, uint32_t vdo2, active_cable_info_t *out) {
    if (!out) {
        return false;
    }

    /* Розбір VDO 1: Струм VBUS (біти 21..20) */
    uint8_t cur_code = (vdo1 >> 20) & 0x03;
    if (cur_code == 0x01) {
        out->vbus_max_current_ma = 3000;
    } else if (cur_code == 0x02) {
        out->vbus_max_current_ma = 5000;
    } else {
        out->vbus_max_current_ma = 0; /* Некоректне значення */
    }

    out->sop_double_prime_present = (vdo1 & (1 << 17)) != 0;

    /* Розбір потужності VCONN (біти 15..13) */
    uint8_t vconn_code = (vdo1 >> 13) & 0x07;
    switch (vconn_code) {
        case 0: out->vconn_req_power_mw = 1000; break;
        case 1: out->vconn_req_power_mw = 1500; break;
        case 2: out->vconn_req_power_mw = 2000; break;
        case 3: out->vconn_req_power_mw = 3000; break;
        default: out->vconn_req_power_mw = 1000; break;
    }

    out->latency_ns_code = (vdo1 >> 10) & 0x07;

    /* Розбір VDO 2: Швидкість USB4 (біти 31..24) */
    uint8_t speed_code = (vdo2 >> 24) & 0xFF;
    switch (speed_code) {
        case 0x01: out->usb4_max_speed_gbps = 20; break;
        case 0x02: out->usb4_max_speed_gbps = 40; break;
        case 0x03: out->usb4_max_speed_gbps = 80; break;
        default:   out->usb4_max_speed_gbps = 10; break;
    }

    /* Фізичне середовище (біти 23..21) */
    uint8_t med_code = (vdo2 >> 21) & 0x07;
    out->medium = (med_code <= 2) ? (cable_medium_t)med_code : CABLE_MEDIUM_COPPER_ACTIVE;

    /* Кількість ретаймерів (біти 20..19) */
    uint8_t retimer_code = (vdo2 >> 19) & 0x03;
    out->retimer_count = (retimer_code <= 2) ? retimer_code : 0;

    out->is_valid = (out->vbus_max_current_ma > 0);
    return out->is_valid;
}
