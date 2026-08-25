# ⚙️ Реалізація планувальника Iterative Modulo Scheduling на C та C++

Програмна конвеєризація вимагає від оптимізуючого компілятора розв'язання складної комбінаторної оптимізаційної задачі: розмістити операції тіла циклу на часовій сітці так, щоб мінімізувати інтервал ініціалізації (`II`), не допустити конфліктів за фізичними блоками процесора у таблиці модульного резервування (MRT) та не порушити залежностей між ітераціями.

Нижче наведено повнофункціональну реалізацію класичного алгоритму **Iterative Modulo Scheduling (IMS)** Боба Рау. Програма будує граф залежностей за даними (DDG), розраховує теоретичні бар'єри `ResMII` та `RecMII`, сортує операції за пріоритетом висоти та виконує ітеративне планування з підтримкою відкатів (Backtracking) при виникненні апаратних конфліктів.

### Архітектура та структури даних планувальника

Реалізація планувальника спирається на чотири взаємопов'язані концептуальні моделі:
1. **Модель операцій та ресурсів (`Node` / `ResourceType`):** Кожна операція циклу має власну фіксовану тривалість виконання (латентність у тактах), вимогу до типу фізичного функціонального пристрою (порт пам'яті, помножувач чи АЛП) та динамічний стан планування (призначений абсолютний такт `sched_time` і лічильник бюджету спроб `budget`).
2. **Модель інформаційних залежностей (`Edge`):** Спрямовані ребра зв'язують операцію-виробника `src` та операцію-споживача `dst`. Кожне ребро несе два числових параметри: апаратну латентність `latency` (скільки тактів має пройти від старту джерела до готовності даних) та дистанцію за ітераціями `distance` (`0` для передачі даних усередині тієї самої ітерації, `1` для міжітераційного накопичення).
3. **Модульна таблиця резервування (`MRT`):** Матриця розміром `II × Resources`. Для довільного абсолютного часу `t` функція відображення `t mod II` визначає рядок таблиці, у якому фіксується зайнятість відповідного блоку. Якщо кілька операцій претендують на один і той самий слот `t mod II` для ресурсу, доступного лише в одному екземплярі, виникає ресурсний конфлікт.
4. **Механізм відкатів (Backtracking):** Якщо в діапазоні `[EStart, EStart + II - 1]` не знайдено жодного вільного слота в MRT, планувальник не зупиняє роботу аварійно, а примусово призначає поточну операцію на момент `EStart`. Усі раніше заплановані операції, з якими вона вступила в апаратну колізію в MRT, витісняються (un-schedule) і повертаються назад у чергу нерозкладених вузлів. Лічильник `budget` кожної вершини декрементується, запобігаючи нескінченному взаємному витісненню.

### Повна реалізація планувальника на C та C++

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>

#define MAX_NODES 16
#define MAX_EDGES 32
#define MAX_RESOURCES 4
#define MAX_II 32
#define MAX_BUDGET 64

// Типи апаратних функціональних блоків процесора
typedef enum {
    RES_MEM = 0, // Порти пам'яті (Load / Store)
    RES_ALU = 1, // Цілочислові АЛП (Add, Sub, Logic)
    RES_MUL = 2, // Блоки конвеєрного множення (Mul)
    RES_COUNT
} ResourceType;

// Ребро залежності між операціями в графі DDG
typedef struct {
    int src;          // Індекс операції-джерела
    int dst;          // Індекс операції-споживача
    int latency;      // Латентність d(u, v) у тактах
    int distance;     // Дистанція за ітераціями delta(u, v)
} Edge;

// Вузол графа залежностей (окрема машинна операція)
typedef struct {
    const char *name;     // Символьна назва операції
    ResourceType res;     // Необхідний функціональний блок
    int latency;          // Власна тривалість операції
    int height;           // Пріоритет висоти в графі
    int sched_time;       // Запланований абсолютний такт (-1, якщо не заплановано)
    int budget;           // Лічильник спроб для запобігання зацикленню відкатів
} Node;

// Граф залежностей за даними
typedef struct {
    Node nodes[MAX_NODES];
    Edge edges[MAX_EDGES];
    int node_count;
    int edge_count;
    int res_units[RES_COUNT]; // Кількість фізичних пристроїв кожного типу
} Graph;

// Таблиця модульного резервування (MRT)
typedef struct {
    int ii;
    int table[MAX_II][MAX_RESOURCES]; // table[slot][res_type] = кількість зайнятих блоків
    int occupied_by[MAX_II][MAX_RESOURCES][MAX_NODES]; // Індекси призначених операцій
} MRT;

// Ініціалізація таблиці MRT для заданого значення II
static void mrt_init(MRT *mrt, int ii) {
    mrt->ii = ii;
    memset(mrt->table, 0, sizeof(mrt->table));
    for (int s = 0; s < MAX_II; ++s) {
        for (int r = 0; r < MAX_RESOURCES; ++r) {
            for (int n = 0; n < MAX_NODES; ++n) {
                mrt->occupied_by[s][r][n] = -1;
            }
        }
    }
}

// Перевірка доступності ресурсу в слоті (time mod II)
static bool mrt_can_reserve(const MRT *mrt, const Graph *g, ResourceType res, int time) {
    int slot = time % mrt->ii;
    return mrt->table[slot][res] < g->res_units[res];
}

// Резервування ресурсу в таблиці MRT
static void mrt_reserve(MRT *mrt, int node_id, ResourceType res, int time) {
    int slot = time % mrt->ii;
    int count = mrt->table[slot][res];
    mrt->occupied_by[slot][res][count] = node_id;
    mrt->table[slot][res]++;
}

// Звільнення ресурсу в MRT при витісненні операції під час відкату
static void mrt_unreserve(MRT *mrt, int node_id, ResourceType res, int time) {
    int slot = time % mrt->ii;
    int count = mrt->table[slot][res];
    for (int i = 0; i < count; ++i) {
        if (mrt->occupied_by[slot][res][i] == node_id) {
            for (int j = i; j < count - 1; ++j) {
                mrt->occupied_by[slot][res][j] = mrt->occupied_by[slot][res][j + 1];
            }
            mrt->occupied_by[slot][res][count - 1] = -1;
            mrt->table[slot][res]--;
            break;
        }
    }
}

// Обчислення ресурсного бар'єра ResMII
static int compute_res_mii(const Graph *g) {
    int res_mii = 1;
    for (int r = 0; r < RES_COUNT; ++r) {
        int count = 0;
        for (int i = 0; i < g->node_count; ++i) {
            if (g->nodes[i].res == r) count++;
        }
        int units = g->res_units[r] > 0 ? g->res_units[r] : 1;
        int mii_r = (count + units - 1) / units;
        if (mii_r > res_mii) res_mii = mii_r;
    }
    return res_mii;
}

// Обчислення рекурентного бар'єра RecMII для циклічних залежностей
static int compute_rec_mii(const Graph *g) {
    int rec_mii = 1;
    for (int e = 0; e < g->edge_count; ++e) {
        if (g->edges[e].src == g->edges[e].dst && g->edges[e].distance > 0) {
            int ratio = (g->edges[e].latency + g->edges[e].distance - 1) / g->edges[e].distance;
            if (ratio > rec_mii) rec_mii = ratio;
        }
    }
    return rec_mii;
}

// Розрахунок пріоритетів висоти (Height) у графі DDG
static void compute_heights(Graph *g, int mii) {
    for (int i = 0; i < g->node_count; ++i) {
        g->nodes[i].height = g->nodes[i].latency;
    }
    bool changed = true;
    while (changed) {
        changed = false;
        for (int e = 0; e < g->edge_count; ++e) {
            int u = g->edges[e].src;
            int v = g->edges[e].dst;
            int d = g->edges[e].latency;
            int delta = g->edges[e].distance;
            int eff_d = d - delta * mii;
            if (g->nodes[u].height < g->nodes[v].height + eff_d) {
                g->nodes[u].height = g->nodes[v].height + eff_d;
                changed = true;
            }
        }
    }
}

// Обчислення раннього моменту старту EStart на основі запланованих предків
static int compute_estart(const Graph *g, int node_id, int ii) {
    int estart = 0;
    for (int e = 0; e < g->edge_count; ++e) {
        if (g->edges[e].dst == node_id) {
            int p = g->edges[e].src;
            if (g->nodes[p].sched_time != -1) {
                int min_t = g->nodes[p].sched_time + g->edges[e].latency - g->edges[e].distance * ii;
                if (min_t > estart) estart = min_t;
            }
        }
    }
    return estart;
}

// Головний цикл планування Iterative Modulo Scheduling (IMS)
static bool ims_schedule(Graph *g, int *final_ii, int *final_length) {
    int res_mii = compute_res_mii(g);
    int rec_mii = compute_rec_mii(g);
    int ii = (res_mii > rec_mii) ? res_mii : rec_mii;

    printf("Розрахункові бар'єри: ResMII = %d, RecMII = %d -> Старт із II = %d\n", res_mii, rec_mii, ii);

    while (ii <= MAX_II) {
        MRT mrt;
        mrt_init(&mrt, ii);
        compute_heights(g, ii);

        for (int i = 0; i < g->node_count; ++i) {
            g->nodes[i].sched_time = -1;
            g->nodes[i].budget = MAX_BUDGET;
        }

        bool success = true;
        int unscheduled_count = g->node_count;

        while (unscheduled_count > 0) {
            // Вибір нерозкладеної вершини з найвищим пріоритетом Height
            int best_node = -1;
            int max_height = -9999;
            for (int i = 0; i < g->node_count; ++i) {
                if (g->nodes[i].sched_time == -1 && g->nodes[i].height > max_height) {
                    max_height = g->nodes[i].height;
                    best_node = i;
                }
            }

            if (best_node == -1) break;

            if (g->nodes[best_node].budget <= 0) {
                printf("Бюджет спроб для операції '%s' вичерпано. Збільшуємо II = %d -> %d\n",
                       g->nodes[best_node].name, ii, ii + 1);
                success = false;
                break;
            }
            g->nodes[best_node].budget--;

            int estart = compute_estart(g, best_node, ii);
            int sched_t = -1;

            // Спроба знайти вільний слот у діапазоні [EStart, EStart + II - 1]
            for (int t = estart; t < estart + ii; ++t) {
                if (mrt_can_reserve(&mrt, g, g->nodes[best_node].res, t)) {
                    sched_t = t;
                    break;
                }
            }

            if (sched_t != -1) {
                g->nodes[best_node].sched_time = sched_t;
                mrt_reserve(&mrt, best_node, g->nodes[best_node].res, sched_t);
                unscheduled_count--;
            } else {
                // Відкат (Backtracking): примусово ставимо на EStart, скидаючи конфліктні операції
                sched_t = estart;
                int slot = sched_t % ii;
                ResourceType r = g->nodes[best_node].res;

                int victim = mrt.occupied_by[slot][r][0];
                if (victim != -1 && victim != best_node) {
                    mrt_unreserve(&mrt, victim, r, g->nodes[victim].sched_time);
                    g->nodes[victim].sched_time = -1;
                    unscheduled_count++;
                }

                g->nodes[best_node].sched_time = sched_t;
                mrt_reserve(&mrt, best_node, r, sched_t);
                unscheduled_count--;
            }
        }

        if (success) {
            *final_ii = ii;
            int max_t = 0;
            for (int i = 0; i < g->node_count; ++i) {
                int end_t = g->nodes[i].sched_time + g->nodes[i].latency;
                if (end_t > max_t) max_t = end_t;
            }
            *final_length = max_t;
            return true;
        }

        ii++;
    }

    return false;
}

int main(void) {
    Graph g = {
        .node_count = 4,
        .edge_count = 4,
        .res_units = { [RES_MEM] = 2, [RES_ALU] = 1, [RES_MUL] = 1 },
        .nodes = {
            { .name = "Load_A", .res = RES_MEM, .latency = 2 },
            { .name = "Load_B", .res = RES_MEM, .latency = 2 },
            { .name = "Multiply", .res = RES_MUL, .latency = 2 },
            { .name = "Accumulate", .res = RES_ALU, .latency = 1 }
        },
        .edges = {
            { .src = 0, .dst = 2, .latency = 2, .distance = 0 }, // Load_A -> Mul
            { .src = 1, .dst = 2, .latency = 2, .distance = 0 }, // Load_B -> Mul
            { .src = 2, .dst = 3, .latency = 2, .distance = 0 }, // Mul -> Acc
            { .src = 3, .dst = 3, .latency = 1, .distance = 1 }  // Acc[i] -> Acc[i+1] (рекурентність)
        }
    };

    printf("=== Планувальник Iterative Modulo Scheduling (C) ===\n\n");
    int final_ii = 0;
    int sched_len = 0;

    if (ims_schedule(&g, &final_ii, &sched_len)) {
        int stages = (sched_len + final_ii - 1) / final_ii;
        printf("\nРозклад побудовано успішно!\n");
        printf("Інтервал ініціалізації (II): %d такт(ів)\n", final_ii);
        printf("Загальна довжина розкладу:   %d тактів\n", sched_len);
        printf("Кількість стадій конвеєра:   %d\n\n", stages);

        printf("Таблиця розміщення інструкцій:\n");
        printf("%-12s | %-10s | %-8s | %-12s\n", "Операція", "Ресурс", "Такт t", "Стадія");
        printf("-------------+------------+----------+-------------\n");
        for (int i = 0; i < g.node_count; ++i) {
            const char *res_str = (g.nodes[i].res == RES_MEM) ? "MEM" :
                                  (g.nodes[i].res == RES_ALU) ? "ALU" : "MUL";
            int stage = g.nodes[i].sched_time / final_ii;
            printf("%-12s | %-10s | %-8d | Стадія %d\n",
                   g.nodes[i].name, res_str, g.nodes[i].sched_time, stage);
        }
    } else {
        printf("Не вдалося знайти допустимий розклад у межах MAX_II.\n");
    }

    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <array>
#include <algorithm>
#include <optional>
#include <iomanip>

enum class ResourceType : size_t {
    Mem = 0, // Порти пам'яті
    Alu = 1, // Цілочислові АЛП
    Mul = 2, // Блоки множення
    Count = 3
};

struct Edge {
    size_t src;
    size_t dst;
    int latency;
    int distance;
};

struct Node {
    std::string name;
    ResourceType res;
    int latency;
    int height{0};
    std::optional<int> schedTime{std::nullopt};
    int budget{64};
};

class ModuloScheduler {
public:
    ModuloScheduler(std::vector<Node> nodes, std::vector<Edge> edges, std::array<size_t, 3> resUnits)
        : nodes_(std::move(nodes)), edges_(std::move(edges)), resUnits_(resUnits) {}

    struct ScheduleResult {
        int ii;
        int scheduleLength;
        int stageCount;
        std::vector<std::pair<std::string, int>> timeline;
    };

    std::optional<ScheduleResult> computeSchedule() {
        const int resMii = computeResMII();
        const int recMii = computeRecMII();
        int ii = std::max(resMii, recMii);

        std::cout << "Розрахункові бар'єри: ResMII = " << resMii
                  << ", RecMII = " << recMii << " -> Старт із II = " << ii << "\n";

        constexpr int MaxII = 32;

        while (ii <= MaxII) {
            computeHeights(ii);
            for (auto& node : nodes_) {
                node.schedTime = std::nullopt;
                node.budget = 64;
            }

            // Модульна таблиця резервування: mrt[slot][resource_type] -> список зайнятих вузлів
            std::vector<std::array<std::vector<size_t>, 3>> mrt(ii);
            size_t unscheduledCount = nodes_.size();
            bool success = true;

            while (unscheduledCount > 0) {
                // Знаходимо нерозкладений вузол із найвищим пріоритетом Height
                std::optional<size_t> bestIdx;
                int maxHeight = -9999;
                for (size_t i = 0; i < nodes_.size(); ++i) {
                    if (!nodes_[i].schedTime.has_value() && nodes_[i].height > maxHeight) {
                        maxHeight = nodes_[i].height;
                        bestIdx = i;
                    }
                }

                if (!bestIdx.has_value()) break;
                const size_t u = *bestIdx;

                if (nodes_[u].budget <= 0) {
                    std::cout << "Бюджет спроб для '" << nodes_[u].name
                              << "' вичерпано. Збільшуємо II: " << ii << " -> " << ii + 1 << "\n";
                    success = false;
                    break;
                }
                --nodes_[u].budget;

                const int estart = computeEStart(u, ii);
                std::optional<int> scheduledTime;

                // Шукаємо вільний слот у вікні [EStart, EStart + II - 1]
                for (int t = estart; t < estart + ii; ++t) {
                    const size_t slot = static_cast<size_t>(t % ii);
                    const auto resIdx = static_cast<size_t>(nodes_[u].res);
                    if (mrt[slot][resIdx].size() < resUnits_[resIdx]) {
                        scheduledTime = t;
                        break;
                    }
                }

                const auto resIdx = static_cast<size_t>(nodes_[u].res);

                if (scheduledTime.has_value()) {
                    nodes_[u].schedTime = *scheduledTime;
                    const size_t slot = static_cast<size_t>(*scheduledTime % ii);
                    mrt[slot][resIdx].push_back(u);
                    --unscheduledCount;
                } else {
                    // Відкат (Backtracking): скидаємо першу операцію з конфліктного слота
                    const int forcedTime = estart;
                    const size_t slot = static_cast<size_t>(forcedTime % ii);

                    if (!mrt[slot][resIdx].empty()) {
                        const size_t victim = mrt[slot][resIdx].front();
                        mrt[slot][resIdx].erase(mrt[slot][resIdx].begin());
                        nodes_[victim].schedTime = std::nullopt;
                        ++unscheduledCount;
                    }

                    nodes_[u].schedTime = forcedTime;
                    mrt[slot][resIdx].push_back(u);
                    --unscheduledCount;
                }
            }

            if (success) {
                int maxEnd = 0;
                ScheduleResult res;
                res.ii = ii;
                for (const auto& node : nodes_) {
                    const int end = *node.schedTime + node.latency;
                    maxEnd = std::max(maxEnd, end);
                    res.timeline.emplace_back(node.name, *node.schedTime);
                }
                res.scheduleLength = maxEnd;
                res.stageCount = (maxEnd + ii - 1) / ii;
                return res;
            }

            ++ii;
        }

        return std::nullopt;
    }

private:
    [[nodiscard]] int computeResMII() const noexcept {
        int resMii = 1;
        for (size_t r = 0; r < 3; ++r) {
            int count = 0;
            for (const auto& node : nodes_) {
                if (static_cast<size_t>(node.res) == r) ++count;
            }
            const size_t units = resUnits_[r] > 0 ? resUnits_[r] : 1;
            const int miiR = static_cast<int>((count + units - 1) / units);
            resMii = std::max(resMii, miiR);
        }
        return resMii;
    }

    [[nodiscard]] int computeRecMII() const noexcept {
        int recMii = 1;
        for (const auto& edge : edges_) {
            if (edge.src == edge.dst && edge.distance > 0) {
                const int ratio = (edge.latency + edge.distance - 1) / edge.distance;
                recMii = std::max(recMii, ratio);
            }
        }
        return recMii;
    }

    void computeHeights(int ii) noexcept {
        for (auto& node : nodes_) {
            node.height = node.latency;
        }
        bool changed = true;
        while (changed) {
            changed = false;
            for (const auto& edge : edges_) {
                const int effD = edge.latency - edge.distance * ii;
                if (nodes_[edge.src].height < nodes_[edge.dst].height + effD) {
                    nodes_[edge.src].height = nodes_[edge.dst].height + effD;
                    changed = true;
                }
            }
        }
    }

    [[nodiscard]] int computeEStart(size_t nodeId, int ii) const noexcept {
        int estart = 0;
        for (const auto& edge : edges_) {
            if (edge.dst == nodeId && nodes_[edge.src].schedTime.has_value()) {
                const int minT = *nodes_[edge.src].schedTime + edge.latency - edge.distance * ii;
                estart = std::max(estart, minT);
            }
        }
        return estart;
    }

    std::vector<Node> nodes_;
    std::vector<Edge> edges_;
    std::array<size_t, 3> resUnits_;
};

int main() {
    std::vector<Node> nodes = {
        {"Load_A", ResourceType::Mem, 2},
        {"Load_B", ResourceType::Mem, 2},
        {"Multiply", ResourceType::Mul, 2},
        {"Accumulate", ResourceType::Alu, 1}
    };

    std::vector<Edge> edges = {
        {0, 2, 2, 0}, // Load_A -> Mul
        {1, 2, 2, 0}, // Load_B -> Mul
        {2, 3, 2, 0}, // Mul -> Acc
        {3, 3, 1, 1}  // Acc[i] -> Acc[i+1]
    };

    std::array<size_t, 3> units = {2, 1, 1}; // 2 Mem, 1 Alu, 1 Mul

    std::cout << "=== Планувальник Iterative Modulo Scheduling (C++) ===\n\n";

    ModuloScheduler scheduler(std::move(nodes), std::move(edges), units);
    auto result = scheduler.computeSchedule();

    if (result) {
        std::cout << "\nРозклад побудовано успішно!\n";
        std::cout << "Інтервал ініціалізації (II): " << result->ii << " такт(ів)\n";
        std::cout << "Загальна довжина розкладу:   " << result->scheduleLength << " тактів\n";
        std::cout << "Кількість стадій конвеєра:   " << result->stageCount << "\n\n";

        std::cout << std::left << std::setw(14) << "Операція" << " | "
                  << std::setw(8) << "Такт t" << " | Стадія\n";
        std::cout << "---------------+----------+-------------\n";
        for (const auto& [name, time] : result->timeline) {
            const int stage = time / result->ii;
            std::cout << std::left << std::setw(14) << name << " | "
                      << std::setw(8) << time << " | Стадія " << stage << "\n";
        }
    }

    return 0;
}
```
:::

### Покроковий розбір виконання тестового прикладу

Розгляньмо, як наведена програма обробляє тестовий цикл скалярного добутку векторів:
```
sum = sum + a[i] * b[i]
```

1. **Аналіз бар'єрів `MII`:**
   - Для пам'яті маємо дві операції `Load_A` та `Load_B` на 2 порти пам'яті: `⌈2 / 2⌉ = 1`.
   - Для помножувача: одна операція `Multiply` на 1 блок множення: `⌈1 / 1⌉ = 1`.
   - Для АЛП: одна операція `Accumulate` на 1 АЛП: `⌈1 / 1⌉ = 1`.
   - Ресурсний бар'єр: `ResMII = max(1, 1, 1) = 1`.
   - Рекурентний зв'язок `Accumulate[i] → Accumulate[i+1]` має латентність `d = 1` та дистанцію `δ = 1`. Рекурентний бар'єр: `RecMII = ⌈1 / 1⌉ = 1`.
   - Стартове значення планувальника: `II = max(1, 1) = 1`.

2. **Побудова розкладу:**
   - Вузли `Load_A` та `Load_B` плануються на такті `t = 0`. Вони займають обидва порти пам'яті в слоті `0 mod 1 = 0`.
   - Вузол `Multiply` залежить від обох завантажень із латентністю `d = 2`, тому `EStart = 0 + 2 = 2`. На такті `t = 2` блок множення вільний у слоті `2 mod 1 = 0`.
   - Вузол `Accumulate` залежить від `Multiply` з латентністю `d = 2`, тому `EStart = 2 + 2 = 4`. На такті `t = 4` блок АЛП вільний у слоті `4 mod 1 = 0`.
   - Перевірка міжітераційного рекурентного зв'язку: для наступної ітерації `EStart(Accumulate, i+1) = Time(Accumulate, i) + 1 - 1·1 = 4 + 1 - 1 = 4`, що точно відповідає моменту `Time(Accumulate, i+1) = 4 + 1·1 = 5`. Жодного конфлікту немає.

3. **Результат:** Загальна довжина ланцюжка обчислень становить 5 тактів (від `t = 0` до `t = 4` плюс 1 такт на завершення додавання). За `II = 1` кількість стадій становить `⌈5 / 1⌉ = 5`. У стабільному ядрі процесор видає **один готовий результат множення з накопиченням щотакту** (IPC = 4 інструкції за такт).

### Розподіл регістрів та інтеграція з компілятором LLVM

Після побудови безконфліктного розкладу наступним критичним етапом оптимізатора є розподіл регістрів для конвеєризованого ядра. Оскільки операція `Load_A` виробляє значення в такті `t = 0`, а операція `Multiply` використовує його в такті `t = 2`, час життя цього значення становить `2` такти.

Для кожного значення `v` компілятор обчислює максимальну кількість одночасно живих копій:
```
MaxLive(v) = ⌈Lifetime(v) / II⌉
```

У нашому прикладі з `II = 1`:
- Значення `Load_A` живе від `t = 0` до `t = 2` (`L = 2`), отже `MaxLive = ⌈2 / 1⌉ = 2` регістри.
- Значення `Load_B` також вимагає `MaxLive = 2` регістри.
- Результат `Multiply` живе від `t = 2` до `t = 4` (`L = 2`), отже `MaxLive = 2` регістри.
- Накопичувач `Accumulate` живе 1 такт, отже `MaxLive = 1` регістр.

Сумарна потреба в регістрах становить `2 + 2 + 2 + 1 = 7` фізичних регістрів. Для призначення конкретних номерів регістрів компілятор використовує алгоритм розфарбовування дуг кола (Circular Arc Coloring): інтервал життя кожного значення відображається як дуга на колі довжиною `II`. Якщо процесор має апаратні ротаційні регістри, кожній змінній просто виділяється вікно з `MaxLive(v)` послідовних адрес, а апаратний покажчик ротації `RRB` автоматично перемикає індекси при переході між стадіями.

У промисловому компіляторі LLVM ця логіка реалізована в пакеті `llvm/lib/CodeGen/MachinePipeliner.cpp`:
- Модуль будує граф `ScheduleDAGMutation` над машинними інструкціями `MachineInstr`.
- Для перевірки відсутності хибних залежностей пам'яті (псевдонімів покажчиків) використовується модуль `AAResults`.
- Клас `SMSchedule` реалізує таблицю MRT та обчислює час життя регістрів через інтервали `LiveIntervals`.
- Клас `ModuloScheduleExpander` генерує фінальний асемблерний код: дублює тіло ядра, вставляє захисні скалярні перевірки мінімальної кількості ітерацій перед входом у конвеєр та розставляє апаратні інструкції ротації або виконує програмне розгортання MVE.

### Типові пастки реалізації планувальника

1. **Зациклення відкатів (Infinite Backtracking Loops):** Якщо дві взаємопов'язані операції з високим пріоритетом постійно витісняють одна одну з єдиного доступного слота MRT, жадібний планувальник потрапляє в нескінченний цикл. Для запобігання цьому обов'язково використовується лічильник `budget` на кожну вершину (у нашому коді — `MAX_BUDGET = 64`). Щойно сумарна кількість спроб вичерпується, компілятор припиняє перебір і збільшує `II`.
2. **Неврахування ланцюгового скидання залежностей:** Якщо при зміщенні вершини `u` у пізніший такт `t` порушується часовий інтервал для вже запланованого споживача `v` (`Time(v) < Time(u) + d(u, v) - δ(u, v)·II`), споживач `v` також повинен бути знятий із розкладу разом із його нащадками, інакше утворюється некоректний розклад із порушенням причинності даних.
3. **Регістровий тиск та вибір `II`:** Чим довша загальна тривалість розкладу відносно `II`, тим більше стадій конвеєра накладаються одна на одну, вимагаючи збереження проміжних операндів у фізичних регістрах процесора. Якщо кількість необхідних регістрів перевищує апаратний ліміт, планувальник штучно збільшує `II`, жертвуючи частиною паралелізму заради усунення скидань на стек.
