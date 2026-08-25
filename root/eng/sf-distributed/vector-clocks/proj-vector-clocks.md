# ⚙️ Реалізація рушія векторних годинників та буфера причинної доставки

У розподілених системах пакети даних передаються через асинхронні мережі без гарантій збереження черговості. Маршрутизатори динамічно змінюють шляхи проходження трафіку, виникають повторні передачі через втрати пакетів, а черги комутаторів створюють мінливі затримки. У результаті повідомлення часто прибувають до отримувача у переплутаному порядку: відповідь на коментар може надійти раніше за сам коментар, а операція оновлення балансу — раніше за створення рахунку.

Якщо вузол застосує отримані оновлення негайно, цілісність даних буде безповоротно зруйнована. Програмний модуль векторного годинника у поєднанні з **буфером причинної доставки** (англ. *causal delivery buffer*) розв'язує цю задачу алгоритмічно: він перехоплює всі вхідні пакети, зіставляє їхні векторні мітки з локальним станом знань вузла та затримує передчасні повідомлення в черзі доти, доки не надійдуть усі їхні причинні попередники.

Нижче наведено повну, готову до промислового використання реалізацію рушія векторних годинників та черги причинного впорядкування двома мовами — C та C++.

## Архітектура модуля та алгоритмічні правила

Модуль складається з двох взаємопов'язаних компонентів:

1. **Векторний годинник (`VectorClock`):** Інкапсулює масив цілочисельних лічильників розміром у кількість вузлів кластера. Надає методи локального інкременту (`tick`), покомпонентного об'єднання за правилом максимуму (`merge`) та предикат порівняння (`compare`), який повертає одне з чотирьох відношень: `EQUAL` (ідентичні), `BEFORE` (передує), `AFTER` (слідує) або `CONCURRENT` (паралельні / незалежні).
2. **Буфер причинної доставки (`CausalBuffer`):** Керує чергою відкладених повідомлень. Коли від вузла `S` надходить пакет `Message { sender_id, vector_clock, payload }`, буфер перевіряє **строгий критерій причинної готовності**:
   - **Умова відсутності пропусків від автора:** `V_msg[S] == V_local[S] + 1`. Це гарантує, що повідомлення є безпосередньо наступним у послідовності дій вузла `S`, і жоден попередній пакет від `S` не загубився в мережі.
   - **Умова завершеності причинного контексту:** `∀ k ≠ S: V_msg[k] ≤ V_local[k]`. Це гарантує, що локальний вузол уже отримав та доставив усі повідомлення інших вузлів `k`, які відправник `S` спостерігав перед відправленням цього пакета.

Якщо обидві умови виконано, пакет негайно передається застосунку, локальний годинник оновлюється значенням `V_local[S] = V_msg[S]`, після чого запускається каскадна перевірка буфера. Якщо хоча б одна умова порушена, повідомлення зберігається в буфері очікування.

## Програмна реалізація

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define MAX_NODES 16
#define MAX_BUFFER 64
#define MAX_PAYLOAD 128

typedef enum {
    ORDER_EQUAL,
    ORDER_BEFORE,
    ORDER_AFTER,
    ORDER_CONCURRENT
} CausalOrder;

typedef struct {
    uint32_t counters[MAX_NODES];
    size_t size;
} VectorClock;

typedef struct {
    size_t sender_id;
    VectorClock clock;
    char payload[MAX_PAYLOAD];
    bool occupied;
} BufferedMessage;

typedef struct {
    size_t node_id;
    VectorClock clock;
    BufferedMessage buffer[MAX_BUFFER];
} Node;

void vc_init(VectorClock *vc, size_t size) {
    vc->size = size;
    memset(vc->counters, 0, sizeof(uint32_t) * MAX_NODES);
}

void vc_tick(VectorClock *vc, size_t node_id) {
    if (node_id < vc->size) {
        vc->counters[node_id]++;
    }
}

void vc_merge(VectorClock *dest, const VectorClock *src) {
    size_t limit = dest->size < src->size ? dest->size : src->size;
    for (size_t i = 0; i < limit; i++) {
        if (src->counters[i] > dest->counters[i]) {
            dest->counters[i] = src->counters[i];
        }
    }
}

CausalOrder vc_compare(const VectorClock *a, const VectorClock *b) {
    bool has_less = false;
    bool has_greater = false;
    size_t limit = a->size < b->size ? a->size : b->size;

    for (size_t i = 0; i < limit; i++) {
        if (a->counters[i] < b->counters[i]) {
            has_less = true;
        } else if (a->counters[i] > b->counters[i]) {
            has_greater = true;
        }
    }

    if (!has_less && !has_greater) return ORDER_EQUAL;
    if (has_less && !has_greater)  return ORDER_BEFORE;
    if (!has_less && has_greater)  return ORDER_AFTER;
    return ORDER_CONCURRENT;
}

void node_init(Node *node, size_t node_id, size_t cluster_size) {
    node->node_id = node_id;
    vc_init(&node->clock, cluster_size);
    for (size_t i = 0; i < MAX_BUFFER; i++) {
        node->buffer[i].occupied = false;
    }
}

bool can_deliver(const Node *node, size_t sender_id, const VectorClock *msg_clock) {
    if (msg_clock->counters[sender_id] != node->clock.counters[sender_id] + 1) {
        return false;
    }
    for (size_t i = 0; i < node->clock.size; i++) {
        if (i != sender_id && msg_clock->counters[i] > node->clock.counters[i]) {
            return false;
        }
    }
    return true;
}

void node_deliver(Node *node, size_t sender_id, const VectorClock *msg_clock, const char *payload) {
    node->clock.counters[sender_id] = msg_clock->counters[sender_id];
    printf("[Вузол %zu] Доставлено від Вузла %zu: \"%s\" (Вектор: [", node->node_id, sender_id, payload);
    for (size_t i = 0; i < node->clock.size; i++) {
        printf("%u%s", node->clock.counters[i], i + 1 < node->clock.size ? ", " : "");
    }
    printf("])\n");

    bool progress = true;
    while (progress) {
        progress = false;
        for (size_t i = 0; i < MAX_BUFFER; i++) {
            if (node->buffer[i].occupied && can_deliver(node, node->buffer[i].sender_id, &node->buffer[i].clock)) {
                node->buffer[i].occupied = false;
                node->clock.counters[node->buffer[i].sender_id] = node->buffer[i].clock.counters[node->buffer[i].sender_id];
                printf("[Вузол %zu] Розблоковано з буфера від Вузла %zu: \"%s\"\n",
                       node->node_id, node->buffer[i].sender_id, node->buffer[i].payload);
                progress = true;
                break;
            }
        }
    }
}

void node_receive_message(Node *node, size_t sender_id, const VectorClock *msg_clock, const char *payload) {
    if (can_deliver(sender_id, msg_clock)) {
        node_deliver(node, sender_id, msg_clock, payload);
    } else {
        for (size_t i = 0; i < MAX_BUFFER; i++) {
            if (!node->buffer[i].occupied) {
                node->buffer[i].occupied = true;
                node->buffer[i].sender_id = sender_id;
                node->buffer[i].clock = *msg_clock;
                strncpy(node->buffer[i].payload, payload, MAX_PAYLOAD - 1);
                node->buffer[i].payload[MAX_PAYLOAD - 1] = '\0';
                printf("[Вузол %zu] Затримано в буфері від Вузла %zu: \"%s\"\n", node->node_id, sender_id, payload);
                return;
            }
        }
        fprintf(stderr, "[Вузол %zu] Помилка: буфер переповнено!\n", node->node_id);
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <optional>

enum class CausalOrder {
    Equal,
    Before,
    After,
    Concurrent
};

class VectorClock {
public:
    explicit VectorClock(size_t size = 0) : counters_(size, 0) {}

    void tick(size_t node_id) {
        if (node_id < counters_.size()) {
            counters_[node_id]++;
        }
    }

    void merge(const VectorClock& other) {
        const size_t limit = std::min(counters_.size(), other.counters_.size());
        for (size_t i = 0; i < limit; ++i) {
            counters_[i] = std::max(counters_[i], other.counters_[i]);
        }
    }

    [[nodiscard]] CausalOrder compare(const VectorClock& other) const {
        bool has_less = false;
        bool has_greater = false;
        const size_t limit = std::min(counters_.size(), other.counters_.size());

        for (size_t i = 0; i < limit; ++i) {
            if (counters_[i] < other.counters_[i]) {
                has_less = true;
            } else if (counters_[i] > other.counters_[i]) {
                has_greater = true;
            }
        }

        if (!has_less && !has_greater) return CausalOrder::Equal;
        if (has_less && !has_greater)  return CausalOrder::Before;
        if (!has_less && has_greater)  return CausalOrder::After;
        return CausalOrder::Concurrent;
    }

    [[nodiscard]] uint32_t get(size_t node_id) const {
        return node_id < counters_.size() ? counters_[node_id] : 0;
    }

    void set(size_t node_id, uint32_t val) {
        if (node_id < counters_.size()) {
            counters_[node_id] = val;
        }
    }

    [[nodiscard]] size_t size() const noexcept { return counters_.size(); }

    void print() const {
        std::cout << "[";
        for (size_t i = 0; i < counters_.size(); ++i) {
            std::cout << counters_[i] << (i + 1 < counters_.size() ? ", " : "");
        }
        std::cout << "]";
    }

private:
    std::vector<uint32_t> counters_;
};

struct Message {
    size_t sender_id;
    VectorClock clock;
    std::string payload;
};

class Node {
public:
    Node(size_t node_id, size_t cluster_size)
        : node_id_(node_id), clock_(cluster_size) {}

    void receive_message(size_t sender_id, const VectorClock& msg_clock, std::string_view payload) {
        if (can_deliver(sender_id, msg_clock)) {
            deliver(sender_id, msg_clock, payload);
        } else {
            buffer_.push_back(Message{sender_id, msg_clock, std::string(payload)});
            std::cout << "[Вузол " << node_id_ << "] Затримано в буфері від Вузла "
                      << sender_id << ": \"" << payload << "\"\n";
        }
    }

    [[nodiscard]] const VectorClock& clock() const noexcept { return clock_; }

private:
    [[nodiscard]] bool can_deliver(size_t sender_id, const VectorClock& msg_clock) const {
        if (msg_clock.get(sender_id) != clock_.get(sender_id) + 1) {
            return false;
        }
        for (size_t i = 0; i < clock_.size(); ++i) {
            if (i != sender_id && msg_clock.get(i) > clock_.get(i)) {
                return false;
            }
        }
        return true;
    }

    void deliver(size_t sender_id, const VectorClock& msg_clock, std::string_view payload) {
        clock_.set(sender_id, msg_clock.get(sender_id));
        std::cout << "[Вузол " << node_id_ << "] Доставлено від Вузла " << sender_id
                  << ": \"" << payload << "\" (Вектор: ";
        clock_.print();
        std::cout << ")\n";

        bool progress = true;
        while (progress) {
            progress = false;
            for (auto it = buffer_.begin(); it != buffer_.end(); ++it) {
                if (can_deliver(it->sender_id, it->clock)) {
                    Message ready_msg = std::move(*it);
                    buffer_.erase(it);
                    clock_.set(ready_msg.sender_id, ready_msg.clock.get(ready_msg.sender_id));
                    std::cout << "[Вузол " << node_id_ << "] Розблоковано з буфера від Вузла "
                              << ready_msg.sender_id << ": \"" << ready_msg.payload << "\"\n";
                    progress = true;
                    break;
                }
            }
        }
    }

    size_t node_id_;
    VectorClock clock_;
    std::vector<Message> buffer_;
};
```
:::

## Покроковий аналіз виконання та каскадної доставки

Простежимо роботу алгоритму на конкретному сценарії порушення черговості між трьома вузлами кластера:

1. **Вузол 0** створює початковий запис `m1 = "Створити рахунок"` та відправляє його всім учасникам. Його вектор стає `[1, 0, 0]`.
2. **Вузол 1** отримує `m1`, оновлює свій локальний вектор до `[1, 0, 0]`, виконує операцію поповнення `m2 = "Поповнити на 100 грн"` (інкрементує власну координату до `[1, 1, 0]`) та розсилає `m2`.
3. **Вузол 2** через аномалію маршрутизації отримує пакет `m2` із вектором `[1, 1, 0]` раніше за `m1`:
   - Локальний годинник Вузла 2 дорівнює `[0, 0, 0]`;
   - Перевірка критерію: для відправника (Вузол 1) умова `V_msg[1] == V_local[1] + 1` (`1 == 0 + 1`) виконується;
   - Перевірка контексту: для `k = 0` маємо `V_msg[0] = 1`, але `V_local[0] = 0`. Умова `V_msg[0] ≤ V_local[0]` **порушена** (`1 ≤ 0` — ХИБА);
   - Висновок: Вузол 2 затримує `m2` у буфері. Застосунок не бачить поповнення неіснуючого рахунку.
4. **Вузол 2** нарешті отримує запізнілий пакет `m1` із вектором `[1, 0, 0]`:
   - Перевірка `m1`: `V_msg[0] == 0 + 1` (ІСТИНА), для інших вузлів `0 ≤ 0` (ІСТИНА);
   - Дія: `m1` доставляється застосунку. Локальний годинник Вузла 2 стає `[1, 0, 0]`;
   - Каскадний запуск: буфер повторно перевіряє `m2`. Тепер для `k = 0` умова `1 ≤ 1` виконується;
   - Дія: `m2` вилучається з буфера та успішно доставляється. Підсумковий стан Вузла 2: `[1, 1, 0]`.

## Пастки проектування, пам'ять та безпека

Під час перенесення наведеного алгоритмічного прототипу у високопродуктивні розподілені системи необхідно враховувати низку важливих інженерних аспектів:

### 1. Надійність транспортного рівня (Reliable Transport)
Алгоритм буфера причинної доставки передбачає, що базова мережа гарантує кінцеву доставку (англ. *eventual delivery*) кожного відправленого пакета. Якщо пакет `m1` буде безповоротно втрачено внаслідок апаратного збою комутатора або падіння вузла-відправника, усі наступні залежні повідомлення застрягнуть у буфері очікування назавжди.

У промислових системах буферизацію завжди комбінують із механізмами виявлення збоїв (failure detectors), протоколами підтвердження доставки (ACK/NACK) та періодичним фоновим антиентропійним відновленням (anti-entropy repair).

### 2. Керування пам'яттю та захист від переповнення буфера
У мові C статичний буфер фіксованого розміру `MAX_BUFFER` захищає від динамічної фрагментації пам'яті, проте створює ризик відмови при тривалих затримках мережі. У мові C++ динамічний вектор `std::vector<Message>` автоматично масштабується, але під час інтенсивного навантаження може призвести до вичерпання оперативної пам'яті (Out-Of-Memory).

У виробничих серверах рекомендується встановлювати жорсткий ліміт на розмір буфера в байтах, застосовувати дискове скидання (spilling to disk) для затриманих черг та скидати повільних клієнтів із примусовим повним пересинхронізаційним зрізом (full snapshot sync).

### 3. Багатопотоковість та синхронізація
У багатопотокових мережевих серверах операції читання з сокетів та обробки буфера відбуваються паралельно. Для запобігання гонкам даних доступ до `VectorClock` та `CausalBuffer` необхідно захищати м'ютексом (`std::mutex` або `pthread_mutex_t`) або проектувати кожен буфер як актор (Actor Model), прив'язаний до єдиного виділеного потоку обробки подій (Event Loop).
