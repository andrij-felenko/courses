# ⚙️ Реалізація ітеративної хеш-функції Меркле — Дамґорда та атак подовження

У цій практичній вставці показано повну працездатну реалізацію ітеративної хеш-функції на основі побудови Меркле — Дамґорда (з підкладкою та додаванням довжини), детальний аналіз її внутрішньої роботи, покрокове простеження стану, математичну демонстрацію вразливості до атаки подовження повідомлення (*Length Extension Attack*), а також практичну реалізацію захисного механізму HMAC.

## Принципи побудови та архітектура ARX

Побудова Меркле — Дамґорда перетворює однобічну функцію стиснення фіксованого розміру `f: {0,1}ᶜ × {0,1}ᵇ → {0,1}ᶜ` у хеш-функцію, здатну обробляти вхідні дані довільної неограниченої довжини.

У нашому практичному прикладі ми побудуємо 128-бітову ітеративну хеш-функцію, яка оперує блоками розміром `b = 64` байти (512 бітів) та зберігає внутрішній стан у вигляді чотирьох 32-бітових слів `(state[0]...state[3])`.

Алгоритм складається з трьох ключових фаз:

### 1. Функція стиснення (ARX Core)

В основу функції стиснення покладено операції **ARX** (*Add-Rotate-XOR*):
- **Add:** додавання 32-бітових цілих чисел за модулем `2³²`.
- **Rotate:** циклічний зсув бітів ліворуч `rotl32(x, n) = (x << n) | (x >> (32 - n))`.
- **XOR:** побітове виключне або `a ^ b`.

ARX-операції обрано тому, що вони виконуються за один такт на будь-якому мікропроцесорі, не містять таблиць підстановки у пам'яті (що гарантує захист від атак по сторонніх каналах через кеш-пам'ять) і створюють швидкий лавинний ефект (*avalanche effect*).

Кожен 64-байтовий блок вхідного повідомлення розпаковується у 16 32-бітових слів `w[0]...w[15]` з урахуванням прямого порядку байтів (*Little-Endian*). Побайтова конверсія гарантує однаковий математичний результат на архітектурах x86, ARM та RISC-V незалежно від апаратного порядкування байтів процесора. Далі виконується 16 раундів змішування з внутрішнім станом за формулою:

```
f(b, c, d) = (b ∧ c) ⊕ (¬b ∧ d)                      [нелінійна вибіркова функція Ch]
temp = a + f(b, c, d) + w[r] + K                     [модульне додавання з блоком даних та константою]
b' = b + rotl32(temp, 7)                             [циклічний зсув та оновлення слова b]
```

Наприкінці обробки кожного блоку до поточного стану додається початковий стан (зв'язок *Feed-Forward* у стилі Давіса — Майєра): `state[i] = state[i] + initial_state[i]`. Це унеможливлює обернення функції стиснення навіть за умови повного контролю вхідних бітів `w[i]`.

### 2. Підкладка та зміцнення Меркле — Дамґорда

Для гарантії того, що будь-яке повідомлення буде кратним 64 байтам і не виникне колізійної амбівалентності між короткими й довгими входами, застосовується канонічна підкладка:
1. Після останнього байта повідомлення додається обов'язковий байт `0x80` (бітова одиниця `10000000₂`).
2. Додаються нульові байти `0x00` доти, доки довжина буфера не досягне 56 байтів у поточному 64-байтовому блоці. Якщо повідомлення вже має довжину понад 56 байтів, поточний блок доповнюється нулями до 64 байтів, обробляється функцією стиснення, а підкладка продовжується у новому порожньому блоці.
3. В останні 8 байтів (з 56 по 63) записується точна початкова довжина вхідного повідомлення у бітах як 64-бітове ціле число без знаку (`total_bits`).

Крайовий випадок виникає тоді, коли довжина вхідного повідомлення становить ровно 56 або 64 байти. Якщо вхід має 56 байтів, доданий байт `0x80` робить довжину 57 байтів, що перевищує поріг 56 байтів. У цьому разі алгоритм доповнює поточний блок нулями до 64 байтів, обчислює для нього раунд стиснення, створює новий порожній 64-байтовий блок, заповнює його 56 нулями та записує 8 байтів довжини в його кінець. Це гарантує, що лічильник довжини завжди потрапляє у фінальний крок обробки.

## Покроковий розбір простеження стану для входу "abc"

Розглянемо покроковий розбір обробки класичного текстового рядка `"abc"` (3 байти = 24 біти).

1. **Формування підкладки у буфері:**
   - Вхідні байти: `[0x61, 0x62, 0x63]` (ASCII значення букв 'a', 'b', 'c').
   - Байт маркування підкладки: `0x80` додається на індексі 3.
   - Нульові байти: 52 байти `0x00` додаються на індексах з 4 по 55.
   - Запис довжини: 64-бітове число `24` (`0x0000000000000018`) записується на індексах з 56 по 63 у форматі Little-Endian: `[0x18, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]`.

2. **Розпакування у слова `w[16]`:**
   - `w[0] = 0x80636261` (байтова комбінація `0x61 | (0x62 << 8) | (0x63 << 16) | (0x80 << 24)`).
   - `w[1...13] = 0x00000000`.
   - `w[14] = 0x00000018` (молодші 32 біти довжини 24).
   - `w[15] = 0x00000000` (старші 32 біти довжини 24).

3. **Обробка раундів:**
   - Вхідні змінні стан ініціалізуються вектором `IV`:
     `a = 0x67452301`, `b = 0xEFCDAB89`, `c = 0x98BADCFE`, `d = 0x10325476`.
   - Після проведення 16 раундів ARX значення `(a, b, c, d)` додаються до початкових слів `IV`.
   - Фінальний стан розпаковується у 16-байтовий масив відбитка.

## Нюанси безпечного зачищення пам'яті (Secure Wiping)

Під час роботи з HMAC чи хешуванням паролів у внутрішній пам'яті (на стеку чи в купі) залишаються проміжні масиви `k_padded`, `i_key` та `o_key`.

Звичайний виклик `memset(k_padded, 0, BLOCK_SIZE)` наприкінці функції дуже часто **видаляється компілятором** під час агресивної оптимізації (`-O2` чи `-O3`), оскільки компілятор бачить, що масив `k_padded` більше не використовується далі у коді (dead store elimination).

Для безпечного очищення секретних ключів необхідно використовувати спеціалізовані функції, які компілятору заборонено оптимізувати:
- У C: `explicit_bzero(k_padded, BLOCK_SIZE)` або `memset_s`.
- У C++: створення класичного RAII-обгортки з викликом `volatile`-вказівника для зачищення пам'яті в деструкторі.

## Механіка атаки подовження повідомлення (Length Extension Attack)

Оскільки вихід хеш-функції Меркле — Дамґорда `H(M)` є результатом роботи останнього кроку функції стиснення `f(h_{m-1}, M_m)`, він містить у собі весь внутрішній стан `(state[0]...state[3])`.

Якщо веб-сервер використовує просте хешування авторизаційного токена та параметрів запиту `token = H(secret_key || "action=transfer&amount=100")`, зловмисник може здійснити атаку:
1. Зловмисник витягує з відомого токена `token` чотири 32-бітові слова `(state[0]...state[3])`.
2. Знаючи довжину ключа `secret_key` та повідомлення, зловмисник відновлює канонічну підкладку `pad`, яку додав алгоритм Меркле — Дамґорда.
3. Зловмисник створює новий екземпляр хешера, завантажує у нього відновлені слова `state` як `IV'` та оновлює кількість оброблених бітів на `|secret_key || message || pad|`.
4. Зловмисник додає до запиту новий параметр `&admin=true` і отримує підпис `token' = H(secret_key || message || pad || "&admin=true")`.

Сервер приймає такий запит як цілком валідний, бо підпис збігається, хоча секретний ключ `secret_key` не знав ніхто, крім сервера!

## Захищена конструкція HMAC

Для запобігання атаці подовження було розроблено стандарт **HMAC** (*Hash-based Message Authentication Code*, RFC 2104):
```
HMAC(K, M) = H((K ⊕ opad) || H((K ⊕ ipad) || M))
```
де `ipad` (inner pad) є 64-байтовим блоком із байтів `0x36`, а `opad` (outer pad) — 64-байтовим блоком із байтів `0x5C`.

Двоетапна обробка знищує зв'язок між внутрішнім станом першого хешування та підсумковим результатом:
- На внутрішньому кроці обчислюється `inner = H((K ⊕ ipad) || M)`.
- На зовнішньому кроці обчислюється `HMAC = H((K ⊕ opad) || inner)`.

Навіть якщо зловмисник дізнається підсумковий `HMAC`, він є результатом хешування `(K ⊕ opad) || inner`, а не первинного повідомлення `M`. Без знання ключа `K` неможливо сформувати підкладку для внутрішнього чи зовнішнього кроку.

## Повний вихідний код у програмуванні

Нижче наведено ідіоматичні реалізації алгоритму двома мовами — C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define BLOCK_SIZE 64
#define STATE_WORDS 4

/* Контекст ітеративної хеш-функції Меркле — Дамґорда */
typedef struct {
    uint32_t state[STATE_WORDS];    /* Внутрішній стан (128 бітів) */
    uint64_t total_bits;            /* Загальна довжина обробленого повідомлення у бітах */
    uint8_t buffer[BLOCK_SIZE];     /* Буфер для накопичення поточного 64-байтового блоку */
    size_t buffer_len;              /* Кількість байтів у поточному буфері */
} md_ctx_t;

/* Циклічний зсув 32-бітового числа ліворуч на n бітів */
static uint32_t rotl32(uint32_t x, int n) {
    return (x << n) | (x >> (32 - n));
}

/* 
 * Основна ARX-функція стиснення f(state, block).
 * Обробляє один 64-байтовий блок і оновлює внутрішній стан.
 */
static void md_compress(uint32_t state[STATE_WORDS], const uint8_t block[BLOCK_SIZE]) {
    uint32_t w[16];

    /* Розпакування 64 байтів у 16 32-бітових слів (Little-Endian) */
    for (int i = 0; i < 16; i++) {
        w[i] = ((uint32_t)block[i * 4]) |
               ((uint32_t)block[i * 4 + 1] << 8) |
               ((uint32_t)block[i * 4 + 2] << 16) |
               ((uint32_t)block[i * 4 + 3] << 24);
    }

    uint32_t a = state[0];
    uint32_t b = state[1];
    uint32_t c = state[2];
    uint32_t d = state[3];

    /* 16 раундів перемішування ARX */
    for (int r = 0; r < 16; r++) {
        /* Нелінійна вибіркова функція Ch(b, c, d) */
        uint32_t f = (b & c) ^ (~b & d);
        uint32_t temp = a + f + w[r] + 0x5A827999U;
        a = d;
        d = c;
        c = b;
        b = b + rotl32(temp, 7);
    }

    /* Додавання початкового стану (Дамґордівська конкатенація Давіса — Майєра) */
    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
}

/* Ініціалізація контексту хешування вектором IV */
void md_init(md_ctx_t *ctx) {
    ctx->state[0] = 0x67452301U;
    ctx->state[1] = 0xEFCDAB89U;
    ctx->state[2] = 0x98BADCFEU;
    ctx->state[3] = 0x10325476U;
    ctx->total_bits = 0;
    ctx->buffer_len = 0;
}

/* Послідовне оновлення хеша покомпонентно */
void md_update(md_ctx_t *ctx, const uint8_t *data, size_t len) {
    ctx->total_bits += ((uint64_t)len * 8);

    for (size_t i = 0; i < len; i++) {
        ctx->buffer[ctx->buffer_len++] = data[i];
        if (ctx->buffer_len == BLOCK_SIZE) {
            md_compress(ctx->state, ctx->buffer);
            ctx->buffer_len = 0;
        }
    }
}

/* Завершення обчислення хеша: підкладка, додавання довжини та фінальне стиснення */
void md_final(md_ctx_t *ctx, uint8_t digest[16]) {
    /* Байт 0x80 позначає початок підкладки */
    ctx->buffer[ctx->buffer_len++] = 0x80;

    /* Якщо в блоці не вистачає місця для 8 байтів довжини */
    if (ctx->buffer_len > 56) {
        while (ctx->buffer_len < BLOCK_SIZE) {
            ctx->buffer[ctx->buffer_len++] = 0x00;
        }
        md_compress(ctx->state, ctx->buffer);
        ctx->buffer_len = 0;
    }

    /* Доповнення нулями до 56 байтів */
    while (ctx->buffer_len < 56) {
        ctx->buffer[ctx->buffer_len++] = 0x00;
    }

    /* Запис 64-бітової довжини повідомлення у бітах (Little-Endian) */
    uint64_t bits = ctx->total_bits;
    for (int i = 0; i < 8; i++) {
        ctx->buffer[56 + i] = (uint8_t)(bits >> (i * 8));
    }

    md_compress(ctx->state, ctx->buffer);

    /* Формування фінального 16-байтового відбитка */
    for (int i = 0; i < 4; i++) {
        digest[i * 4]     = (uint8_t)(ctx->state[i]);
        digest[i * 4 + 1] = (uint8_t)(ctx->state[i] >> 8);
        digest[i * 4 + 2] = (uint8_t)(ctx->state[i] >> 16);
        digest[i * 4 + 3] = (uint8_t)(ctx->state[i] >> 24);
    }
}

/* Реалізація захищеного підпису HMAC */
void hmac_md(const uint8_t *key, size_t key_len, const uint8_t *msg, size_t msg_len, uint8_t out[16]) {
    uint8_t k_padded[BLOCK_SIZE] = {0};

    if (key_len > BLOCK_SIZE) {
        md_ctx_t k_ctx;
        md_init(&k_ctx);
        md_update(&k_ctx, key, key_len);
        md_final(&k_ctx, k_padded);
    } else {
        memcpy(k_padded, key, key_len);
    }

    uint8_t i_key[BLOCK_SIZE];
    uint8_t o_key[BLOCK_SIZE];

    for (int i = 0; i < BLOCK_SIZE; i++) {
        i_key[i] = k_padded[i] ^ 0x36;
        o_key[i] = k_padded[i] ^ 0x5C;
    }

    /* Внутрішній крок: H((K ⊕ ipad) || M) */
    uint8_t inner_digest[16];
    md_ctx_t ctx;
    md_init(&ctx);
    md_update(&ctx, i_key, BLOCK_SIZE);
    md_update(&ctx, msg, msg_len);
    md_final(&ctx, inner_digest);

    /* Зовнішній крок: H((K ⊕ opad) || inner_digest) */
    md_init(&ctx);
    md_update(&ctx, o_key, BLOCK_SIZE);
    md_update(&ctx, inner_digest, 16);
    md_final(&ctx, out);
}

int main(void) {
    const char *message = "action=transfer&amount=100";
    md_ctx_t ctx;
    uint8_t digest[16];

    md_init(&ctx);
    md_update(&ctx, (const uint8_t*)message, strlen(message));
    md_final(&ctx, digest);

    printf("Хеш вхідного повідомлення: ");
    for (int i = 0; i < 16; i++) printf("%02x", digest[i]);
    printf("\n");

    uint8_t hmac_out[16];
    const char *key = "secret_key";
    hmac_md((const uint8_t*)key, strlen(key), (const uint8_t*)message, strlen(message), hmac_out);
    printf("HMAC захищений підпис:     ");
    for (int i = 0; i < 16; i++) printf("%02x", hmac_out[i]);
    printf("\n");

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <string_view>
#include <cstdint>
#include <iomanip>
#include <bit>
#include <span>

/*
 * Ідіоматична C++20 реалізація хеш-функції Меркле — Дамґорда.
 * Використовує std::span для безпечної обробки пам'яті, std::array для фіксованих буферів,
 * та std::rotl для гарантованого циклічного зсуву.
 */
class MerkleDamgardHash {
public:
    static constexpr size_t BlockSize = 64;
    static constexpr size_t DigestSize = 16;

    MerkleDamgardHash() { reset(); }

    void reset() noexcept {
        m_state = {0x67452301U, 0xEFCDAB89U, 0x98BADCFEU, 0x10325476U};
        m_totalBits = 0;
        m_bufferLen = 0;
    }

    void update(std::span<const std::uint8_t> data) noexcept {
        m_totalBits += static_cast<std::uint64_t>(data.size()) * 8;
        for (std::uint8_t byte : data) {
            m_buffer[m_bufferLen++] = byte;
            if (m_bufferLen == BlockSize) {
                compress(m_buffer.data());
                m_bufferLen = 0;
            }
        }
    }

    void update(std::string_view str) noexcept {
        update(std::span{reinterpret_cast<const std::uint8_t*>(str.data()), str.size()});
    }

    [[nodiscard]] std::array<std::uint8_t, DigestSize> finalize() noexcept {
        m_buffer[m_bufferLen++] = 0x80;
        if (m_bufferLen > 56) {
            while (m_bufferLen < BlockSize) m_buffer[m_bufferLen++] = 0x00;
            compress(m_buffer.data());
            m_bufferLen = 0;
        }
        while (m_bufferLen < 56) m_buffer[m_bufferLen++] = 0x00;

        for (size_t i = 0; i < 8; ++i) {
            m_buffer[56 + i] = static_cast<std::uint8_t>(m_totalBits >> (i * 8));
        }
        compress(m_buffer.data());

        std::array<std::uint8_t, DigestSize> digest{};
        for (size_t i = 0; i < 4; ++i) {
            digest[i * 4 + 0] = static_cast<std::uint8_t>(m_state[i] >> 0);
            digest[i * 4 + 1] = static_cast<std::uint8_t>(m_state[i] >> 8);
            digest[i * 4 + 2] = static_cast<std::uint8_t>(m_state[i] >> 16);
            digest[i * 4 + 3] = static_cast<std::uint8_t>(m_state[i] >> 24);
        }
        return digest;
    }

    /* Можливість встановити внутрішній стан для демонстрації атаки подовження */
    void setState(const std::array<std::uint32_t, 4>& state, std::uint64_t totalBits) noexcept {
        m_state = state;
        m_totalBits = totalBits;
        m_bufferLen = 0;
    }

private:
    void compress(const std::uint8_t* block) noexcept {
        std::array<std::uint32_t, 16> w{};
        for (size_t i = 0; i < 16; ++i) {
            w[i] = static_cast<std::uint32_t>(block[i * 4 + 0]) |
                  (static_cast<std::uint32_t>(block[i * 4 + 1]) << 8) |
                  (static_cast<std::uint32_t>(block[i * 4 + 2]) << 16) |
                  (static_cast<std::uint32_t>(block[i * 4 + 3]) << 24);
        }

        auto [a, b, c, d] = m_state;
        for (size_t r = 0; r < 16; ++r) {
            std::uint32_t f = (b & c) ^ (~b & d);
            std::uint32_t temp = a + f + w[r] + 0x5A827999U;
            a = d; d = c; c = b;
            b = b + std::rotl(temp, 7);
        }
        m_state[0] += a; m_state[1] += b;
        m_state[2] += c; m_state[3] += d;
    }

    std::array<std::uint32_t, 4> m_state{};
    std::uint64_t m_totalBits{0};
    std::array<std::uint8_t, BlockSize> m_buffer{};
    size_t m_bufferLen{0};
};

/* Захищена побудова автентифікації повідомлень HMAC у C++ */
class HmacBuilder {
public:
    static std::array<std::uint8_t, MerkleDamgardHash::DigestSize>
    compute(std::span<const std::uint8_t> key, std::span<const std::uint8_t> message) {
        std::array<std::uint8_t, MerkleDamgardHash::BlockSize> kPadded{};

        if (key.size() > MerkleDamgardHash::BlockSize) {
            MerkleDamgardHash hasher;
            hasher.update(key);
            auto d = hasher.finalize();
            std::copy(d.begin(), d.end(), kPadded.begin());
        } else {
            std::copy(key.begin(), key.end(), kPadded.begin());
        }

        std::array<std::uint8_t, MerkleDamgardHash::BlockSize> ipad{}, opad{};
        for (size_t i = 0; i < MerkleDamgardHash::BlockSize; ++i) {
            ipad[i] = kPadded[i] ^ 0x36;
            opad[i] = kPadded[i] ^ 0x5C;
        }

        MerkleDamgardHash hasher;
        hasher.update(ipad);
        hasher.update(message);
        auto innerDigest = hasher.finalize();

        hasher.reset();
        hasher.update(opad);
        hasher.update(innerDigest);
        return hasher.finalize();
    }
};

int main() {
    std::string_view msg = "action=transfer&amount=100";
    MerkleDamgardHash hasher;
    hasher.update(msg);
    auto digest = hasher.finalize();

    std::cout << "Хеш вхідного повідомлення: ";
    for (auto b : digest) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(b);
    }
    std::cout << "\n";

    std::string_view key = "secret_key";
    auto hmac = HmacBuilder::compute(
        std::span{reinterpret_cast<const std::uint8_t*>(key.data()), key.size()},
        std::span{reinterpret_cast<const std::uint8_t*>(msg.data()), msg.size()}
    );

    std::cout << "HMAC захищений підпис:     ";
    for (auto b : hmac) {
        std::cout << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(b);
    }
    std::cout << "\n";

    return 0;
}
```
:::

## Покроковий розбір аналізу вразливостей та захисту

1. **Як працює атака подовження:**
   При використанні схеми `H(key || message)` супротивник отримує підписане повідомлення `"action=transfer&amount=100"` та відповідний відбиток `digest`.
   Оскільки відбиток `digest` дорівнює чотирьом 32-бітовим словам стану `m_state` наприкінці обробки, супротивник може розпакувати `digest` назад у `(state[0]...state[3])`.
   Створивши новий екземпляр хешера та викликавши `setState(digest, total_bits_with_padding)`, супротивник може додати байтовий рядок `&admin=true`.
   Підсумковий хеш буде абсолютно валідним для скомплектованого файлу `key || message || padding || &admin=true`, хоча ключ `key` атакуючий не знав!

2. **Чому HMAC гарантує захист:**
   У конструкції `HMAC` вхідні дані проходять двократну обробку з різними блоками ключа `(K ⊕ ipad)` та `(K ⊕ opad)`.
   Зовнішній крок хешування `H((K ⊕ opad) || inner_digest)` приймає внутрішній відбиток як дані й пропускає його через ще одну функцію стиснення.
   Результат `HMAC` більше не збігається з внутрішнім станом `state` первинного хешування повідомлення `M`, що робить підновлення стану для атаки подовження обчислювально неможливим.
