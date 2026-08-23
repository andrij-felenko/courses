# ⚙️ Реалізація суворої межі довіри на шлюзі Digital Homes

У цьому проєктному розборі порівнюється наївна «ретрофітингова» обробка вхідних повідомлень від датчиків і сувора системна реалізація межі довіри на шлюзі Digital Homes Gateway. На прикладі конкретного коду показано, як перевірка криптографічних підписів, валідація інваріантів схеми, обмеження частоти (rate limiting) та ізоляція радіусу ураження реалізуються в коді мовами C та C++.

Наївна реалізація зазвичай припускає, що якщо пакет надійшов через локальний сокет або серійний порт, його полям можна довіряти. Нападник підробляє ідентифікатор датчика, посилає рядки необмеженої довжини або провокує переповнення буфера. Системний підхід розглядає кожен пакет як потенційну векторну атаку й застосовує правило повної медіації на вході.

## 1. Анатомія наївного підходу та його ризики

Розглянемо поширену помилку, яка виникає при спробі швидкої інтеграції периферійного пристрою в розумному будинку. Розробник створює буфер для прийому даних із мережі та розбирає його за допомогою сирих вказівників або стандартних функцій обробки рядків C:

:::tabs
```c
/* c */
// Наївна обробка: довіра до довжини та вмісту пакета з мережі
void process_sensor_packet_naive(uint8_t *raw_buf) {
    char sensor_id[32];
    // НЕБЕЗПЕКА: strcpy/memcpy без перевірки меж та валідації джерела!
    strcpy(sensor_id, (char*)raw_buf); 
    float temp = *(float*)(raw_buf + 32);

    // Пряме виконання команди без авторизації
    execute_device_command(sensor_id, temp); 
}
```
```cpp
/* cpp */
// Наївна обробка C++: небезпечне копіювання рядка та припущення про вирівнювання
void process_sensor_packet_naive(const std::uint8_t* raw_buf) {
    char sensor_id[32];
    // НЕБЕЗПЕКА: std::strcpy без перевірки розмірів буфера
    std::strcpy(sensor_id, reinterpret_cast<const char*>(raw_buf));
    float temp = *reinterpret_cast<const float*>(raw_buf + 32);

    // Пряме виконання команди без перевірки авторизації
    execute_device_command(sensor_id, temp);
}
```
:::

Придивімося до цього фрагмента з позиції зловмисника як сили. Цей код містить одразу чотири катастрофічні вразливості різного рівня:

### А. Переповнення буфера в пам'яті (Buffer Overflow)
Функція `strcpy` копіює байти до першого нульового байта (`\0`). Якщо нападник надсилає 200 байтів без нульового символу, функція перезаписує адреси повернення на стеку. У кращому випадку це призведе до аварійного завершення процесу (Denial of Service), у гіршому — до виконання довільного коду з правами процесу шлюзу (Remote Code Execution, RCE).

### Б. Сліпа довіра до ідентифікатора джерела (Identity Spoofing)
Заголовок пакета містить `sensor_id`, але система не перевіряє, чи дійсно цей пакет надіслано пристроєм із цим ідентифікатором. Будь-який вузол у мережі Zigbee або Wi-Fi може згенерувати пакет з ідентифікатором дверного замка чи головного термостата.

### В. Відсутність валідації діапазонів (Invariant Bypass)
Змінна `temp` зчитується як сирий `float`. Якщо нападник передає значення `NaN` (Not a Number) або `1e38`, це спричиняє невизначену поведінку в алгоритмах регулювання опалення. Причиною є відсутність валідації бізнес-інваріанту на межі довіри.

### Г. Невирівняне зчитування пам'яті (Unaligned Memory Access)
Пряме приведення вказівника `*(float*)(raw_buf + 32)` припускає, що вирівнювання пам'яті за адресою `raw_buf + 32` кратне 4 байтам. На деяких архітектурах ARM це призводить до апаратного винятку `Bus Fault` та негайної зупинки мікроконтролера.

## 2. Принципи побудови захищеної межі (Secure Gateway Boundary)

Для протидії описаним векторам атаки архітектура шлюзу Digital Homes Gateway будується навколо концепції **суворої межі довіри (Strict Trust Boundary)**. Кожне вхідне повідомлення проходить п'ять послідовних бар'єрів перевірки:

1. **Валідація розмірів та вирівнювання (Size & Alignment Check):** Перевірка належності розміру пакета допустимому діапазону `[MinSize, MaxSize]` до початку будь-якого розбору даних.
2. **Безпечне копіювання з обмеженням меж (Bounds-checked Parsing):** Використання явних довжин замість нуль-термінованих рядків.
3. **Захист від атак повтору (Replay Protection):** Перевірка монотонно зростаючого лічильника послідовності (`sequence_num`). Повідомлення із лічильником, меншим або рівним останньому прийнятому, негайно відкидаються.
4. **Криптографічна автентифікація вмісту (HMAC-SHA256):** Перевірка підпису пакета з використанням симетричного сесійного ключа, узгодженого при реєстрації пристрою. Використання порівняння за сталий час (constant-time comparison) для запобігання таймінговим атакам.
5. **Обмеження частоти викликів (Rate Limiting) та Перевірка інваріантів:** Фіксація кількості повідомлень на секунду від одного джерела та перевірка фізичних меж отриманих величин (`MinTemp <= temp <= MaxTemp`).

## 3. Послідовність перевірок та техніка безпечного зчитування

Для уникнення помилок вирівнювання пам'яті та загрози buffer overflow, розбір двійкового буфера виконується за допомогою послідовного копіювання байтів через `memcpy` з явним відстеженням зсуву `offset`:

```
[Початок буфера] 
  │
  ├─ 0..3:   uint32_t id_len            ───► Перевірка id_len <= 32
  ├─ 4..4+N: uint8_t  sensor_id[N]      ───► Явне копіювання N байтів
  ├─ N+4..:  uint64_t sequence_num      ───► Перевірка sequence > last_sequence
  ├─ ...:    float    temperature       ───► Валідація MinTemp <= temp <= MaxTemp
  └─ Кінцівка: uint8_t hmac[32]         ───► Порівняння за сталий час
```

Такий підхід повністю захищає від спроб перевищення меж масиву та гарантує коректне функціонування незалежно від архітектури CPU (x86_64, ARM Cortex-M, RISC-V).

## 4. Реалізація мовами C та C++

Нижче наведено повні реалізації безпечного обробника для C та C++.

:::tabs
```c
/* c */
#include <stdio.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_PAYLOAD_SIZE 256
#define MAX_SENSOR_ID_LEN 32
#define HMAC_LEN 32
#define MAX_ALLOWED_TEMP 85.0f
#define MIN_ALLOWED_TEMP -40.0f
#define MAX_PACKETS_PER_SEC 10

typedef struct {
    uint8_t sensor_id[MAX_SENSOR_ID_LEN];
    uint32_t sensor_id_len;
    uint64_t sequence_num;
    float temperature;
    uint8_t hmac[HMAC_LEN];
} dh_sensor_packet_t;

typedef enum {
    GATEWAY_OK = 0,
    ERR_BUFFER_TOO_SMALL,
    ERR_INVALID_HMAC,
    ERR_REPLAY_ATTACK,
    ERR_OUT_OF_BOUNDS,
    ERR_RATE_LIMITED
} gateway_error_t;

typedef struct {
    uint64_t last_sequence;
    uint32_t packet_count_current_sec;
    uint64_t last_window_sec;
    uint8_t secret_key[32];
} sensor_session_t;

// Безпечне порівняння двох буферів за сталий час для запобігання таймінговим атакам
static bool constant_time_memcmp(const uint8_t *a, const uint8_t *b, size_t len) {
    uint8_t result = 0;
    for (size_t i = 0; i < len; ++i) {
        result |= (a[i] ^ b[i]);
    }
    return result == 0;
}

// Мок криптографічної перевірки HMAC-SHA256
static bool verify_hmac_c(const uint8_t *data, size_t len, const uint8_t *key, const uint8_t *expected_hmac) {
    // В реальній системі тут використовується mbedTLS hmac_sha256
    uint8_t computed_hmac[HMAC_LEN];
    memset(computed_hmac, 0xAB, HMAC_LEN); // Симуляція розрахованого підпису
    (void)data; (void)len; (void)key;
    return constant_time_memcmp(computed_hmac, expected_hmac, HMAC_LEN);
}

gateway_error_t dh_gateway_process_packet(
    const uint8_t *raw_buf, 
    size_t raw_len, 
    sensor_session_t *session,
    uint64_t current_time_sec,
    dh_sensor_packet_t *out_packet
) {
    // 1. Повна медіація: Перевірка мінімального та максимального розміру
    const size_t min_expected = sizeof(uint32_t) + 1 + sizeof(uint64_t) + sizeof(float) + HMAC_LEN;
    if (raw_buf == NULL || session == NULL || out_packet == NULL) {
        return ERR_BUFFER_TOO_SMALL;
    }
    if (raw_len < min_expected || raw_len > MAX_PAYLOAD_SIZE) {
        return ERR_BUFFER_TOO_SMALL;
    }

    // 2. Безпечний розбір ідентифікатора (little-endian безпечне зчитування)
    uint32_t id_len = 0;
    memcpy(&id_len, raw_buf, sizeof(uint32_t));
    if (id_len == 0 || id_len > MAX_SENSOR_ID_LEN) {
        return ERR_BUFFER_TOO_SMALL;
    }
    if ((sizeof(uint32_t) + id_len + sizeof(uint64_t) + sizeof(float) + HMAC_LEN) > raw_len) {
        return ERR_BUFFER_TOO_SMALL;
    }

    out_packet->sensor_id_len = id_len;
    memcpy(out_packet->sensor_id, raw_buf + sizeof(uint32_t), id_len);
    
    size_t offset = sizeof(uint32_t) + id_len;
    memcpy(&out_packet->sequence_num, raw_buf + offset, sizeof(uint64_t));
    offset += sizeof(uint64_t);
    
    memcpy(&out_packet->temperature, raw_buf + offset, sizeof(float));
    offset += sizeof(float);

    memcpy(out_packet->hmac, raw_buf + offset, HMAC_LEN);

    // 3. Захист від повторів (Replay protection)
    if (out_packet->sequence_num <= session->last_sequence) {
        return ERR_REPLAY_ATTACK;
    }

    // 4. Перевірка HMAC підпису за сталий час
    size_t payload_len = sizeof(uint32_t) + id_len + sizeof(uint64_t) + sizeof(float);
    if (!verify_hmac_c(raw_buf, payload_len, session->secret_key, out_packet->hmac)) {
        return ERR_INVALID_HMAC;
    }

    // 5. Rate limiting на рівні шлюзу
    if (current_time_sec == session->last_window_sec) {
        if (session->packet_count_current_sec >= MAX_PACKETS_PER_SEC) {
            return ERR_RATE_LIMITED;
        }
        session->packet_count_current_sec++;
    } else {
        session->last_window_sec = current_time_sec;
        session->packet_count_current_sec = 1;
    }

    // 6. Валідація бізнес-інваріанту фізичних величин
    if (out_packet->temperature < MIN_ALLOWED_TEMP || out_packet->temperature > MAX_ALLOWED_TEMP) {
        return ERR_OUT_OF_BOUNDS;
    }

    // Оновлення стану сесії ТІЛЬКИ після успішного проходження всіх рубежів
    session->last_sequence = out_packet->sequence_num;

    return GATEWAY_OK;
}
```

```cpp
/* cpp */
#include <cstdint>
#include <array>
#include <string_view>
#include <span>
#include <expected>
#include <algorithm>
#include <cstring>

namespace dh::security {

constexpr std::size_t MaxPayloadSize = 256;
constexpr std::size_t MaxSensorIdLen = 32;
constexpr std::size_t HmacLen = 32;
constexpr float MinAllowedTemp = -40.0f;
constexpr float MaxAllowedTemp = 85.0f;
constexpr std::uint32_t MaxPacketsPerSec = 10;

enum class GatewayError {
    BufferTooSmall,
    InvalidHmac,
    ReplayAttack,
    OutOfBounds,
    RateLimited
};

struct SensorPacket {
    std::array<std::uint8_t, MaxSensorIdLen> sensor_id{};
    std::size_t sensor_id_len{0};
    std::uint64_t sequence_num{0};
    float temperature{0.0f};
};

class SensorSession {
public:
    explicit SensorSession(std::span<const std::uint8_t, 32> secret_key) 
        : key_(secret_key) {}

    [[nodiscard]] std::uint64_t last_sequence() const noexcept { return last_sequence_; }
    [[nodiscard]] std::span<const std::uint8_t, 32> key() const noexcept { return key_; }

    void update_sequence(std::uint64_t new_seq) noexcept { last_sequence_ = new_seq; }

    [[nodiscard]] bool check_rate_limit(std::uint64_t current_time_sec) noexcept {
        if (current_time_sec == last_window_sec_) {
            if (packet_count_current_sec_ >= MaxPacketsPerSec) {
                return false;
            }
            packet_count_current_sec_++;
        } else {
            last_window_sec_ = current_time_sec;
            packet_count_current_sec_ = 1;
        }
        return true;
    }

private:
    std::uint64_t last_sequence_{0};
    std::uint32_t packet_count_current_sec_{0};
    std::uint64_t last_window_sec_{0};
    std::span<const std::uint8_t, 32> key_;
};

// Порівняння за сталий час у сучасній C++20 реалізації
[[nodiscard]] inline bool constant_time_compare(
    std::span<const std::uint8_t> a, 
    std::span<const std::uint8_t> b) noexcept 
{
    if (a.size() != b.size()) return false;
    std::uint8_t result = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        result |= (a[i] ^ b[i]);
    }
    return result == 0;
}

[[nodiscard]] inline bool verify_hmac(
    std::span<const std::uint8_t> payload,
    std::span<const std::uint8_t, 32> key,
    std::span<const std::uint8_t, HmacLen> expected_hmac) noexcept 
{
    std::array<std::uint8_t, HmacLen> computed_hmac{};
    computed_hmac.fill(0xAB); // Симуляція обчислення HMAC
    (void)payload; (void)key;
    return constant_time_compare(computed_hmac, expected_hmac);
}

[[nodiscard]] std::expected<SensorPacket, GatewayError> process_sensor_packet(
    std::span<const std::uint8_t> raw_bytes,
    SensorSession& session,
    std::uint64_t current_time_sec) noexcept
{
    // 1. Валідація розмірів через std::span
    constexpr std::size_t min_header_size = sizeof(std::uint32_t) + 1 + sizeof(std::uint64_t) + sizeof(float) + HmacLen;
    if (raw_bytes.size() < min_header_size || raw_bytes.size() > MaxPayloadSize) {
        return std::unexpected(GatewayError::BufferTooSmall);
    }

    std::uint32_t id_len = 0;
    std::memcpy(&id_len, raw_bytes.data(), sizeof(std::uint32_t));
    if (id_len == 0 || id_len > MaxSensorIdLen) {
        return std::unexpected(GatewayError::BufferTooSmall);
    }

    const std::size_t total_expected = sizeof(std::uint32_t) + id_len + sizeof(std::uint64_t) + sizeof(float) + HmacLen;
    if (raw_bytes.size() < total_expected) {
        return std::unexpected(GatewayError::BufferTooSmall);
    }

    SensorPacket pkt;
    pkt.sensor_id_len = id_len;
    std::copy_n(raw_bytes.begin() + sizeof(std::uint32_t), id_len, pkt.sensor_id.begin());

    std::size_t offset = sizeof(std::uint32_t) + id_len;
    std::memcpy(&pkt.sequence_num, raw_bytes.data() + offset, sizeof(std::uint64_t));
    offset += sizeof(std::uint64_t);

    std::memcpy(&pkt.temperature, raw_bytes.data() + offset, sizeof(float));
    offset += sizeof(float);

    auto hmac_span = raw_bytes.subspan(offset, HmacLen);
    std::array<std::uint8_t, HmacLen> expected_hmac_arr{};
    std::copy_n(hmac_span.begin(), HmacLen, expected_hmac_arr.begin());

    // 2. Захист від повторів (Replay Protection)
    if (pkt.sequence_num <= session.last_sequence()) {
        return std::unexpected(GatewayError::ReplayAttack);
    }

    // 3. Криптографічна повна медіація з порівнянням за сталий час
    auto payload_span = raw_bytes.first(offset);
    if (!verify_hmac(payload_span, session.key(), expected_hmac_arr)) {
        return std::unexpected(GatewayError::InvalidHmac);
    }

    // 4. Rate Limiting на рівні шлюзу
    if (!session.check_rate_limit(current_time_sec)) {
        return std::unexpected(GatewayError::RateLimited);
    }

    // 5. Інваріанти домену
    if (pkt.temperature < MinAllowedTemp || pkt.temperature > MaxAllowedTemp) {
        return std::unexpected(GatewayError::OutOfBounds);
    }

    // Атомарне оновлення лічильника сесії
    session.update_sequence(pkt.sequence_num);
    return pkt;
}

} // namespace dh::security
```
:::

## 5. Детальний порівняльний аналіз реалізацій

Проаналізуємо, які саме архітектурні вимоги захищеного дизайну втілено в обох варіантах коду:

### А. Атомарне оновлення стану сесії (State Mutability Isolation)
У найпростіших обробниках лічильник послідовності оновлюється одразу після зчитання. Це створює діру для атак типу state desynchronization: нападник посилає підроблений пакет із високим `sequence_num` та недійсним HMAC. Якщо система оновлює `last_sequence` до перевірки підпису, легітимні пакети від справжнього датчика надалі будуть відкидатися як «повторні», що призводить до відмови в обслуговуванні (DoS). У нашому коді `session.last_sequence` оновлюється **в останній рядок**, лише після того, як усі п'ять рівнів перевірки повернули позитивний результат.

### Б. Запобігання побічним каналам (Timing Side-Channels)
Функція `constant_time_memcmp` (у C) та `constant_time_compare` (у C++) виконує побайтове порівняння всього буфера HMAC незалежно від того, у якому байті виявлено розходження. Звичайна функція `memcmp` повертає результат при першому неспівпадінні байтів. Це дозволяє нападнику виміряти час відповіді сервера з точністю до наносекунд та підібрати підпис байт за байтом за кілька мільйонів запитів. Використання побітового АБО (`result |= a[i] ^ b[i]`) гарантує однаковий час виконання незалежно від вмісту.

### В. Безпека типів та абстракція помилок у C++20
У версії C++20 замість повернення коду помилки через вказівник чи використання винятків застосовано `std::expected<SensorPacket, GatewayError>`. Це рішення має фундаментальне значення для низькоуровневої безпеки:
- Клієнтський код **змушений** явно перевірити наявність значення через `res.has_value()`, перш ніж отримати доступ до даних пакета. Спроба доступу до недійсного результату автоматично підсвічується статичним аналізатором коду.
- Відсутність винятків гарантує відсутність накладних витрат на unwinding стека, що є критичним для嵌入них систем real-time контролерів.
- Використання `std::span` позбавляє код від необхідності передавати пари `uint8_t *ptr, size_t len`, виключаючи ризик розсинхронізації вказівника й довжини.

## 6. Автоматизація моніторингу та тестування на межі

Для перевірки того, що код реалізації межі довіри дійсно витримує тиск супротивника, в інфраструктуру CI/CD додаються три типи автоматичних тестувальних завад:

1. **Фазинг-тести (Fuzzing with AFL++/libFuzzer):** Генератор викликів передає у функцію `dh_gateway_process_packet` мільйони мутованих двійкових масивів для виявлення прихованих виходів за межі масиву або некоректної роботи з покажчиками.
2. **Негативні тести захисту від повторів (Replay attack test suite):** Автоматичні тести перевіряють, що повторна відправка точної копії раніше прийнятого зашифрованого пакета повертає `ERR_REPLAY_ATTACK` та не змінює стан системи.
3. **Аналіз витоків таймінгу (Timing Attack Benchmarks):** Вимірювання розподілу часу виконання функції `verify_hmac` при подачі пакетів із помилкою у першому, середньому та останньому байті підпису. Різниця часу виконання не повинна перевищувати статистичну похибку таймера.

## 7. Обмеження радіусу ураження на рівні системи

Навіть якщо датчик буде фізично вкрадено, а його сесійний ключ підібрано через прямолабораторне розкриття chip decapping, шлюз обмежує радіус ураження:
- Пристрій може посилати дані **тільки** у межах свого зареєстрованого ідентифікатора.
- Зловмисник не може перевищити ліміт 10 пакетів на секунду (`ERR_RATE_LIMITED`), що запобігає заповненню черги обробки шлюзу.
- Значення температури поза межами `[-40, +85]` відкидаються (`ERR_OUT_OF_BOUNDS`), унеможливлюючи вивід з ладу бізнес-логіки термостата.

Таким чином, сувора межа довіри перетворює небезпечний безпосередній доступ до пам'яті на захищений, квантований та повністю контрольований потік даних.
