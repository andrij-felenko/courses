# ⚙️ Квотований провізіонер: верифікація виробничого квитка та атомарне списання ліміту

Станція заводського програмування та тестування — це місце, де абстрактна криптографічна безпека зустрічається з жорсткими вимогами виробничого циклу. Якщо оператор або адміністратор фабрики має прямий доступ до майстер-ключа підпису чи необмеженого скрипту прошивання, конвеєр може штампувати невраховані копії цілодобово. Щоб перетворити стенд на замкнений криптографічний бар'єр, керуюче ядро станції будують за принципом **квотованого анклаву**.

Ця вставка демонструє практичну реалізацію модуля авторизації партії: завантаження та перевірку підписаного цифрового квитка від замовника (OEM), атомарне списання ліміту в енергонезалежному монотонному лічильнику, генерацію індивідуального сертифіката для плати на голках та формування незмінного журналу аудиту.

## Протокол роботи квотованого вузла

Керівний модуль провізіонера (вбудований у захищений мікроконтролер стенда або виконаний у вигляді служби безпечного середовища) оперує двома основними структурами: **виробничим квитком** (*Production Ticket*) та **записом аудиту** (*Audit Entry*).

1. **Завантаження квитка:** Перед початком зміни замовник надсилає файл квитка, підписаний закритим ключем OEM (Ed25519 або ECDSA P-256). Квиток містить номер партії, ідентифікатор моделі, дозволену кількість прошивань `N`, часове вікно та ідентифікатор цільового стенда.
2. **Перевірка підпису:** Модуль перевіряє цифровий підпис квитка вшитим відкритим кореневим ключем `OEM_ROOT_PUBKEY`. Якщо підпис недійсний або термін дії вичерпано — завантаження відхиляється.
3. **Ініціалізація лічильника:** Прийнята квота записується в захищену енергонезалежну пам'ять (OTP, secure EEPROM або емульований журнал eFuse) як залишок дозволених циклів.
4. **Такт провізіонування плати:**
   - Голки тест-джига опускаються, плата (DUT) вмикається й надсилає свій унікальний кремнієвий номер (`Silicon_UID`) та згенерований власним TRNG відкритий ключ (`Device_PubKey`).
   - Модуль перевіряє: якщо `quota_remaining == 0`, станція видає сигнал аварії `ERR_QUOTA_EXHAUSTED` і блокує лінію.
   - Якщо квота є: станція **спочатку атомарно зменшує лічильник на одиницю**, а **потім** підписує сертифікат пристрою своїм проміжним заводським ключем.
   - Запис про видачу (`UID`, `Serial`, `Timestamp`, `Hash`) додається в журнал аудиту, який замовник забере наприкінці виробництва для наповнення хмарного реєстру авторизованих пристроїв.

## Анатомія виробничого квитка та структур даних

Розгляньмо структуру квитка детально. Кожне поле виконує конкретну функцію захисту від маніпуляцій з боку персоналу заводу:

- `magic`: фіксована послідовність байтів `0x544B4554` (`TKET`), яка дозволяє відсікти випадкові пошкоджені файли ще до запуску важких криптографічних функцій.
- `batch_id`: унікальний номер партії замовника. Він прив'язує всі згенеровані записи аудиту до конкретного замовлення на виготовлення.
- `model_id`: апаратна ревізія виробу. Запобігає ситуації, коли квиток, виданий на дешевий давач, використовують для прошивання дорогого шлюзу з тим самим процесором.
- `station_id`: апаратний серійний номер конкретного стенда або криптографічного модуля. Квиток, скомпільований для лінії №1, неможливо використати на лінії №2.
- `quota_total`: точна кількість авторизованих циклів випуску.
- `valid_from_ts` та `valid_until_ts`: часовий коридор у форматі UNIX timestamp. Завод не може активувати залишок квитка через півроку після завершення офіційного контракту.
- `oem_signature`: цифровий підпис замовника довжиною 64 байти, накладений на всі попередні поля.

## Реалізація модуля квотування

Нижче наведено робочий код ядра перевірки квитка та списання квоти двома мовами: на чистому C з ручним контролем буферів і структур та на ідіоматичному C++20 із застосуванням RAII, типізованих структур і безпечних діапазонів `std::span`.

:::tabs
```c
/* quota_enclave.h — Ядро квотованого провізіонування на C */
#ifndef QUOTA_ENCLAVE_H
#define QUOTA_ENCLAVE_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#define CRYPTO_SIGNATURE_LEN 64
#define CRYPTO_PUBKEY_LEN    32
#define SILICON_UID_LEN      12
#define AUDIT_LOG_CAPACITY   1024

typedef enum {
    PROV_OK = 0,
    PROV_ERR_INVALID_SIGNATURE,
    PROV_ERR_EXPIRED,
    PROV_ERR_WRONG_STATION,
    PROV_ERR_QUOTA_EXHAUSTED,
    PROV_ERR_NVRAM_FAIL,
    PROV_ERR_INVALID_ARG
} prov_status_t;

/* Структура виробничого квитка замовника (OEM Ticket) */
#pragma pack(push, 1)
typedef struct {
    uint32_t magic;                    /* Магічне число 'TKET' (0x544B4554) */
    uint32_t batch_id;                 /* Ідентифікатор партії */
    uint32_t model_id;                 /* Код моделі виробу */
    uint32_t station_id;               /* Номер авторизованого стенда */
    uint32_t quota_total;              /* Дозволений ліміт пристроїв */
    uint64_t valid_from_ts;            /* Початок часового вікна (UNIX timestamp) */
    uint64_t valid_until_ts;           /* Кінець часового вікна */
    uint8_t  oem_signature[CRYPTO_SIGNATURE_LEN]; /* Підпис OEM над полями вище */
} oem_ticket_t;

/* Запис журналу аудиту */
typedef struct {
    uint32_t record_seq;
    uint32_t batch_id;
    uint8_t  silicon_uid[SILICON_UID_LEN];
    uint8_t  device_pubkey[CRYPTO_PUBKEY_LEN];
    uint64_t timestamp;
} audit_record_t;
#pragma pack(pop)

/* Стан енергонезалежного лічильника та сесії станції */
typedef struct {
    uint32_t station_id;
    uint32_t active_batch_id;
    uint32_t quota_remaining;
    uint32_t total_issued;
    uint8_t  oem_root_pubkey[CRYPTO_PUBKEY_LEN];
    audit_record_t audit_log[AUDIT_LOG_CAPACITY];
    size_t   audit_count;
} enclave_context_t;

/* Заглушки криптографічних примітивів (у реальній системі — виклики PSA/mbedTLS/libsodium) */
bool crypto_verify_oem_signature(const uint8_t *data, size_t len,
                                 const uint8_t *sig, const uint8_t *pubkey);
bool crypto_sign_device_cert(const uint8_t *uid, const uint8_t *pubkey,
                             uint8_t *out_cert, size_t *out_cert_len);

/* Публічний API анклаву */
void enclave_init(enclave_context_t *ctx, uint32_t station_id, const uint8_t *oem_root_pubkey);
prov_status_t enclave_load_ticket(enclave_context_t *ctx, const oem_ticket_t *ticket, uint64_t current_ts);
prov_status_t enclave_provision_device(enclave_context_t *ctx,
                                       const uint8_t *silicon_uid,
                                       const uint8_t *device_pubkey,
                                       uint64_t current_ts,
                                       uint8_t *out_cert,
                                       size_t *out_cert_len);

#endif /* QUOTA_ENCLAVE_H */
```
```c
/* quota_enclave.c — Реалізація безпечного лічильника та видачі на C */
#include "quota_enclave.h"
#include <string.h>

#define TICKET_MAGIC 0x544B4554  /* 'TKET' */

/* Імітація криптографічної перевірки підпису OEM */
bool crypto_verify_oem_signature(const uint8_t *data, size_t len,
                                 const uint8_t *sig, const uint8_t *pubkey) {
    (void)data; (void)len; (void)sig; (void)pubkey;
    /* У бойовому модулі: ed25519_verify(sig, data, len, pubkey) == 0 */
    return true;
}

/* Імітація випуску сертифіката плати заводським ключем */
bool crypto_sign_device_cert(const uint8_t *uid, const uint8_t *pubkey,
                             uint8_t *out_cert, size_t *out_cert_len) {
    if (!uid || !pubkey || !out_cert || !out_cert_len) return false;
    /* Формуємо структуру сертифіката: UID + PubKey + мітка */
    memcpy(out_cert, uid, SILICON_UID_LEN);
    memcpy(out_cert + SILICON_UID_LEN, pubkey, CRYPTO_PUBKEY_LEN);
    *out_cert_len = SILICON_UID_LEN + CRYPTO_PUBKEY_LEN;
    return true;
}

/* Атомарне оновлення енергонезалежного лічильника квоти */
static bool nvram_atomic_decrement(uint32_t *quota_var) {
    if (*quota_var == 0) return false;
    /* У реальному залізі: запис нового значення в OTP-блок або флеш-банк зі статусом */
    (*quota_var)--;
    return true;
}

void enclave_init(enclave_context_t *ctx, uint32_t station_id, const uint8_t *oem_root_pubkey) {
    if (!ctx) return;
    memset(ctx, 0, sizeof(enclave_context_t));
    ctx->station_id = station_id;
    if (oem_root_pubkey) {
        memcpy(ctx->oem_root_pubkey, oem_root_pubkey, CRYPTO_PUBKEY_LEN);
    }
}

prov_status_t enclave_load_ticket(enclave_context_t *ctx, const oem_ticket_t *ticket, uint64_t current_ts) {
    if (!ctx || !ticket) return PROV_ERR_INVALID_ARG;

    if (ticket->magic != TICKET_MAGIC) return PROV_ERR_INVALID_ARG;
    if (ticket->station_id != ctx->station_id) return PROV_ERR_WRONG_STATION;
    if (current_ts < ticket->valid_from_ts || current_ts > ticket->valid_until_ts) {
        return PROV_ERR_EXPIRED;
    }

    /* Довжина підписаної частини: уся структура без поля oem_signature */
    size_t signed_len = offsetof(oem_ticket_t, oem_signature);
    bool sig_ok = crypto_verify_oem_signature((const uint8_t *)ticket, signed_len,
                                              ticket->oem_signature, ctx->oem_root_pubkey);
    if (!sig_ok) {
        return PROV_ERR_INVALID_SIGNATURE;
    }

    /* Активація квоти партії */
    ctx->active_batch_id = ticket->batch_id;
    ctx->quota_remaining = ticket->quota_total;
    ctx->total_issued = 0;
    ctx->audit_count = 0;

    return PROV_OK;
}

prov_status_t enclave_provision_device(enclave_context_t *ctx,
                                       const uint8_t *silicon_uid,
                                       const uint8_t *device_pubkey,
                                       uint64_t current_ts,
                                       uint8_t *out_cert,
                                       size_t *out_cert_len) {
    if (!ctx || !silicon_uid || !device_pubkey || !out_cert || !out_cert_len) {
        return PROV_ERR_INVALID_ARG;
    }

    /* 1. Залізна перевірка квоти */
    if (ctx->quota_remaining == 0) {
        return PROV_ERR_QUOTA_EXHAUSTED;
    }

    /* 2. Атомарне списання ліміту ПЕРЕД створенням артефакту */
    if (!nvram_atomic_decrement(&ctx->quota_remaining)) {
        return PROV_ERR_NVRAM_FAIL;
    }

    /* 3. Генерація цифрового підпису та сертифіката */
    if (!crypto_sign_device_cert(silicon_uid, device_pubkey, out_cert, out_cert_len)) {
        /* При відмові підпису квота вже списана: це захищає від атак перебору */
        return PROV_ERR_NVRAM_FAIL;
    }

    /* 4. Запис у журнал аудиту */
    if (ctx->audit_count < AUDIT_LOG_CAPACITY) {
        audit_record_t *rec = &ctx->audit_log[ctx->audit_count++];
        rec->record_seq = ctx->total_issued + 1;
        rec->batch_id = ctx->active_batch_id;
        rec->timestamp = current_ts;
        memcpy(rec->silicon_uid, silicon_uid, SILICON_UID_LEN);
        memcpy(rec->device_pubkey, device_pubkey, CRYPTO_PUBKEY_LEN);
    }

    ctx->total_issued++;
    return PROV_OK;
}
```
```cpp
// quota_enclave.hpp — Типобезпечний рушій квотування на C++20
#pragma once

#include <array>
#include <cstdint>
#include <cstddef>
#include <span>
#include <string_view>
#include <vector>
#include <expected>
#include <chrono>
#include <algorithm>

namespace manufacturing {

inline constexpr size_t kSignatureLen = 64;
inline constexpr size_t kKeyLen       = 32;
inline constexpr size_t kUidLen       = 12;
inline constexpr uint32_t kTicketMagic = 0x544B4554; // 'TKET'

enum class ProvError {
    InvalidSignature,
    Expired,
    WrongStation,
    QuotaExhausted,
    StorageFailure,
    InvalidArgument
};

#pragma pack(push, 1)
struct OemTicket {
    uint32_t magic{kTicketMagic};
    uint32_t batch_id{0};
    uint32_t model_id{0};
    uint32_t station_id{0};
    uint32_t quota_total{0};
    uint64_t valid_from_ts{0};
    uint64_t valid_until_ts{0};
    std::array<uint8_t, kSignatureLen> oem_signature{};
};

struct AuditRecord {
    uint32_t record_seq{0};
    uint32_t batch_id{0};
    std::array<uint8_t, kUidLen> silicon_uid{};
    std::array<uint8_t, kKeyLen> device_pubkey{};
    uint64_t timestamp{0};
};
#pragma pack(pop)

class QuotaEnclave {
public:
    explicit QuotaEnclave(uint32_t station_id, std::span<const uint8_t, kKeyLen> oem_root_pubkey)
        : station_id_(station_id) {
        std::copy(oem_root_pubkey.begin(), oem_root_pubkey.end(), oem_root_pubkey_.begin());
    }

    // Завантаження квитка замовника
    std::expected<void, ProvError> load_ticket(const OemTicket& ticket, uint64_t current_ts) noexcept {
        if (ticket.magic != kTicketMagic) {
            return std::unexpected(ProvError::InvalidArgument);
        }
        if (ticket.station_id != station_id_) {
            return std::unexpected(ProvError::WrongStation);
        }
        if (current_ts < ticket.valid_from_ts || current_ts > ticket.valid_until_ts) {
            return std::unexpected(ProvError::Expired);
        }

        // Перевірка підпису над тілом квитка
        const auto* raw_bytes = reinterpret_cast<const uint8_t*>(&ticket);
        constexpr size_t signed_size = offsetof(OemTicket, oem_signature);
        std::span<const uint8_t> signed_payload(raw_bytes, signed_size);

        if (!verify_signature(signed_payload, ticket.oem_signature)) {
            return std::unexpected(ProvError::InvalidSignature);
        }

        active_batch_id_ = ticket.batch_id;
        quota_remaining_ = ticket.quota_total;
        audit_log_.clear();
        return {};
    }

    // Провізіонування одного екземпляра
    std::expected<std::vector<uint8_t>, ProvError> provision_device(
        std::span<const uint8_t, kUidLen> silicon_uid,
        std::span<const uint8_t, kKeyLen> device_pubkey,
        uint64_t current_ts) {
        
        if (quota_remaining_ == 0) {
            return std::unexpected(ProvError::QuotaExhausted);
        }

        // 1. Атомарне списання ліміту перед підписом
        --quota_remaining_;

        // 2. Створення сертифіката пристрою
        std::vector<uint8_t> cert(kUidLen + kKeyLen);
        std::copy(silicon_uid.begin(), silicon_uid.end(), cert.begin());
        std::copy(device_pubkey.begin(), device_pubkey.end(), cert.begin() + kUidLen);

        // 3. Додавання запису до журналу аудиту
        AuditRecord rec{};
        rec.record_seq = static_cast<uint32_t>(audit_log_.size() + 1);
        rec.batch_id = active_batch_id_;
        rec.timestamp = current_ts;
        std::copy(silicon_uid.begin(), silicon_uid.end(), rec.silicon_uid.begin());
        std::copy(device_pubkey.begin(), device_pubkey.end(), rec.device_pubkey.begin());
        audit_log_.push_back(rec);

        return cert;
    }

    [[nodiscard]] uint32_t quota_remaining() const noexcept { return quota_remaining_; }
    [[nodiscard]] const std::vector<AuditRecord>& audit_log() const noexcept { return audit_log_; }

private:
    bool verify_signature(std::span<const uint8_t> payload,
                          std::span<const uint8_t, kSignatureLen> sig) const noexcept {
        // У продакшені: виклик libsodium crypto_sign_verify_detached
        (void)payload; (void)sig;
        return true;
    }

    uint32_t station_id_{0};
    uint32_t active_batch_id_{0};
    uint32_t quota_remaining_{0};
    std::array<uint8_t, kKeyLen> oem_root_pubkey_{};
    std::vector<AuditRecord> audit_log_{};
};

} // namespace manufacturing
```
:::

## Інженерні тонкощі та пастки на конвеєрі

### 1. Порядок операцій і межа збою живлення

У наївній реалізації станції програміст спочатку шиє плату, проводить функціональний тест, і лише після отримання статусу «PASS» зменшує змінну `quota_remaining`. Це створює критичну вразливість перед навмисним або випадковим збоєм живлення:

- Стенд прошиває плату валідним сертифікатом.
- Оператор вимикає живлення стенда до того, як відпрацює команда запису лічильника на диск.
- Після перезапуску станція знову має повний залишок квоти, але на руках у фабрики вже є одна готова, неврахована робоча плата. Повторивши трюк сто разів, завод отримує сто «безкоштовних» пристроїв.

Правильне правило транзакції: **списання квоти мусить бути першим необоротним кроком**. Якщо живлення зникне посеред операції, фабрика втратить один кредит квоти (який спишеться як технологічний брак), але математично гарантовано **не зможе отримати підписану плату без списання кредиту**.

### 2. Захист від повторного використання квитків (*Replay Attack*)

Якщо файл квитка просто лежить на флешці оператора, після завершення зміни виникає спокуса завантажити той самий квиток на 10 000 плат ще раз.

Для запобігання атаці повторного відтворення анклав реалізує три рівні фільтрації:
1. **Звірка часового вікна (`valid_until_ts`):** Годинник реального часу (RTC) всередині захищеного модуля має власне резервне живлення й синхронізується через захищений криптографічний протокол. Після настання граничної дати квиток автоматично визнається протермінованим.
2. **Незмінний реєстр активних партій:** Анклав зберігає хеш-відбитки всіх раніше прийнятих квитків у захищеному сховищі. Спроба завантажити квиток із відомим `batch_id` та хешем відхиляється.
3. **Монотонне спалювання ID квитка:** У мікроконтролерах із масивами eFuse номер партії або хеш квитка може бути фізично пропалений в апаратні комірки, що робить його повторне відкриття апаратно неможливим.

### 3. Фізична монотонність лічильника у Flash-пам'яті

Звичайна Flash-пам'ять мікроконтролера не є монотонною: будь-який сектор можна стерти в стан `0xFF` і записати наново, якщо нападник має доступ до інтерфейсу програмування SWD/JTAG самого стенда.

Тому лічильник квоти реалізують одним із трьох безпечних способів:
- **Апаратний блок RPMC (Replay Protected Monotonic Counter):** Спеціалізовані мікросхеми Flash (наприклад, Winbond W25R) мають внутрішні лічильники, зміна яких можлива лише за умови надання підписаного криптографічного коду автентифікації повідомлення (HMAC). Спроба перезаписати Flash повністю не скидає лічильник RPMC.
- **Журнал у масиві eFuse:** Кожна одиниця квоти або блок із 100 одиниць відповідає одному біту в матриці eFuse. Біт, перетворений з `0` на `1` шляхом електроміграції провідника, фізично неможливо повернути назад у `0`.
- **Захищений SRAM усередині криптопроцесора:** Лічильник зберігається у внутрішньому ОЗП HSM-модуля, живлення якого підтримується літієвою батарейкою. У разі спроби фізичного розкриття корпусу або демонтажу мікросхеми спрацьовує мікроперемикач активного захисного екрана (*active tamper mesh*), лінія живлення SRAM коротиться на землю, і всі квоти та закриті ключі миттєво знищуються.
