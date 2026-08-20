# ⚙️ Розподілений симулятор годинників Лампорта з перевіркою причинних інваріантів

Цей проєкт демонструє практичну програмну реалізацію логічного годинника Лампорта, дискретно-подійну симуляцію асинхронного обміну повідомленнями між розподіленими вузлами в неблокуючому середовищі, автоматичне впорядкування глобального журналу подій у детермінований тотальний порядок та машинну валідацію фундаментальних інваріантів причинності.

## Завдання та архітектура дискретно-подійного симулятора

У реальній комп'ютерній мережі пакети даних зазнають непередбачуваних затримок, можуть надходити не в тому порядку, у якому були надіслані, або губитися. Щоб перевірити коректність протоколу логічного часу, ми створюємо симулятор розподіленої системи з `N` незалежними вузлами.

Архітектура симулятора складається з трьох ключових компонентів:
1. **Модель вузла (Node State)**: кожен вузол має унікальний числовий ідентифікатор `PID`, локальний лічильник годинника Лампорта `L` та внутрішній лічильник подій. Вузол уміє виконувати локальні обчислення, відправляти повідомлення в мережу та опрацьовувати вхідні пакети.
2. **Мережеве повідомлення (Network Message)**: контейнер даних, що містить ідентифікатор повідомлення, `PID` відправника, `PID` одержувача, мітку часу відправлення `send_timestamp` та корисне навантаження.
3. **Глобальний аудитор журналу (Global Auditor Log)**: централізований спостерігач, який фіксує всі згенеровані вузлами події у хронологічному порядку їх появи в симуляції, після чого здійснює верифікацію математичних інваріантів причинності та сортує журнал за правилом тотального порядку Лампорта.

## Реалізація мовами C та C++

Нижче наведено паралельні реалізації симулятора: версія мовою C демонструє роботу з низькорівневими структурами пам'яті, явними буферами та системними функціями, тоді як версія мовою C++ використовує ідіоматичний підхід RAII, безпечні контейнери стандартної бібліотеки, строго типізовані переліки `enum class` та тристоронній оператор порівняння C++20 (`<=>`).

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <assert.h>

#define MAX_EVENTS 256
#define MAX_NODES  8

typedef enum {
    EVENT_LOCAL,
    EVENT_SEND,
    EVENT_RECV
} EventType;

typedef struct {
    uint64_t logical_time;
    uint32_t process_id;
    uint32_t event_id;
    EventType type;
    uint32_t related_msg_id;
    char description[64];
} EventRecord;

typedef struct {
    uint32_t msg_id;
    uint32_t sender_pid;
    uint32_t receiver_pid;
    uint64_t send_timestamp;
    char payload[32];
} NetworkMessage;

typedef struct {
    uint32_t pid;
    uint64_t clock;
    uint32_t event_counter;
} Node;

typedef struct {
    EventRecord records[MAX_EVENTS];
    size_t count;
} GlobalLog;

static GlobalLog g_log;
static uint32_t g_msg_sequence = 1;

void node_init(Node* node, uint32_t pid) {
    node->pid = pid;
    node->clock = 0;
    node->event_counter = 0;
}

static void log_event(Node* node, EventType type, uint32_t msg_id, const char* desc) {
    assert(g_log.count < MAX_EVENTS);
    EventRecord* rec = &g_log.records[g_log.count++];
    rec->logical_time = node->clock;
    rec->process_id = node->pid;
    rec->event_id = ++node->event_counter;
    rec->type = type;
    rec->related_msg_id = msg_id;
    strncpy(rec->description, desc, sizeof(rec->description) - 1);
    rec->description[sizeof(rec->description) - 1] = '\0';
}

void node_execute_local(Node* node, const char* action) {
    node->clock += 1;
    log_event(node, EVENT_LOCAL, 0, action);
}

NetworkMessage node_send_message(Node* node, uint32_t receiver_pid, const char* payload) {
    node->clock += 1;
    NetworkMessage msg;
    msg.msg_id = g_msg_sequence++;
    msg.sender_pid = node->pid;
    msg.receiver_pid = receiver_pid;
    msg.send_timestamp = node->clock;
    strncpy(msg.payload, payload, sizeof(msg.payload) - 1);
    msg.payload[sizeof(msg.payload) - 1] = '\0';

    char desc[64];
    snprintf(desc, sizeof(desc), "Send msg#%u to Node %u", msg.msg_id, receiver_pid);
    log_event(node, EVENT_SEND, msg.msg_id, desc);
    return msg;
}

void node_receive_message(Node* node, const NetworkMessage* msg) {
    assert(msg->receiver_pid == node->pid);
    uint64_t old_clock = node->clock;
    uint64_t max_ts = (old_clock > msg->send_timestamp) ? old_clock : msg->send_timestamp;
    node->clock = max_ts + 1;

    char desc[64];
    snprintf(desc, sizeof(desc), "Recv msg#%u from Node %u (prev=%llu, msg_ts=%llu)",
             msg->msg_id, msg->sender_pid, (unsigned long long)old_clock, (unsigned long long)msg->send_timestamp);
    log_event(node, EVENT_RECV, msg->msg_id, desc);
}

static int compare_events_total_order(const void* a, const void* b) {
    const EventRecord* ea = (const EventRecord*)a;
    const EventRecord* eb = (const EventRecord*)b;
    if (ea->logical_time != eb->logical_time) {
        return (ea->logical_time < eb->logical_time) ? -1 : 1;
    }
    if (ea->process_id != eb->process_id) {
        return (ea->process_id < eb->process_id) ? -1 : 1;
    }
    return (ea->event_id < eb->event_id) ? -1 : 1;
}

void verify_causality_invariants(void) {
    printf("=== Перевірка причинних інваріантів Лампорта ===\n");
    for (size_t i = 0; i < g_log.count; ++i) {
        if (g_log.records[i].type == EVENT_RECV) {
            uint32_t target_msg = g_log.records[i].related_msg_id;
            uint64_t recv_time = g_log.records[i].logical_time;
            bool found_send = false;
            uint64_t send_time = 0;

            for (size_t j = 0; j < g_log.count; ++j) {
                if (g_log.records[j].type == EVENT_SEND && g_log.records[j].related_msg_id == target_msg) {
                    found_send = true;
                    send_time = g_log.records[j].logical_time;
                    break;
                }
            }

            assert(found_send && "Подія відправлення обов'язково існує для кожного отримання");
            assert(recv_time > send_time && "Інваріант Лампорта: L(recv) > L(send)");
            printf("[OK] Повідомлення #%u: Send (L=%llu) -> Recv (L=%llu)\n",
                   target_msg, (unsigned long long)send_time, (unsigned long long)recv_time);
        }
    }
}

int main(void) {
    g_log.count = 0;
    Node node_a, node_b, node_c;
    node_init(&node_a, 1);
    node_init(&node_b, 2);
    node_init(&node_c, 3);

    // 1. Вузол A виконує локальну дію та надсилає повідомлення вузлу B
    node_execute_local(&node_a, "A: ініціалізація транзакції");
    NetworkMessage msg1 = node_send_message(&node_a, 2, "Запит на списання");

    // 2. Вузол B виконує власну паралельну дію
    node_execute_local(&node_b, "B: фонове оновлення індексу");

    // 3. Вузол B отримує msg1 від A
    node_receive_message(&node_b, &msg1);

    // 4. Вузол B надсилає повідомлення вузлу C
    NetworkMessage msg2 = node_send_message(&node_b, 3, "Підтвердження переказу");

    // 5. Вузол C робить локальні дії і отримує msg2
    node_execute_local(&node_c, "C: підготовка буфера");
    node_execute_local(&node_c, "C: перевірка сертифіката");
    node_receive_message(&node_c, &msg2);
    node_execute_local(&node_c, "C: фіксація в журналі");

    // Перевірка інваріантів причинності
    verify_causality_invariants();

    // Сортування журналу за тотальним порядком (L, PID)
    qsort(g_log.records, g_log.count, sizeof(EventRecord), compare_events_total_order);

    printf("\n=== Глобальний журнал подій (Тотальний порядок за (L, PID)) ===\n");
    for (size_t i = 0; i < g_log.count; ++i) {
        const EventRecord* r = &g_log.records[i];
        printf("Крок %2zu: (L=%2llu, PID=%u) -> %s\n",
               i + 1, (unsigned long long)r->logical_time, r->process_id, r->description);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <cstdint>
#include <cassert>
#include <memory>
#include <format>

enum class EventType {
    Local,
    Send,
    Recv
};

struct EventRecord {
    uint64_t logical_time;
    uint32_t process_id;
    uint32_t event_id;
    EventType type;
    uint32_t related_msg_id;
    std::string description;

    auto operator<=>(const EventRecord& other) const = default;
};

struct NetworkMessage {
    uint32_t msg_id;
    uint32_t sender_pid;
    uint32_t receiver_pid;
    uint64_t send_timestamp;
    std::string payload;
};

class Node {
public:
    explicit Node(uint32_t pid, std::vector<EventRecord>& global_log, uint32_t& msg_seq)
        : pid_(pid), clock_(0), event_counter_(0), log_(global_log), msg_sequence_(msg_seq) {}

    void execute_local(std::string_view action) {
        ++clock_;
        log_event(EventType::Local, 0, std::string(action));
    }

    NetworkMessage send_message(uint32_t receiver_pid, std::string_view payload) {
        ++clock_;
        NetworkMessage msg{
            .msg_id = ++msg_sequence_,
            .sender_pid = pid_,
            .receiver_pid = receiver_pid,
            .send_timestamp = clock_,
            .payload = std::string(payload)
        };

        log_event(EventType::Send, msg.msg_id,
                  std::format("Send msg#{} to Node {}", msg.msg_id, receiver_pid));
        return msg;
    }

    void receive_message(const NetworkMessage& msg) {
        assert(msg.receiver_pid == pid_);
        uint64_t old_clock = clock_;
        clock_ = std::max(old_clock, msg.send_timestamp) + 1;

        log_event(EventType::Recv, msg.msg_id,
                  std::format("Recv msg#{} from Node {} (prev={}, msg_ts={})",
                              msg.msg_id, msg.sender_pid, old_clock, msg.send_timestamp));
    }

    [[nodiscard]] uint32_t pid() const noexcept { return pid_; }
    [[nodiscard]] uint64_t clock() const noexcept { return clock_; }

private:
    void log_event(EventType type, uint32_t msg_id, std::string desc) {
        log_.push_back(EventRecord{
            .logical_time = clock_,
            .process_id = pid_,
            .event_id = ++event_counter_,
            .type = type,
            .related_msg_id = msg_id,
            .description = std::move(desc)
        });
    }

    uint32_t pid_;
    uint64_t clock_;
    uint32_t event_counter_;
    std::vector<EventRecord>& log_;
    uint32_t& msg_sequence_;
};

void verify_causality(const std::vector<EventRecord>& log) {
    std::cout << "=== Перевірка причинних інваріантів Лампорта (C++) ===\n";
    for (const auto& recv_ev : log) {
        if (recv_ev.type != EventType::Recv) continue;

        auto it = std::find_if(log.begin(), log.end(), [&](const EventRecord& send_ev) {
            return send_ev.type == EventType::Send && send_ev.related_msg_id == recv_ev.related_msg_id;
        });

        assert(it != log.end() && "Подія відправлення обов'язково присутня");
        assert(recv_ev.logical_time > it->logical_time && "L(recv) > L(send)");
        std::cout << std::format("[OK] Msg #{}: Send (L={}) -> Recv (L={})\n",
                                 recv_ev.related_msg_id, it->logical_time, recv_ev.logical_time);
    }
}

int main() {
    std::vector<EventRecord> global_log;
    uint32_t msg_sequence = 0;

    Node node_a(1, global_log, msg_sequence);
    Node node_b(2, global_log, msg_sequence);
    Node node_c(3, global_log, msg_sequence);

    // 1. Вузол A робить дію та надсилає повідомлення B
    node_a.execute_local("A: ініціалізація транзакції");
    NetworkMessage msg1 = node_a.send_message(2, "Запит на списання");

    // 2. Вузол B виконує власну паралельну дію
    node_b.execute_local("B: фонове оновлення індексу");

    // 3. Вузол B отримує повідомлення від A
    node_b.receive_message(msg1);

    // 4. Вузол B надсилає повідомлення до C
    NetworkMessage msg2 = node_b.send_message(3, "Підтвердження переказу");

    // 5. Вузол C опрацьовує ланцюжок дій
    node_c.execute_local("C: підготовка буфера");
    node_c.execute_local("C: перевірка сертифіката");
    node_c.receive_message(msg2);
    node_c.execute_local("C: фіксація в журналі");

    // Перевірка інваріантів
    verify_causality(global_log);

    // Сортування у тотальний порядок за (logical_time, process_id, event_id)
    std::sort(global_log.begin(), global_log.end(), [](const EventRecord& a, const EventRecord& b) {
        if (a.logical_time != b.logical_time) return a.logical_time < b.logical_time;
        if (a.process_id != b.process_id) return a.process_id < b.process_id;
        return a.event_id < b.event_id;
    });

    std::cout << "\n=== Глобальний журнал подій (Тотальний порядок за (L, PID)) ===\n";
    for (size_t i = 0; i < global_log.size(); ++i) {
        const auto& r = global_log[i];
        std::cout << std::format("Крок {:2}: (L={:2}, PID={}) -> {}\n",
                                 i + 1, r.logical_time, r.process_id, r.description);
    }
    return 0;
}
```
:::

## Покроковий розбір виконання та перевірка інваріантів

Розберемо, як розвивається внутрішній стан кожного вузла під час виконання демонстраційного сценарію:

1. **Вузол A (PID=1)** стартує зі значенням `L = 0`.
   - Подія 1: дія «A: ініціалізація транзакції» збільшує годинник до `L = 1`.
   - Подія 2: відправлення `msg1` на адресу вузла B збільшує годинник до `L = 2`. У заголовок `msg1` записується мітка `send_timestamp = 2`.
2. **Вузол B (PID=2)** стартує зі значенням `L = 0`.
   - Подія 1: вузол B паралельно виконує локальну дію «B: фонове оновлення індексу», піднімаючи свій годинник до `L = 1`. Подія на вузлі A (`L = 1`) і подія на вузлі B (`L = 1`) є абсолютно незалежними і паралельними (`eA1 ∥ eB1`).
   - Подія 2: отримання `msg1`. Локальний годинник вузла B дорівнював `1`, а мітка вхідного повідомлення — `2`. Алгоритм Лампорта обчислює:
     ```
     L_B = max(1, 2) + 1 = 3
     ```
     Годинник вузла B робить стрибок уперед. Це гарантує виконання головного інваріанта: подія отримання на вузлі B отримала мітку `L = 3`, яка строго більша за мітку відправлення `L = 2`.
   - Подія 3: вузол B формує і надсилає повідомлення `msg2` до вузла C. Годинник зростає до `L = 4`, а повідомлення вирушає з міткою `send_timestamp = 4`.
3. **Вузол C (PID=3)** стартує зі значенням `L = 0`.
   - Подія 1: локальна дія «C: підготовка буфера» (`L = 1`).
   - Подія 2: локальна дія «C: перевірка сертифіката» (`L = 2`).
   - Подія 3: отримання `msg2` (`ts = 4`). Годинник вузла C оновлюється:
     ```
     L_C = max(2, 4) + 1 = 5
     ```
   - Подія 4: локальна дія «C: фіксація в журналі» (`L = 6`).

Функція `verify_causality_invariants` автоматично сканує глобальний журнал і для кожної пари подій `send(m)` та `recv(m)` здійснює машинну перевірку суворої нерівності:
```
assert(L(recv) > L(send))
```
Якщо хоча б один пакет через програмну помилку отримає мітку отримання, меншу або рівну мітці відправлення, робота програми негайно припиняється з аварійним звітом. У нашому симуляторі всі пари повідомлень успішно проходять контроль.

## Тотальний порядок та аналіз відсортованого журналу

Після завершення симуляції журнал сортується за допомогою функції `compare_events_total_order`, яка реалізує лексикографічне правило порівняння кортежів `(logical_time, process_id, event_id)`. Підсумковий глобальний журнал виглядає так:

```
Крок  1: (L= 1, PID=1) -> A: ініціалізація транзакції
Крок  2: (L= 1, PID=2) -> B: фонове оновлення індексу
Крок  3: (L= 1, PID=3) -> C: підготовка буфера
Крок  4: (L= 2, PID=1) -> Send msg#1 to Node 2
Крок  5: (L= 2, PID=3) -> C: перевірка сертифіката
Крок  6: (L= 3, PID=2) -> Recv msg#1 from Node 1 (prev=1, msg_ts=2)
Крок  7: (L= 4, PID=2) -> Send msg#2 to Node 3
Крок  8: (L= 5, PID=3) -> Recv msg#2 from Node 2 (prev=2, msg_ts=4)
Крок  9: (L= 6, PID=3) -> C: фіксація в журналі
```

Зверніть увагу: перші три події мають однакове значення логічного часу `L = 1`. Їхнє розташування в журналі (спочатку вузол 1, потім вузол 2, потім вузол 3) визначено виключно числовим ідентифікатором процесу `PID`. Це штучний вибір для усунення невизначеності, який не має фізичного значення, але гарантує, що кожен вузол кластера відтворить абсолютно однаковий ланцюжок станів.

## Підводні камені та пастки реалізації

1. **Небезпека зловмисного або збійного годинника (Byzantine Clock Poisoning)**:
   Якщо один скомпрометований або несправний вузол кластера помилково надішле повідомлення з міткою `L = 1 000 000 000`, вузол-одержувач за правилом максимуму миттєво підтягне свій локальний годинник до мільярда. Після цього всі наступні повідомлення цього вузла рознесуть «отруєний» гігантський лічильник по всьому кластеру. У промислових системах обов'язково накладають захисні обмеження (англ. *sanity bounds*): якщо отриманий логічний годинник відхиляється від очікуваного діапазону більш ніж на поріг `Δ`, повідомлення відхиляється або відправляється на карантин.
2. **Переповнення при використанні знакових чисел**:
   Використання знакових 32-бітних цілих чисел (`int32_t`) призводить до undefined behavior при переповненні: додавання одиниці до `0x7FFFFFFF` перетворює лічильник на від'ємне число, руйнуючи весь тотальний порядок транзакцій. Використовуйте виключно `uint64_t`.
3. **Хибне сприйняття тотального порядку**:
   Відсортований журнал подій демонструє чітку послідовність від кроку 1 до кроку 9. Проте порядок між паралельними подіями є штучним наслідком умови `PID(A) < PID(B)`. Розробник розподіленої системи не повинен будувати бізнес-логіку на припущенні, що вузол A фізично виконав дію раніше за вузол B.
4. **Використання симулятора для розподіленого модульного тестування**:
   Описана модель дискретно-подійного аудиту є потужним інструментом тестування складних розподілених протоколів (Raft, Paxos, 2PC). Замість запуску повільних інтеграційних тестів із реальними сокетами та недетермінованими затримками операційної системи, симулятор дозволяє за частки мілісекунди генерувати мільйони випадкових перевпорядкувань доставки пакетів і машинно доводити відсутність порушень причинності через assertions.
