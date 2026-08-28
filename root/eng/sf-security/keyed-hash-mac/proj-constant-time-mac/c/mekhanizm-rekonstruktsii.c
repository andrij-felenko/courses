#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

/* Обертання бітів вправо */
#define ROTR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
#define CH(x, y, z) (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x) (ROTR(x, 2) ^ ROTR(x, 13) ^ ROTR(x, 22))
#define EP1(x) (ROTR(x, 6) ^ ROTR(x, 11) ^ ROTR(x, 25))
#define SIG0(x) (ROTR(x, 7) ^ ROTR(x, 18) ^ ((x) >> 3))
#define SIG1(x) (ROTR(x, 17) ^ ROTR(x, 19) ^ ((x) >> 10))

static const uint32_t K[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

/* Компресійний крок SHA-256 над одним 64-байтним блоком */
void sha256_transform_block(uint32_t state[8], const uint8_t block[64]) {
    uint32_t w[64];
    for (size_t i = 0; i < 16; ++i) {
        w[i] = ((uint32_t)block[i * 4] << 24) |
               ((uint32_t)block[i * 4 + 1] << 16) |
               ((uint32_t)block[i * 4 + 2] << 8) |
               ((uint32_t)block[i * 4 + 3]);
    }
    for (size_t i = 16; i < 64; ++i) {
        w[i] = SIG1(w[i - 2]) + w[i - 7] + SIG0(w[i - 15]) + w[i - 16];
    }

    uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint32_t e = state[4], f = state[5], g = state[6], h = state[7];

    for (size_t i = 0; i < 64; ++i) {
        uint32_t t1 = h + EP1(e) + CH(e, f, g) + K[i] + w[i];
        uint32_t t2 = EP0(a) + MAJ(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }

    state[0] += a; state[1] += b; state[2] += c; state[3] += d;
    state[4] += e; state[5] += f; state[6] += g; state[7] += h;
}

/* Формування заповнення Merkle-Damgard для відомої початкової довжини */
size_t build_md_padding(size_t total_len_bytes, uint8_t *pad_out) {
    size_t pad_len = 0;
    pad_out[pad_len++] = 0x80;
    
    size_t current_len = total_len_bytes + 1;
    while ((current_len % 64) != 56) {
        pad_out[pad_len++] = 0x00;
        current_len++;
    }
    
    uint64_t bit_len = (uint64_t)total_len_bytes * 8;
    for (int i = 7; i >= 0; --i) {
        pad_out[pad_len++] = (uint8_t)((bit_len >> (i * 8)) & 0xFF);
    }
    return pad_len;
}

/* Виконання атаки подовженням */
void length_extension_attack(const uint32_t original_hash[8],
                            size_t key_len,
                            const uint8_t *orig_msg, size_t orig_msg_len,
                            const uint8_t *extension, size_t ext_len,
                            uint8_t *forged_msg_out, size_t *forged_msg_len_out,
                            uint32_t forged_hash_out[8]) {
    /* 1. Обчислення заповнення для початкового блоку (Key || Message) */
    size_t total_orig_bytes = key_len + orig_msg_len;
    uint8_t pad[128];
    size_t pad_len = build_md_padding(total_orig_bytes, pad);

    /* 2. Збирання нового фальсифікованого повідомлення: orig_msg || pad || extension */
    memcpy(forged_msg_out, orig_msg, orig_msg_len);
    memcpy(forged_msg_out + orig_msg_len, pad, pad_len);
    memcpy(forged_msg_out + orig_msg_len + pad_len, extension, ext_len);
    *forged_msg_len_out = orig_msg_len + pad_len + ext_len;

    /* 3. Ініціалізація стану регістрів перехопленим гешем */
    memcpy(forged_hash_out, original_hash, 8 * sizeof(uint32_t));

    /* 4. Підготовка блоків розширення з урахуванням сукупної довжини */
    size_t new_total_bytes = total_orig_bytes + pad_len + ext_len;
    uint8_t ext_pad[128];
    size_t ext_pad_len = build_md_padding(new_total_bytes, ext_pad);

    size_t total_ext_stream_len = ext_len + ext_pad_len;
    uint8_t *ext_stream = (uint8_t *)malloc(total_ext_stream_len);
    if (!ext_stream) return;

    memcpy(ext_stream, extension, ext_len);
    memcpy(ext_stream + ext_len, ext_pad, ext_pad_len);

    /* 5. Прогін компресійної функції для всіх нових 64-байтних блоків */
    for (size_t offset = 0; offset < total_ext_stream_len; offset += 64) {
        sha256_transform_block(forged_hash_out, ext_stream + offset);
    }

    free(ext_stream);
}
