#include <stdint.h>
#include <stdbool.h>

/* Константи команд та типів кабелю USB PD */
#define SOP_PRIME                   1
#define CMD_DISCOVER_IDENT          1
#define VDO_INDEX_CABLE_TYPE_2      4

#define CABLE_TYPE_PASSIVE          0
#define CABLE_TYPE_ACTIVE_RETIMER   1
#define CABLE_TYPE_ACTIVE_OPTICAL   2

typedef struct {
    uint8_t  cable_type;
    uint8_t  speed_gbps;
    uint16_t vconn_power_mw;
    uint8_t  latency_ns;
    bool     is_active;
} cable_capabilities_t;

/* Функції драйвера фізичного рівня PD (прототипи) */
extern bool pd_send_vdm_request(uint8_t sop_target, uint8_t cmd, uint32_t *vdo_buf, uint8_t *vdo_count);
extern void pd_set_vconn_power_limit(uint16_t milliwatts);
extern void phy_configure_usb4_retimers(uint8_t retimer_count, uint8_t latency_ns);

/* Обробник розпізнавання та ініціалізації активного кабелю */
bool identify_and_init_cable(cable_capabilities_t *caps) {
    if (!caps) return false;

    uint32_t vdo_response[7] = {0};
    uint8_t vdo_count = 0;

    /* Крок 1: Надсилання запиту Discover Identity до штекера кабелю (SOP') */
    if (!pd_send_vdm_request(SOP_PRIME, CMD_DISCOVER_IDENT, vdo_response, &vdo_count)) {
        /* Кабель не відповів на SOP' -> це звичайний пасивний кабель без E-Marker */
        caps->is_active = false;
        caps->cable_type = CABLE_TYPE_PASSIVE;
        caps->speed_gbps = 5; /* Безпечний дефолт */
        return true;
    }

    /* Крок 2: Перевірка ID Header VDO (vdo_response[0]) */
    uint32_t id_header = vdo_response[0];
    uint8_t product_type = (id_header >> 27) & 0x07;

    if (product_type == 3) {
        /* Product Type = 3 означає Active Cable */
        caps->is_active = true;

        /* Розбір Active Cable VDO 2 (зазвичай у позиції 4 для PD 3.1) */
        if (vdo_count > VDO_INDEX_CABLE_TYPE_2) {
            uint32_t cable_vdo2 = vdo_response[VDO_INDEX_CABLE_TYPE_2];
            uint8_t medium = (cable_vdo2 >> 21) & 0x07;
            uint8_t speed = (cable_vdo2 >> 24) & 0xFF;

            if (medium == 1 || medium == 2) {
                caps->cable_type = CABLE_TYPE_ACTIVE_OPTICAL;
            } else {
                caps->cable_type = CABLE_TYPE_ACTIVE_RETIMER;
            }

            caps->speed_gbps = (speed == 2) ? 40 : ((speed == 3) ? 80 : 20);
            caps->vconn_power_mw = 1500; /* Стандартний запит для активного ретаймера */
            caps->latency_ns = 35;       /* Середнє значення затримки */

            /* Крок 3: Виділення необхідної потужності VCONN */
            pd_set_vconn_power_limit(caps->vconn_power_mw);

            /* Крок 4: Повідомлення PHY-контролера про наявність ретаймерів у тракті */
            phy_configure_usb4_retimers(2, caps->latency_ns);
            return true;
        }
    }

    caps->is_active = false;
    caps->cable_type = CABLE_TYPE_PASSIVE;
    return true;
}
