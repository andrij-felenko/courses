# ⚙️ Реалізація розподіленого маршрутизатора запитів (Shard Router) з консистентним хешуванням та scatter-gather

Маршрутизатор шардингу (Shard Router) є критичним компонентом високонавантаженої платформи даних. Він відповідає за прозору трансляцію користувацьких SQL- та NoSQL-запитів до фізичних вузлів зберігання. Коректно спроєктований роутер повинен розв'язувати три ключові інженерні задачі:
1. **Точкове маршрутизування за ключем (Point Routing):** детерміноване відображення ключа шардингу на цільовий сервер за допомогою кільця консистентного хешування з віртуальними вузлами (Virtual Nodes);
2. **Паралельне опитування (Scatter-Gather Engine):** одночасне виконання запитів без ключа на всіх активних шардах із жорстким контролем таймаутів, агрегацією відповідей та сортуванням результатів;
3. **Атомне оновлення топології (Zero-Downtime Topology Updates):** потокобезпечне оновлення конфігурації кластера без зупинки обробки запитів на базі механізму Read-Copy-Update (RCU) або читацько-письменницьких блокувань.

## Архітектурний дизайн та структури даних

У наведеній реалізації маршрутизатор складається з трьох ключових модулів:
- `ConsistentHashRing`: структура даних, яка зберігає відсортований масив токенів віртуальних вузлів `(Token → ShardID)` і знаходить цільовий шард за бінарним пошуком `O(log(S · V))`;
- `ShardClient`: абстракція підключення до фізичного вузла з можливістю емуляції мережевої затримки, випадкових збоїв та таймаутів;
- `ShardRouter`: фасадний координатор, який утримує атомарний покажчик на поточну топологію, направляє точкові операції та керує пулом потоків для віялових запитів.

### 1. Алгоритм консистентного хешування та роль віртуальних вузлів
Кільце консистентного хешування відображає як фізичні сервери, так і прикладні ключі на єдиний 64-бітний простір цілих чисел `[0 .. 2⁶⁴ - 1]`. Для усунення дисперсії довжин сегментів між фізичними серверами кожен фізичний шард розмножується на `V = 128` віртуальних точок із синтетичними іменами виду `shard_id#vnode_i`. 

Хешування імені віртуального вузла алгоритмом FNV-1a генерує 64-бітний токен, який вставляється у відсортоване дерево або масив токенів. Коли надходить клієнтський ключ (наприклад, `user_10842`), роутер обчислює його хеш і за допомогою функції `lower_bound` (бінарний пошук першого елемента, не меншого за токен ключа) знаходить найближчий вузол за годинниковою стрілкою. Якщо токен ключа перевищує найбільший токен у кільці, спрацьовує замикання кільця (Wrap-around) на перший елемент.

### 2. Механізм RCU (Read-Copy-Update) для нульового блокування
Традиційне використання ексклюзивних блокувань (`std::mutex` або `sync.Mutex`) на рівні маршрутизатора для захисту мапи шардів створює важку конкуренцію за блокування між робочими потоками при темпі у сотні тисяч RPS.

Для усунення цього вузького місця застосовано патерн RCU на розумних атомарних покажчиках (`std::atomic_store` / `std::atomic_load` для `std::shared_ptr` у C++ та `atomic.Pointer` у Go). Вся топологія кластера (кільце, мапа клієнтів, номер генерації) інкапсульована в незмінну структуру `ClusterTopology`. Робочі потоки читають поточний покажчик без жодних блокувань. Коли від координатора надходить нова версія конфігурації, роутер створює новий об'єкт топології в пам'яті й атомарно підміняє глобальний покажчик. Стара топологія автоматично звільняється з пам'яті, коли останній активний запит завершує свою роботу.

### 3. Двигун Scatter-Gather: віялове розпаралелювання та бар'єр синхронізації
Коли виконується запит без ключа шардингу (наприклад, повнотекстовий пошук за фільтром), роутер ініціює паралельний Fan-Out. У C++ створюється вектор об'єктів `std::future`, які виконуються асинхронно в пулі потоків через `std::async(std::launch::async)`. У Go запускаються незалежні горутини з використанням `sync.WaitGroup` та каналу з буферизованою чергою відповідей.

Головний потік очікує завершення всіх підзапитів до досягнення жорсткого таймауту. Отримані масиви рядків об'єднуються в єдиний спільний вектор, після чого виконується фінальне сортування за часовою міткою (`ORDER BY timestamp DESC`). Якщо один із шардів не вкладається у виділений таймаут, роутер фіксує помилку таймауту, повертаючи часткові дані або помилку деградації відповідно до налаштувань політики.

## Вихідний код реалізації

Нижче наведено повністю робочі реалізації маршрутизатора на мовах C++ (сучасний стандарт C++20 із застосуванням RAII, багатопотоковості `std::async` та атомарних покажчиків) та Go (з використанням горутин, каналів та контекстів `context.Context`).

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <map>
#include <algorithm>
#include <memory>
#include <shared_mutex>
#include <future>
#include <chrono>
#include <stdexcept>
#include <sstream>
#include <cstdint>

// 64-бітний хеш FNV-1a для детермінованого розсіювання ключів
class HashUtil {
public:
    static uint64_t fnv1a64(std::string_view key) noexcept {
        uint64_t hash = 0xcbf29ce484222325ULL;
        for (char c : key) {
            hash ^= static_cast<uint8_t>(c);
            hash *= 0x100000001b3ULL;
        }
        return hash;
    }
};

// Модель запису бази даних
struct Record {
    std::string key;
    std::string value;
    int64_t timestamp;
};

// Абстракція фізичного шарду
class ShardClient {
public:
    explicit ShardClient(std::string shardId, std::string endpoint)
        : shardId_(std::move(shardId)), endpoint_(std::move(endpoint)) {}

    [[nodiscard]] const std::string& getId() const noexcept { return shardId_; }
    [[nodiscard]] const std::string& getEndpoint() const noexcept { return endpoint_; }

    // Точковий запис
    bool put(const std::string& key, const std::string& value) {
        // Емуляція виконання запиту до вузла
        return !key.empty() && !value.empty();
    }

    // Точкове читання
    [[nodiscard]] std::string get(const std::string& key) const {
        return "val_from_" + shardId_ + "_for_" + key;
    }

    // Сканування даних для Scatter-Gather
    [[nodiscard]] std::vector<Record> scan(std::string_view queryFilter, std::chrono::milliseconds timeout) const {
        // Емуляція тривалості запиту
        std::this_thread::sleep_for(std::chrono::milliseconds(10));
        
        std::vector<Record> results;
        results.push_back({ "k1_" + shardId_, "payload_match", 100 + static_cast<int64_t>(shardId_.size()) });
        results.push_back({ "k2_" + shardId_, "payload_match", 200 + static_cast<int64_t>(shardId_.size()) });
        return results;
    }

private:
    std::string shardId_;
    std::string endpoint_;
};

// Кільце консистентного хешування
class ConsistentHashRing {
public:
    explicit ConsistentHashRing(size_t virtualNodesPerShard = 128)
        : virtualNodes_(virtualNodesPerShard) {}

    void addShard(const std::string& shardId) {
        for (size_t i = 0; i < virtualNodes_; ++i) {
            std::string vnodeKey = shardId + "#vnode_" + std::to_string(i);
            uint64_t token = HashUtil::fnv1a64(vnodeKey);
            ring_[token] = shardId;
        }
    }

    void removeShard(const std::string& shardId) {
        for (auto it = ring_.begin(); it != ring_.end(); ) {
            if (it->second == shardId) {
                it = ring_.erase(it);
            } else {
                ++it;
            }
        }
    }

    [[nodiscard]] std::string getShard(std::string_view key) const {
        if (ring_.empty()) {
            throw std::runtime_error("Consistent hash ring is empty: no shards available");
        }
        uint64_t token = HashUtil::fnv1a64(key);
        // Пошук першого вузла, токен якого >= токену ключа
        auto it = ring_.lower_bound(token);
        if (it == ring_.end()) {
            // Замикання кільця (Wrap-around)
            it = ring_.begin();
        }
        return it->second;
    }

private:
    size_t virtualNodes_;
    std::map<uint64_t, std::string> ring_;
};

// Топологія кластера (незмінна структура під захистом Shared Pointer)
struct ClusterTopology {
    uint64_t version{ 0 };
    std::shared_ptr<ConsistentHashRing> ring;
    std::map<std::string, std::shared_ptr<ShardClient>> shards;
};

// Розподілений маршрутизатор
class ShardRouter {
public:
    ShardRouter() {
        auto initialTopology = std::make_shared<ClusterTopology>();
        initialTopology->version = 1;
        initialTopology->ring = std::make_shared<ConsistentHashRing>(128);
        std::atomic_store(&currentTopology_, initialTopology);
    }

    // Атомне оновлення конфігурації
    void updateTopology(const std::vector<std::pair<std::string, std::string>>& shardList) {
        auto nextTopology = std::make_shared<ClusterTopology>();
        nextTopology->ring = std::make_shared<ConsistentHashRing>(128);

        for (const auto& [shardId, endpoint] : shardList) {
            nextTopology->shards[shardId] = std::make_shared<ShardClient>(shardId, endpoint);
            nextTopology->ring->addShard(shardId);
        }

        auto oldTopology = std::atomic_load(&currentTopology_);
        nextTopology->version = oldTopology ? oldTopology->version + 1 : 1;

        // Атомарна підміна покажчика топології (RCU патерн)
        std::atomic_store(&currentTopology_, nextTopology);
        std::cout << "[Router] Topology updated to version " << nextTopology->version 
                  << " with " << shardList.size() << " shards.\n";
    }

    // Точковий запис
    bool put(const std::string& key, const std::string& value) {
        auto topology = std::atomic_load(&currentTopology_);
        std::string targetShardId = topology->ring->getShard(key);
        
        auto it = topology->shards.find(targetShardId);
        if (it == topology->shards.end()) {
            throw std::runtime_error("Target shard not found in active topology: " + targetShardId);
        }
        return it->second->put(key, value);
    }

    // Точкове читання
    std::string get(const std::string& key) {
        auto topology = std::atomic_load(&currentTopology_);
        std::string targetShardId = topology->ring->getShard(key);

        auto it = topology->shards.find(targetShardId);
        if (it == topology->shards.end()) {
            throw std::runtime_error("Target shard not found in active topology: " + targetShardId);
        }
        return it->second->get(key);
    }

    // Паралельний Scatter-Gather запит
    std::vector<Record> scatterGatherScan(std::string_view queryFilter, std::chrono::milliseconds timeout) {
        auto topology = std::atomic_load(&currentTopology_);
        const auto& shards = topology->shards;

        if (shards.empty()) return {};

        // Запуск паралельних асинхронних завдань
        std::vector<std::future<std::vector<Record>>> futures;
        futures.reserve(shards.size());

        for (const auto& [id, client] : shards) {
            futures.push_back(std::async(std::launch::async, [client, queryFilter, timeout]() {
                return client->scan(queryFilter, timeout);
            }));
        }

        std::vector<Record> aggregatedResults;

        // Збір результатів із бар'єром синхронізації
        for (auto& fut : futures) {
            auto status = fut.wait_for(timeout);
            if (status == std::future_status::ready) {
                auto shardRows = fut.get();
                aggregatedResults.insert(aggregatedResults.end(), shardRows.begin(), shardRows.end());
            } else {
                std::cerr << "[Router] Warning: Shard query timed out during Scatter-Gather.\n";
            }
        }

        // Локальне сортування об'єднаного результату
        std::sort(aggregatedResults.begin(), aggregatedResults.end(), [](const Record& a, const Record& b) {
            return a.timestamp > b.timestamp; // Свіжі записи першими
        });

        return aggregatedResults;
    }

private:
    std::shared_ptr<ClusterTopology> currentTopology_;
};

int main() {
    ShardRouter router;

    // Ініціалізація кластера з трьох шардів
    router.updateTopology({
        { "shard-0", "10.0.1.10:3306" },
        { "shard-1", "10.0.1.11:3306" },
        { "shard-2", "10.0.1.12:3306" }
    });

    // Тест точкових операцій
    router.put("user_10842", "{ name: 'Alice', balance: 540 }");
    router.put("user_99214", "{ name: 'Bob', balance: 1280 }");

    std::cout << "[Client] Read user_10842: " << router.get("user_10842") << "\n";
    std::cout << "[Client] Read user_99214: " << router.get("user_99214") << "\n";

    // Тест Scatter-Gather
    std::cout << "[Client] Executing Scatter-Gather scan...\n";
    auto rows = router.scatterGatherScan("status = 'ACTIVE'", std::chrono::milliseconds(100));
    std::cout << "[Client] Total records returned across cluster: " << rows.size() << "\n";
    for (const auto& row : rows) {
        std::cout << "  - Key: " << row.key << " | TS: " << row.timestamp << "\n";
    }

    return 0;
}
```
```go
package main

import (
	"context"
	"crypto/fnv"
	"errors"
	"fmt"
	"sort"
	"strconv"
	"sync"
	"sync/atomic"
	"time"
)

// Модель запису
type Record struct {
	Key       string
	Value     string
	Timestamp int64
}

// 64-бітний хеш FNV-1a
func fnv1a64(key string) uint64 {
	h := fnv.New64a()
	_, _ = h.Write([]byte(key))
	return h.Sum64()
}

// Фізичний клієнт шарду
type ShardClient struct {
	ShardID  string
	Endpoint string
}

func (c *ShardClient) Put(key, value string) error {
	if key == "" || value == "" {
		return errors.New("invalid key or value")
	}
	return nil
}

func (c *ShardClient) Get(key string) (string, error) {
	return fmt.Sprintf("val_from_%s_for_%s", c.ShardID, key), nil
}

func (c *ShardClient) Scan(ctx context.Context, filter string) ([]Record, error) {
	select {
	case <-time.After(10 * time.Millisecond):
		return []Record{
			{Key: "k1_" + c.ShardID, Value: "payload", Timestamp: 100 + int64(len(c.ShardID))},
			{Key: "k2_" + c.ShardID, Value: "payload", Timestamp: 200 + int64(len(c.ShardID))},
		}, nil
	case <-ctx.Done():
		return nil, ctx.Err()
	}
}

// Кільце консистентного хешування
type ConsistentHashRing struct {
	virtualNodes int
	sortedTokens []uint64
	tokenToShard map[uint64]string
}

func NewConsistentHashRing(vnodes int) *ConsistentHashRing {
	return &ConsistentHashRing{
		virtualNodes: vnodes,
		tokenToShard: make(map[uint64]string),
	}
}

func (r *ConsistentHashRing) AddShard(shardID string) {
	for i := 0; i < r.virtualNodes; i++ {
		token := fnv1a64(shardID + "#vnode_" + strconv.Itoa(i))
		r.sortedTokens = append(r.sortedTokens, token)
		r.tokenToShard[token] = shardID
	}
	sort.Slice(r.sortedTokens, func(i, j int) bool {
		return r.sortedTokens[i] < r.sortedTokens[j]
	})
}

func (r *ConsistentHashRing) GetShard(key string) (string, error) {
	if len(r.sortedTokens) == 0 {
		return "", errors.New("hash ring is empty")
	}
	token := fnv1a64(key)
	idx := sort.Search(len(r.sortedTokens), func(i int) bool {
		return r.sortedTokens[i] >= token
	})
	if idx == len(r.sortedTokens) {
		idx = 0 // Wrap-around
	}
	return r.tokenToShard[r.sortedTokens[idx]], nil
}

// Топологія кластера
type ClusterTopology struct {
	Version uint64
	Ring    *ConsistentHashRing
	Shards  map[string]*ShardClient
}

// Маршрутизатор шардингу
type ShardRouter struct {
	topology atomic.Pointer[ClusterTopology]
}

func NewShardRouter() *ShardRouter {
	r := &ShardRouter{}
	initTop := &ClusterTopology{
		Version: 1,
		Ring:    NewConsistentHashRing(128),
		Shards:  make(map[string]*ShardClient),
	}
	r.topology.Store(initTop)
	return r
}

func (r *ShardRouter) UpdateTopology(shards map[string]string) {
	newTop := &ClusterTopology{
		Ring:   NewConsistentHashRing(128),
		Shards: make(map[string]*ShardClient),
	}
	for id, ep := range shards {
		newTop.Shards[id] = &ShardClient{ShardID: id, Endpoint: ep}
		newTop.Ring.AddShard(id)
	}

	oldTop := r.topology.Load()
	if oldTop != nil {
		newTop.Version = oldTop.Version + 1
	} else {
		newTop.Version = 1
	}

	r.topology.Store(newTop)
	fmt.Printf("[Router] Topology atomically updated to version %d with %d shards\n", newTop.Version, len(shards))
}

func (r *ShardRouter) Put(key, value string) error {
	top := r.topology.Load()
	shardID, err := top.Ring.GetShard(key)
	if err != nil {
		return err
	}
	client, ok := top.Shards[shardID]
	if !ok {
		return fmt.Errorf("shard %s not found", shardID)
	}
	return client.Put(key, value)
}

func (r *ShardRouter) Get(key string) (string, error) {
	top := r.topology.Load()
	shardID, err := top.Ring.GetShard(key)
	if err != nil {
		return "", err
	}
	client, ok := top.Shards[shardID]
	if !ok {
		return "", fmt.Errorf("shard %s not found", shardID)
	}
	return client.Get(key)
}

// Scatter-Gather опитування з паралельними горутинами
func (r *ShardRouter) ScatterGatherScan(ctx context.Context, filter string, timeout time.Duration) ([]Record, error) {
	top := r.topology.Load()
	shards := top.Shards

	if len(shards) == 0 {
		return nil, nil
	}

	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	type result struct {
		records []Record
		err     error
	}

	resChan := make(chan result, len(shards))
	var wg sync.WaitGroup

	for _, client := range shards {
		wg.Add(1)
		go func(c *ShardClient) {
			defer wg.Done()
			recs, err := c.Scan(ctx, filter)
			resChan <- result{records: recs, err: err}
		}(client)
	}

	wg.Wait()
	close(resChan)

	var aggregated []Record
	for res := range resChan {
		if res.err == nil {
			aggregated = append(aggregated, res.records...)
		} else {
			fmt.Printf("[Router] Shard scan error: %v\n", res.err)
		}
	}

	sort.Slice(aggregated, func(i, j int) bool {
		return aggregated[i].Timestamp > aggregated[j].Timestamp
	})

	return aggregated, nil
}

func main() {
	router := NewShardRouter()

	router.UpdateTopology(map[string]string{
		"shard-0": "10.0.1.10:3306",
		"shard-1": "10.0.1.11:3306",
		"shard-2": "10.0.1.12:3306",
	})

	_ = router.Put("user_10842", "{ name: 'Alice' }")
	_ = router.Put("user_99214", "{ name: 'Bob' }")

	v1, _ := router.Get("user_10842")
	v2, _ := router.Get("user_99214")
	fmt.Printf("[Client] Read user_10842: %s\n", v1)
	fmt.Printf("[Client] Read user_99214: %s\n", v2)

	fmt.Println("[Client] Executing Scatter-Gather scan...")
	records, _ := router.ScatterGatherScan(context.Background(), "status = 'ACTIVE'", 100*time.Millisecond)
	fmt.Printf("[Client] Total records returned: %d\n", len(records))
	for _, rec := range records {
		fmt.Printf("  - Key: %s | TS: %d\n", rec.Key, rec.Timestamp)
	}
}
```
:::

## Покроковий розбір алгоритмічних блоків коду

Щоб розібратися в деталях внутрішньої роботи маршрутизатора, простежимо виконання ключових операцій крок за кроком:

### 1. Детерміноване гешування (FNV-1a 64-bit)
У класі `HashUtil` реалізовано алгоритм Fowler–Noll–Vo (FNV-1a):
- Стартове значення зміщення (FNV Offset Basis) для 64 біт становить `0xcbf29ce484222325ULL`;
- Для кожного байта вхідного ключа виконується операція XOR із поточним хешем: `hash ^= byte`;
- Отримане значення множиться на 64-бітне просте число FNV Prime: `0x100000001b3ULL` (1099511628211).

Цей алгоритм забезпечує відмінний ефект лавини (Avalanche Effect): зміна навіть одного символу в ключі повністю змінює всі 64 біти вихідного токена, забезпечуючи рівномірне розсіювання по кільцю.

### 2. Побудова кільця та бінарний пошук токена
- Під час виклику `ConsistentHashRing::addShard(shardId)` генерується `V` віртуальних вузлів. Для `shard-0` створюються ключі `shard-0#vnode_0`, `shard-0#vnode_1`, ..., `shard-0#vnode_127`;
- У C++ структура `std::map<uint64_t, std::string>` зберігає токени у вигляді червоно-чорного дерева (Red-Black Tree), що гарантує впорядкованість ключів;
- Метод `getShard(key)` обчислює `token = fnv1a64(key)` і викликає `ring_.lower_bound(token)`:
  - Якщо в дереві є вузол із токеном `>= token`, повертається його ідентифікатор;
  - Якщо ключ більший за всі наявні токени (`it == ring_.end()`), ітератор повертається на початок (`it = ring_.begin()`), замикаючи кільце.

### 3. Багатопотоковий Scatter-Gather з бар'єром очікування
- При виклику `scatterGatherScan`:
  - Маршрутизатор завантажує поточну незмінну топологію через `std::atomic_load(&currentTopology_)`;
  - Для кожного з зареєстрованих шардів у векторі створюється асинхронна задача `std::async`, яка передає запит у пул потоків операційної системи;
  - Головний потік ітерується по вектору ф'ючерсів і викликає `fut.wait_for(timeout)`. Якщо шард відповів у межах ліміту, результат розпаковується через `fut.get()`;
  - Якщо час очікування перевищено, ф'ючерс позначається як збійний, запит не блокує інші потоки, а в лог пишеться попередження;
  - Після збору всіх доступних відповідей застосовується швидке сортування `std::sort` за часовою міткою `timestamp DESC`.

## Аналіз крайових випадків та відмовостійкості

Розробка промислового маршрутизатора вимагає врахування низки критичних позаштатних сценаріїв:

1. **Ізоляція збійних шардів та запобіжники (Circuit Breaking):** під час виконання `Scatter-Gather` аварійний збій або зависання одного вузла не повинні блокувати весь запит користувача. Використання жорстких таймаутів (`std::future::wait_for` у C++ та `context.WithTimeout` у Go) гарантує, що відповідь клієнту формується на основі вцілілих шардів із поверненням службового прапорця часткової неповноти вибірки (`PartialResults = true`).
2. **Конкурентне оновлення топології без замків (Lock-Free Swap):** заміна топології виконується атомарним оновленням покажчика (`std::atomic_store` / `atomic.Pointer`). Поточні обчислювальні потоки продовжують читати стару конфігурацію без конфліктів, що усуває потребу у важких м'ютексах на гарячому шляху маршрутизації.
3. **Обробка колізій хеш-токенів:** використання 64-бітного алгоритму FNV-1a знижує ймовірність колізії токенів віртуальних вузлів до зневажливо малої величини (`P_collision < 10⁻¹⁸` для `10 000` vnodes), що унеможливлює накладання діапазонів на кільці.
4. **Вичерпання пулу з'єднань на шардах (Connection Pool Saturation):** якщо сотні маршрутизаторів одночасно виконують віялові запити, кожен фізичний сервер MySQL/PostgreSQL стикається зі штормом нових TCP-сесій. Маршрутизатор зобов'язаний підтримувати постійний пул попередньо відкритих мультиплексованих з'єднань (Connection Multiplexing) із жорстким лімітом черги очікування.
5. **Захист від вичерпання пам'яті при агрегаціях (OOM Protection):** коли клієнт виконує запит `SELECT * FROM big_table ORDER BY date LIMIT 1000000` без ключа шардингу, координатор не повинен завантажувати всі мільйони рядків у буфер. Маршрутизатор зобов'язаний застосовувати потоковий мерджинг через пріоритетну чергу (K-way Merge Heap), споживаючи лише `O(N)` пам'яті незалежно від підсумкового розміру вибірки.
6. **Граційний дренаж при видаленні вузла (Graceful Drain):** при виведенні шарду з експлуатації роутер перестає надсилати на нього нові операції запису, але продовжує обслуговувати розпочаті транзакції читання до вичерпання таймауту лізи.
7. **Хеджування повільних запитів (Hedged Requests):** якщо 95% шардів відповідають за 5 мілісекунд, а один відстає довше ніж на 30 мілісекунд через локальну дискову чергу, маршрутизатор може надіслати дублюючий запит на резервну Read-репліку цього ж шарду, приймаючи перший результат, що надійшов.
8. **Пам'ять та обчислювальна складність:** для кластера зі 100 фізичних шардів та `V = 256` кільце містить `25 600` записів. Загальний обсяг пам'яті структури кільця становить менше 1.5 мегабайта, що дозволяє утримувати його в швидкому L3-кеші процесора маршрутизатора, забезпечуючи точковий пошук за 40–80 наносекунд.

## Порівняльний аналіз моделей багатопотоковості: C++ проти Go

Обидві наведені реалізації демонструють ідіоматичні підходи сучасних мов системного програмування до задачі маршрутизації:

### Модель C++ (C++20 Concurrency & Memory Model)
- **Управління пам'яттю:** незмінність об'єкта `ClusterTopology` захищена розумним покажчиком `std::shared_ptr`. Атомарні операції `std::atomic_load` та `std::atomic_store` гарантують безпеку читання за моделлю послідовної узгодженості (Sequential Consistency);
- **Паралелізм:** створення ф'ючерсів `std::future` через `std::async` забезпечує пряме використання системних потоків OS (pthreads у Linux). Це усуває накладні витрати на інтерпретацію середовища виконання, забезпечуючи мінімальну затримку на наносекундному рівні;
- **RAII-гарантії:** ресурси сокетів та буферів очищаються деструкторами автоматично при виході з області видимості, що унеможливлює витоки дескрипторів навіть під час викидання винятків `std::runtime_error`.

### Модель Go (CSP & Goroutines)
- **Горутини замість потоків OS:** виділення всього 2–4 КБ на стек горутини дозволяє маршрутизатору легко запускати десятки тисяч паралельних віялових опитувань без ризику вичерпання віртуальної пам'яті процесу;
- **Контексти та скасування:** об'єкт `context.Context` забезпечує наскрізне поширення сигналу переривання (`ctx.Done()`) при спрацьовуванні таймауту, миттєво припиняючи очікування на повільних мережевих сокетах;
- **Атомарні покажчики `atomic.Pointer`:** вбудований тип Go 1.19+ надає потокобезпечне оновлення покажчика на топологію з підтримкою автоматичного збирання сміття (GC) для старих поколінь конфігурації.

## Інженерний протокол налаштування та профілювання для High-Load

Під час експлуатації маршрутизатора під навантаженням понад 100 000 RPS рекомендується дотримуватися наступних налаштувань операційної системи та процесу:

1. **Тюнінг мережевого стеку Linux (`sysctl`):**
   - `net.core.somaxconn = 65535` — розширення черги готових підключень сокетів;
   - `net.ipv4.tcp_tw_reuse = 1` — безпечне повторне використання сокетів у стані `TIME_WAIT`;
   - `net.ipv4.tcp_max_syn_backlog = 3240000` — захист від втрати SYN-пакетів при сплесках підключень.
2. **Ліміти файлових дескрипторів (`limits.conf`):**
   - Встановлення `nofile = 1048576` для процесу роутера, що унеможливлює помилки `EMFILE: Too many open files` під час масивних віялових запитів.
3. **Моніторинг затримок через eBPF / perf:**
   - Профілювання функції `getShard` через утиліту `perf top` для перевірки відсутності промахів повз L1/L2 кеш процесора під час бінарного пошуку на кільці;
   - Фіксація тривалості бар'єра синхронізації у Scatter-Gather через Prometheus-гістограму `router_scatter_gather_duration_seconds{status="ok|timeout"}`.
