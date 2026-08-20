# ⚙️ Реалізація конвертного шифрування: AES-256-GCM та обгортання ключів

Конвертне шифрування (англ. *envelope encryption*) є фундаментальним патерном захисту даних у спокої, що поєднує швидкість локального симетричного шифрування великих масивів інформації з безпекою централізованого керування ключами. Замість того, щоб передавати мегабайти чи гігабайти корисного навантаження через повільну мережу до центрального сервісу ключів або модуля безпеки HSM, клієнтський додаток генерує або запитує одноразовий 256-бітний ключ шифрування даних (DEK), локально шифрує корисне навантаження алгоритмом AES-256-GCM із контролем цілісності та контекстом автентифікації (AAD), обгортає DEK довгостроковим ключем шифрування ключів (KEK) і негайно зачищає відкритий DEK у пам'яті.

Нижче наведено повноцінну реалізацію конвертного шифратора та дешифратора з використанням бібліотеки OpenSSL EVP. Приклад містить дві вкладки: ідіоматичний код мовою C з ручним керуванням пам'яттю, контролем життєвого циклу ресурсів та гарантованим очищенням буферів через `OPENSSL_cleanse`, та еквівалентний C++20-код із використанням RAII-обгорток, неволодіючих зрізів пам'яті `std::span`, семантики значень `std::expected` та автоматичного занулення пам'яті у деструкторі.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/crypto.h>

#define KEY_SIZE_256   32
#define GCM_IV_SIZE    12
#define GCM_TAG_SIZE   16

// Структура упакованого зашифрованого конверта
typedef struct {
    uint8_t wrapped_dek[KEY_SIZE_256 + GCM_TAG_SIZE]; // Зашифрований DEK + Tag обгортки
    uint8_t iv_dek[GCM_IV_SIZE];                       // IV для обгортання DEK
    uint8_t iv_data[GCM_IV_SIZE];                      // IV для шифрування корисних даних
    uint8_t tag_data[GCM_TAG_SIZE];                    // Автентифікаційний тег даних
    uint8_t *ciphertext;                               // Тіло зашифрованих даних
    size_t ciphertext_len;                             // Довжина шифротексту
} envelope_t;

// Допоміжна функція AES-256-GCM шифрування
static bool aes_gcm_encrypt(const uint8_t *key, const uint8_t *iv,
                            const uint8_t *aad, size_t aad_len,
                            const uint8_t *plain, size_t plain_len,
                            uint8_t *cipher, uint8_t *tag) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return false;

    int len = 0;
    bool success = false;

    if (EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, GCM_IV_SIZE, NULL) != 1) goto cleanup;
    if (EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv) != 1) goto cleanup;

    // Передача додаткових автентифікованих даних (AAD)
    if (aad && aad_len > 0) {
        if (EVP_EncryptUpdate(ctx, NULL, &len, aad, (int)aad_len) != 1) goto cleanup;
    }

    // Шифрування відкритого тексту
    if (EVP_EncryptUpdate(ctx, cipher, &len, plain, (int)plain_len) != 1) goto cleanup;
    if (EVP_EncryptFinal_ex(ctx, cipher + len, &len) != 1) goto cleanup;

    // Отримання тегу автентифікації
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, GCM_TAG_SIZE, tag) != 1) goto cleanup;

    success = true;

cleanup:
    EVP_CIPHER_CTX_free(ctx);
    return success;
}

// Допоміжна функція AES-256-GCM розшифрування
static bool aes_gcm_decrypt(const uint8_t *key, const uint8_t *iv,
                            const uint8_t *aad, size_t aad_len,
                            const uint8_t *cipher, size_t cipher_len,
                            const uint8_t *tag, uint8_t *plain) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) return false;

    int len = 0;
    bool success = false;

    if (EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL) != 1) goto cleanup;
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, GCM_IV_SIZE, NULL) != 1) goto cleanup;
    if (EVP_DecryptInit_ex(ctx, NULL, NULL, key, iv) != 1) goto cleanup;

    // Передача AAD
    if (aad && aad_len > 0) {
        if (EVP_DecryptUpdate(ctx, NULL, &len, aad, (int)aad_len) != 1) goto cleanup;
    }

    // Розшифрування
    if (EVP_DecryptUpdate(ctx, plain, &len, cipher, (int)cipher_len) != 1) goto cleanup;

    // Встановлення очікуваного тегу перед фіналізацією
    if (EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, GCM_TAG_SIZE, (void*)tag) != 1) goto cleanup;

    // Перевірка цілісності: якщо тег не зійшовся, EVP_DecryptFinal_ex повертає <= 0
    if (EVP_DecryptFinal_ex(ctx, plain + len, &len) != 1) goto cleanup;

    success = true;

cleanup:
    EVP_CIPHER_CTX_free(ctx);
    return success;
}

// Запечатування даних у конверт
bool envelope_seal(const uint8_t *kek, const uint8_t *aad, size_t aad_len,
                   const uint8_t *data, size_t data_len, envelope_t *env) {
    uint8_t raw_dek[KEY_SIZE_256];
    bool status = false;

    // 1. Генерація криптографічно стійкого випадкового DEK та IV
    if (RAND_bytes(raw_dek, KEY_SIZE_256) != 1) return false;
    if (RAND_bytes(env->iv_dek, GCM_IV_SIZE) != 1) goto scrub_dek;
    if (RAND_bytes(env->iv_data, GCM_IV_SIZE) != 1) goto scrub_dek;

    env->ciphertext = (uint8_t*)malloc(data_len);
    if (!env->ciphertext) goto scrub_dek;
    env->ciphertext_len = data_len;

    // 2. Шифрування корисних даних згенерованим DEK
    if (!aes_gcm_encrypt(raw_dek, env->iv_data, aad, aad_len,
                         data, data_len, env->ciphertext, env->tag_data)) {
        free(env->ciphertext);
        env->ciphertext = NULL;
        goto scrub_dek;
    }

    // 3. Обгортання DEK довгостроковим ключем KEK
    uint8_t dek_tag[GCM_TAG_SIZE];
    if (!aes_gcm_encrypt(kek, env->iv_dek, aad, aad_len,
                         raw_dek, KEY_SIZE_256, env->wrapped_dek, dek_tag)) {
        free(env->ciphertext);
        env->ciphertext = NULL;
        goto scrub_dek;
    }
    memcpy(env->wrapped_dek + KEY_SIZE_256, dek_tag, GCM_TAG_SIZE);

    status = true;

scrub_dek:
    // 4. Обов'язкове занулення відкритого ключа DEK у пам'яті
    OPENSSL_cleanse(raw_dek, KEY_SIZE_256);
    return status;
}

// Розпечатування конверта
bool envelope_open(const uint8_t *kek, const uint8_t *aad, size_t aad_len,
                   const envelope_t *env, uint8_t *out_data) {
    uint8_t raw_dek[KEY_SIZE_256];
    bool status = false;

    // 1. Розгортання DEK за допомогою KEK
    const uint8_t *dek_tag = env->wrapped_dek + KEY_SIZE_256;
    if (!aes_gcm_decrypt(kek, env->iv_dek, aad, aad_len,
                         env->wrapped_dek, KEY_SIZE_256, dek_tag, raw_dek)) {
        return false; // Помилка автентифікації KEK або AAD
    }

    // 2. Розшифрування корисного навантаження отриманим DEK
    if (!aes_gcm_decrypt(raw_dek, env->iv_data, aad, aad_len,
                         env->ciphertext, env->ciphertext_len, env->tag_data, out_data)) {
        goto scrub_dek; // Помилка цілісності тіла даних
    }

    status = true;

scrub_dek:
    // 3. Негайне занулення DEK після використання
    OPENSSL_cleanse(raw_dek, KEY_SIZE_256);
    return status;
}
```
```cpp
#include <iostream>
#include <span>
#include <vector>
#include <memory>
#include <array>
#include <expected>
#include <algorithm>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/crypto.h>

constexpr size_t KeySize256 = 32;
constexpr size_t GcmIvSize  = 12;
constexpr size_t GcmTagSize = 16;

// RAII занулювач для безпечного очищення конфіденційних буферів
template <size_t N>
struct SecureBuffer {
    std::array<uint8_t, N> data{};

    ~SecureBuffer() {
        OPENSSL_cleanse(data.data(), data.size());
    }

    SecureBuffer() = default;
    SecureBuffer(const SecureBuffer&) = delete;
    SecureBuffer& operator=(const SecureBuffer&) = delete;
};

// RAII обгортка над EVP_CIPHER_CTX
struct EvpCipherCtxDeleter {
    void operator()(EVP_CIPHER_CTX* ctx) const noexcept {
        if (ctx) EVP_CIPHER_CTX_free(ctx);
    }
};
using UniqueCipherCtx = std::unique_ptr<EVP_CIPHER_CTX, EvpCipherCtxDeleter>;

enum class CryptoError {
    RngFailure,
    ContextInitFailure,
    EncryptionFailure,
    DecryptionTagMismatch,
    AllocationError
};

struct SealedEnvelope {
    std::array<uint8_t, KeySize256 + GcmTagSize> wrapped_dek{};
    std::array<uint8_t, GcmIvSize> iv_dek{};
    std::array<uint8_t, GcmIvSize> iv_data{};
    std::array<uint8_t, GcmTagSize> tag_data{};
    std::vector<uint8_t> ciphertext;
};

class EnvelopeCrypto {
public:
    static std::expected<SealedEnvelope, CryptoError> Seal(
        std::span<const uint8_t, KeySize256> kek,
        std::span<const uint8_t> aad,
        std::span<const uint8_t> plaintext) 
    {
        SecureBuffer<KeySize256> raw_dek;
        SealedEnvelope env;
        env.ciphertext.resize(plaintext.size());

        if (RAND_bytes(raw_dek.data.data(), static_cast<int>(KeySize256)) != 1 ||
            RAND_bytes(env.iv_dek.data(), static_cast<int>(GcmIvSize)) != 1 ||
            RAND_bytes(env.iv_data.data(), static_cast<int>(GcmIvSize)) != 1) {
            return std::unexpected(CryptoError::RngFailure);
        }

        // 1. Шифрування корисних даних за допомогою DEK
        auto data_enc_res = AesGcmEncrypt(
            raw_dek.data, env.iv_data, aad, plaintext, env.ciphertext, env.tag_data);
        if (!data_enc_res) return std::unexpected(data_enc_res.error());

        // 2. Обгортання DEK за допомогою KEK
        std::array<uint8_t, GcmTagSize> dek_tag{};
        auto dek_enc_res = AesGcmEncrypt(
            kek, env.iv_dek, aad, raw_dek.data,
            std::span<uint8_t>(env.wrapped_dek.data(), KeySize256), dek_tag);
        if (!dek_enc_res) return std::unexpected(dek_enc_res.error());

        std::copy(dek_tag.begin(), dek_tag.end(), env.wrapped_dek.begin() + KeySize256);
        return env;
    }

    static std::expected<std::vector<uint8_t>, CryptoError> Open(
        std::span<const uint8_t, KeySize256> kek,
        std::span<const uint8_t> aad,
        const SealedEnvelope& env) 
    {
        SecureBuffer<KeySize256> raw_dek;

        // 1. Розгортання DEK
        std::span<const uint8_t, KeySize256> wrapped_dek_span(env.wrapped_dek.data(), KeySize256);
        std::span<const uint8_t, GcmTagSize> dek_tag_span(env.wrapped_dek.data() + KeySize256, GcmTagSize);

        auto dek_dec_res = AesGcmDecrypt(
            kek, env.iv_dek, aad, wrapped_dek_span, dek_tag_span, raw_dek.data);
        if (!dek_dec_res) return std::unexpected(CryptoError::DecryptionTagMismatch);

        // 2. Розшифрування корисного навантаження
        std::vector<uint8_t> plaintext(env.ciphertext.size());
        auto data_dec_res = AesGcmDecrypt(
            raw_dek.data, env.iv_data, aad, env.ciphertext, env.tag_data, plaintext);
        if (!data_dec_res) return std::unexpected(CryptoError::DecryptionTagMismatch);

        return plaintext;
    }

private:
    static std::expected<void, CryptoError> AesGcmEncrypt(
        std::span<const uint8_t> key, std::span<const uint8_t> iv,
        std::span<const uint8_t> aad, std::span<const uint8_t> plain,
        std::span<uint8_t> cipher, std::span<uint8_t, GcmTagSize> tag) 
    {
        UniqueCipherCtx ctx(EVP_CIPHER_CTX_new());
        if (!ctx) return std::unexpected(CryptoError::ContextInitFailure);

        int len = 0;
        if (EVP_EncryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_IVLEN, static_cast<int>(iv.size()), nullptr) != 1 ||
            EVP_EncryptInit_ex(ctx.get(), nullptr, nullptr, key.data(), iv.data()) != 1) {
            return std::unexpected(CryptoError::EncryptionFailure);
        }

        if (!aad.empty()) {
            if (EVP_EncryptUpdate(ctx.get(), nullptr, &len, aad.data(), static_cast<int>(aad.size())) != 1)
                return std::unexpected(CryptoError::EncryptionFailure);
        }

        if (EVP_EncryptUpdate(ctx.get(), cipher.data(), &len, plain.data(), static_cast<int>(plain.size())) != 1 ||
            EVP_EncryptFinal_ex(ctx.get(), cipher.data() + len, &len) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_GET_TAG, static_cast<int>(GcmTagSize), tag.data()) != 1) {
            return std::unexpected(CryptoError::EncryptionFailure);
        }

        return {};
    }

    static std::expected<void, CryptoError> AesGcmDecrypt(
        std::span<const uint8_t> key, std::span<const uint8_t> iv,
        std::span<const uint8_t> aad, std::span<const uint8_t> cipher,
        std::span<const uint8_t, GcmTagSize> tag, std::span<uint8_t> plain) 
    {
        UniqueCipherCtx ctx(EVP_CIPHER_CTX_new());
        if (!ctx) return std::unexpected(CryptoError::ContextInitFailure);

        int len = 0;
        if (EVP_DecryptInit_ex(ctx.get(), EVP_aes_256_gcm(), nullptr, nullptr, nullptr) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_IVLEN, static_cast<int>(iv.size()), nullptr) != 1 ||
            EVP_DecryptInit_ex(ctx.get(), nullptr, nullptr, key.data(), iv.data()) != 1) {
            return std::unexpected(CryptoError::ContextInitFailure);
        }

        if (!aad.empty()) {
            if (EVP_DecryptUpdate(ctx.get(), nullptr, &len, aad.data(), static_cast<int>(aad.size())) != 1)
                return std::unexpected(CryptoError::ContextInitFailure);
        }

        if (EVP_DecryptUpdate(ctx.get(), plain.data(), &len, cipher.data(), static_cast<int>(cipher.size())) != 1 ||
            EVP_CIPHER_CTX_ctrl(ctx.get(), EVP_CTRL_GCM_SET_TAG, static_cast<int>(GcmTagSize), const_cast<uint8_t*>(tag.data())) != 1 ||
            EVP_DecryptFinal_ex(ctx.get(), plain.data() + len, &len) != 1) {
            return std::unexpected(CryptoError::DecryptionTagMismatch);
        }

        return {};
    }
};
```
:::

### Архітектурний розбір коду та порівняння парадигм

Реалізація конвертного шифрування вимагає суворого дотримання послідовності викликів API OpenSSL EVP, де кожен крок відображає фундаментальні криптографічні вимоги до обробки даних та керування пам'яттю:

1. **Ініціалізація та налаштування контексту (Init & Ctrl):**
   У обох мовах створення криптографічного контексту відбувається через `EVP_CIPHER_CTX_new()`. Для режиму GCM критично важливо встановити довжину вектора ініціалізації (`EVP_CTRL_GCM_SET_IVLEN`) рівною 12 байтам (96 бітів) **до** передачі самого ключа та вектора в `EVP_EncryptInit_ex()`. Якщо цього не зробити, OpenSSL за замовчуванням очікуватиме 16-байтний IV, що призведе до внутрішнього збою гешування GHASH. Сам криптографічний контекст `EVP_CIPHER_CTX` не є потокобезпечним: кожен потік виконання зобов'язаний створювати власний незалежний контекст.

2. **Обробка додаткових автентифікованих даних (AAD):**
   Контекст автентифікації передається у функцію `EVP_EncryptUpdate()` (або `EVP_DecryptUpdate()`) з нульовим вказівником на вихідний буфер шифротексту (`out = NULL`). Це сигналізує рушію OpenSSL, що вхідний масив байтів не потребує симетричного шифрування, а лише включається в поліноміальний розрахунок автентифікаційного тегу GHASH. Обробка AAD обов'язково має передувати викликам `EVP_EncryptUpdate()` над основним тілом даних: змішування черговості викликів призводить до помилки верифікації тегу.

3. **Розділення відповідальності за пам'ять (C проти C++):**
   - У варіанті мовою **C** розробник вручну контролює виділення та звільнення пам'яті через `malloc`/`free`, а всі переходи при виникненні помилок маршрутизуються через мітку `goto scrub_dek`. Це запобігає витоку пам'яті та гарантує, що тимчасовий буфер `raw_dek` буде очищено навіть при збої шифрування на середині буфера.
   - У варіанті мовою **C++20** керування життєвим циклом контексту `EVP_CIPHER_CTX` повністю інкапсульовано в `std::unique_ptr` із кастомним делетером `EvpCipherCtxDeleter`. Шаблонна структура `SecureBuffer` реалізує ідіому RAII для стекового масиву: її деструктор безумовно викликає `OPENSSL_cleanse` під час розкручування стека (stack unwinding), що унеможливлює витік відкритого ключа при будь-яких ранніх поверненнях із функцій.

4. **Вибір алгоритму обгортання ключа (AES-GCM проти AES-KW):**
   У наведеному прикладі для загортання DEK використовується той самий алгоритм AES-256-GCM з окремим вектором `iv_dek` та автентифікаційним тегом. У промислових сховищах альтернативою є стандарт обгортання ключів **AES Key Wrap (KW / KWP, RFC 3394 / RFC 5649)**. AES-KW є детермінованим алгоритмом без вектора ініціалізації, що використовує шестираундну перестановку Фейстеля з фіксованим вектором цілісності `0xA6A6A6A6A6A6A6A6`. Використання AES-GCM є універсальнішим, оскільки дозволяє напряму передавати довільний рядок AAD безпосередньо в обгортку ключа.

---

### Пастки та крайові випадки

1. **Оптимізація мертвого коду (Dead-Store Elimination):**
   Використання стандартної функції `memset(raw_dek, 0, 32)` наприкінці функції є критичною вразливістю. Оптимізувальні компілятори (GCC з флагом `-O2/-O3`, Clang) аналізують граф потоку даних: оскільки масив `raw_dek` більше не читається перед виходом зі стекового кадру, компілятор повністю викидає виклик `memset` як непотрібний. Відкритий ключ залишається у незмінному вигляді в пам'яті стека, звідки може потрапити в аварійний дамп пам'яті (core dump) або розділ підкачки (swap). Обов'язково використовуйте `OPENSSL_cleanse()` або `explicit_bzero()`, які захищені від оптимізацій асемблерними бар'єрами.

2. **Повторне використання вектора ініціалізації (IV Reuse):**
   Режим AES-GCM є лічильним режимом. Якщо зашифрувати два різні повідомлення одним ключем `K` і тим самим вектором `IV`, операція XOR між шифротекстами розкриває XOR відкритих текстів: `C₁ ⊕ C₂ = P₁ ⊕ P₂`. Крім того, повтор IV дозволяє зловмиснику розв'язати лінійне рівняння в полі `GF(2¹²⁸)` і повністю відновити ключ автентифікації GHASH `H`. Для кожного шифрування IV **мусить** бути згенерований криптографічно стійким генератором `RAND_bytes()` або являти собою монотонний 96-бітний лічильник.

3. **Своєчасна перевірка автентифікаційного тегу:**
   Розшифровані байти не можна передавати іншим підсистемам або повертати користувачеві доти, доки `EVP_DecryptFinal_ex()` не підтвердить коректність тегу `tag_data`. Якщо віддати частково розшифровані дані до перевірки тегу, система стає вразливою до атак типу «оракул розшифрування» (Padding/Decryption Oracle).

4. **Криптографічна прив'язка через AAD:**
   Якщо не передавати ідентифікатор ресурсу або орендаря в полі `aad`, зловмисник із доступом до бази даних може переставити зашифрований конверт із поля `user_a.billing_info` у поле `user_b.billing_info` (атака підміни шифротексту / ciphertext transplantation). Перевірка AAD унеможливлює таку маніпуляцію.

5. **Блокування пам'яті від скидання у swap:**
   У високонавантажених сервісах обробки секретів критично важливо заборонити ядру операційної системи витісняти сторінки пам'яті з відкритими ключами на диск у swap-простір. Для цього використовується системний виклик `mlock()` або спеціалізовані захищені алокатори, які виділяють сторінки з прапорцем `MAP_LOCKED`.

6. **Очищення вихідного буфера при збоях автентифікації:**
   Якщо функція `aes_gcm_decrypt` повертає помилку через невідповідність тегу, вихідний буфер `plain` або `out_data` може містити частково розшифровані байти. Викликаючий код зобов'язаний негайно затерти вихідний буфер викликом `OPENSSL_cleanse`, щоб сміттєві фрагменти не стали джерелом витоку інформації через канали побічного спостереження.
