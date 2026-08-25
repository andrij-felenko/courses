# ⚙️ Практична реалізація: симулятор алгоритму Чанді-Лампорта для банківських транзакцій

У розподілених фінансових системах та транзакційних сховищах даних гарантія збереження глобальних інваріантів є критичною інженерною вимогою. Розглянемо приклад розподіленої банківської мережі з трьох вузлів (`P0`, `P1`, `P2`), які здійснюють взаємні асинхронні перекази коштів. У такій системі сумарний капітал розподілений між балансами вузлів та сумами грошей, які в цей момент транспортуються мережевими каналами зв'язку.

Загальний інваріант системи формулюється наступним чином:

```
Total_Money = ∑ Balance(Node_i) + ∑ Balance(Channel_ij)
```

Посеред активного потоку транзакцій один із вузлів автономно запускає процедуру зняття глобального знімка. Алгоритм фіксує баланси вузлів та суми в польоті без блокування та без зупинки генерації нових платежів.

## Архітектура симулятора та компоненти мережі

Програмна модель симулятора складається з чотирьох ключових сутностей:

1. **Канали зв'язку (FIFO Message Queues):** Кожна пара вузлів з'єднана окремою чергою повідомлень із гарантією збереження черговості (FIFO). Канал моделює мережеву затримку, зберігаючи повідомлення у буфері до моменту їхньої доставки. Черга реалізована як кільцевий буфер фіксованого розміру для запобігання динамічним алокаціям у критичних секціях.
2. **Типи повідомлень (Message Types):** Мережа передає два типи повідомлень — звичайні прикладні перекази коштів (`MSG_APP_TRANSFER` / `Transfer`) та спеціальні керуючі маркери (`MSG_MARKER` / `Marker`). Маркер містить ідентифікатор відправника та слугує роздільником епох у каналі.
3. **Кінцевий автомат вузла (Node State Machine):** Вузол відстежує свій поточний рахунок, стан участі в поточному знімку (`snapshot_taken`), зафіксований баланс (`recorded_balance`), а також індивідуальні прапорці запису для кожного вхідного каналу (`channel_recording[src]`).
4. **Координатор доставки (Simulation Step Engine):** Дозволяє покроково доставляти окремі повідомлення з каналів, імітуючи асинхронний розклад роботи мережі, затримки пакетів та чергування подій.

## Покроковий сценарій виконання симуляції

Симуляція демонструє точну послідовність кроків алгоритму в динаміці:

- **Крок 0 (Початковий стан):** Баланси вузлів ініціалізуються: `P0 = 500 грн`, `P1 = 300 грн`, `P2 = 200 грн`. Загальна сума становить `1000 грн`. Усі канали порожні.
- **Крок 1 (Транзитний платіж):** Вузол `P0` переказує `100 грн` вузлу `P1`. Баланс `P0` зменшується до `400 грн`. Повідомлення потрапляє в чергу каналу `C_01` і перебуває в польоті.
- **Крок 2 (Ініціація знімка на P0):** Вузол `P0` фіксує свій локальний стан (`recorded_balance = 400 грн`) і надсилає маркери сусідам `P1` та `P2`. Одночасно `P0` починає запис каналів `C_10` та `C_20`.
- **Крок 3 (Платіж після маркера):** Вузол `P0` надсилає ще `50 грн` вузлу `P1`. Повідомлення стає в чергу `C_01` позаду маркера. Баланс `P0` стає `350 грн`.
- **Крок 4 (Отримання першого платежу):** Вузол `P1` отримує платіж `100 грн` до надходження маркера. Баланс `P1` стає `400 грн`.
- **Крок 5 (Прибуття першого маркера на P1):** Вузол `P1` отримує маркер від `P0`. Оскільки це перший маркер для `P1`, він фіксує свій поточний баланс `400 грн`, позначає стан каналу `C_01` як `0 грн` (порожній), ретранслює маркери сусідам `P0` та `P2` і починає запис каналу `C_21`.
- **Крок 6 (Поширення маркерів):** Маркери доходять до `P2` та повертаються до `P0`. Усі вузли отримують маркери з усіх своїх вхідних каналів і завершують запис.
- **Крок 7 (Доставка пізнього платежу):** Платіж `50 грн` надходить до `P1` після маркера і збільшує поточний баланс `P1` до `450 грн`, але не потрапляє у знімок, оскільки надійшов у наступній епосі.

## Обробка конкурентних ініціаторів та циклічних топологій

У реальних розподілених системах кілька вузлів можуть одночасно вирішити ініціювати глобальний знімок. Алгоритм Чанді-Лампорта є природно стійким до паралельних ініціацій за умови використання унікальних ідентифікаторів епохи (`snapshot_id`). Якщо вузол отримує маркер епохи `K` у момент, коли він сам щойно запустив епоху `K`, він просто трактує цей маркер як сигнал закриття відповідного вхідного каналу (правило Case B), не перезаписуючи локальний стан повторно.

У повнозв'язних або циклічних графах маркер проходить по кожному орієнтованому каналу рівно один раз. Кожен вузол транслює маркер у всі свої вихідні лінії, що гарантує детерміноване завершення запису за скінченну кількість кроків без утворення нескінченних циклів циркуляції маркерів.

## Програмний код симулятора

Нижче наведено самодостатні, ідіоматичні реалізації симулятора мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>

#define NUM_NODES 3
#define MAX_QUEUE 64

typedef enum {
    MSG_APP_TRANSFER,
    MSG_MARKER
} MessageType;

typedef struct {
    MessageType type;
    int from;
    int to;
    int amount;
} Message;

typedef struct {
    Message buffer[MAX_QUEUE];
    int head;
    int tail;
    int count;
} FifoQueue;

static void queue_init(FifoQueue* q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

static bool queue_push(FifoQueue* q, Message msg) {
    if (q->count >= MAX_QUEUE) return false;
    q->buffer[q->tail] = msg;
    q->tail = (q->tail + 1) % MAX_QUEUE;
    q->count++;
    return true;
}

static bool queue_pop(FifoQueue* q, Message* msg) {
    if (q->count == 0) return false;
    *msg = q->buffer[q->head];
    q->head = (q->head + 1) % MAX_QUEUE;
    q->count--;
    return true;
}

typedef struct {
    int id;
    int balance;
    
    /* Стан знімка */
    bool snapshot_taken;
    int recorded_balance;
    
    /* Запис стану вхідних каналів: channel_recording[src] == true */
    bool channel_recording[NUM_NODES];
    bool marker_received[NUM_NODES];
    int recorded_channel_sum[NUM_NODES];
} Node;

typedef struct {
    Node nodes[NUM_NODES];
    FifoQueue channels[NUM_NODES][NUM_NODES];
} Network;

void network_init(Network* net, const int initial_balances[NUM_NODES]) {
    for (int i = 0; i < NUM_NODES; i++) {
        net->nodes[i].id = i;
        net->nodes[i].balance = initial_balances[i];
        net->nodes[i].snapshot_taken = false;
        net->nodes[i].recorded_balance = 0;
        
        for (int j = 0; j < NUM_NODES; j++) {
            net->nodes[i].channel_recording[j] = false;
            net->nodes[i].marker_received[j] = false;
            net->nodes[i].recorded_channel_sum[j] = 0;
            queue_init(&net->channels[i][j]);
        }
    }
}

void node_send_marker_to_all(Network* net, int node_id) {
    for (int dst = 0; dst < NUM_NODES; dst++) {
        if (dst == node_id) continue;
        Message marker = {
            .type = MSG_MARKER,
            .from = node_id,
            .to = dst,
            .amount = 0
        };
        queue_push(&net->channels[node_id][dst], marker);
    }
}

void node_initiate_snapshot(Network* net, int node_id) {
    Node* node = &net->nodes[node_id];
    node->snapshot_taken = true;
    node->recorded_balance = node->balance;
    
    /* Ініціатор записує всі вхідні канали від сусідів */
    for (int src = 0; src < NUM_NODES; src++) {
        if (src != node_id) {
            node->channel_recording[src] = true;
            node->marker_received[src] = false;
        }
    }
    
    node_send_marker_to_all(net, node_id);
    printf("[Вузол %d] Ініціював знімок. Зафіксований баланс = %d\n", node_id, node->recorded_balance);
}

void node_send_money(Network* net, int from, int to, int amount) {
    if (net->nodes[from].balance < amount) return;
    
    net->nodes[from].balance -= amount;
    Message msg = {
        .type = MSG_APP_TRANSFER,
        .from = from,
        .to = to,
        .amount = amount
    };
    queue_push(&net->channels[from][to], msg);
}

void node_process_message(Network* net, int to, Message msg) {
    Node* node = &net->nodes[to];
    int from = msg.from;
    
    if (msg.type == MSG_MARKER) {
        if (!node->snapshot_taken) {
            /* Перший маркер: зберігаємо стан процесу */
            node->snapshot_taken = true;
            node->recorded_balance = node->balance;
            node->marker_received[from] = true;
            node->channel_recording[from] = false; /* Канал прибуття порожній */
            node->recorded_channel_sum[from] = 0;
            
            /* Вмикаємо запис для решти вхідних каналів */
            for (int src = 0; src < NUM_NODES; src++) {
                if (src != to && src != from) {
                    node->channel_recording[src] = true;
                    node->marker_received[src] = false;
                }
            }
            
            node_send_marker_to_all(net, to);
            printf("[Вузол %d] Отримав перший маркер від %d. Баланс = %d, канал C_%d%d = 0\n",
                   to, from, node->recorded_balance, from, to);
        } else {
            /* Наступний маркер: зупиняємо запис цього каналу */
            node->marker_received[from] = true;
            node->channel_recording[from] = false;
            printf("[Вузол %d] Отримав наступний маркер від %d. Стан каналу C_%d%d = %d\n",
                   to, from, from, to, node->recorded_channel_sum[from]);
        }
    } else {
        /* Звичайний грошовий переказ */
        node->balance += msg.amount;
        
        /* Якщо канал записується, фіксуємо транзитні гроші */
        if (node->channel_recording[from]) {
            node->recorded_channel_sum[from] += msg.amount;
            printf("[Вузол %d] Зафіксовано транзит у C_%d%d: +%d грн\n", to, from, to, msg.amount);
        }
    }
}

void deliver_one_message(Network* net, int from, int to) {
    Message msg;
    if (queue_pop(&net->channels[from][to], &msg)) {
        node_process_message(net, to, msg);
    }
}

int main(void) {
    Network net;
    int initial[NUM_NODES] = {500, 300, 200};
    network_init(&net, initial);
    
    printf("=== Старт симуляції Чанді-Лампорта ===\n");
    printf("Початковий загальний баланс: %d грн\n\n", initial[0] + initial[1] + initial[2]);
    
    /* 1. Початок роботи: P0 переказує P1 100 грн (у дорозі) */
    node_send_money(&net, 0, 1, 100);
    
    /* 2. P0 ініціює знімок */
    node_initiate_snapshot(&net, 0);
    
    /* 3. P0 надсилає P1 ще 50 грн (після маркера) */
    node_send_money(&net, 0, 1, 50);
    
    /* 4. P1 отримує 100 грн ДО маркера */
    deliver_one_message(&net, 0, 1);
    
    /* 5. P1 отримує маркер від P0 */
    deliver_one_message(&net, 0, 1);
    
    /* 6. Доставляємо маркери до P2 та назад до P0 */
    deliver_one_message(&net, 0, 2);
    deliver_one_message(&net, 1, 2);
    deliver_one_message(&net, 1, 0);
    deliver_one_message(&net, 2, 0);
    deliver_one_message(&net, 2, 1);
    
    /* 7. Доставляємо останній платіж на 50 грн */
    deliver_one_message(&net, 0, 1);
    
    /* Підсумок знімка */
    int total_nodes = 0;
    int total_channels = 0;
    
    printf("\n=== Результат розподіленого знімка ===\n");
    for (int i = 0; i < NUM_NODES; i++) {
        printf("Вузол P%d: зафіксований стан = %d грн\n", i, net.nodes[i].recorded_balance);
        total_nodes += net.nodes[i].recorded_balance;
        
        for (int j = 0; j < NUM_NODES; j++) {
            if (i != j && net.nodes[i].recorded_channel_sum[j] > 0) {
                printf("  Канал C_%d%d (у польоті) = %d грн\n", j, i, net.nodes[i].recorded_channel_sum[j]);
                total_channels += net.nodes[i].recorded_channel_sum[j];
            }
        }
    }
    
    int snapshot_sum = total_nodes + total_channels;
    printf("\nСума вузлів: %d грн\n", total_nodes);
    printf("Сума каналів: %d грн\n", total_channels);
    printf("Загальна сума знімка: %d грн\n", snapshot_sum);
    printf("Інваріант збереження: %s\n", (snapshot_sum == 1000) ? "ВИКОНАНО" : "ПОРУШЕНО");
    
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <array>
#include <memory>
#include <cassert>

constexpr std::size_t NodeCount = 3;

enum class MessageType {
    Transfer,
    Marker
};

struct Message {
    MessageType type{MessageType::Transfer};
    std::size_t from{0};
    std::size_t to{0};
    int amount{0};
};

class Node {
public:
    explicit Node(std::size_t id, int initial_balance)
        : id_(id), balance_(initial_balance) {
        channel_recording_.fill(false);
        marker_received_.fill(false);
        recorded_channels_.fill(0);
    }

    [[nodiscard]] std::size_t id() const noexcept { return id_; }
    [[nodiscard]] int balance() const noexcept { return balance_; }
    [[nodiscard]] bool snapshot_taken() const noexcept { return snapshot_taken_; }
    [[nodiscard]] int recorded_balance() const noexcept { return recorded_balance_; }
    [[nodiscard]] int recorded_channel(std::size_t from) const noexcept { return recorded_channels_[from]; }

    void deduct(int amount) {
        assert(balance_ >= amount);
        balance_ -= amount;
    }

    void add(int amount) {
        balance_ += amount;
    }

    void initiate_snapshot(std::vector<Message>& outgoing_markers) {
        snapshot_taken_ = true;
        recorded_balance_ = balance_;

        for (std::size_t src = 0; src < NodeCount; ++src) {
            if (src != id_) {
                channel_recording_[src] = true;
                marker_received_[src] = false;
            }
        }
        create_markers(outgoing_markers);
    }

    void handle_marker(std::size_t from, std::vector<Message>& outgoing_markers) {
        if (!snapshot_taken_) {
            snapshot_taken_ = true;
            recorded_balance_ = balance_;
            marker_received_[from] = true;
            channel_recording_[from] = false;
            recorded_channels_[from] = 0;

            for (std::size_t src = 0; src < NodeCount; ++src) {
                if (src != id_ && src != from) {
                    channel_recording_[src] = true;
                    marker_received_[src] = false;
                }
            }
            create_markers(outgoing_markers);
        } else {
            marker_received_[from] = true;
            channel_recording_[from] = false;
        }
    }

    void handle_transfer(std::size_t from, int amount) {
        balance_ += amount;
        if (channel_recording_[from]) {
            recorded_channels_[from] += amount;
        }
    }

private:
    void create_markers(std::vector<Message>& out) {
        for (std::size_t dst = 0; dst < NodeCount; ++dst) {
            if (dst != id_) {
                out.push_back({MessageType::Marker, id_, dst, 0});
            }
        }
    }

    std::size_t id_;
    int balance_;
    bool snapshot_taken_{false};
    int recorded_balance_{0};
    std::array<bool, NodeCount> channel_recording_{};
    std::array<bool, NodeCount> marker_received_{};
    std::array<int, NodeCount> recorded_channels_{};
};

class DistributedSystem {
public:
    explicit DistributedSystem(const std::array<int, NodeCount>& initial_balances) {
        for (std::size_t i = 0; i < NodeCount; ++i) {
            nodes_.push_back(std::make_unique<Node>(i, initial_balances[i]));
        }
    }

    void send_money(std::size_t from, std::size_t to, int amount) {
        nodes_[from]->deduct(amount);
        channels_[from][to].push({MessageType::Transfer, from, to, amount});
    }

    void start_snapshot(std::size_t initiator) {
        std::vector<Message> markers;
        nodes_[initiator]->initiate_snapshot(markers);
        for (const auto& m : markers) {
            channels_[m.from][m.to].push(m);
        }
    }

    void step(std::size_t from, std::size_t to) {
        if (channels_[from][to].empty()) return;
        auto msg = channels_[from][to].front();
        channels_[from][to].pop();

        if (msg.type == MessageType::Marker) {
            std::vector<Message> markers;
            nodes_[to]->handle_marker(from, markers);
            for (const auto& m : markers) {
                channels_[m.from][m.to].push(m);
            }
        } else {
            nodes_[to]->handle_transfer(from, msg.amount);
        }
    }

    void print_snapshot_report() const {
        int node_total = 0;
        int channel_total = 0;

        std::cout << "\n=== Звіт узгодженого знімка (C++) ===\n";
        for (std::size_t i = 0; i < NodeCount; ++i) {
            std::cout << "Вузол P" << i << ": стан = " << nodes_[i]->recorded_balance() << " грн\n";
            node_total += nodes_[i]->recorded_balance();

            for (std::size_t j = 0; j < NodeCount; ++j) {
                if (i != j && nodes_[i]->recorded_channel(j) > 0) {
                    std::cout << "  Канал C_" << j << i << " (в польоті) = " 
                              << nodes_[i]->recorded_channel(j) << " грн\n";
                    channel_total += nodes_[i]->recorded_channel(j);
                }
            }
        }

        int total = node_total + channel_total;
        std::cout << "Сума станів вузлів: " << node_total << " грн\n";
        std::cout << "Сума станів каналів: " << channel_total << " грн\n";
        std::cout << "Загальна сума знімка: " << total << " грн\n";
        std::cout << "Інваріант збереження: " << (total == 1000 ? "ЗБЕРЕЖЕНО" : "ПОРУШЕНО") << "\n";
    }

private:
    std::vector<std::unique_ptr<Node>> nodes_;
    std::array<std::array<std::queue<Message>, NodeCount>, NodeCount> channels_;
};

int main() {
    DistributedSystem system({500, 300, 200});

    system.send_money(0, 1, 100);
    system.start_snapshot(0);
    system.send_money(0, 1, 50);

    system.step(0, 1); // 100 грн отримано P1
    system.step(0, 1); // Маркер від P0 отримано P1
    system.step(0, 2); // Маркер від P0 отримано P2
    system.step(1, 2); // Маркер від P1 отримано P2
    system.step(1, 0); // Маркер від P1 отримано P0
    system.step(2, 0); // Маркер від P2 отримано P0
    system.step(2, 1); // Маркер від P2 отримано P1
    system.step(0, 1); // 50 грн отримано P1 після знімка

    system.print_snapshot_report();
    return 0;
}
```
:::

## Аналіз збереження інваріанта та результатів

Після завершення обробки всіх маркерів сформований знімок містить наступні дані:
- `Вузол P0:` зафіксований баланс = `400 грн` (списування `100 грн` відбулося до знімка, а списування `50 грн` — після).
- `Вузол P1:` зафіксований баланс = `400 грн` (платіж `100 грн` надійшов до маркера і потрапив у баланс).
- `Вузол P2:` зафіксований баланс = `200 грн` (не брав участі у переказах).
- `Канали зв'язку:` у каналі `C_01` стан дорівнює `0 грн`, оскільки перший платіж надійшов до маркера, а другий платіж на `50 грн` був надісланий після маркера.

Сума зафіксованих станів вузлів становить `400 + 400 + 200 = 1000 грн`. Інваріант сумарного капіталу системи зберігся бездоганно, доводячи коректність механізму маркерів в умовах активного асинхронного навантаження.

## Інженерні висновки з моделювання

Практичне моделювання алгоритму Чанді-Лампорта підтверджує важливі інженерні закономірності:
1. **Відсутність блокувань:** Жоден процесорний цикл не витрачається на очікування синхронізації сусідніх вузлів. Прикладні транзакції генеруються та обробляються без затримок.
2. **Локальність прийняття рішень:** Кожен вузол реагує виключно на локальні події та вхідні маркери, не потребуючи централізованого диспетчера чи глобального блокування кластера.
3. **Чутливість до черг:** Розмір буфера запису каналів пропорційний добутку пропускної здатності на затримку мережі (англ. *Bandwidth-Delay Product*). Для високошвидкісних мереж необхідно передбачати захист від переповнення оперативної пам'яті під час фіксації каналів.
