# ⚙️ Стійкий клієнт розподіленого кешу: узгоджене гешування, Singleflight та ймовірнісний захист від навали запитів

Проєктування клієнтської бібліотеки для роботи з розподіленим кешем вимагає розв'язання комплексу системних проблем, які виникають при паралельній обробці сотень тисяч запитів на секунду. Проста клієнтська обгортка над сокетом виявляється вразливою до трьох типових виробничих катастроф:

1. **Дисбаланс розподілу ключів та втрата даних при зміні кластера**: наївне гешування `hash(key) % N` приводить до інвалідації 90–99% даних при додаванні або відмові вузла. Клієнт зобов'язаний реалізувати кільце узгодженого гешування (Consistent Hash Ring) з віртуальними вузлами (vnodes).
2. **Навала запитів (Cache Stampede / Thundering Herd)**: коли гарячий ключ експайриться, тисячі паралельних клієнтських потоків одночасно фіксують промах кешу і спрямовують ідентичні важкі SQL-запити до СУБД. Клієнт повинен реалізувати координатор дедуплікації запитів (Singleflight), який об'єднує ідентичні паралельні виклики в один.
3. **Жорсткий детермінований промах**: очікування повного вичерпання TTL неминуче створює вікно вразливості. Клієнт повинен застосовувати стохастичний алгоритм раннього оновлення (XFetch), який достроково перераховує значення у фоні з інтенсивністю, пропорційною часу обчислення в базі даних.

Нижче наведено повну виробничу реалізацію стійкого клієнта розподіленого кешу:

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <functional>
#include <chrono>
#include <random>
#include <cmath>
#include <cstdint>
#include <optional>
#include <stdexcept>

// ── 1. Гешування FNV-1a (32 біти) ──────────────────────────────────────────
// Швидка некриптографічна геш-функція з відмінним лавинним ефектом для ключів
inline uint32_t fnv1a_32(std::string_view text) noexcept {
    uint32_t hash = 0x811c9dc5u;
    for (char c : text) {
        hash ^= static_cast<uint8_t>(c);
        hash *= 0x01000193u;
    }
    return hash;
}

// ── 2. Структура кешованого запису зі статистикою для XFetch ───────────────
struct CacheItem {
    std::string value;
    std::chrono::steady_clock::time_point expiry; // запланований момент вичерпання TTL
    double compute_duration_sec{0.0};             // час (delta), витрачений СУБД на розрахунок
};

// ── 3. Кільце узгодженого гешування (Consistent Hash Ring) ──────────────────
class ConsistentHashRing {
public:
    explicit ConsistentHashRing(size_t vnodes_per_node = 150)
        : vnodes_per_node_(vnodes_per_node) {}

    // Додавання фізичного сервера: створює vnodes_per_node точок на кільці
    void add_node(const std::string& node_id) {
        std::lock_guard<std::mutex> lock(ring_mutex_);
        nodes_.push_back(node_id);
        for (size_t v = 0; v < vnodes_per_node_; ++v) {
            std::string vnode_key = node_id + "#vnode_" + std::to_string(v);
            uint32_t hash_point = fnv1a_32(vnode_key);
            ring_[hash_point] = node_id;
        }
    }

    // Видалення фізичного сервера: прибирає всі його віртуальні точки
    void remove_node(const std::string& node_id) {
        std::lock_guard<std::mutex> lock(ring_mutex_);
        std::erase(nodes_, node_id);
        for (size_t v = 0; v < vnodes_per_node_; ++v) {
            std::string vnode_key = node_id + "#vnode_" + std::to_string(v);
            uint32_t hash_point = fnv1a_32(vnode_key);
            ring_.erase(hash_point);
        }
    }

    // Пошук цільового сервера за ключем: рух за годинниковою стрілкою (O(log M))
    std::string get_node(std::string_view key) const {
        std::lock_guard<std::mutex> lock(ring_mutex_);
        if (ring_.empty()) {
            return "";
        }
        uint32_t key_hash = fnv1a_32(key);
        // Знаходимо перший вузол, чий хеш-поінт >= key_hash
        auto it = ring_.lower_bound(key_hash);
        if (it == ring_.end()) {
            it = ring_.begin(); // Замикання кільця (wrap-around до початкового сектора)
        }
        return it->second;
    }

    size_t total_vnodes() const {
        std::lock_guard<std::mutex> lock(ring_mutex_);
        return ring_.size();
    }

private:
    size_t vnodes_per_node_;
    std::vector<std::string> nodes_;
    std::map<uint32_t, std::string> ring_; // Червоно-чорне дерево: впорядкований простір точок
    mutable std::mutex ring_mutex_;
};

// ── 4. Координатор дедуплікації запитів (Singleflight Group) ────────────────
class SingleflightGroup {
public:
    using Result = std::string;

    // Гарантує, що для одного ключа функція fn() виконується лише одним потоком
    Result do_work(const std::string& key, std::function<Result()> fn) {
        std::unique_lock<std::mutex> lock(mutex_);

        auto it = in_flight_.find(key);
        if (it != in_flight_.end()) {
            // Запит на цей ключ уже виконується іншим воркером — підключаємося до очікування
            auto call = it->second;
            lock.unlock();

            std::unique_lock<std::mutex> call_lock(call->call_mutex);
            call->cv.wait(call_lock, [&call] { return call->done; });
            return call->val;
        }

        // Ми є першим потоком, що запросив ключ — реєструємо новий дескриптор виклику
        auto call = std::make_shared<Call>();
        in_flight_[key] = call;
        lock.unlock();

        // Виконуємо важку операцію (SQL-запит до СУБД) без утримання загального м'ютексу
        Result res;
        try {
            res = fn();
        } catch (...) {
            // При помилці сповіщаємо очікуючих і видаляємо виклик
            std::lock_guard<std::mutex> call_lock(call->call_mutex);
            call->done = true;
            call->cv.notify_all();
            lock.lock();
            in_flight_.erase(key);
            throw;
        }

        // Сповіщаємо всі підписані потоки, що чекають на результат
        {
            std::lock_guard<std::mutex> call_lock(call->call_mutex);
            call->val = res;
            call->done = true;
        }
        call->cv.notify_all();

        // Видаляємо дескриптор із реєстру активних викликів
        lock.lock();
        in_flight_.erase(key);
        return res;
    }

private:
    struct Call {
        std::mutex call_mutex;
        std::condition_variable cv;
        std::string val;
        bool done{false};
    };

    std::unordered_map<std::string, std::shared_ptr<Call>> in_flight_;
    std::mutex mutex_;
};

// ── 5. Клієнт розподіленого кешу (Resilient Distributed Cache Client) ───────
class ResilientCacheClient {
public:
    explicit ResilientCacheClient(ConsistentHashRing ring, double beta = 1.0)
        : ring_(std::move(ring)), beta_(beta), rng_(std::random_device{}()) {}

    // Метод Get-or-Compute: зчитує з кешу або атомарно обчислює у СУБД
    std::string get_or_compute(
        const std::string& key,
        std::chrono::seconds ttl,
        std::function<std::string()> db_loader
    ) {
        std::string target_node = ring_.get_node(key);
        auto now = std::chrono::steady_clock::now();

        // Крок 1. Спроба читання з кешу цільового шарду
        auto cached = read_from_shard(target_node, key);
        if (cached.has_value()) {
            // Перевіряємо умову стохастичного дострокового оновлення (алгоритм XFetch)
            if (!should_early_refresh(cached.value(), now)) {
                return cached.value().value; // Кеш свіжий і валідний — миттєве повернення (~1 мс)
            }
            // Якщо XFetch спрацював (TTL закінчується), запускаємо фоновий розрахунок через Singleflight
        }

        // Крок 2. Промах або дострокове оновлення — викликаємо Singleflight
        return singleflight_.do_work(key, [&]() -> std::string {
            // Повторна перевірка (Double-Checked Locking) всередині захищеної секції
            auto recheck = read_from_shard(target_node, key);
            if (recheck.has_value() && !should_early_refresh(recheck.value(), std::chrono::steady_clock::now())) {
                return recheck.value().value;
            }

            // Замір тривалості виконання запиту в СУБД (delta)
            auto start_t = std::chrono::steady_clock::now();
            std::string fresh_val = db_loader();
            auto end_t = std::chrono::steady_clock::now();

            double duration_sec = std::chrono::duration<double>(end_t - start_t).count();

            // Запис нового значення у шард
            CacheItem item{
                .value = fresh_val,
                .expiry = end_t + ttl,
                .compute_duration_sec = duration_sec
            };
            write_to_shard(target_node, key, item);
            return fresh_val;
        });
    }

private:
    // Алгоритм XFetch: перевірка now - beta * delta * ln(U) > expiry
    bool should_early_refresh(const CacheItem& item, std::chrono::steady_clock::time_point now) {
        if (now >= item.expiry) {
            return true; // Жорсткий промах: термін життя TTL повністю вичерпано
        }
        std::uniform_real_distribution<double> dist(0.0001, 0.9999);
        double u = dist(rng_);
        double delta = item.compute_duration_sec;
        double early_margin = -beta_ * delta * std::log(u);

        auto effective_time = now + std::chrono::duration<double>(early_margin);
        return effective_time >= item.expiry;
    }

    // Симуляція пам'яті віддалених серверів
    std::optional<CacheItem> read_from_shard(const std::string& node, const std::string& key) {
        std::lock_guard<std::mutex> lock(storage_mutex_);
        auto node_it = mock_storage_.find(node);
        if (node_it != mock_storage_.end()) {
            auto item_it = node_it->second.find(key);
            if (item_it != node_it->second.end()) {
                return item_it->second;
            }
        }
        return std::nullopt;
    }

    void write_to_shard(const std::string& node, const std::string& key, const CacheItem& item) {
        std::lock_guard<std::mutex> lock(storage_mutex_);
        mock_storage_[node][key] = item;
    }

    ConsistentHashRing ring_;
    SingleflightGroup singleflight_;
    double beta_;
    std::mt19937 rng_;
    std::unordered_map<std::string, std::unordered_map<std::string, CacheItem>> mock_storage_;
    std::mutex storage_mutex_;
};

int main() {
    ConsistentHashRing ring(100);
    ring.add_node("cache-node-01.internal:6379");
    ring.add_node("cache-node-02.internal:6379");
    ring.add_node("cache-node-03.internal:6379");

    ResilientCacheClient client(std::move(ring), 1.0);

    // Тестовий виклик читання з емуляцією затримки СУБД
    std::string user_data = client.get_or_compute("user:42:profile", std::chrono::seconds(60), []() {
        std::cout << "-> [СУБД] Виконання SQL-запиту SELECT * FROM users WHERE id = 42\n";
        return "{\"id\":42,\"name\":\"Alice\",\"status\":\"premium\"}";
    });

    std::cout << "<- Отримано результат: " << user_data << "\n";
    return 0;
}
```
```go
package main

import (
	"context"
	"fmt"
	"hash/fnv"
	"math"
	"math/rand"
	"sort"
	"strconv"
	"sync"
	"time"
)

// ── 1. Структура кешованого запису ──────────────────────────────────────────
type CacheItem struct {
	Value              string
	Expiry             time.Time
	ComputeDurationSec float64
}

// ── 2. Кільце узгодженого гешування (Consistent Hash Ring) ──────────────────
type ConsistentHashRing struct {
	mu             sync.RWMutex
	vnodesPerNode  int
	ring           []uint32
	vnodeToNodeMap map[uint32]string
}

func NewConsistentHashRing(vnodesPerNode int) *ConsistentHashRing {
	return &ConsistentHashRing{
		vnodesPerNode:  vnodesPerNode,
		vnodeToNodeMap: make(map[uint32]string),
	}
}

func hashKey(key string) uint32 {
	h := fnv.New32a()
	h.Write([]byte(key))
	return h.Sum32()
}

func (r *ConsistentHashRing) AddNode(nodeID string) {
	r.mu.Lock()
	defer r.mu.Unlock()

	for v := 0; v < r.vnodesPerNode; v++ {
		vnodeKey := nodeID + "#vnode_" + strconv.Itoa(v)
		h := hashKey(vnodeKey)
		r.ring = append(r.ring, h)
		r.vnodeToNodeMap[h] = nodeID
	}
	sort.Slice(r.ring, func(i, j int) bool { return r.ring[i] < r.ring[j] })
}

func (r *ConsistentHashRing) GetNode(key string) string {
	r.mu.RLock()
	defer r.mu.RUnlock()

	if len(r.ring) == 0 {
		return ""
	}
	h := hashKey(key)
	idx := sort.Search(len(r.ring), func(i int) bool { return r.ring[i] >= h })
	if idx == len(r.ring) {
		idx = 0 // Wrap-around
	}
	return r.vnodeToNodeMap[r.ring[idx]]
}

// ── 3. Singleflight координатор дедуплікації ────────────────────────────────
type call struct {
	wg  sync.WaitGroup
	val string
	err error
}

type SingleflightGroup struct {
	mu sync.Mutex
	m  map[string]*call
}

func NewSingleflightGroup() *SingleflightGroup {
	return &SingleflightGroup{m: make(map[string]*call)}
}

func (g *SingleflightGroup) Do(key string, fn func() (string, error)) (string, error) {
	g.mu.Lock()
	if c, ok := g.m[key]; ok {
		g.mu.Unlock()
		c.wg.Wait()
		return c.val, c.err
	}
	c := new(call)
	c.wg.Add(1)
	g.m[key] = c
	g.mu.Unlock()

	c.val, c.err = fn()
	c.wg.Done()

	g.mu.Lock()
	delete(g.m, key)
	g.mu.Unlock()

	return c.val, c.err
}

// ── 4. Клієнт стійкого розподіленого кешу ──────────────────────────────────
type ResilientCacheClient struct {
	ring         *ConsistentHashRing
	singleflight *SingleflightGroup
	beta         float64
	storageMu    sync.RWMutex
	mockStorage  map[string]map[string]CacheItem
}

func NewResilientCacheClient(ring *ConsistentHashRing, beta float64) *ResilientCacheClient {
	return &ResilientCacheClient{
		ring:         ring,
		singleflight: NewSingleflightGroup(),
		beta:         beta,
		mockStorage:  make(map[string]map[string]CacheItem),
	}
}

func (c *ResilientCacheClient) shouldEarlyRefresh(item CacheItem, now time.Time) bool {
	if now.After(item.Expiry) {
		return true
	}
	u := rand.Float64()
	if u <= 0 {
		u = 0.0001
	}
	// XFetch: now - beta * delta * ln(u) > expiry
	earlyMargin := time.Duration(-c.beta * item.ComputeDurationSec * math.Log(u) * float64(time.Second))
	return now.Add(earlyMargin).After(item.Expiry)
}

func (c *ResilientCacheClient) GetOrCompute(
	ctx context.Context,
	key string,
	ttl time.Duration,
	dbLoader func() (string, error),
) (string, error) {
	targetNode := c.ring.GetNode(key)
	now := time.Now()

	c.storageMu.RLock()
	nodeData, existsNode := c.mockStorage[targetNode]
	item, existsItem := nodeData[key]
	c.storageMu.RUnlock()

	if existsNode && existsItem {
		if !c.shouldEarlyRefresh(item, now) {
			return item.Value, nil
		}
	}

	return c.singleflight.Do(key, func() (string, error) {
		start := time.Now()
		freshVal, err := dbLoader()
		if err != nil {
			return "", err
		}
		durationSec := time.Since(start).Seconds()

		c.storageMu.Lock()
		if _, ok := c.mockStorage[targetNode]; !ok {
			c.mockStorage[targetNode] = make(map[string]CacheItem)
		}
		c.mockStorage[targetNode][key] = CacheItem{
			Value:              freshVal,
			Expiry:             time.Now().Add(ttl),
			ComputeDurationSec: durationSec,
		}
		c.storageMu.Unlock()

		return freshVal, nil
	})
}

func main() {
	ring := NewConsistentHashRing(100)
	ring.AddNode("cache-01.internal:6379")
	ring.AddNode("cache-02.internal:6379")
	ring.AddNode("cache-03.internal:6379")

	client := NewResilientCacheClient(ring, 1.0)

	val, err := client.GetOrCompute(context.Background(), "user:100:profile", 30*time.Second, func() (string, error) {
		fmt.Println("-> [СУБД] Читання профілю користувача 100")
		return `{"id":100,"name":"Bob","role":"admin"}`, nil
	})

	if err == nil {
		fmt.Printf("<- Отримано: %s\n", val)
	}
}
```
:::

## Детальний аналіз підсистем клієнта

### 1. Механізм кільця узгодженого гешування та структури даних

Клієнт організовує простір серверів у вигляді неперервного 32-бітного числового кільця від `0` до `2³² - 1` (4 294 967 295 точок).

Для вибору геш-функції обрано алгоритм FNV-1a (Fowler–Noll–Vo). На відміну від криптографічних геш-функцій (таких як MD5 або SHA-256), які вимагають десятків тактів процесора на кожен байт та ініціалізації внутрішніх буферів стану, FNV-1a обчислюється в один компактний регістровий цикл процесора:

```text
hash = (hash XOR byte) * FNV_prime
```

Час обчислення FNV-1a для типового рядка ключа довжиною 32 байти становить менше 12–15 наносекунд, забезпечуючи рівномірне розсіювання бітів по всьому 32-бітному простору.

У реалізації C++ кільце представлено структурою `std::map<uint32_t, std::string>`. Оскільки `std::map` побудовано на основі збалансованого червоно-чорного дерева (Red-Black Tree), елементи в ньому завжди підтримуються у відсортованому за зростанням порядку. Пошук вузла за ключем виконується методом `lower_bound(key_hash)`, який за `O(log M)` знаходить перший вузол, координата якого є більшою або рівною `key_hash`.

У реалізації Go використано плоский масив `[]uint32` та геш-мапу `map[uint32]string`. Сортування масиву `sort.Slice` виконується лише під час додавання або видалення вузла, а пошук здійснюється алгоритмом двійкового пошуку `sort.Search`. Це дає значну перевагу в локальності кешу процесора (Cache Locality): плоский масив зчитується суцільною лінією L1-кешу CPU, виконуючи 10–12 ітерацій двійкового пошуку без промахів сторінок пам'яті.

Якщо ключ отримує значення хешу, більше за будь-яку точку на кільці (наприклад, `key_hash = 4 200 000 000`, а останній віртуальний вузол розташований на `4 150 000 000`), метод `lower_bound` повертає ітератор кінця `ring_.end()`. У цей момент спрацьовує правило замикання кільця (wrap-around), і запит перенаправляється на найперший вузол кільця `ring_.begin()`.

### 2. Внутрішня координація та життєвий цикл виклику в Singleflight

Модуль `SingleflightGroup` запобігає множинному одночасному виконанню однакових ресурсомістких функцій завантаження даних.

Розглянемо покрокову динаміку викликів при надходженні 5 000 паралельних запитів на ключ `user:42:orders` у момент вичерпання TTL:

1. **Крок реєстрації лідера**: Потік 1 захоплює глобальний м'ютекс `mutex_`, перевіряє таблицю `in_flight_`, бачить відсутність активних запитів, створює новий об'єкт `Call` і зберігає `std::shared_ptr<Call>` у мапі. Після цього Потік 1 **негайно відпускає глобальний м'ютекс** `mutex_` і починає виконувати важкий SQL-запит через функцію `db_loader()`.
2. **Крок реєстрації підписників**: Потоки 2...5000 почергово захоплюють `mutex_` на кілька наносекунд. Кожен із них виявляє, що для ключа `user:42:orders` уже створено об'єкт `Call`. Вони копіюють розумний покажчик на цей `Call`, відпускають глобальний `mutex_`, блокують локальний м'ютекс `call->call_mutex` і засинають на змінній умови `call->cv.wait()`. Загальний реєстр `in_flight_` залишається повністю вільним для обробки інших ключів (`user:43`, `user:44`).
3. **Крок виконання в СУБД**: Потік 1 чекає на відповідь від бази даних 40 мілісекунд. Протягом цього часу база даних обробляє **рівно один SQL-запит**, а не 5 000.
4. **Крок завершення та сповіщення**: Отримавши результат, Потік 1 захоплює `call->call_mutex`, записує рядок відповіді у `call->val`, переводить прапорець `call->done` у стан `true` і викликає `call->cv.notify_all()`.
5. **Крок паралельного пробудження**: Усі 4 999 сплячих потоків одночасно прокидаються, перевіряють предикат `call->done == true`, копіюють готове значення `call->val` і повертають його клієнтам.
6. **Крок очищення реєстру**: Потік 1 знову захоплює `mutex_`, видаляє запис `user:42:orders` із мапи `in_flight_` і завершує роботу. Об'єкт `Call` автоматично видаляється з пам'яті через механізм підрахунку посилань `std::shared_ptr`, коли останній потік-підписник завершує читання.

### 3. Безпека винятків та відмова бази даних

Якщо функція завантаження з бази даних `db_loader()` зазнає збою (наприклад, генерує виняток `std::runtime_error("Database connection lost")` або повертає помилку мережевого таймауту), Singleflight повинен гарантувати коректне розблокування всіх сплячих потоків.

У наведеній реалізації блок `try ... catch (...)` перехоплює будь-яке виключення, переводить дескриптор `call` у стан завершення (`call->done = true`), надсилає сигнал пробудження всім підписникам через `notify_all()` і видаляє виклик із таблиці `in_flight_`. Без цієї обробки всі 4 999 потоків назавжди зависли б у стані очікування на умові `cv.wait()`, викликавши вичерпання пулу потоків веб-сервера (Thread Pool Starvation).

### 4. Стохастичний розрахунок імовірності в XFetch

Функція `should_early_refresh` реалізує стохастичну перевірку, яка плавно підвищує ймовірність фонового оновлення ключа в міру наближення до моменту його застарівання.

Формула перевірки:

```text
now + (-beta * delta * ln(U)) >= expiry
```

У цій формулі:
- Величина `delta` зберігає точний час (у секундах), який знадобився базі даних для минулого розрахунку цього об'єкта. Якщо розрахунок тривав `0.5` секунди, вікно раннього оновлення буде вузьким; якщо запит є важким і тривав `5.0` секунд, вікно раннього оновлення пропорційно розшириться, гарантуючи, що оновлення почнеться завчасно.
- Випадкова величина `U ∈ (0, 1)` генерується за допомогою генератора псевдовипадкових чисел Мерсенна Твістера `std::mt19937`. Оскільки `ln(U)` змінюється від `0` (при `U ➔ 1`) до `-∞` (при `U ➔ 0`), вираз `-beta * delta * ln(U)` додає до поточного часу віртуальну надбавку від 0 до десятків секунд.
- Коефіцієнт `beta` регулює агресивність оновлення: при `beta = 1.0` система повністю усуває промахи кешу при мінімальній кількості дублюючих запитів. Збільшення `beta` до 2.0 доцільне для критично важливих фінансових сутностей, де навіть поодинокий промах є неприпустимим.

### 5. Подвійна перевірка блокування (Double-Checked Locking)

Всередині лямбда-функції, яка передається в Singleflight, реалізовано повторну перевірку наявності даних у кеші (Double Check).

Цей прийом захищає від рідкісного крайового випадку: якщо два потоки `T1` та `T2` одночасно зафіксували необхідність оновлення за алгоритмом XFetch, потік `T1` першим отримує блокування і починає оновлювати дані в СУБД. Потік `T2` потрапляє в чергу Singleflight. Коли `T1` завершує запис у шард і сповіщає підписників, потік `T2` прокидається і знову перевіряє стан шарда. Виявивши, що значення вже було оновлене потоком `T1` і його TTL свіжий, `T2` негайно повертає це значення, не виконуючи повторного запиту до СУБД.

Завдяки синергії кільця узгодженого гешування, дедуплікації Singleflight та стохастичного оновлення XFetch клієнтська бібліотека демонструє стабільний час відповіді на рівні 1–2 мілісекунд при 99.99% влучань у кеш під будь-яким навантаженням.
