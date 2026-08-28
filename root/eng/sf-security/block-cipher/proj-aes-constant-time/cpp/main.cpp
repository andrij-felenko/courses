#include <array>
#include <cstdint>
#include <cstddef>
#include <cstring>
#include <expected>
#include <span>
#include <wmmintrin.h>
#include <immintrin.h>

#if defined(_MSC_VER)
  #include <windows.h>
#endif

namespace crypto {

enum class Error {
    InvalidKeyLength,
    InvalidIvLength,
    HardwareUnsupported
};

class Aes128Ctr {
public:
    static constexpr size_t KeySize = 16;
    static constexpr size_t BlockSize = 16;

    explicit Aes128Ctr(std::span<const uint8_t, KeySize> key) noexcept {
        expand_keys(key.data());
    }

    ~Aes128Ctr() noexcept {
        secure_zero();
    }

    Aes128Ctr(const Aes128Ctr&) = delete;
    Aes128Ctr& operator=(const Aes128Ctr&) = delete;

    Aes128Ctr(Aes128Ctr&& other) noexcept {
        std::memcpy(round_keys_.data(), other.round_keys_.data(), sizeof(round_keys_));
        other.secure_zero();
    }

    Aes128Ctr& operator=(Aes128Ctr&& other) noexcept {
        if (this != &other) {
            secure_zero();
            std::memcpy(round_keys_.data(), other.round_keys_.data(), sizeof(round_keys_));
            other.secure_zero();
        }
        return *this;
    }

    void process(std::span<const uint8_t, BlockSize> initial_iv,
                 std::span<const uint8_t> input,
                 std::span<uint8_t> output) const noexcept {
        std::array<uint8_t, BlockSize> cur_iv;
        std::memcpy(cur_iv.data(), initial_iv.data(), BlockSize);

        std::array<uint8_t, BlockSize> keystream;
        size_t offset = 0;
        const size_t length = input.size();

        while (offset < length) {
            __m128i iv_blk = _mm_loadu_si128(reinterpret_cast<const __m128i*>(cur_iv.data()));
            __m128i enc_iv = encrypt_block(iv_blk);
            _mm_storeu_si128(reinterpret_cast<__m128i*>(keystream.data()), enc_iv);

            const size_t chunk = (length - offset < BlockSize) ? (length - offset) : BlockSize;
            for (size_t i = 0; i < chunk; ++i) {
                output[offset + i] = input[offset + i] ^ keystream[i];
            }

            increment_counter(cur_iv);
            offset += chunk;
        }

        secure_zero_memory(cur_iv.data(), cur_iv.size());
        secure_zero_memory(keystream.data(), keystream.size());
    }

private:
    std::array<__m128i, 11> round_keys_{};

    static inline __m128i assist_expand(__m128i key, __m128i assist) noexcept {
        __m128i temp = key;
        assist = _mm_shuffle_epi32(assist, _MM_SHUFFLE(3, 3, 3, 3));
        temp = _mm_xor_si128(temp, _mm_slli_si128(temp, 4));
        temp = _mm_xor_si128(temp, _mm_slli_si128(temp, 4));
        temp = _mm_xor_si128(temp, _mm_slli_si128(temp, 4));
        return _mm_xor_si128(temp, assist);
    }

    void expand_keys(const uint8_t* raw_key) noexcept {
        __m128i k = _mm_loadu_si128(reinterpret_cast<const __m128i*>(raw_key));
        round_keys_[0] = k;

        k = assist_expand(k, _mm_aeskeygenassist_si128(k, 0x01));
        round_keys_[1] = k;
        k = assist_expand(k, _mm_aeskeygenassist_si128(k, 0x02));
        round_keys_[2] = k;
        k = assist_expand(k, _mm_aeskeygenassist_si128(k, 0x04));
        round_keys_[3] = k;
        k = assist_expand(k, _mm_aeskeygenassist_si128(k, 0x08));
        round_keys_[4] = k;
        k = assist_expand(k, _mm_aeskeygenassist_si128(k, 0x10));
        round_keys_[5] = k;
        k = assist_expand(k, _mm_aeskeygenassist_si128(k, 0x20));
        round_keys_[6] = k;
        k = assist_expand(k, _mm_aeskeygenassist_si128(k, 0x40));
        round_keys_[7] = k;
        k = assist_expand(k, _mm_aeskeygenassist_si128(k, 0x80));
        round_keys_[8] = k;
        k = assist_expand(k, _mm_aeskeygenassist_si128(k, 0x1B));
        round_keys_[9] = k;
        k = assist_expand(k, _mm_aeskeygenassist_si128(k, 0x36));
        round_keys_[10] = k;
    }

    [[nodiscard]] inline __m128i encrypt_block(__m128i in) const noexcept {
        __m128i state = _mm_xor_si128(in, round_keys_[0]);
        state = _mm_aesenc_si128(state, round_keys_[1]);
        state = _mm_aesenc_si128(state, round_keys_[2]);
        state = _mm_aesenc_si128(state, round_keys_[3]);
        state = _mm_aesenc_si128(state, round_keys_[4]);
        state = _mm_aesenc_si128(state, round_keys_[5]);
        state = _mm_aesenc_si128(state, round_keys_[6]);
        state = _mm_aesenc_si128(state, round_keys_[7]);
        state = _mm_aesenc_si128(state, round_keys_[8]);
        state = _mm_aesenc_si128(state, round_keys_[9]);
        return _mm_aesenclast_si128(state, round_keys_[10]);
    }

    static inline void increment_counter(std::array<uint8_t, BlockSize>& iv) noexcept {
        for (int i = 15; i >= 0; --i) {
            if (++iv[i] != 0) break;
        }
    }

    void secure_zero() noexcept {
        secure_zero_memory(round_keys_.data(), sizeof(round_keys_));
    }

    static void secure_zero_memory(void* ptr, size_t size) noexcept {
#if defined(_MSC_VER)
        SecureZeroMemory(ptr, size);
#else
        volatile uint8_t* p = static_cast<volatile uint8_t*>(ptr);
        while (size--) *p++ = 0;
#endif
    }
};

} // namespace crypto
