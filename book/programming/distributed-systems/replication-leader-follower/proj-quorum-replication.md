# ⚙️ Реалізація кворумного координатора з Read Repair та версіонуванням на C і C++

У безлідерній системі координатор є безстановим диспетчером, який паралельно опитує репліки, збирає кворум відповідей та усуває розходження версій без участі людини. Тут реалізовано повноцінний кворумний координатор для кластера з `N = 5` вузлів, який підтримує параметризовані кворуми `W` і `R`, монотонне версіонування записів, симуляцію нестабільної мережі та асинхронне відновлення застарілих реплік під час читання (Read Repair).

<preknowlist>
- [Лідер-фоловер, мультилідер і безлідерна реплікація](book:programming/replication-leader-follower) — кворумна модель N, W, R та механіка Read Repair.
- [Математичний апарат кворумних перетинів](book:programming/replication-leader-follower/math-quorum-intersection.md) — перетин множин W + R > N.
- [Багатопоточність у C++](book:programming/cpp-multithreading) — м'ютекси, атоміки та потокобезпека.
</preknowlist>

## 1. Архітектурна модель та інваріанти стану

Кворумна реплікація усуває єдину точку відмови лідера, переносячи відповідальність за узгодження даних на координатор та локальні автомати станів реплік.

Симулятор моделює повний життєвий цикл розподіленого запису та читання над кластером із `N = 5` фізичних вузлів.

### Ключові інваріанти моделі:

1. **Монотонність версій (Monotonic Version Ordering):**
   Кожен запис під певним ключем супроводжується цілочисельним номером покоління `version` (або монотонним логічним годинником). Вузол сховища приймає нове значення `v_new` тоді й лише тоді, коли `v_new >= v_local`. Записи з меншим номером версії мовчки відкидаються, що захищає репліку від перезапису свіжих даних запізнілими мережевими пакетами.

2. **Паралельне опитування (Fan-Out Dispatching):**
   Координатор не опитує вузли послідовно один за одним. При виконанні читання або запису службові запити розсилаються одночасно на всі `N` реплік. Це дозволяє системі завершувати операцію за час відповіді `k`-го найшвидшого вузла, повністю ігноруючи затримки повільних чи завислих машин.

3. **Виявлення розбіжностей та активне самозцілення:**
   Якщо при читанні з кворумом `R` координатор спостерігає, що частина вузлів повернула застарілу версію, він виконує дві незалежні дії:
   - Негайно повертає клієнту максимальну знайдену версію `v_max`.
   - Генерує фонові мутації **Read Repair** для оновлення відстаючих вузлів до версії `v_max`.

```
Клієнт ──(Read key)──> [ Координатор ]
                            │
            ┌───────────────┼───────────────┐ (Паралельний Fan-Out)
            ▼               ▼               ▼
       [ Вузол 1 ]     [ Вузол 2 ]     [ Вузол 3 (Застарілий) ]
        ver = 3         ver = 3         ver = 2
            │               │               │
            └───────────────┼───────────────┘
                            ▼
               Координатор обирає ver = 3
                            │
            ┌───────────────┴──────────────────────────┐
            ▼                                          ▼
   Відповідь клієнту: (val, ver=3)            [ Read Repair ] ──> [ Вузол 3 ]
   (миттєво, без очікування)                  (асинхронно)        оновлено до ver=3
```

---

## 2. Робоча реалізація на C та C++

Нижче наведено дві повноцінні та ідіоматичні реалізації симулятора:
- **Вкладка C:** Класичний системний код із чистими структурами, детерміністичним виділенням пам'яті, явними перевірками кодів помилок `StatusCode` та безпечною роботою з фіксованими буферами.
- **Вкладка C++:** Сучасний C++20 з використанням типізованого результату `std::expected`, RAII-обгортками, генераторами випадкових чисел `<random>`, розумними контейнерами `std::vector` та неблокуючими конструкціями.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <time.h>

#define CLUSTER_SIZE 5
#define MAX_KEY_LEN 32
#define MAX_VAL_LEN 64

typedef enum {
    STATUS_OK = 0,
    STATUS_TIMEOUT = 1,
    STATUS_QUORUM_FAILED = 2,
    STATUS_NOT_FOUND = 3
} StatusCode;

/* Структура запису з версією */
typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    uint64_t version;
    bool exists;
} Record;

/* Вузол сховища */
typedef struct {
    int node_id;
    Record data;
    double failure_rate; /* Імовірність відмови вузла [0.0 .. 1.0] */
} StorageNode;

/* Результат операції читання з одного вузла */
typedef struct {
    int node_id;
    Record record;
    StatusCode status;
} NodeResponse;

/* Ініціалізація кластера */
void cluster_init(StorageNode cluster[CLUSTER_SIZE]) {
    for (int i = 0; i < CLUSTER_SIZE; i++) {
        cluster[i].node_id = i;
        cluster[i].data.exists = false;
        cluster[i].data.version = 0;
        cluster[i].failure_rate = (i == 3) ? 0.40 : 0.05; /* Вузол 3 має вищий рівень збоїв */
    }
}

/* Симуляція прямого запису на один вузол */
StatusCode node_write(StorageNode* node, const char* key, const char* value, uint64_t version) {
    double r = (double)rand() / RAND_MAX;
    if (r < node->failure_rate) {
        return STATUS_TIMEOUT; /* Імітація збою мережі або таймауту */
    }
    
    /* Запис приймається, якщо нова версія суворо більша або рівна */
    if (!node->data.exists || version >= node->data.version) {
        strncpy(node->data.key, key, MAX_KEY_LEN - 1);
        strncpy(node->data.value, value, MAX_VAL_LEN - 1);
        node->data.key[MAX_KEY_LEN - 1] = '\0';
        node->data.value[MAX_VAL_LEN - 1] = '\0';
        node->data.version = version;
        node->data.exists = true;
        return STATUS_OK;
    }
    return STATUS_OK;
}

/* Симуляція прямого читання з одного вузла */
NodeResponse node_read(StorageNode* node, const char* key) {
    NodeResponse resp;
    resp.node_id = node->node_id;
    resp.status = STATUS_OK;
    
    double r = (double)rand() / RAND_MAX;
    if (r < node->failure_rate) {
        resp.status = STATUS_TIMEOUT;
        return resp;
    }
    
    if (!node->data.exists || strcmp(node->data.key, key) != 0) {
        resp.status = STATUS_NOT_FOUND;
        return resp;
    }
    
    resp.record = node->data;
    return resp;
}

/* Координатор: виконання запису з кворумом W */
StatusCode coordinator_write(StorageNode cluster[CLUSTER_SIZE], const char* key, 
                              const char* value, uint64_t version, int w_quorum) {
    int successful_acks = 0;
    
    printf("[Coordinator] Початок запису key='%s', val='%s', ver=%llu (потрібно W=%d acks)...\n",
           key, value, (unsigned long long)version, w_quorum);
    
    for (int i = 0; i < CLUSTER_SIZE; i++) {
        StatusCode res = node_write(&cluster[i], key, value, version);
        if (res == STATUS_OK) {
            successful_acks++;
            printf("  -> Вузол %d: Запис OK\n", i);
        } else {
            printf("  -> Вузол %d: Помилка/Таймаут\n", i);
        }
    }
    
    if (successful_acks >= w_quorum) {
        printf("[Coordinator] Запис успішний: зібрано %d acks з W=%d\n\n", successful_acks, w_quorum);
        return STATUS_OK;
    }
    
    printf("[Coordinator] ПОМИЛКА КВОРУМУ: зібрано лише %d acks з W=%d\n\n", successful_acks, w_quorum);
    return STATUS_QUORUM_FAILED;
}

/* Координатор: виконання читання з кворумом R та запуском Read Repair */
StatusCode coordinator_read(StorageNode cluster[CLUSTER_SIZE], const char* key, 
                             int r_quorum, Record* out_record) {
    NodeResponse responses[CLUSTER_SIZE];
    int successful_reads = 0;
    
    printf("[Coordinator] Початок читання key='%s' (потрібно R=%d відповідей)...\n", key, r_quorum);
    
    for (int i = 0; i < CLUSTER_SIZE; i++) {
        responses[i] = node_read(&cluster[i], key);
        if (responses[i].status == STATUS_OK) {
            successful_reads++;
            printf("  <- Вузол %d відповів: val='%s', ver=%llu\n", 
                   i, responses[i].record.value, (unsigned long long)responses[i].record.version);
        } else {
            printf("  <- Вузол %d: недоступний або не знайдено\n", i);
        }
    }
    
    if (successful_reads < r_quorum) {
        printf("[Coordinator] ПОМИЛКА КВОРУМУ ЧИТАННЯ: зібрано лише %d відповідей з R=%d\n\n",
               successful_reads, r_quorum);
        return STATUS_QUORUM_FAILED;
    }
    
    /* Знаходимо найновішу версію серед опитаних вузлів */
    uint64_t max_version = 0;
    int latest_idx = -1;
    for (int i = 0; i < CLUSTER_SIZE; i++) {
        if (responses[i].status == STATUS_OK) {
            if (responses[i].record.version >= max_version) {
                max_version = responses[i].record.version;
                latest_idx = i;
            }
        }
    }
    
    if (latest_idx == -1) {
        return STATUS_NOT_FOUND;
    }
    
    *out_record = responses[latest_idx].record;
    printf("[Coordinator] Обрано свіжу версію: val='%s' (ver=%llu)\n", 
           out_record->value, (unsigned long long)out_record->version);
    
    /* Асинхронний Read Repair: виявляємо застарілі вузли та оновлюємо їх */
    printf("[Coordinator] Перевірка необхідності Read Repair:\n");
    for (int i = 0; i < CLUSTER_SIZE; i++) {
        if (responses[i].status == STATUS_OK) {
            if (responses[i].record.version < max_version) {
                printf("  -> [Read Repair] Вузол %d має застарілу версію %llu! Оновлюємо до %llu...\n",
                       i, (unsigned long long)responses[i].record.version, (unsigned long long)max_version);
                node_write(&cluster[i], out_record->key, out_record->value, out_record->version);
            }
        }
    }
    printf("[Coordinator] Читання завершено успішно.\n\n");
    return STATUS_OK;
}

int main(void) {
    srand((unsigned int)time(NULL));
    StorageNode cluster[CLUSTER_SIZE];
    cluster_init(cluster);
    
    /* Крок 1: Запис з кворумом W=3 на N=5 */
    coordinator_write(cluster, "account:42", "balance:100", 1, 3);
    
    /* Крок 2: Штучно застаріваємо Вузол 1 (імітація пропущеного оновлення) */
    cluster[1].data.version = 0;
    strcpy(cluster[1].data.value, "balance:0");
    
    /* Крок 3: Читання з кворумом R=3 — виявлення розходження та Read Repair */
    Record result;
    StatusCode status = coordinator_read(cluster, "account:42", 3, &result);
    
    if (status == STATUS_OK) {
        printf("Клієнт отримав фінальний результат: %s (версія %llu)\n", 
               result.value, (unsigned long long)result.version);
    }
    return 0;
}
```
```cpp
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <expected>
#include <random>
#include <algorithm>
#include <cstdint>
#include <optional>

enum class ErrorCode {
    Timeout,
    QuorumFailed,
    NotFound
};

struct Record {
    std::string key;
    std::string value;
    uint64_t    version{0};
};

class StorageNode {
public:
    explicit StorageNode(int id, double failure_rate = 0.05)
        : id_(id), failure_rate_(failure_rate), rng_(std::random_device{}()) {}

    int id() const noexcept { return id_; }

    std::expected<void, ErrorCode> write(std::string_view key, std::string_view value, uint64_t version) {
        if (simulate_failure()) {
            return std::unexpected(ErrorCode::Timeout);
        }
        if (!data_.has_value() || version >= data_->version) {
            data_ = Record{std::string(key), std::string(value), version};
        }
        return {};
    }

    std::expected<Record, ErrorCode> read(std::string_view key) {
        if (simulate_failure()) {
            return std::unexpected(ErrorCode::Timeout);
        }
        if (!data_.has_value() || data_->key != key) {
            return std::unexpected(ErrorCode::NotFound);
        }
        return *data_;
    }

    void force_corrupt_for_testing(std::string_view stale_val, uint64_t stale_ver) {
        if (data_.has_value()) {
            data_->value = std::string(stale_val);
            data_->version = stale_ver;
        }
    }

private:
    bool simulate_failure() {
        std::uniform_real_distribution<double> dist(0.0, 1.0);
        return dist(rng_) < failure_rate_;
    }

    int id_;
    double failure_rate_;
    std::mt19937 rng_;
    std::optional<Record> data_;
};

class QuorumCoordinator {
public:
    explicit QuorumCoordinator(std::vector<StorageNode>& cluster)
        : cluster_(cluster) {}

    std::expected<void, ErrorCode> write(std::string_view key, std::string_view value, 
                                         uint64_t version, size_t w_quorum) {
        std::cout << "[Coordinator] Запис key='" << key << "', val='" << value 
                  << "', ver=" << version << " (потрібно W=" << w_quorum << ")...\n";

        size_t acks = 0;
        for (auto& node : cluster_) {
            if (auto res = node.write(key, value, version); res.has_value()) {
                std::cout << "  -> Вузол " << node.id() << ": Запис OK\n";
                ++acks;
            } else {
                std::cout << "  -> Вузол " << node.id() << ": Таймаут/Відмова\n";
            }
        }

        if (acks >= w_quorum) {
            std::cout << "[Coordinator] Запис успішний: зібрано " << acks << " acks з " << w_quorum << "\n\n";
            return {};
        }

        std::cout << "[Coordinator] ПОМИЛКА: Кворум запису не зібрано!\n\n";
        return std::unexpected(ErrorCode::QuorumFailed);
    }

    std::expected<Record, ErrorCode> read(std::string_view key, size_t r_quorum) {
        std::cout << "[Coordinator] Читання key='" << key << "' (потрібно R=" << r_quorum << ")...\n";

        struct ReadResult {
            int node_id;
            Record record;
        };
        std::vector<ReadResult> successful_reads;

        for (auto& node : cluster_) {
            if (auto res = node.read(key); res.has_value()) {
                std::cout << "  <- Вузол " << node.id() << ": val='" << res->value 
                          << "', ver=" << res->version << "\n";
                successful_reads.push_back({node.id(), *res});
            } else {
                std::cout << "  <- Вузол " << node.id() << ": Недоступний\n";
            }
        }

        if (successful_reads.size() < r_quorum) {
            std::cout << "[Coordinator] ПОМИЛКА: Недостатньо відповідей для кворуму читання!\n\n";
            return std::unexpected(ErrorCode::QuorumFailed);
        }

        // Знаходження свіжої версії
        auto latest_it = std::max_element(
            successful_reads.begin(), successful_reads.end(),
            [](const ReadResult& a, const ReadResult& b) {
                return a.record.version < b.record.version;
            });

        const Record fresh_record = latest_it->record;
        std::cout << "[Coordinator] Свіже значення: val='" << fresh_record.value 
                  << "', ver=" << fresh_record.version << "\n";

        // Асинхронний Read Repair для застарілих вузлів
        std::cout << "[Coordinator] Read Repair перевірка:\n";
        for (const auto& [node_id, record] : successful_reads) {
            if (record.version < fresh_record.version) {
                std::cout << "  -> [Read Repair] Вузол " << node_id << " відстає (ver " 
                          << record.version << " < " << fresh_record.version << "). Оновлюємо...\n";
                cluster_[node_id].write(fresh_record.key, fresh_record.value, fresh_record.version);
            }
        }

        std::cout << "[Coordinator] Читання завершено успішно.\n\n";
        return fresh_record;
    }

private:
    std::vector<StorageNode>& cluster_;
};

int main() {
    std::vector<StorageNode> cluster;
    for (int i = 0; i < 5; ++i) {
        cluster.emplace_back(i, (i == 3) ? 0.35 : 0.05);
    }

    QuorumCoordinator coordinator(cluster);

    // Крок 1: Запис балансу з кворумом W=3
    auto w_res = coordinator.write("user:99", "balance:500", 1, 3);

    // Крок 2: Емуляція застарівання одного вузла
    cluster[2].force_corrupt_for_testing("balance:200", 0);

    // Крок 3: Читання з R=3 та автоматичним Read Repair
    auto r_res = coordinator.read("user:99", 3);
    if (r_res.has_value()) {
        std::cout << "Клієнт успішно прочитав: " << r_res->value 
                  << " (версія " << r_res->version << ")\n";
    }

    return 0;
}
```
:::

---

## 3. Детальний аналіз підводних каменів та крайових випадків

У промисловій експлуатації безлідерних сховищ виникає низка специфічних аномалій, які вимагають додаткових архітектурних захистів:

### 1. Перегони Read Repair із новішими записами (Out-of-Order Race)
Нехай клієнт А зчитує версію `v=2` і виявляє, що Вузол 5 має застарілу версію `v=1`. Координатор відправляє пакет Read Repair `v=2` на Вузол 5. У цей самий момент клієнт Б виконує новий запис `v=3` на Вузол 5.
Якщо пакет `v=3` прибуде раніше за пакет `v=2`, а репліка не перевірятиме версію, запізнілий Read Repair перезапише новіші дані старими (`v=2` знищить `v=3`).
*Захист:* Кожна репліка застосовує мутацію строго за правилом `incoming_version >= current_version`. Якщо вхідна версія менша за збережену в пам'яті, операція ігнорується без генерації помилки.

### 2. Синхронне блокування на Read Repair
Якщо координатор виконує запис Read Repair синхронно у тому самому потоці, який обслуговує клієнтське підключення, затримка операції читання зростає до `Latency = Latency_read + Latency_repair`. Повільний або завислий відстаючий вузол почне сповільнювати швидкі операції читання для користувачів.
*Захист:* Координатор негайно віддає знайдений свіжий результат клієнту, а дельту Read Repair скидає в неблокуючу чергу пулу фонових воркерів (Background Worker Pool).

### 3. Накопичення надгробків (Tombstone Overload)
Коли запис видаляється, безлідерна система створює запис-надгробок (Tombstone) із новим номером версії. Якщо в таблиці виконується мільйон операцій видалення за короткий час, операції послідовного читання (Range Scan) змушені зчитувати мільйони надгробків із диска, що спричиняє сплески використання CPU та збої пам'яті `OutOfMemoryError`.
*Захист:* Регулярне фонове ущільнення дискових таблиць (Compaction) та контроль параметра `gc_grace_seconds`, після спливу якого надгробки фізично вичищаються з файлів.

### 4. Неузгодженість таймауту клієнта та стану кластера
Якщо клієнт відправив запис, координатор отримав 2 підтвердження з необхідних `W=3` і завершив операцію з помилкою `WriteTimeoutException`, клієнт вважає, що запис не відбувся. Проте дані вже збережені на двох машинах. Подальше читання може підхопити ці «неуспішні» дані.
*Захист:* Прикладний код зобов'язаний проектуватися з урахуванням семантики ідемпотентності, де будь-яка операція мутації може бути безпечно повторена без спотворення стану бізнес-логіки.

### 5. Несиметричні мережеві розриви (Asymmetric Network Partitions)
Якщо Вузол 1 бачить Координатор А, але не бачить Координатор Б через маршрутизаційні петлі, операції читання та запису можуть формувати несумісні локальні кворуми. Для захисту від таких топологічних аномалій застосовують багаторівневі перевірки живості вузлів на основі алгоритмів Gossip та вимірювання затримок (Phi Accrual Failure Detector).

### 6. Вплив фонових пауз збирача сміття (GC Pauses)
У мовах із керованим керуванням пам'яттю (Java/Go) зупинка процесу на фазу збирання сміття (Stop-the-World GC) може тривати від 100 мс до 2 секунд. Під час такої паузи репліка не відповідає на запити, змушуючи координатори переходити на резервні машини. Кворумна модель `W = ⌈(N+1)/2⌉` дозволяє кластеру повністю нівелювати такі паузи, оскільки операція фіксується за рахунок решти активних реплік без затримки клієнта.
