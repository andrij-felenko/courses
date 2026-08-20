# ⚙️ Реалізація рушія реконсиляції Scuttlebutt мовами C та C++

У розподілених системах зв'язок між вузлами через плітки вимагає високоефективної реконсиляції стану без блокувань та без перевищення ліміту розміру мережевого пакета (MTU). Реалізація протоколу Scuttlebutt повинна гарантувати:
1. Компактне представлення дайджесту версій розміром `O(N)`;
2. Безпечне пакування дельт у буфер фіксованого розміру з дотриманням монотонного префікса версій;
3. Обробку трьох фаз рукостискання: `SYN -> ACK -> ACK2`.

Нижче наведено робочу реалізацію рушія реконсиляції Scuttlebutt двома мовами — чистим C та ідіоматичним C++20.

---

## 1. Модель пам'яті та структури даних

У центрі архітектури Scuttlebutt лежить структура `EndpointState`, яка зберігає стан окремого сервера. Вона містить 64-бітну епоху запуску `generation`, максимальну відому версію `max_version` та таблицю іменованих атрибутів `ApplicationState`.

У C-реалізації для максимальної швидкодії та відсутності динамічної фрагментації пам'яті на купі (*heap fragmentation*) використовуються статичні буфери та масиви фіксованого розміру. У C++20 версії застосовуються безпечні контейнери `std::unordered_map`, `std::vector` та неволодіючі представлення `std::string_view` та `std::span`, що забезпечують нульове копіювання при читанні мережевих буферів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_NODES 64
#define MAX_KEYS_PER_NODE 32
#define MAX_STR_LEN 64
#define MTU_PAYLOAD_LIMIT 1200

/* Окремий атрибут стану вузла */
typedef struct {
    char key[MAX_STR_LEN];
    char value[MAX_STR_LEN];
    uint64_t version;
} VersionedValue;

/* Повний стан одного конкретного вузла */
typedef struct {
    char node_id[MAX_STR_LEN];
    uint64_t generation;
    uint64_t max_version;
    VersionedValue values[MAX_KEYS_PER_NODE];
    size_t value_count;
} EndpointState;

/* Елемент дайджесту для швидкого порівняння версій */
typedef struct {
    char node_id[MAX_STR_LEN];
    uint64_t generation;
    uint64_t max_version;
} GossipDigest;

/* Окреме оновлення конкретного ключа для передачі мережею */
typedef struct {
    char node_id[MAX_STR_LEN];
    uint64_t generation;
    char key[MAX_STR_LEN];
    char value[MAX_STR_LEN];
    uint64_t version;
} GossipDelta;

/* Локальне сховище знань про весь кластер */
typedef struct {
    char local_node_id[MAX_STR_LEN];
    EndpointState nodes[MAX_NODES];
    size_t node_count;
} ScuttlebuttEngine;
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <algorithm>
#include <cstdint>
#include <optional>
#include <span>

inline constexpr size_t MTU_PAYLOAD_LIMIT = 1200;

struct VersionedValue {
    std::string value;
    uint64_t version{0};
};

struct EndpointState {
    uint64_t generation{0};
    uint64_t max_version{0};
    std::unordered_map<std::string, VersionedValue> attributes;

    void update_attribute(std::string_view key, std::string_view val) {
        ++max_version;
        attributes[std::string(key)] = VersionedValue{std::string(val), max_version};
    }
};

struct GossipDigest {
    std::string node_id;
    uint64_t generation{0};
    uint64_t max_version{0};
};

struct GossipDelta {
    std::string node_id;
    uint64_t generation{0};
    std::string key;
    std::string value;
    uint64_t version{0};
};
```
:::

---

## 2. Формування дельт з контролем MTU та збереженням префікса версій

Найкритичнішим механізмом Scuttlebutt є генерація дельт. Якщо між двома серверами накопичилося більше змін, ніж може вмістити пакет (1200 байтів), алгоритм сортує зміни кожного вузла строго за зростанням версій `version` і додає їх у пакет лише послідовно.

Алгоритм виконує такі кроки:
1. Для кожного вузла локального сховища знаходиться відповідний запис у дайджесті партнера;
2. Якщо покоління локального вузла вище за покоління партнера або партнер узагалі не має запису про цей вузол, партнер отримує всі наявні ключі;
3. Якщо покоління збігаються, вибираються лише ті ключі, чий номер версії строго перевищує `max_version` із дайджесту партнера;
4. Відібрані дельти вузла сортуються за зростанням версії;
5. Дельти пакуються в буфер доти, доки розмір пакета не досягне ліміту `MTU_PAYLOAD_LIMIT`. Щойно ліміт вичерпано, пакування негайно зупиняється на останньому повному елементі.

Цей порядок гарантує, що при отриманні частини оновлень одержувач зафіксує неперервний діапазон версій, не створюючи прогалин у нумерації.

:::tabs
```c
/* Допоміжне сортування дельт за версією для гарантії інваріанта префікса */
static int compare_deltas_by_version(const void *a, const void *b) {
    const GossipDelta *da = (const GossipDelta *)a;
    const GossipDelta *db = (const GossipDelta *)b;
    if (da->version < db->version) return -1;
    if (da->version > db->version) return 1;
    return 0;
}

/* Генерація дельт для партнера на основі його дайджесту */
size_t collect_deltas_for_peer(const ScuttlebuttEngine *engine,
                               const GossipDigest *peer_digest,
                               size_t peer_digest_len,
                               GossipDelta *out_deltas,
                               size_t max_out_deltas) {
    size_t total_deltas = 0;
    size_t approx_bytes = 0;

    for (size_t i = 0; i < engine->node_count; ++i) {
        const EndpointState *local_node = &engine->nodes[i];
        
        /* Шукаємо запис про цей вузол у дайджесті партнера */
        const GossipDigest *peer_entry = NULL;
        for (size_t j = 0; j < peer_digest_len; ++j) {
            if (strcmp(peer_digest[j].node_id, local_node->node_id) == 0) {
                peer_entry = &peer_digest[j];
                break;
            }
        }

        /* Тимчасовий масив для дельт цього конкретного вузла */
        GossipDelta node_deltas[MAX_KEYS_PER_NODE];
        size_t node_delta_count = 0;

        if (peer_entry == NULL || local_node->generation > peer_entry->generation) {
            /* Партнер нічого не знає або його покоління застаріло: віддаємо всі ключі */
            for (size_t k = 0; k < local_node->value_count; ++k) {
                GossipDelta *d = &node_deltas[node_delta_count++];
                strncpy(d->node_id, local_node->node_id, MAX_STR_LEN - 1);
                d->generation = local_node->generation;
                strncpy(d->key, local_node->values[k].key, MAX_STR_LEN - 1);
                strncpy(d->value, local_node->values[k].value, MAX_STR_LEN - 1);
                d->version = local_node->values[k].version;
            }
        } else if (local_node->generation == peer_entry->generation &&
                   local_node->max_version > peer_entry->max_version) {
            /* Покоління збігається, але ми маємо свіжіші версії */
            for (size_t k = 0; k < local_node->value_count; ++k) {
                if (local_node->values[k].version > peer_entry->max_version) {
                    GossipDelta *d = &node_deltas[node_delta_count++];
                    strncpy(d->node_id, local_node->node_id, MAX_STR_LEN - 1);
                    d->generation = local_node->generation;
                    strncpy(d->key, local_node->values[k].key, MAX_STR_LEN - 1);
                    strncpy(d->value, local_node->values[k].value, MAX_STR_LEN - 1);
                    d->version = local_node->values[k].version;
                }
            }
        }

        /* Сортуємо дельти цього вузла за зростанням версій */
        qsort(node_deltas, node_delta_count, sizeof(GossipDelta), compare_deltas_by_version);

        /* Додаємо в вихідний пакет з контролем MTU */
        for (size_t k = 0; k < node_delta_count; ++k) {
            size_t item_size = sizeof(GossipDelta);
            if (approx_bytes + item_size > MTU_PAYLOAD_LIMIT || total_deltas >= max_out_deltas) {
                return total_deltas; /* Пакет заповнено без створення дірок у версіях */
            }
            out_deltas[total_deltas++] = node_deltas[k];
            approx_bytes += item_size;
        }
    }

    return total_deltas;
}
```
```cpp
class ScuttlebuttEngine {
public:
    explicit ScuttlebuttEngine(std::string local_id, uint64_t initial_generation)
        : local_node_id_(std::move(local_id)) {
        cluster_state_[local_node_id_].generation = initial_generation;
    }

    void mutate_local_key(std::string_view key, std::string_view val) {
        cluster_state_[local_node_id_].update_attribute(key, val);
    }

    std::vector<GossipDigest> make_syn_digest() const {
        std::vector<GossipDigest> digests;
        digests.reserve(cluster_state_.size());
        for (const auto& [id, state] : cluster_state_) {
            digests.push_back(GossipDigest{id, state.generation, state.max_version});
        }
        return digests;
    }

    std::vector<GossipDelta> collect_deltas_for_peer(std::span<const GossipDigest> peer_digests) const {
        std::vector<GossipDelta> result;
        size_t approx_bytes = 0;

        // Швидка таблиця для пошуку знань партнера
        std::unordered_map<std::string_view, GossipDigest> peer_map;
        for (const auto& d : peer_digests) {
            peer_map[d.node_id] = d;
        }

        for (const auto& [node_id, state] : cluster_state_) {
            auto it = peer_map.find(node_id);
            std::vector<GossipDelta> node_deltas;

            if (it == peer_map.end() || state.generation > it->second.generation) {
                // Партнер не має стану взагалі або його покоління застаріло
                for (const auto& [k, v] : state.attributes) {
                    node_deltas.push_back(GossipDelta{node_id, state.generation, k, v.value, v.version});
                }
            } else if (state.generation == it->second.generation && state.max_version > it->second.max_version) {
                // Віддаємо тільки дельти, новіші за відому партнеру max_version
                for (const auto& [k, v] : state.attributes) {
                    if (v.version > it->second.max_version) {
                        node_deltas.push_back(GossipDelta{node_id, state.generation, k, v.value, v.version});
                    }
                }
            }

            // Обов'язкове сортування за зростанням версій (Prefix Invariance)
            std::sort(node_deltas.begin(), node_deltas.end(),
                      [](const GossipDelta& a, const GossipDelta& b) {
                          return a.version < b.version;
                      });

            // Пакування в межах MTU
            for (auto&& delta : node_deltas) {
                size_t item_size = sizeof(GossipDelta) + delta.key.size() + delta.value.size();
                if (approx_bytes + item_size > MTU_PAYLOAD_LIMIT) {
                    return result; // Зупиняємося на цілісній межі версії
                }
                approx_bytes += item_size;
                result.push_back(std::move(delta));
            }
        }

        return result;
    }

    void apply_deltas(std::span<const GossipDelta> deltas) {
        for (const auto& d : deltas) {
            auto& state = cluster_state_[d.node_id];
            
            if (d.generation > state.generation) {
                // Нова епоха: старий стан вузла повністю очищується
                state.generation = d.generation;
                state.max_version = d.version;
                state.attributes.clear();
                state.attributes[d.key] = VersionedValue{d.value, d.version};
            } else if (d.generation == state.generation) {
                // Оновлюємо атрибут, якщо його версія свіжіша
                auto attr_it = state.attributes.find(d.key);
                if (attr_it == state.attributes.end() || d.version > attr_it->second.version) {
                    state.attributes[d.key] = VersionedValue{d.value, d.version};
                    if (d.version > state.max_version) {
                        state.max_version = d.version;
                    }
                }
            }
        }
    }

    [[nodiscard]] uint64_t get_node_max_version(const std::string& node_id) const {
        auto it = cluster_state_.find(node_id);
        return (it != cluster_state_.end()) ? it->second.max_version : 0;
    }

private:
    std::string local_node_id_;
    std::unordered_map<std::string, EndpointState> cluster_state_;
};
```
:::

---

## 3. Повний цикл трифазного рукостискання (SYN -> ACK -> ACK2)

У типовому циклі реконсиляції беруть участь два сервери, наприклад `Node-A` та `Node-B`. Повний сценарій демонструє, як розбіжності стану ліквідуються за єдиний трифазний обмін:

1. **Фаза 1 (`SYN`)**: `Node-A` формує вектор `GossipDigest` для всіх відомих йому вузлів і надсилає його до `Node-B`. Цей вектор містить лише ідентифікатори вузлів, їхні покоління та максимальні відомі версії;
2. **Фаза 2 (`ACK`)**: `Node-B` зіставляє отриманий дайджест зі своїми даними. З одного боку, він знаходить власні свіжіші дельти для `Node-A` і додає їх у відповідь. З іншого боку, він бачить, де стан `Node-A` випереджає його власний, і включає свій дайджест відставання;
3. **Фаза 3 (`ACK2`)**: `Node-A` отримує `ACK`, негайно застосовує дельти від `Node-B` і генерує фінальний пакет дельт, запитаний партнером. `Node-B` застосовує `ACK2`, після чого обидва сервери мають абсолютно узгоджений зріз даних.

:::tabs
```c
/* Застосування дельт до локального стану C-рушія */
void apply_deltas_c(ScuttlebuttEngine *engine, const GossipDelta *deltas, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        const GossipDelta *d = &deltas[i];
        
        /* Пошук або створення вузла в локальній таблиці */
        EndpointState *target = NULL;
        for (size_t j = 0; j < engine->node_count; ++j) {
            if (strcmp(engine->nodes[j].node_id, d->node_id) == 0) {
                target = &engine->nodes[j];
                break;
            }
        }
        if (target == NULL && engine->node_count < MAX_NODES) {
            target = &engine->nodes[engine->node_count++];
            strncpy(target->node_id, d->node_id, MAX_STR_LEN - 1);
            target->generation = d->generation;
            target->max_version = 0;
            target->value_count = 0;
        }
        if (target == NULL) continue;

        if (d->generation > target->generation) {
            /* Оновлення епохи */
            target->generation = d->generation;
            target->max_version = d->version;
            target->value_count = 0;
            strncpy(target->values[0].key, d->key, MAX_STR_LEN - 1);
            strncpy(target->values[0].value, d->value, MAX_STR_LEN - 1);
            target->values[0].version = d->version;
            target->value_count = 1;
        } else if (d->generation == target->generation) {
            bool found = false;
            for (size_t k = 0; k < target->value_count; ++k) {
                if (strcmp(target->values[k].key, d->key) == 0) {
                    if (d->version > target->values[k].version) {
                        strncpy(target->values[k].value, d->value, MAX_STR_LEN - 1);
                        target->values[k].version = d->version;
                    }
                    found = true;
                    break;
                }
            }
            if (!found && target->value_count < MAX_KEYS_PER_NODE) {
                VersionedValue *nv = &target->values[target->value_count++];
                strncpy(nv->key, d->key, MAX_STR_LEN - 1);
                strncpy(nv->value, d->value, MAX_STR_LEN - 1);
                nv->version = d->version;
            }
            if (d->version > target->max_version) {
                target->max_version = d->version;
            }
        }
    }
}

int main(void) {
    ScuttlebuttEngine node_a, node_b;
    memset(&node_a, 0, sizeof(node_a));
    memset(&node_b, 0, sizeof(node_b));

    strncpy(node_a.local_node_id, "Node-A", MAX_STR_LEN - 1);
    strncpy(node_b.local_node_id, "Node-B", MAX_STR_LEN - 1);

    /* Ініціалізація локального стану Node-A */
    EndpointState *ea = &node_a.nodes[node_a.node_count++];
    strncpy(ea->node_id, "Node-A", MAX_STR_LEN - 1);
    ea->generation = 100;
    ea->max_version = 2;
    strncpy(ea->values[0].key, "STATUS", MAX_STR_LEN - 1);
    strncpy(ea->values[0].value, "NORMAL", MAX_STR_LEN - 1);
    ea->values[0].version = 1;
    strncpy(ea->values[1].key, "LOAD", MAX_STR_LEN - 1);
    strncpy(ea->values[1].value, "0.85", MAX_STR_LEN - 1);
    ea->values[1].version = 2;
    ea->value_count = 2;

    /* 1. Фаза SYN: Node-A надсилає дайджест до Node-B */
    GossipDigest syn_digest[MAX_NODES];
    size_t syn_len = 1;
    strncpy(syn_digest[0].node_id, "Node-A", MAX_STR_LEN - 1);
    syn_digest[0].generation = 100;
    syn_digest[0].max_version = 2;

    /* 2. Фаза ACK: Node-B обчислює дельти для Node-A та формує свій дайджест */
    GossipDelta ack_deltas[32];
    size_t ack_delta_count = collect_deltas_for_peer(&node_b, syn_digest, syn_len, ack_deltas, 32);

    /* 3. Фаза ACK2: Node-A застосовує ACK дельти і надсилає залишок до Node-B */
    apply_deltas_c(&node_a, ack_deltas, ack_delta_count);

    GossipDigest ack_digest[MAX_NODES];
    size_t ack_digest_len = 0; /* Node-B ще не має своїх ключів */
    GossipDelta ack2_deltas[32];
    size_t ack2_delta_count = collect_deltas_for_peer(&node_a, ack_digest, ack_digest_len, ack2_deltas, 32);

    /* Node-B застосовує ACK2 дельти */
    apply_deltas_c(&node_b, ack2_deltas, ack2_delta_count);

    printf("Реконсиляція C завершена успішно. Node-B знає про Node-A версію: %lu\n",
           node_b.nodes[0].max_version);
    return 0;
}
```
```cpp
int main() {
    ScuttlebuttEngine node_a("Node-A", 100);
    ScuttlebuttEngine node_b("Node-B", 100);

    // Node-A змінює свої атрибути
    node_a.mutate_local_key("STATUS", "NORMAL"); // version 1
    node_a.mutate_local_key("LOAD", "0.85");     // version 2

    // 1. Фаза SYN: A -> B (надсилання дайджесту)
    std::vector<GossipDigest> syn_msg = node_a.make_syn_digest();

    // 2. Фаза ACK: B обробляє SYN, знаходить дельти для A та формує свій дайджест для A
    std::vector<GossipDelta> ack_deltas = node_b.collect_deltas_for_peer(syn_msg);
    std::vector<GossipDigest> ack_digest = node_b.make_syn_digest();

    // 3. Фаза ACK2: A застосовує дельти від B та генерує дельти для B
    node_a.apply_deltas(ack_deltas);
    std::vector<GossipDelta> ack2_deltas = node_a.collect_deltas_for_peer(ack_digest);

    // B застосовує дельти від A
    node_b.apply_deltas(ack2_deltas);

    std::cout << "Реконсиляція C++20 завершена успішно. Стан Node-B для Node-A: v"
              << node_b.get_node_max_version("Node-A") << "\n";
    return 0;
}
```
:::

---

## 4. Пастки реалізації та крайові випадки

1. **Хаотичне пакування дельт під час переповнення MTU**: Якщо дельти різних ключів одного вузла записуються в сокет без попереднього сортування за зростанням `version`, обрив пакета за лімітом розміру призведе до пропуску версій. Наступне рукостискання вважатиме, що вузол володіє всіма даними до `max_version`, і пропущені ключі залишаться застарілими назавжди.
2. **Переповнення монотонного лічильника версій**: 32-бітний лічильник версій при щосекундній зміні стану переповниться за ~136 років, але при високочастотних оновленнях (1000 оновлень/с) — за 49 днів. Лічильники версій та поколінь повинні бути строго 64-бітними цілими числами (`uint64_t`).
3. **Холодне перезавантаження та скидання лічильника**: Якщо сервер перезавантажився й обнулив свій лічильник версій, не збільшивши `generation` (наприклад, використовуючи статичний 0 замість мітки часу), кластер відхилятиме всі нові оновлення вузла, оскільки їхній номер версії (1, 2, ...) буде меншим за старі відомі значення (5000).
4. **Конкурентні мутації під час генерації повідомлень**: Якщо паралельний робочий потік оновлює стан під час формування дельт для партнера, читання не повинно бачити напівзаписаних значень. У високопродуктивних системах використовується копіювання при записі (*Copy-On-Write*) або захист таблиці вузла через легковажний блокувальник читання-запису (*Read-Write Spinlock*).
## 5. Аналіз продуктивності та накладних витрат пам'яті

Реалізація Scuttlebutt оптимізована для постійного фонового виконання в реальному часі. Оцінимо обчислювальну складність та використання пам'яті:

- **Часова складність раунду реконсиляції**: Формування `SYN` займає `O(N)` операцій для обходу локальної таблиці вузлів. Зіставлення знань у `collect_deltas_for_peer` вимагає `O(N)` пошуків у хеш-таблиці або масиві дайджестів. Сортування дельт для окремого вузла займає `O(K · log K)`, де `K` — кількість змінених ключів цього вузла. Оскільки в типовому раунді змінюється лише кілька атрибутів (`K ≤ 5`), сумарна тривалість обробки повідомлення на сучасному процесорі становить менше 50 мікросекунд.
- **Витрати оперативної пам'яті**: Для кластера з `N = 1000` серверів при `K = 50` ключів на вузол повна база метаданих `EndpointState` у пам'яті займає близько `1000 · 50 · 64 байтів ≈ 3.2 МБ`. Це дозволяє утримувати повну картину кластера безпосередньо в оперативній пам'яті процесу без звернення до диска чи зовнішніх сховищ.

