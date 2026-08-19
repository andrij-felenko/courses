# ⚙️ Емулятор динамічного dataflow-рушія з тегованими токенами

Класичні процесори архітектури фон Неймана виконують програми як лінійну послідовність інструкцій, керовану лічильником команд (*program counter*, PC). Навіть у найскладніших сучасних суперскалярних ядрах зовнішній інтерфейс залишається послідовним: команди вибираються з пам'яті по порядку, декодуються та впорядковано списуються в буфері оприлюднення (*reorder buffer*). 

Динамічна архітектура потоку даних (*Tagged-Token Dataflow Architecture*) пропонує принципово іншу модель: **програма є орієнтованим графом операторів, а виконання керується виключно готовністю операндів**. У такій машині немає лічильника команд, немає глобального стану пам'яті та немає поняття послідовного кроку. Інструкція стає активною (*fires*) у ту саму мить, коли на всі її вхідні дуги надійшли необхідні пакети даних — токени (*tokens*).

Щоб зрозуміти внутрішню механіку цієї моделі, розберемо та побудуємо працюючий програмний емулятор динамічного dataflow-рушія мовами C та C++.

## Анатомія динамічного графа потоку даних

У статичній моделі Денніса на кожній дузі графа міг перебувати лише один токен даних. Це блокувало паралельне виконання кількох ітерацій одного й того самого циклу, оскільки новий токен неминуче затер би попередній. Динамічна модель Арвінда знімає це обмеження завдяки **тегованим токенам** (*tagged tokens*).

Кожен токен, що рухається крізь систему, несе в собі не лише корисне числове значення, а й мітку контексту:

```
Token = { Tag, DestinationNode, DestinationPort, Value }
Tag   = { ContextID, IterationID }
```

* `Value`: власне обчислені дані (число з рухомою чи фіксованою комою, ціле число чи бітова маска).
* `DestinationNode`: числовий ідентифікатор цільового оператора в графі, куди прямує цей токен.
* `DestinationPort`: номер вхідного порту цільового оператора (наприклад, `0` для лівого операнда віднімання чи ділення, `1` для правого).
* `Tag`: унікальна мітка, яка відокремлює екземпляри одного й того самого коду. Поле `ContextID` кодує виклик функції або окремий потік обчислень, а `IterationID` — порядковий номер ітерації циклу.

Завдяки тегам токени різних ітерацій циклу (наприклад, `IterationID = 0` та `IterationID = 5`) можуть одночасно перебувати на одній і тій самій дузі графа, не змішуючись і не затираючи один одного.

## Вузли графа: від арифметики до керування потоком

Граф потоку даних будується з кількох базових класів операторів:

1. **Арифметично-логічні вузли (`ADD`, `SUB`, `MUL`, `DIV`)**: класичні бінарні оператори. Вони мають два вхідні порти (лівий і правий) та один або кілька вихідних напрямків. Для спрацьовування вузол обов'язково повинен отримати **два** токени з абсолютно ідентичними тегами `Tag`.
2. **Вузли дублювання (`DUP`)**: унарний оператор, який отримує один вхідний токен і копіює його значення на кілька вихідних дуг для різних споживачів зі збереженням вхідного тегу.
3. **Умовні перемикачі (`SWITCH` / `BRANCH`)**: вузол керування, що приймає токен даних на один порт і логічний токен умови (*boolean predicate*) на інший. Якщо умова істинна, токен даних випускається у вихідну гілку `True`; якщо хибна — у гілку `False`.
4. **Вузли злиття (`MERGE`)**: приймає токени з альтернативних гілок обчислення й передає далі єдиний узгоджений потік даних.
5. **Вузли керування ітераціями (`LOOP_STEP`)**: приймає результат поточної ітерації, модифікує тег (збільшує `IterationID` на одиницю) і направляє токен назад на вхідні дуги циклу.

## Складові частини емулятора

Емулятор складається з чотирьох взаємопов'язаних апаратних абстракцій:

```
[Вхідні токени] ──► [Блок Matching Store] ──► [Черга готових операцій] ──► [Обчислювальний блок ALU]
                           ▲                                                          │
                           └───────────────── [Нові токени] ◄─────────────────────────┘
```

1. **Блок зіставлення операндів (`Matching Store`)**: апаратне сховище (у фізичних машинах — асоціативна пам'ять CAM або спеціалізована хеш-таблиця). Коли бінарний вузол отримує перший операнд, він звертається до `Matching Store`. Якщо парного операнда з таким самим ключем `<NodeID, Tag>` ще немає, токен зберігається в пам'яті. Коли приходить другий операнд із тим самим ключем, блок вилучає перший операнд, об'єднує їх у пару та надсилає до черги готовності.
2. **Черга готових операцій (`Ready Queue`)**: масив інструкцій, для яких зібрано повний набір операндів. Ці операції повністю незалежні одна від одної й можуть виконуватися довільною кількістю паралельних арифметичних пристроїв у будь-якому порядку.
3. **Обчислювальні блоки (`Execution Units / ALU`)**: вилучають пакети з черги готовності, виконують відповідну операцію над числами, генерують вихідні токени відповідно до списку вихідних призначень (`dests`) і відправляють їх назад у систему маршрутизації.

## Реалізація емулятора

Розглянемо повну реалізацію dataflow-рушія, що виконує паралельне обчислення полінома `y = (x + 5) · (x − 2)` для довільного масиву вхідних значень `x`. Граф розпаралелює обчислення виразів `(x + 5)` та `(x − 2)` для кожного елемента масиву й одночасно обробляє кілька ітерацій без взаємних блокувань.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_NODES 16
#define MAX_DESTS 4
#define MATCH_STORE_SIZE 64
#define QUEUE_CAPACITY 128

typedef enum {
    OP_PASS,
    OP_ADD,
    OP_SUB,
    OP_MUL,
    OP_DUP
} OpType;

typedef struct {
    int context_id;
    int iter_id;
} Tag;

typedef struct {
    int node_id;
    int port; // 0: лівий операнд, 1: правий операнд
} Dest;

typedef struct {
    Tag tag;
    int dest_node;
    int dest_port;
    double value;
} Token;

typedef struct {
    OpType op;
    int num_dests;
    Dest dests[MAX_DESTS];
} Node;

typedef struct {
    Tag tag;
    int node_id;
    double val;
    bool occupied;
} MatchEntry;

typedef struct {
    Tag tag;
    int node_id;
    double left_val;
    double right_val;
} ReadyPacket;

typedef struct {
    Node nodes[MAX_NODES];
    int num_nodes;

    MatchEntry match_store[MATCH_STORE_SIZE];

    ReadyPacket ready_queue[QUEUE_CAPACITY];
    int queue_head;
    int queue_tail;
    int queue_count;
} DataflowEngine;

void engine_init(DataflowEngine* eng) {
    eng->num_nodes = 0;
    eng->queue_head = 0;
    eng->queue_tail = 0;
    eng->queue_count = 0;
    for (int i = 0; i < MATCH_STORE_SIZE; ++i) {
        eng->match_store[i].occupied = false;
    }
}

int engine_add_node(DataflowEngine* eng, OpType op) {
    int id = eng->num_nodes++;
    eng->nodes[id].op = op;
    eng->nodes[id].num_dests = 0;
    return id;
}

void engine_add_edge(DataflowEngine* eng, int src, int dest, int dest_port) {
    Node* n = &eng->nodes[src];
    if (n->num_dests < MAX_DESTS) {
        n->dests[n->num_dests].node_id = dest;
        n->dests[n->num_dests].port = dest_port;
        n->num_dests++;
    }
}

void engine_push_ready(DataflowEngine* eng, ReadyPacket pkt) {
    if (eng->queue_count < QUEUE_CAPACITY) {
        eng->ready_queue[eng->queue_tail] = pkt;
        eng->queue_tail = (eng->queue_tail + 1) % QUEUE_CAPACITY;
        eng->queue_count++;
    } else {
        fprintf(stderr, "Помилка: черга готових інструкцій переповнена!\n");
    }
}

bool engine_pop_ready(DataflowEngine* eng, ReadyPacket* pkt) {
    if (eng->queue_count == 0) return false;
    *pkt = eng->ready_queue[eng->queue_head];
    eng->queue_head = (eng->queue_head + 1) % QUEUE_CAPACITY;
    eng->queue_count--;
    return true;
}

void engine_push_token(DataflowEngine* eng, Token tok) {
    Node* node = &eng->nodes[tok.dest_node];

    // Унарні вузли або дублювання не потребують очікування другого операнда
    if (node->op == OP_DUP || node->op == OP_PASS) {
        ReadyPacket pkt = {
            .tag = tok.tag,
            .node_id = tok.dest_node,
            .left_val = tok.value,
            .right_val = 0.0
        };
        engine_push_ready(eng, pkt);
        return;
    }

    // Для бінарних вузлів шукаємо парний токен у Matching Store
    int empty_slot = -1;
    for (int i = 0; i < MATCH_STORE_SIZE; ++i) {
        MatchEntry* entry = &eng->match_store[i];
        if (entry->occupied) {
            if (entry->node_id == tok.dest_node &&
                entry->tag.context_id == tok.tag.context_id &&
                entry->tag.iter_id == tok.tag.iter_id) {
                
                // Знайдено операнд-партнер: збираємо готову до виконання інструкцію
                ReadyPacket pkt;
                pkt.tag = tok.tag;
                pkt.node_id = tok.dest_node;
                if (tok.dest_port == 0) {
                    pkt.left_val = tok.value;
                    pkt.right_val = entry->val;
                } else {
                    pkt.left_val = entry->val;
                    pkt.right_val = tok.value;
                }
                entry->occupied = false; // Звільняємо слот
                engine_push_ready(eng, pkt);
                return;
            }
        } else if (empty_slot == -1) {
            empty_slot = i;
        }
    }

    // Пари ще немає — зберігаємо токен у Matching Store для очікування
    if (empty_slot != -1) {
        eng->match_store[empty_slot].occupied = true;
        eng->match_store[empty_slot].node_id = tok.dest_node;
        eng->match_store[empty_slot].tag = tok.tag;
        eng->match_store[empty_slot].val = tok.value;
    } else {
        fprintf(stderr, "Помилка: Matching Store переповнений!\n");
    }
}

void engine_run(DataflowEngine* eng) {
    ReadyPacket pkt;
    while (engine_pop_ready(eng, &pkt)) {
        Node* node = &eng->nodes[pkt.node_id];
        double res = 0.0;

        switch (node->op) {
            case OP_PASS:
            case OP_DUP:  res = pkt.left_val; break;
            case OP_ADD:  res = pkt.left_val + pkt.right_val; break;
            case OP_SUB:  res = pkt.left_val - pkt.right_val; break;
            case OP_MUL:  res = pkt.left_val * pkt.right_val; break;
        }

        // Якщо вузол термінальний (вихідний), друкуємо фінальний результат
        if (node->num_dests == 0) {
            printf("[Вихід] Контекст %d, Ітерація %d -> Результат = %.2f\n",
                   pkt.tag.context_id, pkt.tag.iter_id, res);
            continue;
        }

        // Розсилаємо обчислений результат за вихідними дугами графа
        for (int i = 0; i < node->num_dests; ++i) {
            Token out_tok = {
                .tag = pkt.tag,
                .dest_node = node->dests[i].node_id,
                .dest_port = node->dests[i].port,
                .value = res
            };
            engine_push_token(eng, out_tok);
        }
    }
}

int main(void) {
    DataflowEngine eng;
    engine_init(&eng);

    // Побудова топології графа: y = (x + 5) * (x - 2)
    int node_in  = engine_add_node(&eng, OP_DUP);  // розгалужувач x
    int node_add = engine_add_node(&eng, OP_ADD);  // додавання: x + 5
    int node_sub = engine_add_node(&eng, OP_SUB);  // віднімання: x - 2
    int node_mul = engine_add_node(&eng, OP_MUL);  // множення: (x + 5) * (x - 2)

    engine_add_edge(&eng, node_in, node_add, 0); // x -> лівий порт ADD
    engine_add_edge(&eng, node_in, node_sub, 0); // x -> лівий порт SUB
    engine_add_edge(&eng, node_add, node_mul, 0); // ADD -> лівий порт MUL
    engine_add_edge(&eng, node_sub, node_mul, 1); // SUB -> правий порт MUL

    // Подаємо константні операнди для трьох паралельних ітерацій (контекст 0)
    for (int iter = 0; iter < 3; ++iter) {
        Tag tag = { .context_id = 0, .iter_id = iter };
        // Правий операнд для ADD (+5)
        engine_push_token(&eng, (Token){ tag, node_add, 1, 5.0 });
        // Правий операнд для SUB (-2)
        engine_push_token(&eng, (Token){ tag, node_sub, 1, 2.0 });
    }

    // Подаємо вхідні значення масиву x = [10.0, 20.0, 30.0] з відповідними тегами ітерацій
    double inputs[3] = { 10.0, 20.0, 30.0 };
    for (int iter = 0; iter < 3; ++iter) {
        Tag tag = { .context_id = 0, .iter_id = iter };
        engine_push_token(&eng, (Token){ tag, node_in, 0, inputs[iter] });
    }

    // Запуск конвеєра обчислень за готовністю даних
    engine_run(&eng);

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <queue>
#include <unordered_map>
#include <tuple>
#include <optional>

enum class OpType {
    Pass,
    Add,
    Sub,
    Mul,
    Dup
};

struct Tag {
    int context_id{0};
    int iter_id{0};

    bool operator==(const Tag& other) const noexcept {
        return context_id == other.context_id && iter_id == other.iter_id;
    }
};

struct TagHash {
    std::size_t operator()(const Tag& t) const noexcept {
        return std::hash<int>()(t.context_id) ^ (std::hash<int>()(t.iter_id) << 1);
    }
};

struct MatchKey {
    int node_id;
    Tag tag;

    bool operator==(const MatchKey& other) const noexcept {
        return node_id == other.node_id && tag == other.tag;
    }
};

struct MatchKeyHash {
    std::size_t operator()(const MatchKey& k) const noexcept {
        return std::hash<int>()(k.node_id) ^ (TagHash()(k.tag) << 2);
    }
};

struct Dest {
    int node_id;
    int port; // 0: лівий операнд, 1: правий операнд
};

struct Token {
    Tag tag;
    int dest_node;
    int dest_port;
    double value;
};

struct Node {
    OpType op;
    std::vector<Dest> dests;
};

struct ReadyPacket {
    Tag tag;
    int node_id;
    double left_val;
    double right_val;
};

class DataflowEngine {
public:
    int add_node(OpType op) {
        int id = static_cast<int>(nodes_.size());
        nodes_.push_back(Node{op, {}});
        return id;
    }

    void add_edge(int src, int dest, int dest_port) {
        nodes_.at(src).dests.push_back(Dest{dest, dest_port});
    }

    void push_token(const Token& tok) {
        const auto& node = nodes_.at(tok.dest_node);

        if (node.op == OpType::Dup || node.op == OpType::Pass) {
            ready_queue_.push(ReadyPacket{tok.tag, tok.dest_node, tok.value, 0.0});
            return;
        }

        MatchKey key{tok.dest_node, tok.tag};
        auto it = match_store_.find(key);

        if (it != match_store_.end()) {
            // Знайдено операнд-партнер: вилучаємо та формуємо готову пару
            double stored_val = it->second;
            match_store_.erase(it);

            ReadyPacket pkt;
            pkt.tag = tok.tag;
            pkt.node_id = tok.dest_node;
            if (tok.dest_port == 0) {
                pkt.left_val = tok.value;
                pkt.right_val = stored_val;
            } else {
                pkt.left_val = stored_val;
                pkt.right_val = tok.value;
            }
            ready_queue_.push(pkt);
        } else {
            // Пари ще немає — очікуємо в Matching Store
            match_store_.emplace(key, tok.value);
        }
    }

    void run() {
        while (!ready_queue_.empty()) {
            auto pkt = ready_queue_.front();
            ready_queue_.pop();

            const auto& node = nodes_.at(pkt.node_id);
            double res = 0.0;

            switch (node.op) {
                case OpType::Pass:
                case OpType::Dup: res = pkt.left_val; break;
                case OpType::Add: res = pkt.left_val + pkt.right_val; break;
                case OpType::Sub: res = pkt.left_val - pkt.right_val; break;
                case OpType::Mul: res = pkt.left_val * pkt.right_val; break;
            }

            if (node.dests.empty()) {
                std::cout << "[Вихід] Контекст " << pkt.tag.context_id
                          << ", Ітерація " << pkt.tag.iter_id
                          << " -> Результат = " << res << '\n';
                continue;
            }

            for (const auto& d : node.dests) {
                push_token(Token{pkt.tag, d.node_id, d.port, res});
            }
        }
    }

private:
    std::vector<Node> nodes_;
    std::unordered_map<MatchKey, double, MatchKeyHash> match_store_;
    std::queue<ReadyPacket> ready_queue_;
};

int main() {
    DataflowEngine eng;

    // Побудова графа: y = (x + 5) * (x - 2)
    int node_in  = eng.add_node(OpType::Dup);
    int node_add = eng.add_node(OpType::Add);
    int node_sub = eng.add_node(OpType::Sub);
    int node_mul = eng.add_node(OpType::Mul);

    eng.add_edge(node_in, node_add, 0);
    eng.add_edge(node_in, node_sub, 0);
    eng.add_edge(node_add, node_mul, 0);
    eng.add_edge(node_sub, node_mul, 1);

    // Ініціалізація константних операндів для трьох ітерацій
    for (int iter = 0; iter < 3; ++iter) {
        Tag tag{0, iter};
        eng.push_token(Token{tag, node_add, 1, 5.0});
        eng.push_token(Token{tag, node_sub, 1, 2.0});
    }

    // Вхідні дані масиву x = [10.0, 20.0, 30.0]
    std::vector<double> inputs = {10.0, 20.0, 30.0};
    for (int iter = 0; iter < static_cast<int>(inputs.size()); ++iter) {
        Tag tag{0, iter};
        eng.push_token(Token{tag, node_in, 0, inputs[iter]});
    }

    // Запуск виконання графа
    eng.run();

    return 0;
}
```
:::

## Покрокове простеження виконання

Подивимося, що відбувається в пам'яті емулятора під час обробки першої ітерації (`iter_id = 0`, `x = 10.0`):

1. **Фаза ініціалізації констант**: у систему надходять токени констант:
   * Токен `<tag=<0,0>, dest=node_add, port=1, val=5.0>`. Оскільки `node_add` бінарний, а лівого операнда ще немає, запис потрапляє в `Matching Store` під ключем `<node_add, tag=<0,0>>`.
   * Токен `<tag=<0,0>, dest=node_sub, port=1, val=2.0>`. Зберігається в `Matching Store` під ключем `<node_sub, tag=<0,0>>`.
2. **Фаза подачі вхідного значення**: у вузол `node_in (DUP)` надходить токен `val = 10.0` з тегом `<0,0>`. Вузол `DUP` унарний, тому він не звертається до `Matching Store`, а негайно створює дві копії:
   * Токен `<tag=<0,0>, dest=node_add, port=0, val=10.0>`.
   * Токен `<tag=<0,0>, dest=node_sub, port=0, val=10.0>`.
3. **Фаза першого зіставлення операндів**:
   * Токен для `node_add` прибуває на лівий порт `0`. Емулятор знаходить у `Matching Store` раніше збережений правий операнд `5.0`. Слот очищується, а пара `(10.0, 5.0)` відправляється в `Ready Queue`.
   * Токен для `node_sub` прибуває на лівий порт `0`. Емулятор знаходить у `Matching Store` збережений операнд `2.0`. Пара `(10.0, 2.0)` потрапляє в `Ready Queue`.
4. **Фаза паралельного обчислення першого ярусу**:
   * Вузол `node_add` обчислює `10.0 + 5.0 = 15.0` і випускає токен `<tag=<0,0>, dest=node_mul, port=0, val=15.0>`. Цей токен потрапляє в `Matching Store`, оскільки другий операнд для `node_mul` ще в дорозі.
   * Вузол `node_sub` обчислює `10.0 - 2.0 = 8.0` і випускає токен `<tag=<0,0>, dest=node_mul, port=1, val=8.0>`.
5. **Фаза фінального множення**:
   * Прибуття токена `8.0` на порт `1` вузла `node_mul` знаходить у `Matching Store` токен `15.0`.
   * Формується фінальний готовий пакет `(15.0, 8.0)`. Вузол `node_mul` обчислює `15.0 · 8.0 = 120.0` і виводить фінальне значення.

Для інших ітерацій (`iter_id = 1` з `x = 20.0` та `iter_id = 2` з `x = 30.0`) усі ці кроки відбуваються паралельно або в довільному порядку чергування. Емулятор видасть правильні результати: `(20 + 5) · (20 − 2) = 25 · 18 = 450.0` та `(30 + 5) · (30 − 2) = 35 · 28 = 980.0`.

## Побудова циклів зі зворотним зв'язком

У наведеному базовому прикладі граф був ациклічним (*Directed Acyclic Graph, DAG*). Проте реальні програми вимагають ітеративних циклів зі зворотним зв'язком, де результат поточної ітерації стає входом для наступної (наприклад, накопичення суми чи обчислення факторіала).

Для організації циклу в dataflow-графі застосовують спеціальну тріаду операторів:

1. **Вузол злиття ініціалізації (`LOOP_INIT_MERGE`)**: на порт `0` приймає початкове значення з тегом `iter_id = 0`, а на порт `1` — результат попередньої ітерації зі зворотного ребра. Вузол спрацьовує як шлюз для початку чергового проходу.
2. **Вузол умови завершення (`LOOP_COND`)**: порівнює поточний індекс циклу з граничним значенням і генерує булевий токен-предикат.
3. **Керівний перемикач (`SWITCH`)**: на основі предиката направляє токени даних або у тіло циклу (гілка `True`), або на вихід із циклу (гілка `False`).
4. **Вузол оновлення тегу (`TAG_INC`)**: спеціальний оператор, розміщений на зворотній дузі. Він приймає токен з тегом `<context, i>`, інкрементує номер ітерації та випускає токен з новим тегом `<context, i + 1>`.

Завдяки цьому ітерації не потребують мутабельних змінних у пам'яті: стан передається виключно через потік токенів із послідовно зростаючими тегами.

## Диспетчеризація черги готовності: FIFO проти LIFO та критичного шляху

У нашій базовій реалізації черга готових інструкцій `ready_queue_` організована за простим принципом FIFO (*First-In, First-Out*). Проте порядок вилучення інструкцій із черги чинить вирішальний вплив на загальну продуктивність і витрати пам'яті:

1. **Пошук у ширину (FIFO)**: вибірка найстаріших готових інструкцій веде до агресивного розкриття паралелізму. Усі гілки дерева обчислень починають розвиватися одночасно. Це максимізує утилізацію великої кількості паралельних ALU, але призводить до вибухового зростання кількості токенів у `Matching Store`.
2. **Пошук у глибину (LIFO / Стек)**: вибірка найновіших результатів фокусує обчислювальні ресурси на доведенні поточної гілки до фінального результату. Це суттєво заощаджує пам'ять токенів, оскільки проміжні значення швидко споживаються й видаляються зі сховища, проте може залишати частину паралельних блоків без роботи.
3. **Планування за критичним шляхом (*Critical Path Scheduling*)**: інструкції в черзі пріоритезуються на основі довжини залишкового графа до термінального вузла. Операції, затримка яких затримує весь фінальний результат, отримують найвищий пріоритет, що дає оптимальний теоретичний час виконання графа.

## Explicit Token Store (ETS) проти асоціативного пошуку

Головним вузьким місцем динамічного dataflow завжди була асоціативна пам'ять `Matching Store`. Пошук за тегом серед тисяч активних операндів вимагав енергоємного сканування або складної апаратної хеш-таблиці з розв'язанням колізій.

Щоб подолати цю проблему, в архітектурі комп'ютера *Monsoon* (розробленого в MIT на початку 1990-х років) було винайдено підхід **Explicit Token Store (ETS)**.

Замість асоціативного пошуку в спільній пам'яті, компілятор виділяє для кожного контексту (виклику функції чи ітерації) фіксований блок звичайної адресної пам'яті — **кадр активації** (*activation frame*). Кожен бінарний оператор графа отримує заздалегідь відоме статичне зміщення (*offset*) усередині цього кадру. 

Коли перший операнд прибуває, процесор просто записує його за прямою адресою `BaseAddress(ContextID) + Offset` і виставляє біт наявності (*presence bit*). Коли прибуває другий операнд, він звертається за тією самою прямою адресою, бачить встановлений біт, миттєво зчитує перший операнд, скидає біт і відправляє готову пару в ALU.

ETS замінив складний асоціативний пошук `O(1)` з високою константою затримки на пряме індексування масиву в локальній пам'яті SRAM. Статичне виділення кадрів усунуло динамічну фрагментацію пам'яті та дозволило апаратурі заздалегідь перерозподіляти фіксовані блоки пам'яті між паралельними контекстами, що зробило апаратну реалізацію dataflow значно реалістичнішою.

## Програмні dataflow-рушії в сучасному стеку

Хоча апаратні універсальні процесори з чистим dataflow-ядром не прижилися, самі принципи графового виконання за готовністю операндів стали базовим фундаментом сучасного високонавантаженого програмного забезпечення:

1. **Графові бібліотеки асинхронних завдань**: такі фреймворки, як *Intel OneTBB (Flow Graph)*, *Taskflow* у C++ або *Ray* у Python, представляють паралельні задачі у вигляді DAG. Потоки пулу завдань забирають задачі з черги готовності рівно тоді, коли всі попередні вузли-залежності записали свої результати.
2. **Модель акторів (Actor Model)**: у мовах Erlang чи фреймворках Akka актори обмінюються незмінними повідомленнями-токенами через поштові скриньки (*mailboxes*). Актор пасивно чекає, доки в скриньку не прибуде повідомлення з відповідним патерном тегу, після чого ініціює обчислення.
3. **Середовища виконання графів обчислень штучного інтелекту**: фреймворки машинного навчання (TensorFlow, PyTorch, ONNX Runtime) перетворюють код нейромережі на оптимізований Dataflow Graph (IR), де тензори виступають токенами даних, а тензорні ядра GPU/TPU — обчислювальними акторами.
4. **Реактивне програмування та потокова обробка**: платформи на кшталт Apache Flink або ReactiveX використовують концепцію нескінченного потоку токенів, де оператори фільтрації, трансформації та агрегації спрацьовують реактивно під час надходження чергового елемента даних.

## Реальні інженерні виклики та вузькі місця

Хоча програмний емулятор виглядає компактно, фізична апаратна реалізація такого механізму стикається з кількома критичними проблемами:

### 1. Необмежене розгортання циклів і переповнення пам'яті токенів
Якщо генератор ітерацій випускає нові значення `x` швидше, ніж арифметичні пристрої встигають виконувати додавання та множення, кількість очікуючих токенів у `Matching Store` зростає експоненційно. У фізичному кристалі місткість асоціативної пам'яті обмежена. 

Для розв'язання цієї проблеми в архітектурах потоку даних застосовують схему обмеженого розгортання (*k-bounded loops*): спеціальний лічильник токенів дозволяє генератору циклу випереджати найповільніший вузол не більше ніж на `k` ітерацій (зазвичай `k = 2...8`). Поки найстаріша активна ітерація не завершиться й не надішле сигнал-дозвіл (*ack token*), генератор нових ітерацій примусово блокується.

### 2. «Мертві» токени при незбалансованих розгалуженнях
Якщо в програмі є умовний оператор `if-else`, токен даних прямує лише в одну з двох гілок графа. Якщо розробник компілятора припустився помилки й оператор злиття (`MERGE`) продовжує очікувати токен з невиконаної гілки, цей вузол зависне назавжди, а залишкові операнди в `Matching Store` перетворяться на витік апаратних ресурсів (*dead token accumulation*). Це вимагає строгої дисципліни синтезу графів та апаратних механізмів очищення контекстів (*context garbage collection*), які примусово скидають усі слоти кадру активації після повернення з функції.

### 3. Порушення часової та просторової локальності кешу
У класичному процесорі фон Неймана цикли виконуються послідовно: `x[0]`, потім `x[1]`, потім `x[2]`. Це забезпечує ідеальну просторову локальність: лінія кешу L1 завантажує одразу 64 байти, і наступні кілька операцій читають дані безпосередньо з надшвидких комірок пам'яті. 

У чистій dataflow-машині обчислення розгортаються «вшир»: одночасно створюються сотні тисяч дрібних токенів для різних частин масиву. Звернення до пам'яті стають хаотичними, розмиваючи робочий набір даних і нівелюючи переваги кеш-пам'яті.

### 4. Накладні витрати серіалізації токенів у між'ядерних мережах
У багатоядерних розподілених dataflow-системах вихідний результат кожного вузла запаковується в мережевий пакет із повною адресою цільового вузла, порту та тегу. Якщо корисне навантаження — це одне 32-бітне число, а заголовок пакета займає ще 64–96 бітів, коефіцієнт корисної дії каналів зв'язку (*payload efficiency*) падає нижче 30%. Це вимагає об'єднання дрібних токенів у більші векторні пакети (*macro-dataflow*).

### 5. Ціна асоціативного пошуку в кремнії та перехід до просторових обчислень
У нашому C++ коді пошук у `Matching Store` реалізовано через `std::unordered_map` з амортизованою складністю `O(1)`. Проте в залізі будь-яка апаратна хеш-таблиця чи асоціативна пам'ять CAM вимагає складних компараторів, високих струмів і додаткових тактів затримки на кожне звернення.

Саме тому сучасні просторові AI-прискорювачі (як-от Google TPU, систолічні масиви чи чіпи Tenstorrent) відмовилися від повністю динамічного `Matching Store`: вони використовують **статично скомпільований, детермінований потік даних**. У таких архітектурах обчислювальний граф статично відображається на просторову сітку процесорних елементів (PE), а токени рухаються за жорстким розкладом такт у такт через локальні між'ядерні регістри, усуваючи будь-яку потребу в динамічному пошуку операндів.
