#include <algorithm>
#include <array>
#include <cstdint>
#include <cstring>
#include <vector>

using Block = std::array<uint8_t, 16>;

// AES-128: одне оборотне перетворення 16-байтового блока під ключем.
// Реалізація — з бібліотеки або з апаратного блока; тут потрібен лише інтерфейс.
struct Aes128 {
    explicit Aes128(const Block& key);
    void encrypt_block(const uint8_t in[16], uint8_t out[16]) const;
    void decrypt_block(const uint8_t in[16], uint8_t out[16]) const;
};

struct Subsample { uint32_t clear_bytes = 0, enc_bytes = 0; };

struct TrackEnc {                            // з tenc — типове на всю доріжку
    uint8_t is_protected = 0, per_sample_iv_size = 0;
    uint8_t crypt_byte_block = 0, skip_byte_block = 0;
    Block   kid{};
    std::vector<uint8_t> constant_iv;
};

struct SampleEnc {                           // з senc — на кожен семпл
    std::vector<uint8_t>   iv;
    std::vector<Subsample> subsamples;       // порожньо → захищений увесь семпл
};
