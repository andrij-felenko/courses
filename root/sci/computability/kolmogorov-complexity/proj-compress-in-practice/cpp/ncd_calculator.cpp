// ncd_calculator.cpp — Обчислення NCD мовою C++ (C++20, RAII, std::span)
#include <iostream>
#include <vector>
#include <string_view>
#include <span>
#include <algorithm>
#include <cstdint>
#include <stdexcept>

class NcdCalculator {
public:
    // Оцінка стисненого розміру на основі RLE/словникового аналізу
    static size_t compressed_size(std::span<const uint8_t> data) noexcept {
        if (data.empty()) return 0;
        size_t compressed_len = 0;
        size_t i = 0;
        
        while (i < data.size()) {
            uint8_t run_byte = data[i];
            size_t run_len = 1;
            while (i + run_len < data.size() && data[i + run_len] == run_byte && run_len < 255) {
                run_len++;
            }
            compressed_len += 2;
            i += run_len;
        }
        return compressed_len;
    }

    // Обчислення NCD між двома послідовностями байтів
    static double distance(std::span<const uint8_t> x, std::span<const uint8_t> y) {
        const size_t cx = compressed_size(x);
        const size_t cy = compressed_size(y);

        // RAII-буфер для конкатенації xy
        std::vector<uint8_t> xy;
        xy.reserve(x.size() + y.size());
        xy.insert(xy.end(), x.begin(), x.end());
        xy.insert(xy.end(), y.begin(), y.end());

        const size_t cxy = compressed_size(xy);

        const double min_c = static_cast<double>(std::min(cx, cy));
        const double max_c = static_cast<double>(std::max(cx, cy));

        if (max_c == 0.0) return 0.0;

        const double ncd = (static_cast<double>(cxy) - min_c) / max_c;
        return std::clamp(ncd, 0.0, 1.0);
    }
};

int main() {
    std::string_view text1 = "AAAAABBBBBCCCCCDDDDDAAAAABBBBBCCCCCDDDDD";
    std::string_view text2 = "AAAAABBBBBCCCCCDDDDDAAAAABBBBBCCCCCDDDDE";
    std::string_view text3 = "XYZ1234567890QWERTYSDFGHJKLZXCVBNMUIOP12";

    auto span1 = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(text1.data()), text1.size());
    auto span2 = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(text2.data()), text2.size());
    auto span3 = std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(text3.data()), text3.size());

    double ncd_12 = NcdCalculator::distance(span1, span2);
    double ncd_13 = NcdCalculator::distance(span1, span3);

    std::cout << "NCD(text1, text2) = " << ncd_12 << " (близькі тексти)\n";
    std::cout << "NCD(text1, text3) = " << ncd_13 << " (різні тексти)\n";

    return 0;
}
