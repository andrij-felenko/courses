# ⚙️ Моделювання асинхронного консенсусу та рандомізованого протоколу Бена-Ора

Теорема FLP стверджує, що в асинхронній мережі детермінований алгоритм не може гарантувати завершення за наявності збоїв. Проте якщо дозволити процесам використовувати локальне джерело випадковості (підкидання монети), заборону можна обійти. Найпростішим і найелегантнішим прикладом такого підходу є **рандомізований протокол консенсусу Бена-Ора (Ben-Or, 1983)**.

Нижче наведено повноцінну симуляцію асинхронної розподіленої мережі з довільними затримками повідомлень та реалізацією алгоритму Бена-Ора.

## Принцип роботи алгоритму Бена-Ора

Нехай у системі є `N` процесів, з яких щонайбільше `f` можуть зазнати аварійної зупинки. Для моделі аварійних відмов без зловмисності (CFT) протокол вимагає суворої більшості: `N ≥ 2f + 1`, або `f < N / 2`.

Протокол виконується послідовними раундами `r = 1, 2, 3, ...`. Кожен раунд складається з двох фаз:

1. **Фаза 1 (Пропозиція — Propose):**
   - Кожен процес `p` надсилає всім повідомлення `PROPOSE(r, v)`, де `v ∈ {0, 1}` — поточна оцінка значення.
   - Процес очікує отримання щонайменше `N - f` повідомлень `PROPOSE` від різних вузлів для поточного раунду `r`.
   - Якщо серед отриманих пропозицій більше ніж `N / 2` голосів віддано за одне значення `v`, процес обирає для наступної фази `RATIFY(r, v)`.
   - Інакше (голоси розділилися порівну або явна більшість відсутня) процес надсилає `RATIFY(r, ?)`, позначаючи невизначеність.

2. **Фаза 2 (Ратифікація та підкидання монети — Ratify / Coin Toss):**
   - Процес очікує щонайменше `N - f` повідомлень `RATIFY` поточного раунду `r`.
   - Якщо отримано щонайменше `f + 1` повідомлень `RATIFY(r, v)` із конкретним значенням `v ≠ ?`:
     - Процес **фіксує остаточне рішення (Decide `v`)** і встановлює свою оцінку для наступних раундів у `v`.
   - Якщо отримано хоча б одне повідомлення `RATIFY(r, v)` із `v ≠ ?`:
     - Процес встановлює свою оцінку на наступний раунд `r + 1` у значення `v` (але ще не вирішує остаточно).
   - Якщо всі отримані повідомлення були `RATIFY(r, ?)`:
     - Процес підкидає монету: обирає значення `v ∈ {0, 1}` рівноймовірно (із ймовірністю `0.5`).
   - Процес переходить до раунду `r + 1`.

## Покроковий механізм та інваріанти безпеки

Чому цей протокол ніколи не порушує одностайність (Agreement), можна побачити з властивостей перетину кворумів:

1. **Неможливість суперечливих ратифікацій у фазі 1:**
   Щоб процес `p` надіслав `RATIFY(r, 0)`, він мусить нарахувати більше ніж `N / 2` голосів за `0` серед зібраних `N - f` пропозицій. Оскільки будь-яка строга більшість `> N / 2` займає понад половину всієї системи, жоден інший процес `q` у тому самому раунді не зможе одночасно зібрати `> N / 2` голосів за `1`. Отже, у кожному раунді `r` може бути згенеровано ратифікації максимум для одного значення `v ∈ {0, 1}` (поряд із повідомленнями невизначеності `?`).

2. **Захист від протилежних рішень у фазі 2:**
   Для прийняття рішення щодо значення `v` процес повинен зібрати щонайменше `f + 1` повідомлень `RATIFY(r, v)`. Якщо процес `p` зафіксував рішення `0` (отримав `f + 1` голосів `RATIFY(r, 0)`), то кожен інший процес `q`, який зібрав `N - f` голосів `RATIFY`, гарантовано отримає хоча б одне повідомлення `RATIFY(r, 0)`, оскільки:

   ```
   (f + 1) + (N - f) - N
   = f + 1 + N - f - N
   = 1      [перетин кворуму рішень і кворуму очікування]
   ```

   Отримавши хоча б одне `RATIFY(r, 0)`, вузол `q` не має права підкидати випадкову монету: він зобов'язаний встановити свою пропозицію на наступний раунд у `0`. Таким чином, у раунді `r + 1` усі коректні вузли одностайно запропонують `0`, що призведе до завершення консенсусу в усіх вузлах.

3. **Гарантія живості через ймовірність:**
   Навіть якщо планувальник мережі навмисно затримує пакети, намагаючись утримати систему в симетричному бівалентному стані (де половина голосує `0`, а половина `1`), підкидання монет діє як рандомізований генератор розриву симетрії. Ймовірність того, що всі `N - f` працюючих вузлів одночасно викинуть однаковий біт, становить `(1/2)^(N - f) > 0`. Як тільки це трапляється, система миттєво переходить в унівалентний стан і фіксує рішення в наступному раунді.

## Реалізація симулятора

Симулятор моделює пул незалежних вузлів та чергу повідомлень з випадковими асинхронними затримками доставки та можливістю емуляції аварійної зупинки вузлів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <time.h>

#define MAX_NODES 32
#define MAX_ROUNDS 100
#define VALUE_NONE -1

typedef enum {
    MSG_PROPOSE,
    MSG_RATIFY
} MsgType;

typedef struct {
    int from;
    int to;
    int round;
    MsgType type;
    int value; /* 0, 1 або VALUE_NONE для '?' */
    int deliver_tick;
} Message;

typedef struct {
    int id;
    int current_round;
    int preference;
    int decided_value;
    bool has_decided;
    bool is_crashed;
    
    /* Буфери отриманих повідомлень поточного раунду */
    int propose_votes[2];
    int propose_count;
    int ratify_votes[2];
    int ratify_unknown_count;
    int ratify_count;
    bool phase1_done;
} Node;

typedef struct {
    Message msgs[4096];
    int head;
    int tail;
    int count;
} MessageQueue;

static void queue_init(MessageQueue* q) {
    q->head = 0;
    q->tail = 0;
    q->count = 0;
}

static void queue_push(MessageQueue* q, Message msg) {
    if (q->count < 4096) {
        q->msgs[q->tail] = msg;
        q->tail = (q->tail + 1) % 4096;
        q->count++;
    }
}

static bool queue_pop_ready(MessageQueue* q, int current_tick, Message* out_msg) {
    for (int i = 0; i < q->count; ++i) {
        int idx = (q->head + i) % 4096;
        if (q->msgs[idx].deliver_tick <= current_tick) {
            *out_msg = q->msgs[idx];
            /* Вилучаємо елемент зсувом */
            for (int j = i; j < q->count - 1; ++j) {
                int curr = (q->head + j) % 4096;
                int next = (q->head + j + 1) % 4096;
                q->msgs[curr] = q->msgs[next];
            }
            q->tail = (q->tail - 1 + 4096) % 4096;
            q->count--;
            return true;
        }
    }
    return false;
}

static void send_broadcast(MessageQueue* q, int from, int n, int round, MsgType type, int val, int current_tick) {
    for (int i = 0; i < n; ++i) {
        Message msg;
        msg.from = from;
        msg.to = i;
        msg.round = round;
        msg.type = type;
        msg.value = val;
        /* Випадкова затримка доставки від 1 до 5 тактів */
        msg.deliver_tick = current_tick + 1 + (rand() % 5);
        queue_push(q, msg);
    }
}

int main(void) {
    srand((unsigned int)time(NULL));
    
    const int n = 5;
    const int f = 2; /* f < n/2 (2 < 2.5) */
    const int quorum = n - f; /* 3 */
    
    Node nodes[MAX_NODES];
    for (int i = 0; i < n; ++i) {
        nodes[i].id = i;
        nodes[i].current_round = 1;
        nodes[i].preference = (i % 2 == 0) ? 0 : 1; /* Різні початкові входи */
        nodes[i].decided_value = VALUE_NONE;
        nodes[i].has_decided = false;
        nodes[i].is_crashed = (i == 0); /* Вузол 0 зазнав аварійної зупинки */
        nodes[i].propose_votes[0] = 0;
        nodes[i].propose_votes[1] = 0;
        nodes[i].propose_count = 0;
        nodes[i].ratify_votes[0] = 0;
        nodes[i].ratify_votes[1] = 0;
        nodes[i].ratify_unknown_count = 0;
        nodes[i].ratify_count = 0;
        nodes[i].phase1_done = false;
    }
    
    MessageQueue queue;
    queue_init(&queue);
    
    int tick = 0;
    /* Стартове розсилання PROPOSE для першого раунду */
    for (int i = 0; i < n; ++i) {
        if (!nodes[i].is_crashed) {
            send_broadcast(&queue, i, n, 1, MSG_PROPOSE, nodes[i].preference, tick);
        }
    }
    
    bool all_decided = false;
    while (tick < 1000 && !all_decided) {
        tick++;
        Message msg;
        while (queue_pop_ready(&queue, tick, &msg)) {
            Node* node = &nodes[msg.to];
            if (node->is_crashed || msg.round != node->current_round) {
                continue;
            }
            
            if (msg.type == MSG_PROPOSE && !node->phase1_done) {
                if (msg.value == 0 || msg.value == 1) {
                    node->propose_votes[msg.value]++;
                }
                node->propose_count++;
                
                if (node->propose_count >= quorum) {
                    node->phase1_done = true;
                    int send_ratify_val = VALUE_NONE;
                    if (node->propose_votes[0] > n / 2) {
                        send_ratify_val = 0;
                    } else if (node->propose_votes[1] > n / 2) {
                        send_ratify_val = 1;
                    }
                    send_broadcast(&queue, node->id, n, node->current_round, MSG_RATIFY, send_ratify_val, tick);
                }
            } else if (msg.type == MSG_RATIFY && node->phase1_done) {
                if (msg.value == 0 || msg.value == 1) {
                    node->ratify_votes[msg.value]++;
                } else {
                    node->ratify_unknown_count++;
                }
                node->ratify_count++;
                
                if (node->ratify_count >= quorum) {
                    /* Перевірка умов завершення або переходу на наступний раунд */
                    if (node->ratify_votes[0] >= f + 1) {
                        node->decided_value = 0;
                        node->has_decided = true;
                        node->preference = 0;
                    } else if (node->ratify_votes[1] >= f + 1) {
                        node->decided_value = 1;
                        node->has_decided = true;
                        node->preference = 1;
                    } else if (node->ratify_votes[0] > 0) {
                        node->preference = 0;
                    } else if (node->ratify_votes[1] > 0) {
                        node->preference = 1;
                    } else {
                        /* Підкидання монети (Coin Flip) */
                        node->preference = rand() % 2;
                    }
                    
                    /* Підготовка до наступного раунду */
                    node->current_round++;
                    node->propose_votes[0] = 0;
                    node->propose_votes[1] = 0;
                    node->propose_count = 0;
                    node->ratify_votes[0] = 0;
                    node->ratify_votes[1] = 0;
                    node->ratify_unknown_count = 0;
                    node->ratify_count = 0;
                    node->phase1_done = false;
                    
                    send_broadcast(&queue, node->id, n, node->current_round, MSG_PROPOSE, node->preference, tick);
                }
            }
        }
        
        /* Перевірка, чи всі працюючі вузли дійшли рішення */
        all_decided = true;
        for (int i = 0; i < n; ++i) {
            if (!nodes[i].is_crashed && !nodes[i].has_decided) {
                all_decided = false;
                break;
            }
        }
    }
    
    printf("Результати консенсусу Бена-Ора (тактів: %d):\n", tick);
    for (int i = 0; i < n; ++i) {
        if (nodes[i].is_crashed) {
            printf("  Вузол %d: [ЗБІЙ/CRASHED]\n", i);
        } else {
            printf("  Вузол %d: Рішення = %d (Раунд = %d)\n",
                   i, nodes[i].decided_value, nodes[i].current_round);
        }
    }
    
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <random>
#include <optional>
#include <algorithm>

enum class MsgType {
    Propose,
    Ratify
};

struct Message {
    int from;
    int to;
    int round;
    MsgType type;
    std::optional<int> value; // nullopt відповідає невизначеності '?'
    int deliver_tick;
};

struct MessageComparator {
    bool operator()(const Message& a, const Message& b) const {
        return a.deliver_tick > b.deliver_tick; // Мін-куча за часом доставки
    }
};

class Node {
public:
    int id;
    int current_round = 1;
    int preference;
    std::optional<int> decided_value = std::nullopt;
    bool is_crashed = false;

    int propose_votes[2] = {0, 0};
    int propose_count = 0;
    int ratify_votes[2] = {0, 0};
    int ratify_count = 0;
    bool phase1_done = false;

    Node(int node_id, int initial_pref, bool crashed = false)
        : id(node_id), preference(initial_pref), is_crashed(crashed) {}

    bool has_decided() const {
        return decided_value.has_value();
    }

    void reset_round_buffers() {
        propose_votes[0] = propose_votes[1] = 0;
        propose_count = 0;
        ratify_votes[0] = ratify_votes[1] = 0;
        ratify_count = 0;
        phase1_done = false;
    }
};

class NetworkSimulator {
public:
    int total_nodes;
    int max_faults;
    int quorum_size;
    std::vector<Node> nodes;
    std::priority_queue<Message, std::vector<Message>, MessageComparator> message_queue;
    std::mt19937 rng{std::random_device{}()};

    NetworkSimulator(int n, int f)
        : total_nodes(n), max_faults(f), quorum_size(n - f) {
        for (int i = 0; i < n; ++i) {
            nodes.emplace_back(i, i % 2, i == 0 /* Вузол 0 зламаний */);
        }
    }

    void broadcast(int from, int round, MsgType type, std::optional<int> val, int current_tick) {
        std::uniform_int_distribution<int> delay_dist(1, 5);
        for (int dest = 0; dest < total_nodes; ++dest) {
            message_queue.push(Message{
                from,
                dest,
                round,
                type,
                val,
                current_tick + delay_dist(rng)
            });
        }
    }

    void run() {
        int tick = 0;
        // Початковий раунд
        for (const auto& node : nodes) {
            if (!node.is_crashed) {
                broadcast(node.id, 1, MsgType::Propose, node.preference, tick);
            }
        }

        std::uniform_int_distribution<int> coin_dist(0, 1);

        while (tick < 1000 && !all_working_decided()) {
            tick++;
            while (!message_queue.empty() && message_queue.top().deliver_tick <= tick) {
                Message msg = message_queue.top();
                message_queue.pop();

                Node& node = nodes[msg.to];
                if (node.is_crashed || msg.round != node.current_round) {
                    continue;
                }

                if (msg.type == MsgType::Propose && !node.phase1_done) {
                    if (msg.value.has_value()) {
                        node.propose_votes[*msg.value]++;
                    }
                    node.propose_count++;

                    if (node.propose_count >= quorum_size) {
                        node.phase1_done = true;
                        std::optional<int> ratify_val = std::nullopt;
                        if (node.propose_votes[0] > total_nodes / 2) {
                            ratify_val = 0;
                        } else if (node.propose_votes[1] > total_nodes / 2) {
                            ratify_val = 1;
                        }
                        broadcast(node.id, node.current_round, MsgType::Ratify, ratify_val, tick);
                    }
                } else if (msg.type == MsgType::Ratify && node.phase1_done) {
                    if (msg.value.has_value()) {
                        node.ratify_votes[*msg.value]++;
                    }
                    node.ratify_count++;

                    if (node.ratify_count >= quorum_size) {
                        if (node.ratify_votes[0] >= max_faults + 1) {
                            node.decided_value = 0;
                            node.preference = 0;
                        } else if (node.ratify_votes[1] >= max_faults + 1) {
                            node.decided_value = 1;
                            node.preference = 1;
                        } else if (node.ratify_votes[0] > 0) {
                            node.preference = 0;
                        } else if (node.ratify_votes[1] > 0) {
                            node.preference = 1;
                        } else {
                            // Підкидання монети (Coin Toss)
                            node.preference = coin_dist(rng);
                        }

                        node.current_round++;
                        node.reset_round_buffers();
                        broadcast(node.id, node.current_round, MsgType::Propose, node.preference, tick);
                    }
                }
            }
        }

        print_results(tick);
    }

    bool all_working_decided() const {
        return std::all_of(nodes.begin(), nodes.end(), [](const Node& node) {
            return node.is_crashed || node.has_decided();
        });
    }

    void print_results(int total_ticks) const {
        std::cout << "Результати C++ симуляції консенсусу Бена-Ора (тактів: " << total_ticks << "):\n";
        for (const auto& node : nodes) {
            if (node.is_crashed) {
                std::cout << "  Вузол " << node.id << ": [ЗБІЙ/CRASHED]\n";
            } else {
                std::cout << "  Вузол " << node.id << ": Рішення = "
                          << (node.decided_value ? std::to_string(*node.decided_value) : "немає")
                          << " (Раунд = " << node.current_round << ")\n";
            }
        }
    }
};

int main() {
    NetworkSimulator sim(5, 2);
    sim.run();
    return 0;
}
```
:::

## Аналіз поведінки, граничні випадки та практичні обмеження

1. **Асинхронний розлад черги та запізнілі повідомлення:**
   У реальній мережі повідомлення з раунду `r = 1` можуть прибути, коли вузол уже перейшов до раунду `r = 3`. Симулятор відкидає пакети з невідповідним номером раунду (`msg.round != node->current_round`), або складає їх у довгостроковий буфер. Завдяки тому, що кожен крок вимагає накопичення кворуму `N - f`, вузли не можуть піти вперед самостійно й не приймають рішень на застарілих даних.
2. **Параліч симетрії та його розрив:**
   Якщо на початку входи розділені порівну (наприклад, 2 вузли за `0` та 2 за `1`), перший раунд не дасть більшості `> N / 2` у фазі 1. Усі вузли надішлють `RATIFY(?)` і звернуться до підкидання монети. З ймовірністю `2 / 2^4 = 1/8` усі 4 працюючі вузли викинуть однакове число, що призведе до миттєвого завершення у 2-му раунді. Якщо ж випадуть різні значення, процес повториться в наступному раунді.
3. **Крайовий випадок перевищення ліміту збоїв (`f ≥ N / 2`):**
   Якщо в кластері з 5 вузлів вийде з ладу 3 вузли (залишиться лише 2), розмір кворуму `N - f = 3` стане недосяжним. Алгоритм коректно зависне у фазі очікування, **не прийнявши хибного рішення**. Це демонструє пріоритет безпеки (Safety) над доступністю.
4. **Ціна чистої рандомізації:**
   Хоча алгоритм Бена-Ора теоретично розв'язує задачу асинхронного консенсусу, його час виконання в найгіршому випадку зростає експоненційно з кількістю вузлів (`O(2^N)` раундів за наявності сильного супротивника). Тому в промислових сховищах даних (Paxos, Raft) перевагу надають частковій синхронності з тайм-аутами лідера, а рандомізовані алгоритми знаходять застосування у великих безлідерних мережах та блокчейн-протоколах (як-от HoneyBadgerBFT).
