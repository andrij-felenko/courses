#include <iostream>
#include <vector>
#include "esp_attr.h"
#include "esp_dsp.h"

class VectorEngine {
public:
    static int32_t dotProduct(const std::vector<int16_t>& a, const std::vector<int16_t>& b) {
        if (a.size() != b.size() || a.empty()) return 0;
        
        int32_t accum = 0;
        size_t count = a.size();
        size_t blocks = count / 8;

        for (size_t i = 0; i < blocks; i++) {
            // Векторний виклики через оптимізоване API DSP
            accum += dsps_dotprod_s16_ansi(&a[i * 8], &b[i * 8], 8, 0);
        }
        return accum;
    }
};
