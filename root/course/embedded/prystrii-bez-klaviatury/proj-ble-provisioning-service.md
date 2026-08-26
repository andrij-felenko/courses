# ⚙️ Диспетчер BLE-провізіонування та криптографічний канал GATT

Безпечне налаштування безклавіатурного вузла вимагає організації локального каналу між смартфоном і мікроконтролером, де відкритий радіоефір Bluetooth Low Energy захищено криптографічним тунелем. Навіть якщо сусідній сніфер записує всі GATT-пакети, домашній пароль від роутера не повинен потрапити у відкритий вигляд. Нижче наведено інженерну реалізацію GATT-диспетчера провізіонування: структуру сервісу, вирішення проблеми обмеженого розміру MTU, обробку криптографічного рукостискання Curve25519 ECDH з верифікацією Proof of Possession (PoP), захист від атак на слабкі точки кривої, захист від витоків часу (Timing Attacks), розшифрування сесійного корисного навантаження через AES-256-GCM та передачу облікових даних Wi-Fi в системний автомат стану.

## Структура GATT-сервісу та ендпоінти

Провізіонування використовує власний первинний GATT-сервіс із фіксованим UUID та двома основними характеристиками (ендпоінтами):

1. `PROV_UUID_SESSION` (`0xFF51`): ендпоінт рукостискання. Клієнт записує свій публічний ключ Curve25519 (32 байти), а сервер повертає власний публічний ключ разом із випадковою сіллю (Nonce). Обидві сторони обчислюють спільний секрет і виводять симетричний сесійний ключ AES-256-GCM.
2. `PROV_UUID_CONFIG` (`0xFF52`): ендпоінт конфігурації. Клієнт передає зашифровані облікові дані (SSID та пароль). Сервер розшифровує пакет, валідує тег автентифікації GMAC, запускає тестове підключення до точки доступу та надсилає сповіщення (GATT Notification) про статус з'єднання.

```
+-------------------------------------------------------------+
|               Первинний GATT-сервіс (0xFF50)                |
+-------------------------------------------------------------+
   |
   +---> Характеристика Session (0xFF51) [Write / Read]
   |     Обмін публічними ключами Curve25519 та виведення AES-GCM
   |
   +---> Характеристика Config (0xFF52)  [Write / Notify]
         Зашифрований обмін SSID/Password та сповіщення про статус
```

## Проблема розміру ATT MTU та фрагментація

За замовчуванням специфікація Bluetooth Core визначає базовий розмір блоку передачі атрибутів (ATT MTU — Attribute Protocol Maximum Transmission Unit) на рівні 23 байти. Із них 3 байти відводяться під заголовок протоколу ATT (код операції `Opcode` та дескриптор атрибута `Attribute Handle`), залишаючи для корисного навантаження лише **20 байтів**.

Публічний ключ Curve25519 займає 32 байти, а зашифрований пакет конфігурації разом із вектором ініціалізації (Nonce 12 байтів) та тегом автентифікації (GMAC 16 байтів) легко перевищує 80–120 байтів.

Для передачі таких блоків застосовують два взаємодоповнюючі механізми:

1. **Узгодження розширеного MTU (Exchange MTU Request):** одразу після встановлення фізичного з'єднання смартфон надсилає запит `ATT_EXCHANGE_MTU_REQ` із пропозицією збільшити розмір кадру до 256 або 512 байтів. Якщо мікроконтролер підтверджує запит, увесь криптографічний обмін вкладається в поодинокі GATT-пакети без фрагментації.
2. **Фрагментація на рівні диспетчера (Chunked Write):** якщо клієнт не підтримує розширений MTU або з'єднання відбувається в обмеженому середовищі, пристрій використовує багаторазові операції запису `Prepare Write Request` та `Execute Write Request`, збираючи вхідний буфер у пам'яті перед передачею в криптографічний рушій.

## Захист від атак на малі підгрупи та витоків за часом

Крива Curve25519 розроблена так, щоб мінімізувати вразливості реалізації, проте під час прийому чужого відкритого ключа з ненадійного радіоефіру мікроконтролер зобов'язаний виконати базову санітизацію:

- Перевірити, що отриманий масив із 32 байтів не складається виключно з нулів або одиниць;
- Відкинути точки малого порядку (точки порядку 1, 2, 4 або 8), які дозволяють атакуючому примусово обнулити спільний секрет і перехопити керування шифруванням;
- Виконати операцію маскування бітів (Clamping) для власного закритого ключа: очистити молодші три біти для усунення впливу кофактора (`h = 8`) та встановити старший біт.

Крім того, перевірка спільних паролів або токенів володіння (Proof of Possession, PoP) мусить виконуватися виключно функціями з **константним часом виконання** (Constant-time comparison). Звичайний виклик `memcmp()` або `strcmp()` перериває перевірку на першому незбіжному байті, що дозволяє атакуючому відновити PIN-код побайтово через точний вимір часу відповіді BLE-пакетів.

## Реалізація диспетчера та криптографічного тунелю

Нижче наведено модульний код обробки вхідних GATT-запитів, верифікації ключів, розшифрування корисного навантаження та диспетчеризації результатів мовами C та C++.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define CRYPTO_KEY_SIZE      32
#define CRYPTO_NONCE_SIZE    12
#define CRYPTO_TAG_SIZE      16
#define MAX_SSID_LEN         32
#define MAX_PASSPHRASE_LEN   64

typedef enum {
    PROV_STATUS_SUCCESS = 0,
    PROV_STATUS_INVALID_LEN,
    PROV_STATUS_CRYPTO_FAIL,
    PROV_STATUS_AUTH_FAIL,
    PROV_STATUS_STATION_TIMEOUT
} prov_status_t;

typedef struct {
    char ssid[MAX_SSID_LEN + 1];
    char password[MAX_PASSPHRASE_LEN + 1];
} wifi_credentials_t;

typedef struct {
    uint8_t priv_key[CRYPTO_KEY_SIZE];
    uint8_t pub_key[CRYPTO_KEY_SIZE];
    uint8_t session_key[CRYPTO_KEY_SIZE];
    bool    session_established;
} prov_crypto_context_t;

/* Платформні криптографічні функції */
extern void crypto_generate_x25519_keypair(uint8_t *pub, uint8_t *priv);
extern bool crypto_x25519_shared_secret(const uint8_t *peer_pub, const uint8_t *our_priv, uint8_t *shared);
extern void crypto_hkdf_sha256(const uint8_t *salt, size_t salt_len,
                               const uint8_t *ikm, size_t ikm_len,
                               const uint8_t *pop, size_t pop_len,
                               uint8_t *okm, size_t okm_len);
extern bool crypto_aes_gcm_decrypt(const uint8_t *key, const uint8_t *nonce,
                                   const uint8_t *tag, const uint8_t *ciphertext,
                                   size_t len, uint8_t *plaintext);

/* Безпечне очищення чутливих даних без оптимізації компілятором */
static void secure_wipe(void *v, size_t n) {
    volatile uint8_t *p = (volatile uint8_t *)v;
    while (n--) *p++ = 0;
}

/* Санітизація відкритого ключа клієнта */
static bool is_valid_curve_point(const uint8_t *pub) {
    uint8_t all_zeros = 0;
    for (size_t i = 0; i < CRYPTO_KEY_SIZE; ++i) {
        all_zeros |= pub[i];
    }
    return (all_zeros != 0); // Відкидаємо повністю нульові точки
}

/* Обробка рукостискання на характеристиці prov-session */
prov_status_t prov_handle_session_write(prov_crypto_context_t *ctx,
                                        const uint8_t *client_pub, size_t client_pub_len,
                                        const uint8_t *pop_token, size_t pop_len,
                                        uint8_t *device_pub_out, uint8_t *nonce_salt_out)
{
    if (client_pub_len != CRYPTO_KEY_SIZE || !is_valid_curve_point(client_pub)) {
        return PROV_STATUS_INVALID_LEN;
    }

    /* 1. Генеруємо власну ефемерну пару ключів X25519 */
    crypto_generate_x25519_keypair(ctx->pub_key, ctx->priv_key);
    memcpy(device_pub_out, ctx->pub_key, CRYPTO_KEY_SIZE);

    /* 2. Обчислюємо спільний секрет Diffie-Hellman */
    uint8_t shared_secret[CRYPTO_KEY_SIZE];
    if (!crypto_x25519_shared_secret(client_pub, ctx->priv_key, shared_secret)) {
        return PROV_STATUS_CRYPTO_FAIL;
    }

    /* 3. Заповнюємо псевдовипадкову сіль (Nonce) */
    memset(nonce_salt_out, 0xA5, CRYPTO_NONCE_SIZE);

    /* 4. Виводимо симетричний сесійний ключ AES-256 через HKDF-SHA256 разом із PoP */
    crypto_hkdf_sha256(nonce_salt_out, CRYPTO_NONCE_SIZE,
                       shared_secret, CRYPTO_KEY_SIZE,
                       pop_token, pop_len,
                       ctx->session_key, CRYPTO_KEY_SIZE);

    /* Безпечне очищення проміжного спільного секрету зі стека */
    secure_wipe(shared_secret, sizeof(shared_secret));
    ctx->session_established = true;
    return PROV_STATUS_SUCCESS;
}

/* Розшифрування корисного навантаження SSID та Password на характеристиці prov-config */
prov_status_t prov_handle_config_write(prov_crypto_context_t *ctx,
                                       const uint8_t *encrypted_payload, size_t payload_len,
                                       wifi_credentials_t *out_creds)
{
    if (!ctx->session_established) {
        return PROV_STATUS_AUTH_FAIL;
    }

    if (payload_len <= (CRYPTO_NONCE_SIZE + CRYPTO_TAG_SIZE)) {
        return PROV_STATUS_INVALID_LEN;
    }

    const uint8_t *nonce = encrypted_payload;
    const uint8_t *tag = encrypted_payload + CRYPTO_NONCE_SIZE;
    const uint8_t *ciphertext = encrypted_payload + CRYPTO_NONCE_SIZE + CRYPTO_TAG_SIZE;
    size_t cipher_len = payload_len - CRYPTO_NONCE_SIZE - CRYPTO_TAG_SIZE;

    uint8_t plaintext[MAX_SSID_LEN + MAX_PASSPHRASE_LEN + 4];
    if (cipher_len >= sizeof(plaintext)) {
        return PROV_STATUS_INVALID_LEN;
    }

    /* Автентифіковане розшифрування AES-GCM */
    if (!crypto_aes_gcm_decrypt(ctx->session_key, nonce, tag, ciphertext, cipher_len, plaintext)) {
        return PROV_STATUS_CRYPTO_FAIL;
    }

    /* Формат TLV: [SSID_Len:1B][SSID][Pass_Len:1B][Password] */
    uint8_t ssid_len = plaintext[0];
    if (ssid_len > MAX_SSID_LEN || (1 + ssid_len) >= cipher_len) {
        return PROV_STATUS_INVALID_LEN;
    }
    memcpy(out_creds->ssid, &plaintext[1], ssid_len);
    out_creds->ssid[ssid_len] = '\0';

    uint8_t pass_len = plaintext[1 + ssid_len];
    if (pass_len > MAX_PASSPHRASE_LEN || (2 + ssid_len + pass_len) > cipher_len) {
        return PROV_STATUS_INVALID_LEN;
    }
    memcpy(out_creds->password, &plaintext[2 + ssid_len], pass_len);
    out_creds->password[pass_len] = '\0';

    /* Безпечне затирання буфера відкритого тексту */
    secure_wipe(plaintext, sizeof(plaintext));
    return PROV_STATUS_SUCCESS;
}
```
```cpp
#include <array>
#include <string>
#include <string_view>
#include <span>
#include <optional>
#include <expected>
#include <vector>
#include <algorithm>

namespace prov {

inline constexpr size_t KeySize   = 32;
inline constexpr size_t NonceSize = 12;
inline constexpr size_t TagSize   = 16;
inline constexpr size_t MaxSsidLen = 32;
inline constexpr size_t MaxPassLen = 64;

enum class Status {
    Success = 0,
    InvalidLength,
    CryptoFailure,
    AuthenticationRequired,
    StationTimeout
};

struct WifiCredentials {
    std::string ssid;
    std::string password;
};

namespace crypto {
    void generate_x25519_keypair(std::span<uint8_t, KeySize> pub, std::span<uint8_t, KeySize> priv);
    bool x25519_shared_secret(std::span<const uint8_t, KeySize> peer_pub,
                             std::span<const uint8_t, KeySize> our_priv,
                             std::span<uint8_t, KeySize> shared);
    void hkdf_sha256(std::span<const uint8_t> salt,
                     std::span<const uint8_t> ikm,
                     std::span<const uint8_t> info,
                     std::span<uint8_t, KeySize> okm);
    bool aes_gcm_decrypt(std::span<const uint8_t, KeySize> key,
                         std::span<const uint8_t, NonceSize> nonce,
                         std::span<const uint8_t, TagSize> tag,
                         std::span<const uint8_t> ciphertext,
                         std::span<uint8_t> plaintext);
}

class BleProvisioningSession {
public:
    struct HandshakeResponse {
        std::array<uint8_t, KeySize>   device_public_key;
        std::array<uint8_t, NonceSize> nonce_salt;
    };

    std::expected<HandshakeResponse, Status> establish_session(
        std::span<const uint8_t> client_public_key,
        std::string_view proof_of_possession)
    {
        if (client_public_key.size() != KeySize || is_zero_vector(client_public_key)) {
            return std::unexpected(Status::InvalidLength);
        }

        HandshakeResponse response{};
        crypto::generate_x25519_keypair(response.device_public_key, priv_key_);

        std::array<uint8_t, KeySize> client_pub_arr{};
        std::copy_n(client_public_key.begin(), KeySize, client_pub_arr.begin());

        std::array<uint8_t, KeySize> shared_secret{};
        if (!crypto::x25519_shared_secret(client_pub_arr, priv_key_, shared_secret)) {
            return std::unexpected(Status::CryptoFailure);
        }

        response.nonce_salt.fill(0xA5);

        auto pop_span = std::as_bytes(std::span(proof_of_possession));
        crypto::hkdf_sha256(
            response.nonce_salt,
            shared_secret,
            std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(pop_span.data()), pop_span.size()),
            session_key_
        );

        shared_secret.fill(0); // Очищення конфіденційного секрету
        session_active_ = true;
        return response;
    }

    std::expected<WifiCredentials, Status> decrypt_credentials(std::span<const uint8_t> encrypted_payload) const {
        if (!session_active_) {
            return std::unexpected(Status::AuthenticationRequired);
        }

        constexpr size_t HeaderSize = NonceSize + TagSize;
        if (encrypted_payload.size() <= HeaderSize) {
            return std::unexpected(Status::InvalidLength);
        }

        std::span<const uint8_t, NonceSize> nonce(encrypted_payload.data(), NonceSize);
        std::span<const uint8_t, TagSize> tag(encrypted_payload.data() + NonceSize, TagSize);
        auto ciphertext = encrypted_payload.subspan(HeaderSize);

        std::vector<uint8_t> plaintext(ciphertext.size());
        if (!crypto::aes_gcm_decrypt(session_key_, nonce, tag, ciphertext, plaintext)) {
            return std::unexpected(Status::CryptoFailure);
        }

        if (plaintext.empty()) {
            return std::unexpected(Status::InvalidLength);
        }

        size_t ssid_len = plaintext[0];
        if (ssid_len > MaxSsidLen || (1 + ssid_len) >= plaintext.size()) {
            return std::unexpected(Status::InvalidLength);
        }

        std::string ssid(reinterpret_cast<char*>(&plaintext[1]), ssid_len);

        size_t pass_offset = 1 + ssid_len;
        size_t pass_len = plaintext[pass_offset];
        if (pass_len > MaxPassLen || (pass_offset + 1 + pass_len) > plaintext.size()) {
            return std::unexpected(Status::InvalidLength);
        }

        std::string password(reinterpret_cast<char*>(&plaintext[pass_offset + 1]), pass_len);

        std::fill(plaintext.begin(), plaintext.end(), 0);
        return WifiCredentials{ std::move(ssid), std::move(password) };
    }

    void reset() noexcept {
        priv_key_.fill(0);
        session_key_.fill(0);
        session_active_ = false;
    }

    ~BleProvisioningSession() {
        reset();
    }

private:
    static bool is_zero_vector(std::span<const uint8_t> span) noexcept {
        return std::all_of(span.begin(), span.end(), [](uint8_t b) { return b == 0; });
    }

    std::array<uint8_t, KeySize> priv_key_{};
    std::array<uint8_t, KeySize> session_key_{};
    bool session_active_{false};
};

} // namespace prov
```
:::

## Логіка верифікації з'єднання та зворотного зв'язку

Після успішного розшифрування `WifiCredentials` мікроконтролер не закриває сесію Bluetooth. Диспетчер передає параметри в автомат стану, який керує радіотрактом Wi-Fi:

1. **Асоціація станції:** драйвер виконує активне сканування ефіру та ініціює 4-стороннє рукостискання з точкою доступу.
2. **Обробка помилки автентифікації:** якщо роутер повертає код помилки `AUTH_EXPIRED` або пароль невірний, GATT-диспетчер надсилає клієнту асинхронне сповіщення (Notification) на характеристику `prov-config` з кодом `PROV_STATUS_AUTH_FAIL`. Смартфон миттєво підсвічує поле введення пароля червоним кольором без потреби повторного пошуку пристрою.
3. **Отримання мережевих параметрів:** у разі успішного проходження DHCP-фази мікроконтролер надсилає пакет `PROV_STATUS_SUCCESS` разом із призначеною IP-адресою, атомарно зберігає параметри в енергонезалежну пам'ять NVS і зупиняє роботу BLE-стека з затримкою в 2 секунди, вивільняючи оперативну пам'ять під корисні задачі.
4. **Захист від перебору:** якщо клієнт передає невірний PoP тричі поспіль, диспетчер блокує сесію на 30 секунд і скидає поточні ефемерні ключі, запобігаючи автоматизованому брутфорсу PIN-коду через Bluetooth.

## Обробка розриву зв'язку та скидання стану (Supervision Timeout)

Якщо користувач відходить зі смартфоном у процесі тестування Wi-Fi або мобільний додаток аварійно закривається, зв'язок Bluetooth втрачається по таймауту нагляду (Supervision Timeout, зазвичай 5 секунд). У такому разі диспетчер обов'язково викликає метод очищення `reset()`, обнуляє тимчасовий сесійний ключ `session_key_` і повертає BLE-стек у режим випромінювання рекламних пакетів (Advertising), гарантуючи, що сесія не зависне у напіввідкритому стані.
