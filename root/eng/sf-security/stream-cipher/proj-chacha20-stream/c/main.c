#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define CHACHA20_KEY_SIZE   32
#define CHACHA20_NONCE_SIZE 12
#define CHACHA20_BLOCK_SIZE 64

/* Циклічний зсув вліво 32-бітного слова за константний час */
static inline uint32_t rotl32(uint32_t v, unsigned int c) {
    return (v << c) | (v >> (32 - c));
}

/* Зчитування 32-бітного слова у форматі Little-Endian */
static inline uint32_t load32_le(const uint8_t *src) {
    return ((uint32_t)src[0]) |
           (((uint32_t)src[1]) << 8) |
           (((uint32_t)src[2]) << 16) |
           (((uint32_t)src[3]) << 24);
}

/* Запис 32-бітного слова у пам'ять у форматі Little-Endian */
static inline void store32_le(uint8_t *dst, uint32_t v) {
    dst[0] = (uint8_t)(v & 0xff);
    dst[1] = (uint8_t)((v >> 8) & 0xff);
    dst[2] = (uint8_t)((v >> 16) & 0xff);
    dst[3] = (uint8_t)((v >> 24) & 0xff);
}

/* Базовий чвертьраунд ChaCha20 QR(a, b, c, d) */
#define CHACHA20_QR(a, b, c, d) do { \
    (a) += (b); (d) ^= (a); (d) = rotl32((d), 16); \
    (c) += (d); (b) ^= (c); (b) = rotl32((b), 12); \
    (a) += (b); (d) ^= (a); (d) = rotl32((d), 8);  \
    (c) += (d); (b) ^= (c); (b) = rotl32((b), 7);  \
} while (0)

/* Обчислення одного 64-байтного блоку гами ChaCha20 */
void chacha20_block(const uint32_t state_in[16], uint8_t key_stream[64]) {
    uint32_t state[16];
    int i;

    /* Копіювання початкового стану */
    for (i = 0; i < 16; i++) {
        state[i] = state_in[i];
    }

    /* 10 подвійних раундів = 20 раундів дифузії */
    for (i = 0; i < 10; i++) {
        /* Колонковий раунд (Column Round) */
        CHACHA20_QR(state[0], state[4], state[8],  state[12]);
        CHACHA20_QR(state[1], state[5], state[9],  state[13]);
        CHACHA20_QR(state[2], state[6], state[10], state[14]);
        CHACHA20_QR(state[3], state[7], state[11], state[15]);

        /* Діагональний раунд (Diagonal Round) */
        CHACHA20_QR(state[0], state[5], state[10], state[15]);
        CHACHA20_QR(state[1], state[6], state[11], state[12]);
        CHACHA20_QR(state[2], state[7], state[8],  state[13]);
        CHACHA20_QR(state[3], state[4], state[9],  state[14]);
    }

    /* Feed-Forward: додавання початкового стану за модулем 2^32 */
    for (i = 0; i < 16; i++) {
        state[i] += state_in[i];
    }

    /* Серіалізація в байти гами у форматі Little-Endian */
    for (i = 0; i < 16; i++) {
        store32_le(key_stream + (i * 4), state[i]);
    }

    /* Гарантоване затирання локального стану */
    volatile uint32_t *v = (volatile uint32_t *)state;
    for (i = 0; i < 16; i++) v[i] = 0;
}

/* Ініціалізація матриці стану ChaCha20 (RFC 8439) */
void chacha20_init_state(uint32_t state[16],
                         const uint8_t key[32],
                         const uint8_t nonce[12],
                         uint32_t block_counter) {
    /* Рядок 0: Константи "expand 32-byte k" */
    state[0] = 0x61707865;
    state[1] = 0x3320646e;
    state[2] = 0x79622d32;
    state[3] = 0x6b206574;

    /* Рядки 1-2: 256-бітний ключ (8 слів) */
    state[4]  = load32_le(key + 0);
    state[5]  = load32_le(key + 4);
    state[6]  = load32_le(key + 8);
    state[7]  = load32_le(key + 12);
    state[8]  = load32_le(key + 16);
    state[9]  = load32_le(key + 20);
    state[10] = load32_le(key + 24);
    state[11] = load32_le(key + 28);

    /* Рядок 3: Лічильник блоків та 96-бітний Nonce */
    state[12] = block_counter;
    state[13] = load32_le(nonce + 0);
    state[14] = load32_le(nonce + 4);
    state[15] = load32_le(nonce + 8);
}

/* Потокове шифрування/дешифрування довільного буфера даних */
void chacha20_crypt(const uint8_t key[32],
                    const uint8_t nonce[12],
                    uint32_t initial_counter,
                    const uint8_t *input,
                    uint8_t *output,
                    size_t length) {
    uint32_t state[16];
    uint8_t block[CHACHA20_BLOCK_SIZE];
    uint32_t counter = initial_counter;
    size_t i, offset = 0;

    chacha20_init_state(state, key, nonce, counter);

    while (length > 0) {
        state[12] = counter;
        chacha20_block(state, block);
        counter++;

        size_t chunk = (length < CHACHA20_BLOCK_SIZE) ? length : CHACHA20_BLOCK_SIZE;
        for (i = 0; i < chunk; i++) {
            output[offset + i] = input[offset + i] ^ block[i];
        }

        offset += chunk;
        length -= chunk;
    }

    /* Безпечне очищення конфіденційної пам'яті */
    volatile uint8_t *vb = (volatile uint8_t *)block;
    for (i = 0; i < sizeof(block); i++) vb[i] = 0;
    volatile uint32_t *vs = (volatile uint32_t *)state;
    for (i = 0; i < 16; i++) vs[i] = 0;
}
