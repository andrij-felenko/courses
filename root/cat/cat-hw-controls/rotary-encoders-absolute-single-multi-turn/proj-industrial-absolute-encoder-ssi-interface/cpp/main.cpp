#include "SsiEncoder.hpp"
#include <iostream>

int main() {
    using namespace hw_controls;

    SsiConfig config{
        .singleturn_bits = 13,
        .multiturn_bits = 12,
        .use_gray_code = true,
        .check_parity = true
    };

    SsiEncoder encoder(config);

    std::cout << "=== Драйвер C++ для декодування абсолютного SSI енкодера ===\n";

    uint32_t test_mt_gray = SsiEncoder::grayToBinary(10);
    uint32_t test_st_gray = SsiEncoder::grayToBinary(4096);

    uint32_t frame = (test_mt_gray << 14) | (test_st_gray << 1) | 0x01;
    bool parity = SsiEncoder::checkParity(frame);
    frame = (frame << 1) | (parity ? 1 : 0);

    auto result = encoder.decodeFrame(frame);

    if (result.has_value()) {
        std::cout << "Декодування успішне!\n";
        std::cout << "- Кут ротора: " << result->angle_deg << " град.\n";
        std::cout << "- Оберти: " << result->turns << "\n";
    } else {
        std::cout << "Помилка декодування пакета!\n";
    }

    return 0;
}
