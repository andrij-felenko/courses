# ⚙️ STRIDE-матриця та перевірка цілісності телеметрії DH

Ця вставка містить практичну реалізацію модуля оцінювання загроз за методологією STRIDE, детальний розрахунок матриці ризиків та вихідний код модуля криптографічної перевірки цілісності телеметрії для домашнього хаба Digital Homes. У матеріалі демонструється процес захисту вхідного потоку повідомлень від підробки вмісту (Tampering), підміни ідентичності джерела (Spoofing) та повторного відтворення кадрів (Replay Attacks).

---

## 1. Практичний виклик безпеки: чому телеметрія потребує криптографічного захисту

У реальних інсталяціях розумних будинків телеметричні дані передаються через різнорідні мережеві середовища: бездротові канали Zigbee, Thread, BLE, локальну сегментовану мережу Ethernet/Wi-Fi та далі через публічний Інтернет до хмарного кластера. Без застосування криптографічного підпису кожного кадру виникає низка критичних ризиків:

1. **Атака повторного відтворення (Replay Attack)**: Зловмисник записує легітимний радіопакет відчинення дверей або зняття з охорони, відправлений мобільним застосунком мешканця. Через кілька днів записаний пакет повторно випускається в ефір. Якщо контролер не перевіряє свіжість часового штампу та монотонію послідовного номера, замок відчиняється повторно.
2. **Модифікація показників (Payload Tampering)**: Зкомпрометований пристрій у локальній мережі або атакуючий за допомогою атаки Man-in-the-Middle (MitM) змінює байти у кадрі телеметрії датчика протікання води (наприклад, замінює біт `leak_detected=true` на `false`). Системні автоматизації не спрацьовують, що призводить до затоплення приміщення.
3. **Підміна джерела (Spoofing)**: Неавторизований вузол надсилає пакети від імені контролера замка. Без перевірки симетричного HMAC-підпису чи асиметричного ECDSA-підпису хаб сприймає хибні повідомлення як автентичні.

Для запобігання цим загрозам у системі Digital Homes впроваджується модуль валідації кадрів телеметрії, який перевіряє цілісність, монотонію та свіжість кожного вхідного пакета.

---

## 2. STRIDE-матриця оцінювання загроз та розрахунок ризиків Digital Homes

Для кожного контейнера C4-архітектури Digital Homes будується вичерпна матриця загроз STRIDE. Оцінка початкового та залишкового ризику розраховується за класичною формулою оцінки кіберризиків:

```
Risk = Likelihood × Impact
```

де **Likelihood (Ймовірність)** оцінюється за шкалою від 1 (вкрай малоймовірно, вимагає фізичного доступу та унікального обладнання) до 5 (майже неминуче, автоматизовані боти в публічному Інтернеті), а **Impact (Вплив)** — від 1 (незначний лог-збій) до 5 (катастрофічні наслідки, загроза фізичній безпеці мешканців, відчинення замків або масовий витік відеопотоків).

| Елемент C4 | Загроза STRIDE | Сценарій атаки | Архітектурний контрзахід | Ймовірність (L) | Вплив (I) | Початковий ризик | Залишковий ризик |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **MQTT Broker** | **S**poofing | Фіктивний хаб підключається з чужим Device ID та зчитує топіки | mTLS з автентифікацією за X.509 сертифікатом у TPM | 5 | 5 | **25** (Критичний) | **5** (Низький) |
| **Telemetry Payload** | **T**ampering | Перехоплення та модифікація показників датчика витоку газу | Підпис HMAC-SHA256 або AEAD (ChaCha20-Poly1305) | 4 | 5 | **20** (Високий) | **4** (Низький) |
| **Audit Logs** | **R**epudiation | Зловмисник відчиняє замок та стирає записи реєстрації хаба | Append-only журнал у хмарі з хеш-ланцюгом (Write-Once) | 3 | 4 | **12** (Середній) | **3** (Низький) |
| **Camera Stream** | **I**nformation Disc. | Несанкціоноване прослуховування RTSP-потоку у локальній мережі | Наскрізне шифрування (E2EE) WebRTC SRTP | 4 | 5 | **20** (Високий) | **5** (Низький) |
| **Hub Gateway** | **D**enial of Service | Флуд подій із скомпрометованої лампочки вичерпує RAM хаба | cgroups v2 + Token Bucket rate-limiter на вході | 5 | 3 | **15** (Високий) | **4** (Низький) |
| **Peripheral Driver**| **E**levation of Priv. | RCE у Zigbee-стеку дає shell з правами `root` | seccomp-bpf фільтр + динамічний unprivileged користувач | 4 | 5 | **20** (Високий) | **4** (Низький) |

### Аналіз рівнів залишкового ризику
Після застосування архітектурних контрзаходів залишковий ризик для кожного елемента падає до прийнятного рівня (значення ≤ 5). Це означає, що успішна атака на систему вимагатиме компрометації апаратного модуля безпеки TPM 2.0 чи фізичного розкриття кремнію, що перевищує бюджет більшості потенційних супротивників.

---

## 3. Деталізація алгоритму валідації кадру телеметрії

Процес валідації кожного вхідного кадру телеметрії на хабі проходить три послідовні фази перевірки.

```
       [ Вхідний кадр телеметрії: DeviceID | Seq | Timestamp | Payload | HMAC ]
                                        │
                                        ▼
       ┌──────────────────────────────────────────────────────────────────┐
       │ Фаза 1: Перевірка свіжості часового штампу                       │
       │ |now_ms - frame.timestamp_ms| <= 5000 ms                         │
       └────────────────────────────────┬─────────────────────────────────┘
                                        │Успіх
                                        ▼
       ┌──────────────────────────────────────────────────────────────────┐
       │ Фаза 2: Захист від Replay (Перевірка монотонії послідовності)    │
       │ frame.sequence_num > device_ctx.last_sequence_num                │
       └────────────────────────────────┬─────────────────────────────────┘
                                        │Успіх
                                        ▼
       ┌──────────────────────────────────────────────────────────────────┐
       │ Фаза 3: Валідація криптографічного підпису HMAC-SHA256            │
       │ constant_time_cmp(frame.signature, compute_hmac(buffer)) == 0    │
       └────────────────────────────────┬─────────────────────────────────┘
                                        │Успіх
                                        ▼
       [ ПАКЕТ ВАЛІДНИЙ: Оновлення last_sequence_num, передача у Twin ]
```

### 3.1. Фаза 1: Перевірка вікна свіжості (Timestamp Tolerance Window)
Першим рубежем захисту є перевірка різниці між поточним системним часом хаба `current_time_ms` та моментом формування кадру на датчику `frame.timestamp_ms`. Допустиме вікно часового зсуву `MAX_ALLOWED_TIME_DRIFT_MS` становить ±5000 мілісекунд (5 секунд).

* **Причина існування вікна**: Мережеві затримки бездротових протоколів Zigbee/Thread, буферизація кадрів на маршрутизаторах та невелика розсинхронізація годинників.
* **Реакція на збій**: Якщо пакет запізнився більше ніж на 5 секунд або прийшов із майбутнього (що свідчить про спробу зловмисника маніпулювати NTP-часом), процес перевірки переривається з кодом `sec_stale_timestamp`.

### 3.2. Фаза 2: Монотонія лічильника послідовностей (Sequence Counter Monotonicity)
Для унеможливлення повторної відправки того самого кадру (Replay Attack) у межах 5-секундного часового вікна, кожен пристрій підтримує монотонічний 64-бітний лічильник `sequence_num`.

* **Правило валідації**: `frame.sequence_num > device_ctx.last_sequence_num`.
* **Крайовий випадок (Wrap-around / Re-keying)**: Якщо лічильник досягає максимального значення $2^{64}-1$, пристрій зобов'язаний виконати повторну автентифікацію (Re-keying Handshake) через mTLS для скидання лічильника та генерації нового сесійного ключа.

### 3.3. Фаза 3: Constant-Time Перевірка криптографічного підпису HMAC-SHA256
Останнім рубежем є обчислення й перевірка 256-бітного підпису HMAC над бінарним вмістом кадру. При порівнянні отриманого цифрового підпису `frame->signature` з очікуваним `expected_hmac` класична функція `memcmp()` є **небезпечною**. 

Ззвичайне порівняння перериває виконання на першому ж неспівпадаючому байті, що дозволяє атакуючому виміряти час відповіді сервера з точністю до наносекунд і побайтово підібрати підпис (Timing Attack). У модулі застосовується порівняння з константним часом (`constant_time_memcmp`), яке гарантовано виконує однакову кількість циклів незалежно від позиції помилкового байта.

---

## 4. Вихідний код модуля валідації цілісності телеметрії (C та C++)

Нижче наведено вихідний код модуля валідації кадрів телеметрії двома мовами програмування.

:::tabs
```c
/* telemetry_validator.c — Повний модуль валідації кадру телеметрії мовою C */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PAYLOAD_LEN 256
#define HMAC_SIZE 32
#define MAX_ALLOWED_TIME_DRIFT_MS 5000

typedef struct {
    uint64_t device_id;
    uint32_t sequence_num;
    uint64_t timestamp_ms;
    uint8_t  payload[MAX_PAYLOAD_LEN];
    size_t   payload_len;
    uint8_t  signature[HMAC_SIZE];
} telemetry_frame_t;

typedef struct {
    uint64_t device_id;
    uint32_t last_sequence_num;
    uint8_t  secret_key[32];
} device_security_ctx_t;

/* Обчислення демонстраційного HMAC підпису над кадром */
static void compute_hmac_sha256(const uint8_t *key, size_t key_len,
                                const uint8_t *data, size_t data_len,
                                uint8_t *out_hmac) {
    /* На практиці тут використовується mbedtls_md_hmac або OpenSSL EVP_MAC */
    for (size_t i = 0; i < HMAC_SIZE; ++i) {
        uint8_t k = key[i % key_len];
        uint8_t d = data[i % data_len];
        out_hmac[i] = (uint8_t)((k ^ d) + (i * 17));
    }
}

/* Перевірка масиву байтів із константним часом виконання */
static bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t diff = 0;
    for (size_t i = 0; i < len; ++i) {
        diff |= (a[i] ^ b[i]);
    }
    return (diff == 0);
}

bool validate_telemetry_frame(device_security_ctx_t *ctx,
                               const telemetry_frame_t *frame,
                               uint64_t current_time_ms) {
    if (!ctx || !frame) {
        fprintf(stderr, "[SECURITY_ERR] Null pointer passed to validator.\n");
        return false;
    }

    if (frame->payload_len > MAX_PAYLOAD_LEN) {
        fprintf(stderr, "[SECURITY_ERR] Payload size %zu exceeds limit %d.\n", 
                frame->payload_len, MAX_PAYLOAD_LEN);
        return false;
    }

    /* 1. Фаза 1: Перевірка свіжості часового штампу (Timestamp Tolerance Window) */
    int64_t time_diff = (int64_t)current_time_ms - (int64_t)frame->timestamp_ms;
    if (time_diff < -MAX_ALLOWED_TIME_DRIFT_MS || time_diff > MAX_ALLOWED_TIME_DRIFT_MS) {
        fprintf(stderr, "[SECURITY_ERR] Stale or future packet. Time diff: %lld ms\n", 
                (long long)time_diff);
        return false;
    }

    /* 2. Фаза 2: Захист від Replay Attacks (Монотонія послідовності) */
    if (frame->sequence_num <= ctx->last_sequence_num) {
        fprintf(stderr, "[SECURITY_ERR] Replay detected! Received seq %u <= Last valid %u\n",
                frame->sequence_num, ctx->last_sequence_num);
        return false;
    }

    /* 3. Фаза 3: Формування серіалізованого буфера та перевірка HMAC */
    uint8_t expected_hmac[HMAC_SIZE];
    uint8_t buffer[sizeof(frame->device_id) + sizeof(frame->sequence_num) +
                   sizeof(frame->timestamp_ms) + MAX_PAYLOAD_LEN];
    
    size_t offset = 0;
    memcpy(buffer + offset, &frame->device_id, sizeof(frame->device_id));
    offset += sizeof(frame->device_id);
    memcpy(buffer + offset, &frame->sequence_num, sizeof(frame->sequence_num));
    offset += sizeof(frame->sequence_num);
    memcpy(buffer + offset, &frame->timestamp_ms, sizeof(frame->timestamp_ms));
    offset += sizeof(frame->timestamp_ms);
    memcpy(buffer + offset, frame->payload, frame->payload_len);
    offset += frame->payload_len;

    compute_hmac_sha256(ctx->secret_key, sizeof(ctx->secret_key), buffer, offset, expected_hmac);

    if (!constant_time_memcmp(frame->signature, expected_hmac, HMAC_SIZE)) {
        fprintf(stderr, "[SECURITY_ERR] HMAC signature mismatch for device_id %llu\n", 
                (unsigned long long)frame->device_id);
        return false;
    }

    /* Успішна валідація: оновлюємо стан монотонійного лічильника */
    ctx->last_sequence_num = frame->sequence_num;
    printf("[SECURITY_OK] Frame seq %u for device %llu validated successfully.\n",
           frame->sequence_num, (unsigned long long)frame->device_id);
    return true;
}
```
```cpp
// telemetry_validator.cpp — Об'єктно-орієнтована реалізація валідатора мовою C++20
#include <iostream>
#include <vector>
#include <array>
#include <span>
#include <expected>
#include <chrono>

namespace dh::security {

enum class ValidationError {
    StaleTimestamp,
    ReplayDetected,
    InvalidSignature,
    PayloadTooLarge,
    NullContext
};

struct TelemetryFrame {
    uint64_t device_id;
    uint32_t sequence_num;
    std::chrono::milliseconds timestamp;
    std::vector<uint8_t> payload;
    std::array<uint8_t, 32> signature;
};

class DeviceSecurityContext {
public:
    explicit DeviceSecurityContext(uint64_t dev_id, std::array<uint8_t, 32> secret_key)
        : device_id_(dev_id), secret_key_(secret_key), last_seq_(0) {}

    [[nodiscard]] std::expected<void, ValidationError> 
    validate_and_update(const TelemetryFrame& frame, std::chrono::milliseconds current_time) noexcept {
        // 1. Фаза 1: Перевірка вікна часового зсуву
        auto diff = std::chrono::abs(current_time - frame.timestamp);
        if (diff > std::chrono::seconds(5)) {
            return std::unexpected(ValidationError::StaleTimestamp);
        }

        // 2. Фаза 2: Монотонія лічильника послідовності
        if (frame.sequence_num <= last_seq_) {
            return std::unexpected(ValidationError::ReplayDetected);
        }

        // 3. Фаза 3: Перевірка HMAC підпису з використанням std::span
        auto expected = compute_hmac(frame);
        if (!constant_time_equals(frame.signature, expected)) {
            return std::unexpected(ValidationError::InvalidSignature);
        }

        // Оновлюємо стан монотонійного лічильника після успіху
        last_seq_ = frame.sequence_num;
        return {};
    }

    [[nodiscard]] uint32_t last_sequence() const noexcept { return last_seq_; }
    [[nodiscard]] uint64_t device_id() const noexcept { return device_id_; }

private:
    uint64_t device_id_;
    std::array<uint8_t, 32> secret_key_;
    uint32_t last_seq_;

    [[nodiscard]] std::array<uint8_t, 32> compute_hmac(const TelemetryFrame& frame) const noexcept {
        std::array<uint8_t, 32> hmac{};
        for (size_t i = 0; i < hmac.size(); ++i) {
            hmac[i] = secret_key_[i] ^ (static_cast<uint8_t>(frame.payload.size() + i));
        }
        return hmac;
    }

    [[nodiscard]] static bool constant_time_equals(std::span<const uint8_t, 32> a,
                                                   std::span<const uint8_t, 32> b) noexcept {
        uint8_t result = 0;
        for (size_t i = 0; i < 32; ++i) {
            result |= (a[i] ^ b[i]);
        }
        return result == 0;
    }
};

} // namespace dh::security
```
:::

---

## 5. Простеження відхилених кадрів через eBPF та лічильники метрик

Для оперативної діагностики атак у продакшені хаб фіксує всі відхилені кадри в системі спостережуваності (Observability). Інструменти eBPF (Extended Berkeley Packet Filter) дозволяють відстежувати точки відмови без збільшення накладних витрат CPU.

Трасування викликів валідатора за допомогою `bpftrace`:

```bash
# Відстеження відхилених кадрів телеметрії через eBPF tracepoint
bpftrace -e 'uprobe:/usr/bin/dh-hub-gateway:validate_telemetry_frame /retval == 0/ { 
    @rejected_frames[comm] = count(); 
    printf("[SECURITY_ALERT] Invalid telemetry frame rejected for PID %d\n", pid); 
}'
```

Метрики Prometheus, що генеруються модулем:
* `dh_telemetry_validation_success_total{device_id="..."}` — лічильник успішно пройшовших валідацію кадрів.
* `dh_telemetry_validation_failed_total{reason="stale_timestamp|replay|invalid_signature"}` — лічильник відхилених кадрів із вказанням конкретної причини зламу.
