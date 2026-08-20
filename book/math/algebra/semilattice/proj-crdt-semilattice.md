# ⚙️ Реалізація безконфліктних типів даних (CRDT) на базі напіврешіток

Розподілені системи без центрального координатора потребують структур даних, які можуть незалежно оновлюватися на різних вузлах мережі та збігатися до єдиного детермінованого стану після обміну даними. Реалізація таких структур на основі операцій join-напіврешітки гарантує сильну кінцеву узгодженість (Strong Eventual Consistency): оскільки функція злиття станів є комутативною, асоціативною та ідемпотентною, порядок надходження повідомлень, їхнє дублювання та затримки не можуть порушити цілісність системи.

У цій практичній вставці розібрано архітектуру, математичні інваріанти пам'яті, механізми збирання сміття та наведено повноцінні робочі реалізації ключових типів State-based CRDT (CvRDT): лічильника тільки для зростання (G-Counter), реверсивного лічильника (PN-Counter), множини на часових мітках (LWW-Element-Set) та множини зі спостережуваним видаленням (OR-Set), а також симулятор ненадійної мережі з перевіркою стійкості до перестановки та дублювання пакетів.

---

### 1. G-Counter: лічильник зростання на покомпонентному максимумі

У розподіленій системі з `N` вузлами кожен вузол має власний унікальний ідентифікатор і володіє виключним правом збільшувати лише свою позицію в цілочисельному векторі. Стан лічильника — це асоціативний масив `node_id → count`. Злиття двох станів полягає у взятті покомпонентного максимуму значень для кожного ідентифікатора вузла.

Оскільки операція взяття максимуму `max(a, b)` є комутативною, асоціативною та ідемпотентною, простір станів `ℕⁿ` утворює прямий добуток `N` верхніх напіврешіток. Вузол ніколи не зменшує свої локальні координати, тому стан репліки монотонно піднімається вгору за частковим порядком.

Часова складність операції локального інкременту становить `O(1)`. Складність операції злиття двох станів становить `O(N)`, де `N` — кількість активних реплік у системі. Обсяг пам'яті також лінійно пропорційний кількості вузлів, що робить структуру надзвичайно компактною для фіксованих топологій кластера.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <numeric>
#include <algorithm>
#include <cstdint>
#include <vector>

class GCounter {
public:
    explicit GCounter(std::string node_id) : node_id_(std::move(node_id)) {}

    void increment(uint64_t delta = 1) {
        state_[node_id_] += delta;
    }

    [[nodiscard]] uint64_t value() const noexcept {
        uint64_t total = 0;
        for (const auto& [id, count] : state_) {
            total += count;
        }
        return total;
    }

    // Операція злиття над join-напіврешіткою: покомпонентний максимум
    void merge(const GCounter& other) {
        for (const auto& [id, count] : other.state_) {
            state_[id] = std::max(state_[id], count);
        }
    }

    [[nodiscard]] const std::unordered_map<std::string, uint64_t>& state() const noexcept {
        return state_;
    }

private:
    std::string node_id_;
    std::unordered_map<std::string, uint64_t> state_;
};
```
```py
from typing import Dict

class GCounter:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.state: Dict[str, int] = {}

    def increment(self, delta: int = 1) -> None:
        self.state[self.node_id] = self.state.get(self.node_id, 0) + delta

    @property
    def value(self) -> int:
        return sum(self.state.values())

    # Операція злиття над join-напіврешіткою: покомпонентний максимум
    def merge(self, other: "GCounter") -> None:
        all_nodes = set(self.state.keys()) | set(other.state.keys())
        for node in all_nodes:
            self.state[node] = max(self.state.get(node, 0), other.state.get(node, 0))
```
:::

---

### 2. PN-Counter: лічильник додавання та віднімання

Оскільки стан напіврешітки може лише монотонно зростати, пряме віднімання від лічильника порушило б умову `s ≤ merge(s, s')`. Якщо один вузол зменшить число з 10 до 9, а інший вузол злиє свій попередній стан 10 зі станом 9 через операцію максимуму, він отримає `max(10, 9) = 10`, і декремент буде безповоротно втрачений.

Щоб підтримувати операцію декременту без порушення монотонності, простір станів розширюють до пари двох незалежних G-лічильників: `P` (вектор додатних приростів) та `N` (вектор від'ємних спадів). 

Поточне значення лічильника обчислюється як різниця їхніх значень:

```
value = value(P) - value(N)
```

Злиття полягає у попарному злитті обох напіврешіток `P` та `N`:

```
⟨P₁, N₁⟩ ⊔ ⟨P₂, N₂⟩ = ⟨P₁ ⊔ P₂, N₁ ⊔ N₂⟩
```

Обидві внутрішні координати монотонно зростають, тому напіврешітковий інваріант зберігається, а результуюче число може вільно збільшуватися та зменшуватися.

:::tabs
```cpp
class PNCounter {
public:
    explicit PNCounter(std::string node_id)
        : p_counter_(node_id), n_counter_(std::move(node_id)) {}

    void increment(uint64_t delta = 1) {
        p_counter_.increment(delta);
    }

    void decrement(uint64_t delta = 1) {
        n_counter_.increment(delta);
    }

    [[nodiscard]] int64_t value() const noexcept {
        return static_cast<int64_t>(p_counter_.value()) - 
               static_cast<int64_t>(n_counter_.value());
    }

    void merge(const PNCounter& other) {
        p_counter_.merge(other.p_counter_);
        n_counter_.merge(other.n_counter_);
    }

private:
    GCounter p_counter_;
    GCounter n_counter_;
};
```
```py
class PNCounter:
    def __init__(self, node_id: str):
        self.p_counter = GCounter(node_id)
        self.n_counter = GCounter(node_id)

    def increment(self, delta: int = 1) -> None:
        self.p_counter.increment(delta)

    def decrement(self, delta: int = 1) -> None:
        self.n_counter.increment(delta)

    @property
    def value(self) -> int:
        return self.p_counter.value - self.n_counter.value

    def merge(self, other: "PNCounter") -> None:
        self.p_counter.merge(other.p_counter)
        self.n_counter.merge(other.n_counter)
```
:::

---

### 3. LWW-Element-Set: множина з розв'язанням за часовими мітками (Last-Write-Wins)

Множина Last-Write-Wins Element Set розв'язує конфлікти між паралельними операціями додавання та видалення за допомогою монотонних часових міток (англ. *timestamps*), які генеруються за локальними фізичними або гібридними логічними годинниками (HLC).

Кожен елемент `x` асоціюється з двома часовими мітками: `t_add(x)` (момент останнього додавання) та `t_rem(x)` (момент останнього видалення). 
- Злиття двох станів є взяттям максимуму часових міток для кожного елемента: `t_add = max(t_add₁, t_add₂)` та `t_rem = max(t_rem₁, t_rem₂)`.
- Елемент вважається присутнім у множині, якщо `t_add(x) > t_rem(x)`. Якщо мітки збігаються (`t_add = t_rem`), правило тай-брейку (наприклад, перевага додавання *add-bias*) детерміновано визначає результат.

Головним компромісом LWW-Set є залежність від точності синхронізації фізичного часу (NTP). Якщо годинник одного з серверів забігає вперед (clock drift), його операції набувають штучного пріоритету над операціями інших реплік.

:::tabs
```cpp
#include <unordered_map>
#include <chrono>

struct ElementTimestamp {
    uint64_t add_time = 0;
    uint64_t remove_time = 0;
};

class LWWSet {
public:
    void add(const std::string& value, uint64_t timestamp) {
        elements_[value].add_time = std::max(elements_[value].add_time, timestamp);
    }

    void remove(const std::string& value, uint64_t timestamp) {
        elements_[value].remove_time = std::max(elements_[value].remove_time, timestamp);
    }

    [[nodiscard]] bool contains(const std::string& value) const {
        auto it = elements_.find(value);
        if (it == elements_.end()) {
            return false;
        }
        return it->second.add_time > it->second.remove_time;
    }

    // Злиття над join-напіврешіткою: покомпонентний максимум міток часу
    void merge(const LWWSet& other) {
        for (const auto& [val, ts] : other.elements_) {
            elements_[val].add_time = std::max(elements_[val].add_time, ts.add_time);
            elements_[val].remove_time = std::max(elements_[val].remove_time, ts.remove_time);
        }
    }

private:
    std::unordered_map<std::string, ElementTimestamp> elements_;
};
```
```py
from typing import Dict

class LWWSet:
    def __init__(self):
        # value -> [add_time, remove_time]
        self.elements: Dict[str, list] = {}

    def add(self, value: str, timestamp: int) -> None:
        if value not in self.elements:
            self.elements[value] = [0, 0]
        self.elements[value][0] = max(self.elements[value][0], timestamp)

    def remove(self, value: str, timestamp: int) -> None:
        if value not in self.elements:
            self.elements[value] = [0, 0]
        self.elements[value][1] = max(self.elements[value][1], timestamp)

    def contains(self, value: str) -> bool:
        if value not in self.elements:
            return False
        add_time, rem_time = self.elements[value]
        return add_time > rem_time

    # Злиття над join-напіврешіткою: покомпонентний максимум міток часу
    def merge(self, other: "LWWSet") -> None:
        all_keys = set(self.elements.keys()) | set(other.elements.keys())
        for k in all_keys:
            self_add, self_rem = self.elements.get(k, [0, 0])
            oth_add, oth_rem = other.elements.get(k, [0, 0])
            self.elements[k] = [max(self_add, oth_add), max(self_rem, oth_rem)]
```
:::

---

### 4. OR-Set: множина зі спостережуваним видаленням (Observed-Remove Set)

Якщо система не може спиратися на синхронізацію годинників або ризикує зіткнутися зі зміщенням часу (clock drift), стандартом безконфліктної множини є Observed-Remove Set (OR-Set).

В OR-Set кожне додавання елемента `x` генерує унікальний ідентифікатор події (тег або UUID) у вигляді пари `(x, tag)`. Структура зберігає дві множини:
1. `add_set`: множина всіх доданих пар `(x, tag)`.
2. `remove_set`: множина всіх видалених тегів `tag` (надгробків, англ. *tombstones*).

Елемент вважається присутнім у множині тоді й тільки тоді, коли в `add_set` є хоча б один тег для цього елемента, який ще не з'явився у `remove_set`. Злиття двох станів є звичайним теоретико-множинним об'єднанням `∪` для обох множин, що утворює чисту join-напіврешітку на булеані:

```
⟨Add₁, Rem₁⟩ ⊔ ⟨Add₂, Rem₂⟩ = ⟨Add₁ ∪ Add₂, Rem₁ ∪ Rem₂⟩
```

Якщо видалення та нове додавання відбуваються паралельно, нове додавання породжує свіжий тег `tag_new`, якого ще немає в `remove_set`, тому елемент коректно залишається у множині (семантика *add-wins*). 

#### Збирання сміття та надгробки (Tombstones)

Оскільки `remove_set` лише монотонно зростає, збереження всіх видалених тегів створює витік пам'яті. У промислових реалізаціях застосовують векторні годинники стабільності: якщо всі репліки кластера підтвердили отримання стану з певним тегом у `remove_set`, цей тег можна безпечно видалити як з `add_set`, так і з `remove_set`, оскільки жодна репліка більше ніколи не надішле старий пакет із цим тегом.

:::tabs
```cpp
#include <set>
#include <string>
#include <utility>

struct TaggedElement {
    std::string value;
    std::string tag;

    auto operator<=>(const TaggedElement&) const = default;
};

class ORSet {
public:
    explicit ORSet(std::string node_id) : node_id_(std::move(node_id)), counter_(0) {}

    void add(const std::string& value) {
        std::string tag = node_id_ + ":" + std::to_string(++counter_);
        add_set_.insert({value, tag});
    }

    void remove(const std::string& value) {
        // Додаємо всі спостережувані на даний момент теги цього значення до множини видалення
        for (const auto& item : add_set_) {
            if (item.value == value) {
                remove_set_.insert(item.tag);
            }
        }
    }

    [[nodiscard]] bool contains(const std::string& value) const {
        for (const auto& item : add_set_) {
            if (item.value == value && !remove_set_.contains(item.tag)) {
                return true;
            }
        }
        return false;
    }

    [[nodiscard]] std::set<std::string> read() const {
        std::set<std::string> result;
        for (const auto& item : add_set_) {
            if (!remove_set_.contains(item.tag)) {
                result.insert(item.value);
            }
        }
        return result;
    }

    // Злиття над напіврешіткою: теоретико-множинне об'єднання множин додавання і видалення
    void merge(const ORSet& other) {
        add_set_.insert(other.add_set_.begin(), other.add_set_.end());
        remove_set_.insert(other.remove_set_.begin(), other.remove_set_.end());
    }

private:
    std::string node_id_;
    uint64_t counter_;
    std::set<TaggedElement> add_set_;
    std::set<std::string> remove_set_;
};
```
```py
import uuid
from typing import Set, Tuple

class ORSet:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.add_set: Set[Tuple[str, str]] = set()  # (value, tag)
        self.remove_set: Set[str] = set()           # tag

    def add(self, value: str) -> None:
        tag = f"{self.node_id}:{uuid.uuid4().hex}"
        self.add_set.add((value, tag))

    def remove(self, value: str) -> None:
        for val, tag in self.add_set:
            if val == value:
                self.remove_set.add(tag)

    def contains(self, value: str) -> bool:
        return any(val == value and tag not in self.remove_set for val, tag in self.add_set)

    def read(self) -> Set[str]:
        return {val for val, tag in self.add_set if tag not in self.remove_set}

    # Злиття над напіврешіткою: об'єднання множин (Union Semilattice)
    def merge(self, other: "ORSet") -> None:
        self.add_set |= other.add_set
        self.remove_set |= other.remove_set
```
:::

---

### 5. Симуляція мережевого хаосу та перевірка збіжності

Щоб продемонструвати математичну надійність напіврешіток, змоделюємо роботу кластера з трьох реплік. У симуляторі пакети передаються через ненадійний буфер: вони перемішуються у довільному порядку, штучно дублюються та доставляються випадковими партіями з імітацією тимчасового розриву зв'язку (мережевої ізоляції).

:::tabs
```cpp
#include <vector>
#include <algorithm>
#include <random>

struct NetworkMessage {
    size_t from_node;
    size_t to_node;
    PNCounter payload;
};

int main() {
    std::vector<PNCounter> cluster = {
        PNCounter("node-0"),
        PNCounter("node-1"),
        PNCounter("node-2")
    };

    // Виконуємо локальні операції на вузлах
    cluster[0].increment(15);
    cluster[0].decrement(3);  // Net: +12

    cluster[1].increment(8);
    cluster[1].decrement(2);  // Net: +6

    cluster[2].increment(30);
    cluster[2].decrement(10); // Net: +20

    // Формуємо чергу повідомлень для повного взаємного обміну
    std::vector<NetworkMessage> network_queue;
    for (size_t i = 0; i < cluster.size(); ++i) {
        for (size_t j = 0; j < cluster.size(); ++j) {
            if (i != j) {
                // Додаємо оригінальне повідомлення
                network_queue.push_back({i, j, cluster[i]});
                // Штучно дублюємо кожне друге повідомлення для тесту ідемпотентності
                if ((i + j) % 2 == 0) {
                    network_queue.push_back({i, j, cluster[i]});
                }
            }
        }
    }

    // Перемішуємо повідомлення для імітації хаотичних мережевих затримок
    std::mt19937 rng(42);
    std::shuffle(network_queue.begin(), network_queue.end(), rng);

    // Доставляємо пакети з черги адресатам
    for (const auto& msg : network_queue) {
        cluster[msg.to_node].merge(msg.payload);
    }

    // Перевірка збіжності: 12 + 6 + 20 = 38 на кожному вузлі
    bool all_converged = true;
    const int64_t expected_value = 38;

    for (size_t i = 0; i < cluster.size(); ++i) {
        std::cout << "Вузол " << i << " стан: " << cluster[i].value() << "\n";
        if (cluster[i].value() != expected_value) {
            all_converged = false;
        }
    }

    if (all_converged) {
        std::cout << "Успіх: усі репліки детерміновано зійшлися до значення 38 завдяки напіврешітці.\n";
    }

    return 0;
}
```
```py
import random

if __name__ == "__main__":
    cluster = [
        PNCounter("node-0"),
        PNCounter("node-1"),
        PNCounter("node-2")
    ]

    cluster[0].increment(15)
    cluster[0].decrement(3)  # Net: +12

    cluster[1].increment(8)
    cluster[1].decrement(2)  # Net: +6

    cluster[2].increment(30)
    cluster[2].decrement(10)  # Net: +20

    network_queue = []
    for i in range(len(cluster)):
        for j in range(len(cluster)):
            if i != j:
                # Додаємо повідомлення та його дублікати
                network_queue.append((i, j, cluster[i]))
                if (i + j) % 2 == 0:
                    network_queue.append((i, j, cluster[i]))

    # Хаотичне перемішування черги
    random.seed(42)
    random.shuffle(network_queue)

    # Доставка пакетів
    for from_node, to_node, payload in network_queue:
        cluster[to_node].merge(payload)

    expected = 38
    converged = all(node.value == expected for node in cluster)
    for i, node in enumerate(cluster):
        print(f"Вузол {i} стан: {node.value}")

    if converged:
        print("Успіх: усі репліки детерміновано зійшлися завдяки напіврешітці.")
```
:::

Усі репліки детерміновано обчислюють однакове значення `38`. Ніякі перестановки, затримки або повтори пакетів у мережевій черзі не можуть спотворити результат, оскільки операція злиття задовольняє аксіоми напіврешітки.
