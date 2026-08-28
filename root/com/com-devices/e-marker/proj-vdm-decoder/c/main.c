#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define USBPD_SVID_STANDARD          0xFF00U
#define VDM_TYPE_STRUCTURED          1U
#define VDM_CMD_DISCOVER_IDENTITY    0x01U
#define VDM_CMD_TYPE_ACK             0x01U

#define PROD_TYPE_PASSIVE_CABLE      0x03U
#define PROD_TYPE_ACTIVE_CABLE       0x04U

typedef enum {
    VDM_PARSE_OK = 0,
    VDM_ERR_BUFFER_TOO_SHORT,
    VDM_ERR_INVALID_SVID,
    VDM_ERR_NOT_STRUCTURED,
    VDM_ERR_WRONG_COMMAND,
    VDM_ERR_NOT_ACK,
    VDM_ERR_NOT_A_CABLE,
    VDM_ERR_INVALID_CURRENT_FIELD
} vdm_parse_result_t;

typedef enum {
    CABLE_SPEED_USB2_ONLY = 0,
    CABLE_SPEED_USB32_GEN1,
    CABLE_SPEED_USB32_GEN2_OR_USB4_GEN2,
    CABLE_SPEED_USB4_GEN3,
    CABLE_SPEED_USB4_GEN4,
    CABLE_SPEED_UNKNOWN
} cable_speed_t;

typedef struct {
    uint16_t vid;
    uint16_t pid;
    uint32_t xid;
    uint8_t  hw_version;
    uint8_t  fw_version;
    bool     is_active_cable;
    bool     is_epr_capable;
    uint16_t max_voltage_mv;
    uint16_t max_current_ma;
    cable_speed_t max_speed;
    uint8_t  max_temperature_c;
    bool     has_thermal_sensor;
} cable_descriptor_t;

vdm_parse_result_t vdm_decode_cable_identity(
    const uint32_t *vdo_buffer,
    size_t word_count,
    cable_descriptor_t *out_desc
) {
    if (vdo_buffer == NULL || out_desc == NULL || word_count < 5) {
        return VDM_ERR_BUFFER_TOO_SHORT;
    }

    uint32_t vdm_header = vdo_buffer[0];
    uint16_t svid = (uint16_t)(vdm_header >> 16);
    uint8_t vdm_type = (uint8_t)((vdm_header >> 15) & 0x01U);
    uint8_t cmd_type = (uint8_t)((vdm_header >> 6) & 0x03U);
    uint8_t cmd_code = (uint8_t)(vdm_header & 0x1FU);

    if (svid != USBPD_SVID_STANDARD) {
        return VDM_ERR_INVALID_SVID;
    }
    if (vdm_type != VDM_TYPE_STRUCTURED) {
        return VDM_ERR_NOT_STRUCTURED;
    }
    if (cmd_code != VDM_CMD_DISCOVER_IDENTITY) {
        return VDM_ERR_WRONG_COMMAND;
    }
    if (cmd_type != VDM_CMD_TYPE_ACK) {
        return VDM_ERR_NOT_ACK;
    }

    uint32_t id_header = vdo_buffer[1];
    uint8_t prod_type = (uint8_t)((id_header >> 27) & 0x07U);
    if (prod_type != PROD_TYPE_PASSIVE_CABLE && prod_type != PROD_TYPE_ACTIVE_CABLE) {
        return VDM_ERR_NOT_A_CABLE;
    }

    out_desc->vid = (uint16_t)(id_header & 0xFFFFU);
    out_desc->is_active_cable = (prod_type == PROD_TYPE_ACTIVE_CABLE);
    out_desc->xid = vdo_buffer[2];

    uint32_t prod_vdo = vdo_buffer[3];
    out_desc->pid = (uint16_t)(prod_vdo >> 16);

    uint32_t cable_vdo1 = vdo_buffer[4];
    out_desc->hw_version = (uint8_t)((cable_vdo1 >> 28) & 0x0FU);
    out_desc->fw_version = (uint8_t)((cable_vdo1 >> 24) & 0x0FU);

    uint8_t volt_bits = (uint8_t)((cable_vdo1 >> 17) & 0x03U);
    switch (volt_bits) {
        case 0x00: out_desc->max_voltage_mv = 20000; break;
        case 0x01: out_desc->max_voltage_mv = 30000; break;
        case 0x02: out_desc->max_voltage_mv = 40000; break;
        case 0x03: out_desc->max_voltage_mv = 50000; break;
    }

    uint8_t curr_bits = (uint8_t)((cable_vdo1 >> 5) & 0x03U);
    if (curr_bits == 0x01) {
        out_desc->max_current_ma = 3000;
    } else if (curr_bits == 0x02) {
        out_desc->max_current_ma = 5000;
    } else {
        return VDM_ERR_INVALID_CURRENT_FIELD;
    }

    uint8_t speed_bits = (uint8_t)(cable_vdo1 & 0x07U);
    switch (speed_bits) {
        case 0x00: out_desc->max_speed = CABLE_SPEED_USB2_ONLY; break;
        case 0x01: out_desc->max_speed = CABLE_SPEED_USB32_GEN1; break;
        case 0x02: out_desc->max_speed = CABLE_SPEED_USB32_GEN2_OR_USB4_GEN2; break;
        case 0x03: out_desc->max_speed = CABLE_SPEED_USB4_GEN3; break;
        case 0x04: out_desc->max_speed = CABLE_SPEED_USB4_GEN4; break;
        default:   out_desc->max_speed = CABLE_SPEED_UNKNOWN; break;
    }

    out_desc->is_epr_capable = (out_desc->max_voltage_mv >= 50000 && out_desc->max_current_ma == 5000);
    out_desc->max_temperature_c = 0;
    out_desc->has_thermal_sensor = false;

    if (word_count >= 6) {
        uint32_t cable_vdo2 = vdo_buffer[5];
        out_desc->max_temperature_c = (uint8_t)((cable_vdo2 >> 24) & 0xFFU);
        uint8_t thermal_sensor = (uint8_t)((cable_vdo2 >> 12) & 0x0FU);
        out_desc->has_thermal_sensor = (thermal_sensor != 0);

        uint8_t epr_flag = (uint8_t)((cable_vdo2 >> 8) & 0x0FU);
        if (epr_flag == 0x01) {
            out_desc->is_epr_capable = true;
            out_desc->max_voltage_mv = 50000;
        }
    }

    return VDM_PARSE_OK;
}
