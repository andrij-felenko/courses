# ⚙️ Генератор підписаного релізного маніфесту та перевірка цілісності артефактів

На фінальному етапі конвеєра неперервної інтеграції (CI/CD) окремі результати роботи компілятора та лінкера — бінарний образ прошивки, файл налагоджувальних символів ELF, мапа пам'яті та специфікація компонентів SBOM — мають бути перевірені на цілісність, об'єднані в детермінований маніфест випуску та підписані криптографічним ключем.

Цей процес реалізує генератор релізного пакета. Програма виконує чотири послідовні інженерні кроки:
1. **Обчислення криптографічних дайджестів SHA-256** для кожного вхідного артефакту випуску;
2. **Перевірка бінарних параметрів образу:** валідація точки входу, відповідності архітектури процесора та контролю залишку місця у пам'яті Flash;
3. **Формування бінарного заголовка прошивки (англ. *Firmware Header*):** фіксація магічного числа, версії, маски апаратних ревізій, лічильника анти-відкату та гешу образу;
4. **Створення підписаного маніфесту релізу** та верифікація цілісності створеного пакета перед його публікацією у сховище артефактів.

---

## Архітектурний механізм пакування та перевірки

Під час збірки вбудованої системи вихідні файли компіляції розкидані по робочій теці: бінарний виконуваний блок `firmware.bin` лежить у каталозі збірки, налагоджувальний файл `firmware.elf` містить таблиці символів DWARF, файл мапи пам'яті `firmware.map` фіксує розподіл секцій лінкером, а генератор залежностей створює `sbom.json`. 

Якщо передати ці файли на фабрику або сервер оновлення окремо, виникає ризик часткового завантаження, неузгодженості версій або прошивання образу, призначеного для нової ревізії плати, у застаріле залізо.

Щоб унеможливити такі помилки, генератор зв'язує всі артефакти через бінарний криптографічний заголовок:

```
[Виконуваний образ .bin] ──> [Обчислення SHA-256] ──> [Запис у заголовок Header]
[Маска заліза (HW Mask)] ──> [Контроль ревізії]   ──> [Підпис Ed25519/ECDSA]
[Лічильник Anti-rollback] ─> [Захист від відкату] ──> [Склеювання: Header + Binary]
```

### 1. Контроль апаратних ревізій через бітову маску
У процесі виробництва апаратна плата пристрою проходить через кілька ревізій (наприклад, Rev.A, Rev.B, Rev.C), де можуть змінюватися виводи підключення датчиків або тип мікросхеми Flash-пам'яті. Бінарний заголовок містить поле `target_hw_mask` — 32-бітну маску сумісності. Якщо прошивка підтримує ревізії 1 і 2, біти `(1 << 1) | (1 << 2)` встановлюються в одиницю. Завантажувач пристрою, зчитуючи апаратні резистивні підтяжки або значення з OTP-пам'яті, миттєво відхиляє несумісний образ ще до початку його запису у Flash.

### 2. Захист від відкату версії (Anti-Rollback Protection)
Зловмисник, маючи легітимно підписаний старий образ прошивки дворічної давнини з відомою вразливістю, може спробувати примусово прошити його у пристрій. Поле `anti_rollback_version` містить строго монотонно зростаючий числовий лічильник. Завантажувач порівнює це число зі значенням, записаним у захищених апаратних регістрах eFuse або захищеній пам'яті процесора. Якщо версія в заголовку нижча за поточну апаратну відмітку, оновлення блокується як потенційна атака.

### 3. Фіксація криптографічного підпису
Геш-сума SHA-256 обчислюється виключно від тіла бінарного коду. Потім цей геш разом із полями версії та маски заліза підписується закритим ключем релізної інженерної станції. Завантажувач пристрою перевіряє відкритим ключем як цілісність полів заголовка, так і відповідність гешу всього тіла прошивки.

---

## Реалізація пакувальника та валідатора

Нижче наведено повноцінну реалізацію генератора релізного маніфесту двома мовами: на чистому системному C99 для вбудованих утиліт та на ідіоматичному C++20 з використанням концепції RAII, безпечних зрізів пам'яті `std::span` та механізму обробки помилок `std::expected`.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define BUNDLE_MAGIC          0x42554E44U /* "BUND" в ASCII */
#define BUNDLE_FORMAT_VERSION 1U
#define SHA256_DIGEST_LEN     32U
#define SIGNATURE_LEN         64U

#pragma pack(push, 1)
typedef struct {
    uint32_t magic;                    /* Магічне число ідентифікації BUNDLE_MAGIC */
    uint16_t header_version;           /* Версія формату заголовка */
    uint16_t reserved;                 /* Вирівнювання структури */
    uint32_t payload_size;             /* Розмір виконуваного бінарного образу в байтах */
    uint32_t target_hw_mask;           /* Бітова маска сумісних ревізій апаратної плати */
    uint32_t anti_rollback_version;    /* Монотонний лічильник захисту від відкату версії */
    uint8_t  payload_sha256[SHA256_DIGEST_LEN]; /* Криптографічний геш SHA-256 образу */
    uint8_t  signature[SIGNATURE_LEN];          /* Цифровий підпис (Ed25519/ECDSA) */
} firmware_header_t;
#pragma pack(pop)

typedef struct {
    char filename[64];
    uint32_t file_size;
    uint8_t  sha256[SHA256_DIGEST_LEN];
    bool     is_mandatory;
} release_artifact_entry_t;

typedef struct {
    uint16_t ver_major;
    uint16_t ver_minor;
    uint16_t ver_patch;
    uint32_t target_hw_mask;
    uint32_t anti_rollback_version;
    size_t   artifact_count;
    release_artifact_entry_t artifacts[8];
} release_bundle_spec_t;

/* Спрощена імітація криптографічного SHA-256 для демонстрації зв'язування даних */
static void compute_sha256_mock(const uint8_t *data, size_t len, uint8_t *out_hash) {
    memset(out_hash, 0, SHA256_DIGEST_LEN);
    uint32_t acc = 0x811C9DC5U;
    for (size_t i = 0; i < len; ++i) {
        acc = (acc ^ data[i]) * 0x01000193U;
        out_hash[i % SHA256_DIGEST_LEN] ^= (uint8_t)(acc & 0xFFU);
    }
}

/* Генерація та валідація бінарного заголовка */
static bool generate_firmware_header(
    const uint8_t *bin_payload,
    size_t bin_size,
    uint32_t hw_mask,
    uint32_t rollback_ver,
    firmware_header_t *out_header
) {
    if (!bin_payload || bin_size == 0 || !out_header) {
        return false;
    }

    out_header->magic = BUNDLE_MAGIC;
    out_header->header_version = BUNDLE_FORMAT_VERSION;
    out_header->reserved = 0;
    out_header->payload_size = (uint32_t)bin_size;
    out_header->target_hw_mask = hw_mask;
    out_header->anti_rollback_version = rollback_ver;

    compute_sha256_mock(bin_payload, bin_size, out_header->payload_sha256);

    /* Імітація накладання підпису приватним ключем релізної станції */
    for (size_t i = 0; i < SIGNATURE_LEN; ++i) {
        out_header->signature[i] = (uint8_t)(out_header->payload_sha256[i % SHA256_DIGEST_LEN] ^ 0xAAU);
    }
    return true;
}

/* Перевірка цілісності релізного пакета */
static bool verify_bundle_integrity(
    const firmware_header_t *header,
    const uint8_t *bin_payload,
    size_t bin_size,
    uint32_t device_hw_revision,
    uint32_t device_current_rollback_ver
) {
    if (!header || !bin_payload) {
        return false;
    }

    if (header->magic != BUNDLE_MAGIC) {
        fprintf(stderr, "Помилка: недійсне магічне число заголовка: 0x%08X\n", header->magic);
        return false;
    }

    if (header->payload_size != bin_size) {
        fprintf(stderr, "Помилка: невідповідність розміру образу: %u != %zu\n", header->payload_size, bin_size);
        return false;
    }

    if ((header->target_hw_mask & (1U << device_hw_revision)) == 0) {
        fprintf(stderr, "Помилка: прошивка не підтримує ревізію плати %u (маска 0x%X)\n",
                device_hw_revision, header->target_hw_mask);
        return false;
    }

    if (header->anti_rollback_version < device_current_rollback_ver) {
        fprintf(stderr, "Атака відкату версії! Поточна версія пристрою: %u, образ: %u\n",
                device_current_rollback_ver, header->anti_rollback_version);
        return false;
    }

    uint8_t calculated_hash[SHA256_DIGEST_LEN];
    compute_sha256_mock(bin_payload, bin_size, calculated_hash);
    if (memcmp(calculated_hash, header->payload_sha256, SHA256_DIGEST_LEN) != 0) {
        fprintf(stderr, "Помилка: не збігається SHA-256 контрольна сума образу!\n");
        return false;
    }

    return true;
}

int main(void) {
    /* Симуляція скомпільованого бінарного коду мікроконтролера */
    uint8_t dummy_binary[1024];
    for (size_t i = 0; i < sizeof(dummy_binary); ++i) {
        dummy_binary[i] = (uint8_t)(i & 0xFF);
    }

    firmware_header_t header;
    const uint32_t target_hw_bitmask = (1U << 1) | (1U << 2); /* Підтримка ревізій Rev.1 та Rev.2 */
    const uint32_t release_rollback_counter = 105;

    if (!generate_firmware_header(dummy_binary, sizeof(dummy_binary),
                                  target_hw_bitmask, release_rollback_counter, &header)) {
        fprintf(stderr, "Не вдалося сформувати заголовок прошивки\n");
        return EXIT_FAILURE;
    }

    printf("Маніфест прошивки сформовано успішно:\n");
    printf("  Магічне число: 0x%08X (OK)\n", header.magic);
    printf("  Розмір тіла:    %u байт\n", header.payload_size);
    printf("  Маска заліза:   0x%08X\n", header.target_hw_mask);
    printf("  Анти-відкат:    %u\n", header.anti_rollback_version);
    printf("  SHA-256 геш:    %02x%02x%02x%02x...%02x\n",
           header.payload_sha256[0], header.payload_sha256[1],
           header.payload_sha256[2], header.payload_sha256[3],
           header.payload_sha256[31]);

    /* Тестування валідації на цільовому пристрої */
    const uint32_t board_rev = 2;
    const uint32_t current_fw_rollback_ver = 104;

    printf("\nВалідація образу для плати Rev.%u (поточний лічильник %u)...\n",
           board_rev, current_fw_rollback_ver);

    if (verify_bundle_integrity(&header, dummy_binary, sizeof(dummy_binary),
                                board_rev, current_fw_rollback_ver)) {
        printf("РЕЗУЛЬТАТ: Пакет успішно валідовано, прошивка дозволена до запису у Flash.\n");
    } else {
        printf("РЕЗУЛЬТАТ: Валідацію провалено! Запис заборонено.\n");
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <span>
#include <array>
#include <cstdint>
#include <expected>
#include <iomanip>
#include <algorithm>

namespace release {

constexpr uint32_t BUNDLE_MAGIC = 0x42554E44U; /* "BUND" */
constexpr uint16_t BUNDLE_FORMAT_VERSION = 1U;
constexpr size_t SHA256_LEN = 32;
constexpr size_t SIGNATURE_LEN = 64;

using Sha256Digest = std::array<uint8_t, SHA256_LEN>;
using SignatureBlock = std::array<uint8_t, SIGNATURE_LEN>;

enum class ValidationError {
    InvalidMagic,
    SizeMismatch,
    IncompatibleHardware,
    RollbackDetected,
    IntegrityCheckFailed,
    EmptyPayload
};

#pragma pack(push, 1)
struct FirmwareHeader {
    uint32_t magic{BUNDLE_MAGIC};
    uint16_t header_version{BUNDLE_FORMAT_VERSION};
    uint16_t reserved{0};
    uint32_t payload_size{0};
    uint32_t target_hw_mask{0};
    uint32_t anti_rollback_version{0};
    Sha256Digest payload_sha256{};
    SignatureBlock signature{};
};
#pragma pack(pop)

class ReleaseBundlePackager {
public:
    static Sha256Digest calculate_sha256(std::span<const uint8_t> data) noexcept {
        Sha256Digest digest{};
        uint32_t acc = 0x811C9DC5U;
        for (size_t i = 0; i < data.size(); ++i) {
            acc = (acc ^ data[i]) * 0x01000193U;
            digest[i % SHA256_LEN] ^= static_cast<uint8_t>(acc & 0xFFU);
        }
        return digest;
    }

    static std::expected<FirmwareHeader, ValidationError> create_header(
        std::span<const uint8_t> payload,
        uint32_t hw_mask,
        uint32_t rollback_ver
    ) {
        if (payload.empty()) {
            return std::unexpected(ValidationError::EmptyPayload);
        }

        FirmwareHeader header{};
        header.magic = BUNDLE_MAGIC;
        header.header_version = BUNDLE_FORMAT_VERSION;
        header.payload_size = static_cast<uint32_t>(payload.size());
        header.target_hw_mask = hw_mask;
        header.anti_rollback_version = rollback_ver;
        header.payload_sha256 = calculate_sha256(payload);

        // Симуляція накладання цифрового підпису
        for (size_t i = 0; i < SIGNATURE_LEN; ++i) {
            header.signature[i] = static_cast<uint8_t>(header.payload_sha256[i % SHA256_LEN] ^ 0xAAU);
        }

        return header;
    }

    static std::expected<void, ValidationError> verify_header(
        const FirmwareHeader& header,
        std::span<const uint8_t> payload,
        uint32_t target_board_rev,
        uint32_t device_rollback_ver
    ) noexcept {
        if (header.magic != BUNDLE_MAGIC) {
            return std::unexpected(ValidationError::InvalidMagic);
        }

        if (header.payload_size != payload.size()) {
            return std::unexpected(ValidationError::SizeMismatch);
        }

        if ((header.target_hw_mask & (1U << target_board_rev)) == 0) {
            return std::unexpected(ValidationError::IncompatibleHardware);
        }

        if (header.anti_rollback_version < device_rollback_ver) {
            return std::unexpected(ValidationError::RollbackDetected);
        }

        const auto computed = calculate_sha256(payload);
        if (computed != header.payload_sha256) {
            return std::unexpected(ValidationError::IntegrityCheckFailed);
        }

        return {};
    }
};

} // namespace release

int main() {
    // Формування тестового виконуваного бінарника
    std::vector<uint8_t> firmware_binary(1024);
    for (size_t i = 0; i < firmware_binary.size(); ++i) {
        firmware_binary[i] = static_cast<uint8_t>(i & 0xFF);
    }

    constexpr uint32_t target_hw_mask = (1U << 1) | (1U << 2);
    constexpr uint32_t target_rollback_version = 105;

    auto header_result = release::ReleaseBundlePackager::create_header(
        firmware_binary,
        target_hw_mask,
        target_rollback_version
    );

    if (!header_result) {
        std::cerr << "Помилка формування маніфесту прошивки!\n";
        return 1;
    }

    const auto& header = *header_result;
    std::cout << "Маніфест випуску (C++20) згенеровано успішно:\n"
              << "  Магічне число:  0x" << std::hex << header.magic << std::dec << "\n"
              << "  Розмір образу:  " << header.payload_size << " байтів\n"
              << "  Маска ревізій:  0x" << std::hex << header.target_hw_mask << std::dec << "\n"
              << "  Лічильник версії: " << header.anti_rollback_version << "\n";

    // Перевірка на цільовому пристрої
    constexpr uint32_t current_board_rev = 2;
    constexpr uint32_t current_device_rollback = 104;

    std::cout << "\nВалідація образу для плати Rev." << current_board_rev
              << " (поточний лічильник " << current_device_rollback << ")...\n";

    auto verification = release::ReleaseBundlePackager::verify_header(
        header,
        firmware_binary,
        current_board_rev,
        current_device_rollback
    );

    if (verification) {
        std::cout << "РЕЗУЛЬТАТ: Образ цілісний, сумісний з апаратною ревізією та дозволений до прошивки.\n";
    } else {
        std::cerr << "РЕЗУЛЬТАТ: Валідацію провалено з кодом помилки: "
                  << static_cast<int>(verification.error()) << "\n";
        return 1;
    }

    return 0;
}
```
:::

---

## Порівняльний аналіз реалізацій C та C++

Обидві мовні реалізації вирішують одне технічне завдання, проте демонструють суттєво різні підходи до безпеки типів та управління пам'яттю:

1. **Контроль меж буферів:** У версії на C передача масиву даних вимагає пари аргументів — вказівника `const uint8_t *bin_payload` та окремої довжини `size_t bin_size`. Будь-яка помилка в арифметиці покажчиків може призвести до читання за межами буфера (англ. *buffer overrun*). У версії на C++20 використовується тип `std::span<const uint8_t>`, який інкапсулює вказівник і розмір в один легкостійкий неволодіючий об'єкт із нульовими накладними витратами під час виконання.
2. **Обробка виняткових ситуацій:** C-код покладається на булеві коди повернення (`true`/`false`) або цілочисельні коди помилок через вихідні покажчики. C++20 застосовує контейнер `std::expected<FirmwareHeader, ValidationError>`, який примушує розробника явно перевірити результат перед доступом до сформованого заголовка, унеможливлюючи використання неініціалізованої пам'яті.
3. **Фіксований розмір контейнерів:** Замість сирих масивів `uint8_t payload_sha256[32]` у C++ використано строго типізовані псевдоніми `std::array<uint8_t, 32>`, що забезпечує коректне копіювання за значенням, підтримку операторів порівняння `==` та сумісність зі стандартними алгоритмами без виклику небезпечних функцій `memcmp` чи `memcpy`.

---

## Інваріанти та типові пастки при генерації пакетів

Під час побудови виробничого конвеєра збірки слід дотримуватися чотирьох ключових правил:
1. **Вирівнювання структур заголовка (`#pragma pack`):** поля бінарного заголовка повинні мати фіксовані розміри та порядок байтів (Little-Endian). Неузгоджене вирівнювання на компіляторі хоста збірки (x86_64) та цільового мікроконтролера (ARM Cortex-M) призведе до фатального зміщення полів;
2. **Атомарність оновлення лічильника анти-відкату:** запис нового значення лічильника версії в однократно програмовану пам'ять (OTP) або eFuse процесора повинен відбуватися лише після успішної повної верифікації прошивки та її першого коректного старту;
3. **Ізоляція ключів підпису:** приватний ключ підпису ніколи не повинен зберігатися на сервері збірки у відкритому вигляді. Він має викликатися через мережевий сервіс апаратного модуля безпеки (HSM / KMS);
4. **Контроль розміру бінарника:** перевірка `payload_size` повинна строго звірятися з доступним простором Flash-пам'яті, виділеним у скрипті лінкера, щоб запобігти перезапису сусідніх секторів або завантажувача.
