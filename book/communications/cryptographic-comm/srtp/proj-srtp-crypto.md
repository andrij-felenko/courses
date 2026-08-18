# ⚙️ Реалізація криптографічного ядра SRTP: індекс, ROC, антиповтор і KDF

Розробка надійного та високопродуктивного рушія SRTP для вбудованих систем, медіасерверів або VoIP-клієнтів вимагає точної реалізації чотирьох тісно пов'язаних криптографічних компонентів: функції виведення сесійних ключів (KDF), відстеження 48-бітного індексу пакета з лічильником переповнень (ROC), ковзного вікна захисту від повторного відтворення та конвеєра шифрування й верифікації за схемою Encrypt-then-MAC.

Усі обчислення виконуються в умовах суворих часових обмежень: на обробку одного пакета медіапотоку аудіо або відео відводиться не більше кількох десятків мікросекунд, причому операції не повинні створювати витоків через час виконання (Timing Attacks).

---

## 1. Розрахунок 48-бітного індексу пакета та супровід лічильника ROC

Головний виклик у реалізації прийому [RTP](book:communications/rtp-rtcp) полягає в тому, що протокол передається через [UDP](book:communications/tcp-vs-udp), де пакети можуть запізнюватися, дублюватися або приходити в переплутаному порядку. При цьому 16-бітний номер послідовності `SEQ` переповнюється кожні 65 536 пакетів. Для стандартного голосового потоку Opus із фреймами по 20 мілісекунд (50 пакетів на секунду) переповнення стається кожні 21.8 хвилини. Для відеопотоку 4K з частотою 60 кадрів на секунду та фрагментацією великих кадрів на кілька датаграм переповнення лічильника наступає менш ніж за хвилину.

Якби шифрування AES-CTR спиралося виключно на 16-бітний номер `SEQ`, то після кожного переповнення вектор ініціалізації `IV` повторювався б. У режимі лічильника повторне використання пари (Key, IV) для шифрування двох різних повідомлень призводить до катастрофічного витоку: побітове додавання двох шифротекстів `C₁ ⊕ C₂` повністю знищує гаму й дає відкритий результат `P₁ ⊕ P₂`, з якого легко відновити початковий звук або відео.

Для збереження абсолютної унікальності вектора ініціалізації отримувач розгортає 16-бітний `SEQ` у повний 48-бітний абсолютний індекс пакета `i`:

```text
i = 2¹⁶ · ROC + SEQ
```

### Алгоритм оцінки значення ROC при порушенні порядку доставки

Отримувач зберігає два стани: `s_l` — найвищий підтверджений номер послідовності, та `ROC` — поточний 32-бітний лічильник переповнень. Коли надходить новий номер `SEQ`, оцінка `ROC_est` обчислюється за правилами модульної арифметики на кільці `2¹⁶`.

Основна складність виникає на межі переходу `65535 → 0`. Якщо отримувач перебуває в стані `s_l = 65534`, а через затримку в мережі надходить запізнілий пакет з номером `SEQ = 65530`, він належить поточній епосі (`ROC`). Якщо ж надходить пакет `SEQ = 2`, це означає, що потік перетнув межу переповнення, і цей пакет належить наступній епосі (`ROC + 1`). Зворотна ситуація виникає, коли першим приходить пакет нової епохи `SEQ = 1` (стан стає `s_l = 1`, `ROC = 1`), а слідом за ним приходить запізнілий пакет старої епохи `SEQ = 65533`: його треба розшифрувати з попереднім значенням `ROC - 1`.

Поріг розрізнення встановлено на половині діапазону лічильника — `2¹⁵ = 32768`.

```text
Якщо s_l < 32768:
    Якщо (SEQ - s_l) > 32768:
        ROC_est = ROC - 1 (якщо ROC > 0)
    Інакше:
        ROC_est = ROC

Якщо s_l >= 32768:
    Якщо (s_l - SEQ) > 32768:
        ROC_est = ROC + 1
    Інакше:
        ROC_est = ROC
```

### Реалізація розрахунку індексу та оновлення стану ROC

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint32_t roc;      /* Лічильник переповнень (Rollover Counter) */
    uint16_t s_l;      /* Найвищий підтверджений номер послідовності */
    bool initialized;  /* Прапорець отримання першого пакета */
} srtp_roc_state_t;

/* Оцінка 48-бітного індексу без зміни внутрішнього стану */
uint64_t srtp_estimate_index(const srtp_roc_state_t *state, uint16_t seq, uint32_t *out_roc) {
    if (!state->initialized) {
        if (out_roc) *out_roc = 0;
        return (uint64_t)seq;
    }

    uint32_t roc_est = state->roc;
    if (state->s_l < 32768) {
        if ((uint16_t)(seq - state->s_l) > 32768) {
            roc_est = (state->roc > 0) ? state->roc - 1 : 0;
        }
    } else {
        if ((uint16_t)(state->s_l - seq) > 32768) {
            roc_est = state->roc + 1;
        }
    }

    if (out_roc) *out_roc = roc_est;
    return (((uint64_t)roc_est) << 16) | seq;
}

/* Фіксація нового підтвердженого номера після перевірки автентичності */
void srtp_update_roc_state(srtp_roc_state_t *state, uint16_t seq, uint32_t roc_est) {
    if (!state->initialized) {
        state->s_l = seq;
        state->roc = roc_est;
        state->initialized = true;
        return;
    }

    uint64_t new_idx = (((uint64_t)roc_est) << 16) | seq;
    uint64_t cur_idx = (((uint64_t)state->roc) << 16) | state->s_l;

    if (new_idx > cur_idx) {
        state->s_l = seq;
        state->roc = roc_est;
    }
}
```
```cpp
#include <cstdint>
#include <optional>
#include <algorithm>

class RocTracker {
public:
    struct Estimate {
        std::uint64_t index;
        std::uint32_t roc;
    };

    [[nodiscard]] Estimate estimate_index(std::uint16_t seq) const noexcept {
        if (!initialized_) {
            return { static_cast<std::uint64_t>(seq), 0 };
        }

        std::uint32_t roc_est = roc_;
        if (s_l_ < 32768) {
            if (static_cast<std::uint16_t>(seq - s_l_) > 32768) {
                roc_est = (roc_ > 0) ? (roc_ - 1) : 0;
            }
        } else {
            if (static_cast<std::uint16_t>(s_l_ - seq) > 32768) {
                roc_est = roc_ + 1;
            }
        }

        const std::uint64_t idx = (static_cast<std::uint64_t>(roc_est) << 16) | seq;
        return { idx, roc_est };
    }

    void update(std::uint16_t seq, std::uint32_t roc_est) noexcept {
        if (!initialized_) {
            s_l_ = seq;
            roc_ = roc_est;
            initialized_ = true;
            return;
        }

        const std::uint64_t new_idx = (static_cast<std::uint64_t>(roc_est) << 16) | seq;
        const std::uint64_t cur_idx = (static_cast<std::uint64_t>(roc_) << 16) | s_l_;

        if (new_idx > cur_idx) {
            s_l_ = seq;
            roc_ = roc_est;
        }
    }

    [[nodiscard]] bool is_initialized() const noexcept { return initialized_; }
    [[nodiscard]] std::uint32_t current_roc() const noexcept { return roc_; }
    [[nodiscard]] std::uint16_t highest_seq() const noexcept { return s_l_; }

private:
    std::uint32_t roc_{0};
    std::uint16_t s_l_{0};
    bool initialized_{false};
};
```
:::

---

## 2. Ковзне вікно захисту від повторного відтворення (Replay Window)

Для захисту від атак повторного відтворення (Replay Attack) отримувач підтримує 64-бітну або 128-бітну бітову маску отриманих пакетів. Якщо зловмисник перехоплює дійсний зашифрований аудіопакет і відправляє його повторно, вікно виявляє дублікат і негайно скидає пакет без витрат часу на розшифрування.

Зберігати список усіх коли-небудь отриманих індексів у пам'яті неможливо, оскільки тривала сесія генерує сотні мільйонів пакетів. Замість цього використовується компактна бітова маска, прив'язана до найвищого зареєстрованого індексу `max_index`.

```text
       <- старші пакети (відкинуто)       новіші пакети ->
[ ... 0 1 1 0 1 1 1 1 1 1 1 1 1 1 1 1 ] [ Найвищий індекс: max_idx ]
  |<-         Вікно 64 біти         ->|
```

Коли надходить пакет з індексом `i`:
1. Якщо `i > max_index`: пакет вважається новішим за всі попередні. Бітова маска зсувається ліворуч на величину різниці `(i - max_index)`, молодший біт встановлюється в `1`, а `max_index` оновлюється.
2. Якщо `i <= max_index`: обчислюється зміщення `diff = max_index - i`. Якщо `diff >= 64`, пакет вважається занадто старим (випав за ліву межу вікна) і відкидається. Якщо `diff < 64`, перевіряється біт на позиції `diff`. Якщо біт дорівнює `1`, це повторний дублікат (скидання). Якщо біт дорівнює `0`, пакет приймається, і біт виставляється в `1`.

### Реалізація 64-бітного вікна антиповтору

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>

#define SRTP_REPLAY_WINDOW_SIZE 64

typedef enum {
    SRTP_REPLAY_OK = 0,
    SRTP_REPLAY_DUPLICATE = 1,
    SRTP_REPLAY_OLD = 2
} srtp_replay_status_t;

typedef struct {
    uint64_t max_index;    /* Найвищий успішно автентифікований індекс */
    uint64_t window_mask;  /* Бітова маска (біт 0 = max_index - 63) */
    bool initialized;
} srtp_replay_window_t;

srtp_replay_status_t srtp_check_replay(const srtp_replay_window_t *w, uint64_t index) {
    if (!w->initialized) {
        return SRTP_REPLAY_OK;
    }

    if (index > w->max_index) {
        return SRTP_REPLAY_OK; /* Новий пакет випереджає вікно */
    }

    uint64_t diff = w->max_index - index;
    if (diff >= SRTP_REPLAY_WINDOW_SIZE) {
        return SRTP_REPLAY_OLD; /* Занадто старий пакет поза межами вікна */
    }

    if ((w->window_mask & (1ULL << diff)) != 0) {
        return SRTP_REPLAY_DUPLICATE; /* Цей пакет уже було оброблено */
    }

    return SRTP_REPLAY_OK;
}

void srtp_update_replay(srtp_replay_window_t *w, uint64_t index) {
    if (!w->initialized) {
        w->max_index = index;
        w->window_mask = 1ULL;
        w->initialized = true;
        return;
    }

    if (index > w->max_index) {
        uint64_t shift = index - w->max_index;
        if (shift < SRTP_REPLAY_WINDOW_SIZE) {
            w->window_mask <<= shift;
        } else {
            w->window_mask = 0;
        }
        w->window_mask |= 1ULL;
        w->max_index = index;
    } else {
        uint64_t diff = w->max_index - index;
        if (diff < SRTP_REPLAY_WINDOW_SIZE) {
            w->window_mask |= (1ULL << diff);
        }
    }
}
```
```cpp
#include <cstdint>
#include <optional>

enum class ReplayStatus {
    Ok,
    Duplicate,
    Old
};

class ReplayWindow {
public:
    static constexpr std::uint64_t WindowSize = 64;

    [[nodiscard]] ReplayStatus check(std::uint64_t index) const noexcept {
        if (!initialized_) {
            return ReplayStatus::Ok;
        }

        if (index > max_index_) {
            return ReplayStatus::Ok;
        }

        const std::uint64_t diff = max_index_ - index;
        if (diff >= WindowSize) {
            return ReplayStatus::Old;
        }

        if ((window_mask_ & (1ULL << diff)) != 0) {
            return ReplayStatus::Duplicate;
        }

        return ReplayStatus::Ok;
    }

    void update(std::uint64_t index) noexcept {
        if (!initialized_) {
            max_index_ = index;
            window_mask_ = 1ULL;
            initialized_ = true;
            return;
        }

        if (index > max_index_) {
            const std::uint64_t shift = index - max_index_;
            if (shift < WindowSize) {
                window_mask_ <<= shift;
            } else {
                window_mask_ = 0;
            }
            window_mask_ |= 1ULL;
            max_index_ = index;
        } else {
            const std::uint64_t diff = max_index_ - index;
            if (diff < WindowSize) {
                window_mask_ |= (1ULL << diff);
            }
        }
    }

    [[nodiscard]] std::uint64_t max_index() const noexcept { return max_index_; }

private:
    std::uint64_t max_index_{0};
    std::uint64_t window_mask_{0};
    bool initialized_{false};
};
```
:::

---

## 3. Генерація сесійних ключів (SRTP KDF)

Функція KDF бере 128-бітний майстер-ключ та 112-бітну майстер-сіль і виробляє три робочі ключі:
1. `k_e` (16 байтів) — ключ шифрування AES-CTR.
2. `k_a` (20 байтів) — ключ автентифікації HMAC-SHA1.
3. `k_s` (14 байтів) — сесійна сіль для розрахунку векторів IV.

Функція деривації запускає AES у режимі лічильника, використовуючи майстер-ключ. Вхідний 16-байтовий блок формується з майстер-солі, в яку вбудовано 1-байтову мітку `label` (`0x00` для шифрування, `0x01` для автентифікації, `0x02` для солі) та 16-бітний внутрішній лічильник блоків. Оскільки ключ автентифікації SHA-1 має довжину 20 байтів, KDF генерує два послідовні 16-байтові блоки AES (із лічильниками `0x0000` та `0x0001`) і бере перші 20 байтів з результуючого 32-байтового буфера.

### Доведення криптографічної стійкості AES-CTR PRF

Функція виведення ключів KDF у стандарті RFC 3711 спирається на той факт, що блоковий шифр AES є псевдовипадковою перестановкою (PRP). Оскільки простір можливих входів лічильника `IV_kdf` для різних міток `label` (0x00..0x05) є взаємно неперетинним, послідовності вихідних блоків AES під таємним `Master Key` є статистично незалежними одна від одної.

Ймовірність розрізнення згенерованого потоку від ідеально випадкового шуму обмежена величиною `O(q² / 2¹²⁸)`, де `q` — кількість згенерованих 16-байтових блоків. Оскільки для однієї сесії KDF генерує менше десяти блоків (для `k_e`, `k_a`, `k_s`), перевага будь-якого поліноміального супротивника становить менше `10⁻³⁶`, що забезпечує бездоганну криптографічну міцність.

### Гарантоване очищення пам'яті та захист від оптимізацій компілятора

Очищення таємних ключів після завершення виклику є критичною вимогою безпеки. Стандартні виклики `memset(key, 0, len)` часто ігноруються або видаляються оптимізатором компілятора (Dead Store Elimination), якщо компілятор виявляє, що буфер `key` більше ніде не читається перед звільненням пам'яті.

Для запобігання цьому застосовуються спеціалізовані бар'єри пам'яті:
- В OpenSSL: функція `OPENSSL_cleanse()`, реалізована асемблерними інструкціями або через покажчик на `volatile`.
- У стандарті C23: функція `memset_explicit()`.
- У чистому C++: виклик `std::atomic_thread_fence()` або затирання через покажчик `volatile uint8_t*`, що змушує компілятор згенерувати дійсні інструкції запису в пам'ять.
- На рівні процесорних регістрів SIMD: при використанні інструкцій AES-NI проміжні розширені ключі зберігаються у 128-бітних регістрах `XMM0..XMM15` або 256-бітних `YMM`. Їхнє очищення вимагає явного завантаження нульових векторів за допомогою макросів `_mm_setzero_si128()` або виклику `_mm256_zeroupper()`, щоб запобігти витоку ключів через перемикання контексту ядра або інспекцію реєстрів.

### Реалізація KDF на базі псевдовипадкової функції AES-CTR

:::tabs
```c
#include <stdint.h>
#include <string.h>
#include <openssl/aes.h>

#define SRTP_LABEL_ENCRYPT 0x00
#define SRTP_LABEL_AUTH    0x01
#define SRTP_LABEL_SALT    0x02

typedef struct {
    uint8_t enc_key[16];   /* k_e */
    uint8_t auth_key[20];  /* k_a */
    uint8_t salt_key[14];  /* k_s */
} srtp_session_keys_t;

/* Генерація псевдовипадкового потоку за міткою Label */
static void srtp_kdf_derive(const AES_KEY *aes_ctx, const uint8_t *master_salt,
                            uint8_t label, uint8_t *out_key, size_t out_len) {
    uint8_t iv[16];
    memcpy(iv, master_salt, 14);
    iv[14] = 0;
    iv[15] = 0;

    /* Вбудовування 1-байтової мітки Label у 7-й байт солі (RFC 3711) */
    iv[7] ^= label;

    uint8_t keystream[32];
    size_t generated = 0;
    uint16_t block_counter = 0;

    while (generated < out_len) {
        iv[14] = (uint8_t)(block_counter >> 8);
        iv[15] = (uint8_t)(block_counter & 0xFF);

        AES_encrypt(iv, &keystream[generated], aes_ctx);
        generated += 16;
        block_counter++;
    }

    memcpy(out_key, keystream, out_len);
}

int srtp_derive_session_keys(const uint8_t *master_key, const uint8_t *master_salt,
                             srtp_session_keys_t *keys) {
    AES_KEY aes_ctx;
    if (AES_set_encrypt_key(master_key, 128, &aes_ctx) != 0) {
        return -1;
    }

    /* Генерація трьох незалежних сесійних ключів */
    srtp_kdf_derive(&aes_ctx, master_salt, SRTP_LABEL_ENCRYPT, keys->enc_key, 16);
    srtp_kdf_derive(&aes_ctx, master_salt, SRTP_LABEL_AUTH, keys->auth_key, 20);
    srtp_kdf_derive(&aes_ctx, master_salt, SRTP_LABEL_SALT, keys->salt_key, 14);

    return 0;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <cstring>
#include <expected>
#include <openssl/aes.h>

struct SessionKeys {
    std::array<std::uint8_t, 16> enc_key{};   // k_e (128 біт)
    std::array<std::uint8_t, 20> auth_key{};  // k_a (160 біт)
    std::array<std::uint8_t, 14> salt_key{};  // k_s (112 біт)
};

enum class KdfError {
    AesKeyInitFailed
};

class SrtpKdf {
public:
    static constexpr std::uint8_t LabelEncrypt = 0x00;
    static constexpr std::uint8_t LabelAuth    = 0x01;
    static constexpr std::uint8_t LabelSalt    = 0x02;

    static std::expected<SessionKeys, KdfError> derive(
        std::span<const std::uint8_t, 16> master_key,
        std::span<const std::uint8_t, 14> master_salt) noexcept {
        
        AES_KEY aes_ctx{};
        if (AES_set_encrypt_key(master_key.data(), 128, &aes_ctx) != 0) {
            return std::unexpected(KdfError::AesKeyInitFailed);
        }

        SessionKeys keys{};
        derive_key(aes_ctx, master_salt, LabelEncrypt, keys.enc_key);
        derive_key(aes_ctx, master_salt, LabelAuth, keys.auth_key);
        derive_key(aes_ctx, master_salt, LabelSalt, keys.salt_key);

        return keys;
    }

private:
    static void derive_key(const AES_KEY& aes_ctx,
                           std::span<const std::uint8_t, 14> master_salt,
                           std::uint8_t label,
                           std::span<std::uint8_t> out_buf) noexcept {
        std::array<std::uint8_t, 16> iv{};
        std::memcpy(iv.data(), master_salt.data(), 14);
        iv[7] ^= label;

        std::array<std::uint8_t, 32> keystream{};
        std::size_t generated = 0;
        std::uint16_t block_counter = 0;

        while (generated < out_buf.size()) {
            iv[14] = static_cast<std::uint8_t>(block_counter >> 8);
            iv[15] = static_cast<std::uint8_t>(block_counter & 0xFF);

            AES_encrypt(iv.data(), &keystream[generated], &aes_ctx);
            generated += 16;
            ++block_counter;
        }

        std::memcpy(out_buf.data(), keystream.data(), out_buf.size());
    }
};
```
:::

---

## 4. Конвеєр шифрування (Protect) та дешифрування (Unprotect)

Повний конвеєр обробки пакета SRTP об'єднує генерацію вектора IV, накладання гами AES-CTR на корисне навантаження та обчислення усіченого тега HMAC-SHA1-80 (10 байтів) поверх заголовка, шифротексту та лічильника ROC.

Критично важливо дотримуватися схеми Encrypt-then-MAC. На відміну від застарілої схеми MAC-then-Encrypt (де спершу обчислювався підпис, а потім усе разом шифрувалося), Encrypt-then-MAC дозволяє отримувачу перевірити цілісність датаграми **до того**, як блок розшифрування торкнеться даних. Якщо пакет пошкоджено в мережі або модифіковано зловмисником, він негайно скидається після перевірки HMAC, що захищає систему від атак на базі оракулів дешифрування (Padding Oracle Attacks).

Під час дешифрування (Unprotect) отримувач виконує кроки у строгому зворотному порядку:
1. Оцінює індекс `i` та `ROC_est` за номером `SEQ`.
2. Перевіряє індекс у ковзному вікні антиповтору.
3. Обчислює контрольний тег HMAC-SHA1 з використанням `ROC_est` і порівнює його з тегом у трейлері пакета в режимі константного часу (`CRYPTO_memcmp`).
4. Якщо автентифікація успішна, розшифровує корисне навантаження та фіксує новий стан вікна й лічильника переповнень.

### Робота з некратними довжинами корисного навантаження (Fractional Keystream)

Особливістю голосових кодеків (таких як Opus або AMR) є змінна довжина закодованого аудіокадру: наприклад, розмір корисного навантаження може становити 87 або 133 байти, що не ділиться на 16-байтовий розмір блоку AES. У режимі лічильника (CTR) це не вимагає жодного доповнення (Padding):
- Для зашифрування 87 байтів генеруються 6 повних блоків AES (96 байтів гами).
- Перші 80 байтів шифрують перші 5 повних блоків навантаження.
- З шостого 16-байтового блоку гами беруться лише перші 7 байтів, які додаються побітово `XOR` до 7 байтів залишку даних, а решта 9 байтів згенерованої гами просто відкидаються.
- Довжина зашифрованого медіапотоку залишається рівно 87 байтів, не змінюючи вирівнювання пам'яті в мережевому буфері.

### Реалізація повного конвеєра SRTP Protect та Unprotect

:::tabs
```c
#include <stdint.h>
#include <string.h>
#include <openssl/aes.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>

/* Побудова 128-бітного вектора IV для AES-CTR */
static void srtp_build_iv(const uint8_t *salt, uint32_t ssrc, uint64_t index, uint8_t *iv) {
    memcpy(iv, salt, 14);
    iv[14] = 0;
    iv[15] = 0;

    /* IV = (Salt << 16) ^ (SSRC << 64) ^ (Index << 16) */
    iv[4] ^= (uint8_t)(ssrc >> 24);
    iv[5] ^= (uint8_t)(ssrc >> 16);
    iv[6] ^= (uint8_t)(ssrc >> 8);
    iv[7] ^= (uint8_t)(ssrc & 0xFF);

    for (int b = 0; b < 6; ++b) {
        iv[8 + b] ^= (uint8_t)((index >> (8 * (5 - b))) & 0xFF);
    }
}

/* Шифрування корисного навантаження та додавання тега автентифікації */
int srtp_protect_packet(const srtp_session_keys_t *keys,
                        uint8_t *rtp_packet, size_len_t header_len, size_t payload_len,
                        uint32_t ssrc, uint64_t index, uint32_t roc,
                        size_t *out_total_len) {
    uint8_t iv[16];
    srtp_build_iv(keys->salt_key, ssrc, index, iv);

    AES_KEY aes_ctx;
    if (AES_set_encrypt_key(keys->enc_key, 128, &aes_ctx) != 0) {
        return -1;
    }

    /* Шифрування Payload у режимі AES-CTR */
    uint8_t ecount_buf[16] = {0};
    unsigned int num = 0;
    AES_ctr128_encrypt(rtp_packet + header_len, rtp_packet + header_len,
                       payload_len, &aes_ctx, iv, ecount_buf, &num);

    /* Обчислення HMAC-SHA1 поверх [Header || Encrypted_Payload || ROC] */
    uint8_t mac_out[32];
    unsigned int mac_len = 0;
    HMAC_CTX *hmac = HMAC_CTX_new();
    if (!hmac) return -1;

    HMAC_Init_ex(hmac, keys->auth_key, 20, EVP_sha1(), NULL);
    HMAC_Update(hmac, rtp_packet, header_len + payload_len);

    uint8_t roc_be[4] = {
        (uint8_t)(roc >> 24), (uint8_t)(roc >> 16),
        (uint8_t)(roc >> 8),  (uint8_t)(roc & 0xFF)
    };
    HMAC_Update(hmac, roc_be, 4);
    HMAC_Final(hmac, mac_out, &mac_len);
    HMAC_CTX_free(hmac);

    /* Додавання усіченого 80-бітного тега (10 байтів) у трейлер */
    memcpy(rtp_packet + header_len + payload_len, mac_out, 10);
    *out_total_len = header_len + payload_len + 10;

    return 0;
}

/* Верифікація підпису та дешифрування вхідного пакета */
int srtp_unprotect_packet(const srtp_session_keys_t *keys,
                          uint8_t *packet, size_t total_len, size_t header_len,
                          uint32_t ssrc, uint64_t index, uint32_t roc_est,
                          size_t *out_payload_len) {
    if (total_len < header_len + 10) {
        return -1;
    }
    size_t payload_len = total_len - header_len - 10;
    const uint8_t *received_tag = packet + header_len + payload_len;

    /* 1. Обчислення контрольного підпису HMAC-SHA1 */
    uint8_t mac_calc[32];
    unsigned int mac_len = 0;
    HMAC_CTX *hmac = HMAC_CTX_new();
    if (!hmac) return -1;

    HMAC_Init_ex(hmac, keys->auth_key, 20, EVP_sha1(), NULL);
    HMAC_Update(hmac, packet, header_len + payload_len);

    uint8_t roc_be[4] = {
        (uint8_t)(roc_est >> 24), (uint8_t)(roc_est >> 16),
        (uint8_t)(roc_est >> 8),  (uint8_t)(roc_est & 0xFF)
    };
    HMAC_Update(hmac, roc_be, 4);
    HMAC_Final(hmac, mac_calc, &mac_len);
    HMAC_CTX_free(hmac);

    /* 2. Константне порівняння тега автентифікації */
    if (CRYPTO_memcmp(received_tag, mac_calc, 10) != 0) {
        return -2; /* Помилка автентифікації */
    }

    /* 3. Дешифрування корисного навантаження */
    uint8_t iv[16];
    srtp_build_iv(keys->salt_key, ssrc, index, iv);

    AES_KEY aes_ctx;
    if (AES_set_encrypt_key(keys->enc_key, 128, &aes_ctx) != 0) {
        return -3;
    }

    uint8_t ecount_buf[16] = {0};
    unsigned int num = 0;
    AES_ctr128_encrypt(packet + header_len, packet + header_len,
                       payload_len, &aes_ctx, iv, ecount_buf, &num);

    *out_payload_len = payload_len;
    return 0;
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <cstring>
#include <memory>
#include <expected>
#include <openssl/aes.h>
#include <openssl/hmac.h>
#include <openssl/crypto.h>

enum class ProtectError {
    AesInitFailed,
    HmacInitFailed
};

enum class UnprotectError {
    PacketTooShort,
    AuthFailed,
    AesInitFailed,
    HmacInitFailed
};

struct HmacCtxDeleter {
    void operator()(HMAC_CTX* ctx) const noexcept {
        if (ctx) HMAC_CTX_free(ctx);
    }
};
using UniqueHmacCtx = std::unique_ptr<HMAC_CTX, HmacCtxDeleter>;

class SrtpPipeline {
public:
    static std::expected<std::size_t, ProtectError> protect(
        const SessionKeys& keys,
        std::span<std::uint8_t> rtp_buffer,
        std::size_t header_len,
        std::size_t payload_len,
        std::uint32_t ssrc,
        std::uint64_t index,
        std::uint32_t roc) noexcept {

        if (rtp_buffer.size() < header_len + payload_len + 10) {
            return std::unexpected(ProtectError::HmacInitFailed);
        }

        std::array<std::uint8_t, 16> iv{};
        build_iv(keys.salt_key, ssrc, index, iv);

        AES_KEY aes_ctx{};
        if (AES_set_encrypt_key(keys.enc_key.data(), 128, &aes_ctx) != 0) {
            return std::unexpected(ProtectError::AesInitFailed);
        }

        std::array<std::uint8_t, 16> ecount_buf{};
        unsigned int num = 0;
        AES_ctr128_encrypt(rtp_buffer.data() + header_len,
                           rtp_buffer.data() + header_len,
                           payload_len, &aes_ctx, iv.data(),
                           ecount_buf.data(), &num);

        UniqueHmacCtx hmac(HMAC_CTX_new());
        if (!hmac) {
            return std::unexpected(ProtectError::HmacInitFailed);
        }

        HMAC_Init_ex(hmac.get(), keys.auth_key.data(), 20, EVP_sha1(), nullptr);
        HMAC_Update(hmac.get(), rtp_buffer.data(), header_len + payload_len);

        const std::array<std::uint8_t, 4> roc_be = {
            static_cast<std::uint8_t>(roc >> 24),
            static_cast<std::uint8_t>(roc >> 16),
            static_cast<std::uint8_t>(roc >> 8),
            static_cast<std::uint8_t>(roc & 0xFF)
        };
        HMAC_Update(hmac.get(), roc_be.data(), roc_be.size());

        std::array<std::uint8_t, 32> mac_out{};
        unsigned int mac_len = 0;
        HMAC_Final(hmac.get(), mac_out.data(), &mac_len);

        std::memcpy(rtp_buffer.data() + header_len + payload_len, mac_out.data(), 10);
        return header_len + payload_len + 10;
    }

    static std::expected<std::size_t, UnprotectError> unprotect(
        const SessionKeys& keys,
        std::span<std::uint8_t> packet_buffer,
        std::size_t header_len,
        std::uint32_t ssrc,
        std::uint64_t index,
        std::uint32_t roc_est) noexcept {

        if (packet_buffer.size() < header_len + 10) {
            return std::unexpected(UnprotectError::PacketTooShort);
        }

        const std::size_t payload_len = packet_buffer.size() - header_len - 10;
        const std::uint8_t* received_tag = packet_buffer.data() + header_len + payload_len;

        UniqueHmacCtx hmac(HMAC_CTX_new());
        if (!hmac) {
            return std::unexpected(UnprotectError::HmacInitFailed);
        }

        HMAC_Init_ex(hmac.get(), keys.auth_key.data(), 20, EVP_sha1(), nullptr);
        HMAC_Update(hmac.get(), packet_buffer.data(), header_len + payload_len);

        const std::array<std::uint8_t, 4> roc_be = {
            static_cast<std::uint8_t>(roc_est >> 24),
            static_cast<std::uint8_t>(roc_est >> 16),
            static_cast<std::uint8_t>(roc_est >> 8),
            static_cast<std::uint8_t>(roc_est & 0xFF)
        };
        HMAC_Update(hmac.get(), roc_be.data(), roc_be.size());

        std::array<std::uint8_t, 32> mac_calc{};
        unsigned int mac_len = 0;
        HMAC_Final(hmac.get(), mac_calc.data(), &mac_len);

        if (CRYPTO_memcmp(received_tag, mac_calc.data(), 10) != 0) {
            return std::unexpected(UnprotectError::AuthFailed);
        }

        std::array<std::uint8_t, 16> iv{};
        build_iv(keys.salt_key, ssrc, index, iv);

        AES_KEY aes_ctx{};
        if (AES_set_encrypt_key(keys.enc_key.data(), 128, &aes_ctx) != 0) {
            return std::unexpected(UnprotectError::AesInitFailed);
        }

        std::array<std::uint8_t, 16> ecount_buf{};
        unsigned int num = 0;
        AES_ctr128_encrypt(packet_buffer.data() + header_len,
                           packet_buffer.data() + header_len,
                           payload_len, &aes_ctx, iv.data(),
                           ecount_buf.data(), &num);

        return payload_len;
    }

private:
    static void build_iv(std::span<const std::uint8_t, 14> salt,
                         std::uint32_t ssrc,
                         std::uint64_t index,
                         std::span<std::uint8_t, 16> iv) noexcept {
        std::memcpy(iv.data(), salt.data(), 14);
        iv[14] = 0;
        iv[15] = 0;

        iv[4] ^= static_cast<std::uint8_t>(ssrc >> 24);
        iv[5] ^= static_cast<std::uint8_t>(ssrc >> 16);
        iv[6] ^= static_cast<std::uint8_t>(ssrc >> 8);
        iv[7] ^= static_cast<std::uint8_t>(ssrc & 0xFF);

        for (int b = 0; b < 6; ++b) {
            iv[8 + b] ^= static_cast<std::uint8_t>((index >> (8 * (5 - b))) & 0xFF);
        }
    }
};
```
:::

---

## 5. Оптимізація та апаратне прискорення у високонавантажених серверах

У сучасних медіасерверах (SFU, Selective Forwarding Unit), які маршрутизують сотні одночасних відеоконференцій із тисячами учасників, програмне шифрування стає головним споживачем тактових циклів CPU.

### Безкопіювальна обробка буферів пам'яті (Zero-Copy Pipeline)

У традиційній наївній реалізації кожен пакет копіюється з буфера мережевого сокета в буфер дешифрування, а потім — у буфер медіадекодера. При бітрейті 10 Гбіт/с на сервері таке копіювання повністю забиває пропускну здатність шини пам'яті (Memory Bandwidth Bottleneck).

Професійні рушії SRTP виконують шифрування та дешифрування безпосередньо за місцем (In-Place Encryption) у тому самому буфері сокета. Оскільки довжина відкритого й зашифрованого тексту в AES-CTR збігається, відправник просто виділяє буфер із додатковими 10 байтами в кінці під трейлер автентифікації. Для формування вектора введення-виведення застосовуються системні структури векторного запису `struct iovec` у POSIX або `std::span` у C++, що дозволяє відправляти заголовок і зашифроване тіло за один системний виклик `sendmsg()`.

### Використання векторних інструкцій AES-NI та AVX2

Стандартний блоковий шифр AES в режимі лічильника має чудову властивість: обчислення блоків гами є повністю незалежним. На відміну від режимів зі зчепленням блоків (CBC), де кожен наступний блок чекає результату попереднього, у CTR можна паралельно згенерувати 4 або 8 блоків гами за один такт процесора за допомогою інструкцій Intel/AMD AES-NI (`_mm_aesenc_si128`) або ARMv8 Crypto Extensions.

Сучасний профіль `SRTP_AEAD_AES_128_GCM` (RFC 7714) забезпечує додатковий виграш: апаратний блок обчислення поля Галуа (інструкція `PCLMULQDQ` для множення многочленів) формує тег GMAC одночасно з генерацією гами шифрування, скорочуючи загальний час обробки пакета більш ніж удвічі порівняно з послідовним конвеєром AES-CTR + HMAC-SHA1.

### Багатопоточність та ізоляція контекстів SSRC

У високопродуктивних системах криптографічний контекст створюється окремо для кожного джерела `SSRC`. Оскільки різні медіапотоки мають власні незалежні лічильники `ROC`, порядкові номери та вікна антиповтору, пакети різних SSRC можуть оброблятися в паралельних робочих потоках (Worker Threads) без міжпотокових блокувань (Lock-Free Processing).

---

## 6. Безпека життєвого циклу сесії та тестування надійності

Експлуатація рушіїв SRTP у продакшені вимагає суворого дотримання правил безпеки пам'яті та верифікації стану:

### Робота з переініціалізацією та зміною ключів (Rekeying)

Коли під час тривалого дзвінка відбувається зміна ключів через сигналізацію DTLS (Renegotiation), старий і новий криптографічні контексти повинні співіснувати в пам'яті протягом перехідного вікна (зазвичай 2–5 секунд). Це необхідно тому, що пакети, зашифровані старим ключем, можуть затриматися в мережі й прибути вже після отримання нового майстер-ключа. Застосування поля `MKI` (Master Key Identifier) дозволяє отримувачу однозначно визначити потрібний контекст для кожного вхідного пакета.

### Фазинг та перевірка еталонними векторами RFC 3711

Для забезпечення абсолютної стійкості проти зловмисних пакетів рушії SRTP тестуються фазерами (наприклад, `libFuzzer` та `AFL++`) з увімкненими санітайзерами AddressSanitizer (ASan) та UndefinedBehaviorSanitizer (UBSan). Генератор мутацій цілеспрямовано спотворює поля RTP-розширень, змінює байти тегів HMAC та моделює шторм дубльованих пакетів на межі переповнення `ROC`.

Еталонна верифікація виконується за тестовими векторами з Додатка B стандарту RFC 3711, які фіксують точні шістнадцяткові дампи для майстер-ключа, солі, згенерованих сесійних ключів та фінальних зашифрованих пакетів.

---

## 7. Типові пастки та крайові випадки інженерної реалізації

Практична експлуатація криптографічних протоколів реального часу виявляє тонкі дефекти реалізації, які не помітні під час синтетичних тестів, але призводять до вразливостей або розриву зв'язку в реальних мережах:

1. **Включення ROC у підпис HMAC:** Найпоширеніша помилка початківців — обчислення HMAC лише поверх байтів, фізично переданих у датаграмі. Стандарт RFC 3711 вимагає додавати 4 байти лічильника `ROC` у прямому мережевому порядку байтів (Big-Endian) у кінець повідомлення перед фіналізацією хешу HMAC, навіть якщо саме поле `ROC` не передається через мережу. Якби цього не робилося, зловмисник міг би записати легітимний пакет епохи `ROC = 0` і відправити його повторно через 21 хвилину в епосі `ROC = 1`: підпис зійшовся б, а отримувач прийняв би фальшиве аудіо.
2. **Константний час порівняння тегів автентифікації:** При перевірці отриманого тега автентифікації категорично заборонено використовувати стандартну функцію `memcmp()`. Вона перериває порівняння на першому незбіжному байті, створюючи витік інформації через час виконання (Timing Attack). Зловмисник, вимірюючи наносекундні затримки відповідей сервера, може байт за байтом підібрати валідний підпис. Слід застосовувати функцію з константним часом виконання, таку як `CRYPTO_memcmp()` в OpenSSL, або самостійно реалізоване порозрядне бітове додавання `OR` по всіх байтах без умовних переходів.
3. **Побітова робота з мережевим порядком байтів:** Усі поля заголовків RTP (`Sequence Number`, `Timestamp`, `SSRC`) передаються в порядку Big-Endian (Network Byte Order). При формуванні векторів ініціалізації на архітектурах x86/x64 (Little-Endian) необхідно явно виконувати побітові зсуви або застосовувати функції `htons()` / `htonl()`. Помилка в порядку байтів призводить до повної розсинхронізації гами між відправником і отримувачем.
4. **Гарантоване знищення сесійних ключів у пам'яті:** Після завершення виклику структури з ключами `k_e`, `k_a`, `k_s` та майстер-секретами повинні негайно затиратися нулями за допомогою функцій `OPENSSL_cleanse()` або `explicit_bzero()`. Звичайний виклик `memset()` часто оптимізується й повністю видаляється компілятором, якщо пам'ять звільняється одразу після цього, залишаючи відкриті ключі в дампі пам'яті процесу.
