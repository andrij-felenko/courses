#include <stdint.h>
#include <stdbool.h>

typedef enum {
    HW_REV_UNKNOWN = 0,
    HW_REV_A       = 1,
    HW_REV_B       = 2,
    HW_REV_C       = 3
} hw_revision_t;

typedef struct {
    hw_revision_t rev;
    uint16_t min_raw;
    uint16_t max_raw;
} hw_rev_window_t;

/* Допускові вікна для 12-бітного АЦП (Vref = 3.3V) */
static const hw_rev_window_t REV_WINDOWS[] = {
    { HW_REV_A,    0,  300 },   /* 0.00 В ± 0.24 В (GND) */
    { HW_REV_B,  850, 1200 },   /* 0.825 В ± 0.15 В      */
    { HW_REV_C, 1850, 2250 }    /* 1.650 В ± 0.15 В      */
};

#define REV_WINDOWS_COUNT (sizeof(REV_WINDOWS) / sizeof(REV_WINDOWS[0]))

hw_revision_t bsp_detect_hardware_revision(uint16_t adc_sample) {
    for (size_t i = 0; i < REV_WINDOWS_COUNT; ++i) {
        if (adc_sample >= REV_WINDOWS[i].min_raw && 
            adc_sample <= REV_WINDOWS[i].max_raw) {
            return REV_WINDOWS[i].rev;
        }
    }
    return HW_REV_UNKNOWN;
}
