#include <stdio.h>
#include <stdbool.h>
#include "driver/spi_master.h"

#define AS5048_REG_AGC_DIAG 0x3FFD
#define AS5048_FLAG_OCF      (1 << 8)
#define AS5048_FLAG_COF      (1 << 9)
#define AS5048_FLAG_COMPL    (1 << 10)
#define AS5048_FLAG_COMPH    (1 << 11)

typedef struct {
    uint8_t agc_value;
    bool offset_comp_ok;
    bool cordic_overflow;
    bool field_too_low;
    bool field_too_high;
    bool is_valid;
} as5048_diag_status_t;

as5048_diag_status_t as5048_decode_diagnostics(uint16_t rx_frame) {
    as5048_diag_status_t diag;
    
    diag.agc_value       = (uint8_t)(rx_frame & 0xFF);
    diag.offset_comp_ok  = (rx_frame & AS5048_FLAG_OCF) != 0;
    diag.cordic_overflow = (rx_frame & AS5048_FLAG_COF) != 0;
    diag.field_too_low   = (rx_frame & AS5048_FLAG_COMPL) != 0;
    diag.field_too_high  = (rx_frame & AS5048_FLAG_COMPH) != 0;
    
    diag.is_valid = diag.offset_comp_ok && !diag.cordic_overflow && 
                    !diag.field_too_low && !diag.field_too_high;
                    
    return diag;
}
