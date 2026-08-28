#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <algorithm>
#include <bit>

namespace crypto {

class ChaCha20 final {
public:
    static constexpr size_t KeySize   = 32;
    static constexpr size_t NonceSize = 12;
    static constexpr size_t BlockSize = 64;

    /* Безпечне затирання пам'яті за допомогою бар'єра компілятора */
    static void secure_cleanse(void *ptr, size_t len) noexcept {
        volatile uint8_t *p = static_cast<volatile uint8_t *>(ptr);
        while (len--) {
            *p++ = 0;
        }
    }

    /* Шифрування/дешифрування потоку даних за схемою RFC 8439 */
    static void crypt(std::span<const uint8_t, KeySize> key,
                      std::span<const uint8_t, NonceSize> nonce,
                      uint32_t initial_counter,
                      std::span<const uint8_t> input,
                      std::span<uint8_t> output) {
        if (input.size() != output.size()) {
            return;
        }

        std::array<uint32_t, 16> state{};
        init_state(state, key, nonce, initial_counter);

        std::array<uint8_t, BlockSize> keystream_block{};
        uint32_t counter = initial_counter;
        size_t processed = 0;
        size_t remaining = input.size();

        while (remaining > 0) {
            state[12] = counter;
            generate_block(state, keystream_block);
            counter++;

            const size_t take = std::min(remaining, BlockSize);
            for (size_t i = 0; i < take; ++i) {
                output[processed + i] = input[processed + i] ^ keystream_block[i];
            }

            processed += take;
            remaining -= take;
        }

        /* Затирання ключів та внутрішнього стану перед виходом з функції */
        secure_cleanse(keystream_block.data(), keystream_block.size());
        secure_cleanse(state.data(), state.size() * sizeof(uint32_t));
    }

private:
    /* Базовий чвертьраунд ChaCha20 QR */
    static inline void quarter_round(uint32_t &a, uint32_t &b, uint32_t &c, uint32_t &d) noexcept {
        a += b; d ^= a; d = std::rotl(d, 16);
        c += d; b ^= c; b = std::rotl(b, 12);
        a += b; d ^= a; d = std::rotl(d, 8);
        c += d; b ^= c; b = std::rotl(b, 7);
    }

    /* Зчитування 32-бітного слова з пам'яті (Little-Endian) */
    static inline uint32_t load32_le(const uint8_t *src) noexcept {
        return static_cast<uint32_t>(src[0]) |
              (static_cast<uint32_t>(src[1]) << 8) |
              (static_cast<uint32_t>(src[2]) << 16) |
              (static_cast<uint32_t>(src[3]) << 24);
    }

    /* Запис 32-бітного слова у пам'ять (Little-Endian) */
    static inline void store32_le(uint8_t *dst, uint32_t v) noexcept {
        dst[0] = static_cast<uint8_t>(v & 0xff);
        dst[1] = static_cast<uint8_t>((v >> 8) & 0xff);
        dst[2] = static_cast<uint8_t>((v >> 16) & 0xff);
        dst[3] = static_cast<uint8_t>((v >> 24) & 0xff);
    }

    /* Ініціалізація матриці 4x4 */
    static void init_state(std::array<uint32_t, 16> &state,
                           std::span<const uint8_t, KeySize> key,
                           std::span<const uint8_t, NonceSize> nonce,
                           uint32_t counter) noexcept {
        state[0] = 0x61707865;
        state[1] = 0x3320646e;
        state[2] = 0x79622d32;
        state[3] = 0x6b206574;

        for (size_t i = 0; i < 8; ++i) {
            state[4 + i] = load32_le(key.data() + (i * 4));
        }

        state[12] = counter;
        state[13] = load32_le(nonce.data() + 0);
        state[14] = load32_le(nonce.data() + 4);
        state[15] = load32_le(nonce.data() + 8);
    }

    /* Генерація одного 64-байтного блоку */
    static void generate_block(const std::array<uint32_t, 16> &state_in,
                               std::array<uint8_t, BlockSize> &out_block) noexcept {
        std::array<uint32_t, 16> s = state_in;

        for (int i = 0; i < 10; ++i) {
            /* Колонки */
            quarter_round(s[0], s[4], s[8],  s[12]);
            quarter_round(s[1], s[5], s[9],  s[13]);
            quarter_round(s[2], s[6], s[10], s[14]);
            quarter_round(s[3], s[7], s[11], s[15]);

            /* Діагоналі */
            quarter_round(s[0], s[5], s[10], s[15]);
            quarter_round(s[1], s[6], s[11], s[12]);
            quarter_round(s[2], s[7], s[8],  s[13]);
            quarter_round(s[3], s[4], s[9],  s[14]);
        }

        /* Feed-Forward додавання */
        for (size_t i = 0; i < 16; ++i) {
            s[i] += state_in[i];
            store32_le(out_block.data() + (i * 4), s[i]);
        }

        secure_cleanse(s.data(), sizeof(s));
    }
};

} // namespace crypto
