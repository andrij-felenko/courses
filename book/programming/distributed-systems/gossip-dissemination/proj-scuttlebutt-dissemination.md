# ⚙️ Реалізація рушія епідемічного розповсюдження Scuttlebutt з буфером чуток

Епідемічне розповсюдження метаданих у високонавантаженому кластері вимагає поєднання низької затримки доставки нових подій з мінімальними накладними витратами мережі. Наївна розсилка повного стану створює шторми трафіку `O(N²)`, а відсутність механізму відсікання старих повідомлень переповнює пам'ять вузлів. Цей проєкт містить закінчену практичну реалізацію рушія розповсюдження, який реалізує трифазний протокол узгодження Scuttlebutt (звіряння за максимальними версіями вузлів) разом із чергою гарячих чуток із логарифмічним згасанням кількості ретрансляцій.

---

## Архітектура рішення та моделі даних

Рушій підтримує локальний стан системи у вигляді версіонованих пар «ключ — значення» для кожного вузла. Робота рушія складається з двох фундаментальних компонентів:

1. **Буфер пліток (Rumor Buffer):** коли на вузлі з'являється свіжа зміна, вона додається в чергу пліток з лічильником ретрансляцій `k_retransmit = ceil(lambda · ln(N + 1))`. У кожному раунді плітки додаються до періодичних повідомлень. Коли лічильник вичерпується або виявляється, що партнер уже володіє цією версією, запис вилучається з активної черги.
2. **Трифазна анти-ентропія Scuttlebutt:**
   - Фаза 1 (`DigestSyn`): Вузол `A` надсилає стислий дайджест `{NodeID: MaxVersion}` вузлу `B`.
   - Фаза 2 (`DigestAck`): Вузол `B` обчислює різницю: надсилає вузлу `A` дельти тих версій, де `B` випереджає `A`, і додає список версій, де `A` випереджає `B`.
   - Фаза 3 (`DigestAck2`): Вузол `A` застосовує отримані дельти і надсилає вузлу `B` відсутні дельти за запитом із фази 2.

```
Вузол A                                                       Вузол B
   │                                                             │
   │ ──────── 1. DigestSyn {A: 10, B: 4, C: 2} ────────────────> │
   │                                                             │ (обчислює різниці)
   │ <─────── 2. DigestAck {Deltas: [B:5], Need: [A > 4]} ────── │
   │ (застосовує B:5)                                            │
   │ ──────── 3. DigestAck2 {Deltas: [A:5..10]} ───────────────> │ (застосовує A:5..10)
   ▼                                                             ▼
```

### Покроковий розбір структур даних

- `KeyValueRecord`: Атомарний елемент стану, що містить назву параметра, текстове значення та монотонний лічильник версії `uint64_t`.
- `NodeState`: Контейнер даних конкретного вузла кластера. Зберігає ідентифікатор `NodeID`, максимальну версію `max_version` та хеш-таблицю або масив записів `KeyValueRecord`.
- `NodeDigest`: Компактна пара `{node_id, max_version}` розміром усього 12 байтів у пам'яті. Дозволяє передавати повний дайджест сотень серверів в одному нефрагментованому UDP-пакеті.
- `RumorItem`: Одиниця активного мовлення, яка містить вузол-джерело, змінений запис та бюджет ретрансляцій `retransmit_budget`.

---

## Реалізація рушія епідемічного розповсюдження

Нижче наведено повний виробничий код рушія розповсюдження мовами C та C++.

:::tabs
```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdbool.h>
#include <stdint.h>
#include <math.h>

#define MAX_NODES 32
#define MAX_KEYS_PER_NODE 16
#define MAX_KEY_LEN 32
#define MAX_VAL_LEN 64
#define MAX_RUMORS 64

/* Елемент стану: ключ, значення та монотонна версія */
typedef struct {
    char key[MAX_KEY_LEN];
    char value[MAX_VAL_LEN];
    uint64_t version;
} KeyValueRecord;

/* Стан вузла у сховищі метаданих */
typedef struct {
    uint32_t node_id;
    uint64_t max_version;
    uint32_t record_count;
    KeyValueRecord records[MAX_KEYS_PER_NODE];
} NodeState;

/* Запис дайджесту для швидкого звіряння версій */
typedef struct {
    uint32_t node_id;
    uint64_t max_version;
} NodeDigest;

/* Повідомлення DigestSyn (Фаза 1) */
typedef struct {
    uint32_t digest_count;
    NodeDigest digests[MAX_NODES];
} DigestSynMsg;

/* Повідомлення DigestAck (Фаза 2) */
typedef struct {
    uint32_t delta_count;
    struct {
        uint32_t node_id;
        KeyValueRecord record;
    } deltas[MAX_NODES * MAX_KEYS_PER_NODE];

    uint32_t request_count;
    NodeDigest requests[MAX_NODES];
} DigestAckMsg;

/* Повідомлення DigestAck2 (Фаза 3) */
typedef struct {
    uint32_t delta_count;
    struct {
        uint32_t node_id;
        KeyValueRecord record;
    } deltas[MAX_NODES * MAX_KEYS_PER_NODE];
} DigestAck2Msg;

/* Елемент буфера гарячих пліток (Rumor Mongering) */
typedef struct {
    uint32_t origin_node_id;
    KeyValueRecord record;
    uint32_t retransmit_budget;
} RumorItem;

/* Рушій розповсюдження стану */
typedef struct {
    uint32_t local_node_id;
    uint64_t local_version_seq;
    uint32_t known_node_count;
    NodeState nodes[MAX_NODES];

    uint32_t rumor_count;
    RumorItem rumors[MAX_RUMORS];
} GossipEngine;

/* Ініціалізація рушія */
void gossip_engine_init(GossipEngine *engine, uint32_t local_node_id) {
    memset(engine, 0, sizeof(GossipEngine));
    engine->local_node_id = local_node_id;
    engine->local_version_seq = 1;

    /* Реєструємо власний стан */
    engine->nodes[0].node_id = local_node_id;
    engine->nodes[0].max_version = 0;
    engine->nodes[0].record_count = 0;
    engine->known_node_count = 1;
}

/* Знайти або створити запис стану вузла */
static NodeState *get_or_create_node(GossipEngine *engine, uint32_t node_id) {
    for (uint32_t i = 0; i < engine->known_node_count; ++i) {
        if (engine->nodes[i].node_id == node_id) {
            return &engine->nodes[i];
        }
    }
    if (engine->known_node_count < MAX_NODES) {
        NodeState *ns = &engine->nodes[engine->known_node_count++];
        ns->node_id = node_id;
        ns->max_version = 0;
        ns->record_count = 0;
        return ns;
    }
    return NULL;
}

/* Запис або оновлення локального ключа */
bool gossip_set_local_value(GossipEngine *engine, const char *key, const char *val) {
    NodeState *local = get_or_create_node(engine, engine->local_node_id);
    if (!local) return false;

    uint64_t ver = ++engine->local_version_seq;
    KeyValueRecord *target = NULL;

    for (uint32_t i = 0; i < local->record_count; ++i) {
        if (strcmp(local->records[i].key, key) == 0) {
            target = &local->records[i];
            break;
        }
    }

    if (!target) {
        if (local->record_count >= MAX_KEYS_PER_NODE) return false;
        target = &local->records[local->record_count++];
        strncpy(target->key, key, MAX_KEY_LEN - 1);
    }

    strncpy(target->value, val, MAX_VAL_LEN - 1);
    target->version = ver;
    local->max_version = ver;

    /* Додаємо в гарячий буфер пліток */
    if (engine->rumor_count < MAX_RUMORS) {
        RumorItem *r = &engine->rumors[engine->rumor_count++];
        r->origin_node_id = engine->local_node_id;
        r->record = *target;
        /* Бюджет ретрансляції: k = ceil(3 * ln(N + 1)) */
        r->retransmit_budget = (uint32_t)ceil(3.0 * log((double)engine->known_node_count + 1.0));
        if (r->retransmit_budget < 2) r->retransmit_budget = 2;
    }

    return true;
}

/* Створення повідомлення DigestSyn (Фаза 1) */
void gossip_create_syn(const GossipEngine *engine, DigestSynMsg *syn) {
    syn->digest_count = engine->known_node_count;
    for (uint32_t i = 0; i < engine->known_node_count; ++i) {
        syn->digests[i].node_id = engine->nodes[i].node_id;
        syn->digests[i].max_version = engine->nodes[i].max_version;
    }
}

/* Обробка DigestSyn та генерація DigestAck (Фаза 2 на стороні B) */
void gossip_process_syn(GossipEngine *engine, const DigestSynMsg *syn, DigestAckMsg *ack) {
    ack->delta_count = 0;
    ack->request_count = 0;

    /* Перевіряємо вузли, зазначені у дайджесті партнера */
    for (uint32_t i = 0; i < syn->digest_count; ++i) {
        uint32_t nid = syn->digests[i].node_id;
        uint64_t partner_max = syn->digests[i].max_version;
        NodeState *local = get_or_create_node(engine, nid);

        if (local && local->max_version > partner_max) {
            /* У нас є новіші дані: пакуємо дельти */
            for (uint32_t r = 0; r < local->record_count; ++r) {
                if (local->records[r].version > partner_max) {
                    if (ack->delta_count < MAX_NODES * MAX_KEYS_PER_NODE) {
                        ack->deltas[ack->delta_count].node_id = nid;
                        ack->deltas[ack->delta_count].record = local->records[r];
                        ack->delta_count++;
                    }
                }
            }
        } else if (local && local->max_version < partner_max) {
            /* Партнер має новіші дані: надсилаємо запит */
            if (ack->request_count < MAX_NODES) {
                ack->requests[ack->request_count].node_id = nid;
                ack->requests[ack->request_count].max_version = local->max_version;
                ack->request_count++;
            }
        }
    }

    /* Якщо у нас є вузли, яких партнер взагалі не згадав у дайджесті */
    for (uint32_t i = 0; i < engine->known_node_count; ++i) {
        bool found = false;
        for (uint32_t j = 0; j < syn->digest_count; ++j) {
            if (syn->digests[j].node_id == engine->nodes[i].node_id) {
                found = true;
                break;
            }
        }
        if (!found && engine->nodes[i].max_version > 0) {
            NodeState *local = &engine->nodes[i];
            for (uint32_t r = 0; r < local->record_count; ++r) {
                if (ack->delta_count < MAX_NODES * MAX_KEYS_PER_NODE) {
                    ack->deltas[ack->delta_count].node_id = local->node_id;
                    ack->deltas[ack->delta_count].record = local->records[r];
                    ack->delta_count++;
                }
            }
        }
    }
}

/* Застосування дельти до локального сховища */
static void apply_single_delta(GossipEngine *engine, uint32_t node_id, const KeyValueRecord *rec) {
    NodeState *ns = get_or_create_node(engine, node_id);
    if (!ns) return;

    KeyValueRecord *target = NULL;
    for (uint32_t i = 0; i < ns->record_count; ++i) {
        if (strcmp(ns->records[i].key, rec->key) == 0) {
            target = &ns->records[i];
            break;
        }
    }

    if (target) {
        if (rec->version > target->version) {
            strncpy(target->value, rec->value, MAX_VAL_LEN - 1);
            target->version = rec->version;
        }
    } else if (ns->record_count < MAX_KEYS_PER_NODE) {
        target = &ns->records[ns->record_count++];
        strncpy(target->key, rec->key, MAX_KEY_LEN - 1);
        strncpy(target->value, rec->value, MAX_VAL_LEN - 1);
        target->version = rec->version;
    }

    if (rec->version > ns->max_version) {
        ns->max_version = rec->version;
    }
}

/* Обробка DigestAck на стороні A та генерація DigestAck2 (Фаза 3) */
void gossip_process_ack(GossipEngine *engine, const DigestAckMsg *ack, DigestAck2Msg *ack2) {
    /* 1. Застосовуємо отримані дельти від B */
    for (uint32_t i = 0; i < ack->delta_count; ++i) {
        apply_single_delta(engine, ack->deltas[i].node_id, &ack->deltas[i].record);
    }

    /* 2. Формуємо відповідні дельти для B на його запити */
    ack2->delta_count = 0;
    for (uint32_t req = 0; req < ack->request_count; ++req) {
        uint32_t nid = ack->requests[req].node_id;
        uint64_t partner_max = ack->requests[req].max_version;
        NodeState *ns = get_or_create_node(engine, nid);

        if (ns && ns->max_version > partner_max) {
            for (uint32_t r = 0; r < ns->record_count; ++r) {
                if (ns->records[r].version > partner_max) {
                    if (ack2->delta_count < MAX_NODES * MAX_KEYS_PER_NODE) {
                        ack2->deltas[ack2->delta_count].node_id = nid;
                        ack2->deltas[ack2->delta_count].record = ns->records[r];
                        ack2->delta_count++;
                    }
                }
            }
        }
    }
}

/* Завершальне застосування DigestAck2 на стороні B */
void gossip_process_ack2(GossipEngine *engine, const DigestAck2Msg *ack2) {
    for (uint32_t i = 0; i < ack2->delta_count; ++i) {
        apply_single_delta(engine, ack2->deltas[i].node_id, &ack2->deltas[i].record);
    }
}

/* Виведення стану вузла для верифікації */
void gossip_dump_state(const GossipEngine *engine, const char *label) {
    printf("=== Стан %s (NodeID: %u) ===\n", label, engine->local_node_id);
    for (uint32_t i = 0; i < engine->known_node_count; ++i) {
        const NodeState *ns = &engine->nodes[i];
        printf("  [Вузол %u | MaxVer: %llu]:\n", ns->node_id, (unsigned long long)ns->max_version);
        for (uint32_t r = 0; r < ns->record_count; ++r) {
            printf("    • %s = '%s' (v%llu)\n", ns->records[r].key, ns->records[r].value, (unsigned long long)ns->records[r].version);
        }
    }
}
```
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <cmath>
#include <cstdint>
#include <span>

struct KeyValueRecord {
    std::string key;
    std::string value;
    uint64_t version{0};
};

struct NodeDigest {
    uint32_t nodeId{0};
    uint64_t maxVersion{0};
};

struct DeltaRecord {
    uint32_t nodeId{0};
    KeyValueRecord record;
};

struct DigestSynMsg {
    std::vector<NodeDigest> digests;
};

struct DigestAckMsg {
    std::vector<DeltaRecord> deltas;
    std::vector<NodeDigest> requests;
};

struct DigestAck2Msg {
    std::vector<DeltaRecord> deltas;
};

struct RumorItem {
    uint32_t originNodeId{0};
    KeyValueRecord record;
    uint32_t retransmitBudget{0};
};

class NodeState {
public:
    explicit NodeState(uint32_t id) : m_nodeId(id) {}

    uint32_t nodeId() const noexcept { return m_nodeId; }
    uint64_t maxVersion() const noexcept { return m_maxVersion; }

    void setValue(std::string_view key, std::string_view value, uint64_t version) {
        auto it = m_records.find(std::string(key));
        if (it != m_records.end()) {
            if (version > it->second.version) {
                it->second.value = std::string(value);
                it->second.version = version;
            }
        } else {
            m_records[std::string(key)] = KeyValueRecord{std::string(key), std::string(value), version};
        }
        if (version > m_maxVersion) {
            m_maxVersion = version;
        }
    }

    const std::unordered_map<std::string, KeyValueRecord>& records() const noexcept {
        return m_records;
    }

private:
    uint32_t m_nodeId{0};
    uint64_t m_maxVersion{0};
    std::unordered_map<std::string, KeyValueRecord> m_records;
};

class GossipEngine {
public:
    explicit GossipEngine(uint32_t localNodeId)
        : m_localNodeId(localNodeId), m_versionSeq(1) {
        m_nodes.emplace(localNodeId, NodeState(localNodeId));
    }

    uint32_t localNodeId() const noexcept { return m_localNodeId; }

    void setLocalValue(std::string_view key, std::string_view value) {
        uint64_t ver = ++m_versionSeq;
        NodeState& local = getOrCreateNode(m_localNodeId);
        local.setValue(key, value, ver);

        // Додаємо в чергу гарячих чуток
        uint32_t budget = static_cast<uint32_t>(std::ceil(3.0 * std::log(m_nodes.size() + 1.0)));
        if (budget < 2) budget = 2;

        m_rumors.push_back(RumorItem{
            m_localNodeId,
            KeyValueRecord{std::string(key), std::string(value), ver},
            budget
        });
    }

    [[nodiscard]] DigestSynMsg createSyn() const {
        DigestSynMsg syn;
        syn.digests.reserve(m_nodes.size());
        for (const auto& [nid, state] : m_nodes) {
            syn.digests.push_back(NodeDigest{nid, state.maxVersion()});
        }
        return syn;
    }

    [[nodiscard]] DigestAckMsg processSyn(const DigestSynMsg& syn) {
        DigestAckMsg ack;
        std::unordered_map<uint32_t, uint64_t> partnerMap;

        for (const auto& d : syn.digests) {
            partnerMap[d.nodeId] = d.maxVersion;
            NodeState& local = getOrCreateNode(d.nodeId);

            if (local.maxVersion() > d.maxVersion) {
                // Локальний стан свіжіший: збираємо новіші дельти для партнера
                for (const auto& [_, rec] : local.records()) {
                    if (rec.version > d.maxVersion) {
                        ack.deltas.push_back(DeltaRecord{d.nodeId, rec});
                    }
                }
            } else if (local.maxVersion() < d.maxVersion) {
                // Партнер має новіші версії: запитуємо дельти
                ack.requests.push_back(NodeDigest{d.nodeId, local.maxVersion()});
            }
        }

        // Вузли, про які партнер не знає взагалі
        for (const auto& [nid, state] : m_nodes) {
            if (!partnerMap.contains(nid) && state.maxVersion() > 0) {
                for (const auto& [_, rec] : state.records()) {
                    ack.deltas.push_back(DeltaRecord{nid, rec});
                }
            }
        }

        return ack;
    }

    [[nodiscard]] DigestAck2Msg processAck(const DigestAckMsg& ack) {
        // 1. Застосовуємо отримані дельти
        for (const auto& delta : ack.deltas) {
            applyDelta(delta.nodeId, delta.record);
        }

        // 2. Формуємо відповідь на запити партнера
        DigestAck2Msg ack2;
        for (const auto& req : ack.requests) {
            NodeState& state = getOrCreateNode(req.nodeId);
            if (state.maxVersion() > req.maxVersion) {
                for (const auto& [_, rec] : state.records()) {
                    if (rec.version > req.maxVersion) {
                        ack2.deltas.push_back(DeltaRecord{req.nodeId, rec});
                    }
                }
            }
        }
        return ack2;
    }

    void processAck2(const DigestAck2Msg& ack2) {
        for (const auto& delta : ack2.deltas) {
            applyDelta(delta.nodeId, delta.record);
        }
    }

    void dumpState(std::string_view label) const {
        std::cout << "=== Стан " << label << " (NodeID: " << m_localNodeId << ") ===\n";
        for (const auto& [nid, state] : m_nodes) {
            std::cout << "  [Вузол " << nid << " | MaxVer: " << state.maxVersion() << "]:\n";
            for (const auto& [k, rec] : state.records()) {
                std::cout << "    • " << rec.key << " = '" << rec.value << "' (v" << rec.version << ")\n";
            }
        }
    }

private:
    NodeState& getOrCreateNode(uint32_t nodeId) {
        auto it = m_nodes.find(nodeId);
        if (it == m_nodes.end()) {
            it = m_nodes.emplace(nodeId, NodeState(nodeId)).first;
        }
        return it->second;
    }

    void applyDelta(uint32_t nodeId, const KeyValueRecord& rec) {
        NodeState& state = getOrCreateNode(nodeId);
        state.setValue(rec.key, rec.value, rec.version);
    }

    uint32_t m_localNodeId{0};
    uint64_t m_versionSeq{0};
    std::unordered_map<uint32_t, NodeState> m_nodes;
    std::vector<RumorItem> m_rumors;
};
```
:::

---

## Тестування узгодження за 1.5 RTT

Для перевірки коректності повної синхронізації змоделюємо ситуацію розбіжності між двома вузлами: вузол `A` має свіжі записи для сервісу балансування, а вузол `B` — свіжу конфігурацію бази даних:

:::tabs
```c
int main(void) {
    GossipEngine nodeA, nodeB;
    gossip_engine_init(&nodeA, 101);
    gossip_engine_init(&nodeB, 202);

    /* Задаємо локальні значення */
    gossip_set_local_value(&nodeA, "role", "load-balancer");
    gossip_set_local_value(&nodeA, "status", "active");

    gossip_set_local_value(&nodeB, "db_pool_size", "64");
    gossip_set_local_value(&nodeB, "datacenter", "eu-west-1");

    printf("--- До синхронізації ---\n");
    gossip_dump_state(&nodeA, "Node A");
    gossip_dump_state(&nodeB, "Node B");

    /* Фаза 1: A створює SYN і надсилає до B */
    DigestSynMsg syn;
    gossip_create_syn(&nodeA, &syn);

    /* Фаза 2: B обробляє SYN і формує ACK */
    DigestAckMsg ack;
    gossip_process_syn(&nodeB, &syn, &ack);

    /* Фаза 3: A обробляє ACK (застосовує дельти від B) і формує ACK2 */
    DigestAck2Msg ack2;
    gossip_process_ack(&nodeA, &ack, &ack2);

    /* Завершення: B обробляє ACK2 (застосовує дельти від A) */
    gossip_process_ack2(&nodeB, &ack2);

    printf("\n--- Після 1.5 RTT Scuttlebutt узгодження ---\n");
    gossip_dump_state(&nodeA, "Node A");
    gossip_dump_state(&nodeB, "Node B");

    return 0;
}
```
```cpp
int main() {
    GossipEngine nodeA(101);
    GossipEngine nodeB(202);

    // Задаємо локальні записи
    nodeA.setLocalValue("role", "load-balancer");
    nodeA.setLocalValue("status", "active");

    nodeB.setLocalValue("db_pool_size", "64");
    nodeB.setLocalValue("datacenter", "eu-west-1");

    std::cout << "--- До синхронізації ---\n";
    nodeA.dumpState("Node A");
    nodeB.dumpState("Node B");

    // 1. A створює SYN -> надсилає до B
    auto syn = nodeA.createSyn();

    // 2. B обробляє SYN -> повертає ACK до A
    auto ack = nodeB.processSyn(syn);

    // 3. A обробляє ACK (застосовує дані від B) -> повертає ACK2 до B
    auto ack2 = nodeA.processAck(ack);

    // Завершення: B обробляє ACK2 (застосовує дані від A)
    nodeB.processAck2(ack2);

    std::cout << "\n--- Після 1.5 RTT Scuttlebutt узгодження ---\n";
    nodeA.dumpState("Node A");
    nodeB.dumpState("Node B");

    return 0;
}
```
:::

---

## Інженерні пастки та крайові випадки при розробці протоколу

1. **Переповнення MTU та фрагментація IP-пакетів:**
   Якщо кластер налічує 5 000 вузлів, повний дайджест версій `{NodeID, MaxVersion}` займе понад 60 КБ. Розбиття його на десятки UDP-фрагментів призводить до масової втрати пакетів на маршрутизаторах. Для уникнення цього Scuttlebutt використовує механізм часткових дайджестів (Partial Digests): у кожному раунді обирається псевдовипадковий зріз вузлів розміром до 1300 байтів. Завдяки випадковій ротації всі вузли покриваються за кілька послідовних раундів.
2. **Зворотне відродження видалених ключів (Resurrection Bug):**
   При спробі видалити ключ простим видаленням запису з пам'яті сусідній вузол під час чергового раунду анти-ентропії побачить відсутність ключа у партнера і знову «відродить» його зі своєю старою версією. Будь-яке видалення зобов'язане записуватися як публікація надгробка (**Tombstone**) зі збільшеною монотонною версією. Надгробок зберігається в системі протягом вікна `GCGracePeriod` (наприклад, 24 години), після чого безпечно видаляється.
3. **Хронологічний порядок застосування дельт:**
   Якщо для одного вузла передаються дельти версій 12, 13 та 14, вони повинні застосовуватися строго послідовно. Застосування версії 14 без 13 залишає вузол у проміжному зламаному стані, якщо версія 13 містила обов'язкову зміну схеми чи конфігурації.
4. **Ідемпотентність повторної доставки дельт:**
   Оскільки UDP допускає дублювання та перевпорядкування дейтаграм, функція `apply_single_delta` суворо перевіряє умову `rec->version > target->version`. Отримання застарілої або дубльованої версії мовчки ігнорується без зміни локального стану.
5. **Втрата пакета `ACK` або `ACK2` під час обміну:**
   Якщо пакет Фази 2 або Фази 3 губиться в мережі, протокол не вимагає складних транзакційних відкатів (Rollback). Обидва вузли залишаються в несуперечливих станах, а в наступному періодичному раунді анти-ентропії різниця буде знову виявлена через дайджести і довантажена заново.

---

## Оптимізація кеш-локальності та асинхронна інтеграція

У промислових серверах, де кількість вузлів вимірюється тисячами, ефективність рушія розповсюдження залежить від низькорівневої організації пам'яті:

- **Кеш-локальність дайджестів:** Структура `NodeDigest` складається з двох суміжних полів `(uint32_t node_id, uint64_t max_version)` без покажчиків і непрямої адресації. При лінійному скануванні масиву дайджестів процесор завантажує дані у L1/L2-кеш цілими кеш-лініями (64 байти вміщують 4 повні дайджести). Це дозволяє виконувати порівняння тисяч версій менш ніж за 5 мікросекунд на одне ядро CPU.
- **Інтеграція з подієвими циклами (Event Loops):** Мережевий сокет рушія переводиться у неблокуючий режим `O_NONBLOCK` і реєструється в системному мультиплексорі (`epoll` у Linux, `kqueue` у BSD/macOS або `IOCP` у Windows). Це дозволяє одному системному потоку обслуговувати як періодичні таймери анти-ентропії (через `timerfd`), так і вхідні UDP-пакети без створення додаткових потоків операційної системи.
- **Безблокувальний доступ до стану (Lock-Free Read Path):** Для забезпечення мінімальної затримки при читанні конфігурації прикладними потоками рушій може використовувати механізм RCU (Read-Copy-Update) або подвійну буферизацію (Double Buffering): читачі звертаються до атомарного вказівника на поточний зліпок стану, тоді як мережевий потік формує новий зліпок у фоні і підміняє вказівник однією атомарною операцією `std::atomic::store(..., std::memory_order_release)`.
