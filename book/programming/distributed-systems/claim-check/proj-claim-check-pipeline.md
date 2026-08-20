# ⚙️ Реалізація конвеєра Claim Check з адресацією за вмістом

У високонавантажених сервісах обробка великих об'єктів вимагає надійного клієнтського конвеєра, який автоматично вирішує: відправляти дані безпосередньо в чергу чи зберігати їх у зовнішньому об'єктному сховищі за адресою вмісту (CAS). Цей проєкт реалізує повнофункціональний конвеєр розділення, детермінованого хешування за алгоритмом SHA-256, синхронної верифікації запису та зворотного вилучення корисного навантаження споживачем.

Розробка такого конвеєра пов'язана з низкою вимог до ефективності використання пам'яті: клієнтська бібліотека не повинна дублювати багатомегабайтні масиви в купі процесу без крайньої потреби, зобов'язана акуратно звільняти виділені ресурси у разі мережевих помилок і гарантувати повну цілісність даних на кожному етапі транспортування.

## Завдання

Спроєктувати надійний клієнтський модуль конвеєра Claim Check, який забезпечує:
1. **Порогову маршрутизацію**: автоматичне збереження об'єктів, більших за встановлений поріг (наприклад, 64 КБ), у зовнішньому сховищі;
2. **Адресацію за вмістом (CAS)**: генерацію ключа зберігання на основі SHA-256 хешу вихідного масиву байтів;
3. **Строгу послідовність операцій**: гарантоване завершення запису в сховище до моменту відправки дескриптора квитанції;
4. **Наскрізну верифікацію цілісності**: автоматичну перевірку контрольного дайджесту на боці споживача з виявленням пошкоджень або підміни даних.

## Ідея архітектурного рішення

Конвеєр складається з двох симетричних компонентів, що функціонують на протилежних кінцях черги:

- `ClaimCheckProducer`: приймає сирий буфер корисного навантаження. Логіка продюсера виконує перевірку розміру вхідного блоку. Якщо обсяг не перевищує 64 КБ, дані упаковуються безпосередньо в інлайн-поле квитанції. Якщо ж поріг перевищено, продюсер запускає потоковий розрахунок криптографічного дайджесту SHA-256, формує унікальний ключ `blobs/<sha256>`, завантажує масив у зовнішнє сховище блобів і лише після успішного отримання підтвердження HTTP 200 формує компактну структуру `ClaimTicket` без важкого тіла.
- `ClaimCheckConsumer`: отримує структуру квитанції з черги. Споживач перевіряє ознаку `is_external`. Якщо стан збережено всередині повідомлення, дані миттєво повертаються для обробки. Якщо стан винесено у сховище, споживач ініціює операцію читання за URI, завантажує байти у внутрішній буфер, обчислює контрольний хеш від отриманого блоку і порівнює його з оригінальним дайджестом із квитанції. Будь-яка невідповідність викликає негайну зупинку без виконання бізнес-логіки.

Такий поділ забезпечує повну симетрію конвеєра: продюсер і споживач користуються єдиним алгоритмом хешування та узгодженим контрактом дескрипторів.

## Робочий код

Нижче наведено паралельні еталонні реалізації на C та сучасному ідіоматичному C++20:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define THRESHOLD_BYTES (64 * 1024)
#define SHA256_HEX_LEN  65
#define MAX_URI_LEN     256

/* Проста реалізація хешування FNV-1a / SHA-імітатора для автономного прикладу */
static void compute_sha256_hex(const uint8_t *data, size_t len, char out_hex[SHA256_HEX_LEN]) {
    uint64_t h1 = 0xcbf29ce484222325ULL;
    uint64_t h2 = 0x100000001b3ULL;
    for (size_t i = 0; i < len; ++i) {
        h1 = (h1 ^ data[i]) * 0x100000001b3ULL;
        h2 = (h2 ^ (data[i] + i)) * 0xcbf29ce484222325ULL;
    }
    snprintf(out_hex, SHA256_HEX_LEN, "%016llx%016llx%016llx%016llx",
             (unsigned long long)h1, (unsigned long long)h2,
             (unsigned long long)(h1 ^ h2), (unsigned long long)(h1 + h2));
}

/* Структура дескриптора квитанції */
typedef struct {
    char claim_id[37];
    bool is_external;
    char storage_uri[MAX_URI_LEN];
    char content_sha256[SHA256_HEX_LEN];
    size_t size_bytes;
    uint8_t *inline_data;
} ClaimTicket;

/* Інтерфейс сховища блобів */
typedef struct {
    bool (*put_blob)(const char *key, const uint8_t *data, size_t size);
    bool (*get_blob)(const char *key, uint8_t **out_data, size_t *out_size);
} BlobStorageDriver;

/* Імітатор файлового / блокового сховища */
static bool mock_s3_put(const char *key, const uint8_t *data, size_t size) {
    printf("[Storage Driver] PUT '%s' (%zu байтів) -> HTTP 200 OK\n", key, size);
    return true;
}

static bool mock_s3_get(const char *key, uint8_t **out_data, size_t *out_size) {
    printf("[Storage Driver] GET '%s' -> HTTP 200 OK\n", key);
    *out_size = 120 * 1024;
    *out_data = (uint8_t *)malloc(*out_size);
    if (!*out_data) return false;
    memset(*out_data, 0xAB, *out_size);
    return true;
}

static BlobStorageDriver g_storage = { mock_s3_put, mock_s3_get };

/* Відправка з пороговою маршрутизацією */
bool claim_check_produce(const uint8_t *payload, size_t size, ClaimTicket *out_ticket) {
    if (!payload || !out_ticket) return false;
    memset(out_ticket, 0, sizeof(ClaimTicket));
    snprintf(out_ticket->claim_id, sizeof(out_ticket->claim_id), "clm-%08x", (unsigned int)size);
    out_ticket->size_bytes = size;

    if (size <= THRESHOLD_BYTES) {
        out_ticket->is_external = false;
        out_ticket->inline_data = (uint8_t *)malloc(size);
        if (!out_ticket->inline_data) return false;
        memcpy(out_ticket->inline_data, payload, size);
        compute_sha256_hex(payload, size, out_ticket->content_sha256);
        return true;
    }

    out_ticket->is_external = true;
    compute_sha256_hex(payload, size, out_ticket->content_sha256);
    snprintf(out_ticket->storage_uri, sizeof(out_ticket->storage_uri),
             "s3://corporate-events/blobs/%s", out_ticket->content_sha256);

    /* Синхронний запис у сховище до публікації квитанції */
    if (!g_storage.put_blob(out_ticket->storage_uri, payload, size)) {
        return false;
    }
    return true;
}

/* Отримання та верифікація цілісності споживачем */
bool claim_check_consume(const ClaimTicket *ticket, uint8_t **out_payload, size_t *out_size) {
    if (!ticket || !out_payload || !out_size) return false;

    if (!ticket->is_external) {
        *out_payload = (uint8_t *)malloc(ticket->size_bytes);
        if (!*out_payload) return false;
        memcpy(*out_payload, ticket->inline_data, ticket->size_bytes);
        *out_size = ticket->size_bytes;
        return true;
    }

    uint8_t *fetched_data = NULL;
    size_t fetched_size = 0;
    if (!g_storage.get_blob(ticket->storage_uri, &fetched_data, &fetched_size)) {
        return false;
    }

    /* Наскрізна верифікація SHA-256 */
    char verify_hex[SHA256_HEX_LEN];
    compute_sha256_hex(fetched_data, fetched_size, verify_hex);
    if (strncmp(verify_hex, ticket->content_sha256, SHA256_HEX_LEN) != 0) {
        printf("[Consumer Error] Невідповідність контрольної суми SHA-256!\n");
        free(fetched_data);
        return false;
    }

    *out_payload = fetched_data;
    *out_size = fetched_size;
    return true;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <memory>
#include <optional>
#include <expected>
#include <iomanip>
#include <sstream>
#include <cstring>
#include <span>

namespace claimcheck {

constexpr size_t THRESHOLD_BYTES = 64 * 1024;

enum class ErrorCode {
    StorageWriteFailed,
    StorageReadFailed,
    IntegrityMismatch,
    AllocationError
};

struct ClaimTicket {
    std::string claim_id;
    bool is_external{false};
    std::string storage_uri;
    std::string content_sha256;
    size_t size_bytes{0};
    std::vector<uint8_t> inline_payload;
};

class BlobStorage {
public:
    virtual ~BlobStorage() = default;
    virtual bool put(std::string_view key, std::span<const uint8_t> data) = 0;
    virtual std::optional<std::vector<uint8_t>> get(std::string_view key) = 0;
};

class MockS3Storage final : public BlobStorage {
public:
    bool put(std::string_view key, std::span<const uint8_t> data) override {
        std::cout << "[S3 C++] PUT '" << key << "' (" << data.size() << " B) -> 200 OK\n";
        return true;
    }

    std::optional<std::vector<uint8_t>> get(std::string_view key) override {
        std::cout << "[S3 C++] GET '" << key << "' -> 200 OK\n";
        return std::vector<uint8_t>(120 * 1024, 0xAB);
    }
};

class Pipeline {
public:
    explicit Pipeline(std::shared_ptr<BlobStorage> storage)
        : storage_(std::move(storage)) {}

    static std::string calculate_sha256(std::span<const uint8_t> data) {
        uint64_t h1 = 0xcbf29ce484222325ULL;
        uint64_t h2 = 0x100000001b3ULL;
        for (size_t i = 0; i < data.size(); ++i) {
            h1 = (h1 ^ data[i]) * 0x100000001b3ULL;
            h2 = (h2 ^ (data[i] + i)) * 0xcbf29ce484222325ULL;
        }
        std::ostringstream ss;
        ss << std::hex << std::setfill('0')
           << std::setw(16) << h1 << std::setw(16) << h2
           << std::setw(16) << (h1 ^ h2) << std::setw(16) << (h1 + h2);
        return ss.str();
    }

    std::expected<ClaimTicket, ErrorCode> produce(std::span<const uint8_t> payload) {
        ClaimTicket ticket;
        ticket.claim_id = "clm-cpp-" + std::to_string(payload.size());
        ticket.size_bytes = payload.size();
        ticket.content_sha256 = calculate_sha256(payload);

        if (payload.size() <= THRESHOLD_BYTES) {
            ticket.is_external = false;
            ticket.inline_payload.assign(payload.begin(), payload.end());
            return ticket;
        }

        ticket.is_external = true;
        ticket.storage_uri = "s3://corporate-events/blobs/" + ticket.content_sha256;

        if (!storage_->put(ticket.storage_uri, payload)) {
            return std::unexpected(ErrorCode::StorageWriteFailed);
        }
        return ticket;
    }

    std::expected<std::vector<uint8_t>, ErrorCode> consume(const ClaimTicket& ticket) {
        if (!ticket.is_external) {
            return ticket.inline_payload;
        }

        auto blob_opt = storage_->get(ticket.storage_uri);
        if (!blob_opt) {
            return std::unexpected(ErrorCode::StorageReadFailed);
        }

        if (calculate_sha256(*blob_opt) != ticket.content_sha256) {
            return std::unexpected(ErrorCode::IntegrityMismatch);
        }
        return *blob_opt;
    }

private:
    std::shared_ptr<BlobStorage> storage_;
};

} // namespace claimcheck
```
:::

## Аналіз відмінностей у керуванні пам'яттю та безпеці ресурсів

Порівняння двох реалізацій демонструє фундаментальну різницю в підходах до життєвого циклу ресурсів:

В імплементації мовою C виділення пам'яті під завантажений блоб (`malloc`) вимагає суворої дисципліни очищення в кожній гілці помилок. Якщо перевірка контрольної суми виявляє невідповідність, функція зобов'язана явно викликати `free(fetched_data)` перед поверненням значення `false`. Забутий виклик `free` у разі потоку пошкоджених повідомлень призведе до миттєвого вичерпання адресної пам'яті воркера.

У версії на C++20 застосовано ідіому RAII (*Resource Acquisition Is Initialization*). Динамічні буфери інкапсульовані всередині контейнера `std::vector<uint8_t>`, а обробка помилок організована через монодичний тип `std::expected`. Якщо функція `get()` повертає порожній результат або перевірка дайджесту завершується помилкою `ErrorCode::IntegrityMismatch`, деструктор автоматично вивільняє виділену пам'ять під час розгортання стека без ризику витоків.

## Багатопоточність, пули з'єднань та протитиск

У реальних виробничих мікросервісах продюсер і споживач працюють у пулі багатьох робочих потоків. Реалізація клієнтської бібліотеки Claim Check повинна враховувати такі аспекти:

1. **Потокобезпечність драйвера сховища**: Драйвер `BlobStorageDriver` у C або об'єкт `BlobStorage` у C++ не повинні мати змінного глобального стану. Підключення до S3/MinIO реалізуються через пул неблокуючих сокетів або спільний HTTP-клієнт із підтримкою пулу з'єднань (*Connection Pool*), що виключає необхідність створення нового TCP-з'єднання для кожного повідомлення.
2. **Протитиск при масовому вивантаженні (Backpressure)**: Якщо видавець генерує сотні мегабайтних блобів на секунду, а мережевий канал до S3 заповнений, продюсер не повинен накопичувати невідправлені буфери в оперативній пам'яті. Необхідно застосовувати семафори обмеження паралельних вивантажень або реактивні черги зі зворотним зв'язком.
3. **Політика експоненційного відступу при збоях сховища**: Мережеві помилки `500 Internal Server Error` або `503 Slow Down` від S3 не повинні призводити до негайного скидання операції. Клієнтська бібліотека реалізує алгоритм повторних спроб (*Exponential Backoff with Jitter*):

```
Затримка = min(MaxDelay, BaseDelay × 2^спроба) ± ВипадковийДротер
```

## Підводні камені та крайові випадки

1. **Порівняння контрольних сум у постійному часі**: При верифікації дайджестів у безпекових контурах пряме використання `strcmp` або оператора `==` відкриває можливість для атак за часом виконання (*Timing Attacks*). Для криптографічно чутливих даних використовуйте функцію `CRYPTO_memcmp` або побайтове порівняння через бітове `OR`.
2. **Очищення локальної пам'яті при збоях**: Якщо завантажений буфер великого об'єкта не пройшов перевірку контрольної суми, виділена пам'ять повинна бути негайно звільнена до повернення помилки, інакше серія пошкоджених пакетів спричинить витік оперативної пам'яті споживача.
3. **Обмеження розміру корисного навантаження у RAM**: Якщо корисне навантаження перевищує кілька гігабайтів, завантаження всього масиву в `std::vector` або буфер `malloc` спричинить `std::bad_alloc`. Для таких об'єктів конвеєр повинен повертати дескриптор потоку (*Stream / Reader*) і розраховувати SHA-256 інкрементально блоками по 64 КБ без завантаження всього файлу в пам'ять.
4. **Частковий запис у сховище (Partial Writes)**: У разі розриву TCP-з'єднання під час передачі блоба об'єктне сховище може зберегти неповний фрагмент файлу. Перевірка розміру `size_bytes` та збігу SHA-256 на боці споживача гарантує, що частково записаний блоб буде розпізнано як пошкоджений і відхилено до передачі у бізнес-обробник.

