# ⚙️ Реалізація рушія векторних годинників та буфера причинної доставки

Причинний порядок у розподіленій системі вимагає двох взаємопов'язаних компонентів:
1. **Структури даних векторного годинника:** обчислення монотонного зростання локальних подій, злиття векторів при отриманні повідомлень та покомпонентне порівняння для виявлення відношень «передує», «слідує», «ідентичний» або «конкурентний».
2. **Буфера причинної доставки (Causal Delivery Buffer):** механізму, що перехоплює вхідні пакети з мережі та затримує їхню передачу в бізнес-логіку застосунку доти, доки всі причинні попередники пакета не будуть гарантовано доставлені локально.

Нижче наведено робочу реалізацію рушія обома мовами: у чистому C (структури, явне керування пам'яттю та коди помилок) та ідіоматичному сучасному C++ (RAII, інкапсуляція, сильна типізація).

### Вибір структури даних та алгоритм буферизації

Для системи з `N` вузлів векторний годинник представляється масивом цілих чисел `uint64_t`.

Коли вузол `j` отримує від вузла `i` повідомлення з прикріпленим вектором `W`, умова негайної доставки формується двома правилами:
1. `W[i] == V_local[i] + 1` — це безпосередньо наступне очікуване повідомлення від вузла `i` (немає пропущених пакетів від цього відправника).
2. `∀ k ≠ i: W[k] ≤ V_local[k]` — вузол `j` уже доставив усі повідомлення інших вузлів `k`, які вузол `i` встиг побачити перед відправленням поточного пакета.

Якщо хоча б одна умова порушується, пакет розміщується в черзі очікування. Після кожної успішної доставки локальний вектор оновлюється, і буфер повторно сканується для каскадного розблокування залежних повідомлень.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_NODES 16
#define MAX_PAYLOAD 256
#define BUFFER_CAPACITY 64

typedef enum {
    ORDER_LESS,       /* v1 причинно передує v2 (v1 < v2) */
    ORDER_GREATER,    /* v1 причинно слідує за v2 (v1 > v2) */
    ORDER_EQUAL,      /* v1 та v2 ідентичні (v1 == v2) */
    ORDER_CONCURRENT  /* v1 та v2 паралельні / конфліктні (v1 || v2) */
} OrderRelation;

typedef struct {
    uint32_t size;
    uint64_t ticks[MAX_NODES];
} VectorClock;

typedef struct {
    uint32_t sender_id;
    VectorClock clock;
    char payload[MAX_PAYLOAD];
} CausalMessage;

typedef struct {
    CausalMessage messages[BUFFER_CAPACITY];
    bool occupied[BUFFER_CAPACITY];
    size_t count;
} CausalBuffer;

typedef struct {
    uint32_t node_id;
    VectorClock clock;
    CausalBuffer buffer;
} NodeEngine;

void vc_init(VectorClock *vc, uint32_t size) {
    vc->size = (size <= MAX_NODES) ? size : MAX_NODES;
    memset(vc->ticks, 0, sizeof(vc->ticks));
}

void vc_tick(VectorClock *vc, uint32_t node_id) {
    if (node_id < vc->size) {
        vc->ticks[node_id]++;
    }
}

void vc_merge(VectorClock *dest, const VectorClock *src) {
    uint32_t limit = (dest->size < src->size) ? dest->size : src->size;
    for (uint32_t i = 0; i < limit; i++) {
        if (src->ticks[i] > dest->ticks[i]) {
            dest->ticks[i] = src->ticks[i];
        }
    }
}

OrderRelation vc_compare(const VectorClock *v1, const VectorClock *v2) {
    bool has_less = false;
    bool has_greater = false;
    uint32_t size = (v1->size < v2->size) ? v1->size : v2->size;

    for (uint32_t i = 0; i < size; i++) {
        if (v1->ticks[i] < v2->ticks[i]) {
            has_less = true;
        } else if (v1->ticks[i] > v2->ticks[i]) {
            has_greater = true;
        }
    }

    if (has_less && !has_greater) return ORDER_LESS;
    if (has_greater && !has_less) return ORDER_GREATER;
    if (!has_less && !has_greater) return ORDER_EQUAL;
    return ORDER_CONCURRENT;
}

void node_init(NodeEngine *node, uint32_t node_id, uint32_t total_nodes) {
    node->node_id = node_id;
    vc_init(&node->clock, total_nodes);
    memset(node->buffer.occupied, 0, sizeof(node->buffer.occupied));
    node->buffer.count = 0;
}

CausalMessage node_create_message(NodeEngine *node, const char *payload) {
    vc_tick(&node->clock, node->node_id);
    CausalMessage msg;
    msg.sender_id = node->node_id;
    msg.clock = node->clock;
    snprintf(msg.payload, MAX_PAYLOAD, "%s", payload);
    return msg;
}

static bool is_causally_ready(const NodeEngine *node, const CausalMessage *msg) {
    uint32_t s = msg->sender_id;
    if (s >= node->clock.size) return false;

    /* 1. Повинно бути безпосередньо наступним від цього відправника */
    if (msg->clock.ticks[s] != node->clock.ticks[s] + 1) {
        return false;
    }

    /* 2. Для всіх інших вузлів ми повинні бачити щонайменше стільки ж повідомлень */
    for (uint32_t k = 0; k < node->clock.size; k++) {
        if (k != s && msg->clock.ticks[k] > node->clock.ticks[k]) {
            return false;
        }
    }
    return true;
}

static void apply_delivery(NodeEngine *node, const CausalMessage *msg) {
    node->clock.ticks[msg->sender_id] = msg->clock.ticks[msg->sender_id];
    printf("[Вузол %u] ДОСТАВЛЕНО: '%s' від вузла %u | Годинник: [",
           node->node_id, msg->payload, msg->sender_id);
    for (uint32_t i = 0; i < node->clock.size; i++) {
        printf("%llu%s", (unsigned long long)node->clock.ticks[i],
               (i + 1 < node->clock.size) ? ", " : "");
    }
    printf("]\n");
}

void node_receive_message(NodeEngine *node, const CausalMessage *msg) {
    if (is_causally_ready(node, msg)) {
        apply_delivery(node, msg);

        /* Каскадна перевірка буфера після просування годинника */
        bool progressed = true;
        while (progressed) {
            progressed = false;
            for (size_t i = 0; i < BUFFER_CAPACITY; i++) {
                if (node->buffer.occupied[i]) {
                    if (is_causally_ready(node, &node->buffer.messages[i])) {
                        apply_delivery(node, &node->buffer.messages[i]);
                        node->buffer.occupied[i] = false;
                        node->buffer.count--;
                        progressed = true;
                        break; /* перезапускаємо цикл для свіжого вектора */
                    }
                }
            }
        }
    } else {
        /* Збереження у буфер очікування */
        if (node->buffer.count < BUFFER_CAPACITY) {
            for (size_t i = 0; i < BUFFER_CAPACITY; i++) {
                if (!node->buffer.occupied[i]) {
                    node->buffer.messages[i] = *msg;
                    node->buffer.occupied[i] = true;
                    node->buffer.count++;
                    printf("[Вузол %u] ЗАБУФЕРИЗОВАНО: '%s' від вузла %u (залежності не виконано)\n",
                           node->node_id, msg->payload, msg->sender_id);
                    return;
                }
            }
        } else {
            fprintf(stderr, "[Вузол %u] ПОМИЛКА: буфер переповнено!\n", node->node_id);
        }
    }
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <optional>
#include <algorithm>
#include <cstdint>

enum class OrderRelation {
    Less,       // v1 причинно передує v2 (v1 < v2)
    Greater,    // v1 причинно слідує за v2 (v1 > v2)
    Equal,      // v1 та v2 ідентичні (v1 == v2)
    Concurrent  // v1 та v2 паралельні / конфліктні (v1 || v2)
};

class VectorClock {
public:
    explicit VectorClock(size_t size = 0) : ticks_(size, 0) {}

    void tick(size_t node_id) {
        if (node_id < ticks_.size()) {
            ticks_[node_id]++;
        }
    }

    void merge(const VectorClock& other) {
        size_t common_size = std::min(ticks_.size(), other.ticks_.size());
        for (size_t i = 0; i < common_size; ++i) {
            ticks_[i] = std::max(ticks_[i], other.ticks_[i]);
        }
    }

    [[nodiscard]] size_t size() const noexcept { return ticks_.size(); }
    [[nodiscard]] uint64_t get(size_t node_id) const {
        return (node_id < ticks_.size()) ? ticks_[node_id] : 0;
    }
    void set(size_t node_id, uint64_t val) {
        if (node_id < ticks_.size()) ticks_[node_id] = val;
    }

    [[nodiscard]] OrderRelation compare(const VectorClock& other) const noexcept {
        bool has_less = false;
        bool has_greater = false;
        size_t common_size = std::min(ticks_.size(), other.ticks_.size());

        for (size_t i = 0; i < common_size; ++i) {
            if (ticks_[i] < other.ticks_[i]) has_less = true;
            else if (ticks_[i] > other.ticks_[i]) has_greater = true;
        }

        if (has_less && !has_greater) return OrderRelation::Less;
        if (has_greater && !has_less) return OrderRelation::Greater;
        if (!has_less && !has_greater) return OrderRelation::Equal;
        return OrderRelation::Concurrent;
    }

    friend std::ostream& operator<<(std::ostream& os, const VectorClock& vc) {
        os << "[";
        for (size_t i = 0; i < vc.ticks_.size(); ++i) {
            os << vc.ticks_[i] << (i + 1 < vc.ticks_.size() ? ", " : "");
        }
        return os << "]";
    }

private:
    std::vector<uint64_t> ticks_;
};

struct CausalMessage {
    size_t sender_id;
    VectorClock clock;
    std::string payload;
};

class NodeEngine {
public:
    NodeEngine(size_t node_id, size_t total_nodes)
        : node_id_(node_id), clock_(total_nodes) {}

    CausalMessage create_message(std::string_view payload) {
        clock_.tick(node_id_);
        return CausalMessage{node_id_, clock_, std::string(payload)};
    }

    void receive_message(const CausalMessage& msg) {
        if (is_causally_ready(msg)) {
            apply_delivery(msg);
            drain_buffer();
        } else {
            std::cout << "[Вузол " << node_id_ << "] ЗАБУФЕРИЗОВАНО: '"
                      << msg.payload << "' від вузла " << msg.sender_id
                      << " (очікування залежностей)\n";
            buffer_.push_back(msg);
        }
    }

    [[nodiscard]] const VectorClock& clock() const noexcept { return clock_; }

private:
    [[nodiscard]] bool is_causally_ready(const CausalMessage& msg) const noexcept {
        size_t s = msg.sender_id;
        if (s >= clock_.size()) return false;

        // 1. Повідомлення має бути строго наступним від цього відправника
        if (msg.clock.get(s) != clock_.get(s) + 1) {
            return false;
        }

        // 2. Для всіх інших вузлів локальний стан повинен бачити щонайменше стільки ж
        for (size_t k = 0; k < clock_.size(); ++k) {
            if (k != s && msg.clock.get(k) > clock_.get(k)) {
                return false;
            }
        }
        return true;
    }

    void apply_delivery(const CausalMessage& msg) {
        clock_.set(msg.sender_id, msg.clock.get(msg.sender_id));
        std::cout << "[Вузол " << node_id_ << "] ДОСТАВЛЕНО: '" << msg.payload
                  << "' від вузла " << msg.sender_id << " | Годинник: " << clock_ << "\n";
    }

    void drain_buffer() {
        bool progressed = true;
        while (progressed) {
            progressed = false;
            auto it = std::find_if(buffer_.begin(), buffer_.end(),
                [this](const CausalMessage& m) { return is_causally_ready(m); });

            if (it != buffer_.end()) {
                CausalMessage ready_msg = std::move(*it);
                buffer_.erase(it);
                apply_delivery(ready_msg);
                progressed = true; // перезапускаємо пошук із новим вектором
            }
        }
    }

    size_t node_id_;
    VectorClock clock_;
    std::vector<CausalMessage> buffer_;
};
```
:::

### Покроковий розбір сценарію виконання та трасування

Щоб побачити, як рушій запобігає перевпорядкуванню повідомлень, розглянемо виконання тестового сценарію з трьома вузлами:

1. **Вузол 0** створює повідомлення `M1` ("Init Database") з вектором `[1, 0, 0]` і розсилає його Вузлу 1 та Вузлу 2.
2. **Вузол 1** отримує `M1`. Умова `is_causally_ready` перевіряє: `M1.clock[0] == 1` та `V_local[0] + 1 == 1` (збігається), сторонні координати `≤ 0` (виконано). Повідомлення негайно доставляється, і локальний годинник Вузла 1 стає `[1, 0, 0]`.
3. **Вузол 1** створює залежне повідомлення `M2` ("Create Table Users") з вектором `[1, 1, 0]` і відправляє його на Вузол 2 через високошвидкісний прямий канал.
4. **Мережева аномалія:** прямий пакет `M2` обганяє `M1` на шляху до Вузла 2. Вузол 2 (маючи локальний годинник `[0, 0, 0]`) отримує `M2` раніше за `M1`.
5. **Спрацьовування буфера на Вузлі 2:** перевірка `is_causally_ready` для `M2` дає `false`, оскільки для відправника 0 значення `M2.clock[0] = 1`, але `V_local[0] = 0` (умова `M2.clock[k] ≤ V_local[k]` для `k ≠ sender` порушена). Повідомлення `M2` безпечно поміщається в чергу `buffer_`. Застосунок не бачить спроби створити таблицю до ініціалізації бази.
6. **Прибуття запізнілого `M1` на Вузол 2:** перевірка `M1` успішна (`1 == 0 + 1`), `M1` доставляється застосунку, локальний годинник Вузла 2 стає `[1, 0, 0]`.
7. **Каскадне вивільнення (Drain Buffer):** виклик `drain_buffer()` знаходить `M2` у черзі. Тепер умова для `M2` виконується: `M2.clock[1] == 1 == 0 + 1`, а `M2.clock[0] = 1 ≤ V_local[0] = 1`. Повідомлення `M2` вилучається з буфера та передається застосунку.

Лог роботи цього сценарію наочно демонструє відновлення причинності:

```text
[Вузол 0] Створено M1: 'Init Database' | Годинник: [1, 0, 0]
[Вузол 1] ДОСТАВЛЕНО: 'Init Database' від вузла 0 | Годинник: [1, 0, 0]
[Вузол 1] Створено M2: 'Create Table Users' | Годинник: [1, 1, 0]
[Вузол 2] ЗАБУФЕРИЗОВАНО: 'Create Table Users' від вузла 1 (очікування залежностей)
[Вузол 2] ДОСТАВЛЕНО: 'Init Database' від вузла 0 | Годинник: [1, 0, 0]
[Вузол 2] ДОСТАВЛЕНО: 'Create Table Users' від вузла 1 | Годинник: [1, 1, 0]
```

### Крайові випадки та інженерні пастки

Під час експлуатації рушіїв причинної доставки на практиці виникають чотири критичні ризики:

1. **Блокування голови черги через втрату зв'язку (Head-of-Line Blocking):**
   Якщо одне повідомлення `m_lost` від вузла `A` губиться в мережі, усі наступні повідомлення від `A`, а також усі повідомлення інших вузлів, які причинно залежать від `m_lost`, застрягнуть у буфері назавжди. Без протоколу надійної повторної передачі (англ. *reliable broadcast / retransmit*) пам'ять буфера швидко вичерпається. У промислових системах буфер супроводжується таймером очікування (Negative Acknowledgement, NACK): якщо повідомлення заблоковане довше ніж `2 × RTT`, рушій відправляє запит на повторну передачу відсутнього номера `V_local[k] + 1` безпосередньо до вузла `k`.
2. **Переповнення 64-бітного лічильника:**
   При частоті 1 мільйон операцій на секунду 64-бітне беззнакове число `uint64_t` переповниться лише через 584 000 років безперервної роботи, тому `uint64_t` є абсолютно безпечним стандартом для промислових розподілених систем (на відміну від 32-бітного, який переповниться за 71 хвилину).
3. **Динамічна зміна складу кластера:**
   Якщо до системи додається новий вузол, розмірність вектора `N` змінюється. У статичних масивах це призводить до помилок доступу за межі пам'яті. У відкритих системах вектори реалізують як асоціативні масиви (хеш-таблиці) пар `NodeID -> uint64_t`, де відсутні ключі неявно вважаються нульовими.
4. **Контроль цілісності причинного ланцюга:**
   Отримання вектора, у якому координати менші за попередній стан від того самого відправника (`W[sender] < V_local[sender]`), свідчить про перезавантаження вузла з втратою стану (англ. *amnesia crash*) або атаку підміни пакетів. Рушій повинен генерувати виняток та ініціювати протокол узгодження стану (англ. *state reconciliation*).

### Методика верифікації та стрес-тестування

Для перевірки коректності реалізації рушія під високим навантаженням використовується техніка хаос-тестування (Chaos Testing / Jepsen-подібні тести):
- **Генератор випадкових мережевих затримок:** проміжний проксі-шар емулює псевдовипадковий джиттер від `0` до `500` мс і перевпорядковує до 40% мережевих пакетів.
- **Інваріант верифікації:** для будь-яких двох повідомлень `M_A` та `M_B`, якщо за вектором `M_A.clock < M_B.clock`, порядок викликів `apply_delivery(M_A)` на кожному вузлі кластера зобов'язаний строго передувати виклику `apply_delivery(M_B)`.
- Будь-яке порушення інваріанта автоматично фіксується тестовим фреймворком як критичний дефект узгодженості даних.

### Протокол негативних підтверджень (NACK) та очищення пам'яті

Для запобігання нескінченному витоку пам'яті в разі незворотної втрати мережевих пакетів рушій інтегрується з таймером відстеження прогалин (Gap Detection Timer):

1. **Виявлення пропуску (Sequence Gap):** якщо вузол отримує повідомлення з лічильником `W[sender] = V_local[sender] + k` (де `k > 1`), створюється запис у таблиці очікуваних пакетів із таймаутом `T_nack = 1.5 × RTT`.
2. **Надсилання NACK-запиту:** після спрацьовування таймауту вузол відправляє прямий запит на відправника: `REQ_RETRANSMIT(from_seq = V_local[sender] + 1, to_seq = W[sender] - 1)`.
3. **Евакуація мертвого вузла (Tombstoning):** якщо відправник не відповідає протягом кількох спроб ретрансляції (вузол зазнав катастрофічної аварії), адміністративний протокол консенсусу виключає його зі складу кластера, а локальний рушій примусово просуває значення `V_local[dead_node] = W[dead_node]`, розблоковуючи доставку всіх залежних повідомлень інших працездатних вузлів.
