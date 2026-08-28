# ⚙️ Реалізація захищеного завантажувача з підтримкою ротації та відкликання ключів

Захищений завантажувач другого ступеня (англ. *Second-stage Bootloader*) у вбудованих системах відповідає за збереження цілісності та автентичності коду під час кожного перезавантаження пристрою. Коли система стикається з втратою чи витоком одного з ключів підпису, завантажувач зобов'язаний виконати безпечний перехід на резервний ключ, не допустивши стану «зацегливання» (англ. *bricking*) та гарантувавши неможливість повернення до скомпрометованих версій прошивки.

Головна складність розробки завантажувача полягає в тому, що він виконується в умовах суворих апаратних обмежень: динамічне виділення пам'яті (`malloc`) заборонене через ризик фрагментації купи та вичерпання SRAM, стандартна бібліотека C часто урізана або відсутня, а будь-яка невиправлена помилка в логіці завантажувача призводить до незворотної втрати контролю над пристроєм у полі.

Нижче наведено практичну реалізацію машини станів верифікації прошивки, яка підтримує чотири слоти відкритих ключів Root of Trust, перевірку апаратних бітів відкликання в eFuse, контроль монотонного лічильника захисту від відкату (Anti-Rollback) та безпечне спалювання eFuse після успішного підтвердження нової версії.

---

### Архітектура та послідовність верифікації

Процес верифікації в завантажувачі розбивається на п'ять послідовних кроків із перевіркою криптографічних інваріантів на кожному етапі:

1. **Читання та первинний розбір маніфесту:** Зчитування бінарного заголовка нової прошивки з Flash-пам'яті за фіксованим зміщенням, перевірка магічного числа (`0x5346574D`, ASCII `"SFWM"`) та перевірка контрольної суми CRC-32 заголовка. Якщо заголовок пошкоджено, завантажувач негайно повертає помилку `BOOT_ERR_MAGIC` і зупиняє розбір.
2. **Перевірка відкликання ключа (Revocation Check):** Завантажувач витягує з маніфесту індекс слота ключа, використаного для підпису (0..3). Якщо у регістрі eFuse біт відкликання для цього слота вже дорівнює `1`, верифікація негайно зупиняється з помилкою `BOOT_ERR_KEY_REVOKED`. Це блокує виконання прошивок, підписаних старими або скомпрометованими ключами, навіть якщо їхній математичний підпис формально є правильним.
3. **Звірка кореня довіри (Root of Trust Match):** Обчислення криптографічного хешу SHA-256 від відкритого ключа, що міститься в маніфесті, та його побайтове порівняння за сталий час (`constant_time_memcmp`) з еталонним хешем відповідного слота в eFuse. Якщо хеші не збігаються, повертається помилка `BOOT_ERR_ROOT_MISMATCH`.
4. **Контроль монотонного лічильника (Anti-Rollback):** Перевірка версії безпеки `security_version` із маніфесту. Якщо версія у прошивці суворо менша за значення апаратного лічильника eFuse, образ відкидається для захисту від атак повернення на старі версії з відомими вразливостями (`BOOT_ERR_ROLLBACK_DETECTED`).
5. **Математична верифікація підпису:** Обчислення SHA-256 хешу від тіла прошивки та перевірка цифрового підпису (алгоритмом Ed25519 або ECDSA P-256) відкритим ключем. Лише після проходження всіх п'яти етапів образ вважається автентичним.

---

### Реалізація завантажувача мовами C та C++

У реалізації мовою C структури упаковано для точного зіставлення з пам'яттю Flash, а всі перевірки реалізовано без динамічного виділення пам'яті. У реалізації мовою C++ використано сучасні стандарти C++20: безпечні діапазони пам'яті `std::span`, контейнери фіксованого розміру `std::array` та механізм `std::expected` для виразної передачі статусів помилок без використання механізму винятків (Exceptions), який неприпустимий у середовищі завантажувачів.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MANIFEST_MAGIC      0x5346574D  /* "SFWM" */
#define MAX_KEY_SLOTS       4
#define HASH_SIZE_BYTES     32
#define SIGNATURE_SIZE      64
#define PUBLIC_KEY_SIZE     32

typedef enum {
    BOOT_OK = 0,
    BOOT_ERR_MAGIC,
    BOOT_ERR_INVALID_SLOT,
    BOOT_ERR_KEY_REVOKED,
    BOOT_ERR_ROOT_MISMATCH,
    BOOT_ERR_ROLLBACK_DETECTED,
    BOOT_ERR_SIGNATURE_INVALID,
    BOOT_ERR_FLASH_READ
} BootStatus;

/* Структура бінарного маніфесту прошивки */
typedef struct {
    uint32_t magic;
    uint32_t payload_length;
    uint32_t security_version;
    uint8_t  key_slot_index;
    uint8_t  reserved[3];
    uint8_t  public_key[PUBLIC_KEY_SIZE];
    uint8_t  signature[SIGNATURE_SIZE];
} __attribute__((packed)) FirmwareManifest;

/* Апаратний стан eFuse (емулюється або читається з регістрів чіпа) */
typedef struct {
    uint8_t  root_key_digests[MAX_KEY_SLOTS][HASH_SIZE_BYTES];
    uint8_t  revocation_bits;       /* Бітова маска: біт N = 1 означає, що слот N відкликано */
    uint32_t monotonic_counter;     /* Апаратний лічильник анти-відкату */
} HardwareEfuseMirror;

/* Безпечне побайтове порівняння за сталий час (захист від Timing Attacks) */
static bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t size) {
    uint8_t result = 0;
    for (size_t i = 0; i < size; ++i) {
        result |= (a[i] ^ b[i]);
    }
    return (result == 0);
}

/* Зовнішні криптографічні функції (наприклад, з mbedTLS або апаратного крипторушія) */
extern void crypto_sha256(const uint8_t *data, size_t len, uint8_t *out_hash);
extern bool crypto_ed25519_verify(const uint8_t *pub_key, const uint8_t *msg_hash, const uint8_t *sig);
extern bool hardware_burn_efuse_revocation(uint8_t slot_index);
extern bool hardware_burn_efuse_counter(uint32_t new_version);

/* Головна функція верифікації та запуску прошивки */
BootStatus bootloader_verify_and_stage(
    const FirmwareManifest *manifest,
    const uint8_t *payload,
    const HardwareEfuseMirror *efuse,
    bool should_commit_rotation
) {
    if (!manifest || !payload || !efuse) {
        return BOOT_ERR_FLASH_READ;
    }

    /* 1. Перевірка магічного числа */
    if (manifest->magic != MANIFEST_MAGIC) {
        return BOOT_ERR_MAGIC;
    }

    /* 2. Перевірка допустимості індексу слота */
    if (manifest->key_slot_index >= MAX_KEY_SLOTS) {
        return BOOT_ERR_INVALID_SLOT;
    }

    /* 3. Перевірка відкликання ключа в eFuse */
    if ((efuse->revocation_bits & (1U << manifest->key_slot_index)) != 0) {
        return BOOT_ERR_KEY_REVOKED;
    }

    /* 4. Звірка відкритого ключа з еталоном Root of Trust */
    uint8_t computed_key_hash[HASH_SIZE_BYTES];
    crypto_sha256(manifest->public_key, PUBLIC_KEY_SIZE, computed_key_hash);

    if (!constant_time_memcmp(computed_key_hash, efuse->root_key_digests[manifest->key_slot_index], HASH_SIZE_BYTES)) {
        return BOOT_ERR_ROOT_MISMATCH;
    }

    /* 5. Захист від відкату версій */
    if (manifest->security_version < efuse->monotonic_counter) {
        return BOOT_ERR_ROLLBACK_DETECTED;
    }

    /* 6. Обчислення хешу тіла прошивки та перевірка підпису */
    uint8_t payload_hash[HASH_SIZE_BYTES];
    crypto_sha256(payload, manifest->payload_length, payload_hash);

    if (!crypto_ed25519_verify(manifest->public_key, payload_hash, manifest->signature)) {
        return BOOT_ERR_SIGNATURE_INVALID;
    }

    /* 7. Фіксація ротації eFuse (якщо це міграційний реліз і система підтвердила старт) */
    if (should_commit_rotation) {
        /* Спалюємо старі скомпрометовані слоти, якщо оновлення перейшло на вищий слот */
        for (uint8_t slot = 0; slot < manifest->key_slot_index; ++slot) {
            if ((efuse->revocation_bits & (1U << slot)) == 0) {
                hardware_burn_efuse_revocation(slot);
            }
        }

        /* Підвищуємо апаратний лічильник анти-відкату */
        if (manifest->security_version > efuse->monotonic_counter) {
            hardware_burn_efuse_counter(manifest->security_version);
        }
    }

    return BOOT_OK;
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <expected>

namespace bootloader {

constexpr uint32_t ManifestMagic = 0x5346574D; // "SFWM"
constexpr size_t MaxKeySlots = 4;
constexpr size_t HashSizeBytes = 32;
constexpr size_t SignatureSizeBytes = 64;
constexpr size_t PublicKeySizeBytes = 32;

enum class Status : uint8_t {
    Ok = 0,
    InvalidMagic,
    InvalidSlot,
    KeyRevoked,
    RootMismatch,
    RollbackDetected,
    SignatureInvalid,
    BufferTooShort
};

using HashArray = std::array<uint8_t, HashSizeBytes>;
using PublicKeyArray = std::array<uint8_t, PublicKeySizeBytes>;
using SignatureArray = std::array<uint8_t, SignatureSizeBytes>;

#pragma pack(push, 1)
struct FirmwareManifest {
    uint32_t magic;
    uint32_t payloadLength;
    uint32_t securityVersion;
    uint8_t  keySlotIndex;
    uint8_t  reserved[3];
    PublicKeyArray publicKey;
    SignatureArray signature;
};
#pragma pack(pop)

struct EfuseState {
    std::array<HashArray, MaxKeySlots> rootKeyDigests;
    uint8_t revocationMask;
    uint32_t monotonicCounter;
};

// Безпечне порівняння двох блоків за сталий час
[[nodiscard]] constexpr bool constantTimeEqual(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }
    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return diff == 0;
}

// Абстракція над апаратними крипторушіями
class CryptoEngine {
public:
    static HashArray sha256(std::span<const uint8_t> data) noexcept;
    static bool verifyEd25519(
        std::span<const uint8_t, PublicKeySizeBytes> pubKey,
        std::span<const uint8_t, HashSizeBytes> msgHash,
        std::span<const uint8_t, SignatureSizeBytes> signature
    ) noexcept;
};

class HardwareSecurityController {
public:
    static bool burnRevocationBit(uint8_t slotIndex) noexcept;
    static bool burnMonotonicCounter(uint32_t newCounter) noexcept;
};

class SecureBootVerifier {
public:
    [[nodiscard]] static std::expected<void, Status> verifyAndStage(
        const FirmwareManifest& manifest,
        std::span<const uint8_t> payload,
        const EfuseState& efuse,
        bool shouldCommitRotation
    ) noexcept {
        // 1. Перевірка заголовка
        if (manifest.magic != ManifestMagic) {
            return std::unexpected(Status::InvalidMagic);
        }

        // 2. Валідація індексу слота
        if (manifest.keySlotIndex >= MaxKeySlots) {
            return std::unexpected(Status::InvalidSlot);
        }

        // 3. Перевірка біта відкликання в eFuse
        const uint8_t slotMask = static_cast<uint8_t>(1U << manifest.keySlotIndex);
        if ((efuse.revocationMask & slotMask) != 0) {
            return std::unexpected(Status::KeyRevoked);
        }

        // 4. Порівняння хешу відкритого ключа з еталоном Root of Trust
        const HashArray computedKeyDigest = CryptoEngine::sha256(manifest.publicKey);
        if (!constantTimeEqual(computedKeyDigest, efuse.rootKeyDigests[manifest.keySlotIndex])) {
            return std::unexpected(Status::RootMismatch);
        }

        // 5. Захист від відкату
        if (manifest.securityVersion < efuse.monotonicCounter) {
            return std::unexpected(Status::RollbackDetected);
        }

        // 6. Перевірка цифрового підпису образу
        const HashArray payloadHash = CryptoEngine::sha256(payload.first(manifest.payloadLength));
        if (!CryptoEngine::verifyEd25519(manifest.publicKey, payloadHash, manifest.signature)) {
            return std::unexpected(Status::SignatureInvalid);
        }

        // 7. Безпечна фіксація ротації
        if (shouldCommitRotation) {
            for (uint8_t slot = 0; slot < manifest.keySlotIndex; ++slot) {
                if ((efuse.revocationMask & (1U << slot)) == 0) {
                    HardwareSecurityController::burnRevocationBit(slot);
                }
            }

            if (manifest.securityVersion > efuse.monotonicCounter) {
                HardwareSecurityController::burnMonotonicCounter(manifest.securityVersion);
            }
        }

        return {};
    }
};

} // namespace bootloader
```
:::

---

### Підводні камені та інженерні пастки реалізації

#### 1. Небезпека передчасного спалювання eFuse (Premature Fuse Burning)
Найбільш критична помилка під час ротації ключів — спалювання біта відкликання старого ключа `REVOKE_KEY0` *до того*, як новий образ у Банку B успішно пройшов повну верифікацію та здійснив перший тестовий запуск.

Якщо після спалювання eFuse з'ясується, що нова прошивка містить фатальну помилку ініціалізації периферії (Kernel Panic, HardFault або вічний WDT-скид), система опиняється в безвихідному стані: вона не може ані завантажити новий код, ані відкотитися на стару стабільну прошивку з Банку A, оскільки ключ Банку A щойно було безповоротно відкликано залізом.

Єдиним надійним вирішенням є **двофазний комміт (Two-Phase Commit)**:
- На першому етапі завантажувач лише верифікує новий образ новим ключем і дозволяє пробне завантаження.
- Нова прошивка стартує в режимі перевірки (`STATUS_TESTING`), ініціалізує критичні підсистеми та виконує самодіагностику (POST, Self-Test).
- Тільки після успішного встановлення з'єднання з сервером і підтвердження працездатності застосунок викликає системну функцію запису eFuse, безповоротно спалюючи старий слот і фіксуючи новий лічильник анти-відкату.

#### 2. Атаки за часом виконання (Timing Attacks на порівняння хешів)
Використання стандартної бібліотечної функції `memcmp()` для перевірки хешів або відкритих ключів у захищеному завантажувачі категорично заборонено.

Стандартний `memcmp()` оптимізовано для швидкості: він порівнює байти послідовно і перериває цикл на першому ж байті, що не збігся. Зловмисник, подаючи на вхід завантажувача модифіковані образи та вимірюючи час відповіді процесора за допомогою високоточного осцилографа або апаратного таймера (з точністю до одного такту), може побайтово відновити еталонний хеш eFuse або відкритий ключ, підбираючи кожну наступну позицію за мікроскопічним збільшенням часу виконання перевірки.

Функція `constant_time_memcmp()` (або `constantTimeEqual` у C++) усуває цей канал витоку інформації: вона завжди ітерує рівно всі `N` байтів масиву, накопичуючи побітову різницю через операцію XOR (`result |= (a[i] ^ b[i])`), тому час її виконання залишається суворо константним незалежно від того, на якій позиції виникла розбіжність.

#### 3. Стійкість до збою живлення під час запису eFuse (Power-Cut Glitching)
Операція фізичного перепалювання кремнієвих перемичок eFuse вимагає подачі підвищеної напруги програмування (наприклад, 2.5 В або 3.3 В через внутрішній генератор підкачування заряду Charge Pump) протягом суворо визначеного інтервалу часу (типово від 5 до 12 мікросекунд на біт).

Якщо живлення пристрою зникає або просідає безпосередньо в процесі запису біта eFuse, комірка може перейти в проміжний, напівпровідниковий стан (метастабільний опір). За такого стану під час холодного старту при кімнатній температурі чіп може зчитувати біт як `1`, а при нагріванні на сонці або падінні напруги — як `0`.

Для захисту від такого сценарію драйвер спалювання eFuse зобов'язаний:
1. Перевіряти стан апаратного детектора просідання напруги (Brownout Detector / Power Good) перед подачею імпульсу.
2. Виконувати повторне контрольне зчитування комірки (Read-Back Verification) в екстремальних режимах опорного струму (Marginal Read Mode) після завершення запису.
