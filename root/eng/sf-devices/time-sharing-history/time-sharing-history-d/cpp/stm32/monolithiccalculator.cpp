#include "stm32f4xx_hal.h"
#include <array>
#include <cstdint>

class MonolithicCalculator {
public:
    static constexpr size_t kBufferSize = 1024;

    uint32_t ComputeCrc(const std::array<uint8_t, kBufferSize>& data) {
        uint32_t crc = 0xFFFFFFFF;
        for (uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 1) {
                    crc = (crc >> 1) ^ 0xEDB88320;
                } else {
                    crc >>= 1;
                }
                // Затримка імітує складний математичний алгоритм
                for (volatile int delay = 0; delay < 100; ++delay) {}
            }
        }
        return ~crc;
    }
};

extern UART_HandleTypeDef huart2;

int main() {
    HAL_Init();
    MonolithicCalculator calculator;
    std::array<uint8_t, MonolithicCalculator::kBufferSize> dummy_data{};

    while (true) {
        // Виконання монолітної задачі блокує цикл на тривалий час
        uint32_t crc_result = calculator.ComputeCrc(dummy_data);
        (void)crc_result;

        // Перевірка прапорця прийому UART після завершення монолітного блоку
        // Якщо за цей час прийшло кілька байтів, виникне помилка ORE (Overrun Error)
        if (__HAL_UART_GET_FLAG(&huart2, UART_FLAG_ORE)) {
            __HAL_UART_CLEAR_OREFLAG(&huart2); // Скидання прапорця помилки переповнення
        }
    }
}
