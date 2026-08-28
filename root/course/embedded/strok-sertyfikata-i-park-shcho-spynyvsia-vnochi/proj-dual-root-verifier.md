# ⚙️ Дводжерельний валідатор довіри та безперервна ротація сертифікатів у прошивці

Головна вразливість стандартного сховища довіри вбудованої системи полягає у жорсткому зашиванні єдиного кореневого сертифіката (Root CA) безпосередньо у вихідний код або бінарний образ прошивки. Коли строк дії цього сертифіката добігає кінця, пристрій втрачає можливість встановити TLS-з'єднання зі своїм сервером оновлень. Щоб усунути цей ризик, прошивка повинна підтримувати дводжерельне сховище довіри (Dual-Root Trust Store) в енергонезалежній Flash-пам'яті з підтримкою двох незалежних слотів: активного (Slot A) та резервного/майбутнього (Slot B).

Розглянемо практичну реалізацію такого механізму для мікроконтролерів із використанням бібліотеки Mbed TLS, включно зі структурою заголовків секторів пам'яті, логікою вибору чинного якоря довіри та безпечним зворотним викликом валідації ланцюга.

---

### Архітектура дводжерельного сховища у Flash-пам'яті

Щоб унеможливити пошкодження критичних криптографічних даних під час оновлення сертифікатів або в разі раптового зникнення живлення пристрою, масив енергонезалежної пам'яті (Flash / EEPROM / FRAM) розбивається на два ізольовані сектори, вирівняні за межами фізичних сторінок запису:
- **Slot A:** зберігає поточний основний кореневий сертифікат або робочий сертифікат пристрою.
- **Slot B:** виділяється під резервний, оновлений або наступний центр сертифікації.

Кожен сектор захищений бінарним заголовком із контрольною сумою CRC32, мітками версії структури, полями часових рамок валідності та бітовими прапорцями життєвого циклу:

```
+-------------------------------------------------------------------------+
| Заголовок слота довіри (64 байти, вирівняно по 4 байти)                 |
| ├── magic: 0x54525553 (ASCII 'TRUS')                                    |
| ├── version: версія формату структури (наприклад, 0x0001)               |
| ├── slot_state: 0x01 = ACTIVE, 0x02 = STANDBY, 0x00 = REVOKED, 0xFF=FREE|
| ├── cert_len: фактичний розмір сертифіката у байтах (512..2048 байтів)  |
| ├── valid_from: Unix timestamp дати notBefore                           |
| ├── valid_to: Unix timestamp дати notAfter                              |
| ├── data_crc32: контрольна сума корисного навантаження (IEEE 802.3)     |
| └── padding: зарезервоване вирівнювання під розмір сторінки Flash       |
+-------------------------------------------------------------------------+
| Тіло сертифіката X.509 (двійковий масив ASN.1 DER або PEM рядок)        |
+-------------------------------------------------------------------------+
```

---

### Реалізація дводжерельного сховища довіри

Наведений нижче програмний модуль завантажує обидва слоти довіри з Flash-пам'яті, проводить перевірку контрольних сум, порівнює дати валідності з системним часом пристрою та ініціалізує контекст валідації Mbed TLS.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "mbedtls/ssl.h"
#include "mbedtls/x509_crt.h"

#define TRUST_SLOT_MAGIC 0x54525553U
#define MAX_CERT_SIZE    2048U

typedef enum {
    SLOT_EMPTY   = 0xFF,
    SLOT_STANDBY = 0x02,
    SLOT_ACTIVE  = 0x01,
    SLOT_REVOKED = 0x00
} trust_slot_state_t;

typedef struct __attribute__((packed)) {
    uint32_t magic;
    uint16_t version;
    uint8_t  slot_state;
    uint8_t  reserved;
    uint32_t cert_len;
    uint64_t valid_from;
    uint64_t valid_to;
    uint32_t data_crc32;
    uint8_t  padding[36];
} trust_slot_header_t;

typedef struct {
    trust_slot_header_t header;
    uint8_t cert_data[MAX_CERT_SIZE];
} trust_slot_t;

typedef struct {
    mbedtls_x509_crt ca_chain;
    uint32_t active_certs_count;
    uint64_t current_system_time;
} dual_trust_store_t;

static uint32_t calculate_crc32(const uint8_t *data, size_t len) {
    uint32_t crc = 0xFFFFFFFFU;
    for (size_t i = 0; i < len; ++i) {
        crc ^= data[i];
        for (uint8_t j = 0; j < 8; ++j) {
            crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
        }
    }
    return ~crc;
}

int dual_trust_store_init(dual_trust_store_t *store, uint64_t current_time) {
    if (!store) return -1;
    mbedtls_x509_crt_init(&store->ca_chain);
    store->active_certs_count = 0;
    store->current_system_time = current_time;
    return 0;
}

int dual_trust_store_load_slot(dual_trust_store_t *store, const trust_slot_t *slot) {
    if (!store || !slot) return -1;
    if (slot->header.magic != TRUST_SLOT_MAGIC) return -2;
    if (slot->header.slot_state != SLOT_ACTIVE && slot->header.slot_state != SLOT_STANDBY) {
        return -3;
    }
    if (slot->header.cert_len == 0 || slot->header.cert_len > MAX_CERT_SIZE) {
        return -4;
    }

    uint32_t calculated_crc = calculate_crc32(slot->cert_data, slot->header.cert_len);
    if (calculated_crc != slot->header.data_crc32) {
        return -5; /* Помилка контрольної суми */
    }

    /* Перевірка часових меж сертифіката, якщо системний час валідний */
    if (store->current_system_time > 0) {
        if (store->current_system_time < slot->header.valid_from ||
            store->current_system_time > slot->header.valid_to) {
            /* Сертифікат прострочений, але якщо це резервний слот, ми можемо завантажити його для аналізу */
            if (slot->header.slot_state == SLOT_ACTIVE) {
                return -6; /* Активний сертифікат прострочено */
            }
        }
    }

    /* Парсинг та додавання сертифіката X.509 до ланцюга Mbed TLS */
    int ret = mbedtls_x509_crt_parse(&store->ca_chain, slot->cert_data, slot->header.cert_len);
    if (ret != 0) {
        return ret;
    }

    store->active_certs_count++;
    return 0;
}

void dual_trust_store_free(dual_trust_store_t *store) {
    if (store) {
        mbedtls_x509_crt_free(&store->ca_chain);
        store->active_certs_count = 0;
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <vector>
#include <expected>
#include <chrono>
#include <memory>
#include "mbedtls/ssl.h"
#include "mbedtls/x509_crt.h"

enum class TrustSlotState : uint8_t {
    Empty   = 0xFF,
    Standby = 0x02,
    Active  = 0x01,
    Revoked = 0x00
};

enum class TrustStoreError {
    InvalidMagic,
    InactiveSlot,
    InvalidLength,
    ChecksumMismatch,
    ExpiredCertificate,
    MbedTlsParseError,
    NoValidAnchors
};

struct alignas(4) TrustSlotHeader {
    uint32_t magic;
    uint16_t version;
    TrustSlotState slot_state;
    uint8_t  reserved;
    uint32_t cert_len;
    uint64_t valid_from;
    uint64_t valid_to;
    uint32_t data_crc32;
    uint8_t  padding[36];
};

class DualTrustStore {
public:
    static constexpr uint32_t ExpectedMagic = 0x54525553U;
    static constexpr size_t MaxCertSize = 2048U;

    explicit DualTrustStore(std::chrono::system_clock::time_point now) noexcept
        : currentTimeSec_(std::chrono::duration_cast<std::chrono::seconds>(now.time_since_epoch()).count()) {
        mbedtls_x509_crt_init(&caChain_);
    }

    ~DualTrustStore() noexcept {
        mbedtls_x509_crt_free(&caChain_);
    }

    DualTrustStore(const DualTrustStore&) = delete;
    DualTrustStore& operator=(const DualTrustStore&) = delete;
    DualTrustStore(DualTrustStore&&) = delete;
    DualTrustStore& operator=(DualTrustStore&&) = delete;

    [[nodiscard]] std::expected<void, TrustStoreError> loadSlot(
        const TrustSlotHeader& header,
        std::span<const uint8_t> certData) noexcept {
        
        if (header.magic != ExpectedMagic) {
            return std::unexpected(TrustStoreError::InvalidMagic);
        }
        if (header.slot_state != TrustSlotState::Active && header.slot_state != TrustSlotState::Standby) {
            return std::unexpected(TrustStoreError::InactiveSlot);
        }
        if (header.cert_len == 0 || header.cert_len > certData.size() || header.cert_len > MaxCertSize) {
            return std::unexpected(TrustStoreError::InvalidLength);
        }

        if (calculateCrc32(certData.subspan(0, header.cert_len)) != header.data_crc32) {
            return std::unexpected(TrustStoreError::ChecksumMismatch);
        }

        if (currentTimeSec_ > 0) {
            if (currentTimeSec_ < header.valid_from || currentTimeSec_ > header.valid_to) {
                if (header.slot_state == TrustSlotState::Active) {
                    return std::unexpected(TrustStoreError::ExpiredCertificate);
                }
            }
        }

        const int ret = mbedtls_x509_crt_parse(&caChain_, certData.data(), header.cert_len);
        if (ret != 0) {
            return std::unexpected(TrustStoreError::MbedTlsParseError);
        }

        loadedAnchorsCount_++;
        return {};
    }

    [[nodiscard]] mbedtls_x509_crt* nativeHandle() noexcept {
        return &caChain_;
    }

    [[nodiscard]] size_t anchorsCount() const noexcept {
        return loadedAnchorsCount_;
    }

private:
    mbedtls_x509_crt caChain_{};
    size_t loadedAnchorsCount_{0};
    uint64_t currentTimeSec_{0};

    [[nodiscard]] static uint32_t calculateCrc32(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0xFFFFFFFFU;
        for (const uint8_t byte : data) {
            crc ^= byte;
            for (uint8_t j = 0; j < 8; ++j) {
                crc = (crc >> 1) ^ (0xEDB88320U & (-(crc & 1U)));
            }
        }
        return ~crc;
    }
};
```
:::

---

### Користувацький зворотний виклик перевірки ланцюга (Verify Callback)

За замовчуванням бібліотека Mbed TLS негайно перериває рукостискання TLS, якщо дата кінцевого сертифіката виходить за межі системного часу пристрою. У вбудованих пристроях із розрядженою батареєю годинника реального часу (RTC) системний час при старті може скидатися на дефолтну епоху (наприклад, 1 січня 1970 року або 1 січня 2020 року).

Щоб уникнути блокування пристрою через хибний локальний час, у конфігурацію TLS впроваджується спеціальний фільтр помилок:

:::tabs
```c
int custom_tls_verify_callback(void *data, mbedtls_x509_crt *crt, int depth, uint32_t *flags) {
    /* Отримуємо бітову маску помилок валідації Mbed TLS */
    uint32_t validation_flags = *flags;

    /* Якщо єдина проблема полягає у невідповідності часу (сертифікат ще не діє або прострочений) */
    if (validation_flags == MBEDTLS_X509_BADCERT_EXPIRED || 
        validation_flags == MBEDTLS_X509_BADCERT_FUTURE) {
        
        bool is_emergency_bootstrap_mode = (bool)(uintptr_t)data;
        if (is_emergency_bootstrap_mode) {
            /* В аварійному режимі відновлення тимчасово ігноруємо помилку часу для виділеного сервера */
            *flags &= ~(MBEDTLS_X509_BADCERT_EXPIRED | MBEDTLS_X509_BADCERT_FUTURE);
            return 0;
        }
    }

    /* Якщо пошкоджено цифровий підпис або ім'я вузла не збігається — жорстке блокування */
    if (validation_flags & (MBEDTLS_X509_BADCERT_NOT_TRUSTED | MBEDTLS_X509_BADCERT_BAD_KEY)) {
        return -1;
    }

    return 0;
}
```
```cpp
#include <cstdint>
#include "mbedtls/x509_crt.h"

struct VerifyContext {
    bool emergencyBootstrapMode{false};
    bool allowClockSkewRecovery{false};
};

extern "C" int customCppVerifyCallback(void* parameter, mbedtls_x509_crt* /*crt*/, int /*depth*/, uint32_t* flags) noexcept {
    if (!flags) return -1;
    auto* context = static_cast<VerifyContext*>(parameter);

    const uint32_t currentFlags = *flags;

    // Перевірка на суто часові помилки (розсинхронізація RTC)
    constexpr uint32_t TimeFlagsMask = MBEDTLS_X509_BADCERT_EXPIRED | MBEDTLS_X509_BADCERT_FUTURE;
    if ((currentFlags & ~TimeFlagsMask) == 0 && (currentFlags & TimeFlagsMask) != 0) {
        if (context && (context->emergencyBootstrapMode || context->allowClockSkewRecovery)) {
            // Очищаємо прапорці часу лише для аварійного каналу відновлення
            *flags &= ~TimeFlagsMask;
            return 0;
        }
    }

    // Будь-яке порушення криптографічної цілісності або підпису призводить до негайної відмови
    constexpr uint32_t CriticalFlags = MBEDTLS_X509_BADCERT_NOT_TRUSTED | MBEDTLS_X509_BADCERT_BAD_KEY | MBEDTLS_X509_BADCERT_BAD_MD;
    if ((currentFlags & CriticalFlags) != 0) {
        return -1;
    }

    return 0;
}
```
:::

---

### Інтеграція з апаратними модулями безпеки (Secure Elements)

У пристроях промислового класу закриті ключі клієнтських сертифікатів не зберігаються у звичайній Flash-пам'яті мікроконтролера, а генеруються й запечатуються всередині виділеної захищеної мікросхеми (Secure Element, наприклад, Microchip ATECC608B, NXP EdgeLock SE050 або STMicroelectronics STSAFE-A110).

Взаємодія між Mbed TLS та крипточипом організовується через механізм абстракції закритого ключа (PK Wrapper):
1. **Зовнішній підпис (External Signing Callback):** під час фази `CertificateVerify` бібліотека Mbed TLS не звертається до сирих байтів ключа в оперативній пам'яті, а викликає зареєстровану функцію зворотного виклику.
2. **Апаратне обчислення дайджесту:** мікроконтролер передає обчислений SHA-256 хеш рукостискання по захищеній шині I2C до крипточипа.
3. **Генерація цифрового підпису:** чип Secure Element виконує обчислення ECDSA всередині свого захищеного кремнієвого ядра та повертає готову пару чисел `(r, s)`. Закритий ключ ніколи не з'являється на шинах плати чи в регістрах процесора.

---

### Робота з пам'яттю та керування ресурсами Mbed TLS

У мікроконтролерах із ядрами ARM Cortex-M0+/M4 керування пам'яттю для структур сертифікатів X.509 потребує особливої уваги через ризик фрагментації динамічної пам'яті (heap):
1. **Зв'язний список сертифікатів:** функція `mbedtls_x509_crt_parse` динамічно виділяє пам'ять під кожну нову ланку ланцюга. Для системи без динамічного виділення пам'яті (MISRA C compliance) конфігурація збирається з прапорцем `MBEDTLS_MEMORY_BUFFER_ALLOC_C`, де Mbed TLS отримує статично виділений масив у секції `.bss`.
2. **Очищення дескрипторів:** виклик `mbedtls_x509_crt_free` повністю звільняє всі пов'язані ланки списку. У реалізації C++ це інкапсульовано в деструкторі класу `DualTrustStore` за принципом RAII (Resource Acquisition Is Initialization), що унеможливлює витік пам'яті при виникненні винятків чи достроковому поверненні з функцій.
3. **Обмеження розміру буфера вводу-виводу:** за замовчуванням максимальний розмір фрагмента TLS становить 16384 байти (`MBEDTLS_SSL_IN_CONTENT_LEN`). Для вбудованих пристроїв використовується розширення `Max Fragment Length Negotiation` (RFC 6066), що зменшує розмір буфера до 2048 або 4096 байтів, заощаджуючи понад 24 КБ SRAM мікроконтролера.

---

### Регламент безпечної зміни активного слота (Atomic Slot Swap)

Для гарантування безперервності роботи під час оновлення сертифіката прошивка дотримується правил:
1. **Запис у резервний слот:** новий сертифікат записується виключно у неактивний сектор (`Slot B`), стан якого встановлюється як `SLOT_STANDBY`.
2. **Верифікація вмісту в пам'яті:** обчислюється контрольна сума CRC32 записаних даних, проводиться тестовий парсинг ASN.1 DER структури сертифіката бібліотекою Mbed TLS та перевірка коректності дати закінчення.
3. **Пробне рукостискання TLS:** мікроконтролер встановлює тестове TLS-з'єднання з сервером, використовуючи новий сертифікат у тестовому режимі.
4. **Атомарне перемикання:** лише після успішного завершення сеансу стан `Slot B` атомарно перезаписується на `SLOT_ACTIVE`, а старий `Slot A` позначається як `SLOT_STANDBY`. Якщо в процесі запису виникає збій живлення, завантажувач при старті продовжує використовувати старий перевірений `Slot A`.
5. **Зносостійкість Flash-пам'яті:** оскільки ротація сертифікатів відбувається 1–2 рази на рік, ресурс Flash-пам'яті (10 000–100 000 циклів стирання) практично не вичерпується, що гарантує надійність протягом усього життєвого циклу виробу.
