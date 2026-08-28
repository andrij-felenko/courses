#define LO_CODE  1200u            // нижня межа вікна (код АЦП)
#define HI_CODE  2800u            // верхня межа

static inline int in_window(uint16_t s) {
    return (s >= LO_CODE) && (s <= HI_CODE);   // два порівняння + AND
}

uint16_t s = adc_read();
if (!in_window(s))                // відлік вийшов за межі
    flag_out_of_range();
