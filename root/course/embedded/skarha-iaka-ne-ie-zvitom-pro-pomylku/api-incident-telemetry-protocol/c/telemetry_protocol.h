/* telemetry_protocol.h */
#pragma once
#include <stdint.h>

#define TELEMETRY_MAGIC 0xDEADBEEFUL
#define PROTOCOL_V1_0   0x0100U

typedef enum {
    FAULT_NONE              = 0x00000000UL,
    FAULT_HARDFAULT_PRECISE = 0x01010001UL,
    FAULT_HARDFAULT_IMPREC  = 0x01010002UL,
    FAULT_MEMMANAGE         = 0x01020001UL,
    FAULT_USAGE_DIV0        = 0x01030001UL,
    FAULT_WDT_TASK_STALL    = 0x02010001UL,
    FAULT_WDT_ISR_FLOOD     = 0x02010002UL,
    FAULT_PWR_BROWNOUT      = 0x03010001UL,
    FAULT_PWR_OVERTEMP      = 0x03020001UL,
    FAULT_BUS_I2C_STUCK     = 0x04010001UL,
    FAULT_BUS_SPI_LOCK      = 0x04020001UL
} fault_category_t;

typedef struct __attribute__((packed)) {
    uint32_t magic_tag;
    uint16_t protocol_version;
    uint16_t payload_length;
    uint64_t device_uid;
    uint32_t boot_count;
    uint32_t uptime_seconds;
    uint32_t reset_flags_raw;
    uint32_t fault_code;
    uint32_t fault_pc;
    uint32_t fault_lr;
    uint32_t fault_cfsr;
    int16_t  v_bat_mv;
    int16_t  v_core_mv;
    int16_t  temp_die_c;
    int16_t  temp_pcb_c;
    uint16_t bus_err_i2c;
    uint16_t bus_err_spi;
    uint32_t task_active_id;
    uint32_t task_min_stack_words;
    uint32_t crc32;
} telemetry_incident_frame_t;
