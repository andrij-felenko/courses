# ⚙️ Симулятор розподіленого регістра з моделями Linearizable, Causal та Eventual

Розподілене сховище даних мусить надавати розробнику чіткий контракт: що саме поверне операція читання `read(key)`, якщо просто зараз інший клієнт на іншому континенті виконує `write(key, value)`.

Коли застосунок працює з локальною пам'яттю одного комп'ютера, операція читання завжди повертає результат найближчого попереднього запису. У розподіленій системі кожна репліка володіє власною локальною копією стану, а повідомлення між вузлами проходять через ненадійні мережеві маршрутизатори, затримуються в чергах операційної системи та можуть змінювати послідовність доставки. Без формального механізму впорядкування стан реплік неминуче розходиться, породжуючи аномалії застарілих читань, втрачених оновлень та розриву причинно-наслідкових зв'язків.

Щоб дослідити різницю між ключовими точками спектру консистентності на практиці, створимо модульний симулятор кластера з трьох повнофункціональних вузлів-реплік. Симулятор моделює передачу повідомлень, облік фізичного часу та дозволяє динамічно перемикати фундаментальні протоколи узгодження:
1. **Linearizable (Лінеаризовний):** операції запису та читання проходять через строгий кворум більшості (Majority Quorum `W + R > N`). Читання гарантовано повертає найсвіжіший підтверджений запис у реальному часі без можливості спостереження відкату стану назад.
2. **Causal (Причинний):** репліки обмінюються оновленнями асинхронно, прикріплюючи до кожного повідомлення векторний годинник (Vector Clock). Якщо репліка отримує повідомлення, чиї причинні залежності ще не надійшли через мережеву затримку, вона буферизує його в оперативній пам'яті до прибуття всіх попередніх змін.
3. **Eventual (Кінцева узгодженість):** репліки негайно застосовують локальні записи й розсилають їх без контролю порядку; конфлікти одночасних оновлень розв'язуються детерміністичним правилом Last-Write-Wins (LWW) за фізичними часовими мітками.

## Математична логіка векторних годинників та причинної готовності

Для забезпечення причинної консистентності кожен вузол `i` підтримує вектор цілих чисел `V` розмірності `N` (де `N` — загальна кількість реплік у кластері):
- Компонент `V[i]` позначає кількість локальних операцій запису, згенерованих безпосередньо вузлом `i`.
- Компонент `V[k]` (де `k ≠ i`) відображає кількість оновлень від вузла `k`, які вузол `i` вже успішно отримав і застосував до свого стану.

Коли вузол `i` генерує новий запис, він інкрементує свій лічильник `V[i] = V[i] + 1` і відправляє повідомлення `m`, прикріплюючи до нього копію свого оновленого вектора `m.vc = V`.

Коли віддалений вузол `j` отримує повідомлення `m` від вузла `origin`, він не має права застосувати його негайно, якщо повідомлення спирається на проміжні події, про які вузол `j` ще не знає. Функція перевірки причинної готовності `vc_is_causally_ready(msg_vc, node_vc, origin)` перевіряє виконання двох обов'язкових умов:

```
1. msg_vc[origin] == node_vc[origin] + 1   [подія є строго наступною від цього автора]
2. ∀ k ≠ origin: msg_vc[k] ≤ node_vc[k]     [усі причинні залежності вже застосовані]
```

Якщо хоча б для одного індексу `k` значення `msg_vc[k] > node_vc[k]`, це свідчить про наявність пропущеного повідомлення від вузла `k`, яке автор запису вже бачив, а поточний вузол `j` — ще ні. У такому разі повідомлення `m` поміщається в чергу відкладеної доставки (Causal Buffer). Як тільки пропущене повідомлення надходить і оновлює `node_vc`, алгоритм повторно сканує буфер і каскадно розблоковує всі операції, чиї залежності нарешті закрилися.

Векторні годинники також дозволяють однозначно розпізнавати та класифікувати конкурентні оновлення стану:
- `V₁ < V₂` (подія `V₁` причинно передує `V₂`): для всіх компонентів `k` виконується `V₁[k] ≤ V₂[k]` і гарантовано існує хоча б один індекс `m`, де `V₁[m] < V₂[m]`.
- `V₁ || V₂` (події є строго конкурентними): не виконується ані відношення `V₁ ≤ V₂`, ані відношення `V₂ ≤ V₁`. Це математично доводить, що записи виникли незалежно на різних репліках без взаємного впливу та узгодження.

## Реалізація симулятора

Нижче наведено паралельну реалізацію розподіленого симулятора мовами C та сучасним C++20. Обидва варіанти демонструють обробку станів, протоколи реплікації та роботу з буфером причинності.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define MAX_NODES 3
#define MAX_BUFFER 16

typedef enum {
    CONSISTENCY_LINEARIZABLE,
    CONSISTENCY_CAUSAL,
    CONSISTENCY_EVENTUAL
} consistency_mode_t;

typedef struct {
    uint32_t clock[MAX_NODES];
} vector_clock_t;

typedef struct {
    int value;
    uint64_t timestamp;
    vector_clock_t vc;
    int origin_node;
} register_entry_t;

typedef struct {
    int id;
    register_entry_t current;
    register_entry_t buffer[MAX_BUFFER];
    int buffer_count;
} replica_node_t;

typedef struct {
    replica_node_t nodes[MAX_NODES];
    consistency_mode_t mode;
    uint64_t physical_timer;
} cluster_t;

static void vc_init(vector_clock_t *vc) {
    memset(vc->clock, 0, sizeof(vc->clock));
}

static bool vc_is_causally_ready(const vector_clock_t *msg_vc, const vector_clock_t *node_vc, int origin) {
    /* Повідомлення готове до застосування, якщо:
       1. Подія від origin є строго наступною: msg_vc[origin] == node_vc[origin] + 1
       2. Для всіх інших вузлів k: msg_vc[k] <= node_vc[k] */
    if (msg_vc->clock[origin] != node_vc->clock[origin] + 1) {
        return false;
    }
    for (int i = 0; i < MAX_NODES; ++i) {
        if (i != origin && msg_vc->clock[i] > node_vc->clock[i]) {
            return false;
        }
    }
    return true;
}

static void cluster_init(cluster_t *c, consistency_mode_t mode) {
    c->mode = mode;
    c->physical_timer = 100;
    for (int i = 0; i < MAX_NODES; ++i) {
        c->nodes[i].id = i;
        c->nodes[i].current.value = 0;
        c->nodes[i].current.timestamp = 0;
        c->nodes[i].current.origin_node = -1;
        vc_init(&c->nodes[i].current.vc);
        c->nodes[i].buffer_count = 0;
    }
}

/* Запис значення у кластер */
static void cluster_write(cluster_t *c, int target_node, int value) {
    replica_node_t *node = &c->nodes[target_node];
    c->physical_timer += 10;
    node->current.value = value;
    node->current.timestamp = c->physical_timer;
    node->current.origin_node = target_node;
    node->current.vc.clock[target_node]++;

    printf("[WRITE] Вузол %d: запис value=%d (VC: [%u, %u, %u], t=%llu)\n",
           target_node, value,
           node->current.vc.clock[0],
           node->current.vc.clock[1],
           node->current.vc.clock[2],
           (unsigned long long)node->current.timestamp);

    if (c->mode == CONSISTENCY_LINEARIZABLE) {
        /* Строгий синхронний кворум: миттєва реплікація на більшість вузлів */
        for (int i = 0; i < MAX_NODES; ++i) {
            c->nodes[i].current = node->current;
        }
        printf("  -> [Кворум W=3] Стан синхронізовано на всі вузли.\n");
    }
}

/* Асинхронне надходження повідомлення реплікації */
static void cluster_deliver_replication(cluster_t *c, int to_node, register_entry_t entry) {
    replica_node_t *dest = &c->nodes[to_node];

    if (c->mode == CONSISTENCY_EVENTUAL) {
        /* Last-Write-Wins за фізичною часовою міткою */
        if (entry.timestamp >= dest->current.timestamp) {
            dest->current = entry;
            printf("[EVENTUAL DELIVER] Вузол %d застосував value=%d (t=%llu)\n",
                   to_node, entry.value, (unsigned long long)entry.timestamp);
        } else {
            printf("[EVENTUAL DROP] Вузол %d відкинув старіший запис value=%d (t=%llu < %llu)\n",
                   to_node, entry.value, (unsigned long long)entry.timestamp,
                   (unsigned long long)dest->current.timestamp);
        }
        return;
    }

    if (c->mode == CONSISTENCY_CAUSAL) {
        /* Перевірка готовності векторного годинника */
        if (vc_is_causally_ready(&entry.vc, &dest->current.vc, entry.origin_node)) {
            dest->current.value = entry.value;
            dest->current.timestamp = entry.timestamp;
            dest->current.vc.clock[entry.origin_node] = entry.vc.clock[entry.origin_node];
            printf("[CAUSAL DELIVER] Вузол %d застосував value=%d (Новий VC: [%u, %u, %u])\n",
                   to_node, entry.value,
                   dest->current.vc.clock[0],
                   dest->current.vc.clock[1],
                   dest->current.vc.clock[2]);

            /* Спроба розблокувати відкладені повідомлення з буфера */
            bool progressed = true;
            while (progressed) {
                progressed = false;
                for (int b = 0; b < dest->buffer_count; ++b) {
                    register_entry_t buf_e = dest->buffer[b];
                    if (vc_is_causally_ready(&buf_e.vc, &dest->current.vc, buf_e.origin_node)) {
                        dest->current.value = buf_e.value;
                        dest->current.timestamp = buf_e.timestamp;
                        dest->current.vc.clock[buf_e.origin_node] = buf_e.vc.clock[buf_e.origin_node];
                        printf("  -> [CAUSAL UNBUFFER] Вузол %d розблокував із буфера value=%d\n",
                               to_node, buf_e.value);

                        /* Видалення з буфера */
                        dest->buffer[b] = dest->buffer[dest->buffer_count - 1];
                        dest->buffer_count--;
                        progressed = true;
                        break;
                    }
                }
            }
        } else {
            /* Причинні залежності ще не надійшли: буферизуємо */
            if (dest->buffer_count < MAX_BUFFER) {
                dest->buffer[dest->buffer_count++] = entry;
                printf("[CAUSAL BUFFER] Вузол %d відклав value=%d у буфер (очікує попередні події)\n",
                       to_node, entry.value);
            }
        }
    }
}

/* Читання значення з вузла */
static int cluster_read(const cluster_t *c, int target_node) {
    const replica_node_t *node = &c->nodes[target_node];
    printf("[READ] Читання з Вузла %d -> value=%d (VC: [%u, %u, %u])\n",
           target_node, node->current.value,
           node->current.vc.clock[0],
           node->current.vc.clock[1],
           node->current.vc.clock[2]);
    return node->current.value;
}

int main(void) {
    cluster_t sim;

    printf("=== 1. ТЕСТ ПРИЧИННОЇ КОНСИСТЕНТНОСТІ (Causal Consistency) ===\n");
    cluster_init(&sim, CONSISTENCY_CAUSAL);

    /* Аліса на Вузлі 0 пише пост (value=10) */
    cluster_write(&sim, 0, 10);
    register_entry_t post_alice = sim.nodes[0].current;

    /* Боб на Вузлі 1 зчитує пост Аліси через реплікацію та пише відповідь (value=20) */
    cluster_deliver_replication(&sim, 1, post_alice);
    cluster_write(&sim, 1, 20);
    register_entry_t reply_bob = sim.nodes[1].current;

    /* Повідомлення Боба (reply_bob) прибуває на Вузол 2 РАНІШЕ за пост Аліси (перевпорядкування в мережі) */
    printf("\n--- Мережевий збій: відповідь Боба прибула на Вузол 2 раніше за пост Аліси ---\n");
    cluster_deliver_replication(&sim, 2, reply_bob);
    cluster_read(&sim, 2); /* Має повернути 0, бо відповідь заблокована в буфері */

    /* Тепер до Вузла 2 нарешті доходить пост Аліси */
    printf("\n--- Пост Аліси нарешті дійшов до Вузла 2 ---\n");
    cluster_deliver_replication(&sim, 2, post_alice);
    cluster_read(&sim, 2); /* Має автоматично розблокувати відповідь Боба й повернути 20 */

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <array>
#include <optional>
#include <algorithm>
#include <cstdint>

namespace dist {

inline constexpr size_t NodeCount = 3;

enum class ConsistencyMode {
    Linearizable,
    Causal,
    Eventual
};

struct VectorClock {
    std::array<uint32_t, NodeCount> clock{};

    [[nodiscard]] bool isCausallyReady(const VectorClock& nodeVc, size_t origin) const noexcept {
        if (clock[origin] != nodeVc.clock[origin] + 1) {
            return false;
        }
        for (size_t i = 0; i < NodeCount; ++i) {
            if (i != origin && clock[i] > nodeVc.clock[i]) {
                return false;
            }
        }
        return true;
    }
};

struct RegisterEntry {
    int value{0};
    uint64_timestamp{0};
    VectorClock vc{};
    size_t originNode{0};
};

class ClusterSimulator {
public:
    explicit ClusterSimulator(ConsistencyMode mode) noexcept
        : mode_{mode} {}

    void write(size_t targetNode, int value) {
        timer_ += 10;
        auto& node = nodes_[targetNode];
        node.current.value = value;
        node.current.timestamp = timer_;
        node.current.originNode = targetNode;
        node.current.vc.clock[targetNode]++;

        std::cout << "[WRITE] Вузол " << targetNode << ": value=" << value
                  << " (VC: [" << node.current.vc.clock[0] << ", "
                  << node.current.vc.clock[1] << ", "
                  << node.current.vc.clock[2] << "], t=" << timer_ << ")\n";

        if (mode_ == ConsistencyMode::Linearizable) {
            for (auto& n : nodes_) {
                n.current = node.current;
            }
            std::cout << "  -> [Кворум W=3] Синхронно зафіксовано на всіх вузлах.\n";
        }
    }

    void deliverReplication(size_t toNode, const RegisterEntry& entry) {
        auto& dest = nodes_[toNode];

        if (mode_ == ConsistencyMode::Eventual) {
            if (entry.timestamp >= dest.current.timestamp) {
                dest.current = entry;
                std::cout << "[EVENTUAL DELIVER] Вузол " << toNode
                          << " застосував value=" << entry.value << '\n';
            }
            return;
        }

        if (mode_ == ConsistencyMode::Causal) {
            if (entry.vc.isCausallyReady(dest.current.vc, entry.originNode)) {
                applyEntry(toNode, entry);
                drainBuffer(toNode);
            } else {
                dest.buffer.push_back(entry);
                std::cout << "[CAUSAL BUFFER] Вузол " << toNode
                          << " відклав value=" << entry.value << " (очікує залежності)\n";
            }
        }
    }

    [[nodiscard]] int read(size_t targetNode) const noexcept {
        const auto& node = nodes_[targetNode];
        std::cout << "[READ] Вузол " << targetNode << " -> value=" << node.current.value
                  << " (VC: [" << node.current.vc.clock[0] << ", "
                  << node.current.vc.clock[1] << ", "
                  << node.current.vc.clock[2] << "])\n";
        return node.current.value;
    }

    [[nodiscard]] const RegisterEntry& getEntry(size_t nodeIndex) const noexcept {
        return nodes_[nodeIndex].current;
    }

private:
    struct NodeState {
        RegisterEntry current{};
        std::vector<RegisterEntry> buffer{};
    };

    void applyEntry(size_t nodeId, const RegisterEntry& entry) {
        auto& node = nodes_[nodeId];
        node.current.value = entry.value;
        node.current.timestamp = entry.timestamp;
        node.current.vc.clock[entry.originNode] = entry.vc.clock[entry.originNode];
        std::cout << "[CAUSAL DELIVER] Вузол " << nodeId << " застосував value=" << entry.value
                  << " (Новий VC: [" << node.current.vc.clock[0] << ", "
                  << node.current.vc.clock[1] << ", "
                  << node.current.vc.clock[2] << "])\n";
    }

    void drainBuffer(size_t nodeId) {
        auto& dest = nodes_[nodeId];
        bool progressed = true;
        while (progressed) {
            progressed = false;
            for (auto it = dest.buffer.begin(); it != dest.buffer.end(); ++it) {
                if (it->vc.isCausallyReady(dest.current.vc, it->originNode)) {
                    RegisterEntry readyEntry = *it;
                    dest.buffer.erase(it);
                    std::cout << "  -> [CAUSAL UNBUFFER] Вузол " << nodeId
                              << " розблокував value=" << readyEntry.value << '\n';
                    applyEntry(nodeId, readyEntry);
                    progressed = true;
                    break;
                }
            }
        }
    }

    ConsistencyMode mode_;
    uint64_t timer_{100};
    std::array<NodeState, NodeCount> nodes_{};
};

} // namespace dist

int main() {
    using namespace dist;
    std::cout << "=== 1. ТЕСТ ПРИЧИННОЇ КОНСИСТЕНТНОСТІ (C++20) ===\n";
    ClusterSimulator sim{ConsistencyMode::Causal};

    sim.write(0, 10);
    RegisterEntry postAlice = sim.getEntry(0);

    sim.deliverReplication(1, postAlice);
    sim.write(1, 20);
    RegisterEntry replyBob = sim.getEntry(1);

    std::cout << "\n--- Мережевий збій: відповідь Боба прибула на Вузол 2 раніше за пост Аліси ---\n";
    sim.deliverReplication(2, replyBob);
    sim.read(2);

    std::cout << "\n--- Пост Аліси нарешті дійшов до Вузла 2 ---\n";
    sim.deliverReplication(2, postAlice);
    sim.read(2);

    return 0;
}
```
:::

## Глибокий інженерний розбір сценаріїв виконання

Продемонстрований у коді сценарій ілюструє класичну задачу синхронізації повідомлень у розподіленій стрічці коментарів:

1. **Ініціація причинного ланцюга (Подія A):**
   Користувачка Аліса на Вузлі 0 публікує вихідний запис `value = 10`. Вузол 0 генерує векторний годинник `[1, 0, 0]`. Цей вектор фіксує, що зміна створена на першому вузлі й не спирається на жодні попередні події інших реплік.
2. **Причинне успадкування (Подія B = f(A)):**
   Боб підключений до Вузла 1. Вузол 1 отримує повідомлення реплікації від Аліси. Оскільки вектор `[1, 0, 0]` задовольняє критерій `msg[0] == node[0] + 1`, Вузол 1 негайно застосовує його й оновлює локальний годинник до `[1, 0, 0]`.
   Прочитавши пост Аліси, Боб пише коментар-відповідь `value = 20`. Вузол 1 інкрементує свій лічильник і формує вектор `[1, 1, 0]`. Цей вектор несе в собі математичний доказ: запис Боба виник **після того й на основі того**, як на Вузлі 1 було зафіксовано першу подію Аліси.
3. **Мережева аномалія доставки:**
   Повідомлення від Боба (`VC: [1, 1, 0]`) передається швидким оптоволоконним маршрутом і досягає Вузла 2 (Керол) за 15 мілісекунд. Повідомлення Аліси (`VC: [1, 0, 0]`) застрягло в буфері перевантаженого комутатора й затримується на 120 мілісекунд.
4. **Поведінка різних моделей узгодженості:**
   - **У моделі Eventual (LWW):** Вузол 2 не аналізує причинні зв'язки. Він порівнює лише мітки часу, бачить, що повідомлення Боба має свіжий таймстемп `t = 120`, і негайно перезаписує стан. Коли через 100 мс приходить повідомлення Аліси з міткою `t = 110`, Вузол 2 вважає його застарілим і відкидає! Якщо цей регістр моделював створення теми та коментаря, тема Аліси буде втрачена назавжди, а коментар Боба зависне без батьківського контексту.
   - **У моделі Causal:** Вузол 2 викликає `vc_is_causally_ready`. Він бачить, що `msg.vc[0] == 1`, тоді як локальний вектор Вузла 2 дорівнює `[0, 0, 0]`. Алгоритм розпізнає: повідомлення Боба посилається на невідому зміну від Вузла 0. Повідомлення поміщається в чергу `buffer`. Читання з Вузла 2 повертає безпечний вихідний стан `value = 0`, не допускаючи аномалії «відповідь без питання».
   - **У моделі Linearizable:** Аномалія не може виникнути в принципі, оскільки операція запису Боба на Вузлі 1 не отримає статус `OK`, доки кворум вузлів (включно з Вузлом 2) не зафіксує попередній запис Аліси в точці лінеаризації.

## Порівняння архітектури C та C++ реалізацій

Порівняння двох вкладок коду демонструє еволюцію системного мислення:
- **У версії C:** використовується статична алокація пам'яті (`fixed-size arrays`), пряме маніпулювання байтами через `memset` та ручне управління лічильниками буфера `buffer_count`. Видалення обробленого повідомлення з буфера реалізовано патерном швидкого обміну з останнім елементом (`swap with back`), що дає складність `O(1)`, але не зберігає порядок черги.
- **У версії C++20:** структура повністю інкапсульована в простір імен `dist`. Використання `std::array<uint32_t, NodeCount>` гарантує нульовий накладний оверхед при збереженні безпеки типів і семантики значень. Метод `drainBuffer` використовує ітератори `std::vector::erase`, автоматично керуючи динамічною пам'яттю за принципом RAII, а метод `read` позначений специфікатором `[[nodiscard]] noexcept`, що унеможливлює ігнорування результату й гарантує відсутність генерації винятків у критичному шляху читання.

## Підводні камені та практичні обмеження

1. **Проблема розміру векторів у великих кластерах (Vector Scaling Explosion):**
   У симуляторі вектор складається з трьох елементів. У реальних системах з тисячами динамічних вузлів векторні годинники стають занадто важкими для передачі в кожному мережевому запиті. Промислові сховища (Dynamo, Riak) застосовують евристики зрізання векторів за часом (Vector Pruning), що може призводити до хибної появи конкурентності та порожніх конфліктів.
2. **Проблема прихованого каналу (Hidden Channel / Out-of-band Causality):**
   Якщо Аліса пише повідомлення у базу даних, а потім дзвонить Бобу через стільниковий зв'язок і просить прочитати його, між цими подіями існує причинний зв'язок у фізичному світі. Проте база даних не знає про телефонний дзвінок, тому векторні годинники не зафіксують залежність. Уникнути цієї проблеми дозволяє лише повна **лінеаризовність**.
3. **Дрейф фізичних годинників при Last-Write-Wins:**
   Утилізація LWW для розв'язання конфліктів у кінцевій узгодженості приховує небезпеку: розходження системних годинників серверів через NTP навіть на кілька мілісекунд призводить до того, що фізично пізніший запис на сервері з повільним годинником буде тихо відкинутий старішим записом із сервера зі швидким годинником.
4. **Переповнення буферів відкладених повідомлень (Buffer Bloat):**
   Якщо вузол-джерело зазнає перманентного збою або мережевого ізолювання, його пропущені повідомлення ніколи не надійдуть до решти реплік. У результаті буфери причинності на здорових вузлах почнуть безконтрольно накопичувати залежні повідомлення, що врешті призведе до вичерпання оперативної пам'яті (OOM Crash). Для запобігання цій аварії промислові системи встановлюють таймаути очікування залежностей і механізми переведення залиплих оновлень у режим карантину.
5. **Низька швидкість збіжності каскадних розблокувань:**
   Коли після тривалої мережевої паузи надходить довгоочікуване базове повідомлення, функція `drainBuffer` змушена багаторазово сканувати весь масив буфера для виявлення розблокованих транзитивних залежностей. У високонавантажених сервісах замість лінійного сканування застосовують структури індексації залежностей на основі спрямованих ациклічних графів (DAG Dependency Graph), де надходження події негайно активує лише її прямих нащадків.

## Альтернатива LWW: Конфліктно-вільні репліковані типи даних (CRDT)

Щоб уникнути втрати даних через дрейф фізичних годинників у моделях кінцевої узгодженості, замість евристики Last-Write-Wins застосовують безальтернативні математичні структури — **CRDT** (*Conflict-free Replicated Data Types*).

CRDT на основі стану (State-based / CvRDT) перетворюють операції реплікації на злиття над напівґраткою (Join-Semilattice). Функція злиття станів `merge(A, B)` задовольняє три аксіоми:
1. **Комутативність:** `merge(A, B) = merge(B, A)` — порядок прибуття повідомлень не впливає на кінцевий стан.
2. **Асоціативність:** `merge(merge(A, B), C) = merge(A, merge(B, C))` — групування пакетів не має значення.
3. **Ідемпотентність:** `merge(A, A) = A` — дублікати мережевих пакетів не спотворюють результат.

Для лічильників застосовують **PN-Counter** (Positive-Negative Counter), де кожен вузол веде два окремі вектори: вектор інкрементів `P` та вектор декрементів `N`. Поточне значення обчислюється як сума всіх `P` мінус сума всіх `N`. Злиття двох станів зводиться до взяття покомпонентного максимуму: `P_merged[k] = max(P_local[k], P_remote[k])`. Це гарантує строгу кінцеву узгодженість (Strong Eventual Consistency) без блокувань та втрати паралельних оновлень.

Для множин використовують **Observed-Remove Set (OR-Set)**: кожен доданий елемент отримує унікальний тег (UUID або логічну мітку часу). Операція видалення елемента вилучає лише ті теги, які вже спостерігалися локально на момент видалення. Якщо паралельно інший вузол додав той самий елемент з новим унікальним тегом, операція додавання перемагає, усуваючи класичну аномалію воскресіння видалених даних (Ghost Reappearance Anomaly).

## Організація пам'яті та багатопотокова продуктивність

При переході від симулятора до реального багатопотокового рушія сховища на C/C++ інженери стикаються з апаратними ефектами кеш-ліній процесора:
1. **Захист від хибного спільного використання (False Sharing):**
   Якщо структури векторних годинників різних вузлів розташовані в одному суцільному масиві, паралельне оновлення лічильників різними ядрами CPU призводить до постійної інвалідації кеш-ліній L1/L2 (Cache Line Bouncing). Для запобігання цьому структури вирівнюють за межею кеш-лінії процесора (`alignas(64)` або `alignas(128)`).
2. **Атомарні операції з ослабленою моделлю пам'яті (Relaxed Atomics):**
   Інкремент локального векторного годинника не вимагає важких бар'єрів пам'яті `std::memory_order_seq_cst`. Достатньо використання `std::memory_order_relaxed` для локальних змін у поєднанні з `std::memory_order_release` під час публікації повідомлення в чергу сокета та `std::memory_order_acquire` під час вичитування з буфера прийому.
3. **Неблокувальні черги повідомлень (Lock-free MPSC Queues):**
   Передача реплікаційних пакетів між мережевими потоками (I/O Threads) та потоками кінцевого автомата (Worker Threads) організується через кільцеві буфери без блокувань (Ring Buffers), що забезпечує пропускну здатність у мільйони операцій на секунду на одне ядро.

## Збір сміття причинних метаданих (Causal Garbage Collection)

У тривало працюючій системі неможливо вічно зберігати повну історію векторних годинників та журналів оновлень. Для очищення пам'яті застосовують протокол **причинної стабільності (Causal Stability)**:
- Кожен вузол періодично розсилає вектор підтверджень `AckVector`, повідомляючи партнерам свій локальний векторний годинник `V_local`.
- Репліки збирають матрицю підтверджень `AckMatrix[N][N]`.
- Вектор `V_stable = min_i(AckMatrix[i])` позначає точку, до якої оновлення гарантовано отримані й застосовані абсолютно всіма репліками кластера.
- Усі метадані залежностей та записи буферів, чиї вектори `V ≤ V_stable`, вважаються стабільними та безпечно видаляються з пам'яті (Garbage Collection), гарантуючи обмежений розмір структур даних незалежно від тривалості роботи кластера.

## Інженерний чекліст тестування консистентності в продакшені

Для верифікації реальних сервісів під навантаженням застосовують інженерні методики хаос-тестування за моделлю Jepsen:

1. **Ін'єкція штучних мережевих розділень (Network Partition Injections):**
   За допомогою утиліти `iptables` або `tc netem` розривають зв'язок між координатором та репліками. Тестовий генератор перевіряє, чи не повертає лінеаризовний сервіс суперечливих відповідей під час розпаду кластера на меншість і більшість.
2. **Штучне внесення джиттеру та перевпорядкування пакетів (Packet Reordering & Delay):**
   Емуляція затримок до 500 мс на випадкових лініях зв'язку дозволяє виявити помилки в реалізації буферів причинної доставки та перевірити роботу механізмів виявлення пропущених повідомлень.
3. **Стрес-тестування годинників (Clock Skew & Leap Second Injection):**
   Примусовий зсув системного часу вузлів уперед і назад на 5–10 секунд перевіряє, чи не спирається бізнес-логіка на настінний час (`CLOCK_REALTIME`) замість монотонних таймерів (`CLOCK_MONOTONIC`) або логічних годинників Лампорта.
4. **Верифікація історії через аналізатор Knossos / Elle:**
   Усі згенеровані під час тесту операції записуються в структурований журнал подій `H = (inv, res)` і подаються на вхід валідатору лінеаризовності. Виявлення хоча б одного циклу в графі залежностей однозначно свідчить про наявність багів у протоколі реплікації або конфігурації сховища.
5. **Динамічна зміна конфігурації кластера (Membership Reconfiguration):**
   Додавання або видалення реплік «на льоту» під активним навантаженням вимагає двоетапного переходу (Joint Consensus у Raft або двофазної зміни конфігурації у Paxos), щоб уникнути виникнення двох незалежних кворумних більшостей у перехідний період.
6. **Перевірка розриву лідерської оренди під час пауз ОС:**
   Штучне заморожування процесу лідера сигналом `SIGSTOP` на 3000 мс дозволяє перевірити, чи не віддасть лідер застарілі читання після відновлення роботи сигналом `SIGCONT`, коли його термін оренди вже сплив у фізичному часі.
