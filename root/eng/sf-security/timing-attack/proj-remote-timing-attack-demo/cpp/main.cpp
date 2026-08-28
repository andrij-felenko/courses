#include <iostream>
#include <vector>
#include <array>
#include <string_view>
#include <chrono>
#include <numeric>
#include <algorithm>
#include <span>
#include <x86intrin.h>

namespace timing_demo {

constexpr size_t TOKEN_LEN = 16;
constexpr size_t SAMPLES_PER_BYTE = 10000;

const std::array<uint8_t, TOKEN_LEN> SECRET_TOKEN = {
    0x53, 0x65, 0x63, 0x75, 0x72, 0x65, 0x50, 0x61,
    0x73, 0x73, 0x77, 0x6F, 0x72, 0x64, 0x34, 0x32
};

void work_delay() noexcept {
    volatile int dummy = 0;
    for (int i = 0; i < 50; ++i) {
        dummy += i;
    }
}

// Вразлива перевірка: ранній вихід
bool vulnerable_verify(std::span<const uint8_t> user_token) noexcept {
    if (user_token.size() != TOKEN_LEN) {
        return false;
    }
    for (size_t i = 0; i < TOKEN_LEN; ++i) {
        work_delay();
        if (user_token[i] != SECRET_TOKEN[i]) {
            return false; // Витік часу
        }
    }
    return true;
}

// Захищена перевірка: константний час
bool constant_time_verify(std::span<const uint8_t> user_token) noexcept {
    if (user_token.size() != TOKEN_LEN) {
        return false;
    }
    uint8_t diff = 0;
    for (size_t i = 0; i < TOKEN_LEN; ++i) {
        work_delay();
        diff |= (user_token[i] ^ SECRET_TOKEN[i]);
    }
    asm volatile("" : "+r"(diff) : : "memory");
    return (diff == 0);
}

// Вимірювання циклів через RDTSCP
template <typename VerifyFn>
uint64_t measure_cycles(std::span<const uint8_t> candidate, VerifyFn&& verify_fn) noexcept {
    unsigned int aux = 0;
    _mm_lfence();
    uint64_t start = __rdtscp(&aux);
    _mm_lfence();

    volatile bool res = verify_fn(candidate);
    (void)res;

    _mm_lfence();
    uint64_t end = __rdtscp(&aux);
    _mm_lfence();

    return end - start;
}

void execute_attack(std::string_view target_name, auto verify_fn) {
    std::array<uint8_t, TOKEN_LEN> recovered{};
    std::cout << "=== Запуск таймінг-атаки на: " << target_name << " ===\n";

    for (size_t pos = 0; pos < TOKEN_LEN; ++pos) {
        uint64_t max_avg_cycles = 0;
        uint8_t best_byte = 0;

        for (int candidate = 0; candidate < 256; ++candidate) {
            recovered[pos] = static_cast<uint8_t>(candidate);
            uint64_t total_cycles = 0;

            for (size_t s = 0; s < SAMPLES_PER_BYTE; ++s) {
                total_cycles += measure_cycles(recovered, verify_fn);
            }

            uint64_t avg = total_cycles / SAMPLES_PER_BYTE;
            if (avg > max_avg_cycles) {
                max_avg_cycles = avg;
                best_byte = static_cast<uint8_t>(candidate);
            }
        }

        recovered[pos] = best_byte;
        std::cout << "Позиція " << pos << ": знайдено байт 0x" << std::hex << static_cast<int>(best_byte)
                  << " ('" << static_cast<char>(best_byte) << "')"
                  << " [сер. час: " << std::dec << max_avg_cycles << " тактів]\n";
    }

    std::cout << "Відновлений токен: \"";
    for (uint8_t b : recovered) {
        std::cout << static_cast<char>(b);
    }
    std::cout << "\"\n\n";
}

} // namespace timing_demo

int main() {
    timing_demo::execute_attack("Вразливий алгоритм (Early-Exit)", timing_demo::vulnerable_verify);
    return 0;
}
