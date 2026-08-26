# ⚙️ Захисна рандомізація API: боротьба з неявними залежностями в C та C++

Штучна рандомізація порядку елементів та часових затримок у неспецифікованих частинах інтерфейсу дозволяє виявити неявні клієнтські залежності на ранніх етапах тестування ще до випуску коду в експлуатацію.

## Постановка задачі: пастка детермінізму

Уявімо сервіс реєстрації вузлів кластера або підсистему черги завдань у розподіленій системі. Специфікація публічного API стверджує:

> «Метод повертає список активних робочих вузлів. Порядок елементів у списку не гарантується і може змінюватися між викликами».

На практиці розробник бібліотеки зберігає вузли у звичайному динамічному масиві. Під час кожного запиту масив повертається у порядку додавання: `["node-alpha", "node-beta", "node-gamma"]`.

Клієнтський інженер, створюючи свій сервіс, пише інтеграційний тест:

```
assert(nodes[0] == "node-alpha");
```

Оскільки порядок завжди однаковий, цей тест успішно проходить 10 000 разів поспіль на всіх стендах CI/CD. Клієнтський код починає спиратися на те, що перший вузол — це завжди головний координатор (`leader`), хоча в документації про це немає жодного слова.

Через пів року автор бібліотеки оптимізує внутрішню структуру: замінює масив на паралельну хеш-таблицю або шардований буфер. Порядок повернення змінюється на `["node-beta", "node-gamma", "node-alpha"]`. Контракт не порушено, типи збігаються, SemVer зафіксував виправлення патчем. Проте сотні клієнтських сервісів падають в аварійному режимі у продакшені. Це класичний прояв закону Гайрама.

## Архітектурне рішення: активна дедетермінізація

Щоб клієнти не могли зав'язатися на випадковий детермінізм реалізації, сервіс у тестовому та налагоджувальному режимах впроваджує **захисну рандомізацію** (англ. *defensive randomization*):
1. **Перемішування порядку колекції:** застосування тасування Фішера — Єйтса (англ. *Fisher-Yates shuffle*) до масиву перед його поверненням клієнтові.
2. **Штучний часовий джиттер (Latency Jitter):** введення контрольованих мікрозатримок для унеможливлення зав'язування на надшвидкі мікросекундні відповіді.

Нижче наведено повну реалізацію безпечного реєстру вузлів на C та C++:

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <stdint.h>

#define MAX_NODES 16
#define NAME_LEN  32

typedef struct {
    char     name[NAME_LEN];
    int      load_percent;
    uint32_t node_id;
} ClusterNode;

typedef struct {
    ClusterNode nodes[MAX_NODES];
    size_t      count;
    unsigned int rng_seed;
    int         defensive_mode; /* 1 = тасувати неспецифікований порядок */
} NodeRegistry;

void registry_init(NodeRegistry *reg, int defensive_mode, unsigned int seed) {
    if (!reg) return;
    reg->count = 0;
    reg->rng_seed = seed ? seed : (unsigned int)time(NULL);
    reg->defensive_mode = defensive_mode;
}

int registry_add(NodeRegistry *reg, const char *name, int load, uint32_t id) {
    if (!reg || !name) return -1;
    if (reg->count >= MAX_NODES) return -1;

    strncpy(reg->nodes[reg->count].name, name, NAME_LEN - 1);
    reg->nodes[reg->count].name[NAME_LEN - 1] = '\0';
    reg->nodes[reg->count].load_percent = load;
    reg->nodes[reg->count].node_id = id;
    reg->count++;
    return 0;
}

/* Отримання вузлів із захисним перемішуванням (Fisher-Yates) */
size_t registry_get_active(NodeRegistry *reg, ClusterNode *out_buf, size_t max_out) {
    if (!reg || !out_buf || max_out == 0) return 0;

    size_t n = (reg->count < max_out) ? reg->count : max_out;
    for (size_t i = 0; i < n; i++) {
        out_buf[i] = reg->nodes[i];
    }

    /* Якщо увімкнено захисний режим і в списку більше одного елемента,
       виконуємо тасування Фішера — Єйтса для дедетермінізації */
    if (reg->defensive_mode && n > 1) {
        for (size_t i = n - 1; i > 0; i--) {
            size_t j = (size_t)(rand_r(&reg->rng_seed) % (i + 1));
            ClusterNode tmp = out_buf[i];
            out_buf[i] = out_buf[j];
            out_buf[j] = tmp;
        }
    }
    return n;
}
```
```cpp
#include <algorithm>
#include <chrono>
#include <cstdint>
#include <random>
#include <span>
#include <string>
#include <string_view>
#include <vector>

struct ClusterNode {
    std::string name;
    int         load_percent{0};
    uint32_t    node_id{0};
};

class NodeRegistry {
public:
    explicit NodeRegistry(bool defensive_mode = true, uint32_t custom_seed = 0)
        : defensive_mode_{defensive_mode},
          rng_{custom_seed != 0 ? custom_seed : static_cast<std::mt19937::result_type>(
              std::chrono::steady_clock::now().time_since_epoch().count())} {}

    bool add_node(std::string_view name, int load, uint32_t id) {
        nodes_.push_back(ClusterNode{std::string(name), load, id});
        return true;
    }

    /* Повертає знімок вузлів. Якщо увімкнено захисний режим,
       порядок свідомо тасується для унеможливлення неявного зв'язування */
    [[nodiscard]] std::vector<ClusterNode> get_active_nodes() {
        std::vector<ClusterNode> snapshot = nodes_;
        if (defensive_mode_ && snapshot.size() > 1) {
            std::shuffle(snapshot.begin(), snapshot.end(), rng_);
        }
        return snapshot;
    }

    [[nodiscard]] size_t size() const noexcept {
        return nodes_.size();
    }

private:
    std::vector<ClusterNode> nodes_;
    bool                     defensive_mode_{true};
    std::mt19937             rng_;
};
```
:::

## Захисний часовий шар: фаззинг затримок (Latency Jitter)

Окрім порядку елементів, клієнти нерідко зв'язуються з часовими характеристиками (latency). Якщо у тестовому середовищі виклик завершується за 50 мікросекунд, клієнтський розробник виставляє таймаут 2 мілісекунди. При перенесенні у реальну мережу затримка зростає до 5 мс, і всі клієнтські запити завершуються аварією `TimeoutException`.

Для запобігання цьому використовують шар фаззингу затримок:

:::tabs
```c
#include <unistd.h>

/* Введення штучного мікросекундного джиттеру в C */
void defensive_latency_jitter(unsigned int *seed, int min_ms, int max_ms) {
    if (!seed || max_ms <= min_ms) return;
    int span = max_ms - min_ms + 1;
    int delay_ms = min_ms + (rand_r(seed) % span);
    usleep((useconds_t)delay_ms * 1000);
}
```
```cpp
#include <chrono>
#include <random>
#include <thread>

/* Введення штучного мікросекундного джиттеру в C++ */
class LatencyJitterFilter {
public:
    LatencyJitterFilter(std::chrono::milliseconds min_delay,
                        std::chrono::milliseconds max_delay)
        : min_delay_{min_delay}, max_delay_{max_delay},
          dist_{static_cast<double>(min_delay.count()), static_cast<double>(max_delay.count())},
          rng_{std::random_device{}()} {}

    void inject_delay() {
        auto ms = static_cast<int64_t>(dist_(rng_));
        std::this_thread::sleep_for(std::chrono::milliseconds(ms));
    }

private:
    std::chrono::milliseconds min_delay_;
    std::chrono::milliseconds max_delay_;
    std::uniform_real_distribution<double> dist_;
    std::mt19937 rng_;
};
```
:::

## Стійкий клієнт проти крихкого клієнта

Розглянемо, як поводяться два різні клієнтські застосунки під час взаємодії з рандомізованим інтерфейсом:

:::tabs
```c
/* Клієнтська логіка на C */
int compare_nodes_by_id(const void *a, const void *b) {
    const ClusterNode *na = (const ClusterNode *)a;
    const ClusterNode *nb = (const ClusterNode *)b;
    if (na->node_id < nb->node_id) return -1;
    if (na->node_id > nb->node_id) return 1;
    return 0;
}

void robust_client_process(NodeRegistry *reg) {
    ClusterNode received[MAX_NODES];
    size_t count = registry_get_active(reg, received, MAX_NODES);

    /* СТІЙКИЙ ПІДХІД: клієнт не покладається на порядок з API,
       а явно сортує отримані дані перед обробкою за стабільним ключем */
    qsort(received, count, sizeof(ClusterNode), compare_nodes_by_id);

    for (size_t i = 0; i < count; i++) {
        /* Детермінована обробка: received[0] завжди має мінімальний ID */
    }
}
```
```cpp
/* Клієнтська логіка на C++ */
#include <algorithm>
#include <iostream>

void robust_client_process(NodeRegistry& registry) {
    std::vector<ClusterNode> nodes = registry.get_active_nodes();

    /* СТІЙКИЙ ПІДХІД: якщо клієнту потрібен детермінований порядок,
       він явно сортує колекцію за ідентифікатором або назвою */
    std::sort(nodes.begin(), nodes.end(), [](const auto& a, const auto& b) {
        return a.node_id < b.node_id;
    });

    for (const auto& node : nodes) {
        // Гарантована детермінована обробка незалежно від поведінки API
    }
}
```
:::

## Покроковий розбір поведінки та виявлення дефектів

Коли клієнт викликає `get_active_nodes()` або `registry_get_active()`, тестовий сценарій виконує три послідовні перевірки:

1. **Крок 1: Перший виклик.** Реєстр повертає вузли у стані `["node-gamma", "node-alpha", "node-beta"]`. Крихкий клієнт, що очікував `node-alpha` на нульовій позиції, негайно отримує твердження `AssertionError: expected 'node-alpha', got 'node-gamma'`.
2. **Крок 2: Локалізація помилки.** Інженер відкриває документацію і бачить: «порядок не гарантується». Оскільки помилка сталася на локальній машині розробника під час першого запуску тесту, виправлення коштує 2 хвилини: додати виклик `std::sort` або `qsort`.
3. **Крок 3: Перевірка стійкості.** Після додавання сортування клієнтський тест успішно проходить на будь-якій випадковій перестановці елементів. Система стає несприйнятливою до майбутніх змін реалізації сервера.

## Крайові випадки та тонкощі алгоритму

Під час реалізації захисної рандомізації необхідно враховувати специфічні крайові ситуації:

- **Порожня колекція або один елемент:** Якщо масив містить `0` або `1` елемент, циклічне перемішування виконуватися не повинно (`n > 1`). Для `n = 1` відсутність розгалуження призведе до помилки виходу за межі пам'яті у циклі Фішера — Єйтса при зверненні до індексу `n - 1`.
- **Зміщення залишку від ділення (Modulo Bias):** Вираз `rand() % (i + 1)` створює нерівномірний розподіл, якщо діапазон генератора не ділиться націло на `(i + 1)`. У критичних криптографічних підсистемах слід використовувати алгоритм відкидання (rejection sampling) або функцію `arc4random_uniform()`. Для цілей захисної дедетермінізації тестів звичайного `rand_r` чи `std::mt19937` цілком достатньо.
- **Потокобезпечність (Thread Safety):** Стандартний `rand()` використовує спільний глобальний стан без блокування. Виклик `rand_r(&seed)` із локальним сідом або використання `thread_local std::mt19937` унеможливлює стан гонитви (race condition) у багатопотокових сервісах.

## Інженерні компроміси та рекомендації

1. **Режими роботи (CI vs Production):**
   - У тестовому середовищі (`CI`, `Staging`, локальні юніт-тести) захисна рандомізація повинна бути увімкнена на 100%. Це забезпечує агресивне виявлення неявних зв'язків.
   - У високопродуктивному бойовому середовищі перемішування масивів на кожному виклику може створювати зайве навантаження на процесор. У продакшені достатньо використовувати випадковий сід під час старту процесу (стратегія Go map), що виключає оверхед на кожен виклик, але змінює порядок при перезапуску інстансів.
2. **Відтворюваність падінь через фіксований сід (Test Seeds):**
   - Якщо рандомізований порядок виявив рідкісний баг race condition або некоректне сортування, тестовий фреймворк зобов'язаний вивести значення сіду генератора у лог (наприклад, `Test failed with RNG seed: 0x8F3A21C0`).
   - Розробник передає прапорець `--seed=0x8F3A21C0` і отримує 100% детерміноване повторення послідовності для покрокового налагодження в `gdb` або `lldb`.
3. **Фаззинг часових характеристик у конвеєрі тестування:**
   - Введення випадкової затримки у межах `[1ms, 20ms]` у тестовому середовищі змушує клієнтські команди виставляти адекватні таймаути та впроваджувати механізми експоненційного відступу (Exponential Backoff).
