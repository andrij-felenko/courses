# ⚙️ Реалізація Pub/Sub брокера: дерево префіксів тем, буферизація та захист від повільних споживачів

Реалізація власного брокера повідомлень публікації-підписки (Pub/Sub) вимагає розв'язання двох фундаментальних інженерних задач: швидкого зіставлення теми опублікованої події з тисячами підписок із підтримкою масок (wildcards) та ізоляції підписників через обмежені кільцеві буфери, щоб збій або повільність одного клієнта не призводили до блокування всієї системи.

Нижче наведено повністю працездатний потокобезпечний брокер у пам'яті (in-memory broker), який реалізує префіксне дерево тем (Trie) зі спеціальними символами `*` (один рівень) та `>` (всі наступні рівні), а також політику скидання найстаріших повідомлень (*DropOldest*) при переповненні буфера підписника.

:::tabs
```cpp
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <queue>
#include <thread>
#include <chrono>
#include <functional>
#include <sstream>
#include <atomic>
#include <optional>

// Повідомлення в системі Pub/Sub
struct Message {
    std::string topic;
    std::string payload;
    uint64_t sequence_id;
};

// Політика поведінки при переповненні буфера
enum class OverflowPolicy {
    DropOldest,
    RejectNewest
};

// Черга підписника з обмеженою ємністю
class SubscriberQueue {
public:
    SubscriberQueue(std::string id, size_t capacity, OverflowPolicy policy)
        : id_(std::move(id)), capacity_(capacity), policy_(policy), dropped_count_(0) {}

    bool push(const Message& msg) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.size() >= capacity_) {
            if (policy_ == OverflowPolicy::DropOldest) {
                queue_.pop();
                dropped_count_++;
                queue_.push(msg);
                return true;
            } else {
                dropped_count_++;
                return false;
            }
        }
        queue_.push(msg);
        return true;
    }

    std::optional<Message> pop() {
        std::lock_guard<std::mutex> lock(mutex_);
        if (queue_.empty()) {
            return std::nullopt;
        }
        Message msg = queue_.front();
        queue_.pop();
        return msg;
    }

    std::string id() const { return id_; }
    size_t dropped_count() const { return dropped_count_.load(); }
    size_t size() {
        std::lock_guard<std::mutex> lock(mutex_);
        return queue_.size();
    }

private:
    std::string id_;
    size_t capacity_;
    OverflowPolicy policy_;
    std::queue<Message> queue_;
    std::atomic<size_t> dropped_count_;
    std::mutex mutex_;
};

// Вузол дерева префіксів тем (Topic Trie)
class TrieNode {
public:
    std::unordered_map<std::string, std::unique_ptr<TrieNode>> children;
    std::vector<std::shared_ptr<SubscriberQueue>> subscribers;

    // Рекурсивне додавання підписки на шаблон теми
    void insert(const std::vector<std::string>& tokens, size_t index, 
                std::shared_ptr<SubscriberQueue> sub) {
        if (index == tokens.size()) {
            subscribers.push_back(sub);
            return;
        }

        const std::string& token = tokens[index];
        if (children.find(token) == children.end()) {
            children[token] = std::make_unique<TrieNode>();
        }
        children[token]->insert(tokens, index + 1, sub);
    }

    // Рекурсивний пошук усіх підписників, що відповідають опублікованій темі
    void match(const std::vector<std::string>& tokens, size_t index,
               std::vector<std::shared_ptr<SubscriberQueue>>& result) const {
        // Якщо на цьому рівні є підписка на всі наступні рівні ('>')
        auto multi_it = children.find(">");
        if (multi_it != children.end()) {
            for (const auto& sub : multi_it->second->subscribers) {
                result.push_back(sub);
            }
        }

        if (index == tokens.size()) {
            for (const auto& sub : subscribers) {
                result.push_back(sub);
            }
            return;
        }

        const std::string& token = tokens[index];

        // 1. Точний збіг токена
        auto exact_it = children.find(token);
        if (exact_it != children.end()) {
            exact_it->second->match(tokens, index + 1, result);
        }

        // 2. Однорівнева маска ('*')
        auto single_it = children.find("*");
        if (single_it != children.end()) {
            single_it->second->match(tokens, index + 1, result);
        }
    }
};

// Центральний Pub/Sub Брокер
class PubSubBroker {
public:
    PubSubBroker() : seq_counter_(0), root_(std::make_unique<TrieNode>()) {}

    // Допоміжна функція розбиття теми на токени
    static std::vector<std::string> tokenize(std::string_view topic) {
        std::vector<std::string> tokens;
        size_t start = 0;
        while (start < topic.size()) {
            size_t end = topic.find('/', start);
            if (end == std::string_view::npos) {
                tokens.emplace_back(topic.substr(start));
                break;
            }
            tokens.emplace_back(topic.substr(start, end - start));
            start = end + 1;
        }
        return tokens;
    }

    // Підписка на тему
    void subscribe(std::string_view pattern, std::shared_ptr<SubscriberQueue> sub) {
        std::lock_guard<std::mutex> lock(trie_mutex_);
        auto tokens = tokenize(pattern);
        root_->insert(tokens, 0, sub);
    }

    // Публікація повідомлення в тему
    size_t publish(std::string_view topic, std::string payload) {
        Message msg;
        msg.topic = std::string(topic);
        msg.payload = std::move(payload);
        msg.sequence_id = ++seq_counter_;

        std::vector<std::shared_ptr<SubscriberQueue>> targets;
        {
            std::lock_guard<std::mutex> lock(trie_mutex_);
            auto tokens = tokenize(topic);
            root_->match(tokens, 0, targets);
        }

        // Доставка в буфери знайдених підписників (fan-out)
        size_t delivered = 0;
        for (auto& queue : targets) {
            if (queue->push(msg)) {
                delivered++;
            }
        }
        return delivered;
    }

private:
    std::atomic<uint64_t> seq_counter_;
    std::unique_ptr<TrieNode> root_;
    std::mutex trie_mutex_;
};

int main() {
    PubSubBroker broker;

    // Створюємо два підписники з обмеженими буферами
    // Клієнт 1: Швидкий аналітик з буфером 1000
    auto fast_sub = std::make_shared<SubscriberQueue>("FastAnalytics", 1000, OverflowPolicy::DropOldest);
    // Клієнт 2: Повільний експортер у PDF з малим буфером 5
    auto slow_sub = std::make_shared<SubscriberQueue>("SlowPDFExporter", 5, OverflowPolicy::DropOldest);

    // Підписка за шаблонами
    broker.subscribe("orders/eu/*", fast_sub); // Ловить orders/eu/ua, orders/eu/de
    broker.subscribe("orders/>", slow_sub);    // Ловить orders/eu/ua, orders/us/ny/vip тощо

    std::cout << "[Broker] Запуск демонстрації публікації...\n";

    // Видавець надсилає 20 повідомлень поспіль
    for (int i = 1; i <= 20; ++i) {
        std::string payload = "OrderData_#" + std::to_string(i);
        broker.publish("orders/eu/ua", payload);
    }

    std::cout << "\n[Результати доставки]:\n";
    std::cout << "FastAnalytics черга: " << fast_sub->size() 
              << " msg, скинуто: " << fast_sub->dropped_count() << "\n";
    std::cout << "SlowPDFExporter черга: " << slow_sub->size() 
              << " msg (макс 5), скинуто через повільність: " << slow_sub->dropped_count() << "\n";

    // Демонстрація вичитування
    std::cout << "\n[SlowPDFExporter] Зміст збережених повідомлень (найновіші):\n";
    while (auto msg = slow_sub->pop()) {
        std::cout << "  -> seq=" << msg->sequence_id << " payload=" << msg->payload << "\n";
    }

    return 0;
}
```
```go
package main

import (
	"fmt"
	"strings"
	"sync"
	"sync/atomic"
	"time"
)

// Message описує подію в Pub/Sub
type Message struct {
	Topic      string
	Payload    string
	SequenceID uint64
}

// OverflowPolicy визначає стратегію обробки переповнення
type OverflowPolicy int

const (
	DropOldest OverflowPolicy = iota
	RejectNewest
)

// SubscriberQueue представляє буфер конкретного підписника
type SubscriberQueue struct {
	id       string
	capacity int
	policy   OverflowPolicy
	ch       chan Message
	dropped  uint64
	mu       sync.Mutex
}

func NewSubscriberQueue(id string, capacity int, policy OverflowPolicy) *SubscriberQueue {
	return &SubscriberQueue{
		id:       id,
		capacity: capacity,
		policy:   policy,
		ch:       make(chan Message, capacity),
	}
}

func (sq *SubscriberQueue) Push(msg Message) bool {
	sq.mu.Lock()
	defer sq.mu.Unlock()

	select {
	case sq.ch <- msg:
		return true
	default:
		// Буфер переповнений
		atomic.AddUint64(&sq.dropped, 1)
		if sq.policy == DropOldest {
			// Скидаємо старе повідомлення і записуємо нове
			select {
			case <-sq.ch:
			default:
			}
			select {
			case sq.ch <- msg:
				return true
			default:
				return false
			}
		}
		return false
	}
}

func (sq *SubscriberQueue) Pop() (Message, bool) {
	select {
	case msg := <-sq.ch:
		return msg, true
	default:
		return Message{}, false
	}
}

// TrieNode вузол дерева маршрутизації тем
type TrieNode struct {
	children    map[string]*TrieNode
	subscribers []*SubscriberQueue
}

func NewTrieNode() *TrieNode {
	return &TrieNode{
		children: make(map[string]*TrieNode),
	}
}

func (n *TrieNode) Insert(tokens []string, sub *SubscriberQueue) {
	if len(tokens) == 0 {
		n.subscribers = append(n.subscribers, sub)
		return
	}
	token := tokens[0]
	child, exists := n.children[token]
	if !exists {
		child = NewTrieNode()
		n.children[token] = child
	}
	child.Insert(tokens[1:], sub)
}

func (n *TrieNode) Match(tokens []string, result *[]*SubscriberQueue) {
	// Багаторівневий wildcard '>'
	if multi, exists := n.children[">"]; exists {
		*result = append(*result, multi.subscribers...)
	}

	if len(tokens) == 0 {
		*result = append(*result, n.subscribers...)
		return
	}

	token := tokens[0]

	// Точний збіг
	if exact, exists := n.children[token]; exists {
		exact.Match(tokens[1:], result)
	}

	// Однорівневий wildcard '*'
	if single, exists := n.children["*"]; exists {
		single.Match(tokens[1:], result)
	}
}

// Broker центральний диспетчер Pub/Sub
type Broker struct {
	root       *TrieNode
	seqCounter uint64
	mu         sync.RWMutex
}

func NewBroker() *Broker {
	return &Broker{
		root: NewTrieNode(),
	}
}

func (b *Broker) Subscribe(pattern string, sub *SubscriberQueue) {
	b.mu.Lock()
	defer b.mu.Unlock()
	tokens := strings.Split(pattern, "/")
	b.root.Insert(tokens, sub)
}

func (b *Broker) Publish(topic string, payload string) int {
	seq := atomic.AddUint64(&b.seqCounter, 1)
	msg := Message{
		Topic:      topic,
		Payload:    payload,
		SequenceID: seq,
	}

	b.mu.RLock()
	var targets []*SubscriberQueue
	tokens := strings.Split(topic, "/")
	b.root.Match(tokens, &targets)
	b.mu.RUnlock()

	delivered := 0
	for _, sub := range targets {
		if sub.Push(msg) {
			delivered++
		}
	}
	return delivered
}

func main() {
	broker := NewBroker()

	fastSub := NewSubscriberQueue("FastAnalytics", 1000, DropOldest)
	slowSub := NewSubscriberQueue("SlowPDFExporter", 5, DropOldest)

	broker.Subscribe("orders/eu/*", fastSub)
	broker.Subscribe("orders/>", slowSub)

	fmt.Println("[Broker] Запуск публікації 20 подій...")
	for i := 1; i <= 20; i++ {
		broker.Publish("orders/eu/ua", fmt.Sprintf("OrderData_#%d", i))
	}

	time.Sleep(10 * time.Millisecond)

	fmt.Printf("FastAnalytics: в черзі %d, скинуто %d\n", len(fastSub.ch), atomic.LoadUint64(&fastSub.dropped))
	fmt.Printf("SlowPDFExporter: в черзі %d, скинуто %d\n", len(slowSub.ch), atomic.LoadUint64(&slowSub.dropped))

	fmt.Println("\n[SlowPDFExporter] Збережені повідомлення (останні 5):")
	for {
		msg, ok := slowSub.Pop()
		if !ok {
			break
		}
		fmt.Printf("  -> seq=%d payload=%s\n", msg.SequenceID, msg.Payload)
	}
}
```
:::

## Детальний розбір архітектури компонентів

Наведена реалізація демонструє ключові патерни побудови промислових систем обробки повідомлень:

### 1. Дерево префіксів тем (Topic Trie) проти лінійного пошуку

У наївній реалізації брокер зберігає список зареєстрованих підписників у лінійному масиві або хеш-таблиці. Якщо в системі зареєстровано `N` підписників із масками на зразок `orders/+/created`, при кожній публікації брокер змушений перевіряти регулярні вирази або розбивати рядки для кожного з `N` правил. Це дає алгоритмічну складність `O(N · L)`, де `L` — середня довжина теми. При 100 000 підписників час доставки одного повідомлення сягає десятків мілісекунд, що унеможливлює роботу в реальному часі.

Дерево префіксів `TrieNode` організовує теми у вигляді ієрархії токенів. Кожен вузол містить асоціативний масив дочірніх вузлів `children` за назвою токена та список підписників, зареєстрованих саме на цьому рівні.
При надходженні повідомлення з темою `orders/eu/ua` метод `match()` виконує рекурсивний спуск:
1. На рівні кореня перевіряється наявність дочірнього вузла `>` (багаторівневий збіг). Якщо він є, усі його підписники негайно додаються до списку отримувачів.
2. Далі перевіряється точний збіг першого токена (`orders`) та однорівневий збіг (`*`).
3. Пошук продовжується для токенів `eu` та `ua`.
4. Складність пошуку становить `O(L + K)`, де `L` — кількість сегментів теми (зазвичай 3–6), а `K` — кількість фактично знайдених отримувачів. Швидкість маршрутизації не залежить від загальної кількості підписок у системі.

### 2. Кільцеві буфери підписників та ізоляція відмов

Кожен підписник володіє власним екземпляром `SubscriberQueue` із фіксованою ємністю `capacity_`. Коли видавець викликає `publish()`, брокер лише розміщує копію повідомлення в черзі кожного знайденого підписника.
Це забезпечує повну ізоляцію споживачів:
- **Швидкий споживач (`FastAnalytics`):** має великий буфер (1000) і швидко вичитує дані. Його черга завжди майже порожня, затримка мінімальна, лічильник скинутих повідомлень дорівнює нулю.
- **Повільний споживач (`SlowPDFExporter`):** має малий буфер (5) і не встигає за видавцем. Коли черга заповнюється, спрацьовує політика `OverflowPolicy::DropOldest`: черга видаляє найстаріше повідомлення з голови (`queue_.pop()`) і записує нове в хвіст. Лічильник `dropped_count_` атомарно інкрементується.
- **Результат виконання тесту:** під час відправки 20 повідомлень швидкий підписник зберіг усі 20, а повільний підписник відкинув 15 найстаріших повідомлень (з 1 по 15) і зберіг лише останні 5 (із номерами 16, 17, 18, 19, 20). Жоден інший клієнт і сам видавець не відчули затримок.

### 3. Двоетапна диспетчеризація та усунення взаємних блокувань (Deadlock Freedom)

Критичною вимогою до багатопотокового брокера є запобігання взаємним блокуванням (*deadlocks*).
Якщо метод `publish()` триматиме блокування глобального дерева тем `trie_mutex_` у той самий момент, коли викликається `queue->push()`, виникає небезпечна ієрархія блокувань:
```
Потік 1 (Publish):   Захопив TrieLock ───> Намагається захопити QueueLock_A
Потік 2 (Subscribe): Захопив QueueLock_A ─> Намагається захопити TrieLock
===> Взаємне блокування (Deadlock)!
```

Щоб повністю усунути цей ризик, у коді реалізовано **двоетапну диспетчеризацію (Two-Phase Dispatch)**:
1. **Фаза 1 (Пошук адресатів):** під захистом короткого блокування дерева тем формується локальний вектор вказівників на цільові черги `std::vector<std::shared_ptr<SubscriberQueue>> targets`.
2. **Фаза 2 (Роздача):** блокування дерева тем `trie_mutex_` **негайно звільняється**, після чого брокер ітерується по чергах і викликає `push()`. Жоден потік ніколи не тримає два м'ютекси одночасно.

### 4. Керування пам'яттю та оптимізація копіювання корисного навантаження

У наведеному коді для наочності структури кожне повідомлення містить власну копію рядків `topic` та `payload`. У високонавантажених промислових брокерах (наприклад, Apache Pulsar або NATS Core) застосовують оптимізацію незмінного буфера (*immutable shared payload*):

```cpp
struct OptimizedMessage {
    std::string_view topic;
    std::shared_ptr<const std::vector<uint8_t>> payload;
    uint64_t sequence_id;
};
```

При коефіцієнті розмноження `M = 1000` брокер не копіює масив байтів корисного навантаження розміром 1 МБ тисячу разів. Замість цього створюється один блок `shared_ptr`, а в черги підписників передаються лише легкі дескриптори. Пам'ять звільняється автоматично, коли останній підписник завершує обробку свого повідомлення.

### 5. Конкурентність та усунення блокувань при масштабуванні

У класі `PubSubBroker` дерево тем захищене м'ютексом `trie_mutex_`. У середовищі з тисячами паралельних потоків видавців взяття ексклюзивного блокування при кожній публікації стає вузьким місцем.
Для оптимізації в багатоядерних системах застосовують такі підходи:
1. **Розділення блокувань читання/запису (`std::shared_mutex` у C++ або `sync.RWMutex` у Go):** операція `publish()` бере блокування лише на читання (`shared_lock`), дозволяючи сотням потоків паралельно виконувати пошук у дереві. Ексклюзивне блокування (`unique_lock`) береться лише під час рідкісних операцій `subscribe()` або `unsubscribe()`.
2. **Шардинг дерев (Partitioned Trie):** теми хешуються за кореневим префіксом (наприклад, `orders/...` в один шард, `telemetry/...` в інший), кожен із яких має власний незалежний м'ютекс.
3. **Дерева без блокувань або Copy-on-Write (COW):** при реєстрації нової підписки створюється копія гілки дерева, а вказівник підмінюється атомарною операцією `std::atomic_store`. Видавці читають дерево взагалі без системних викликів блокування.
4. **Конструкція кільцевого буфера без динамічних алокацій:** використання `std::queue<Message>` виконує виділення пам'яті в купі (`malloc`) на кожне повідомлення. Заміна її на фіксований кільцевий масив `std::vector<Message>` з індексами голови й хвоста усуває навантаження на алокатор пам'яті та підвищує просторову локальність кешу процесора (L1/L2 cache locality).

### 6. Порівняння реалізації мовою Go та патерни CSP

У версії мовою Go черга `SubscriberQueue` реалізована поверх вбудованого каналу `chan Message`. Це демонструє різницю підходів між об'єктно-орієнтованим керуванням пам'яттю в C++ та моделлю взаємодіючих послідовних процесів (CSP) у Go:
- Неблокуюча відправка реалізується за допомогою конструкції `select` із секцією `default`. Якщо канал заповнений, потік виконання не блокується, а негайно переходить до скидання старого значення через вичитування `<-sq.ch`.
- Подвійний захист `sq.mu.Lock()` навколо каналу запобігає стану гонитви між двома паралельними потоками видавців, які одночасно намагаються скинути елемент із каналу при переповненні.
- Атомарний лічильник `atomic.AddUint64` забезпечує потокобезпечний збір метрик для систем моніторингу Prometheus без взяття блокувань під час читання статистики.
