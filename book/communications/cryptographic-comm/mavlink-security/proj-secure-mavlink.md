# Реалізація рушія підпису та захищеного тунелю MAVLink 2

Створення надійного криптографічного контуру для безпілотного апарата вимагає не просто виклику бібліотечних функцій, а глибокого розуміння потокової моделі обробки даних, усунення витоків через бічні канали вимірювання часу, захисту від повторного відтворення команд та коректної ізоляції незалежних ліній зв'язку. У цьому проекті розглядається повна інженерна реалізація програмного рушія безпеки для протоколу MAVLink 2: від низькорівневих функцій постійного часу та монотонного обліку часу сесій до конвеєра підписання, валідації кадру, протоколів захищеної ротації ключів, конфігурації захисту пам'яті MPU, інтеграції з диспетчером завдань RTOS, тестування на стійкість до атак та інкапсуляції трафіку в зашифровані тунелі AES-256-GCM.

### Архітектурні виклики та системний дизайн

Розробка криптографічного модуля для бортового комп'ютера або польотного контролера (на базі операційних систем реального часу NuttX або FreeRTOS) стикається з трьома основними інженерними обмеженнями:
1. **Детермінізм часу виконання в реальному часі:** розрахунок та перевірка підпису не повинні створювати непередбачуваних джиттерів у контурі керування кутовою орієнтацією літального апарата, який виконується в перериваннях із частотою від 400 до 1000 Гц.
2. **Абсолютний захист від витоків через час (Timing Attacks):** процедура верифікації криптографічного гешу зобов'язана виконуватися за суворо однаковий час незалежно від того, чи правильний підпис надіслав клієнт, чи зловмисник передав випадкові байти в ефір.
3. **Ізоляція незалежних радіоліній (Multi-Link Isolation):** безпілотник одночасно використовує низькошвидкісний далекобійний радіомодем телеметрії (UART, 57600 бод, темп 10 Гц) та високошвидкісну шину взаємодії з супутнім комп'ютером (Ethernet/UDP, 100 Мбіт/с, темп 200 Гц). Лічильники часу на цих каналах ростуть із різною швидкістю, і змішування їхнього стану призводить до миттєвого блокування радіокоманд.

Програмний комплекс проекту побудовано за багатошаровою модульною схемою:
- **Базовий криптографічний рівень:** функції постійного часу `secure_memcmp()`, процедури гарантованого затирання пам'яті `secure_zeroize()` та обчислення гешу SHA-256.
- **Рівень сесій та автентифікації MAVLink 2:** керування таблицею потоків `(sysid, compid, link_id)`, збирання 13-байтового трейлера та перевірка монотонності таймстемпів.
- **Рівень динамічної ротації ключів:** обробка повідомлень `SETUP_SIGNING` та плавне перемикання криптографічного контексту без втрати зв'язку.
- **Рівень тунельного шифрування:** інкапсуляція пакетів у повідомлення `TUNNEL` (Message ID 385) з використанням алгоритму автентифікованого шифрування AES-256-GCM.
- **Рівень інтеграції з RTOS та апаратним захистом:** потокобезпечні черги обробки кадрів, ізоляція обчислень від переривань, налаштування регіонів захисту пам'яті MPU та керування кеш-пам'яттю при роботі з прямим доступом до пам'яті (DMA).

---

### Рівень 1: Функції постійного часу та безпечне затирання пам'яті

У стандартній бібліотеці мови C функція `memcmp()` здійснює побайтове порівняння двох буферів у пам'яті й зупиняється на першому незбіглому байті. Якщо зловмисник намагається підібрати підпис і вгадав перший байт, функція `memcmp()` виконується на одну ітерацію довше (додаткові 5–10 наносекунд).

Хоча на мікроконтролері ця різниця здається мізерною, сучасні мережеві аналізатори та SDR-приймачі здатні статистично накопичувати заміри затримок відповідей автопілота на тисячі запитів (атака за часом відгуку). В результаті зловмисник отримує можливість побайтово відновити валідний 6-байтовий підпис усього за `6 × 256 = 1536` спроб замість повного перебору `2⁴⁸ ≈ 2.81 × 10¹⁴` варіантів.

Для повного усунення цієї загрози функція `secure_memcmp()` завжди переглядає всі байти буфера від першого до останнього без дострокових виходів, накопичуючи побітову різницю за допомогою оператора `OR`:

:::tabs
```c
#include <stdint.h>
#include <stddef.h>
#include <string.h>

// Порівняння двох масивів пам'яті за строго постійний час
int secure_memcmp(const void *a, const void *b, size_t len) {
    const uint8_t *p1 = (const uint8_t *)a;
    const uint8_t *p2 = (const uint8_t *)b;
    uint8_t result = 0;

    for (size_t i = 0; i < len; ++i) {
        result |= (p1[i] ^ p2[i]);
    }

    return (result == 0) ? 0 : -1;
}

// Гарантоване затирання конфіденційних даних у пам'яті (захист від оптимізації компілятора)
void secure_zeroize(void *ptr, size_t len) {
    volatile uint8_t *p = (volatile uint8_t *)ptr;
    while (len--) {
        *p++ = 0;
    }
}
```
```cpp
#include <cstdint>
#include <cstddef>
#include <span>
#include <algorithm>

namespace mavlink_sec {

// Порівняння спанів пам'яті за строго постійний час у C++
[[nodiscard]] int secureMemcmp(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return -1;
    }

    uint8_t result = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        result |= (a[i] ^ b[i]);
    }

    return (result == 0) ? 0 : -1;
}

// Гарантоване очищення пам'яті з використанням volatile-вказівника
void secureZeroize(std::span<uint8_t> buffer) noexcept {
    volatile uint8_t* p = const_cast<volatile uint8_t*>(buffer.data());
    for (size_t i = 0; i < buffer.size(); ++i) {
        p[i] = 0;
    }
}

} // namespace mavlink_sec
```
:::

Зверніть увагу на функцію `secure_zeroize()`: стандартний виклик `memset(buffer, 0, size)` наприкінці функції компілятор GCC/Clang часто оптимізує та повністю видаляє (Dead Store Elimination), оскільки буфер більше не використовується до виходу зі стекового кадру. Використання кваліфікатора `volatile` змушує компілятор генерувати реальні інструкції запису нулів у пам'ять, що унеможливлює вилучення залишкових секретних ключів через аналіз дампів пам'яті після аварійних перезавантажень (HardFault).

---

### Рівень 2: Таблиця сесій та відстеження монотонного часу

Приймач повідомлень зобов'язаний підтримувати внутрішню таблицю стану вхідних потоків. Ключем пошуку є складений ідентифікатор із трьох полів:
- `sysid`: номер відправника в мережі (наземна станція має SysID 255);
- `compid`: номер конкретного компонента відправника (пункт керування зазвичай має CompID 190);
- `link_id`: номер фізичного інтерфейсу, через який надійшов пакет (радіолінія UART1, резервний модем UART2 або прямий UDP сокет).

Принцип функціонування таблиці полягає в тому, що для кожного зареєстрованого триплету зберігається останнє перевірене значення 48-бітного таймстемпу `last_timestamp`. Коли надходить новий пакет, його часова мітка `incoming_timestamp` порівнюється зі збереженою. Якщо нове число менше або дорівнює збереженому, пакет є або застарілим, або записаною зловмисником копією старої команди (Replay Attack) і негайно відхиляється.

:::tabs
```c
#include <stdbool.h>

#define MAX_SIGNING_STREAMS 16

typedef struct {
    uint8_t  sysid;
    uint8_t  compid;
    uint8_t  link_id;
    bool     active;
    uint64_t last_timestamp;
} signing_stream_entry_t;

typedef struct {
    signing_stream_entry_t entries[MAX_SIGNING_STREAMS];
} stream_table_t;

void stream_table_init(stream_table_t *table) {
    memset(table, 0, sizeof(stream_table_t));
}

// Пошук або виділення слота для вхідного потоку
signing_stream_entry_t* stream_table_get(stream_table_t *table, uint8_t sysid, uint8_t compid, uint8_t link_id) {
    // 1. Пошук існуючого активного потоку
    for (size_t i = 0; i < MAX_SIGNING_STREAMS; ++i) {
        if (table->entries[i].active &&
            table->entries[i].sysid == sysid &&
            table->entries[i].compid == compid &&
            table->entries[i].link_id == link_id) {
            return &table->entries[i];
        }
    }

    // 2. Виділення першого вільного слота для нового відправника
    for (size_t i = 0; i < MAX_SIGNING_STREAMS; ++i) {
        if (!table->entries[i].active) {
            table->entries[i].sysid = sysid;
            table->entries[i].compid = compid;
            table->entries[i].link_id = link_id;
            table->entries[i].active = true;
            table->entries[i].last_timestamp = 0;
            return &table->entries[i];
        }
    }

    return NULL; // Таблиця заповнена (захист від вичерпання пам'яті)
}
```
```cpp
#include <cstdint>
#include <array>
#include <optional>

namespace mavlink_sec {

struct StreamKey {
    uint8_t sysid{0};
    uint8_t compid{0};
    uint8_t link_id{0};

    constexpr bool operator==(const StreamKey&) const noexcept = default;
};

struct StreamEntry {
    StreamKey key{};
    bool      active{false};
    uint64_t  last_timestamp{0};
};

class StreamTable {
public:
    static constexpr size_t kMaxStreams = 16;

    StreamEntry* getOrCreate(const StreamKey& key) noexcept {
        for (auto& entry : entries_) {
            if (entry.active && entry.key == key) {
                return &entry;
            }
        }
        for (auto& entry : entries_) {
            if (!entry.active) {
                entry.key = key;
                entry.active = true;
                entry.last_timestamp = 0;
                return &entry;
            }
        }
        return nullptr;
    }

    void reset() noexcept {
        entries_.fill(StreamEntry{});
    }

private:
    std::array<StreamEntry, kMaxStreams> entries_{};
};

} // namespace mavlink_sec
```
:::

У цій реалізації передбачено фіксовану кількість слотів (16 записів), що виключає динамічне виділення пам'яті через купу (`malloc` / `new`) під час обробки пакетів у перериваннях UART або RTOS-задачах зв'язку.

---

### Рівень 3: Конвеєр формування та підписання вихідного кадру MAVLink 2

Процедура створення підписаного пакета вимагає суворого дотримання послідовності операцій над бінарним буфером:

1. **Встановлення біта підпису:** у третьому байті кадру (поле `incompat_flags`) виставляється прапорець `MAVLINK_IFLAG_SIGNED = 0x01`. Цей біт повідомляє приймачу, що розмір кадру збільшено на 13 байтів трейлера.
2. **Монотонне оновлення часу:** локальний лічильник часу передавача інкрементується щонайменше на 1 квант (10 мкс), гарантуючи, що жодні два вихідні пакети не матимуть однакового таймстемпу.
3. **Розрахунок CRC-16 кадру:** контрольна сума пакета обчислюється над байтами заголовка (від поля `LEN` до кінця `MSG_ID`) та корисного навантаження, після чого акумулюється байт сумісності схеми `CRC_EXTRA`. Отримане 16-бітне число записується у форматі Little-Endian за зсувом `10 + payload_len`.
4. **Запис полів трейлера:** за зсувом `12 + payload_len` записується 1 байт `link_id` та 6 байтів поточного монотонного часу (48 молодших бітів `timestamp`).
5. **Розрахунок SHA-256:** формується вхідний блок даних загальною довжиною `51 + payload_len` байтів, що містить: `[32 байти спільного ключа] + [10 байтів заголовка] + [payload_len байтів даних] + [2 байти CRC-16] + [1 байт link_id] + [6 байтів timestamp]`.
6. **Обтинання та фіксація:** обчислюється 32-байтовий дайджест SHA-256, з якого беруться перші 6 байтів і записуються в байти `7 .. 12` трейлера підпису.

:::tabs
```c
#include <mavlink.h>

// Зовнішня функція розрахунку SHA-256
void sha256_compute(const uint8_t *data, size_t len, uint8_t *digest);

uint16_t sign_mavlink_packet(
    uint8_t *frame_buffer,
    size_t payload_len,
    uint8_t link_id,
    uint64_t *inout_timestamp,
    const uint8_t *secret_key,
    uint8_t crc_extra
) {
    // 1. Забезпечуємо строгу монотонність таймстемпу
    (*inout_timestamp)++;
    uint64_current_ts = *inout_timestamp;

    // 2. Встановлюємо прапорець підпису у полі incompat_flags (байт 2)
    frame_buffer[2] |= MAVLINK_IFLAG_SIGNED;

    // 3. Обчислюємо та записуємо 16-бітну контрольну суму кадру
    uint16_t crc = crc_calculate(&frame_buffer[1], 9 + payload_len);
    crc_accumulate(crc_extra, &crc);
    frame_buffer[10 + payload_len]     = (uint8_t)(crc & 0xFF);
    frame_buffer[10 + payload_len + 1] = (uint8_t)((crc >> 8) & 0xFF);

    // 4. Формуємо блок Link ID та 48-бітного Timestamp у трейлері
    size_t trailer_offset = 12 + payload_len;
    frame_buffer[trailer_offset] = link_id;
    for (int i = 0; i < 6; ++i) {
        frame_buffer[trailer_offset + 1 + i] = (uint8_t)((current_ts >> (8 * i)) & 0xFF);
    }

    // 5. Збираємо лінійний буфер для SHA-256 (розмір = 51 + payload_len)
    uint8_t hash_input[300];
    memcpy(hash_input, secret_key, 32);
    memcpy(hash_input + 32, frame_buffer, 10 + payload_len + 2 + 1 + 6);

    uint8_t digest[32];
    sha256_compute(hash_input, 51 + payload_len, digest);

    // 6. Записуємо перші 6 байтів обрізаного хешу
    memcpy(&frame_buffer[trailer_offset + 7], digest, 6);

    // Очищаємо конфіденційні буфери
    secure_zeroize(hash_input, sizeof(hash_input));
    secure_zeroize(digest, sizeof(digest));

    // Повна фізична довжина підписаного кадру
    return (uint16_t)(10 + payload_len + 2 + 13);
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <cstring>

namespace mavlink_sec {

void sha256Compute(std::span<const uint8_t> input, std::span<uint8_t, 32> output) noexcept;
uint16_t calculateCrc(std::span<const uint8_t> data, uint8_t crc_extra) noexcept;

class PacketSigner {
public:
    explicit PacketSigner(std::span<const uint8_t, 32> secret_key, uint8_t link_id = 0)
        : link_id_(link_id) {
        std::copy(secret_key.begin(), secret_key.end(), secret_key_.begin());
    }

    ~PacketSigner() {
        secureZeroize(secret_key_);
    }

    [[nodiscard]] std::vector<uint8_t> signPacket(
        std::span<const uint8_t> header_and_payload,
        uint8_t crc_extra
    ) {
        const size_t payload_len = header_and_payload.size() - 10;
        std::vector<uint8_t> packet(header_and_payload.size() + 2 + 13);

        // Копіюємо заголовок та корисні дані
        std::copy(header_and_payload.begin(), header_and_payload.end(), packet.begin());

        // Встановлюємо прапорець підпису MAVLINK_IFLAG_SIGNED
        packet[2] |= 0x01;
        timestamp_++;

        // Розрахунок CRC-16
        const uint16_t crc = calculateCrc(std::span{packet.data() + 1, 9 + payload_len}, crc_extra);
        packet[10 + payload_len]     = static_cast<uint8_t>(crc & 0xFF);
        packet[10 + payload_len + 1] = static_cast<uint8_t>((crc >> 8) & 0xFF);

        // Трейлер підпису: Link ID + 48-бітний Timestamp
        const size_t trailer_pos = 12 + payload_len;
        packet[trailer_pos] = link_id_;
        for (size_t i = 0; i < 6; ++i) {
            packet[trailer_pos + 1 + i] = static_cast<uint8_t>((timestamp_ >> (8 * i)) & 0xFF);
        }

        // Вхідний масив для SHA-256
        std::vector<uint8_t> hash_input(51 + payload_len);
        std::copy(secret_key_.begin(), secret_key_.end(), hash_input.begin());
        std::copy(packet.begin(), packet.begin() + 10 + payload_len + 2 + 7, hash_input.begin() + 32);

        std::array<uint8_t, 32> digest{};
        sha256Compute(hash_input, digest);

        // Копіюємо перші 6 байтів дайджесту
        std::copy(digest.begin(), digest.begin() + 6, packet.begin() + trailer_pos + 7);

        secureZeroize(hash_input);
        secureZeroize(digest);

        return packet;
    }

private:
    std::array<uint8_t, 32> secret_key_{};
    uint8_t                 link_id_{0};
    uint64_t                timestamp_{1000000ULL};
};

} // namespace mavlink_sec
```
:::

---

### Рівень 4: Конвеєр верифікації та фільтрація вхідного трафіку

Конвеєр обробки вхідних байтів спроєктовано за принципом каскадної фільтрації, де найменш ресурсомісткі перевірки виконуються першими:

1. **Фільтрація за CRC-16:** якщо пакет спотворено завадами в ефірі, він відкидається на першому кроці, що запобігає марнуванню процесорного часу на розрахунок SHA-256.
2. **Обробка непідписаних пакетів:** якщо кадр не має прапорця `MAVLINK_IFLAG_SIGNED`, викликається функція предикату `accept_unsigned_cb`. Пакет дозволяється лише для відкритих типів повідомлень (наприклад, `HEARTBEAT` або `ATTITUDE`), а будь-які непідписані команди керування негайно блокуються.
3. **Фільтрація Replay-атак:** виконується перевірка `incoming_ts > stream->last_timestamp`. Застарілі пакети відхиляються без виконання криптографічних операцій.
4. **Звірка SHA-256 за сталий час:** обчислюється підпис для вхідних даних і порівнюється з полем `signature` через `secure_memcmp()`. Тільки після повного збігу оновлюється час у таблиці сесій.

:::tabs
```c
typedef enum {
    VERIFY_SUCCESS = 0,
    VERIFY_ERR_BAD_CRC,
    VERIFY_ERR_UNSIGNED_REJECTED,
    VERIFY_ERR_REPLAY_ATTACK,
    VERIFY_ERR_BAD_SIGNATURE,
    VERIFY_ERR_STREAM_OVERFLOW
} verify_result_t;

verify_result_t verify_mavlink_packet(
    const uint8_t *frame,
    size_t frame_len,
    stream_table_t *streams,
    const uint8_t *secret_key,
    uint8_t crc_extra,
    bool (*accept_unsigned_cb)(uint32_t msgid)
) {
    if (frame_len < 12) return VERIFY_ERR_BAD_CRC;

    uint8_t payload_len = frame[1];
    uint8_t incompat_flags = frame[2];
    uint8_t sysid = frame[5];
    uint8_t compid = frame[6];
    uint32_t msgid = frame[7] | ((uint32_t)frame[8] << 8) | ((uint32_t)frame[9] << 16);

    // 1. Перевірка контрольної суми CRC-16
    uint16_t expected_crc = frame[10 + payload_len] | ((uint16_t)frame[10 + payload_len + 1] << 8);
    uint16_t calc_crc = crc_calculate(&frame[1], 9 + payload_len);
    crc_accumulate(crc_extra, &calc_crc);
    if (calc_crc != expected_crc) return VERIFY_ERR_BAD_CRC;

    // 2. Обробка пакетів без криптографічного підпису
    if (!(incompat_flags & MAVLINK_IFLAG_SIGNED)) {
        if (accept_unsigned_cb && accept_unsigned_cb(msgid)) {
            return VERIFY_SUCCESS;
        }
        return VERIFY_ERR_UNSIGNED_REJECTED;
    }

    if (frame_len < (size_t)(10 + payload_len + 2 + 13)) return VERIFY_ERR_BAD_SIGNATURE;

    size_t trailer_offset = 12 + payload_len;
    uint8_t link_id = frame[trailer_offset];

    uint64_t incoming_ts = 0;
    for (int i = 0; i < 6; ++i) {
        incoming_ts |= ((uint64_t)frame[trailer_offset + 1 + i]) << (8 * i);
    }

    // 3. Пошук потоку та перевірка на Replay-атаку
    signing_stream_entry_t *stream = stream_table_get(streams, sysid, compid, link_id);
    if (!stream) return VERIFY_ERR_STREAM_OVERFLOW;

    if (stream->last_timestamp != 0 && incoming_ts <= stream->last_timestamp) {
        return VERIFY_ERR_REPLAY_ATTACK;
    }

    // 4. Розрахунок та побайтова звірка SHA-256
    uint8_t hash_input[300];
    memcpy(hash_input, secret_key, 32);
    memcpy(hash_input + 32, frame, 10 + payload_len + 2 + 7);

    uint8_t digest[32];
    sha256_compute(hash_input, 51 + payload_len, digest);

    int cmp = secure_memcmp(&frame[trailer_offset + 7], digest, 6);
    secure_zeroize(hash_input, sizeof(hash_input));
    secure_zeroize(digest, sizeof(digest));

    if (cmp != 0) return VERIFY_ERR_BAD_SIGNATURE;

    // 5. Оновлюємо стан успішного потоку
    stream->last_timestamp = incoming_ts;
    return VERIFY_SUCCESS;
}
```
```cpp
#include <expected>
#include <span>
#include <functional>

namespace mavlink_sec {

enum class VerifyError {
    BadCrc,
    UnsignedRejected,
    ReplayDetected,
    BadSignature,
    StreamOverflow
};

class PacketVerifier {
public:
    using AcceptUnsignedPredicate = std::function<bool(uint32_t msgid)>;

    explicit PacketVerifier(std::span<const uint8_t, 32> secret_key, AcceptUnsignedPredicate unsigned_filter = nullptr)
        : unsigned_filter_(std::move(unsigned_filter)) {
        std::copy(secret_key.begin(), secret_key.end(), secret_key_.begin());
    }

    ~PacketVerifier() {
        secureZeroize(secret_key_);
    }

    [[nodiscard]] std::expected<void, VerifyError> verifyPacket(
        std::span<const uint8_t> frame,
        uint8_t crc_extra
    ) {
        if (frame.size() < 12) return std::unexpected(VerifyError::BadCrc);

        const uint8_t payload_len = frame[1];
        const uint8_t incompat_flags = frame[2];
        const uint8_t sysid = frame[5];
        const uint8_t compid = frame[6];
        const uint32_t msgid = frame[7] | (uint32_t(frame[8]) << 8) | (uint32_t(frame[9]) << 16);

        // 1. CRC
        const uint16_t expected_crc = frame[10 + payload_len] | (uint16_t(frame[11 + payload_len]) << 8);
        const uint16_t calc_crc = calculateCrc(frame.subspan(1, 9 + payload_len), crc_extra);
        if (calc_crc != expected_crc) return std::unexpected(VerifyError::BadCrc);

        // 2. Непідписані повідомлення
        if (!(incompat_flags & 0x01)) {
            if (unsigned_filter_ && unsigned_filter_(msgid)) {
                return {};
            }
            return std::unexpected(VerifyError::UnsignedRejected);
        }

        if (frame.size() < 10 + payload_len + 2 + 13) {
            return std::unexpected(VerifyError::BadSignature);
        }

        const size_t trailer_offset = 12 + payload_len;
        const uint8_t link_id = frame[trailer_offset];

        uint64_t incoming_ts = 0;
        for (size_t i = 0; i < 6; ++i) {
            incoming_ts |= (uint64_t(frame[trailer_offset + 1 + i]) << (8 * i));
        }

        // 3. Перевірка Replay
        auto* stream = streams_.getOrCreate({sysid, compid, link_id});
        if (!stream) return std::unexpected(VerifyError::StreamOverflow);

        if (stream->last_timestamp != 0 && incoming_ts <= stream->last_timestamp) {
            return std::unexpected(VerifyError::ReplayDetected);
        }

        // 4. Обчислення SHA-256
        std::vector<uint8_t> hash_input(51 + payload_len);
        std::copy(secret_key_.begin(), secret_key_.end(), hash_input.begin());
        std::copy(frame.begin(), frame.begin() + 10 + payload_len + 2 + 7, hash_input.begin() + 32);

        std::array<uint8_t, 32> digest{};
        sha256Compute(hash_input, digest);

        const int match = secureMemcmp(frame.subspan(trailer_offset + 7, 6), std::span{digest.data(), 6});
        secureZeroize(hash_input);
        secureZeroize(digest);

        if (match != 0) return std::unexpected(VerifyError::BadSignature);

        stream->last_timestamp = incoming_ts;
        return {};
    }

private:
    std::array<uint8_t, 32> secret_key_{};
    AcceptUnsignedPredicate unsigned_filter_{};
    StreamTable             streams_{};
};

} // namespace mavlink_sec
```
:::

---

### Рівень 5: Тунелювання та автентифіковане шифрування AES-256-GCM

Коли лінія зв'язку вимагає повної конфіденційності телеметрії (приховування точних координат дрона та точок місії від ворожих комплексів радіорозвідки), корисне навантаження шифрується алгоритмом AES-256-GCM та передається через системне повідомлення `MAVLINK_MSG_ID_TUNNEL` (ID 385).

Режим лічильника Галуа (AES-GCM) забезпечує дві властивості одночасно:
- **Конфіденційність:** відкритий текст пакета шифрується симетричним 256-бітним ключем із 96-бітним вектором ініціалізації (IV / Nonce).
- **Автентичність шифротексту:** генерується 128-бітний (16 байтів) криптографічний тег автентичності (Auth Tag), який гарантує, що зловмисник не зміг модифікувати жоден біт шифротексту в ефірі.

:::tabs
```c
// Виклик функції шифрування AES-GCM (на базі апаратного блоку або криптобібліотеки)
int aes_gcm_encrypt(
    const uint8_t *key,
    const uint8_t *iv, size_t iv_len,
    const uint8_t *aad, size_t aad_len,
    const uint8_t *input, size_t input_len,
    uint8_t *output,
    uint8_t *tag, size_t tag_len
);

uint16_t pack_encrypted_mavlink_tunnel(
    uint8_t *out_frame,
    uint8_t target_sys,
    uint8_t target_comp,
    const uint8_t *plain_mavlink_msg,
    size_t msg_len,
    const uint8_t *aes_key,
    uint64_t *inout_nonce_counter
) {
    if (msg_len > 100) return 0; // Максимальна місткість буфера TUNNEL payload (128 - 12 - 16 = 100 байт)

    mavlink_tunnel_t tunnel = {0};
    tunnel.payload_type = 100; // Користувацький тип: AES-256-GCM Encapsulation
    tunnel.target_system = target_sys;
    tunnel.target_component = target_comp;

    // 1. Формуємо 12-байтовий Nonce з монотонного лічильника
    (*inout_nonce_counter)++;
    uint8_t iv[12] = {0};
    memcpy(iv, inout_nonce_counter, sizeof(uint64_t));
    memcpy(tunnel.payload, iv, 12);

    // 2. Шифруємо дані та отримуємо 16-байтовий тег автентичності
    uint8_t tag[16];
    aes_gcm_encrypt(
        aes_key,
        iv, 12,
        NULL, 0,
        plain_mavlink_msg, msg_len,
        &tunnel.payload[12],
        tag, 16
    );

    memcpy(&tunnel.payload[12 + msg_len], tag, 16);
    tunnel.payload_length = (uint8_t)(12 + msg_len + 16);

    // 3. Кодуємо у стандартне повідомлення TUNNEL
    mavlink_message_t msg;
    mavlink_msg_tunnel_encode(255, 190, &msg, &tunnel);
    return mavlink_msg_to_send_buffer(out_frame, &msg);
}
```
```cpp
#include <cstdint>
#include <array>
#include <span>
#include <vector>
#include <stdexcept>
#include <cstring>

namespace mavlink_sec {

void aesGcmEncrypt(
    std::span<const uint8_t, 32> key,
    std::span<const uint8_t, 12> iv,
    std::span<const uint8_t> plaintext,
    std::span<uint8_t> ciphertext,
    std::span<uint8_t, 16> tag
);

class TunnelEncryptor {
public:
    explicit TunnelEncryptor(std::span<const uint8_t, 32> aes_key) {
        std::copy(aes_key.begin(), aes_key.end(), aes_key_.begin());
    }

    ~TunnelEncryptor() {
        secureZeroize(aes_key_);
    }

    [[nodiscard]] MavlinkTunnel encryptFrame(
        uint8_t target_sys,
        uint8_t target_comp,
        std::span<const uint8_t> plain_packet
    ) {
        if (plain_packet.size() > 100) {
            throw std::length_error("Payload exceeds maximum TUNNEL buffer capacity (100 bytes)");
        }

        MavlinkTunnel tunnel{};
        tunnel.payload_type = 100; // Custom AES-GCM
        tunnel.target_system = target_sys;
        tunnel.target_component = target_comp;

        // Генерація унікального Nonce
        nonce_counter_++;
        std::array<uint8_t, 12> iv{};
        std::memcpy(iv.data(), &nonce_counter_, sizeof(nonce_counter_));
        std::copy(iv.begin(), iv.end(), tunnel.payload.begin());

        // Шифрування
        std::array<uint8_t, 16> tag{};
        aesGcmEncrypt(
            aes_key_,
            iv,
            plain_packet,
            std::span{tunnel.payload.data() + 12, plain_packet.size()},
            tag
        );

        std::copy(tag.begin(), tag.end(), tunnel.payload.begin() + 12 + plain_packet.size());
        tunnel.payload_length = static_cast<uint8_t>(12 + plain_packet.size() + 16);

        return tunnel;
    }

private:
    std::array<uint8_t, 32> aes_key_{};
    uint64_t                nonce_counter_{0};
};

} // namespace mavlink_sec
```
:::

---

### Наскрізний покроковий трейс обробки кадру

Розглянемо практичний числовий приклад обробки підписаного кадру в бінарному вигляді:

1. **Формування повідомлення:** наземна станція (`sysid = 255`, `compid = 190`) створює команду `COMMAND_LONG` із наказом озброїти мотори (`MAV_CMD_COMPONENT_ARM_DISARM`, `param1 = 1.0f`).
2. **Застосування Zero-Trimming:** початковий розмір структури `mavlink_command_long_t` становить 33 байти (7 полів `float` по 4 байти + команда 2 байти + цільові адреси 3 байти). Оскільки поля `param2..param7` містять нулі `0.0f`, передавач відтинає 24 кінцеві нульові байти. Довжина корисного навантаження стає `LEN = 9` байтів.
3. **Розрахунок CRC:** обчислюється CRC-16 над заголовком і 9 байтами даних із врахуванням `CRC_EXTRA = 152`. Нехай отримане значення становить `0x3A5B`.
4. **Трейлер підпису:** поточний монотонний час станції становить `Timestamp = 150 000 000` (1500 секунд від епохи 2015 року), `link_id = 0`.
5. **Вхідні дані SHA-256:** формується буфер розміром `51 + 9 = 60` байтів:
   - байти `0..31`: 32 байти секретного ключа;
   - байти `32..41`: 10 байтів заголовка MAVLink 2 (байт 2 має `incompat_flags = 0x01`);
   - байти `42..50`: 9 байтів корисного навантаження команди;
   - байти `51..52`: 2 байти CRC-16 (`0x5B`, `0x3A`);
   - байт `53`: `link_id = 0x00`;
   - байти `54..59`: 6 байтів таймстемпу `150 000 000` у форматі Little-Endian (`0x80, 0x8D, 0x5B, 0x08, 0x00, 0x00`).
6. **Генерація та обтинання:** обчислюється дайджест SHA-256. Перші 6 байтів записуються в кінець пакета. Загальний розмір вихідного кадру становить `10 + 9 + 2 + 13 = 34` байти.

Прийом на автопілоті здійснюється у зворотному порядку:
- Перевіряється `STX == 0xFD` та розмір `34` байти.
- Перевіряється контрольна сума `CRC-16 == 0x3A5B`.
- Витягується потік `(sysid = 255, compid = 190, link_id = 0)`. Попередній час у таблиці був `149 980 000`. Оскільки `150 000 000 > 149 980 000`, перевірка replay-атаки успішна.
- Збирається вхідний буфер із локально збереженого 32-байтового ключа та отриманих 28 байтів пакета, обчислюється SHA-256 і звіряється 6 байтів підпису за допомогою `secure_memcmp()`.
- Час у таблиці оновлюється до `150 000 000`, наказ передається польотному диспетчеру, і дрони запускають двигуни.

---

### Тестування стійкості, фазинг та аварійні сценарії

Для підтвердження надійності розробленого рушія розробники впроваджують автоматизовані набори модульних тестів (Unit Tests) та фазинг-тести (Fuzzing Harness), що імітують екстремальні умови радіоефіру:

1. **Тест на відбиття Replay-атаки:** генератор тестових послідовностей надсилає валідний підписаний пакет із таймстемпом `T = 1000`, фіксує успішне прийняття, а потім повторно надсилає той самий байтовий масив. Рушій зобов'язаний повернути помилку `VERIFY_ERR_REPLAY_ATTACK`, а лічильник виконаних команд автопілота має залишитися незмінним.
2. **Тест на спотворення підпису:** модифікація будь-якого одного біта в полі `signature` (64 тестові комбінації на байт) повинна повертати статус `VERIFY_ERR_BAD_SIGNATURE` без виклику обробника корисних даних.
3. **Тест на зміну поля довжини (Zero-Trimming Inconsistency):** якщо зловмисник додає нульовий байт наприкінці корисних даних і збільшує поле `LEN` на 1, перевірка підпису зобов'язана провалитися, оскільки зміна поля `LEN` змінює вхідний блок SHA-256.
4. **Тест на переповнення таблиці потоків:** надсилання підписаних пакетів від 17 різних відправників із різними комбінаціями `(sysid, compid)` повинно коректно відпрацьовувати політику блокування або витіснення застарілих слотів без порушення пам'яті (Buffer Overflow).
5. **Тест на захищену ротацію ключів:** імітація надсилання повідомлення `SETUP_SIGNING`, завіреного поточним ключем. Автопілот повинен атомарно оновити секрет у пам'яті, скинути лічильники потоків і плавно продовжити прийом команд, завірених новим ключем, без перезапуску польотного стека.

---

### Інтеграція з RTOS, MPU, маршрутизаторами та пам'яттю FRAM

У польотних контролерах на базі ядра ARM Cortex-M7 (чипи STM32F7 / STM32H7) процесор має окремий кеш даних першого рівня (D-Cache), а приймання байтів UART виконується через кільцевий буфер контролера прямого доступу до пам'яті (DMA).

Це створює дві потенційні пастки:
1. **Когерентність кешу:** перед перевіркою підпису в буфері, заповненому DMA, процесор зобов'язаний виконати операцію інвалідації рядків кешу (`SCB_InvalidateDCache_by_Addr`), інакше ядро прочитає старі дані з кешу замість щойно отриманого з ефіру кадру.
2. **Вирівнювання пам'яті:** вхідні буфери для криптографічних геш-функцій та таблиця потоків повинні розміщуватися в пам'яті, вирівняній за 32-байтними межами (розмір рядка кешу L1).

Апаратний захист пам'яті (MPU):
Для запобігання несанкціонованому чи випадковому зчитуванню секретних ключів сторонніми низькопріоритетними задачами польотного стека область оперативної пам'яті зі структурою `signing_ctx` конфігурується через апаратний модуль захисту пам'яті (Memory Protection Unit — MPU) як привілейований регіон (Privileged Read/Write Only). Спроба коду користувацького драйвера звернутися за адресою ключа призводить до миттєвого апаратного винятку `MemManage_Handler`.

Асинхронна диспетчеризація завдань у FreeRTOS:
Обробка криптографічних підписів ніколи не виконується безпосередньо всередині обробника переривання UART (ISR). Переривання лише фіксує межу кадру в кільцевому DMA-буфері та відправляє повідомлення у чергу завдань зв'язку через виклик `xQueueSendFromISR()`. Окрема задача зв'язку з пріоритетом вищим за звичайні навігаційні модулі, але нижчим за контур кутової стабілізації, прокидається по семафору, виконує перевірку CRC, монотонного часу та дайджесту SHA-256. Це гарантує, що контур гіроскопів та акселерометрів (400–1000 Гц) ніколи не зазнає джиттеру через криптографічні розрахунки на лінії зв'язку.

Вимога прозорості для проміжних маршрутизаторів:
Проміжні демони маршрутизації (такі як `mavlink-router` або `mavproxy`), що працюють на бортових комп'ютерах під керуванням Linux, зобов'язані пересилати підписані кадри MAVLink як прозорі двійкові згустки («as-is»). Будь-яка спроба проміжного проксі розпакувати пакет у внутрішні структури, доповнити корисне навантаження нулями або змінити службові прапорці неминуче руйнує криптографічний підпис на кінцевому приймачі.

Збереження стану в енергонезалежній пам'яті FRAM:
Для захисту від втрати синхронізації часу при раптовому знеструмленні польотний контролер періодично скидає значення `stream->last_timestamp` у захищену енергонезалежну пам'ять FRAM (Ferroelectric RAM) по шині SPI. На відміну від звичайної Flash-пам'яті, FRAM витримує понад `10¹⁴` циклів запису без зношування і не вимагає попереднього стирання сторінок, що дозволяє зберігати часову мітку з періодичністю раз на 1–5 секунд. При перезавантаженні система зчитує збережений час і збільшує його на захисний інтервал (наприклад, +5 секунд), повністю усуваючи загрозу блокування зв'язку.

Утилізація процесорного часу при обробці підписів:
- На мікроконтролері STM32F427 (Cortex-M4F, 168 МГц) розрахунок одного підпису SHA-256 займає 850–900 тактів (~5.2 мкс).
- За інтенсивності вхідних команд 20 Гц навантаження на процесор складає мізерні 0.01% бюджету ядра.
- Використання апаратного криптографічного акселератора HASH на STM32H7 скорочує час обробки кадру до 0.4 мкс.

Ця багатошарова програмна архітектура утворює замкнений, надійний та високопродуктивний контур безпеки, адаптований як для низькопотужних мікроконтролерів польотних стеків, так і для потужних наземних станцій керування безпілотними комплексами.
