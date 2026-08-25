# ⚙️ Проєктування збіжного розподіленого регістра з векторними годинниками та сесійними токенами

Коли розподілене сховище відмовляється від синхронних блокувань і двофазної фіксації транзакцій, воно бере на себе зобов'язання розв'язувати конфлікти та вирівнювати стан реплік постфактум.

Цей проєкт реалізує повністю працездатний, протестований кластер розподіленого регістра типу «ключ-значення», що забезпечує детерміновану кінцеву узгодженість (Eventual Consistency), реактивне самолікування через механізм Read-Repair та клієнтські сесійні гарантії Read-Your-Writes.

---

## 1. Інженерна постановка задачі та модель загроз

У георозподіленій інфраструктурі вузли розміщені в різних дата-центрах (наприклад, Регіон EU у Франкфурті та Регіон US у Вірджинії). Міжрегіональний канал зв'язку має затримку RTT близько 80–100 мілісекунд і періодично зазнає короткочасних мережевих розривів.

Якщо система вимагає нульової латентності на запис, кожен регіональний вузол зобов'язаний приймати оновлення локально й підтверджувати їх клієнту негайно, без очікування міжконтинентальної відповіді.

Це породжує три фундаментальні інженерні виклики:

```
1. Виявлення конкурентних оновлень (Concurrency Detection):
   Якщо користувач Аліса змінює налаштування на вузлі EU, а користувач Боб
   змінює те саме налаштування на вузлі US під час мережевого розділення,
   система не має права сліпо перезаписати одне значення іншим. Вона зобов'язана
   математично виявити факт паралельного розгалуження історії.

2. Детерміноване злиття станів (Deterministic Convergence):
   Коли зв'язок відновлюється, обидва вузли повинні самостійно прийти до
   абсолютно ідентичного значення без центрального координатора і без блокувань.

3. Усунення клієнтських аномалій (Session Integrity):
   Клієнт, який щойно виконав успішний запис на швидкому вузлі, не повинен
   спостерігати відкат до старого стану при наступному читанні з відсталого вузла.
```

Наївне використання фізичного настінного часу (Wall Clock / NTP Timestamp) для правила Last-Write-Wins (LWW) є неприпустимим як єдиний механізм, оскільки дрейф годинників між серверами навіть на 20–50 мс призводить до тихих безповоротних втрат найновіших бізнес-даних. Тому основою версіонування в нашому проєкті виступають **векторні годинники** (Vector Clocks).

---

## 2. Еволюція годинників: від Лампорта до векторів версій

Щоб зрозуміти, чому простих монотонних чисел недостатньо для систем із кінцевою узгодженістю, порівняємо три покоління розподіленого часу:

### 1. Скалярні годинники Лампорта (Lamport Timestamps)

Леслі Лампорт 1978 року запропонував пов'язувати з кожною подією скалярне число `T`. При відправленні повідомлення вузол інкрементує свій лічильник, а при отриманні встановлює `T_local = max(T_local, T_msg) + 1`.

- **Перевага:** гарантує строгий порядок слідування: якщо подія `A` причинно передує події `B` (`A → B`), то `T(A) < T(B)`.
- **Фатальний недолік:** зворотне твердження **невірне**. Якщо `T(A) < T(B)`, ми не можемо стверджувати, що `A → B`. Події могли відбутися абсолютно незалежно в різних сегментах мережі, але випадково отримати числа `10` та `12`. Годинники Лампорта не здатні виявити конкурентність.

### 2. Класичні векторні годинники (Vector Clocks)

Векторний годинник зберігає масив лічильників для всіх `M` вузлів системи `V = [v₁, v₂, ..., v_M]`.
- Якщо `V_A < V_B`, запис `A` однозначно є причинним предком `B`.
- Якщо `V_A` і `V_B` не порівнювані (`V_A ∥ V_B`), система **гарантовано** фіксує конфлікт і відсутність причинного зв'язку.

### 3. Точкові вектори версій (Dotted Version Vectors)

У таких сховищах, як Riak та Cassandra, кожна мутація позначається унікальною точкою `(Вузол, Версія)`, що дозволяє ефективно розділяти клієнтські контексти від серверних реплік та уникати помилкових конфліктів при паралельних записах одного клієнта.

У нашому проєкті ми реалізуємо динамічний векторний годинник `VectorClock`, який підтримує довільну кількість вузлів та автоматично адаптується до зміни топології.

---

## 3. Моделі безконфліктних регістрів (CRDT Register Semantics)

Розподілені регістри поділяються на три базові типи за способом розв'язання конфліктів при паралельних оновленнях:

### 1. LWW-Register (Last-Write-Wins Register)

Регістр із вибором останнього запису за фізичним таймстемпом. При паралельних записах перемагає версія з найбільшим значенням часу.
- **Перевага:** надзвичайна простота, фіксований розмір пам'яті (не потрібно зберігати двійники).
- **Недолік:** приховані втрати даних при несинхронізованих годинниках або одночасних редагуваннях різних полів одного документа.

### 2. MV-Register (Multi-Value Register)

Регістр, який при виявленні конкурентності зберігає всі паралельні гілки як множину двійників (Siblings).
- **Перевага:** стовідсоткова відсутність втрати даних; бізнес-застосунок сам вирішує, як об'єднати версії (наприклад, злити кошики покупок через union).
- **Недолік:** збільшення накладних витрат мережі та пам'яті; кожен читач зобов'язаний вміти розв'язувати конфлікти.

### 3. PN-Counter (Positive-Negative Counter Register)

Спеціалізований числовий регістр для розподілених лічильників (лайків, переглядів, залишків на складі). Складається з двох векторів: вектору інкрементів `P` та вектору декрементів `N`.
- Значення лічильника: `Value = ∑ P[i] - ∑ N[i]`.
- Злиття станів: `P_merged[i] = max(P_A[i], P_B[i])` та `N_merged[i] = max(N_A[i], N_B[i])`.
- Завдяки властивостям напівґратки операції додавання та віднімання комутують у будь-якому порядку без блокувань.

У нашому практичному коді реалізовано гібридний детермінований регістр: він використовує векторні годинники для відстеження причинності, а при виявленні істинного конкурентного конфлікту застосовує детерміноване правило таймстемпу з лексикографічним вирівнюванням.

---

## 4. Архітектура та математична модель регістра

Кожен запис у сховищі інкапсулюється в структуру `VersionedValue`, яка містить корисне навантаження та повний причинний контекст:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        VersionedValue                                  │
├────────────────────────────────────────────────────────────────────────┤
│  key: "config:theme"                                                   │
│  value: "dark-mode"                                                    │
│  clock: { "Node-EU": 2, "Node-US": 1 }       <── Вектор версій         │
│  timestamp_ms: 1724148000120                 <── Фізичний таймстемп    │
│  is_tombstone: false                         <── Маркер видалення      │
└────────────────────────────────────────────────────────────────────────┘
```

### Алгоритм порівняння векторних годинників

Нехай `V_A` та `V_B` — два векторні годинники, що відображають ідентифікатори вузлів у монотонні лічильники версій. Їхнє відношення класифікується за чотирма взаємовиключними станами:

```
1. Equal (Рівні):
   ∀ node : V_A[node] == V_B[node]
   [Версії ідентичні, жодних дій не потрібно]

2. Ancestor (Предок):
   (∀ node : V_A[node] ≤ V_B[node]) ∧ (∃ node : V_A[node] < V_B[node])
   [Стан A є застарілим і повинен бути беззастережно заміщений станом B]

3. Descendant (Нащадок):
   (∀ node : V_A[node] ≥ V_B[node]) ∧ (∃ node : V_A[node] > V_B[node])
   [Стан A строго новіший за стан B]

4. Concurrent (Конкурентні / Конфлікт):
   (∃ n₁ : V_A[n₁] > V_B[n₁]) ∧ (∃ n₂ : V_A[n₂] < V_B[n₂])
   [Стани виникли незалежно — потрібне застосування правила злиття]
```

Операція злиття векторів `merge(V_A, V_B)` формує покомпонентний максимум `V_res[node] = max(V_A[node], V_B[node])`, що відповідає точній операції join у напівґратці.

---

## 5. Реалізація розподіленого кластера

Нижче наведено повну реалізацію на C++ (із використанням сучасних засобів стандарту C++20: RAII, `std::optional`, потокобезпеки на м'ютексах та вичерпної типізації) та на мові Go (з горутинами, каналами та структурами синхронізації `sync.RWMutex`):

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <unordered_map>
#include <memory>
#include <optional>
#include <chrono>
#include <algorithm>
#include <mutex>
#include <cstdint>
#include <sstream>

// ── Векторний годинник (Vector Clock) ───────────────────────────────────────
enum class ClockRelation {
    Equal,      // V_A == V_B
    Ancestor,   // V_A < V_B (A строго передує B)
    Descendant, // V_A > V_B (A строго новіший за B)
    Concurrent  // V_A || V_B (Конкурентні оновлення / Конфлікт)
};

class VectorClock {
private:
    std::map<std::string, uint64_t> versions_;

public:
    VectorClock() = default;

    void increment(const std::string& node_id) {
        versions_[node_id]++;
    }

    uint64_t get(const std::string& node_id) const {
        auto it = versions_.find(node_id);
        return (it != versions_.end()) ? it->second : 0;
    }

    const std::map<std::string, uint64_t>& entries() const {
        return versions_;
    }

    // Злиття векторів: покомпонентний максимум (напівґратка)
    VectorClock merge(const VectorClock& other) const {
        VectorClock result = *this;
        for (const auto& [node, ver] : other.versions_) {
            result.versions_[node] = std::max(result.get(node), ver);
        }
        return result;
    }

    // Порівняння часткового порядку двох векторних годинників
    ClockRelation compare(const VectorClock& other) const {
        bool has_greater = false;
        bool has_less = false;

        // Збираємо всі унікальні ідентифікатори вузлів
        std::map<std::string, uint64_t> all_nodes = versions_;
        for (const auto& [node, ver] : other.versions_) {
            all_nodes[node] = std::max(all_nodes[node], ver);
        }

        for (const auto& [node, _] : all_nodes) {
            uint64_t v1 = get(node);
            uint64_t v2 = other.get(node);

            if (v1 > v2) has_greater = true;
            if (v1 < v2) has_less = true;
        }

        if (!has_greater && !has_less) return ClockRelation::Equal;
        if (has_greater && !has_less)  return ClockRelation::Descendant;
        if (!has_greater && has_less)  return ClockRelation::Ancestor;
        return ClockRelation::Concurrent;
    }

    std::string to_string() const {
        std::ostringstream oss;
        oss << "{";
        bool first = true;
        for (const auto& [node, ver] : versions_) {
            if (!first) oss << ", ";
            oss << node << ":" << ver;
            first = false;
        }
        oss << "}";
        return oss.str();
    }
};

// ── Значення з метаданими версіонування ─────────────────────────────────────
struct VersionedValue {
    std::string key;
    std::string value;
    VectorClock clock;
    int64_t timestamp_ms{0};
    bool is_tombstone{false};

    // Детерміноване злиття двох конкурентних версій
    static VersionedValue merge_concurrent(const VersionedValue& a, const VersionedValue& b) {
        VersionedValue merged;
        merged.key = a.key;
        merged.clock = a.clock.merge(b.clock);

        // Правило розв'язання конфлікту: пріоритет LWW за фізичним часом
        // При рівності фізичного часу — детермінований лексикографічний вибір
        if (a.timestamp_ms > b.timestamp_ms) {
            merged.value = a.value;
            merged.timestamp_ms = a.timestamp_ms;
            merged.is_tombstone = a.is_tombstone;
        } else if (b.timestamp_ms > a.timestamp_ms) {
            merged.value = b.value;
            merged.timestamp_ms = b.timestamp_ms;
            merged.is_tombstone = b.is_tombstone;
        } else {
            merged.value = std::max(a.value, b.value);
            merged.timestamp_ms = a.timestamp_ms;
            merged.is_tombstone = a.is_tombstone || b.is_tombstone;
        }
        return merged;
    }
};

// ── Вузол кластера (Storage Node) ──────────────────────────────────────────
class StorageNode {
private:
    std::string node_id_;
    std::unordered_map<std::string, VersionedValue> store_;
    mutable std::mutex mutex_;

public:
    explicit StorageNode(std::string node_id) : node_id_(std::move(node_id)) {}

    const std::string& id() const { return node_id_; }

    // Локальний запис із просуванням годинника вузла
    VersionedValue put_local(const std::string& key, const std::string& value,
                             const VectorClock& client_clock, int64_t timestamp_ms) {
        std::lock_guard<std::mutex> lock(mutex_);

        VectorClock new_clock = client_clock;
        new_clock.increment(node_id_);

        VersionedValue entry{
            .key = key,
            .value = value,
            .clock = new_clock,
            .timestamp_ms = timestamp_ms,
            .is_tombstone = false
        };

        store_[key] = entry;
        return entry;
    }

    // Прийом репліки від іншого вузла (із перевіркою часткового порядку)
    bool apply_replication(const VersionedValue& incoming) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = store_.find(incoming.key);

        if (it == store_.end()) {
            store_[incoming.key] = incoming;
            return true;
        }

        ClockRelation rel = incoming.clock.compare(it->second.clock);

        if (rel == ClockRelation::Descendant) {
            // Вхідний запис строго новіший — заміщуємо старий
            it->second = incoming;
            return true;
        } else if (rel == ClockRelation::Concurrent) {
            // Конкурентний запис — виконуємо детерміноване злиття
            it->second = VersionedValue::merge_concurrent(it->second, incoming);
            return true;
        }
        // Вхідний запис є предком (застарілий) — відхиляємо
        return false;
    }

    std::optional<VersionedValue> get_local(const std::string& key) const {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = store_.find(key);
        if (it != store_.end() && !it->second.is_tombstone) {
            return it->second;
        }
        return std::nullopt;
    }

    std::unordered_map<std::string, VersionedValue> get_all_entries() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return store_;
    }
};

// ── Кластерний координатор з підтримкою Read-Repair ────────────────────────
class DistributedCluster {
private:
    std::vector<std::shared_ptr<StorageNode>> nodes_;

public:
    void add_node(std::shared_ptr<StorageNode> node) {
        nodes_.push_back(std::move(node));
    }

    std::shared_ptr<StorageNode> get_node(const std::string& id) {
        for (auto& n : nodes_) {
            if (n->id() == id) return n;
        }
        return nullptr;
    }

    // Читання з кворуму з реактивним виправленням (Read-Repair)
    std::optional<VersionedValue> read_with_repair(const std::string& key,
                                                   const std::vector<std::string>& node_ids) {
        std::vector<VersionedValue> responses;
        std::vector<std::shared_ptr<StorageNode>> participating_nodes;

        for (const auto& nid : node_ids) {
            auto node = get_node(nid);
            if (!node) continue;
            participating_nodes.push_back(node);
            auto val = node->get_local(key);
            if (val.has_value()) {
                responses.push_back(*val);
            }
        }

        if (responses.empty()) return std::nullopt;

        // Знаходимо найсвіжішу або зведену версію
        VersionedValue canonical = responses[0];
        for (size_t i = 1; i < responses.size(); ++i) {
            ClockRelation rel = canonical.clock.compare(responses[i].clock);
            if (rel == ClockRelation::Ancestor) {
                canonical = responses[i];
            } else if (rel == ClockRelation::Concurrent) {
                canonical = VersionedValue::merge_concurrent(canonical, responses[i]);
            }
        }

        // Read-Repair: надсилаємо оновлений канонічний стан усім відсталим вузлам
        for (auto& node : participating_nodes) {
            auto current = node->get_local(key);
            if (!current.has_value() ||
                current->clock.compare(canonical.clock) == ClockRelation::Ancestor) {
                std::cout << "  [Read-Repair] Вузол " << node->id()
                          << " оновлено до годинника " << canonical.clock.to_string() << "\n";
                node->apply_replication(canonical);
            }
        }

        return canonical;
    }

    // Фонова анти-ентропія між двома вузлами (Gossip Sync)
    void anti_entropy_sync(const std::string& node_a_id, const std::string& node_b_id) {
        auto node_a = get_node(node_a_id);
        auto node_b = get_node(node_b_id);
        if (!node_a || !node_b) return;

        auto entries_a = node_a->get_all_entries();
        auto entries_b = node_b->get_all_entries();

        for (const auto& [k, v_a] : entries_a) {
            node_b->apply_replication(v_a);
        }
        for (const auto& [k, v_b] : entries_b) {
            node_a->apply_replication(v_b);
        }
    }
};

// ── Клієнтська сесія з гарантією Read-Your-Writes ────────────────────────────
class ClientSession {
private:
    std::string client_id_;
    DistributedCluster& cluster_;
    VectorClock session_clock_; // Токен причинності клієнта

public:
    ClientSession(std::string client_id, DistributedCluster& cluster)
        : client_id_(std::move(client_id)), cluster_(cluster) {}

    void write(const std::string& preferred_node, const std::string& key,
               const std::string& value, int64_t timestamp_ms) {
        auto node = cluster_.get_node(preferred_node);
        if (!node) throw std::runtime_error("Node not found");

        VersionedValue result = node->put_local(key, value, session_clock_, timestamp_ms);
        // Оновлюємо клієнтський токен версії
        session_clock_ = session_clock_.merge(result.clock);

        std::cout << "[Client " << client_id_ << " Write] Ключ: " << key
                  << " -> " << preferred_node << ", новий токен: "
                  << session_clock_.to_string() << "\n";
    }

    // Читання з перевіркою сесійного інваріанта
    std::optional<std::string> read_with_session_guarantee(const std::string& target_node,
                                                           const std::string& key) {
        auto node = cluster_.get_node(target_node);
        if (!node) return std::nullopt;

        auto val = node->get_local(key);

        // Перевіряємо, чи вузол уже наздогнав власний запис клієнта
        if (val.has_value()) {
            ClockRelation rel = val->clock.compare(session_clock_);
            if (rel == ClockRelation::Ancestor) {
                std::cout << "  [Попередження] Вузол " << target_node
                          << " відстає від сесії клієнта! Потрібен Read-Repair.\n";
            }
        }

        // Якщо вузол відстає — ініціюємо читання з виправленням по кластеру
        auto repaired = cluster_.read_with_repair(key, {"Node-EU", "Node-US"});
        if (repaired.has_value()) {
            session_clock_ = session_clock_.merge(repaired->clock);
            return repaired->value;
        }
        return std::nullopt;
    }
};

int main() {
    DistributedCluster cluster;
    auto node_eu = std::make_shared<StorageNode>("Node-EU");
    auto node_us = std::make_shared<StorageNode>("Node-US");

    cluster.add_node(node_eu);
    cluster.add_node(node_us);

    std::cout << "=== 1. Одночасні записи в ізольовані регіони (Мережевий поділ) ===\n";
    ClientSession client_alice("Alice", cluster);
    ClientSession client_bob("Bob", cluster);

    // Аліса пише в Регіон EU, Боб пише в Регіон US одночасно
    client_alice.write("Node-EU", "config:theme", "dark-mode", 1000);
    client_bob.write("Node-US", "config:theme", "light-mode", 1005);

    std::cout << "\n=== 2. Стан вузлів до синхронізації ===\n";
    auto val_eu = node_eu->get_local("config:theme");
    auto val_us = node_us->get_local("config:theme");
    std::cout << "Node-EU стан: " << (val_eu ? val_eu->value : "null")
              << " | годинник: " << val_eu->clock.to_string() << "\n";
    std::cout << "Node-US стан: " << (val_us ? val_us->value : "null")
              << " | годинник: " << val_us->clock.to_string() << "\n";

    std::cout << "\n=== 3. Аліса читає з Node-US (Сесійний захист + Read-Repair) ===\n";
    auto res_alice = client_alice.read_with_session_guarantee("Node-US", "config:theme");
    std::cout << "Аліса отримала зведений результат: " << (res_alice ? *res_alice : "null") << "\n";

    std::cout << "\n=== 4. Фонова синхронізація Anti-Entropy (Повна збіжність) ===\n";
    cluster.anti_entropy_sync("Node-EU", "Node-US");

    auto final_eu = node_eu->get_local("config:theme");
    auto final_us = node_us->get_local("config:theme");
    std::cout << "Node-EU фінал: " << final_eu->value << " | " << final_eu->clock.to_string() << "\n";
    std::cout << "Node-US фінал: " << final_us->value << " | " << final_us->clock.to_string() << "\n";

    return 0;
}
```
```go
package main

import (
	"fmt"
	"sync"
)

// ClockRelation визначає частковий порядок двох векторних годинників
type ClockRelation int

const (
	Equal ClockRelation = iota
	Ancestor
	Descendant
	Concurrent
)

// VectorClock реалізує векторний годинник версіонування
type VectorClock struct {
	versions map[string]uint64
}

func NewVectorClock() VectorClock {
	return VectorClock{versions: make(map[string]uint64)}
}

func (vc VectorClock) Clone() VectorClock {
	c := NewVectorClock()
	for k, v := range vc.versions {
		c.versions[k] = v
	}
	return c
}

func (vc VectorClock) Increment(nodeID string) {
	vc.versions[nodeID]++
}

func (vc VectorClock) Get(nodeID string) uint64 {
	return vc.versions[nodeID]
}

func (vc VectorClock) Merge(other VectorClock) VectorClock {
	res := vc.Clone()
	for node, ver := range other.versions {
		if ver > res.versions[node] {
			res.versions[node] = ver
		}
	}
	return res
}

func (vc VectorClock) Compare(other VectorClock) ClockRelation {
	hasGreater, hasLess := false, false
	allNodes := make(map[string]struct{})
	for k := range vc.versions {
		allNodes[k] = struct{}{}
	}
	for k := range other.versions {
		allNodes[k] = struct{}{}
	}

	for node := range allNodes {
		v1 := vc.Get(node)
		v2 := other.Get(node)
		if v1 > v2 {
			hasGreater = true
		}
		if v1 < v2 {
			hasLess = true
		}
	}

	if !hasGreater && !hasLess {
		return Equal
	}
	if hasGreater && !hasLess {
		return Descendant
	}
	if !hasGreater && hasLess {
		return Ancestor
	}
	return Concurrent
}

func (vc VectorClock) String() string {
	res := "{"
	first := true
	for k, v := range vc.versions {
		if !first {
			res += ", "
		}
		res += fmt.Sprintf("%s:%d", k, v)
		first = false
	}
	res += "}"
	return res
}

// VersionedValue представляє сутність даних із метаданими
type VersionedValue struct {
	Key         string
	Value       string
	Clock       VectorClock
	TimestampMS int64
	IsTombstone bool
}

func MergeConcurrent(a, b VersionedValue) VersionedValue {
	merged := VersionedValue{
		Key:   a.Key,
		Clock: a.Clock.Merge(b.Clock),
	}
	if a.TimestampMS >= b.TimestampMS {
		merged.Value = a.Value
		merged.TimestampMS = a.TimestampMS
		merged.IsTombstone = a.IsTombstone
	} else {
		merged.Value = b.Value
		merged.TimestampMS = b.TimestampMS
		merged.IsTombstone = b.IsTombstone
	}
	return merged
}

// StorageNode представляє локальний сервер зберігання
type StorageNode struct {
	nodeID string
	mu     sync.RWMutex
	store  map[string]VersionedValue
}

func NewStorageNode(nodeID string) *StorageNode {
	return &StorageNode{
		nodeID: nodeID,
		store:  make(map[string]VersionedValue),
	}
}

func (n *StorageNode) PutLocal(key, value string, clientClock VectorClock, ts int64) VersionedValue {
	n.mu.Lock()
	defer n.mu.Unlock()

	newClock := clientClock.Clone()
	newClock.Increment(n.nodeID)

	entry := VersionedValue{
		Key:         key,
		Value:       value,
		Clock:       newClock,
		TimestampMS: ts,
		IsTombstone: false,
	}
	n.store[key] = entry
	return entry
}

func (n *StorageNode) ApplyReplication(incoming VersionedValue) bool {
	n.mu.Lock()
	defer n.mu.Unlock()

	current, exists := n.store[incoming.Key]
	if !exists {
		n.store[incoming.Key] = incoming
		return true
	}

	rel := incoming.Clock.Compare(current.Clock)
	if rel == Descendant {
		n.store[incoming.Key] = incoming
		return true
	} else if rel == Concurrent {
		n.store[incoming.Key] = MergeConcurrent(current, incoming)
		return true
	}
	return false
}

func (n *StorageNode) GetLocal(key string) (VersionedValue, bool) {
	n.mu.RLock()
	defer n.mu.RUnlock()
	val, ok := n.store[key]
	if ok && !val.IsTombstone {
		return val, true
	}
	return VersionedValue{}, false
}

func (n *StorageNode) GetAll() map[string]VersionedValue {
	n.mu.RLock()
	defer n.mu.RUnlock()
	res := make(map[string]VersionedValue, len(n.store))
	for k, v := range n.store {
		res[k] = v
	}
	return res
}

// DistributedCluster керує координацією між вузлами
type DistributedCluster struct {
	nodes map[string]*StorageNode
}

func NewDistributedCluster() *DistributedCluster {
	return &DistributedCluster{nodes: make(map[string]*StorageNode)}
}

func (c *DistributedCluster) AddNode(node *StorageNode) {
	c.nodes[node.nodeID] = node
}

func (c *DistributedCluster) ReadWithRepair(key string, nodeIDs []string) (VersionedValue, bool) {
	var responses []VersionedValue
	var queried []*StorageNode

	for _, nid := range nodeIDs {
		node, ok := c.nodes[nid]
		if !ok {
			continue
		}
		queried = append(queried, node)
		if val, found := node.GetLocal(key); found {
			responses = append(responses, val)
		}
	}

	if len(responses) == 0 {
		return VersionedValue{}, false
	}

	canonical := responses[0]
	for i := 1; i < len(responses); i++ {
		rel := canonical.Clock.Compare(responses[i].Clock)
		if rel == Ancestor {
			canonical = responses[i]
		} else if rel == Concurrent {
			canonical = MergeConcurrent(canonical, responses[i])
		}
	}

	// Read-Repair для вузлів із застарілою версією
	for _, node := range queried {
		if cur, found := node.GetLocal(key); !found || cur.Clock.Compare(canonical.Clock) == Ancestor {
			fmt.Printf("  [Read-Repair] Вузол %s оновлено до актуального стану\n", node.nodeID)
			node.ApplyReplication(canonical)
		}
	}

	return canonical, true
}

func (c *DistributedCluster) AntiEntropySync(nodeAID, nodeBID string) {
	nodeA := c.nodes[nodeAID]
	nodeB := c.nodes[nodeBID]
	if nodeA == nil || nodeB == nil {
		return
	}

	for _, v := range nodeA.GetAll() {
		nodeB.ApplyReplication(v)
	}
	for _, v := range nodeB.GetAll() {
		nodeA.ApplyReplication(v)
	}
}

// ClientSession реалізує клієнтський контекст із гарантією RYW
type ClientSession struct {
	clientID     string
	cluster      *DistributedCluster
	sessionClock VectorClock
}

func NewClientSession(clientID string, cluster *DistributedCluster) *ClientSession {
	return &ClientSession{
		clientID:     clientID,
		cluster:      cluster,
		sessionClock: NewVectorClock(),
	}
}

func (cs *ClientSession) Write(preferredNode, key, value string, ts int64) {
	node := cs.cluster.nodes[preferredNode]
	if node == nil {
		panic("Node not found")
	}

	res := node.PutLocal(key, value, cs.sessionClock, ts)
	cs.sessionClock = cs.sessionClock.Merge(res.Clock)
	fmt.Printf("[Client %s Write] Ключ: %s -> %s, токен: %s\n", cs.clientID, key, preferredNode, cs.sessionClock.String())
}

func (cs *ClientSession) ReadWithGuarantee(targetNode, key string) (string, bool) {
	node := cs.cluster.nodes[targetNode]
	if node == nil {
		return "", false
	}

	val, found := node.GetLocal(key)
	if found {
		rel := val.Clock.Compare(cs.sessionClock)
		if rel == Ancestor {
			fmt.Printf("  [Попередження] Вузол %s відстає від сесії клієнта! Запуск Read-Repair.\n", targetNode)
		}
	}

	repaired, ok := cs.cluster.ReadWithRepair(key, []string{"Node-EU", "Node-US"})
	if ok {
		cs.sessionClock = cs.sessionClock.Merge(repaired.Clock)
		return repaired.Value, true
	}
	return "", false
}

func main() {
	cluster := NewDistributedCluster()
	nodeEU := NewStorageNode("Node-EU")
	nodeUS := NewStorageNode("Node-US")
	cluster.AddNode(nodeEU)
	cluster.AddNode(nodeUS)

	fmt.Println("=== 1. Одночасні записи в ізольовані вузли (Partition) ===")
	alice := NewClientSession("Alice", cluster)
	bob := NewClientSession("Bob", cluster)

	alice.Write("Node-EU", "config:theme", "dark-mode", 1000)
	bob.Write("Node-US", "config:theme", "light-mode", 1005)

	valEU, _ := nodeEU.GetLocal("config:theme")
	valUS, _ := nodeUS.GetLocal("config:theme")
	fmt.Printf("Node-EU стан: %s | Clock: %s\n", valEU.Value, valEU.Clock.String())
	fmt.Printf("Node-US стан: %s | Clock: %s\n", valUS.Value, valUS.Clock.String())

	fmt.Println("\n=== 2. Аліса читає з Node-US (Сесійний захист + Read-Repair) ===\n")
	resAlice, _ := alice.ReadWithGuarantee("Node-US", "config:theme")
	fmt.Printf("Аліса отримала зведений результат: %s\n", resAlice)

	fmt.Println("\n=== 3. Фонова анти-ентропія (Anti-Entropy Sync) ===")
	cluster.AntiEntropySync("Node-EU", "Node-US")
	finalEU, _ := nodeEU.GetLocal("config:theme")
	finalUS, _ := nodeUS.GetLocal("config:theme")
	fmt.Printf("Node-EU фінал: %s | Clock: %s\n", finalEU.Value, finalEU.Clock.String())
	fmt.Printf("Node-US фінал: %s | Clock: %s\n", finalUS.Value, finalUS.Clock.String())
}
```
:::

---

## 6. Покроковий розбір конвеєра реплікації та розв'язання конфліктів

Простежимо, що саме відбувається в системі на кожному кроці виконання демонстраційної програми:

### Етап 1: Розгалуження версій (Branching)

Аліса відправляє запит на запис значення `"dark-mode"` на вузол `Node-EU`. На цей момент її сесійний годинник порожній `{}`.
1. `Node-EU` генерує новий векторний годинник, інкрементуючи власний лічильник: `{"Node-EU": 1}`.
2. Фіксується фізичний час `timestamp_ms = 1000`.
3. Аліса отримує підтвердження й зберігає оновлений токен `{"Node-EU": 1}` у своїй локальній сесії.

У цей самий час у паралельному потоці Боб відправляє запис `"light-mode"` на вузол `Node-US`.
1. `Node-US` генерує годинник `{"Node-US": 1}` та фіксує фізичний час `timestamp_ms = 1005`.
2. Боб оновлює свій сесійний токен до `{"Node-US": 1}`.

Оскільки між вузлами відсутній синхронний зв'язок, жоден із них не знає про запис сусіда. Стан кластера розходиться.

### Етап 2: Виявлення паралелізму та Read-Repair

Аліса відкриває наступну сторінку, і її запит потрапляє через географічний балансувальник на вузол `Node-US`.
1. Клієнтська сесія передає збережений токен `{"Node-EU": 1}`.
2. Вузол `Node-US` перевіряє свій локальний запис, який має годинник `{"Node-US": 1}`.
3. Метод `compare()` порівнює `{"Node-US": 1}` та `{"Node-EU": 1}`:
   - Вузол `Node-US` має більший лічильник для себе (`1 > 0`);
   - Вузол `Node-EU` має більший лічильник для себе (`0 < 1`);
   - Результат: `ClockRelation::Concurrent`.
4. Сесійний шар виявляє, що `Node-US` не містить причинного предка запису Аліси, тому ініціює читання з виправленням `read_with_repair()` по всіх доступних вузлах кластера.
5. Координатор збирає обидві версії та виконує детерміноване злиття `merge_concurrent()`:
   - Об'єднаний векторний годинник: `{"Node-EU": 1, "Node-US": 1}`;
   - Фізичний таймстемп Боба `1005` більший за таймстемп Аліси `1000`, тому канонічним значенням обирається `"light-mode"`.
6. Координатор негайно відправляє канонічний стан на `Node-EU` та `Node-US`, ліквідуючи розбіжність на обох серверах.

### Етап 3: Повна збіжність через фонову анти-ентропію

Фоновий процес `anti_entropy_sync()` періодично сканує таблиці сусідніх вузлів:
1. `Node-EU` передає свій зведений стан `{"Node-EU": 1, "Node-US": 1}` на `Node-US`.
2. `Node-US` порівнює вхідний годинник зі своїм локальним. Оскільки вони вже рівні або вхідний є нащадком, стан стабілізується.
3. Обидва вузли досягають ідентичного значення `"light-mode"` з годинником `{"Node-EU": 1, "Node-US": 1}`.

---

## 7. Інтеграція з транспортним протоколом: HTTP-заголовки та сесійні проксі

У реальних веб-сервісах клієнтський застосунок взаємодіє з розподіленим сховищем через протокол HTTP REST або gRPC. Щоб приховати складність векторних годинників від кінцевого бізнес-коду, сесійний механізм виносять у проміжний шар (API Gateway або HTTP Middleware).

### Формат сесійного токена у HTTP-заголовках

При виконанні будь-якої операції запису сервер повертає серіалізований причинний токен у заголовку відповіді:

```http
HTTP/1.1 200 OK
Content-Type: application/json
ETag: W/"v-NodeEU:3,NodeUS:1"
X-State-Causal-Token: eyJOb2RlRVUiOjMsIk5vZGVVUyI6MX0=
```

Клієнтський браузер або мобільний SDK зберігає цей токен у локальному сховищі (LocalStorage, Cookie або пам'ять сесії). При наступному запиті на читання клієнт автоматично прикріплює токен у заголовках запиту:

```http
GET /api/v1/user/profile HTTP/1.1
Host: api.example.com
If-None-Match: W/"v-NodeEU:3,NodeUS:1"
X-Session-Minimum-Version: eyJOb2RlRVUiOjMsIk5vZGVVUyI6MX0=
```

### Алгоритм маршрутизації на API-шлюзі

API-шлюз або балансувальник навантаження реалізує алгоритм перевірки свіжості:
1. Шлюз розпаковує токен `X-Session-Minimum-Version` і витягує вектор мінімально необхідних версій `V_req`.
2. Шлюз направляє запит на найближчу локальну репліку `Node-Local`.
3. Репліка перевіряє свій локальний стан `V_local`. Якщо `V_local ≥ V_req`, вона миттєво віддає дані.
4. Якщо `V_local < V_req` (репліка відстає від сесії клієнта), шлюз застосовує одну з трьох стратегій:
   - **Pinned Fallback:** перенаправляє запит на вузол-лідер або вузол, де клієнт виконував останній запис;
   - **Local Wait (Bounded Polling):** призупиняє відповідь на 10–20 мс, очікуючи, поки реплікація дожене LSN запису;
   - **Cluster Quorum Read:** опитує кворум вузлів із примусовим Read-Repair.

Завдяки цьому користувач завжди бачить власні збережені дані без необхідності синхронного блокування всієї бази даних.

---

## 8. Зберігання на диску: інтеграція з LSM-деревом та журналами WAL

У пам'яті дані живуть у швидких структурах `std::unordered_map` або `std::map`, але для забезпечення довговічності (Durability) кожна репліка зобов'язана фіксувати зміни на постійному накопичувачі (SSD / NVMe).

У системах класу Apache Cassandra, ScyllaDB або RocksDB архітектура дискового збереження базується на **LSM-деревах** (Log-Structured Merge-Trees):

```
Клієнтський запис
      │
      ▼
┌──────────────┐    Паралельно     ┌────────────────┐
│  CommitLog   │ ───────────────►  │  MemTable      │  (У пам'яті: B-дерево
│  (WAL на SSD)│                   │  (RAM Buffer)  │   з векторними годинниками)
└──────────────┘                   └────────────────┘
                                           │
                           При заповненні  │ Flush на диск
                                           ▼
                                   ┌────────────────┐
                                   │  SSTable L0    │  (Незмінний файл на диску)
                                   └────────────────┘
                                           │
                                           │ Фонова компакція (Compaction)
                                           ▼
                                   ┌────────────────┐
                                   │  SSTable L1..k │  (Злиття напівґраткою)
                                   └────────────────┘
```

### Особливості обробки векторних годинників у рушії зберігання:
1. **Незмінність SSTable:** старі версії файлів ніколи не модифікуються на місці. Новий запис створює свіжий рядок із новим векторним годинником.
2. **Фільтри Блума (Bloom Filters):** перед читанням файлу SSTable з диска рушій перевіряє фільтр Блума. Якщо ключ відсутній у файлі, дорогий дисковий пошук пропускається.
3. **Злиття при компакції:** коли фоновий потік зливає кілька SSTable файлів в один (Major Compaction), він знаходить дублікати одного ключа, порівнює їхні векторні годинники й фізичні таймстеми, викликає детерміноване правило `merge_concurrent()` і записує на диск лише єдину актуальну версію, фізично видаляючи застарілих предків та надгробки з вичерпаним TTL.

---

## 9. Розподілене трасування та спостережуваність (Observability)

Коли запити реплікації розлітаються мережею асинхронно, традиційні логи окремих серверів стають безпорадними: неможливо зрозуміти, чому конкретне читання повернуло застарілу версію і яка саме ланка реплікації затримала оновлення.

Для діагностики систем із кінцевою узгодженістю використовують розподілений трейсинг (OpenTelemetry / W3C Trace Context):

```
1. Наскрізний контекст трасування:
   Кожен клієнтський запис генерує унікальний traceparent за стандартом W3C:
   traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01

2. Передача контексту крізь асинхронні повідомлення:
   Координатор запису вкладає цей traceparent у службовий заголовок
   пакета реплікації. Коли репліка отримує WAL або повідомлення пліток,
   вона створює дочірній спан (Span), фіксуючи точний час застосування
   та поточний реплікаційний лаг у метриках OpenTelemetry.

3. Моніторинг затримки збіжності:
   Система моніторингу (Prometheus / Grafana) рахує гістограму часу
   між моментом створення запису на координаторі та моментом його
   фіксації на останній з N реплік (метрика replication_convergence_time_ms).
   Якщо 99-й перцентиль p99 перевищує 500 мс, генерується сповіщення для чергового інженера.
```

---

## 10. Ідемпотентність повторів та дедуплікація транзакцій

У розподілених мережах ненадійність каналу зв'язку призводить до повторних спроб (Retries). Якщо клієнт відправив запис, сервер успішно зафіксував його в базі даних, але HTTP-відповідь `200 OK` загубилася через тайм-аут сокета, клієнт неминуче повторить спробу (Retry).

Без спеціального захисту повторний запис спричинить подвійне інкрементування векторного годинника (`{"Node-EU": 2}` замість `{"Node-EU": 1}`), що викривить історію причинності.

Для захисту від дублікатів застосовують два правила:
1. **Клієнтський ключ ідемпотентності (Idempotency Key):** кожен запит містить унікальний UUID або хеш операції. Вузол зберігає таблицю останніх оброблених ідентифікаторів. Повторний запит повертає раніше згенерований `VersionedValue` без повторної мутації годинника.
2. **Ідемпотентність оператора злиття:** операція `apply_replication(incoming)` перевіряє `rel == ClockRelation::Equal`. Якщо вхідний запис має точно такий самий векторний годинник, він ігнорується без зміни локального стану сховища.

---

## 11. Виробничі пастки та захисні шаблони

Під час промислової експлуатації кінцево-узгоджених сховищ виникають чотири класи критичних пасток:

### 1. Неконтрольоване розростання векторних годинників (Vector Clock Bloat)

Якщо в системі діють тисячі мікросервісів або клієнтів, які модифікують записи, словник `map<string, uint64_t>` у кожному рядку таблиці розростається до кілобайтів.

- **Механізм проблеми:** кожен новий ідентифікатор клієнта додає ключ до карти, збільшуючи накладні витрати на передачу мережею та дисковий простір.
- **Захист:** застосування алгоритмів усікання (Clock Pruning / Truncation). Вузол зберігає щонайбільше `K_max` найновіших записів (наприклад, 10), а для решти веде єдину нижню часову межу.

### 2. Накопичення надгробків та їх воскресіння (Tombstone Resurrection)

При видаленні ключа не можна просто стерти запис із пам'яті, оскільки сусідня репліка під час наступної анти-ентропії сприйме «відсутність» запису як застарілість і знову відновить видалений об'єкт. Видалення фіксується як запис спеціального маркера — «надгробка» (Tombstone).

- **Механізм проблеми:** якщо надгробок видалити занадто рано (раніше, ніж завершиться реплікація на відсталий вузол), відсталий вузол надішле старий стан і «воскресить» видалені дані.
- **Захист:** двофазне видалення з горизонтом збирання сміття (GC Grace Seconds). Надгробок зберігається протягом періоду, гарантовано більшого за максимальний інтервал реплікаційного лагу (наприклад, 10 днів у Cassandra), після чого фізично видаляється фоновим процесом компакції (Compaction).

### 3. Шторм виправлень на гарячих ключах (Read-Repair Storm)

Якщо популярний ключ (наприклад, конфігурація головної сторінки) читають 50 000 клієнтів щосекунди, і одна репліка тимчасово відстала, всі 50 000 запитів одночасно спробують відправити фоновий запис Read-Repair на цю репліку, перевантажуючи її процесор та мережу.

- **Механізм проблеми:** мультиплікація трафіку виправлення пропорційно читацькому навантаженню (`N_repairs = QPS · P(stale)`).
- **Захист:** застосування ймовірнісного лагодження (Probabilistic Read-Repair, наприклад, лише для 1% прочитаних запитів) або використання дедуплікатора запитів (патерн Singleflight).

### 4. Втрата зв'язку клієнта та оновлення сесійних токенів

Якщо мобільний застосунок користувача кешує занадто старий сесійний токен (наприклад, після трьох днів перебування в режимі польоту), спроба передати цей токен на сучасний вузол може спричинити зайві дорогі перевірки або помилкову класифікацію актуальних даних як застарілих.

- **Захист:** обмеження часу життя сесійного токена (TTL токена). Якщо вік токена перевищує гарантований інтервал фонової збіжності кластера (наприклад, 60 секунд), сесійний шар вважає кластер гарантовано збіжним і скидає токен до базового стану.

---

## 12. Профілювання пам'яті та оптимізація гарячого шляху

У високонавантажених C++ сервісах структура `std::map<std::string, uint64_t>` для векторного годинника створює надмірну кількість динамічних алокацій у кучі (Heap Allocations), що навантажує алокатор пам'яті при 100 000 запитів/с.

Для оптимізації гарячого шляху застосовують три інженерні техніки:

```
1. Фіксований плоский масив (Flat Small-Vector):
   Якщо кількість реплік у кластері невелика (наприклад, N = 3 або N = 5),
   замість std::map використовують std::array<uint64_t, N> з числовими ID вузлів.
   Це зменшує розмір годинника до 24-40 байтів та дозволяє розміщувати його
   прямо на стеку процесора без жодного виклику malloc.

2. Секційне блокування таблиці (Sharded Mutex Partitioning):
   Замість одного загального std::mutex на весь вузол, таблиця розбивається
   на 64 або 128 незалежних сегментів за хешем ключа (std::hash<string>{}(key) % 128).
   Це усуває конкуренцію за блокування між незалежними ключами.

3. Асинхронний Read-Repair через чергу задач (Non-blocking Writeback):
   Координатор читання не чекає завершення запису на відсталу репліку, а відправляє
   задачу лагодження в неблокуючу чергу фонового пулу потоків, негайно
   повертаючи результат клієнту.
```

---

## 13. Методологія тестування на збіжність (Chaos Testing)

Щоб довести надійність кінцево-узгодженої системи перед запуском у прод, застосовують автоматизовані хаос-тести (подібні до інструменту Jepsen):

```
1. Ін'єкція штучних затримок та розривів (Fault Injection):
   Фреймворк випадковим чином блокує TCP-пакети між парою вузлів (iptables DROP)
   на 5-10 секунд, симулюючи розділення мережі.

2. Генерація паралельного навантаження (Concurrent Workload):
   Сотні віртуальних клієнтів одночасно виконують випадкові операції запису
   та читання на різних вузлах кластера, записуючи повний аудит-лог.

3. Перевірка інваріантів (Invariant Verification):
   - Інваріант збіжності: після відновлення зв'язку та очікування T_gossip
     хеш стану всіх вузлів зобов'язаний збігтися до єдиного бінарного значення;
   - Інваріант сесій: жоден клієнт не повинен зафіксувати відкат версії
     у своїй локальній часовій шкалі (Monotonic Reads Check);
   - Інваріант причинності: жодна транзакція не повинна з'явитися раніше
     своїх причинних предків (Causal Consistency Check).
```

Ці інженерні практики та архітектурні патерни перетворюють кінцево-узгоджений регістр на надстійку, детерміновану та блискавично швидку платформу для сучасних хмарних систем.
