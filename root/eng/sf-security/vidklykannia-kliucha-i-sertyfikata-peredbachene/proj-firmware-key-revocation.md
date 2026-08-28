# ⚙️ Реалізація перевірки та ротації ключів прошивки з апаратним захистом eFuse

Коли у виробництві випускається партія промислових пристроїв або контролерів з розрахунком на 10–15 років автономної експлуатації, жорстко зашивати в код первинного завантажувача (ROM Bootloader) єдиний відкритий ключ для перевірки цифрового підпису прошивок є неприпустимим архітектурним ризиком. У випадку витоку приватного ключа з сервера збирання або розкриття криптографічного алгоритму виробник опиняється перед вибором: або назавжди втратити контроль над безпекою пристроїв, або фізично відкликати весь парк обладнання з експлуатації.

Цей модуль реалізує систему багаторівневої перевірки та апаратної ротації ключів безпечного завантаження (Secure Boot):
1. Апаратна пам'ять eFuse зберігає геші чотирьох незалежних кореневих ключів OEM (Root of Trust Slots 0..3).
2. Одноразово програмований регістр eFuse містить бітову маску анулювання скомпрометованих ключів (Revocation Bitmask).
3. Монотонний апаратний лічильник захищає пристрій від атак на відкат версії (Anti-Rollback Protection).
4. Механізм міграції виконує безпечний перехід на резервний ключ з атомарним перепалюванням перемички скомпрометованого слота.

---

## 1. Архітектурна модель та структури даних

У надійній вбудованій системі корінь довіри (Root of Trust) розподіляється між незмінним первинним завантажувачем у Mask ROM та областю одноразово програмованої пам'яті (One-Time Programmable, OTP / eFuse). Замість зберігання повних відкритих ключів ECDSA у дефіцитній пам'яті eFuse зберігаються їхні 256-бітні криптографічні дайджести SHA-256. Сам відкритий ключ передається всередині підписаного заголовка кожного бінарного образу прошивки.

Заголовок бінарного образу містить магічне число для ідентифікації формату, версію прошивки, індекс цільового слота ключа, довжину корисного навантаження, відкритий ключ ECDSA P-256, підпис та контрольний дайджест.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define OEM_KEY_SLOTS           4
#define SHA256_DIGEST_SIZE      32
#define SIGNATURE_SIZE          64
#define FW_MAGIC                0x53454355  /* "SECU" */

/* Заголовок образу прошивки */
typedef struct {
    uint32_t magic;
    uint32_t fw_version;
    uint32_t key_slot_index;
    uint32_t payload_length;
    uint8_t  public_key[64];       /* Відкритий ключ ECDSA P-256 (X, Y) */
    uint8_t  signature[SIGNATURE_SIZE]; /* Підпис заголовка та корисного навантаження */
    uint8_t  payload_sha256[SHA256_DIGEST_SIZE];
} __attribute__((packed)) FirmwareHeader;

/* Апаратний стан підсистеми eFuse мікроконтролера */
typedef struct {
    uint8_t  root_key_hashes[OEM_KEY_SLOTS][SHA256_DIGEST_SIZE];
    uint32_t revoked_keys_mask;     /* Біт i = 1: Слот i анульовано назавжди */
    uint32_t monotonic_version;     /* Мінімально допустима версія прошивки */
    bool     security_locked;       /* Блокування зміни заводських гешів */
} HardwareEfuseBank;

/* Результати валідації безпечного завантаження */
typedef enum {
    BOOT_OK = 0,
    BOOT_ERR_INVALID_MAGIC,
    BOOT_ERR_KEY_SLOT_OUT_OF_BOUNDS,
    BOOT_ERR_KEY_REVOKED,
    BOOT_ERR_KEY_HASH_MISMATCH,
    BOOT_ERR_VERSION_ROLLBACK,
    BOOT_ERR_PAYLOAD_CORRUPTED,
    BOOT_ERR_SIGNATURE_INVALID,
    BOOT_ERR_EFUSE_BURN_FAILED
} BootResult;
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>
#include <algorithm>

inline constexpr std::size_t OemKeySlots = 4;
inline constexpr std::size_t Sha256DigestSize = 32;
inline constexpr std::size_t SignatureSize = 64;
inline constexpr std::size_t PublicKeySize = 64;
inline constexpr std::uint32_t FwMagic = 0x53454355; // "SECU"

enum class BootError : std::uint8_t {
    InvalidMagic,
    KeySlotOutOfBounds,
    KeyRevoked,
    KeyHashMismatch,
    VersionRollback,
    PayloadCorrupted,
    SignatureInvalid,
    EfuseBurnFailed
};

#pragma pack(push, 1)
struct FirmwareHeader {
    std::uint32_t magic;
    std::uint32_t fw_version;
    std::uint32_t key_slot_index;
    std::uint32_t payload_length;
    std::array<std::uint8_t, PublicKeySize> public_key;
    std::array<std::uint8_t, SignatureSize> signature;
    std::array<std::uint8_t, Sha256DigestSize> payload_sha256;
};
#pragma pack(pop)

struct HardwareEfuseBank {
    std::array<std::array<std::uint8_t, Sha256DigestSize>, OemKeySlots> root_key_hashes;
    std::uint32_t revoked_keys_mask{0};
    std::uint32_t monotonic_version{0};
    bool security_locked{true};
};
```
:::

---

## 2. Логіка верифікації та апаратного захисту

Послідовність перевірки безпечного завантаження виконується як суворий покроковий конвеєр із розривом виконання при першій же невідповідності:

1. **Контроль структури**: Перевірка магічного числа `FW_MAGIC` та діапазону слота `key_slot_index < OEM_KEY_SLOTS`.
2. **Апаратне відкликання**: Перевірка `revoked_keys_mask & (1 << key_slot_index)`. Якщо біт у регістрі eFuse встановлено в `1`, ключ вважається фізично спаленим і виконання негайно зупиняється.
3. **Автентифікація відкритого ключа**: Обчислення `SHA256(header.public_key)` та побайтове порівняння з заводським дайджестом `root_key_hashes[key_slot_index]`. Це гарантує, що відкритий ключ у заголовку дійсно належить виробнику обладнання.
4. **Контроль відкату версії (Anti-Rollback)**: Перевірка `header.fw_version >= monotonic_version`. Запобігає запуску старих уразливих прошивок.
5. **Контроль цілісності корисного навантаження**: Обчислення гешу образу та звірка з `payload_sha256`.
6. **Перевірка цифрового підпису**: Валідація підпису ECDSA `(R, S)` за допомогою перевіреного відкритого ключа.
7. **Атомарне оновлення апаратного лічильника**: Якщо нова прошивка має версію `fw_version > monotonic_version`, завантажувач допалює фізичні перемички монотонного лічильника eFuse.

:::tabs
```c
/* Допоміжні функції криптографії (заглушки для стандартизованих крипторушіїв) */
bool crypto_sha256(const uint8_t *data, size_t len, uint8_t *digest_out);
bool crypto_ecdsa_verify(const uint8_t *pub_key, const uint8_t *digest, const uint8_t *signature);
bool hardware_burn_efuse_bit(HardwareEfuseBank *efuse, uint32_t bit_index);
bool hardware_update_monotonic_counter(HardwareEfuseBank *efuse, uint32_t new_version);

BootResult verify_and_authorize_firmware(
    HardwareEfuseBank *efuse,
    const FirmwareHeader *header,
    const uint8_t *payload_data,
    bool auto_burn_version)
{
    if (header->magic != FW_MAGIC) {
        return BOOT_ERR_INVALID_MAGIC;
    }

    if (header->key_slot_index >= OEM_KEY_SLOTS) {
        return BOOT_ERR_KEY_SLOT_OUT_OF_BOUNDS;
    }

    /* 1. Перевірка бітової маски відкликання eFuse */
    if ((efuse->revoked_keys_mask & (1U << header->key_slot_index)) != 0) {
        return BOOT_ERR_KEY_REVOKED;
    }

    /* 2. Звірка гешу публічного ключа з апаратним слотом */
    uint8_t computed_key_hash[SHA256_DIGEST_SIZE];
    if (!crypto_sha256(header->public_key, sizeof(header->public_key), computed_key_hash)) {
        return BOOT_ERR_KEY_HASH_MISMATCH;
    }

    if (memcmp(computed_key_hash, efuse->root_key_hashes[header->key_slot_index], SHA256_DIGEST_SIZE) != 0) {
        return BOOT_ERR_KEY_HASH_MISMATCH;
    }

    /* 3. Перевірка версії проти апаратного лічильника відкату */
    if (header->fw_version < efuse->monotonic_version) {
        return BOOT_ERR_VERSION_ROLLBACK;
    }

    /* 4. Перевірка цілісності корисного навантаження */
    uint8_t computed_payload_hash[SHA256_DIGEST_SIZE];
    if (!crypto_sha256(payload_data, header->payload_length, computed_payload_hash)) {
        return BOOT_ERR_PAYLOAD_CORRUPTED;
    }

    if (memcmp(computed_payload_hash, header->payload_sha256, SHA256_DIGEST_SIZE) != 0) {
        return BOOT_ERR_PAYLOAD_CORRUPTED;
    }

    /* 5. Перевірка криптографічного підпису образу */
    if (!crypto_ecdsa_verify(header->public_key, computed_payload_hash, header->signature)) {
        return BOOT_ERR_SIGNATURE_INVALID;
    }

    /* 6. Якщо версія новіша і підтверджена — спалюємо біти лічильника відкату */
    if (auto_burn_version && header->fw_version > efuse->monotonic_version) {
        if (!hardware_update_monotonic_counter(efuse, header->fw_version)) {
            return BOOT_ERR_EFUSE_BURN_FAILED;
        }
    }

    return BOOT_OK;
}

/* Функція екстреного або планового анулювання скомпрометованого ключа */
BootResult revoke_key_slot(HardwareEfuseBank *efuse, uint32_t slot_to_revoke)
{
    if (slot_to_revoke >= OEM_KEY_SLOTS) {
        return BOOT_ERR_KEY_SLOT_OUT_OF_BOUNDS;
    }

    /* Спалюємо відповідний біт eFuse (однобічна операція 0 -> 1) */
    if (!hardware_burn_efuse_bit(efuse, slot_to_revoke)) {
        return BOOT_ERR_EFUSE_BURN_FAILED;
    }

    efuse->revoked_keys_mask |= (1U << slot_to_revoke);
    return BOOT_OK;
}
```
```cpp
namespace Security {

// Оголошення криптографічних інтерфейсів платформи
bool Sha256(std::span<const std::uint8_t> data, std::span<std::uint8_t, Sha256DigestSize> out_digest) noexcept;
bool EcdsaVerify(std::span<const std::uint8_t, PublicKeySize> pub_key,
                 std::span<const std::uint8_t, Sha256DigestSize> digest,
                 std::span<const std::uint8_t, SignatureSize> signature) noexcept;
bool BurnEfuseBit(HardwareEfuseBank& efuse, std::uint32_t bit_index) noexcept;
bool UpdateMonotonicCounter(HardwareEfuseBank& efuse, std::uint32_t new_version) noexcept;

class SecureBootVerifier {
public:
    static std::expected<void, BootError> AuthorizeFirmware(
        HardwareEfuseBank& efuse,
        const FirmwareHeader& header,
        std::span<const std::uint8_t> payload_data,
        bool auto_burn_version = true) noexcept
    {
        if (header.magic != FwMagic) {
            return std::unexpected(BootError::InvalidMagic);
        }

        if (header.key_slot_index >= OemKeySlots) {
            return std::unexpected(BootError::KeySlotOutOfBounds);
        }

        // 1. Апаратний статус відкликання ключа
        const std::uint32_t slot_mask = 1U << header.key_slot_index;
        if ((efuse.revoked_keys_mask & slot_mask) != 0) {
            return std::unexpected(BootError::KeyRevoked);
        }

        // 2. Звірка гешу публічного ключа з заводським слотом eFuse
        std::array<std::uint8_t, Sha256DigestSize> key_hash{};
        if (!Sha256(header.public_key, key_hash)) {
            return std::unexpected(BootError::KeyHashMismatch);
        }

        const auto& expected_hash = efuse.root_key_hashes[header.key_slot_index];
        if (!std::ranges::equal(key_hash, expected_hash)) {
            return std::unexpected(BootError::KeyHashMismatch);
        }

        // 3. Захист від відкату версії прошивки (Anti-Rollback)
        if (header.fw_version < efuse.monotonic_version) {
            return std::unexpected(BootError::VersionRollback);
        }

        // 4. Перевірка дайджесту образу
        std::array<std::uint8_t, Sha256DigestSize> payload_hash{};
        if (!Sha256(payload_data, payload_hash)) {
            return std::unexpected(BootError::PayloadCorrupted);
        }

        if (!std::ranges::equal(payload_hash, header.payload_sha256)) {
            return std::unexpected(BootError::PayloadCorrupted);
        }

        // 5. Перевірка криптографічного підпису
        if (!EcdsaVerify(header.public_key, payload_hash, header.signature)) {
            return std::unexpected(BootError::SignatureInvalid);
        }

        // 6. Атомарне оновлення апаратного лічильника версії
        if (auto_burn_version && header.fw_version > efuse.monotonic_version) {
            if (!UpdateMonotonicCounter(efuse, header.fw_version)) {
                return std::unexpected(BootError::EfuseBurnFailed);
            }
        }

        return {};
    }

    static std::expected<void, BootError> RevokeKeySlot(
        HardwareEfuseBank& efuse,
        std::uint32_t slot_index) noexcept
    {
        if (slot_index >= OemKeySlots) {
            return std::unexpected(BootError::KeySlotOutOfBounds);
        }

        if (!BurnEfuseBit(efuse, slot_index)) {
            return std::unexpected(BootError::EfuseBurnFailed);
        }

        efuse.revoked_keys_mask |= (1U << slot_index);
        return {};
    }
};

} // namespace Security
```
:::

---

## 3. Критичні пастки під час апаратної ротації ключів

### 3.1. Пастка передчасного прожигу eFuse (The Premature Burn Trap)
Найнебезпечніша помилка розробника — перепалювання біта відкликання старого ключа **до того**, як нова прошивка успішно пройшла перше тестове завантаження, підключилася до мережі та підтвердила відсутність фатальних помилок (Health Check Confirmation).
- **Сценарій катастрофи**: Завантажувач оновив образ, відразу спалив eFuse для Ключа 0. Але нова прошивка має помилку ініціалізації драйвера живлення і йде в нескінченний циклічний перезапуск (Bootloop).
- **Результат**: Оскільки завантажувач унеможливив відкат назад на попередню стабільну прошивку (ключ 0 анульовано в залізі), пристрій назавжди перетворюється на «цеглину».
- **Правило**: Прожиг eFuse біта відкликання виконується **виключно після успішного старту** нової версії та отримання команди підтвердження валідності образу.

### 3.2. Пастка відсутності подвійного підпису в перехідних пакетах
Під час міграції парку з 500 000 пристроїв оновлення не відбувається миттєво. Частина пристроїв може перебувати офлайн, у сплячому режимі або на складі:
- Якщо випустити прошивку, підписану **тільки новим Ключем 1**, пристрої зі старою версією завантажувача можуть не знати про активацію слота 1 і відхилять оновлення.
- Перехідний пакет прошивки (Transition Firmware Bundle) завжди постачається з **подвійним підписом**: він містить підпис Ключем 0 (для валідації старим софтом) та підпис Ключем 1 (для підтвердження готовності нового ключа).

### 3.3. Виснаження монотонних лічильників eFuse
Апаратні масиви eFuse мають скінченну кількість фізичних перемичок (наприклад, 32 або 64 біти). Якщо конвеєр CI/CD збільшує монотонну версію з кожним щоденним збірковим комітом, комірки eFuse закінчаться за кілька місяців.
- **Рішення**: Розділяти версію збірки (Software Semantic Version) та версію безпеки (Security Version / Anti-Rollback Counter).
- Лічильник безпеки збільшується тільки тоді, коли виправлено критичну вразливість, повернення до якої неприпустиме.

### 3.4. Захист від збоїв живлення та глітч-атак під час прожигу
Процес програмування eFuse вимагає подачі спеціальної напруги `VPP` (зазвичай 1.8V або 2.5V) протягом строго визначеного часового імпульсу (наприклад, 10–50 мікросекунд на біт).
- Якщо живлення пристрою зникне прямо під час прожигу, перемичка може згоріти частково, створивши нестабільний стан із плаваючим опором (Metastable State). При наступному зчитуванні біт може повертати `0` або `1` залежно від температури кристала.
- **Рішення**: Завантажувач повинен завжди виконувати повторне контрольне зчитування (Read-After-Write Verification) та перевіряти статус перемички при різних порогах напруги компаратора контролера eFuse.
