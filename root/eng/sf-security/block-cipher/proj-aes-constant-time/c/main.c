#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include <wmmintrin.h>
#include <immintrin.h>

#if defined(_MSC_VER)
  #include <windows.h>
  #define SECURE_ZERO(ptr, size) SecureZeroMemory((ptr), (size))
#elif defined(__STDC_LIB_EXT1__)
  #define SECURE_ZERO(ptr, size) memset_s((ptr), (size), 0, (size))
#else
  static void secure_zero_fallback(void *v, size_t n) {
      volatile uint8_t *p = (volatile uint8_t *)v;
      while (n--) *p++ = 0;
  }
  #define SECURE_ZERO(ptr, size) secure_zero_fallback((ptr), (size))
#endif

typedef struct {
    __m128i round_keys[11];
} aes128_ctx_t;

/* Допоміжна функція розкладу ключів для AES-128 */
static inline __m128i aes128_key_expand_assist(__m128i key, __m128i assist) {
    __m128i temp1 = key;
    assist = _mm_shuffle_epi32(assist, _MM_SHUFFLE(3, 3, 3, 3));
    
    temp1 = _mm_xor_si128(temp1, _mm_slli_si128(temp1, 4));
    temp1 = _mm_xor_si128(temp1, _mm_slli_si128(temp1, 4));
    temp1 = _mm_xor_si128(temp1, _mm_slli_si128(temp1, 4));
    
    return _mm_xor_si128(temp1, assist);
}

int aes128_init(aes128_ctx_t *ctx, const uint8_t key[16]) {
    if (!ctx || !key) return -1;

    __m128i k = _mm_loadu_si128((const __m128i *)key);
    ctx->round_keys[0] = k;

    k = aes128_key_expand_assist(k, _mm_aeskeygenassist_si128(k, 0x01));
    ctx->round_keys[1] = k;
    k = aes128_key_expand_assist(k, _mm_aeskeygenassist_si128(k, 0x02));
    ctx->round_keys[2] = k;
    k = aes128_key_expand_assist(k, _mm_aeskeygenassist_si128(k, 0x04));
    ctx->round_keys[3] = k;
    k = aes128_key_expand_assist(k, _mm_aeskeygenassist_si128(k, 0x08));
    ctx->round_keys[4] = k;
    k = aes128_key_expand_assist(k, _mm_aeskeygenassist_si128(k, 0x10));
    ctx->round_keys[5] = k;
    k = aes128_key_expand_assist(k, _mm_aeskeygenassist_si128(k, 0x20));
    ctx->round_keys[6] = k;
    k = aes128_key_expand_assist(k, _mm_aeskeygenassist_si128(k, 0x40));
    ctx->round_keys[7] = k;
    k = aes128_key_expand_assist(k, _mm_aeskeygenassist_si128(k, 0x80));
    ctx->round_keys[8] = k;
    k = aes128_key_expand_assist(k, _mm_aeskeygenassist_si128(k, 0x1B));
    ctx->round_keys[9] = k;
    k = aes128_key_expand_assist(k, _mm_aeskeygenassist_si128(k, 0x36));
    ctx->round_keys[10] = k;

    return 0;
}

static inline __m128i aes128_encrypt_block(const aes128_ctx_t *ctx, __m128i in) {
    __m128i state = _mm_xor_si128(in, ctx->round_keys[0]);
    
    state = _mm_aesenc_si128(state, ctx->round_keys[1]);
    state = _mm_aesenc_si128(state, ctx->round_keys[2]);
    state = _mm_aesenc_si128(state, ctx->round_keys[3]);
    state = _mm_aesenc_si128(state, ctx->round_keys[4]);
    state = _mm_aesenc_si128(state, ctx->round_keys[5]);
    state = _mm_aesenc_si128(state, ctx->round_keys[6]);
    state = _mm_aesenc_si128(state, ctx->round_keys[7]);
    state = _mm_aesenc_si128(state, ctx->round_keys[8]);
    state = _mm_aesenc_si128(state, ctx->round_keys[9]);
    state = _mm_aesenclast_si128(state, ctx->round_keys[10]);
    
    return state;
}

/* Інкремент 128-бітного лічильника у форматі big-endian */
static inline void inc_counter_be(uint8_t iv[16]) {
    for (int i = 15; i >= 0; --i) {
        if (++iv[i] != 0) break;
    }
}

int aes128_ctr_crypt(const aes128_ctx_t *ctx,
                      const uint8_t iv[16],
                      const uint8_t *in,
                      uint8_t *out,
                      size_t length) {
    if (!ctx || !iv || !in || !out) return -1;

    uint8_t cur_iv[16];
    memcpy(cur_iv, iv, 16);

    uint8_t keystream[16];
    size_t offset = 0;

    while (offset < length) {
        __m128i iv_blk = _mm_loadu_si128((const __m128i *)cur_iv);
        __m128i enc_iv = aes128_encrypt_block(ctx, iv_blk);
        _mm_storeu_si128((__m128i *)keystream, enc_iv);

        size_t block_size = (length - offset < 16) ? (length - offset) : 16;
        for (size_t i = 0; i < block_size; ++i) {
            out[offset + i] = in[offset + i] ^ keystream[i];
        }

        inc_counter_be(cur_iv);
        offset += block_size;
    }

    SECURE_ZERO(cur_iv, sizeof(cur_iv));
    SECURE_ZERO(keystream, sizeof(keystream));
    return 0;
}

void aes128_destroy(aes128_ctx_t *ctx) {
    if (ctx) {
        SECURE_ZERO(ctx, sizeof(aes128_ctx_t));
    }
}
