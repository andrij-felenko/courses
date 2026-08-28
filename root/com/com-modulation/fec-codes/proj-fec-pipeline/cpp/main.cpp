#include <iostream>
#include <vector>
#include <array>
#include <cstdint>
#include <iomanip>
#include <span>
#include <string_view>

class HammingCodec {
public:
    static constexpr size_t K = 4; // Кількість інформаційних бітів
    static constexpr size_t N = 7; // Повна довжина кодового слова

    [[nodiscard]] static constexpr uint8_t encode(uint8_t nibble) noexcept {
        uint8_t d0 = (nibble >> 0) & 1;
        uint8_t d1 = (nibble >> 1) & 1;
        uint8_t d2 = (nibble >> 2) & 1;
        uint8_t d3 = (nibble >> 3) & 1;

        uint8_t p0 = d0 ^ d1 ^ d2;
        uint8_t p1 = d1 ^ d2 ^ d3;
        uint8_t p2 = d0 ^ d1 ^ d3;

        return static_cast<uint8_t>(d0 | (d1 << 1) | (d2 << 2) | (d3 << 3) |
                                   (p0 << 4) | (p1 << 5) | (p2 << 6));
    }

    struct DecodeResult {
        uint8_t data;
        bool has_error;
        int error_bit_index;
    };

    [[nodiscard]] static constexpr DecodeResult decode(uint8_t codeword) noexcept {
        std::array<uint8_t, N> r{};
        for (size_t i = 0; i < N; ++i) {
            r[i] = (codeword >> i) & 1;
        }

        uint8_t s0 = r[4] ^ r[0] ^ r[1] ^ r[2];
        uint8_t s1 = r[5] ^ r[1] ^ r[2] ^ r[3];
        uint8_t s2 = r[6] ^ r[0] ^ r[1] ^ r[3];
        uint8_t syndrome = static_cast<uint8_t>(s0 | (s1 << 1) | (s2 << 2));

        if (syndrome == 0) {
            uint8_t out = static_cast<uint8_t>(r[0] | (r[1] << 1) | (r[2] << 2) | (r[3] << 3));
            return {out, false, -1};
        }

        int error_pos = -1;
        switch (syndrome) {
            case 0b101: error_pos = 0; break; // d0
            case 0b111: error_pos = 1; break; // d1
            case 0b011: error_pos = 2; break; // d2
            case 0b110: error_pos = 3; break; // d3
            case 0b001: error_pos = 4; break; // p0
            case 0b010: error_pos = 5; break; // p1
            case 0b100: error_pos = 6; break; // p2
            default:    error_pos = -1; break;
        }

        if (error_pos >= 0 && static_cast<size_t>(error_pos) < N) {
            r[error_pos] ^= 1; // Виправлення інверсією біта
        }

        uint8_t out = static_cast<uint8_t>(r[0] | (r[1] << 1) | (r[2] << 2) | (r[3] << 3));
        return {out, true, error_pos};
    }
};

template <size_t Rows, size_t Cols>
class MatrixInterleaver {
public:
    [[nodiscard]] static std::vector<uint8_t> interleave(std::span<const uint8_t, Rows> codewords) {
        std::vector<uint8_t> stream(Rows * Cols, 0);
        for (size_t col = 0; col < Cols; ++col) {
            for (size_t row = 0; row < Rows; ++row) {
                uint8_t bit = (codewords[row] >> col) & 1;
                stream[col * Rows + row] = bit;
            }
        }
        return stream;
    }

    [[nodiscard]] static std::array<uint8_t, Rows> deinterleave(std::span<const uint8_t> stream) {
        std::array<uint8_t, Rows> codewords{};
        for (size_t col = 0; col < Cols; ++col) {
            for (size_t row = 0; row < Rows; ++row) {
                uint8_t bit = stream[col * Rows + row];
                codewords[row] |= static_cast<uint8_t>(bit << col);
            }
        }
        return codewords;
    }
};

int main() {
    constexpr size_t NumRows = 4;
    constexpr size_t NumCols = HammingCodec::N;

    std::array<uint8_t, NumRows> original_data = {0b1010, 0b1100, 0b0111, 0b0001};
    std::array<uint8_t, NumRows> encoded_codewords{};

    std::cout << "=== 1. Кодування інформаційних блоків ===\n";
    for (size_t i = 0; i < NumRows; ++i) {
        encoded_codewords[i] = HammingCodec::encode(original_data[i]);
        std::cout << "Блок " << i << ": дані=0x" << std::hex << (int)original_data[i]
                  << " -> кодове слово=0x" << (int)encoded_codewords[i] << '\n';
    }

    // 2. Переміжнення
    auto channel_bits = MatrixInterleaver<NumRows, NumCols>::interleave(encoded_codewords);

    // 3. Симуляція каналу: неперервний імпульсний пакет із 3 помилок
    std::cout << "\n=== 2. Передача каналом: накладання пакету помилок ===\n";
    std::cout << "Пакет завади вражає канальні біти з індексами 5, 6, 7...\n";
    channel_bits[5] ^= 1;
    channel_bits[6] ^= 1;
    channel_bits[7] ^= 1;

    // 4. Депереміжнення
    auto received_codewords = MatrixInterleaver<NumRows, NumCols>::deinterleave(channel_bits);

    // 5. Декодування
    std::cout << "\n=== 3. Депереміжнення та відновлення повідомлення ===\n";
    bool success = true;
    for (size_t i = 0; i < NumRows; ++i) {
        auto res = HammingCodec::decode(received_codewords[i]);
        bool match = (res.data == original_data[i]);
        if (!match) success = false;

        std::cout << "Рядок " << i << ": вхід=0x" << (int)original_data[i]
                  << ", спотворене слово=0x" << (int)received_codewords[i]
                  << " -> відновлено=0x" << (int)res.data
                  << " (виправлено біт #" << res.error_bit_index
                  << ", статус: " << (match ? "УСПІХ" : "ЗБІЙ") << ")\n";
    }

    std::cout << "\nРезультат: "
              << (success ? "Усі блоки відновлено без втрат завдяки розсіюванню!" :
                            "Виникли невиправні помилки!")
              << '\n';

    return 0;
}
