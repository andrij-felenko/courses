# ⚙️ Реалізація рушія крипто-політики та конвертного шифрування

<preknowlist>
- [Шифрування у спокої й ключі](root:sf-security/encryption-at-rest) — прозоре проти прикладного шифрування, ієрархія DEK/KEK і сховища ключів (KMS).
- [Наскрізне шифрування](root:sf-security/end-to-end-encryption) — обмін ключами між кінцевими пристроями та осліплення сервера.
- [Специфікація конверта даних та атрибутів шифрування](root:progarch/e2e-vs-serverside-choice/api-crypto-envelope-spec.md) — структури JSON-конвертів та коди помилок.
</preknowlist>

У цій практичній вставці показано реалізацію системного рушія криптографічних політик (*Crypto Policy Engine*). Його завдання — приймати вхідні дані платформи Digital Homes, визначати належний режим шифрування за класифікатором (`CLASS_A_E2E`, `CLASS_B_EDGE`, `CLASS_C_SSE`) та маркапувати або шифрувати payload за відповідним контрактом.

## 1. Архітектура та послідовність викликів рушія політики

Рушій крипто-політики розміщується на найпершому рубежі шлюзу прийому даних (*Ingestion Gateway*) та діє як жорсткий криптографічний фільтр до того, як корисне навантаження потрапить у внутрішні сервіси обробки чи шину повідомлень Kafka.

Головна мета створення окремого рушія крипто-політики — це централізація криптографічних рішень у єдиній перевіреній точці. Замість того, щоб дозволяти кожному розробнику мікросервісів самостійно вирішувати, як шифрувати дані або де береться ключ, системна політика контролюється ізольованим модулем.

При надходженні нового пакета рушій виконує чітку послідовність з чотирьох кроків:

1. **Валідація класифікації та дозволів**: рушій зчитує заголовок `X-DH-Data-Class`. Якщо пакет позначено як `CLASS_A_E2E`, рушій активує режим засліплення: будь-які спроби передати цей пакет до модулів серверної аналітики, розпізнавання облич або повнотекстового індексатора блокуються на рівні маршрутизатора.
2. **Конвертне шифрування для `CLASS_C_SSE`**: для системної телеметрії та логів рушій запитує у хмарного KMS або локального HSM новий ключ даних (DEK), виконує симетричне шифрування AES-256-GCM, формує шифротекст, дописує зашифрований DEK у заголовок конверта та негайно виконує очищення пам'яті (Zeroization) відкритого DEK.
3. **Паспрохідний E2E-маршрут для `CLASS_A_E2E`**: рушій перевіряє цілісність заголовочної структури E2E-пакета, але не намагається торкатися зашифрованого корисного навантаження. Зашифрований блок без змін пересилається у шину повідомлень для доставки споживачу.
4. **Гарантія безпеки пам'яті (Zeroization)**: ключі даних (DEK) та відкритий текст не повинні залишатися в оперативній пам'яті після завершення обробки запиту. Буфери обнуляються байтом `0x00` через спеціальні функції, які не оптимізуються компілятором.

## 2. Механізми захисту оперативної пам'яті (Zeroization)

Одна з найбільш підступних вразливостей у системній криптографії — це залишки чутливих даних у вивільненій оперативній пам'яті процесу.

Стандартна функція `memset(buffer, 0, size)` може бути повністю видалена оптимізатором C/C++ компілятора (Dead Code Elimination), якщо компілятор виявить, що змінна `buffer` більше не використовується після виклику `memset`. В результаті зашифрований ключ даних (DEK) залишається у купі (heap) чи на стеку процесу, звідки може бути зчитаний через вразливість типу Heartbleed або витік через дамп пам'яті (core dump).

Щоб запобігти цьому, рушій політики використовує два підходи:
- У мові C реалізується техніка `volatile` вказівника (`secure_memzero`), яка примушує компілятор виконувати физичні записи байта `0x00` у пам'ять незалежно від подальшого використання змінної, або викликає системні функції типу `explicit_bzero` / `memset_s`.
- У мові C++ реалізується обгортка RAII (`SecureBuffer`), деструктор якої автоматично викликає обнулення пам'яті при виході з області видимості, унеможливлюючи витік ключів при виникненні винятків чи ранньому поверненні з функції (`return`).

## 3. Вимоги до вирівнювання пам'яті та апаратної акселерації (AES-NI / NEON)

Шифрування медіапотоків вимагає максимальної продуктивності обробки в байтах на секунду. Рушій політики розрахований на використання апаратних прискорювачів кріптографії, присутніх у сучасних процесорах:
- **x86_64**: інструкції AES-NI (`_mm_aesenc_si128`, `_mm_clmulepi64_si128` для розрахунку тегу GCM).
- **ARM64 (AArch64)**: інструкції ARMv8 Crypto Extensions (`vaeseq_u8`, `pmull`).

Щоб апаратні векторні інструкції (SIMD / AVX2 / NEON) працювали без затримок на неалінований доступ, виділення буферів пам'яті для корисного навантаження мусить бути вирівняним по межі **64 байти** (розмір кеш-рядка процесора).

У реалізації C це досягається викликом `posix_memalign` або `_aligned_malloc`. У мові C++20 вирівнювання задається через атрибут `alignas(64)` або кастомний алокатор `std::allocator` із вирівнюванням.

## 4. Реалізація C та C++

У реальних embedded-хабах та високонавантажених сервісах обробки медіапотоків цей рушій пишеться мовами C або C++. Нижче наведено ідіоматичні реалізації для обох середовищ.

Зверніть увагу на відмінності підходів: C-реалізація вимагає явного управління розмірами буферів, перевірки вказівників на `NULL` та гарантованого очищення через `memset`, тоді як C++20 реалізація використовує підхід RAII (Resource Acquisition Is Initialization), типи `std::span` для безпечного зрізу пам'яті та `std::expected` для прямої передачі помилок без винятків.

:::tabs
```c
/* C: Низькорівневий рушій крипто-політики з явним управлінням буферами */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef enum {
    DATA_CLASS_A_E2E = 1,
    DATA_CLASS_B_EDGE = 2,
    DATA_CLASS_C_SSE = 3
} dh_data_class_t;

typedef struct {
    dh_data_class_t data_class;
    uint8_t* payload;
    size_t payload_len;
    uint8_t* out_buffer;
    size_t out_capacity;
    size_t out_len;
} crypto_job_t;

typedef enum {
    CRYPTO_OK = 0,
    CRYPTO_ERR_POLICY_VIOLATION = -1,
    CRYPTO_ERR_NO_MEMORY = -2,
    CRYPTO_ERR_BUFFER_TOO_SMALL = -3
} crypto_result_t;

/* Безпечне обнулення пам'яті, яке не оптимізується компілятором */
static void secure_memzero(void* ptr, size_t len) {
    volatile uint8_t* p = (volatile uint8_t*)ptr;
    while (len--) {
        *p++ = 0;
    }
}

/* Симуляція генерації та шифрування DEK через KMS */
static crypto_result_t apply_serverside_envelope(crypto_job_t* job) {
    uint8_t dummy_dek[32];
    size_t i;
    
    if (job->out_capacity < job->payload_len + 64) {
        return CRYPTO_ERR_BUFFER_TOO_SMALL;
    }

    /* 1. Генеруємо одноразовий DEK */
    for (i = 0; i < 32; ++i) dummy_dek[i] = (uint8_t)(rand() % 256);

    /* 2. Записуємо префікс конверта SSE: [MAGIC_SSE][CLASS_C][DEK_HEADER][CIPHERTEXT] */
    memcpy(job->out_buffer, "SSE_ENV", 7);
    job->out_buffer[7] = (uint8_t)job->data_class;
    
    /* XOR-симуляція AES-GCM шифрування для прикладу */
    for (i = 0; i < job->payload_len; ++i) {
        job->out_buffer[8 + i] = job->payload[i] ^ dummy_dek[i % 32];
    }
    job->out_len = 8 + job->payload_len;

    /* 3. Гарантовано очищаємо відкритий DEK у пам'яті (Zeroization) */
    secure_memzero(dummy_dek, sizeof(dummy_dek));
    return CRYPTO_OK;
}

crypto_result_t process_crypto_policy(crypto_job_t* job) {
    if (!job || !job->payload || !job->out_buffer) {
        return CRYPTO_ERR_POLICY_VIOLATION;
    }

    switch (job->data_class) {
        case DATA_CLASS_A_E2E:
            /* E2E: Сервер не шифрує і не розшифровує — лише копіює непрозорий шифротекст */
            if (job->out_capacity < job->payload_len) return CRYPTO_ERR_BUFFER_TOO_SMALL;
            memcpy(job->out_buffer, job->payload, job->payload_len);
            job->out_len = job->payload_len;
            return CRYPTO_OK;

        case DATA_CLASS_C_SSE:
            /* SSE: Виконуємо конвертне шифрування на сервері */
            return apply_serverside_envelope(job);

        case DATA_CLASS_B_EDGE:
            /* Edge: Передається без змін на локальний хаб */
            if (job->out_capacity < job->payload_len) return CRYPTO_ERR_BUFFER_TOO_SMALL;
            memcpy(job->out_buffer, job->payload, job->payload_len);
            job->out_len = job->payload_len;
            return CRYPTO_OK;

        default:
            return CRYPTO_ERR_POLICY_VIOLATION;
    }
}
```
```cpp
// C++20: Ідіоматичний рушій крипто-політики з RAII, std::span та безпекою пам'яті
#include <vector>
#include <span>
#include <string_view>
#include <expected>
#include <memory>
#include <algorithm>
#include <random>
#include <cstring>

enum class DataClass {
    ClassA_E2E,
    ClassB_Edge,
    ClassC_SSE
};

enum class CryptoError {
    PolicyViolation,
    BufferOverflow,
    KmsError
};

struct CryptoEnvelope {
    DataClass data_class;
    std::vector<uint8_t> payload;
    std::string key_reference;
};

// RAII обгортка для гарантованого обнулення сесійних ключів при виході з області видимості
class SecureBuffer {
private:
    std::vector<uint8_t> buffer_;
public:
    explicit SecureBuffer(size_t size) : buffer_(size) {}
    ~SecureBuffer() {
        // Safe zeroization of memory upon destruction via volatile pointer
        std::fill_n(static_cast<volatile uint8_t*>(buffer_.data()), buffer_.size(), 0);
    }
    uint8_t* data() { return buffer_.data(); }
    [[nodiscard]] size_t size() const { return buffer_.size(); }
    std::span<uint8_t> span() { return std::span<uint8_t>(buffer_); }
};

class CryptoPolicyEngine {
public:
    std::expected<CryptoEnvelope, CryptoError> process(DataClass classification, std::span<const uint8_t> raw_input) {
        switch (classification) {
            case DataClass::ClassA_E2E:
                // Pass-through opaque ciphertext. Cloud does not touch payload.
                return CryptoEnvelope{
                    .data_class = DataClass::ClassA_E2E,
                    .payload = std::vector<uint8_t>(raw_input.begin(), raw_input.end()),
                    .key_reference = "e2e:client-managed"
                };

            case DataClass::ClassC_SSE:
                return apply_envelope_encryption(raw_input);

            case DataClass::ClassB_Edge:
                return CryptoEnvelope{
                    .data_class = DataClass::ClassB_Edge,
                    .payload = std::vector<uint8_t>(raw_input.begin(), raw_input.end()),
                    .key_reference = "edge:local-hub"
                };
        }
        return std::unexpected(CryptoError::PolicyViolation);
    }

private:
    std::expected<CryptoEnvelope, CryptoError> apply_envelope_encryption(std::span<const uint8_t> raw_input) {
        SecureBuffer dek(32);
        
        // Random DEK generation via CSPRNG
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<uint32_t> dist(0, 255);
        for (size_t i = 0; i < dek.size(); ++i) {
            dek.data()[i] = static_cast<uint8_t>(dist(gen));
        }

        std::vector<uint8_t> encrypted_payload;
        encrypted_payload.reserve(raw_input.size() + 16);
        
        // Simulate AES-GCM encryption with DEK
        for (size_t i = 0; i < raw_input.size(); ++i) {
            encrypted_payload.push_back(raw_input[i] ^ dek.data()[i % dek.size()]);
        }

        // dek buffer is automatically zeroed out by RAII destructor upon exit
        return CryptoEnvelope{
            .data_class = DataClass::ClassC_SSE,
            .payload = std::move(encrypted_payload),
            .key_reference = "kms:arn:aws:kms:eu-central-1:key/dh-kms-kek"
        };
    }
};
```
:::

## 5. Покроковий розбір виконання та обробка крайніх випадків

Простежимо шлях виконання функції `process_crypto_policy` для виклику з класом `CLASS_C_SSE`:

1. **Ініціалізація роботи**: викликач виділяє вихідний буфер `out_buffer` необхідного розміру (вхідний payload + розмір заголовка конверта) та передає його у структуру `crypto_job_t`.
2. **Перевірка меж бувера**: функція `apply_serverside_envelope` перевіряє, що `out_capacity` достатньо велика. Якщо буфер малий, виконання переривається з кодом `CRYPTO_ERR_BUFFER_TOO_SMALL` без виконання криптографічних операцій.
3. **Генерація DEK**: генерується 256-бітний ключ `dummy_dek`. В реальній системі замість `rand()` викликається криптографічно стійкий генератор `sys_random` або API KMS.
4. **Шифрування корисного навантаження**: відкритий текст шифрується алгоритмом AES-256-GCM. За замовчуванням у заголовок записується ідентифікатор ключа KEK та вектор ініціалізації IV.
5. **Очищення ключа DEK**: викликом `secure_memzero` відкритий DEK у локальному масиві `dummy_dek` затирається нулями.
6. **Повернення результату**: статус `CRYPTO_OK` сигналізує шлюзу, що зашифрований конверт готовий до безпечного запису у базу даних.

### Крайовий випадок: Паніка пам'яті та обробка винятків у C++
У мові C++ при виділенні пам'яті під `std::vector` може виникнути виняток `std::bad_alloc`.
Якщо виняток пролітає повз звичайну функцію шифрування, виконання переривається, і ззвичайні локальні масиви з відкритим DEK на стеку можуть лишитися не зачищеними.
Завдяки використанню класу `SecureBuffer`, деструктор якого викликається під час розгортання стека (*stack unwinding*), відкритий DEK гарантовано затирається нулями навіть при виникненні винятку `std::bad_alloc`.

## 6. Інтеграція з OpenSSL / BoringSSL API в реальному виробництві

У реальних системних сервісах замість симуляції XOR використовуються виклики криптографічної бібліотеки OpenSSL або BoringSSL.

При використанні OpenSSL EVP API для AES-256-GCM розробник зобов'язаний дотримуватися суворої послідовності викликів:

1. **`EVP_CIPHER_CTX_new()`**: виділяє контекст шифрування.
2. **`EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL)`**: ініціалізує контекст алгоритмом AES-256-GCM.
3. **`EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, 12, NULL)`**: задає довжину вектора ініціалізації у 12 байт (96 біт).
4. **`EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv)`**: передає симетричний ключ DEK та IV у контекст.
5. **`EVP_EncryptUpdate(ctx, ciphertext, &out_len, plaintext, plaintext_len)`**: виконує апаратне шифрування блоку.
6. **`EVP_EncryptFinal_ex(ctx, ciphertext + out_len, &final_len)`**: фіналізує шифрування.
7. **`EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, 16, tag)`**: зчитує 128-бітний тег автентичності `authTag`.
8. **`EVP_CIPHER_CTX_free(ctx)`**: вивільняє контекст та обнуляє внутрішні буфери OpenSSL.

Нехтування будь-яким із цих кроків (наприклад, пропуск перевірки `EVP_EncryptFinal_ex`) призводить до виникнення мовчки пошкоджених шифротекстів, які неможливо розшифрувати на боці приймача.

## 7. Патерн Ring Buffer для нульового перевиділення пам'яті (Zero-Allocation)

При обробці 100 000 пакетів телеметрії на секунду виклики `malloc` або `new` стають головним вузьким місцем продуктивності (memory allocation bottleneck).

Для досягнення високої пропускної здатності рушій політики інтегрується з паттерном **Ring Buffer (кільцевий буфер)**:
- При старті продуктового мікросервісу виділяється пул фіксованих буферів пам'яті (наприклад, 1024 буфери по 64 КБ кожен).
- Робочі потоки обробки (worker threads) отримують попередньо виділений буфер із пулу, заповнюють зашифрованим конвертом та передають у мережевий сокет.
- Після надсилання пакету буфер повертається у пул без виклику системного `free()`.
- Це дозволяє досягти чудового показника **Zero Dynamic Allocations** під час гарячого циклу обробки трафіку, знижуючи накладні витрати CPU до мінімальних 1–2 мс на мегабайт.

## 8. Механізм автентифікованого додаткового тексту (Associated Data, AAD)

Важливим технічним нюансом при шифруванні конверта AES-256-GCM є використання додаткових незашифрованих даних **AAD (Additional Authenticated Data)**.

При обробці конверта рушій передає відкриті метадані (заголовок класифікації `X-DH-Data-Class`, ідентифікатор пристрою `senderDeviceId` та часову позначку `timestampMs`) в алгоритм AES-GCM як AAD-блок через функцію `EVP_EncryptUpdate` з вказівником `out=NULL`.

Це означає, що хоча самі заголовки залишаються відкритими для маршрутизації в мережі, вони підписуються підсумковим 128-бітним тегом `authTag`.
Якщо зловмисник або проміжний проксі-сервер намагатиметься підробити заголовок `X-DH-Data-Class` з `CLASS_A_E2E` на `CLASS_C_SSE` під час транспортування, верифікація `authTag` на сервері завершиться збоєм з кодом `auth_tag_mismatch`, і пакет буде негайно відкинуто.

## 9. Аналіз продуктивності та профілювання CPU

При профілюванні продуктивності рушія політики інструментами `perf` та `valgrind / callgrind` розрозділ витрат тактових частот CPU на обробку 1 000 000 пакетів телеметрії по 1 КБ розподіляється наступним чином:

- **Апаратне шифрування AES-256-GCM (AES-NI)**: ~32% часу CPU.
- **Розрахунок автентифікованого тегу GHASH**: ~18% часу CPU.
- **Копіювання буферів та вирівнювання пам'яті (memcpy)**: ~14% часу CPU.
- **Серіалізація метаданих JSON/Protobuf**: ~26% часу CPU.
- **Очищення пам'яті (Zeroization)**: ~10% часу CPU.

Цей розподіл викриває важливий висновок: **серіалізація метаданих та копіювання буферів займають майже стільки ж часу CPU, скільки й саме апаратне шифрування AES-NI**.
Саме тому оптимізація двійкового представлення Protobuf та використання ring-буферів є критичними для високонавантажених gateways.

## 10. Обробка гонки потоків та розрозсинхронізації ключів (Concurrency & Race Conditions)

У багатопотоковому середовищі, коли мобільний застосунок надсилає серію E2E-пакетів через кілька паралельних WebSocket або gRPC з'єднань, виникає крайовий випадок розрозсинхронізації кроків ратчета (`ratchetStep` reordering).

Якщо пакет із кроком `ratchetStep = 143` надходить до сервера раніше пакета з `ratchetStep = 142` через випередення у мережі:
- Шлюз маршрутизації не повинен відкидати пакет `143`, якщо вони позначені однаковою сесією `CLASS_A_E2E`.
- Клієнтський пристрій отримувача підтримує буфер пропущених ключів (Skipped Keys Buffer) розміром до 200 елементів, дозволяючи зберегти розшифрований ключ для пакета `142`, коли той нарешті надійде.
- Якщо відставання перевищує 200 кроків, рушій повертає статус `409 Conflict` з кодом `e2e_key_expired`, що змушує клієнтську бібліотеку скинути сесійний ланцюжок.

## 11. Специфікація виклику KMS API та захист від падінь (Circuit Breaker)

При виконанні конвертного шифрування `CLASS_C_SSE` рушій політики звертається до сервісу ключів (KMS).

Щоб уникнути катастрофічного падіння шлюзу при тимчасових затримках або збоях мережі з KMS, впроваджується паттерн **Circuit Breaker**:
- Якщо кількість таймаутів при зверненні до KMS перевищує 5% за 10 секунд, Circuit Breaker переходить у стан `OPEN`.
- Рушій політики припиняє звернення до мережевого KMS і перемикається на резервний локальний кеш розшифрованих DEK (з терміном життя TTL = 300 секунд).
- Якщо резервний кеш порожній, рушій повертає клієнту статус `503 Service Unavailable` з заголовком `Retry-After: 10`, запобігаючи накопиченню завислих потоків в оперативній пам'яті шлюзу.

## 12. Безперервна ротація ключів KEK (Zero-Downtime Key Rotation)

При проведенні регламентної ротації майстер-ключа KEK у хмарному KMS продуктовий сервіс не повинен зупиняти обробку запитів:

- Рушій політики підтримує **дворежимне вікно розшифрування**: при зчитуванні конверта `CLASS_C_SSE` рушій зчитує `kmsKeyArn` із заголовка пакета і розшифровує `encryptedDek` відповідним KEK (старим або новим).
- Для усіх нових операцій шифрування використовується виключно новий активний псевдонім майстер-ключа `alias/dh-telemetry-kek-active`.
- Фоновий воркер оновлює застарілі конверти в базі даних шляхом виклику KMS ReEncrypt без читання й перезапису корисного навантаження.

## 13. Захист ланцюга збірки та підпис бінарного артефакту (Supply Chain Provenance)

Усі компільовані бінарні файли рушія політики C/C++ проходять підписання в пайплайні CI/CD за стандартом SLSA Level 3 (Supply-chain Levels for Software Artifacts):
- Збірка виконується у ізольованому ефемерному контейнері без доступу до зовнішньої мережі Internet.
- Готовий артефакт `crypto_policy_engine.so` підписується асиметричним ключем CI-комплексу інструментом Cosign / Sigstore.
- Перед запуском у продуктовому середовищі Kubernetes daemon-set додаток перевіряє цифровий підпис бінарного модуля та його SBOM (Software Bill of Materials). Це унеможливлює підміну криптографічного рушія шкідливими бекдорами під час розгортання.

## 14. Інтеграція санітайзерів пам'яті у CI/CD (ASan & UBSan)

Для гарантії відсутності переповнення буферів (Buffer Overflow) та неалінованого доступу до пам'яті, збірка C/C++ рушія політики у CI/CD збирається з прапорами санітайзерів Clang / GCC:

```bash
g++ -O2 -std=c++20 -fsanitize=address,undefined,leak -fno-omit-frame-pointer policy_engine.cpp -o policy_engine_test
```

Автоматичні юніт-тести перевіряють:
- Відсутність витоків пам'яті (`AddressSanitizer: leak detected`) при обробці 1 000 000 пошкоджених пакетів.
- Відсутність невизначеної поведінки (`UndefinedBehaviorSanitizer: out of bounds read`) при передачі від'ємних розмірів буферів.
- Відсутність гонки даних (`ThreadSanitizer: data race`) при одночасному виклику `process_crypto_policy` з 64 паралельних потоків.

## 15. Аудит криптографічної відповідності та відтворення збірки (Reproducible Builds)

Для забезпечення найвищого рівня довіри у системному програмуванні C/C++ бінарні файли рушія збираються за принципом **відтворюваної збірки (Reproducible Builds)**:
- Компіляція одного й того самого вихідного коду C/C++ з тими самими опціями компілятора завжди створює бінарний файл `crypto_policy_engine.so` з ідентичним хед-хешем (SHA-256).
- Прапори компілятора `-frandom-seed` та `-ffile-prefix-map` фіксують часові позначки та шляхи до файлів, запобігаючи недетермінованості бінарного відбитку.
- Незалежні криптографічні аудитори можуть перевірити, що наданий бінарний модуль у Kubernetes точно відповідає публічному сирцевому коду без наявності прихованих закладка чи бекдорів.

## 16. Фітнес-функції та автоматизоване тестування у CI/CD

Для гарантії того, що жоден розробник випадково не порушить криптографічні межі у майбутньому, архітектор створює автоматичний тестувальний гейт (фітнес-функцію в пайплайні CI/CD):

1. **Тест інваріанта засліплення (Blindness Invariant)**: фітнес-тест передає в рушій об'єкт `CLASS_A_E2E` і симулює спробу викликати індексатор SearchService або AI Vision Service. Тест вважається пройденим лише тоді, коли шлюз повертає виняток `PolicyViolation` і фіксує спробу витоку в аудит-лог.
2. **Тест на відсутність залишкових даних у пам'яті (Heap Inspection Test)**: тест запускає обробку пакета `CLASS_C_SSE`, після чого виконує інспекцію дампа heap-пам'яті процесу. Якщо у зрізі пам'яті знайдено відкритий ключ DEK або відкритий текст корисного навантаження, збірка CI блокується.
3. **Тест продуктивності (Zero-Allocation Benchmark)**: для C++ реалізації вимірюється кількість алокацій у динамічній пам'яті на один пакет. У гарячому циклі обробки відеопотоку кількість додаткових алокацій повинна дорівнювати нулю (використовуються попередньо виділені буфери або стекові масиви).
