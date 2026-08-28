// main.cpp — Приклад використання C++20 API бібліотеки libldpc
#include <iostream>
#include <vector>
#include "ldpc_codec.hpp"

int main() {
    ldpc::Config cfg{
        .num_v = 6,
        .num_c = 3,
        .h_matrix = {
            1, 1, 1, 0, 0, 0,
            0, 1, 0, 1, 1, 0,
            0, 0, 1, 0, 1, 1
        },
        .algo = ldpc::Algorithm::NormalizedMinSum,
        .max_iterations = 30,
        .norm_factor = 0.85f
    };

    auto codec_result = ldpc::Codec::create(cfg);
    if (!codec_result.has_value()) {
        std::cerr << "Помилка створення кодека: " << ldpc::to_string(codec_result.error()) << '\n';
        return EXIT_FAILURE;
    }

    const auto& codec = codec_result.value();

    const std::vector<std::uint8_t> info_bits = {1, 0, 1};
    auto encode_res = codec.encode(info_bits);
    if (!encode_res) {
        std::cerr << "Помилка кодування\n";
        return EXIT_FAILURE;
    }

    // Симуляція зашумлених LLR від радіоприймача
    const std::vector<float> rx_llr = {-4.5f, +3.2f, -5.0f, +4.1f, +3.8f, -4.9f};

    auto decode_res = codec.decode(rx_llr);
    if (decode_res.has_value()) {
        const auto& result = decode_res.value();
        std::cout << "Успішно декодовано за " << result.iterations_used << " ітерацій!\n";
        std::cout << "Відновлені біти: ";
        for (auto b : result.bits) {
            std::cout << static_cast<int>(b) << ' ';
        }
        std::cout << '\n';
    } else {
        std::cout << "Декодування не збіглося: " << ldpc::to_string(decode_res.error()) << '\n';
    }

    return EXIT_SUCCESS;
}
