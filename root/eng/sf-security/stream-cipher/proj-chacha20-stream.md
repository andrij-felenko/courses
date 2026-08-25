# ⚙️ Практична реалізація шифру ChaCha20 мовами C та C++

Надійна програмна реалізація потокового шифру ChaCha20 (RFC 8439) вимагає суворого виконання операцій за константний час CPU без умовних переходів, коректного порядку байтів (little-endian) та гарантованого очищення конфіденційного стану з оперативної пам'яті.

## Архітектура реалізації

Алгоритм ChaCha20 побудовано на трьох чітко розмежованих рівнях обробки даних:

1. **Чвертьраунд (Quarter Round, QR):** Базова операція ARX (додавання за модулем `2³²`, циклічний зсув вліво, побітовий XOR), що виконується над чотирма 32-бітними словами. Функція не містить умовних розгалужень `if/else`, що унеможливлює витоки через предикцію переходів процесора (Branch Prediction Side-Channels).
2. **Блокова функція (Block Function):** Ініціалізація матриці стану `4 × 4` (16 слів по 32 біти), проходження 10 подвійних раундів (20 раундів загалом: 10 колонкових та 10 діагональних) та обов'язкове пряме додавання початкового стану (Feed-Forward) для унеможливлення обернення раундів.
3. **Потокове шифрування (Stream XOR):** Генерація 64-байтних блоків гами, інкремент 32-бітного лічильника блоків та побайтове накладання гами на відкритий текст або шифротекст із можливістю прямого довільного доступу до будь-якої позиції в потоці (Random Access).

## Вихідний код реалізації

Нижче наведено модульну та безпечну реалізацію ChaCha20 мовами C та сучасним C++20.

:::tabs
@tab C
```c
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
```
@tab C++
```cpp
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
```
:::

## Векторизація SIMD та паралелізм обчислень

Архітектурна перевага ChaCha20 полягає у природній підтримці векторних інструкцій сучасних процесорів (AVX2, AVX-512 на x86-64 та NEON на ARMv8/v9):

1. **Паралелізм усередині блоку (4-way parallelism):** Чотири колонкові чвертьраунди `QR(0..3)` абсолютно незалежні між собою. Чотири слова кожної колонки завантажуються в чотири 128-бітні векторні регістри SIMD (`__m128i` або `uint32x4_t`). Усі 16 слів матриці оновлюються паралельно лише за 4 векторні операції додавання, 4 векторні XOR та 4 векторні зсуви.
2. **Паралелізм між блоками (Multi-block processing):** Оскільки шифрування в режимі лічильника є повністю паралельним, процесор із 256-бітними регістрами AVX2 може одночасно обчислювати **два незалежні блоки гами** (128 байтів за прохід), а векторні розширення AVX-512 або 8-блокові конвеєри обробляють **512 байтів гами за один виклик**, досягаючи швидкості понад 4 ГБайт/с на одне процесорне ядро без використання спеціалізованих апаратних прискорювачів.
3. **Вирівнювання пам'яті (Memory Alignment):** Для досягнення максимальної пропускної здатності SIMD-векторів буфери відкритого тексту та шифротексту рекомендується вирівнювати за межею 64 байтів (розмір лінії кешу L1). Це запобігає штрафам за розщеплення ліній кешу (Cache-Line Split Penalty) під час непарних векторних завантажень.

## Розширення XChaCha20 для безпечного випадкового Nonce

У розподілених системах без централізованого лічильника пакетів (наприклад, у p2p-мережах або stateless серверах) 96-бітний Nonce не можна вибирати випадково через ризик колізій за парадоксом днів народження (колізія стає ймовірною вже після `2⁴⁸` повідомлень).

Для вирішення цієї проблеми розроблено **XChaCha20** з 192-бітним (24 байти) Nonce:
1. Застосовується допоміжна функція **HChaCha20**: перші 16 байтів 192-бітного Nonce разом із 256-бітним ключем пропускаються крізь 20 раундів ChaCha20 без фінального додавання Feed-Forward.
2. На виході формується проміжний 256-бітний підключ `SubKey`.
3. Решта 8 байтів Nonce використовуються разом із 64-бітним лічильником блоків для стандартного шифрування ChaCha20 на згенерованому `SubKey`.

При 192-бітному просторі Nonce випадкова генерація залишається абсолютно безпечною до `2⁹⁶` пакетів, що повністю виключає колізії в будь-яких практичних системах.

## Тестові вектори валідації (RFC 8439 Test Vectors)

Для верифікації правильності реалізації RFC 8439 надає еталонний тестовий вектор:

- **Ключ (32 байти):** `00:01:02:03:04:05:06:07:08:09:0a:0b:0c:0d:0e:0f:10:11:12:13:14:15:16:17:18:19:1a:1b:1c:1d:1e:1f`
- **Nonce (12 байтів):** `00:00:00:00:00:00:00:4a:00:00:00:00`
- **Initial Block Counter:** `1`
- **Очікуваний перший блок гами (64 байти):**
  `10:f1:e7:e4:d1:3b:59:15:50:0f:dd:1f:a3:20:71:c4:37:d6:44:31:68:e2:b0:c2:c0:3a:5d:09:73:e2:f6:17:90:ba:d3:db:c7:c1:d8:98:ea:05:68:05:d4:d3:0a:21:b8:cc:5b:31:43:49:15:30:57:a2:70:e1:81:67:e4:3b`

Якщо згенеровані байти збігаються з еталоном, реалізація чвертьраундів, порядку байтів та додавання Feed-Forward є коректною.

## Інженерні пастки реалізації та захист пам'яті

1. **Оптимізація мертвого коду (Dead Code Elimination):** Компілятори C/C++ (GCC, Clang, MSVC) за високих рівнів оптимізації (`-O2`, `-O3`) часто видаляють стандартний виклик `memset(state, 0, sizeof(state))` наприкінці функції, якщо масив є локальною змінною на стеку і більше не читається в поточному коді. Це призводить до збереження ключів у пам'яті стека, де вони можуть бути викрадені через дампи пам'яті або атаки переповнення буфера в інших функціях. Використання кваліфікатора `volatile` або функцій `explicit_bzero` / `SecureZeroMemory` є обов'язковим для надійного очищення секретів.
2. **Переповнення лічильника блоків (Block Counter Overflow):** При 32-бітному лічильнику блоків максимальний обсяг даних, зашифрованих на одній парі `(Key, Nonce)`, становить `2³² × 64` байти = **256 Гігабайтів**. Якщо потік перевищує цей ліміт, лічильник переповнюється до `0`, спричиняючи катастрофічне повторення гами (Nonce Reuse). Для захисту протокол повинен ініціювати обов'язкову зміну ключа (Rekeying) задовго до досягнення ліміту блоків.
3. **Строгий порядок байтів (Endianness):** На платформах Big-Endian (деякі мережеві маршрутизатори MIPS та процесори SPARC/PowerPC) прямий кастинг покажчиків `(uint32_t*)ptr` ламає сумісність із RFC 8439. Зчитування та запис через явні побайтові зсуви `load32_le` / `store32_le` гарантують детерміністичну та кросплатформну роботу алгоритму на будь-яких архітектурах.
