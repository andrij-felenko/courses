# ⚙️ Верифікатор криптографічно підписаних оновлень прошивки з захистом від відкату

Європейський стандарт ETSI EN 303 645 (Пункт 5.3) та Регламент CRA (Додаток I, Частина I.2) встановлюють дві непорушні інженерні вимоги до процесу оновлення мікропрограмного забезпечення:
1. **Криптографічна автентифікація коду:** пристрій зобов'язаний перевіряти цифрову автентичність та цілісність будь-якого оновлення за допомогою асиметричної криптографії перед записом у робочий розділ флеш-пам'яті або передачею керування новому образу.
2. **Захист від пониження версії (Anti-Rollback):** пристрій повинен блокувати завантаження старіших версій прошивки, які містять відомі вразливості, навіть якщо вони мають повністю валідний цифровий підпис виробника.

![Ланцюг захищеного оновлення прошивки](/root/sys/sys-notary/normatyvni-vymohy-do-bezpeky-kodu/img/secure-firmware-pipeline.svg)
*Архітектурний ланцюг: від збирання образу та генерації SBOM до асиметричного підпису в HSM, перевірки відкритого ключа в eFuse та пробного запуску в системі Dual-Bank.*

## Архітектура криптографічної перевірки у вбудованих системах

Для задоволення вимог EN 303 645 та CRA завантажувач (*Bootloader*) або демон оновлення ОС повинен реалізовувати наскрізний конвеєр перевірки. Використання симетричних ключів (наприклад, спільного секрету AES чи HMAC) для підпису оновлень у споживчих пристроях категорично заборонено, оскільки вилучення цього симетричного ключа з пам'яті одного зламаного пристрою дозволить зловмисникам підписувати довільні шкідливі прошивки для всього парку пристроїв.

Тому стандарт вимагає застосування **асиметричної криптографії**:
- Закритий ключ підпису (*Private Key*) генерується і зберігається виключно в апаратному модулі безпеки (HSM / KMS) на закритому сервері розробника або в ізольованому CI/CD конвеєрі.
- Відкритий ключ перевірки (*Public Key*) зашивається в мікроконтролер на етапі виробництва в захищені одноразово програмовані комірки (eFuse / OTP) або вбудовується в апаратний корінь довіри (*Secure Element*).

Як криптографічний алгоритм підпису найчастіше обирають схему **Ed25519** (цифровий підпис на базі скрученої кривої Едвардса Edwards-curve, RFC 8032) або **ECDSA P-256 / SHA-256** (FIPS 186-4). Алгоритм Ed25519 має суттєві переваги для мікроконтролерів: фіксований компактний розмір підпису (64 байти), високу швидкість верифікації, відсутність залежності від генератора випадкових чисел під час підпису та природну стійкість до атак через аналіз сторонніх каналів витоку інформації (Side-Channel Attacks).

## Структура двійкового заголовка захищеного образу

Кожен файл оновлення прошивки містить фіксований заголовок (*Image Header*) розміром 128 байтів, що передує двійковому тілу виконуваного коду.

```
 0                   1                   2                   3
 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Magic: "CRAU" (0x43524155)              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|       HeaderVersion (0x0001)  |           Reserved1           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|               Security Version Number (SVN / Monotonic)       |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|               Binary Image Payload Size in Bytes              |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                   Payload SHA-256 Hash Digest                 +
|                            (32 Bytes)                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                   Ed25519 Asymmetric Signature                +
|                            (64 Bytes)                         |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                       Reserved / Padding (16 Bytes)           |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                                                               |
+                  Binary Firmware Executable Payload           +
|                                                               |
```

Поля заголовка (перші 48 байтів: магічне число, версія формату, номер версії безпеки SVN, розмір двійкового коду та геш SHA-256 тіла прошивки) підписуються закритим ключем виробника, а результуючий 64-байтовий підпис розміщується в полі `signature`.

## Покрокова логіка верифікатора

Верифікатор виконує сувору послідовність перевірок, де будь-яка невідповідність негайно перериває процес і повертає відповідний код помилки:
1. **Перевірка магічного числа та розміру:** верифікатор переконується, що заголовок починається з комбінації `0x43524155` ("CRAU"), версія заголовка підтримується поточною системою, а розмір тіла прошивки не перевищує розміру виділеного розділу Flash.
2. **Контроль Anti-Rollback:** верифікатор зчитує з апаратного регістра eFuse поточний номер версії безпеки `active_security_version` та звіряє його з полем `header->security_version`. Якщо `header->security_version < active_security_version`, оновлення відхиляється. Це унеможливлює атаку відкату на застарілу вразливу версію.
3. **Обчислення цілісності тіла прошивки:** обчислюється криптографічний геш SHA-256 над усім корисним навантаженням. Обчислений геш порівнюється з полем `header->payload_sha256` за постійний час (*constant-time comparison*), щоб унеможливити таймінг-атаки на побайтове порівняння.
4. **Асиметрична перевірка підпису Ed25519:** функція верифікації перевіряє підпис метаданих заголовка за допомогою вшитого відкритого ключа виробника.
5. **Захист від атак ін'єкції збоїв (Glitching Defense):** для захисту від збоїв живлення (*power glitching*), які можуть примусово змінити прапорець нульового регістра процесора в умові розгалуження `if (result == 0)`, успішний статус операції фіксується у вигляді складної багатобітової константи (`0x5AA55AA5u`), яка перевіряється повторно.

## Реалізація верифікатора: C та C++

Нижче наведено робочу реалізацію модуля верифікації прошивки двома мовами з однаковим рівнем суворості та захищеності.

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <string.h>

#define CRA_IMAGE_MAGIC          0x43524155u /* "CRAU" у порядку байтів Little-Endian */
#define CRA_HEADER_VERSION        1u
#define CRA_MAX_IMAGE_SIZE        (4u * 1024u * 1024u) /* Максимальний розмір образу 4 МБ */

#define CRA_TOKEN_SUCCESS        0x5AA55AA5u
#define CRA_TOKEN_FAILURE        0xA55AA55Au

typedef enum {
    CRA_VERIFY_OK = 0,
    CRA_ERR_NULL_POINTER,
    CRA_ERR_BAD_MAGIC,
    CRA_ERR_UNSUPPORTED_HEADER,
    CRA_ERR_IMAGE_TOO_LARGE,
    CRA_ERR_ROLLBACK_DETECTED,
    CRA_ERR_DIGEST_MISMATCH,
    CRA_ERR_INVALID_SIGNATURE
} cra_verify_status_t;

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;
    uint16_t header_version;
    uint16_t reserved1;
    uint32_t security_version;
    uint32_t image_size;
    uint8_t  payload_sha256[32];
    uint8_t  signature[64];
    uint8_t  reserved2[16];
} cra_image_header_t;
#pragma pack(pop)

/* Зовнішні криптографічні примітиви апаратного прискорювача або mbedTLS */
extern int crypto_sha256(const uint8_t *data, size_t len, uint8_t hash_out[32]);
extern int crypto_ed25519_verify(const uint8_t sig[64], const uint8_t *msg, size_t msg_len, const uint8_t pubkey[32]);

/* Безпечне порівняння буферів за постійний час для захисту від таймінг-атак */
static bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t diff = 0;
    for (size_t i = 0; i < len; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}

cra_verify_status_t cra_verify_firmware(
    const cra_image_header_t *header,
    const uint8_t *payload,
    uint32_t active_security_version,
    const uint8_t root_public_key[32]
) {
    if (!header || !payload || !root_public_key) {
        return CRA_ERR_NULL_POINTER;
    }

    /* 1. Перевірка магічного числа заголовка */
    if (header->magic != CRA_IMAGE_MAGIC) {
        return CRA_ERR_BAD_MAGIC;
    }

    if (header->header_version != CRA_HEADER_VERSION) {
        return CRA_ERR_UNSUPPORTED_HEADER;
    }

    if (header->image_size == 0 || header->image_size > CRA_MAX_IMAGE_SIZE) {
        return CRA_ERR_IMAGE_TOO_LARGE;
    }

    /* 2. Захист від пониження версії (Anti-Rollback за EN 303 645) */
    if (header->security_version < active_security_version) {
        return CRA_ERR_ROLLBACK_DETECTED;
    }

    /* 3. Перевірка цілісності корисного навантаження через SHA-256 */
    uint8_t computed_digest[32];
    if (crypto_sha256(payload, header->image_size, computed_digest) != 0) {
        return CRA_ERR_DIGEST_MISMATCH;
    }

    if (!constant_time_memcmp(computed_digest, header->payload_sha256, 32)) {
        return CRA_ERR_DIGEST_MISMATCH;
    }

    /* 4. Перевірка цифрового підпису заголовка */
    /* Підписуються перші 48 байтів структури (magic, версії, розмір, геш образу) */
    size_t signed_metadata_len = offsetof(cra_image_header_t, signature);
    uint32_t verify_token = CRA_TOKEN_FAILURE;

    if (crypto_ed25519_verify(header->signature, (const uint8_t *)header, signed_metadata_len, root_public_key) == 0) {
        verify_token = CRA_TOKEN_SUCCESS;
    }

    /* Подвійна перевірка токена проти збоїв у регістрах (glitch attack mitigation) */
    if (verify_token != CRA_TOKEN_SUCCESS || verify_token == CRA_TOKEN_FAILURE) {
        return CRA_ERR_INVALID_SIGNATURE;
    }

    return CRA_VERIFY_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <array>
#include <expected>
#include <algorithm>

namespace cra {

constexpr uint32_t ImageMagic = 0x43524155u; // "CRAU"
constexpr uint16_t HeaderVersion = 1u;
constexpr size_t MaxImageSize = 4u * 1024u * 1024u;

constexpr uint32_t TokenSuccess = 0x5AA55AA5u;
constexpr uint32_t TokenFailure = 0xA55AA55Au;

enum class VerifyError : uint8_t {
    InvalidMagic,
    UnsupportedVersion,
    InvalidImageSize,
    RollbackViolation,
    DigestMismatch,
    SignatureInvalid,
    CryptoFailure
};

#pragma pack(push, 1)
struct ImageHeader {
    uint32_t magic;
    uint16_t header_version;
    uint16_t reserved1;
    uint32_t security_version;
    uint32_t image_size;
    std::array<uint8_t, 32> payload_sha256;
    std::array<uint8_t, 64> signature;
    std::array<uint8_t, 16> reserved2;
};
#pragma pack(pop)

// Зовнішні криптографічні функції платформи
extern "C" int crypto_sha256(const uint8_t* data, size_t len, uint8_t hash_out[32]);
extern "C" int crypto_ed25519_verify(const uint8_t sig[64], const uint8_t* msg, size_t msg_len, const uint8_t pubkey[32]);

[[nodiscard]] inline bool constant_time_equal(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) return false;
    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}

class FirmwareVerifier {
public:
    explicit constexpr FirmwareVerifier(std::span<const uint8_t, 32> root_public_key) noexcept
        : root_key_(root_public_key) {}

    [[nodiscard]] std::expected<void, VerifyError> verify(
        const ImageHeader& header,
        std::span<const uint8_t> payload,
        uint32_t active_security_version
    ) const noexcept {
        if (header.magic != ImageMagic) {
            return std::unexpected(VerifyError::InvalidMagic);
        }

        if (header.header_version != HeaderVersion) {
            return std::unexpected(VerifyError::UnsupportedVersion);
        }

        if (header.image_size == 0 || header.image_size > MaxImageSize || header.image_size != payload.size()) {
            return std::unexpected(VerifyError::InvalidImageSize);
        }

        // Anti-Rollback перевірка за EN 303 645 Cl. 5.3
        if (header.security_version < active_security_version) {
            return std::unexpected(VerifyError::RollbackViolation);
        }

        // Перевірка цілісності коду SHA-256
        std::array<uint8_t, 32> computed_digest{};
        if (crypto_sha256(payload.data(), payload.size(), computed_digest.data()) != 0) {
            return std::unexpected(VerifyError::CryptoFailure);
        }

        if (!constant_time_equal(computed_digest, header.payload_sha256)) {
            return std::unexpected(VerifyError::DigestMismatch);
        }

        // Перевірка підпису метаданих заголовка
        constexpr size_t signed_len = offsetof(ImageHeader, signature);
        const auto* header_bytes = reinterpret_cast<const uint8_t*>(&header);
        uint32_t verify_token = TokenFailure;

        if (crypto_ed25519_verify(header.signature.data(), header_bytes, signed_len, root_key_.data()) == 0) {
            verify_token = TokenSuccess;
        }

        if (verify_token != TokenSuccess || verify_token == TokenFailure) {
            return std::unexpected(VerifyError::SignatureInvalid);
        }

        return {};
    }

private:
    std::span<const uint8_t, 32> root_key_;
};

} // namespace cra
```
:::

## Інженерні пастки реалізації та крайові випадки

1. **Атака підміни під час виконання (TOCTOU — Time-of-Check to Time-of-Use):** Якщо завантажувач перевіряє підпис прошивки в оперативній пам'яті (RAM), а потім записує її в зовнішню мікросхему SPI Flash, зловмисник може перехопити керування лініями шини SPI (*SPI Glitching / Interposer*) і модифікувати байти коду вже після проходження перевірки підпису. **Правильне рішення:** записувати образ безпосередньо у пасивний банк флеш-пам'яті (Dual-Bank), зчитувати байти безпосередньо з Flash для обчислення SHA-256 та верифікації підпису, і лише після цього атомарно перемикати вказівник активного слота завантаження.
2. **Передчасне спалювання лічильника eFuse:** Якщо пропалити новий номер версії `SVN` в апаратний лічильник eFuse до першого успішного старту нової операційної системи, помилка ініціалізації периферійного драйвера перетворить пристрій на «цеглину» (*hard brick*), оскільки відкат на стабільну попередню версію буде заблокований цим же механізмом захисту. **Правильне рішення:** лічильник `SVN` пропалюється в eFuse лише після того, як нова прошивка завершила повну системну самодіагностику та підтвердила успішний старт сторожовому таймеру (Watchdog).
3. **Зберігання відкритого ключа у незахищеній пам'яті:** Якщо відкритий ключ верифікації зберігається у звичайному секторі Flash, зловмисник через налагоджувальний інтерфейс UART/JTAG або вразливість переповнення буфера може перезаписати цей ключ власним відкритим ключем. Відкритий ключ повинен зберігатися в одноразово програмованих комірках OTP/eFuse або захищеному апаратному модулі довіри (Secure Element).
4. **Обробка потокового хешування для систем із малим обсягом RAM:** На мікроконтролерах із 32–64 КБ оперативної пам'яті завантаження 4-мегабайтного образу прошивки в RAM є фізично неможливим. У реальних системах функція `crypto_sha256` виконується потоково: послідовними викликами `sha256_init()`, `sha256_update()` блоками по 512–4096 байтів безпосередньо з флеш-пам'яті, та `sha256_final()`.
