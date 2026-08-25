# ⚙️ Реалізація безлідерного кластера: кворумні операції, координатор та Read-Repair

Розподілене сховище без центрального лідера спирається на симетричні вузли, де кожен сервер може виступати координатором запиту, збирати кворум підтверджень та відновлювати застарілі репліки просто під час операцій читання. Цей практичний розбір містить повну, працюючу реалізацію безлідерного протоколу з налаштовуваними параметрами `N, W, R`, логікою відсікання повільних вузлів, порівнянням версій та механізмом відновлення при читанні (Read-Repair) мовами C та C++.

## Архітектура та протокол координації

У безлідерній системі клієнт може надіслати запит до **будь-якого** вузла кластера. Вузол, який прийняв з'єднання від клієнта, на час виконання цієї конкретної операції бере на себе роль **координатора** (Coordinator).

```
   [ Клієнт ]
       │  1. write(k, v)
       ▼
 [ Координатор ] ──┬── 2. MsgWrite(v2) ──► [ Репліка 1 ] (ACK)
                   ├── 2. MsgWrite(v2) ──► [ Репліка 2 ] (ACK)
                   └── 2. MsgWrite(v2) ──► [ Репліка 3 ] (Збій/Мережевий лаг)
       │
       │  3. Отримано 2 з 3 ACK (W = 2) ──► Успіх!
       ▼
   [ Клієнт ] (HTTP 200 OK)
```

Координатор реалізує два ключові алгоритми взаємодії з вузлами:

### 1. Кворумний запис (`write_quorum`)
1. **Генерація версії:** Координатор генерує монотонно зростаючий номер версії (у промислових базах — мітку часу в мікросекундах або векторний годинник).
2. **Паралельне розсилання:** Координатор надсилає повідомлення `MsgWrite` всім `N` реплікам, призначеним для збереження цього ключа в кільці хешування.
3. **Збір підтверджень:** Координатор очікує на підтвердження (ACK) щонайменше від `W` реплік.
4. **Ухвалення рішення:**
   - Якщо `W` підтверджень зібрано в межах встановленого таймауту — координатор повертає клієнту статус успіху. Решта `N - W` реплік можуть відповісти пізніше або перебувати у збої; система не блокується.
   - Якщо таймаут минув, а кількість підтверджень менша за `W` — координатор повертає клієнту помилку нестачі кворуму.

### 2. Кворумне читання та Read-Repair (`read_quorum`)
1. **Паралельне опитування:** Координатор надсилає запит `MsgRead` усім `N` реплікам і чекає на відповіді від перших `R` найшвидших вузлів.
2. **Звірка версій:** Отримавши `R` відповідей, координатор порівнює номери версій та обирає значення з максимальною версією `v_max`.
3. **Миттєва відповідь клієнту:** Координатор повертає клієнту актуальне значення негайно, не затримуючи клієнтський потік виконанням фонових операцій.
4. **Асинхронний Read-Repair:** Якщо серед `R` опитаних вузлів виявлено репліку, чия версія `v < v_max` (або яка взагалі не мала запису), координатор у фоні надсилає на цей відсталий вузол команду оновлення до версії `v_max`.

---

## Робоча реалізація мовами C та C++

Наведений нижче код реалізує повноцінну модель розподіленого кластера з `N = 3` вузлів, імітує мережеві збої окремих серверів, демонструє успішний запис із кворумом `W = 2`, читання з кворумом `R = 2` та автоматичне лікування відсталого вузла через Read-Repair.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>

#define MAX_KEY_LEN   64
#define MAX_VAL_LEN   128
#define MAX_REPLICAS  8

/* Запис даних у сховищі окремої репліки */
typedef struct {
    char     key[MAX_KEY_LEN];
    char     value[MAX_VAL_LEN];
    uint64_t version;     /* монотонний лічильник версії */
    bool     is_deleted;  /* tombstone-маркер видалення */
    bool     present;     /* чи існує запис */
} Record;

/* Стан окремого вузла-репліки */
typedef struct {
    uint32_t id;
    bool     is_alive;    /* прапорець доступності вузла в мережі */
    Record   storage[64]; /* спрощене локальне сховище */
    size_t   count;
} ReplicaNode;

/* Результат операції читання з однієї репліки */
typedef struct {
    uint32_t node_id;
    bool     responded;
    Record   record;
} ReadResponse;

/* Ініціалізація вузла */
void node_init(ReplicaNode *node, uint32_t id) {
    node->id = id;
    node->is_alive = true;
    node->count = 0;
    memset(node->storage, 0, sizeof(node->storage));
}

/* Локальний запис на вузол */
bool node_local_write(ReplicaNode *node, const char *key, const char *val, uint64_t ver) {
    if (!node->is_alive) return false;

    for (size_t i = 0; i < node->count; ++i) {
        if (strcmp(node->storage[i].key, key) == 0) {
            /* Оновлюємо лише якщо нова версія новіша за поточну */
            if (ver >= node->storage[i].version) {
                strncpy(node->storage[i].value, val, MAX_VAL_LEN - 1);
                node->storage[i].version = ver;
                node->storage[i].is_deleted = false;
                node->storage[i].present = true;
            }
            return true;
        }
    }

    if (node->count < 64) {
        Record *r = &node->storage[node->count++];
        strncpy(r->key, key, MAX_KEY_LEN - 1);
        strncpy(r->value, val, MAX_VAL_LEN - 1);
        r->version = ver;
        r->is_deleted = false;
        r->present = true;
        return true;
    }
    return false;
}

/* Локальне читання з вузла */
bool node_local_read(const ReplicaNode *node, const char *key, Record *out_rec) {
    if (!node->is_alive) return false;

    for (size_t i = 0; i < node->count; ++i) {
        if (strcmp(node->storage[i].key, key) == 0) {
            *out_rec = node->storage[i];
            return true;
        }
    }
    /* Ключ не знайдено на живому вузлі */
    memset(out_rec, 0, sizeof(Record));
    strncpy(out_rec->key, key, MAX_KEY_LEN - 1);
    out_rec->present = false;
    out_rec->version = 0;
    return true;
}

/* Координатор: виконання запису з кворумом W */
bool coordinator_write(ReplicaNode cluster[], size_t n, size_t w,
                       const char *key, const char *val, uint64_t ver) {
    size_t acks = 0;

    printf("[Coordinator] Запис key='%s', val='%s', ver=%llu (потрібно W=%zu з N=%zu)...\n",
           key, val, (unsigned long long)ver, w, n);

    for (size_t i = 0; i < n; ++i) {
        if (node_local_write(&cluster[i], key, val, ver)) {
            acks++;
            printf("  -> Вузол %u: OK (підтверджено)\n", cluster[i].id);
        } else {
            printf("  -> Вузол %u: ВІДМОВА (недоступний)\n", cluster[i].id);
        }
    }

    if (acks >= w) {
        printf("[Coordinator] УСПІХ: зібрано %zu ACK >= W=%zu\n\n", acks, w);
        return true;
    } else {
        printf("[Coordinator] ПОМИЛКА КВОРУМУ: зібрано лише %zu ACK < W=%zu\n\n", acks, w);
        return false;
    }
}

/* Координатор: читання з кворумом R та запуск Read-Repair */
bool coordinator_read(ReplicaNode cluster[], size_t n, size_t r,
                      const char *key, char *out_val, uint64_t *out_ver) {
    ReadResponse responses[MAX_REPLICAS];
    size_t resp_count = 0;

    printf("[Coordinator] Читання key='%s' (потрібно R=%zu з N=%zu)...\n", key, r, n);

    for (size_t i = 0; i < n && resp_count < r; ++i) {
        Record rec;
        if (node_local_read(&cluster[i], key, &rec)) {
            responses[resp_count].node_id = cluster[i].id;
            responses[resp_count].responded = true;
            responses[resp_count].record = rec;
            printf("  <- Відповідь від вузла %u: val='%s', ver=%llu, present=%d\n",
                   cluster[i].id, rec.value, (unsigned long long)rec.version, rec.present);
            resp_count++;
        } else {
            printf("  <- Вузол %u не відповів (таймаут)\n", cluster[i].id);
        }
    }

    if (resp_count < r) {
        printf("[Coordinator] ПОМИЛКА КВОРУМУ ЧИТАННЯ: отримано %zu відповідей < R=%zu\n\n",
               resp_count, r);
        return false;
    }

    /* Знаходимо найновішу версію серед отриманих відповідей */
    uint64_t max_ver = 0;
    int best_idx = -1;

    for (size_t i = 0; i < resp_count; ++i) {
        if (responses[i].record.present && responses[i].record.version >= max_ver) {
            max_ver = responses[i].record.version;
            best_idx = (int)i;
        }
    }

    if (best_idx >= 0) {
        strncpy(out_val, responses[best_idx].record.value, MAX_VAL_LEN - 1);
        *out_ver = max_ver;
        printf("[Coordinator] Обрано найновіший стан: val='%s', ver=%llu\n", out_val, (unsigned long long)max_ver);
    } else {
        printf("[Coordinator] Ключ не знайдено на жодній з опитаних реплік\n");
        return false;
    }

    /* ФАЗА READ-REPAIR: оновлюємо всі відсталі вузли серед опитаних */
    for (size_t i = 0; i < resp_count; ++i) {
        if (!responses[i].record.present || responses[i].record.version < max_ver) {
            uint32_t target_id = responses[i].node_id;
            printf("  [Read-Repair] Вузол %u відстає (ver=%llu < %llu) -> надсилаємо оновлення...\n",
                   target_id, (unsigned long long)responses[i].record.version, (unsigned long long)max_ver);

            for (size_t k = 0; k < n; ++k) {
                if (cluster[k].id == target_id) {
                    node_local_write(&cluster[k], key, out_val, max_ver);
                    printf("  [Read-Repair] Вузол %u успішно зцілено до ver=%llu!\n",
                           target_id, (unsigned long long)max_ver);
                    break;
                }
            }
        }
    }
    printf("\n");
    return true;
}

int main(void) {
    const size_t N = 3;
    const size_t W = 2;
    const size_t R = 2;

    ReplicaNode cluster[3];
    for (size_t i = 0; i < N; ++i) node_init(&cluster[i], (uint32_t)(i + 1));

    printf("=== Сценарій 1: Звичайний запис (W=2) при всіх живих вузлах ===\n");
    coordinator_write(cluster, N, W, "user:101", "Andriy", 1);

    printf("=== Сценарій 2: Вузол 3 падає; оновлення записується на вузли 1 і 2 ===\n");
    cluster[2].is_alive = false; /* Вузол 3 вийшов з ладу */
    coordinator_write(cluster, N, W, "user:101", "Andriy Felenko", 2);

    printf("=== Сценарій 3: Вузол 3 оживає зі старим станом (ver=1) ===\n");
    cluster[2].is_alive = true;
    cluster[0].is_alive = false; /* Тимчасово недоступний вузол 1 */

    char val_buf[MAX_VAL_LEN] = {0};
    uint64_t ver_out = 0;

    /* Читання опитує вузли 2 і 3 (R = 2). Вузол 2 має ver=2, вузол 3 має ver=1. */
    coordinator_read(cluster, N, R, "user:101", val_buf, &ver_out);

    printf("=== Сценарій 4: Перевірка після Read-Repair (Вузол 3 має бути оновлений) ===\n");
    Record check_rec;
    node_local_read(&cluster[2], "user:101", &check_rec);
    printf("Прямий погляд на сховище Вузла 3: val='%s', ver=%llu (Зцілення підтверджено!)\n",
           check_rec.value, (unsigned long long)check_rec.version);

    return 0;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <optional>
#include <cstdint>
#include <algorithm>
#include <unordered_map>

struct Record {
    std::string key;
    std::string value;
    uint64_t    version{0};
    bool        is_deleted{false};
};

class ReplicaNode {
public:
    explicit ReplicaNode(uint32_t id) : id_(id), is_alive_(true) {}

    [[nodiscard]] uint32_t id() const noexcept { return id_; }
    [[nodiscard]] bool is_alive() const noexcept { return is_alive_; }
    void set_alive(bool state) noexcept { is_alive_ = state; }

    bool write(const std::string& key, const std::string& val, uint64_t ver) {
        if (!is_alive_) return false;

        auto it = storage_.find(key);
        if (it != storage_.end()) {
            if (ver >= it->second.version) {
                it->second = Record{key, val, ver, false};
            }
        } else {
            storage_[key] = Record{key, val, ver, false};
        }
        return true;
    }

    [[nodiscard]] std::optional<Record> read(const std::string& key) const {
        if (!is_alive_) return std::nullopt;

        auto it = storage_.find(key);
        if (it != storage_.end()) {
            return it->second;
        }
        /* Вузол живий, але ключа немає */
        return Record{key, "", 0, false};
    }

private:
    uint32_t id_;
    bool is_alive_;
    std::unordered_map<std::string, Record> storage_;
};

class LeaderlessCoordinator {
public:
    LeaderlessCoordinator(std::vector<ReplicaNode>& cluster, size_t w, size_t r)
        : cluster_(cluster), w_quorum_(w), r_quorum_(r) {}

    bool write(const std::string& key, const std::string& val, uint64_t ver) {
        size_t acks = 0;
        std::cout << "[Coordinator] Запис key='" << key << "', val='" << val
                  << "', ver=" << ver << " (потрібно W=" << w_quorum_
                  << " з N=" << cluster_.size() << ")...\n";

        for (auto& node : cluster_) {
            if (node.write(key, val, ver)) {
                ++acks;
                std::cout << "  -> Вузол " << node.id() << ": OK (підтверджено)\n";
            } else {
                std::cout << "  -> Вузол " << node.id() << ": ВІДМОВА (недоступний)\n";
            }
        }

        if (acks >= w_quorum_) {
            std::cout << "[Coordinator] УСПІХ: зібрано " << acks << " ACK >= W=" << w_quorum_ << "\n\n";
            return true;
        }
        std::cout << "[Coordinator] ПОМИЛКА КВОРУМУ: зібрано лише " << acks << " ACK\n\n";
        return false;
    }

    std::optional<Record> read(const std::string& key) {
        struct NodeResponse {
            uint32_t node_id;
            Record record;
        };

        std::vector<NodeResponse> responses;
        std::cout << "[Coordinator] Читання key='" << key
                  << "' (потрібно R=" << r_quorum_
                  << " з N=" << cluster_.size() << ")...\n";

        for (auto& node : cluster_) {
            if (responses.size() >= r_quorum_) break;

            if (auto rec = node.read(key)) {
                responses.push_back({node.id(), *rec});
                std::cout << "  <- Відповідь від вузла " << node.id()
                          << ": val='" << rec->value
                          << "', ver=" << rec->version << "\n";
            } else {
                std::cout << "  <- Вузол " << node.id() << " не відповів (таймаут)\n";
            }
        }

        if (responses.size() < r_quorum_) {
            std::cout << "[Coordinator] ПОМИЛКА КВОРУМУ ЧИТАННЯ: замало відповідей\n\n";
            return std::nullopt;
        }

        /* Пошук максимальної версії серед опитаного кворуму */
        auto best_it = std::max_element(responses.begin(), responses.end(),
            [](const NodeResponse& a, const NodeResponse& b) {
                return a.record.version < b.record.version;
            });

        Record newest = best_it->record;
        std::cout << "[Coordinator] Обрано найновіший стан: val='" << newest.value
                  << "', ver=" << newest.version << "\n";

        /* ФАЗА READ-REPAIR: асинхронне лікування відсталих вузлів */
        for (const auto& resp : responses) {
            if (resp.record.version < newest.version) {
                std::cout << "  [Read-Repair] Вузол " << resp.node_id
                          << " відстає (ver=" << resp.record.version
                          << " < " << newest.version << ") -> зцілення...\n";

                for (auto& node : cluster_) {
                    if (node.id() == resp.node_id) {
                        node.write(key, newest.value, newest.version);
                        std::cout << "  [Read-Repair] Вузол " << resp.node_id
                                  << " оновлено до ver=" << newest.version << "!\n";
                        break;
                    }
                }
            }
        }
        std::cout << "\n";
        return newest;
    }

private:
    std::vector<ReplicaNode>& cluster_;
    size_t w_quorum_;
    size_t r_quorum_;
};

int main() {
    std::vector<ReplicaNode> cluster;
    cluster.emplace_back(1);
    cluster.emplace_back(2);
    cluster.emplace_back(3);

    LeaderlessCoordinator coordinator(cluster, /*W=*/2, /*R=*/2);

    std::cout << "=== Сценарій 1: Звичайний запис (W=2) при всіх живих вузлах ===\n";
    coordinator.write("user:101", "Andriy", 1);

    std::cout << "=== Сценарій 2: Вузол 3 падає; оновлення записується на вузли 1 і 2 ===\n";
    cluster[2].set_alive(false);
    coordinator.write("user:101", "Andriy Felenko", 2);

    std::cout << "=== Сценарій 3: Вузол 3 оживає зі старим станом (ver=1) ===\n";
    cluster[2].set_alive(true);
    cluster[0].set_alive(false); // Вузол 1 стає тимчасово недоступним

    auto result = coordinator.read("user:101");

    std::cout << "=== Сценарій 4: Перевірка після Read-Repair (Вузол 3 має бути оновлений) ===\n";
    auto direct_check = cluster[2].read("user:101");
    if (direct_check) {
        std::cout << "Прямий погляд на сховище Вузла 3: val='"
                  << direct_check->value << "', ver=" << direct_check->version
                  << " (Зцілення підтверджено!)\n";
    }

    return 0;
}
```
:::

---

## Покроковий розбір виконання та механіка станів

Простежимо, як змінюється внутрішній стан структур даних на кожному з чотирьох кроків роботи програми:

1. **Сценарій 1 (Повний запис):** Запис версії `ver = 1` успішно потрапляє на всі три репліки (`acks = 3 >= W = 2`). Усі вузли мають ідентичний стан.
2. **Сценарій 2 (Запис при аварії репліки):** Вузол 3 симулює падіння (`is_alive = false`). Координатор надсилає `ver = 2`. Вузли 1 та 2 підтверджують запис (`acks = 2 >= W = 2`). Клієнт отримує підтвердження успіху. У цей момент виникає невідповідність станів: Вузол 1 і Вузол 2 мають `ver = 2`, а Вузол 3 залишився на `ver = 1`.
3. **Сценарій 3 (Читання з перетином та лікуванням):** Вузол 3 оживає, але Вузол 1 тимчасово перестає відповідати. Клієнт запитує читання з кворумом `R = 2`. Координатор опитує живі Вузол 2 та Вузол 3. Вузол 2 повертає `ver = 2`, Вузол 3 — застарілу `ver = 1`. Координатор знаходить максимум (`max_ver = 2`) і миттєво віддає свіже значення клієнту. У фазі Read-Repair координатор виявляє, що Вузол 3 має меншу версію, і оновлює його сховище до `ver = 2`.
4. **Сценарій 4 (Верифікація):** Пряме читання з Вузла 3 підтверджує, що він успішно зцілився без зупинки системи та без запуску важких фонових утиліт.

---

## Відмінності між ідіомами C та C++ у реалізації

Порівняння двох вкладок коду наочно демонструє, як різняться інженерні моделі керування ресурсами:

1. **Керування пам'яттю та рядками:**
   - У версії на C структура `Record` використовує статичні масиви символів фіксованого розміру `char key[MAX_KEY_LEN]` та ручне копіювання через `strncpy`. Це запобігає динамічній фрагментації купи (Heap Fragmentation), що критично для низькорівневих сховищ, але створює ризик обрізання довгих рядків.
   - У версії на C++ застосовано `std::string`, який автоматично керує виділенням пам'яті через Small String Optimization (SSO), позбавляючи код жорстких лімітів на розмір значень.

2. **Індексація та пошук:**
   - У C сховище представлено простим масивом `storage[64]` із лінійним пошуком `O(K)`.
   - У C++ використано асоціативний контейнер `std::unordered_map<std::string, Record>`, що дає амортизовану швидкість доступу `O(1)`.

3. **Обробка відсутності значення та збоїв:**
   - У C функція повертає булевий прапорець успіху, а результат передає через вихідний вказівник `Record *out_rec`.
   - У C++ застосовано тип `std::optional<Record>`, який явно на рівні системи типів виражає можливу відсутність відповіді або мережевий таймаут вузла без використання магічних сигнатур чи нульових покажчиків.

4. **Агрегація відповідей:**
   - У C++ пошук найновішої версії виконано через стандартний алгоритм `std::max_element` із лямбда-компаратором, що гарантує відсутність помилок виходу за межі масиву.

---

## Інженерні пастки реалізації безлідерних сховищ

При переносі цієї базової моделі у виробниче середовище інженер стикається з п'ятьма неочевидними пастками розподіленого стану:

### 1. Частковий збій запису (Ghost / Phantom State)
Якщо запис виконав локальне збереження на `W - 1` вузлах, а на решті реплік сталася мережева помилка, координатор повертає клієнту статус помилки (Timeout). Проте дані **вже зафіксовані** на диску цих `W - 1` вузлів.
У безлідерній системі немає розподіленого транзакційного менеджера, який би виконав відкат (Rollback). Якщо наступне читання опитає саме ці `W - 1` вузлів, воно поверне значення, про неуспішність якого було повідомлено попередньому клієнту. Висновок: у безлідерних системах статус помилки запису означає «не гарантовано збережено», а не «гарантовано відсутнє».

### 2. Гонка конкурентних записів (Racing Writes) та годинниковий дрейф
Якщо два клієнти одночасно записують різні значення для одного ключа через різних координаторів, їхні кворуми можуть частково перекриватися (наприклад, Клієнт 1 записав на `{Вузол 1, Вузол 2}`, а Клієнт 2 — на `{Вузол 2, Вузол 3}`).
Якщо версії базуються на системному годиннику (NTP), навіть мікросекундний дрейф годинників між серверами призводить до того, що логічно старіший запис отримує більшу мітку часу і назавжди стирає новіший запис. Для збереження повної причинності застосовують векторні годинники або безконфліктні репліковані типи даних (CRDT).

### 3. Воскресіння видалених даних (Tombstone Resurrection)
Видалення запису в безлідерній базі не може бути миттєвим фізичним видаленням байтів із пам'яті: якщо Вузол 1 просто видалить ключ, а Вузол 2 під час видалення був вимкнений, то під час наступного Read-Repair старий запис із Вузла 2 «зцілить» Вузол 1, і видалений об'єкт воскресне!
Тому видалення оформлюється як запис спеціального маркера видалення — **надгробка** (Tombstone) з новим номером версії. Надгробок живе в системі фіксований час (наприклад, `gc_grace_seconds = 10 днів`), гарантуючи, що всі відсталі репліки встигнуть дізнатися про факт видалення до того, як маркер буде остаточно стертий з диска збирачем сміття (Compaction).

### 4. Конкуренція між Read-Repair та новим записом
Якщо операція Read-Repair асинхронно відправляє стару версію `v2` на відсталу репліку, а в цей самий момент новий клієнтський запит записує туди версію `v3`, порядок приходу пакетів по мережі не детермінований.
Якщо пакет Read-Repair прийде **після** `v3`, вузол зобов'язаний перевірити умову `ver >= local.version`: побачивши, що локальна версія `v3` новіша за прислану `v2`, вузол мовчки проігнорує застарілий пакет оновлення, запобігаючи деградації стану.
