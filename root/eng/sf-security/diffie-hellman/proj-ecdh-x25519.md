# ⚙️ Ефемерний обмін ключами X25519 та виведення сесійних ключів через HKDF

У сучасних захищених мережевих протоколах (TLS 1.3, SSHv2, Signal, WireGuard) процедура встановлення безпечного сеансу зв'язку будується на композиції двох фундаментальних примітивів: ефемерного скалярного множення на еліптичній кривій **X25519** (RFC 7748) та стандартизованої функції виведення ключів на основі HMAC **HKDF-SHA256** (RFC 5869).

### Архітектура та етапи узгодження сесійного стану

Наївне використання сирого результату скалярного множення `K` як прямого симетричного ключа для шифрування є грубою інженерною помилкою. Обчислений спільний секрет `K` є x-координатою точки на еліптичній кривій: його байти мають специфічну математичну структуру і не є статистично рівномірно розподіленими випадковими даними. Крім того, для повнодуплексного захищеного зв'язку вимагається роздільний набір ключів для клієнта та сервера, а також незалежні вектори ініціалізації (IV).

Конвеєр встановлення захищеного з'єднання складається з п'яти послідовних фаз:

1. **Генерація ефемерних пар ключів:** Обидві сторони генерують 256-бітні приватні скаляри за допомогою системного криптографічного генератора випадкових чисел (CSPRNG) та обчислюють відповідні відкриті ключі шляхом множення базової точки `G`.
2. **Відкритий обмін та обчислення сирого секрету:** Клієнт та сервер обмінюються 32-байтними відкритими ключами через відкритий канал й обчислюють скалярний добуток `K = X25519(our_priv, peer_pub)`. Завдяки комутативності скалярного множення на кривій Монтгомері обидві сторони отримують однаковий 32-байтний масив `K`.
3. **Екстракція ентропії (HKDF-Extract):** Сирий 32-байтний секрет `K` разом із випадковою сіллю (англ. *Salt*, наприклад, конкатенацією `ClientHello.random` та `ServerHello.random`) перетворюється на псевдовипадковий майстер-ключ (англ. *Pseudorandom Key*, PRK) фіксованої довжини:
   ```
   PRK = HMAC-SHA256(Salt, K)
   ```
   Етап Extract усуває будь-яку нерівномірність розподілу бітів, перетворюючи сирий математичний результат на криптографічно стійкий псевдовипадковий ключ.
4. **Розширення ключів (HKDF-Expand):** Майстер-ключ `PRK` розгортається у вихідний ключовий матеріал (англ. *Output Keying Material*, OKM) необхідної сумарної довжини із прив'язкою до контекстного рядка протоколу (англ. *Info*, наприклад `"tls13-session-v1"`):
   ```
   OKM = HKDF-Expand(PRK, Info, L)
   ```
   З отриманого блоку `OKM` послідовно нарізаються окремі параметри:
   * `ClientWriteKey` (32 байти) — симетричний ключ для шифрування трафіку від клієнта до сервера.
   * `ServerWriteKey` (32 байти) — симетричний ключ для шифрування трафіку від сервера до клієнта.
   * `ClientWriteIV` (12 байтів) — вектор ініціалізації для AEAD-шифру клієнта (наприклад, AES-GCM або ChaCha20-Poly1305).
   * `ServerWriteIV` (12 байтів) — вектор ініціалізації для AEAD-шифру сервера.
5. **Гарантоване затирання пам'яті (Secure Memory Cleanse):** Для суворого дотримання принципу прямої секретності (PFS) змінні, що містили закриті ключі, проміжний спільний секрет `K` та робочі буфери розширення, негайно затираються нулями за допомогою функцій `OPENSSL_cleanse`, які захищені від оптимізацій компілятора.

### Реалізація на мовах C та C++20

Нижче наведено повний вихідний код програми, яка демонструє повний цикл узгодження ключів між клієнтом та сервером за допомогою бібліотеки OpenSSL 3.0.

:::tabs
```c
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/kdf.h>
#include <openssl/rand.h>

#define KEY_LEN 32
#define IV_LEN 12

typedef struct {
    uint8_t client_write_key[KEY_LEN];
    uint8_t server_write_key[KEY_LEN];
    uint8_t client_write_iv[IV_LEN];
    uint8_t server_write_iv[IV_LEN];
} session_keys_t;

static void secure_cleanse(void *ptr, size_t len) {
    OPENSSL_cleanse(ptr, len);
}

/* Генерація пари ключів X25519 */
static EVP_PKEY* generate_x25519_keypair(void) {
    EVP_PKEY_CTX *pctx = EVP_PKEY_CTX_new_id(EVP_PKEY_X25519, NULL);
    if (!pctx) return NULL;

    EVP_PKEY *pkey = NULL;
    if (EVP_PKEY_keygen_init(pctx) <= 0 || EVP_PKEY_keygen(pctx, &pkey) <= 0) {
        EVP_PKEY_CTX_free(pctx);
        return NULL;
    }
    EVP_PKEY_CTX_free(pctx);
    return pkey;
}

/* Обчислення спільного секрету K через X25519 */
static int derive_shared_secret(EVP_PKEY *our_priv, EVP_PKEY *peer_pub,
                                uint8_t *out_secret, size_t *out_len) {
    EVP_PKEY_CTX *ctx = EVP_PKEY_CTX_new(our_priv, NULL);
    if (!ctx) return 0;

    if (EVP_PKEY_derive_init(ctx) <= 0 ||
        EVP_PKEY_derive_set_peer(ctx, peer_pub) <= 0) {
        EVP_PKEY_CTX_free(ctx);
        return 0;
    }

    if (EVP_PKEY_derive(ctx, out_secret, out_len) <= 0) {
        EVP_PKEY_CTX_free(ctx);
        return 0;
    }

    EVP_PKEY_CTX_free(ctx);
    return 1;
}

/* Виведення симетричних ключів через HKDF-SHA256 (RFC 5869) */
static int derive_session_keys(const uint8_t *shared_secret, size_t secret_len,
                               const uint8_t *salt, size_t salt_len,
                               const char *info, session_keys_t *keys) {
    EVP_KDF *kdf = EVP_KDF_fetch(NULL, "HKDF", NULL);
    if (!kdf) return 0;

    EVP_KDF_CTX *kctx = EVP_KDF_CTX_new(kdf);
    EVP_KDF_free(kdf);
    if (!kctx) return 0;

    char digest[] = "SHA256";
    OSSL_PARAM params[5];
    params[0] = OSSL_PARAM_construct_utf8_string("digest", digest, sizeof(digest));
    params[1] = OSSL_PARAM_construct_octet_string("key", (void*)shared_secret, secret_len);
    params[2] = OSSL_PARAM_construct_octet_string("salt", (void*)salt, salt_len);
    params[3] = OSSL_PARAM_construct_octet_string("info", (void*)info, strlen(info));
    params[4] = OSSL_PARAM_construct_end();

    uint8_t out_material[sizeof(session_keys_t)];
    int ret = EVP_KDF_derive(kctx, out_material, sizeof(out_material), params);
    EVP_KDF_CTX_free(kctx);

    if (ret <= 0) return 0;

    memcpy(keys->client_write_key, out_material, KEY_LEN);
    memcpy(keys->server_write_key, out_material + KEY_LEN, KEY_LEN);
    memcpy(keys->client_write_iv, out_material + 2 * KEY_LEN, IV_LEN);
    memcpy(keys->server_write_iv, out_material + 2 * KEY_LEN + IV_LEN, IV_LEN);

    secure_cleanse(out_material, sizeof(out_material));
    return 1;
}

int main(void) {
    /* 1. Клієнт генерує ефемерну пару */
    EVP_PKEY *client_key = generate_x25519_keypair();
    /* 2. Сервер генерує ефемерну пару */
    EVP_PKEY *server_key = generate_x25519_keypair();
    if (!client_key || !server_key) goto cleanup;

    /* 3. Обидві сторони обчислюють спільний секрет */
    uint8_t client_secret[KEY_LEN] = {0};
    uint8_t server_secret[KEY_LEN] = {0};
    size_t client_sec_len = KEY_LEN, server_sec_len = KEY_LEN;

    if (!derive_shared_secret(client_key, server_key, client_secret, &client_sec_len) ||
        !derive_shared_secret(server_key, client_key, server_secret, &server_sec_len)) {
        goto cleanup;
    }

    /* Перевірка ідентичності секретів за сталий час */
    if (CRYPTO_memcmp(client_secret, server_secret, KEY_LEN) != 0) {
        goto cleanup;
    }

    /* 4. Виведення сесійних ключів з використанням спільної солі */
    uint8_t salt[16];
    RAND_bytes(salt, sizeof(salt));
    const char *context_info = "tls13-session-v1";

    session_keys_t client_keys, server_keys;
    derive_session_keys(client_secret, KEY_LEN, salt, sizeof(salt), context_info, &client_keys);
    derive_session_keys(server_secret, KEY_LEN, salt, sizeof(salt), context_info, &server_keys);

cleanup:
    /* 5. Негайне затирання пам'яті (PFS) */
    secure_cleanse(client_secret, sizeof(client_secret));
    secure_cleanse(server_secret, sizeof(server_secret));
    if (client_key) EVP_PKEY_free(client_key);
    if (server_key) EVP_PKEY_free(server_key);
    return 0;
}
```
```cpp
#include <iostream>
#include <array>
#include <span>
#include <memory>
#include <string_view>
#include <expected>
#include <openssl/evp.h>
#include <openssl/kdf.h>
#include <openssl/rand.h>
#include <openssl/crypto.h>

namespace crypto {

inline constexpr size_t KeySize = 32;
inline constexpr size_t IvSize = 12;

struct SessionKeys {
    std::array<uint8_t, KeySize> client_write_key{};
    std::array<uint8_t, KeySize> server_write_key{};
    std::array<uint8_t, IvSize>  client_write_iv{};
    std::array<uint8_t, IvSize>  server_write_iv{};

    ~SessionKeys() {
        OPENSSL_cleanse(client_write_key.data(), client_write_key.size());
        OPENSSL_cleanse(server_write_key.data(), server_write_key.size());
        OPENSSL_cleanse(client_write_iv.data(), client_write_iv.size());
        OPENSSL_cleanse(server_write_iv.data(), server_write_iv.size());
    }
};

/* RAII-обгортка для EVP_PKEY з автоматичним затиранням */
struct EvpKeyDeleter {
    void operator()(EVP_PKEY* p) const noexcept {
        if (p) EVP_PKEY_free(p);
    }
};
using UniquePkey = std::unique_ptr<EVP_PKEY, EvpKeyDeleter>;

struct EvpCtxDeleter {
    void operator()(EVP_PKEY_CTX* c) const noexcept {
        if (c) EVP_PKEY_CTX_free(c);
    }
};
using UniquePkeyCtx = std::unique_ptr<EVP_PKEY_CTX, EvpCtxDeleter>;

class EphemeralX25519 {
public:
    static std::expected<UniquePkey, std::string_view> generate_keypair() {
        UniquePkeyCtx pctx(EVP_PKEY_CTX_new_id(EVP_PKEY_X25519, nullptr));
        if (!pctx) return std::unexpected("Failed to create X25519 context");

        EVP_PKEY* raw_key = nullptr;
        if (EVP_PKEY_keygen_init(pctx.get()) <= 0 ||
            EVP_PKEY_keygen(pctx.get(), &raw_key) <= 0) {
            return std::unexpected("Failed to generate X25519 keypair");
        }
        return UniquePkey(raw_key);
    }

    static std::expected<std::array<uint8_t, KeySize>, std::string_view>
    compute_shared_secret(EVP_PKEY* our_priv, EVP_PKEY* peer_pub) {
        UniquePkeyCtx ctx(EVP_PKEY_CTX_new(our_priv, nullptr));
        if (!ctx) return std::unexpected("Failed to initialize derivation context");

        if (EVP_PKEY_derive_init(ctx.get()) <= 0 ||
            EVP_PKEY_derive_set_peer(ctx.get(), peer_pub) <= 0) {
            return std::unexpected("Failed to set peer public key");
        }

        std::array<uint8_t, KeySize> secret{};
        size_t out_len = KeySize;
        if (EVP_PKEY_derive(ctx.get(), secret.data(), &out_len) <= 0 || out_len != KeySize) {
            OPENSSL_cleanse(secret.data(), secret.size());
            return std::unexpected("Shared secret derivation failed");
        }
        return secret;
    }

    static std::expected<SessionKeys, std::string_view>
    derive_session_keys(std::span<const uint8_t, KeySize> secret,
                        std::span<const uint8_t> salt,
                        std::string_view info) {
        std::unique_ptr<EVP_KDF, decltype(&EVP_KDF_free)> kdf(
            EVP_KDF_fetch(nullptr, "HKDF", nullptr), &EVP_KDF_free);
        if (!kdf) return std::unexpected("HKDF implementation not found");

        std::unique_ptr<EVP_KDF_CTX, decltype(&EVP_KDF_CTX_free)> kctx(
            EVP_KDF_CTX_new(kdf.get()), &EVP_KDF_CTX_free);
        if (!kctx) return std::unexpected("Failed to create HKDF context");

        char digest_name[] = "SHA256";
        std::array<OSSL_PARAM, 5> params = {
            OSSL_PARAM_construct_utf8_string("digest", digest_name, sizeof(digest_name)),
            OSSL_PARAM_construct_octet_string("key", const_cast<uint8_t*>(secret.data()), secret.size()),
            OSSL_PARAM_construct_octet_string("salt", const_cast<uint8_t*>(salt.data()), salt.size()),
            OSSL_PARAM_construct_octet_string("info", const_cast<char*>(info.data()), info.size()),
            OSSL_PARAM_construct_end()
        };

        constexpr size_t total_material_len = 2 * KeySize + 2 * IvSize;
        std::array<uint8_t, total_material_len> out_material{};

        int ret = EVP_KDF_derive(kctx.get(), out_material.data(), out_material.size(), params.data());
        if (ret <= 0) {
            OPENSSL_cleanse(out_material.data(), out_material.size());
            return std::unexpected("HKDF key derivation execution failed");
        }

        SessionKeys keys;
        std::copy_n(out_material.data(), KeySize, keys.client_write_key.begin());
        std::copy_n(out_material.data() + KeySize, KeySize, keys.server_write_key.begin());
        std::copy_n(out_material.data() + 2 * KeySize, IvSize, keys.client_write_iv.begin());
        std::copy_n(out_material.data() + 2 * KeySize + IvSize, IvSize, keys.server_write_iv.begin());

        OPENSSL_cleanse(out_material.data(), out_material.size());
        return keys;
    }
};

} // namespace crypto

int main() {
    auto client_kp = crypto::EphemeralX25519::generate_keypair();
    auto server_kp = crypto::EphemeralX25519::generate_keypair();
    if (!client_kp || !server_kp) return 1;

    auto client_sec = crypto::EphemeralX25519::compute_shared_secret(client_kp->get(), server_kp->get());
    auto server_sec = crypto::EphemeralX25519::compute_shared_secret(server_kp->get(), client_kp->get());
    if (!client_sec || !server_sec) return 1;

    // Константний час перевірки збігу секретів
    if (CRYPTO_memcmp(client_sec->data(), server_sec->data(), crypto::KeySize) != 0) {
        return 1;
    }

    std::array<uint8_t, 16> salt{};
    RAND_bytes(salt.data(), static_cast<int>(salt.size()));

    auto client_keys = crypto::EphemeralX25519::derive_session_keys(*client_sec, salt, "tls13-session-v1");
    auto server_keys = crypto::EphemeralX25519::derive_session_keys(*server_sec, salt, "tls13-session-v1");

    // Затирання проміжних секретів
    OPENSSL_cleanse(client_sec->data(), client_sec->size());
    OPENSSL_cleanse(server_sec->data(), server_sec->size());

    return (client_keys && server_keys) ? 0 : 1;
}
```
:::

### Верифікація реалізації за еталонними векторами RFC 7748

Під час розробки або аудиту коду узгодження ключів реалізація повинна обов'язково тестуватися на стандартних тестових векторах RFC 7748 Section 6.1:

* **Закритий ключ Аліси `a`:** `77076d0a7318a57d3c16c17251b26645df4c2f87ebc0992ab177fba51db92c2a`
* **Відкритий ключ Аліси `A`:** `8520f0098930a754748b7ddcb43ef75a0dbf3a0d263815f4e2c64ee2d9b04401`
* **Закритий ключ Боба `b`:** `5dab087e624a8a4b797a57349149c51e458650ee03add02f6e505f4b88f6f64d`
* **Відкритий ключ Боба `B`:** `de9edb7d7b7dc1b4d35b61c2ece435373f8343c85b78674dadfc7e146f882b4f`
* **Еталонний спільний секрет `K`:** `4a5d9d5ba4ce2de1728e3bf480350f25e07e21c947d19e3376f09b3c1e161742`

Будь-яка розбіжність у молодших або старших байтах обчисленого секрету свідчить про помилку в порядку байтів (Little-Endian / Big-Endian) або некоректне застосування бітового маскування (clamping).

### Інтеграція виведених ключів із шифрами AEAD

Отримані з HKDF симетричні ключі `client_write_key` та `server_write_key` безпосередньо передаються в конвеєри автентифікованого шифрування (AEAD), такі як **AES-256-GCM** або **ChaCha20-Poly1305**.

Наприклад, у захищеному каналі кожен мережевий пакет шифрується одноразовим вектором ініціалізації:

```
Packet_IV = Base_Write_IV ⊕ Sequence_Number
```

Операція побітового виключного АБО (XOR) базового 12-байтного вектора `Base_Write_IV` із 64-бітним монотонним лічильником пакетів `Sequence_Number` гарантує, що для одного й того самого сесійного ключа ніколи не буде використано однаковий Nonce (що запобігає катастрофічній компрометації автентичності в AEAD-шифрах).

### Інженерний аналіз та типові пастки при розробці

1. **Оптимізація мертвого коду (Dead Store Elimination):** Якщо розробник зачищає пароль чи секрет через звичайний виклик `memset(buf, 0, sizeof(buf))` безпосередньо перед звільненням пам'яті чи виходом із функції, сучасні компілятори (GCC, Clang, MSVC) з рівнем оптимізації `-O2` або `-O3` повністю видаляють цей виклик. Компілятор бачить, що буфер `buf` більше не читається в коді програми, і вважає запис нулів непотрібною операцією. Це залишає відкритий секрет у стеку або пам'яті процесу, звідки його можна викрасти через уразливості читання пам'яті (типу Heartbleed) або аналіз дампу після аварійного завершення (Core Dump). Слід використовувати виключно `OPENSSL_cleanse`, `explicit_bzero` або `sodium_memzero`.
2. **Невідповідність контексту HKDF Info:** Рядок `info` у виклику `HKDF-Expand` слугує криптографічним доменним роздільником (англ. *Domain Separation Tag*). Якщо дві системи використовують різні рядки або не включають у нього ідентифікатор версії шифронабору, виведені ключі не збігатимуться, навіть якщо спільний секрет `K` пораховано абсолютно правильно.
3. **Порівняння секретів не за константний час:** Використання стандартного `memcmp()` для перевірки ключів чи тегів автентифікації створює витік інформації через час повернення (англ. *Timing Side-Channel*): `memcmp` повертає результат після першого ж неспівпалого байта. Перевірки повинні виконуватися через `CRYPTO_memcmp()` або `sodium_memcmp()`, які завжди сканують буфер до кінця незалежно від позиції помилки.
4. **Керування ресурсами в C++:** Реалізація мовою C++20 використовує патерн RAII з користувацькими видалячами (`EvpKeyDeleter`, `EvpCtxDeleter`), що гарантує відсутність витоків дескрипторів `EVP_PKEY` та контекстів операцій навіть у разі повернення помилок на будь-якому кроці конвеєра. Тип `std::expected` забезпечує строгу типізацію статусів помилок без накладних витрат механізму винятків (Exceptions).
