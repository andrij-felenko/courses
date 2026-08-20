# ⚙️ Практична реалізація рушія Bimodal Multicast на C та C++

Практична побудова високопродуктивного рушія Bimodal Multicast (pbcast) вимагає вирішення комплексу інженерних задач на перетині мережевого програмування ядра, багатопотоковості та керування пам'яттю.

Головний виклик полягає у забезпеченні мінімальної затримки прийому трансляційного потоку одночасно з фоновим обслуговуванням протоколу анти-ентропії. Якщо обробник Gossip блокуватиме основний мережевий сокет, затримка доставки зросте, а вхідний системний буфер сокета переповниться. Тому архітектура промислового рушія розділяється на два ізольовані контури:
1. **Швидкий контур (Fast Path / Data Plane):** неблокуючий прийом пакетів фази 1 через системний сокет `SOCK_DGRAM`, перевірка цілісності, запис у кільцевий буфер та негайна передача прикладному коду.
2. **Контур відновлення (Gossip Engine / Control Plane):** періодичний фоновий таймер, який формує дайджести, опитує випадкових пірів та обробляє запити ретрансляції через окремий пул потоків.

Нижче наведено повнофункціональну реалізацію ядра pbcast двома мовами: низькорівневому системному C (демонструє точне бітове маніпулювання та роботу зі структурами пам'яті) та ідіоматичному сучасному C++20 із застосуванням RAII, безпечних обгорток `std::span` та контейнерів стандартної бібліотеки.

---

## 1. Архітектура кільцевого буфера та бітові маски

Ключовим компонентом вузла pbcast є кільцевий буфер ретрансляції. Кожен вузол веде облік отриманих повідомлень окремо для кожного активного джерела мовлення за допомогою двох фундаментальних скалярів:
- `low_watermark`: найбільший монотонний номер послідовності `SeqNum`, до якого всі повідомлення отримано підряд без жодного пропуску.
- `received_mask`: 64-бітне беззнакове ціле число, де встановлений у `1` біт із позицією `k` (тобто `1ULL << k`) свідчить про те, що пакет із номером `low_watermark + 1 + k` успішно отримано та збережено в буфері, а біт `0` означає пропуск.

Місткість кільцевого буфера `PBCAST_BUFFER_CAPACITY` обирається як степінь двійки (1024 слоти), що дозволяє замінити операцію ділення швидкою побітовою маскою `seq_num & (CAPACITY - 1)`.

:::tabs
```c
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>

#define PBCAST_BUFFER_CAPACITY 1024
#define PBCAST_MAX_PAYLOAD 512
#define PBCAST_MASK_BITS 64

/* Структура збереженого пакета в кільцевому буфері */
typedef struct {
    uint64_t seq_num;
    uint32_t payload_len;
    uint8_t  payload[PBCAST_MAX_PAYLOAD];
    bool     valid;
} pbcast_slot_t;

/* Кільцевий буфер для одного джерела мовлення */
typedef struct {
    uint64_t      sender_id;
    uint64_t      low_watermark;
    uint64_t      received_mask;
    pbcast_slot_t slots[PBCAST_BUFFER_CAPACITY];
} pbcast_buffer_t;

/* Ініціалізація буфера джерела */
void pbcast_buffer_init(pbcast_buffer_t *buf, uint64_t sender_id, uint64_t initial_seq) {
    buf->sender_id = sender_id;
    buf->low_watermark = initial_seq;
    buf->received_mask = 0;
    for (size_t i = 0; i < PBCAST_BUFFER_CAPACITY; ++i) {
        buf->slots[i].valid = false;
        buf->slots[i].seq_num = 0;
        buf->slots[i].payload_len = 0;
    }
}
```
```cpp
#include <cstdint>
#include <vector>
#include <array>
#include <optional>
#include <span>
#include <memory>
#include <iostream>
#include <string_view>

constexpr size_t BufferCapacity = 1024;
constexpr size_t MaxPayloadSize = 512;
constexpr size_t MaskBits = 64;

/* Збережений пакет у буфері ретрансляції */
struct PacketSlot {
    uint64_t seq_num{0};
    std::vector<uint8_t> payload;
    bool valid{false};
};

/* Кільцевий буфер джерела */
class PbcastBuffer {
public:
    explicit PbcastBuffer(uint64_t sender_id, uint64_t initial_seq = 0)
        : sender_id_(sender_id), low_watermark_(initial_seq), received_mask_(0) {
        slots_.resize(BufferCapacity);
    }

    [[nodiscard]] uint64_t sender_id() const noexcept { return sender_id_; }
    [[nodiscard]] uint64_t low_watermark() const noexcept { return low_watermark_; }
    [[nodiscard]] uint64_t received_mask() const noexcept { return received_mask_; }

private:
    uint64_t sender_id_;
    uint64_t low_watermark_;
    uint64_t received_mask_;
    std::vector<PacketSlot> slots_;
};
```
:::

---

## 2. Логіка вставки пакета та монотонного зсуву водяної лінії

Коли на мережевий сокет надходить чергова дейтаграма, алгоритм виконує швидку перевірку:
1. Якщо номер `seq_num <= low_watermark`, пакет уже був доставлений раніше і є застарілим дублікатом. Такий пакет негайно відкидається без захоплення системних блокувань.
2. Якщо `seq_num > low_watermark`, обчислюється зміщення `offset = seq_num - low_watermark - 1`. Якщо зміщення не перевищує розмір буфера, дані копіюються у слот `seq_num % CAPACITY`, а відповідний біт у `received_mask` встановлюється в `1`.
3. Якщо отриманий пакет закриває найстаріший наявний пропуск (тобто біт `0` у масці став рівним `1`), водяна лінія `low_watermark` монотонно інкрементується, а маска зсувається вправо доти, доки молодший біт не стане нулем.

Такий підхід гарантує, що прикладний рівень завжди отримує доступ до актуальної інформації про стан черги без необхідності повного лінійного сканування буфера.

:::tabs
```c
/* Додавання пакета до кільцевого буфера з оновленням водяної лінії */
bool pbcast_buffer_insert(pbcast_buffer_t *buf, uint64_t seq_num, 
                          const uint8_t *data, uint32_t len) {
    if (len > PBCAST_MAX_PAYLOAD) return false;

    /* Пакет уже старіший за поточну водяну лінію — дублікат */
    if (seq_num <= buf->low_watermark) return false;

    uint64_t offset = seq_num - buf->low_watermark - 1;
    if (offset >= PBCAST_BUFFER_CAPACITY) {
        /* Пакет занадто далеко попереду — буфер переповнено через тривалий розрив */
        return false;
    }

    /* Запис у відповідний слот кільцевого буфера */
    size_t slot_idx = seq_num % PBCAST_BUFFER_CAPACITY;
    pbcast_slot_t *slot = &buf->slots[slot_idx];
    slot->seq_num = seq_num;
    slot->payload_len = len;
    memcpy(slot->payload, data, len);
    slot->valid = true;

    /* Оновлення бітової маски, якщо зміщення в межах 64 бітів */
    if (offset < PBCAST_MASK_BITS) {
        buf->received_mask |= (1ULL << offset);
    }

    /* Просування low_watermark для неперервного ланцюжка отриманих пакетів */
    while (buf->received_mask & 1ULL) {
        buf->low_watermark++;
        buf->received_mask >>= 1;

        /* Підтягування наступного біта за межами поточної 64-бітної маски */
        uint64_t next_check_seq = buf->low_watermark + PBCAST_MASK_BITS;
        size_t next_slot_idx = next_check_seq % PBCAST_BUFFER_CAPACITY;
        if (buf->slots[next_slot_idx].valid && buf->slots[next_slot_idx].seq_num == next_check_seq) {
            buf->received_mask |= (1ULL << (PBCAST_MASK_BITS - 1));
        }
    }

    return true;
}
```
```cpp
#include <cstring>
#include <algorithm>

class PbcastReceiver {
public:
    explicit PbcastReceiver(uint64_t sender_id, uint64_t initial_seq = 0)
        : sender_id_(sender_id), low_watermark_(initial_seq), received_mask_(0) {
        slots_.resize(BufferCapacity);
    }

    bool insert_packet(uint64_t seq_num, std::span<const uint8_t> data) {
        if (data.size() > MaxPayloadSize) return false;
        if (seq_num <= low_watermark_) return false;

        const uint64_t offset = seq_num - low_watermark_ - 1;
        if (offset >= BufferCapacity) return false;

        const size_t slot_idx = seq_num % BufferCapacity;
        slots_[slot_idx].seq_num = seq_num;
        slots_[slot_idx].payload.assign(data.begin(), data.end());
        slots_[slot_idx].valid = true;

        if (offset < MaskBits) {
            received_mask_ |= (1ULL << offset);
        }

        /* Просування водяної лінії для безперервної послідовності */
        while (received_mask_ & 1ULL) {
            low_watermark_++;
            received_mask_ >>= 1;

            const uint64_t next_seq = low_watermark_ + MaskBits;
            const size_t next_idx = next_seq % BufferCapacity;
            if (slots_[next_idx].valid && slots_[next_idx].seq_num == next_seq) {
                received_mask_ |= (1ULL << (MaskBits - 1));
            }
        }

        return true;
    }

    [[nodiscard]] std::optional<std::span<const uint8_t>> get_packet(uint64_t seq_num) const {
        const size_t idx = seq_num % BufferCapacity;
        if (slots_[idx].valid && slots_[idx].seq_num == seq_num) {
            return std::span<const uint8_t>(slots_[idx].payload);
        }
        return std::nullopt;
    }

    [[nodiscard]] uint64_t low_watermark() const noexcept { return low_watermark_; }
    [[nodiscard]] uint64_t received_mask() const noexcept { return received_mask_; }

private:
    uint64_t sender_id_;
    uint64_t low_watermark_;
    uint64_t received_mask_;
    std::vector<PacketSlot> slots_;
};
```
:::

---

## 3. Звірка дайджестів та генерація запитів на ремонт

Під час раунду анти-ентропії вузол отримує дайджест від випадково обраного партнера. Функція `pbcast_process_digest` порівнює стан віддаленого піра з локальним кільцевим буфером:
1. Якщо віддалена водяна лінія `remote_watermark` вища за локальну `low_watermark`, вузол виявляє діапазон відсутніх номерів і формує запит на відновлення (`Solicitation`).
2. Додатково скануються одиничні біти у віддаленій масці: якщо партнер володіє пакетом `remote_watermark + 1 + bit`, якого немає в локальній пам'яті, цей номер послідовності також додається до запиту.
3. Якщо ж локальний буфер містить дейтаграми, які відсутні у партнера (наприклад, локальна водяна лінія вища за віддалену), вузол може ініціювати надсилання копій (Push-відновлення).

:::tabs
```c
/* Звірка локального буфера з отриманим дайджестом та формування списку пропусків */
void pbcast_process_digest(const pbcast_buffer_t *buf,
                           uint64_t remote_watermark, uint64_t remote_mask,
                           uint64_t *out_missing_seqs, size_t *out_missing_count,
                           size_t max_requests) {
    *out_missing_count = 0;

    /* Якщо у віддаленого піра водяна лінія вища за нашу */
    if (remote_watermark > buf->low_watermark) {
        for (uint64_t s = buf->low_watermark + 1; s <= remote_watermark; ++s) {
            uint64_t offset = s - buf->low_watermark - 1;
            bool local_has = (offset < PBCAST_MASK_BITS) ? ((buf->received_mask & (1ULL << offset)) != 0) : false;
            if (!local_has && *out_missing_count < max_requests) {
                out_missing_seqs[(*out_missing_count)++] = s;
            }
        }
    }

    /* Перевірка бітової маски віддаленого піра */
    for (size_t bit = 0; bit < PBCAST_MASK_BITS; ++bit) {
        if (remote_mask & (1ULL << bit)) {
            uint64_t s = remote_watermark + 1 + bit;
            if (s > buf->low_watermark) {
                uint64_t offset = s - buf->low_watermark - 1;
                bool local_has = (offset < PBCAST_MASK_BITS) ? ((buf->received_mask & (1ULL << offset)) != 0) : false;
                if (!local_has && *out_missing_count < max_requests) {
                    out_missing_seqs[(*out_missing_count)++] = s;
                }
            }
        }
    }
}
```
```cpp
#include <vector>

struct Digest {
    uint64_t sender_id{0};
    uint64_t low_watermark{0};
    uint64_t received_mask{0};
};

std::vector<uint64_t> calculate_missing_sequences(const PbcastReceiver& receiver, 
                                                  const Digest& remote_digest,
                                                  size_t max_requests = 16) {
    std::vector<uint64_t> missing;
    missing.reserve(max_requests);

    const uint64_t local_wm = receiver.low_watermark();
    const uint64_t local_mask = receiver.received_mask();

    /* Перевірка діапазону від local_wm до remote_watermark */
    if (remote_digest.low_watermark > local_wm) {
        for (uint64_t seq = local_wm + 1; seq <= remote_digest.low_watermark; ++seq) {
            const uint64_t offset = seq - local_wm - 1;
            const bool has = (offset < MaskBits) && ((local_mask & (1ULL << offset)) != 0);
            if (!has) {
                missing.push_back(seq);
                if (missing.size() >= max_requests) return missing;
            }
        }
    }

    /* Перевірка бітів у віддаленій масці */
    for (size_t bit = 0; bit < MaskBits; ++bit) {
        if (remote_digest.received_mask & (1ULL << bit)) {
            const uint64_t seq = remote_digest.low_watermark + 1 + bit;
            if (seq > local_wm) {
                const uint64_t offset = seq - local_wm - 1;
                const bool has = (offset < MaskBits) && ((local_mask & (1ULL << offset)) != 0);
                if (!has) {
                    missing.push_back(seq);
                    if (missing.size() >= max_requests) return missing;
                }
            }
        }
    }

    return missing;
}
```
:::

---

## 4. Комплексний тест відновлення втрат між вузлами

Нижче наведено повноцінний демонстраційний сценарій, який моделює взаємодію двох серверів у кластері:
1. Вузол `B` успішно отримує повну неперервну серію дейтаграм із номерами `#101`, `#102`, `#103`, `#104`.
2. Вузол `A` зазнає пачкової втрати пакета `#103` на локальному інтерфейсі (отримує лише `#101`, `#102` та `#104`).
3. Вузол `A` отримує епідемічний дайджест від `B`, аналізує бітову маску, виявляє пропуск пакета `#103` та надсилає запит `Solicitation`.
4. Вузол `B` здійснює одноадресну ретрансляцію відсутньої дейтаграми, після чого стан вузла `A` досягає повної збіжності, а водяна лінія автоматично зсувається до `#104`.

:::tabs
```c
int main(void) {
    pbcast_buffer_t node_a, node_b;
    pbcast_buffer_init(&node_a, 1, 100);
    pbcast_buffer_init(&node_b, 1, 100);

    const char *msg1 = "Payload #101";
    const char *msg2 = "Payload #102";
    const char *msg3 = "Payload #103 (Lost on A)";
    const char *msg4 = "Payload #104";

    /* Вузол B отримує всі пакети 101..104 */
    pbcast_buffer_insert(&node_b, 101, (const uint8_t*)msg1, strlen(msg1));
    pbcast_buffer_insert(&node_b, 102, (const uint8_t*)msg2, strlen(msg2));
    pbcast_buffer_insert(&node_b, 103, (const uint8_t*)msg3, strlen(msg3));
    pbcast_buffer_insert(&node_b, 104, (const uint8_t*)msg4, strlen(msg4));

    /* Вузол A втратив #103 */
    pbcast_buffer_insert(&node_a, 101, (const uint8_t*)msg1, strlen(msg1));
    pbcast_buffer_insert(&node_a, 102, (const uint8_t*)msg2, strlen(msg2));
    pbcast_buffer_insert(&node_a, 104, (const uint8_t*)msg4, strlen(msg4));

    printf("Стан вузла A перед gossip: LowWatermark=%llu, Mask=0x%llx\n",
           (unsigned long long)node_a.low_watermark, (unsigned long long)node_a.received_mask);

    /* Вузол B надсилає свій дайджест вузлу A */
    uint64_t missing[16];
    size_t missing_count = 0;
    pbcast_process_digest(&node_a, node_b.low_watermark, node_b.received_mask, missing, &missing_count, 16);

    printf("Вузол A виявив пропуски: %zu шт. Перший номер: %llu\n",
           missing_count, missing_count > 0 ? (unsigned long long)missing[0] : 0);

    /* Ретрансляція пакета #103 від B до A */
    if (missing_count > 0 && missing[0] == 103) {
        size_t s_idx = 103 % PBCAST_BUFFER_CAPACITY;
        pbcast_buffer_insert(&node_a, 103, node_b.slots[s_idx].payload, node_b.slots[s_idx].payload_len);
    }

    printf("Стан вузла A після ремонту: LowWatermark=%llu, Mask=0x%llx (Збіжність досягнута!)\n",
           (unsigned long long)node_a.low_watermark, (unsigned long long)node_a.received_mask);

    return 0;
}
```
```cpp
int main() {
    PbcastReceiver node_a(1, 100);
    PbcastReceiver node_b(1, 100);

    const std::string msg1 = "Payload #101";
    const std::string msg2 = "Payload #102";
    const std::string msg3 = "Payload #103 (Lost on A)";
    const std::string msg4 = "Payload #104";

    /* Вузол B отримує всі пакети 101..104 */
    node_b.insert_packet(101, std::span{reinterpret_cast<const uint8_t*>(msg1.data()), msg1.size()});
    node_b.insert_packet(102, std::span{reinterpret_cast<const uint8_t*>(msg2.data()), msg2.size()});
    node_b.insert_packet(103, std::span{reinterpret_cast<const uint8_t*>(msg3.data()), msg3.size()});
    node_b.insert_packet(104, std::span{reinterpret_cast<const uint8_t*>(msg4.data()), msg4.size()});

    /* Вузол A пропускає #103 */
    node_a.insert_packet(101, std::span{reinterpret_cast<const uint8_t*>(msg1.data()), msg1.size()});
    node_a.insert_packet(102, std::span{reinterpret_cast<const uint8_t*>(msg2.data()), msg2.size()});
    node_a.insert_packet(104, std::span{reinterpret_cast<const uint8_t*>(msg4.data()), msg4.size()});

    std::cout << "Стан A до gossip: LowWatermark=" << node_a.low_watermark() 
              << ", Mask=" << node_a.received_mask() << "\n";

    Digest digest_b{
        .sender_id = node_b.sender_id(),
        .low_watermark = node_b.low_watermark(),
        .received_mask = node_b.received_mask()
    };

    auto missing = calculate_missing_sequences(node_a, digest_b);
    std::cout << "Вузол A знайшов " << missing.size() << " пропусків. Перший: " << missing.front() << "\n";

    /* Затягування відсутнього пакета з буфера B */
    if (!missing.empty()) {
        auto repair_data = node_b.get_packet(missing.front());
        if (repair_data.has_value()) {
            node_a.insert_packet(missing.front(), *repair_data);
        }
    }

    std::cout << "Стан A після ремонту: LowWatermark=" << node_a.low_watermark() 
              << ", Mask=" << node_a.received_mask() << " (Повна збіжність!)\n";

    return 0;
}
```
:::

---

## 5. Багатопотоковість та атомарна синхронізація

У реальних високопродуктивних серверах мережевий потік прийому дейтаграм (I/O thread) працює паралельно з фоновим таймером анти-ентропії (Gossip thread). Щоб уникнути важких блокувань через м'ютекси на гарячому шляху, застосовують атомарні змінні:
- Поля `low_watermark` та `received_mask` оголошуються як атомарні типи (`std::atomic<uint64_t>` у C++ або `_Atomic` у C11).
- Операція запису слота виконується з бар'єром пам'яті `std::memory_order_release`.
- Читання дайджесту у фоновому потоці використовує `std::memory_order_acquire`.

Це дозволяє фоновому потоку зчитувати цілісний зріз стану буфера без зупинки основного циклу вичитування пакетів із сокета.

---

## 6. Практичні рекомендації щодо оптимізації під Linux

Під час експлуатації рушія pbcast у високонавантажених серверах Linux критично важливо правильно налаштувати мережеві параметри ядра:
1. **Збільшення системних буферів сокетів (`SO_RCVBUF` / `SO_SNDBUF`):** за замовчуванням буфери UDP можуть становити лише 208 КБ. Для уникнення апаратного скидання пакетів ядром під час короткочасних сплесків слід встановити розмір буфера сокета у 8–16 МБ (`setsockopt(fd, SOL_SOCKET, SO_RCVBUF, ...)`).
2. **Моніторинг лічильників втрат у ядрі:** скидання пакетів через переповнення буферів фіксуються в статистиці `/proc/net/snmp` (лічильник `UdpRcvbufErrors`) та через утиліту `netstat -s -u`.
3. **Пакетний прийом дейтаграм (`recvmmsg`):** замість виконання системного виклику `recvfrom` на кожен окремий пакет, використання `recvmmsg` дозволяє вичитувати до 64 пакетів за один перехід у простір ядра, зменшуючи навантаження на процесор у рази.
