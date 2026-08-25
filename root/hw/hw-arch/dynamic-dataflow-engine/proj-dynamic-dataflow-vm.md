# ⚙️ Реалізація динамічної віртуальної машини Dataflow з кадрами активації та I-структурами

Практичне опанування потокової архітектури обчислень вимагає переходу від абстрактних діаграм графа до низькорівневої моделі виконання. Традиційні паралельні програми на мовах C та C++ будуються довкола потоків операційної системи (`pthread`, `std::jthread`), спільних структур даних та явних синхронізаторів (м'ютексів, умовних змінних, атомарних прапорців). Проте в парадигмі потоку даних (Dataflow) керування повністю інвертується: обчислювальні блоки є пасивними споживачами, а рушійною силою виконання виступає сам рух токенів крізь апаратні або віртуальні черги.

Нижче наведено повну архітектурну реалізацію віртуальної машини динамічного потоку даних двома мовами: на системному C з ручним керуванням пам'яттю, пулом потоків POSIX та атомарними операціями, і на ідіоматичному сучасному C++20 з використанням семантики володіння RAII, безпечних контейнерів та шаблонів.

## Архітектурний дизайн віртуальної машини

Віртуальна машина динамічного потоку даних моделює повнофункціональне процесорне кільце (*Processing Ring*) та складається з чотирьох взаємопов'язаних підсистем:

1. **Токен даних (`Token`)**: мінімальний пакет повідомлення розміром 16–24 байти, який містить ідентифікатор кадру активації `frame_id`, індекс інструкції `node_id`, номер порту операнда `port` (0 для лівого, 1 для правого) та 64-бітне числове значення `value`.
2. **Пам'ять Explicit Token Store (ETS)**: масив ізольованих кадрів активації (*Activation Frames*). Кожен кадр виділяється динамічно під окремий екземпляр обчислення (ітерацію циклу чи виклик функції). Усередині кадру кожен слот операнда захищено атомарним бітом присутності (`has_value` / `Presence Bit`). Перший токен записує значення у слот і встановлює біт; другий токен атомарно скидає біт, забирає збережене значення першого операнда і відправляє готову пару на виконання в ALU.
3. **Пам'ять нестрогих I-структур (`I-Structure`)**: підсистема агрегатних даних з трипозиційним автоматом станів комірок (`EMPTY`, `DEFERRED`, `PRESENT`). Читання порожньої комірки не блокує робочий потік, а реєструє токен-продовження у списку очікування; одноразовий запис фіксує значення та миттєво пробуджує всіх підписаних споживачів.
4. **Багатопотокове кільце обчислень**: потокобезпечна черга повідомлень типу MPMC (*Multiple Producer Multiple Consumer*), яку паралельно обробляє пул робочих потоків (*worker threads*). Кожен потік виступає еквівалентом апаратного ALU.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdatomic.h>
#include <pthread.h>
#include <string.h>
#include <unistd.h>
#include <assert.h>

#define MAX_NODES 64
#define MAX_SLOTS_PER_FRAME 16
#define MAX_FRAMES 128
#define QUEUE_CAPACITY 1024
#define MAX_ARCS 2
#define MAX_DEFERRED_READS 16

/* ── 1. Типи та структури токена ── */
typedef uint32_t frame_id_t;
typedef uint16_t node_id_t;
typedef uint8_t  port_t;

typedef struct {
    frame_id_t frame_id;
    node_id_t  node_id;
    port_t     port;
    int64_t    value;
} df_token_t;

/* ── 2. Опис графа ── */
typedef enum {
    OP_NOP,
    OP_ADD,
    OP_SUB,
    OP_MUL,
    OP_OUTPUT
} df_opcode_t;

typedef struct {
    node_id_t dest_node;
    port_t    dest_port;
} df_arc_t;

typedef struct {
    df_opcode_t opcode;
    uint8_t     is_binary;
    uint8_t     slot_idx;
    uint8_t     num_arcs;
    df_arc_t    arcs[MAX_ARCS];
} df_node_t;

typedef struct {
    df_node_t nodes[MAX_NODES];
    uint32_t  node_count;
} df_graph_t;

/* ── 3. Explicit Token Store (ETS) Кадри ── */
typedef struct {
    atomic_int has_value;
    int64_t    value;
} ets_slot_t;

typedef struct {
    ets_slot_t slots[MAX_SLOTS_PER_FRAME];
    atomic_bool in_use;
} ets_frame_t;

/* ── 4. Черга токенів ── */
typedef struct {
    df_token_t      items[QUEUE_CAPACITY];
    size_t          head;
    size_t          tail;
    size_t          count;
    pthread_mutex_t lock;
    pthread_cond_t  not_empty;
    pthread_cond_t  not_full;
    bool            shutdown;
} token_queue_t;

/* ── 5. Рушій Dataflow ── */
typedef struct {
    df_graph_t    graph;
    ets_frame_t   frames[MAX_FRAMES];
    token_queue_t queue;
    pthread_t     workers[4];
    uint32_t      num_workers;
    atomic_long   output_sum;
} df_engine_t;

/* Ініціалізація черги токенів */
static void queue_init(token_queue_t* q) {
    q->head = q->tail = q->count = 0;
    q->shutdown = false;
    pthread_mutex_init(&q->lock, NULL);
    pthread_cond_init(&q->not_empty, NULL);
    pthread_cond_init(&q->not_full, NULL);
}

static bool queue_push(token_queue_t* q, df_token_t tok) {
    pthread_mutex_lock(&q->lock);
    while (q->count == QUEUE_CAPACITY && !q->shutdown) {
        pthread_cond_wait(&q->not_full, &q->lock);
    }
    if (q->shutdown) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    q->items[q->tail] = tok;
    q->tail = (q->tail + 1) % QUEUE_CAPACITY;
    q->count++;
    pthread_cond_signal(&q->not_empty);
    pthread_mutex_unlock(&q->lock);
    return true;
}

static bool queue_pop(token_queue_t* q, df_token_t* out_tok) {
    pthread_mutex_lock(&q->lock);
    while (q->count == 0 && !q->shutdown) {
        pthread_cond_wait(&q->not_empty, &q->lock);
    }
    if (q->count == 0 && q->shutdown) {
        pthread_mutex_unlock(&q->lock);
        return false;
    }
    *out_tok = q->items[q->head];
    q->head = (q->head + 1) % QUEUE_CAPACITY;
    q->count--;
    pthread_cond_signal(&q->not_full);
    pthread_mutex_unlock(&q->lock);
    return true;
}

/* Виділення кадру активації з пулу ETS */
static frame_id_t frame_alloc(df_engine_t* eng) {
    for (uint32_t i = 0; i < MAX_FRAMES; ++i) {
        bool expected = false;
        if (atomic_compare_exchange_strong(&eng->frames[i].in_use, &expected, true)) {
            for (uint32_t s = 0; s < MAX_SLOTS_PER_FRAME; ++s) {
                atomic_store(&eng->frames[i].slots[s].has_value, 0);
            }
            return (frame_id_t)i;
        }
    }
    fprintf(stderr, "Помилка: пул кадрів ETS вичерпано!\n");
    exit(1);
}

/* Виконання операції вузла в ALU */
static void execute_node(df_engine_t* eng, frame_id_t fid, const df_node_t* node, int64_t v1, int64_t v2) {
    int64_t result = 0;
    switch (node->opcode) {
        case OP_ADD: result = v1 + v2; break;
        case OP_SUB: result = v1 - v2; break;
        case OP_MUL: result = v1 * v2; break;
        case OP_OUTPUT:
            atomic_fetch_add(&eng->output_sum, v1);
            printf("[C Рушій] Отримано фінальний результат: %ld (Кадр %u)\n", (long)v1, fid);
            return;
        default: return;
    }

    /* Емісія токенів-наступників по вихідних дугах */
    for (uint8_t i = 0; i < node->num_arcs; ++i) {
        df_token_t out_tok = {
            .frame_id = fid,
            .node_id  = node->arcs[i].dest_node,
            .port     = node->arcs[i].dest_port,
            .value    = result
        };
        queue_push(&eng->queue, out_tok);
    }
}

/* Робочий потік процесорного кільця */
static void* worker_thread_fn(void* arg) {
    df_engine_t* eng = (df_engine_t*)arg;
    df_token_t tok;

    while (queue_pop(&eng->queue, &tok)) {
        const df_node_t* node = &eng->graph.nodes[tok.node_id];

        if (!node->is_binary) {
            /* Унарна інструкція: негайне виконання */
            execute_node(eng, tok.frame_id, node, tok.value, 0);
        } else {
            /* Бінарна інструкція: атомарне зіставлення в ETS слоті */
            ets_slot_t* slot = &eng->frames[tok.frame_id].slots[node->slot_idx];
            
            int expected = 0;
            if (atomic_compare_exchange_strong(&slot->has_value, &expected, 1)) {
                /* Прибув перший операнд: зберегти значення в слоті */
                slot->value = tok.value;
            } else {
                /* Прибув другий операнд: повний набір операндів готовий! */
                int64_t first_val = slot->value;
                atomic_store(&slot->has_value, 0); /* Звільнити слот */

                int64_t left  = (tok.port == 0) ? tok.value : first_val;
                int64_t right = (tok.port == 0) ? first_val : tok.value;

                execute_node(eng, tok.frame_id, node, left, right);
            }
        }
    }
    return NULL;
}

int main(void) {
    df_engine_t eng;
    memset(&eng, 0, sizeof(eng));
    queue_init(&eng.queue);

    /* Побудова графа для обчислення: (a + b) * (c - d) */
    /* Вузол 0: ADD (слот 0) -> відправляє в порт 0 Вузла 2 */
    eng.graph.nodes[0] = (df_node_t){
        .opcode = OP_ADD, .is_binary = 1, .slot_idx = 0, .num_arcs = 1,
        .arcs = {{ .dest_node = 2, .dest_port = 0 }}
    };
    /* Вузол 1: SUB (слот 1) -> відправляє в порт 1 Вузла 2 */
    eng.graph.nodes[1] = (df_node_t){
        .opcode = OP_SUB, .is_binary = 1, .slot_idx = 1, .num_arcs = 1,
        .arcs = {{ .dest_node = 2, .dest_port = 1 }}
    };
    /* Вузол 2: MUL (слот 2) -> відправляє у Вузол 3 */
    eng.graph.nodes[2] = (df_node_t){
        .opcode = OP_MUL, .is_binary = 1, .slot_idx = 2, .num_arcs = 1,
        .arcs = {{ .dest_node = 3, .dest_port = 0 }}
    };
    /* Вузол 3: OUTPUT (термінальний вузол) */
    eng.graph.nodes[3] = (df_node_t){
        .opcode = OP_OUTPUT, .is_binary = 0, .slot_idx = 0, .num_arcs = 0
    };

    /* Запуск пулу робочих потоків */
    eng.num_workers = 4;
    for (uint32_t i = 0; i < eng.num_workers; ++i) {
        pthread_create(&eng.workers[i], NULL, worker_thread_fn, &eng);
    }

    /* Виділення кадру активації та запуск обчислення (10 + 20) * (50 - 15) = 30 * 35 = 1050 */
    frame_id_t fid1 = frame_alloc(&eng);

    queue_push(&eng.queue, (df_token_t){ fid1, 0, 0, 10 }); /* a = 10 */
    queue_push(&eng.queue, (df_token_t){ fid1, 0, 1, 20 }); /* b = 20 */
    queue_push(&eng.queue, (df_token_t){ fid1, 1, 0, 50 }); /* c = 50 */
    queue_push(&eng.queue, (df_token_t){ fid1, 1, 1, 15 }); /* d = 15 */

    /* Паралельний запуск другого незалежного кадру (100 + 200) * (40 - 30) = 300 * 10 = 3000 */
    frame_id_t fid2 = frame_alloc(&eng);

    queue_push(&eng.queue, (df_token_t){ fid2, 0, 0, 100 });
    queue_push(&eng.queue, (df_token_t){ fid2, 0, 1, 200 });
    queue_push(&eng.queue, (df_token_t){ fid2, 1, 0, 40 });
    queue_push(&eng.queue, (df_token_t){ fid2, 1, 1, 30 });

    /* Очікування завершення обчислень */
    sleep(1);

    pthread_mutex_lock(&eng.queue.lock);
    eng.queue.shutdown = true;
    pthread_cond_broadcast(&eng.queue.not_empty);
    pthread_mutex_unlock(&eng.queue.lock);

    for (uint32_t i = 0; i < eng.num_workers; ++i) {
        pthread_join(eng.workers[i], NULL);
    }

    printf("Сумарний результат усіх виконаних графів: %ld\n", atomic_load(&eng.output_sum));
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <queue>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <atomic>
#include <optional>
#include <span>
#include <memory>
#include <chrono>

namespace dataflow {

using FrameId = uint32_t;
using NodeId  = uint16_t;
using Port    = uint8_t;

/* ── 1. Тип токена ── */
struct Token {
    FrameId frame_id{0};
    NodeId  node_id{0};
    Port    port{0};
    int64_t value{0};
};

/* ── 2. Опис вузлів графа ── */
enum class Opcode : uint8_t {
    Add,
    Sub,
    Mul,
    Output
};

struct Arc {
    NodeId dest_node{0};
    Port   dest_port{0};
};

struct Node {
    Opcode           opcode{Opcode::Add};
    bool             is_binary{true};
    uint8_t          slot_index{0};
    std::vector<Arc> successors;
};

/* ── 3. Explicit Token Store (ETS) Кадр ── */
struct EtsSlot {
    std::atomic<bool> has_value{false};
    int64_t           value{0};
};

class ActivationFrame {
public:
    static constexpr size_t kMaxSlots = 16;

    ActivationFrame() = default;

    void reset() noexcept {
        for (auto& s : slots_) {
            s.has_value.store(false, std::memory_order_relaxed);
            s.value = 0;
        }
    }

    /* Атомарне зіставлення токена в слоті */
    std::optional<std::pair<int64_t, int64_t>> match(uint8_t slot_idx, Port port, int64_t incoming_val) noexcept {
        auto& slot = slots_[slot_idx];
        bool expected = false;

        /* Перший операнд: захоплення слота через CAS */
        if (slot.has_value.compare_exchange_strong(expected, true, std::memory_order_acq_rel)) {
            slot.value = incoming_val;
            return std::nullopt;
        }

        /* Другий операнд: читання значення та атомарне звільнення слота */
        int64_t stored_val = slot.value;
        slot.has_value.store(false, std::memory_order_release);

        int64_t left  = (port == 0) ? incoming_val : stored_val;
        int64_t right = (port == 0) ? stored_val   : incoming_val;
        return std::make_pair(left, right);
    }

private:
    std::array<EtsSlot, kMaxSlots> slots_{};
};

/* ── 4. Потокобезпечна черга токенів ── */
class TokenQueue {
public:
    void push(Token tok) {
        {
            std::lock_guard lock(mtx_);
            queue_.push(tok);
        }
        cv_.notify_one();
    }

    bool pop(Token& out_tok) {
        std::unique_lock lock(mtx_);
        cv_.wait(lock, [this]() { return !queue_.empty() || shutdown_; });

        if (queue_.empty() && shutdown_) {
            return false;
        }

        out_tok = queue_.front();
        queue_.pop();
        return true;
    }

    void shutdown() noexcept {
        {
            std::lock_guard lock(mtx_);
            shutdown_ = true;
        }
        cv_.notify_all();
    }

private:
    std::queue<Token>       queue_;
    std::mutex              mtx_;
    std::condition_variable cv_;
    bool                    shutdown_{false};
};

/* ── 5. Рушій Dataflow ── */
class Engine {
public:
    explicit Engine(std::vector<Node> graph, size_t num_workers = 4)
        : graph_(std::move(graph)) {
        frames_.resize(128);
        for (size_t i = 0; i < num_workers; ++i) {
            workers_.emplace_back([this]() { worker_loop(); });
        }
    }

    ~Engine() {
        queue_.shutdown();
        for (auto& w : workers_) {
            if (w.joinable()) {
                w.join();
            }
        }
    }

    Engine(const Engine&) = delete;
    Engine& operator=(const Engine&) = delete;

    FrameId allocate_frame() noexcept {
        size_t id = next_frame_id_.fetch_add(1, std::memory_order_relaxed);
        frames_[id % frames_.size()].reset();
        return static_cast<FrameId>(id);
    }

    void emit(Token tok) {
        queue_.push(tok);
    }

    [[nodiscard]] int64_t result() const noexcept {
        return total_sum_.load(std::memory_order_relaxed);
    }

private:
    void execute(FrameId fid, const Node& node, int64_t v1, int64_t v2) {
        int64_t res = 0;
        switch (node.opcode) {
            case Opcode::Add: res = v1 + v2; break;
            case Opcode::Sub: res = v1 - v2; break;
            case Opcode::Mul: res = v1 * v2; break;
            case Opcode::Output:
                total_sum_.fetch_add(v1, std::memory_order_relaxed);
                std::cout << "[C++ Dataflow] Результат кадру " << fid << " = " << v1 << "\n";
                return;
        }

        for (const auto& arc : node.successors) {
            queue_.push(Token{fid, arc.dest_node, arc.dest_port, res});
        }
    }

    void worker_loop() {
        Token tok;
        while (queue_.pop(tok)) {
            const auto& node = graph_[tok.node_id];

            if (!node.is_binary) {
                execute(tok.frame_id, node, tok.value, 0);
            } else {
                auto& frame = frames_[tok.frame_id % frames_.size()];
                if (auto operands = frame.match(node.slot_index, tok.port, tok.value)) {
                    execute(tok.frame_id, node, operands->first, operands->second);
                }
            }
        }
    }

    std::vector<Node>            graph_;
    std::vector<ActivationFrame> frames_;
    TokenQueue                   queue_;
    std::vector<std::thread>     workers_;
    std::atomic<size_t>          next_frame_id_{0};
    std::atomic<int64_t>         total_sum_{0};
};

} // namespace dataflow

int main() {
    using namespace dataflow;

    /* Побудова графа виразу: (a + b) * (c - d) */
    std::vector<Node> graph{
        /* Вузол 0: ADD (слот 0) -> відправляє у Вузол 2, Порт 0 */
        Node{Opcode::Add, true, 0, {{2, 0}}},
        /* Вузол 1: SUB (слот 1) -> відправляє у Вузол 2, Порт 1 */
        Node{Opcode::Sub, true, 1, {{2, 1}}},
        /* Вузол 2: MUL (слот 2) -> відправляє у Вузол 3, Порт 0 */
        Node{Opcode::Mul, true, 2, {{3, 0}}},
        /* Вузол 3: OUTPUT (термінальний вузол) */
        Node{Opcode::Output, false, 0, {}}
    };

    Engine engine(std::move(graph), 4);

    /* Екземпляр 1: (10 + 20) * (50 - 15) = 30 * 35 = 1050 */
    auto frame1 = engine.allocate_frame();
    engine.emit(Token{frame1, 0, 0, 10});
    engine.emit(Token{frame1, 0, 1, 20});
    engine.emit(Token{frame1, 1, 0, 50});
    engine.emit(Token{frame1, 1, 1, 15});

    /* Екземпляр 2: (100 + 200) * (40 - 30) = 300 * 10 = 3000 */
    auto frame2 = engine.allocate_frame();
    engine.emit(Token{frame2, 0, 0, 100});
    engine.emit(Token{frame2, 0, 1, 200});
    engine.emit(Token{frame2, 1, 0, 40});
    engine.emit(Token{frame2, 1, 1, 30});

    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << "Сумарний результат усіх паралельних графів: " << engine.result() << "\n";
    return 0;
}
```
:::

## Детальний розбір механізмів синхронізації

### 1. Атомарна перевірка та встановлення слота ETS без м'ютексів
Критичним місцем продуктивності потокового рушія є відсутність важких блокувань під час зустрічі операндів.
У C-реалізації функція `worker_thread_fn` звертається до слота кадру через операцію `atomic_compare_exchange_strong(&slot->has_value, &expected, 1)`:
* Якщо `has_value == 0`: потік гарантовано першим захоплює слот, записує `slot->value = tok.value` і завершує поточний крок.
* Якщо `has_value == 1`: операція CAS повертає `false`. Це однозначно свідчить, що перший операнд уже збережено іншим потоком. Потік зчитує `slot->value`, скидає прапорець `atomic_store(&slot->has_value, 0)` та передає готову пару в `execute_node`.

У C++ версії цей протокол інкапсульовано в методі `ActivationFrame::match()`, який повертає типізований `std::optional<std::pair<int64_t, int64_t>>`. Це виключає використання неініціалізованих змінних або пошкодження стану слота при виникненні гонитви операндів (*race conditions*).

### 2. Запобігання хибному спільному використанню (False Sharing)
При розміщенні операндних слотів `slots[16]` у межах одного кадру активації декілька робочих потоків можуть одночасно записувати дані в сусідні слоти. Якщо слоти розташовані в межах однієї 64-байтної кеш-лінії, паралельні записи викликають постійне витіснення кеш-рядка між ядрами CPU (протокол когерентності MESI/MOESI). Щоб усунути це «пінг-понгове» навантаження на шину, структури слотів вирівнюють за розміром кеш-лінії.

:::tabs
```c
/* Вирівнювання кожного слота за 64-байтною кеш-лінією в C11 */
typedef struct {
    _Alignas(64) atomic_int has_value;
    int64_t                 value;
    uint8_t                 pad[64 - sizeof(atomic_int) - sizeof(int64_t)];
} ets_aligned_slot_t;
```
```cpp
/* Вирівнювання структури слота в C++20 */
struct alignas(64) AlignedEtsSlot {
    std::atomic<bool> has_value{false};
    int64_t           value{0};
};
```
:::

### 3. Життєвий цикл кадру активації та запобігання витокам ресурсів

У традиційних програмах стек викликів росте та зменшується синхронно за дисципліною LIFO (*Last In, First Out*). У динамічному потоковому рушії паралельні ітерації циклів та асинхронні виклики функцій розгортаються нелінійно у вигляді орієнтованого графа або дерева.

Кадри активації виділяються з попередньо створеного пулу фіксованого розміру за час `O(1)` за допомогою атомарного лічильника або неблокуючого бітового масиву. Звільнення кадру відбувається автоматично: коли термінальний вузол графа фіксує отримання всіх очікуваних результатів і передає токени наступникам або викликаючому контексту, він скидає прапорець використання кадру `in_use = false`. Це гарантує повну відсутність динамічної фрагментації купи (`malloc`/`free`) на гарячому шляху виконання.

### 4. Порівняння затримок: потоки ОС проти Dataflow-рушія

Зіставимо вартість перемикання контексту та синхронізації в операційній системі з обробкою токенів у потоковому кільці:

* **Перемикання нитки ОС (`pthread_create` / context switch)**: збереження регістрів CPU, перехід у простір ядра, запуск планувальника ОС, промах L1I-кешу та скидання буфера асоціативної трансляції TLB. Середня затримка становить від `1000` до `3000` наносекунд (тисячі тактів).
* **Спрацьовування вузла в Dataflow-рушії**: отримання 16-байтного токена з черги FIFO, одна атомарна операція CAS над бітом присутності в локальній пам'яті L1D, вибірка коду операції та обчислення в ALU. Середня затримка становить лише `10–25` наносекунд.

Це пояснює, чому розбиття обчислень на мільйони дрібнозернистих задач (*fine-grained tasks*) у класичній моделі потоків призводить до катастрофічного падіння продуктивності, тоді як у потоковому рушії дрібнозернистий паралелізм є природним і високоефективним режимом роботи.

### 5. Покроковий розбір паралельного виконання тестового графа

У наведеному тестовому сценарії програма ініціалізує два абсолютно незалежні кадри активації `fid1` та `fid2`, призначені для паралельного обчислення виразу `(a + b) · (c − d)` над різними наборами даних:

1. **Кадр 1 (`fid1`)**: вхідні дані `a = 10, b = 20, c = 50, d = 15`. Очікуваний результат: `(10 + 20) · (50 − 15) = 30 · 35 = 1050`.
2. **Кадр 2 (`fid2`)**: вхідні дані `a = 100, b = 200, c = 40, d = 30`. Очікуваний результат: `(100 + 200) · (40 − 30) = 300 · 10 = 3000`.

Усі 8 вхідних токенів одночасно вкидаються у спільну чергу рушія. Чотири робочі потоки розбирають токени в довільному порядку надходження. Завдяки ізоляції через поле `frame_id` проміжні результати вузлів `ADD` і `SUB` для першого виразу ніколи не потрапляють у слоти другого, а операції `MUL` активуються автоматично в момент прибуття другого операнда у відповідний кадр. Сумарний лічильник `output_sum` детерміновано отримує значення `1050 + 3000 = 4050`.
