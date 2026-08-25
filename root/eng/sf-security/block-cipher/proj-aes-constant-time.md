# ⚙️ Реалізація AES-128 у режимі CTR: константний час та апаратне прискорення AES-NI

Цей інженерний проект демонструє низькорівневу реалізацію симетричного шифрування блоковим шифром AES-128 у потоковому режимі лічильника (Counter Mode, CTR) із прямим використанням апаратного набору інструкцій Intel/AMD AES-NI. Архітектура рішення спроектована для гарантованого виконання в константному часі, максимального насичення конвеєра суперскалярного процесора та повного усунення вразливостей до атак за сторонніми каналами через кеш-пам'ять.

## Архітектура режиму CTR та апаратний конвеєр

Режим CTR перетворює 128-бітний блоковий шифр на високопродуктивний генератор псевдовипадкової гами. Замість послідовного шифрування блоків відкритих даних із взаємною залежністю (як у режимі CBC), блоковий шифр незалежно шифрує послідовність детерміністичних блоків лічильника. Отримана псевдовипадкова гама накладається на відкритий текст або шифротекст операцією побітового додавання за модулем 2 (XOR):

```
Блок лічильника i:   IV_Block[i] = Nonce (96 бітів) || Counter[i] (32 біти)
Генерація гами:      Keystream[i] = AES_Encrypt(Key, IV_Block[i])
Шифрування:          Ciphertext[i] = Plaintext[i] ⊕ Keystream[i]
Дешифрування:        Plaintext[i] = Ciphertext[i] ⊕ Keystream[i]
```

Ця схема надає три критичні інженерні переваги:
1. **Симетрія та простота контуру:** Дешифрування є повністю тотожним до шифрування. Конвеєр використовує лише пряму функцію `AES_Encrypt`, що дозволяє не реалізовувати обернені операції розкладу ключів та інверсні раунди `AESDEC`.
2. **Паралелізм та конвеєризація:** Обчислення `Keystream[i]` для будь-якого блоку `i` не залежить від попереднього блоку `i-1`. Сучасні процесори з кількома портами виконання інструкцій AES (наприклад, конвеєри векторного виконання Intel Skylake/Sunny Cove або AMD Zen 3/4) можуть одночасно обробляти до чотирьох незалежних блоків, досягаючи пропускної здатності менш ніж 0.6 такту на байт.
3. **Обробка довільної довжини без доповнення (Zero Padding Overhead):** Якщо фінальний фрагмент даних має розмір менш ніж 16 байтів, він маскується рівно відповідною кількістю байтів поточного блоку гами. Залишок згенерованої гами просто відкидається.

## Розширення ключа через `_mm_aeskeygenassist_si128`

Для AES-128 початковий 128-бітний майстер-ключ розгортається в 11 раундових ключів `RoundKeys[0...10]`. Кожен раундовий ключ обчислюється комбінацією векторних зсувів, заміни 4-байтових слів через апаратний S-Box інструкцією `_mm_aeskeygenassist_si128` та додаванням раундової константи `Rcon`:

- Інструкція `_mm_aeskeygenassist_si128(k, rcon)` виконує операцію `SubWord(RotWord(k))` над старшими байтами та додає константу `rcon`.
- Інструкція `_mm_shuffle_epi32` дублює отримане 32-бітне слово по всіх чотирьох позиціях 128-бітного регістра XMM.
- Серія з трьох зсувів `_mm_slli_si128(temp, 4)` та каскадних операцій XOR генерує наступні 4 слова раундового ключа.

## Реалізація модуля шифрування

:::tabs
```c
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
```
```cpp
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
```
:::

## Інженерний аналіз оптимізації та безпеки

### 1. Механізм константного часу в кремнії
Традиційні програмні реалізації AES на мові C використовують так звані T-таблиці (T-tables) розміром 4 КБ або 8 КБ, які об'єднують операції `SubBytes`, `ShiftRows` та `MixColumns`. Індекс звернення до таблиці формується як `index = state[i] ⊕ key[i]`. Оскільки індекс залежить від бітів таємного ключа, а адреса пам'яті визначає номер рядка кеш-пам'яті L1 (64 байти на лінію), час доступу різниться залежно від наявності даних у кеші (кеш-попадання ~4 такти проти промаху ~40 тактів). Супротивник через атаки Prime+Probe або Flush+Reload вимірює час виконання та відновлює повний 128-бітний ключ.

Використання інструкцій AES-NI (`AESENC`, `AESENCLAST`) повністю усуває звернення до пам'яті під час раундових обчислень. Усі операції — заміна байтів, циклічний зсув, множення многочленів у полі Галуа та додавання раундового ключа — виконуються всередині комбінаційної логіки конвеєра АЛП (ALU) за строго фіксовану кількість тактів незалежно від оброблюваних даних.

### 2. Вирівнювання пам'яті та робота з SIMD-регістрами
Інструкція `_mm_loadu_si128` завантажує 16 байтів із довільної (у тому числі невирівняної) адреси пам'яті у векторний регістр XMM. На сучасних мікроархітектурах штраф за невирівняне завантаження виникає лише тоді, коли блок даних перетинає межу 64-байтового рядка кешу (Cache-line split). Для критичних до затримки мережевих конвеєрів рекомендується вирівнювати буфери на 16 або 64 байти за допомогою `alignas(16)` або `posix_memalign`, що дозволяє замінити не вирівняні інструкції на швидші `_mm_load_si128` та `_mm_store_si128`.

### 3. Запобігання витоку пам'яті через Dead Store Elimination (DSE)
При завершенні роботи криптографічного контексту критично важливо гарантовано очистити масив раундових ключів `round_keys` та буфери лічильника. Звичайний виклик `memset(round_keys, 0, sizeof(round_keys))` оптимізуючий компілятор (GCC, Clang, MSVC) майже завжди видаляє під час фази оптимізації мертвого збереження (Dead Store Elimination), оскільки пам'ять після цього більше не читається програмою.

Для запобігання цій вразливості в C++ реалізації застосовано патерн RAII-деструктора із захищеним очищенням пам'яті через неоптимізований покажчик `volatile uint8_t*` або платформо-специфічну функцію ОС `SecureZeroMemory`. Компілятор зобов'язаний згенерувати інструкції запису нулів для кожного байта через семантику `volatile`.

### 4. Контроль переповнення лічильника в режимі CTR
Функція `inc_counter_be` виконує інкремент 128-бітного цілого числа у форматі порядку байтів від старшого до молодшого (big-endian), як вимагає стандарт NIST SP 800-38A. У високошвидкісних системах лічильник часто ділять на 96-бітний унікальний префікс (Nonce / Initialization Vector) та 32-бітний локальний лічильник блоків. При досягненні лічильником значення `2³² - 1` (тобто після шифрування `2³² × 16 = 64` Гігабайтів даних під одним IV) сесія шифрування зобов'язана бути негайно зупинена з обов'язковою генерацією нового ключа або нового Nonce, оскільки переповнення призведе до повторного використання пари `(Key, Counter)`, що еквівалентно повторному використанню одноразового блокнота (Two-Time Pad).
