#include <stdint.h>
#include <stdbool.h>

/* Векторна оцінка предиката (col > 100) над пакетом із n значень */
void filter_vector_3vl(const int32_t* data, const uint8_t* null_mask, 
                        uint8_t* out_result_mask, uint8_t* out_null_mask, int n) {
    for (int i = 0; i < n; ++i) {
        if (null_mask[i]) {
            out_null_mask[i] = 1;   /* UNKNOWN */
            out_result_mask[i] = 0;
        } else {
            out_null_mask[i] = 0;   /* Визначено */
            out_result_mask[i] = (data[i] > 100) ? 1 : 0;
        }
    }
}
