# ⚙️ Реалізація 3-фазного протоколу Scuttlebutt (Syn-Ack-Ack2)

У розподілених базах даних (зокрема в Apache Cassandra) поширення стану кластера та метаданих вузлів виконується за моделлю **Scuttlebutt** (розробленою Робом ван Ренессе). На відміну від прямолінійного надсилання всього стану вузла в кожному повідомленні, Scuttlebutt використовує 3-фазне узгодження на базі дайджестів версій.

Робоча реалізація алгоритму 3-фазного узгодження станів (Syn, Ack, Ack2) забезпечує передачу виключно різниці (дельти) оновлених значень за 1.5 RTT без дублювання незмінених даних.

---

## 1. Принцип роботи та архітектура узгодження

У великому кластері стан кожного сервера складається з десятків параметрів: статус у кільці токенів, поточне завантаження процесора та дисків, ідентифікатор стійки, версія бінарного коду та UUID схеми таблиць. Якщо кожен вузол передаватиме весь свій стан кожну секунду всім партнерам, мережевий трафік швидко перевантажить комутатори.

Scuttlebutt розв'язує цю проблему за допомогою версіонування окремих полів та обміну компактними дайджестами:

```
Вузол A (Ініціатор)                                           Вузол B (Партнер)
       |                                                             |
       | ------ 1. GossipDigestSyn (дайджести версій) -------------> |
       |                                                             |
       | <----- 2. GossipDigestAck (дельта для A + запит для B) ---- |
       |                                                             |
       | ------ 3. GossipDigestAck2 (залишкова дельта для B) ------> |
       |                                                             |
```

Процес повної двосторонньої синхронізації між ініціатором `A` та обраним партнером `B` розгортається у три послідовні фази.

Під час першої фази (`GossipDigestSyn`) ініціатор `A` сканує свою локальну таблицю станів і формує список пар `(генерація, максимальна_версія)` для кожного відомого йому вузла. Це повідомлення має фіксований компактний розмір, оскільки воно не містить значень полів, а лише ідентифікатори та мітки версій.

Під час другої фази (`GossipDigestAck`) партнер `B` зіставляє кожен отриманий дайджест зі своєю пам'яттю. Для кожного вузла можливі три ситуації:
- Якщо партнер `B` має більший номер генерації або більший номер версії, він витягує всі локальні поля, версія яких вища за версію ініціатора, і пакує їх у секцію дельти `Ack.delta`.
- Якщо ініціатор `A` має більший номер версії, партнер `B` додає дайджест цього вузла до списку запитів `Ack.requests` із зазначенням своєї поточної версії.
- Якщо номери генерацій та версій повністю збігаються, стан вузла вважається ідентичним, і жодні дані мережею не передаються.

Під час третьої фази (`GossipDigestAck2`) ініціатор `A` спершу застосовує всі отримані з `Ack.delta` нові значення до своєї пам'яті. Потім він переглядає список запитів `Ack.requests`, вибирає відповідні поля, версія яких перевищує версію партнера, і відправляє їх у фінальному повідомленні `Ack2.delta`. Партнер `B` застосовує отриману дельту, після чого обидва вузли мають абсолютно ідентичний стан.

---

## 2. Реалізація алгоритму на C та C++

У реалізації на мові C структури даних використовують статичні масиви з фіксованими лімітами для гарантії детермінованого використання пам'яті без динамічних алокацій у критичному мережевому циклі. Це забезпечує високу локальність даних у кеші процесора (L1/L2 data cache) та запобігає фрагментації оперативної пам'яті під тривалим навантаженням. У версії на C++ застосовуються ідіоми RAII, стандартні хеш-таблиці `std::unordered_map`, динамічні вектори та семантика переміщення (`std::move`), що забезпечує гнучке масштабування кількості полів і безпечне автоматичне звільнення ресурсів.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_NODES 16
#define MAX_STATES_PER_NODE 8
#define MAX_STR_LEN 32

/* Стан окремого поля метаданих вузла */
typedef struct {
    char key[MAX_STR_LEN];
    char value[MAX_STR_LEN];
    uint64_t version;
} ApplicationState;

/* Повний стан вузла в пам'яті */
typedef struct {
    uint32_t endpoint_id;
    uint64_t generation; /* Мітка запуску вузла */
    uint64_t heartbeat_version;
    int state_count;
    ApplicationState states[MAX_STATES_PER_NODE];
} EndpointState;

/* Компактний дайджест для фази SYN */
typedef struct {
    uint32_t endpoint_id;
    uint64_t generation;
    uint64_t max_version;
} GossipDigest;

/* Повідомлення Фази 1: SYN */
typedef struct {
    int digest_count;
    GossipDigest digests[MAX_NODES];
} GossipDigestSyn;

/* Повідомлення Фази 2: ACK */
typedef struct {
    int delta_count;
    EndpointState delta[MAX_NODES];
    int request_count;
    GossipDigest requests[MAX_NODES];
} GossipDigestAck;

/* Повідомлення Фази 3: ACK2 */
typedef struct {
    int delta_count;
    EndpointState delta[MAX_NODES];
} GossipDigestAck2;

/* Локальна база станів вузла */
typedef struct {
    uint32_t self_id;
    int node_count;
    EndpointState nodes[MAX_NODES];
} NodeClusterState;

/* Знаходження або створення запису про вузол */
static EndpointState* get_or_create_endpoint(NodeClusterState* cluster, uint32_t endpoint_id) {
    for (int i = 0; i < cluster->node_count; i++) {
        if (cluster->nodes[i].endpoint_id == endpoint_id) {
            return &cluster->nodes[i];
        }
    }
    if (cluster->node_count < MAX_NODES) {
        EndpointState* ep = &cluster->nodes[cluster->node_count++];
        memset(ep, 0, sizeof(EndpointState));
        ep->endpoint_id = endpoint_id;
        return ep;
    }
    return NULL;
}

/* Оновлення або додавання стану поля */
void update_application_state(EndpointState* ep, const char* key, const char* val, uint64_t ver) {
    for (int i = 0; i < ep->state_count; i++) {
        if (strcmp(ep->states[i].key, key) == 0) {
            if (ver > ep->states[i].version) {
                strncpy(ep->states[i].value, val, MAX_STR_LEN - 1);
                ep->states[i].version = ver;
            }
            if (ver > ep->heartbeat_version) ep->heartbeat_version = ver;
            return;
        }
    }
    if (ep->state_count < MAX_STATES_PER_NODE) {
        ApplicationState* s = &ep->states[ep->state_count++];
        strncpy(s->key, key, MAX_STR_LEN - 1);
        strncpy(s->value, val, MAX_STR_LEN - 1);
        s->version = ver;
        if (ver > ep->heartbeat_version) ep->heartbeat_version = ver;
    }
}

/* Фаза 1: Формування SYN повідомлення */
GossipDigestSyn build_syn(const NodeClusterState* cluster) {
    GossipDigestSyn syn;
    syn.digest_count = cluster->node_count;
    for (int i = 0; i < cluster->node_count; i++) {
        const EndpointState* ep = &cluster->nodes[i];
        syn.digests[i].endpoint_id = ep->endpoint_id;
        syn.digests[i].generation = ep->generation;
        syn.digests[i].max_version = ep->heartbeat_version;
    }
    return syn;
}

/* Фаза 2: Обробка SYN і формування ACK на вузлі B */
GossipDigestAck handle_syn_build_ack(NodeClusterState* cluster_b, const GossipDigestSyn* syn) {
    GossipDigestAck ack;
    ack.delta_count = 0;
    ack.request_count = 0;

    for (int i = 0; i < syn->digest_count; i++) {
        const GossipDigest* remote_d = &syn->digests[i];
        EndpointState* local_ep = NULL;
        for (int j = 0; j < cluster_b->node_count; j++) {
            if (cluster_b->nodes[j].endpoint_id == remote_d->endpoint_id) {
                local_ep = &cluster_b->nodes[j];
                break;
            }
        }

        if (!local_ep) {
            /* Вузол B нічого не знає про цей вузол -> просить усі дані */
            GossipDigest* req = &ack.requests[ack.request_count++];
            req->endpoint_id = remote_d->endpoint_id;
            req->generation = 0;
            req->max_version = 0;
            continue;
        }

        if (local_ep->generation > remote_d->generation) {
            /* Генерація B новіша (вузол перезавантажився) -> надсилаємо всі дані B */
            ack.delta[ack.delta_count++] = *local_ep;
        } else if (local_ep->generation < remote_d->generation) {
            /* Генерація A новіша -> просимо всі дані з A */
            GossipDigest* req = &ack.requests[ack.request_count++];
            req->endpoint_id = remote_d->endpoint_id;
            req->generation = local_ep->generation;
            req->max_version = local_ep->heartbeat_version;
        } else {
            /* Генерації однакові: порівнюємо версії */
            if (local_ep->heartbeat_version > remote_d->max_version) {
                /* B має новіші поля -> формуємо дельту */
                EndpointState* d_ep = &ack.delta[ack.delta_count++];
                memset(d_ep, 0, sizeof(EndpointState));
                d_ep->endpoint_id = local_ep->endpoint_id;
                d_ep->generation = local_ep->generation;
                d_ep->heartbeat_version = local_ep->heartbeat_version;

                for (int s = 0; s < local_ep->state_count; s++) {
                    if (local_ep->states[s].version > remote_d->max_version) {
                        d_ep->states[d_ep->state_count++] = local_ep->states[s];
                    }
                }
            } else if (local_ep->heartbeat_version < remote_d->max_version) {
                /* A має новіші поля -> запитуємо дельту від версії B */
                GossipDigest* req = &ack.requests[ack.request_count++];
                req->endpoint_id = local_ep->endpoint_id;
                req->generation = local_ep->generation;
                req->max_version = local_ep->heartbeat_version;
            }
        }
    }
    return ack;
}

/* Застосування дельти станів */
void apply_delta(NodeClusterState* cluster, const EndpointState* delta, int count) {
    for (int i = 0; i < count; i++) {
        const EndpointState* d_ep = &delta[i];
        EndpointState* local_ep = get_or_create_endpoint(cluster, d_ep->endpoint_id);
        if (!local_ep) continue;

        if (d_ep->generation > local_ep->generation) {
            *local_ep = *d_ep;
        } else if (d_ep->generation == local_ep->generation) {
            for (int s = 0; s < d_ep->state_count; s++) {
                update_application_state(local_ep, d_ep->states[s].key,
                                         d_ep->states[s].value, d_ep->states[s].version);
            }
        }
    }
}

/* Фаза 3: Обробка ACK і формування ACK2 на вузлі A */
GossipDigestAck2 handle_ack_build_ack2(NodeClusterState* cluster_a, const GossipDigestAck* ack) {
    /* 1. Застосовуємо дельту, яку надіслав B для A */
    apply_delta(cluster_a, ack->delta, ack->delta_count);

    /* 2. Формуємо відповідь на запити B */
    GossipDigestAck2 ack2;
    ack2.delta_count = 0;

    for (int i = 0; i < ack->request_count; i++) {
        const GossipDigest* req = &ack->requests[i];
        EndpointState* local_ep = NULL;
        for (int j = 0; j < cluster_a->node_count; j++) {
            if (cluster_a->nodes[j].endpoint_id == req->endpoint_id) {
                local_ep = &cluster_a->nodes[j];
                break;
            }
        }
        if (local_ep) {
            EndpointState* d_ep = &ack2.delta[ack2.delta_count++];
            memset(d_ep, 0, sizeof(EndpointState));
            d_ep->endpoint_id = local_ep->endpoint_id;
            d_ep->generation = local_ep->generation;
            d_ep->heartbeat_version = local_ep->heartbeat_version;

            for (int s = 0; s < local_ep->state_count; s++) {
                if (local_ep->states[s].version > req->max_version) {
                    d_ep->states[d_ep->state_count++] = local_ep->states[s];
                }
            }
        }
    }
    return ack2;
}
```
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <cstdint>
#include <optional>

struct ApplicationState {
    std::string value;
    uint64_t version{0};
};

struct EndpointState {
    uint32_t endpoint_id{0};
    uint64_t generation{0};
    uint64_t heartbeat_version{0};
    std::unordered_map<std::string, ApplicationState> states;

    void update(const std::string& key, const std::string& val, uint64_t ver) {
        auto& entry = states[key];
        if (ver > entry.version) {
            entry.value = val;
            entry.version = ver;
        }
        if (ver > heartbeat_version) {
            heartbeat_version = ver;
        }
    }
};

struct GossipDigest {
    uint32_t endpoint_id{0};
    uint64_t generation{0};
    uint64_t max_version{0};
};

struct GossipDigestSyn {
    std::vector<GossipDigest> digests;
};

struct GossipDigestAck {
    std::vector<EndpointState> delta;
    std::vector<GossipDigest> requests;
};

struct GossipDigestAck2 {
    std::vector<EndpointState> delta;
};

class NodeCluster {
public:
    uint32_t self_id{0};
    std::unordered_map<uint32_t, EndpointState> nodes;

    explicit NodeCluster(uint32_t id) : self_id(id) {}

    void set_state(uint32_t node_id, uint64_t gen, const std::string& key, const std::string& val, uint64_t ver) {
        auto& ep = nodes[node_id];
        ep.endpoint_id = node_id;
        ep.generation = gen;
        ep.update(key, val, ver);
    }

    [[nodiscard]] GossipDigestSyn build_syn() const {
        GossipDigestSyn syn;
        syn.digests.reserve(nodes.size());
        for (const auto& [id, ep] : nodes) {
            syn.digests.push_back({id, ep.generation, ep.heartbeat_version});
        }
        return syn;
    }

    GossipDigestAck handle_syn(const GossipDigestSyn& syn) {
        GossipDigestAck ack;

        for (const auto& remote_d : syn.digests) {
            auto it = nodes.find(remote_d.endpoint_id);
            if (it == nodes.end()) {
                ack.requests.push_back({remote_d.endpoint_id, 0, 0});
                continue;
            }

            const auto& local_ep = it->second;
            if (local_ep.generation > remote_d.generation) {
                ack.delta.push_back(local_ep);
            } else if (local_ep.generation < remote_d.generation) {
                ack.requests.push_back({remote_d.endpoint_id, local_ep.generation, local_ep.heartbeat_version});
            } else {
                if (local_ep.heartbeat_version > remote_d.max_version) {
                    EndpointState delta_ep;
                    delta_ep.endpoint_id = local_ep.endpoint_id;
                    delta_ep.generation = local_ep.generation;
                    delta_ep.heartbeat_version = local_ep.heartbeat_version;

                    for (const auto& [k, v] : local_ep.states) {
                        if (v.version > remote_d.max_version) {
                            delta_ep.states[k] = v;
                        }
                    }
                    ack.delta.push_back(std::move(delta_ep));
                } else if (local_ep.heartbeat_version < remote_d.max_version) {
                    ack.requests.push_back({local_ep.endpoint_id, local_ep.generation, local_ep.heartbeat_version});
                }
            }
        }
        return ack;
    }

    void apply_delta(const std::vector<EndpointState>& delta) {
        for (const auto& d_ep : delta) {
            auto& local_ep = nodes[d_ep.endpoint_id];
            local_ep.endpoint_id = d_ep.endpoint_id;

            if (d_ep.generation > local_ep.generation) {
                local_ep = d_ep;
            } else if (d_ep.generation == local_ep.generation) {
                for (const auto& [k, v] : d_ep.states) {
                    local_ep.update(k, v.value, v.version);
                }
            }
        }
    }

    GossipDigestAck2 handle_ack(const GossipDigestAck& ack) {
        apply_delta(ack.delta);

        GossipDigestAck2 ack2;
        for (const auto& req : ack.requests) {
            auto it = nodes.find(req.endpoint_id);
            if (it != nodes.end()) {
                EndpointState delta_ep;
                delta_ep.endpoint_id = it->second.endpoint_id;
                delta_ep.generation = it->second.generation;
                delta_ep.heartbeat_version = it->second.heartbeat_version;

                for (const auto& [k, v] : it->second.states) {
                    if (v.version > req->max_version) {
                        delta_ep.states[k] = v;
                    }
                }
                ack2.delta.push_back(std::move(delta_ep));
            }
        }
        return ack2;
    }

    void handle_ack2(const GossipDigestAck2& ack2) {
        apply_delta(ack2.delta);
    }
};
```
:::

---

## 3. Інваріанти, крайові випадки та аналіз складності

При проектуванні та експлуатації трифазного протоколу Scuttlebutt важливо враховувати кілька фундаментальних інваріантів розподілених систем:

Перший інваріант полягає в ідемпотентності операції злиття станів (Join-semilattice). Будь-яке повідомлення може бути дубльоване на рівні мережі, затримане або доставлене в довільному порядку. Локальний стан змінюється виключно за умови, що версія вхідного поля строго перевищує поточну збережену версію. Якщо версії однакові або вхідна версія менша, оновлення мовчки ігнорується, що гарантує детермінізм фінального стану незалежно від порядку обробки пакетів.

Другий інваріант стосується обробки перезапусків серверів. Якщо процес аварійно завершується, його пам'ять очищається, а локальний лічильник версій після старту починається з нуля. Щоб уникнути колізії, коли старі збережені версії на інших вузлах блокуватимуть нові оновлення, під час старту генерується новий монотонний `Generation` на основі системного часу. Будь-який вузол, побачивши `new_gen > old_gen`, негайно перезаписує весь попередній кеш новим знімком.

Третій інваріант стосується багатопотокової безпеки та ізоляції транзакцій. У реальних системах підсистема gossip працює в окремому фоновому потоці, тоді як клієнтські CQL-потоки постійно читають таблицю маршрутизації токенів. Застосування дельти станів виконується атомарно або через копіювання при записі (Copy-on-Write), що унеможливлює стан гонитви, коли координатор направляє клієнтський запит на половинчасто оновлений стан репліки.

Четвертий інваріант стосується фрагментації та передачі великих пакетів через сокети. У разі масового рестарту кластера список відсутніх станів у повідомленні `ACK` може досягати кількох мегабайтів. Двигун Cassandra розбиває велику дельту на окремі порції (чанкі), передаючи їх послідовно через TCP-стрім із контролем переповнення буфера сокета (`SO_SNDBUF`).

П'ятий інваріант стосується мережевої та обчислювальної складності:
- Об'єм повідомлення `SYN` становить строго `O(N)` дайджестів, де `N` — загальна кількість відомих вузлів кластера.
- Об'єм повідомлень `ACK` та `ACK2` залежить виключно від кількості модифікованих полів `O(M)`. Якщо в системі не відбувалося змін метаданих, корисне навантаження дельти дорівнює нулю.
- Час досягнення глобальної узгодженості після зміни стану на одному вузлі становить `O(log N)` раундів пліткування завдяки експоненційному поширенню через випадковий вибір партнерів.
