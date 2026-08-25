# ⚙️ Реалізація патернів кешування: Cache-Aside, Read-Through, Write-Through та Write-Behind

Коли високонавантаженій розподіленій системі потрібно узгодити швидку оперативну пам'ять із надійним дисковим сховищем, архітектор стикається з фундаментальним питанням розподілу обов'язків: хто координує потік запитів, у який момент дані завантажуються в кеш, як запобігти розходженню стану під час одночасних модифікацій і що відбувається з даними в разі раптового аварійного збою.

Нижче наведено вичерпну практичну реалізацію базових патернів кешування — **Cache-Aside** (оркестрація застосунком), **Read-Through** (прозорий автозавантажувач із дедуплікацією запитів singleflight), **Write-Through** (синхронний наскрізний запис) та **Write-Behind** (асинхронний відкладений запис із буферизацією, коалесценцією мутацій та зворотним тиском) — мовами C++ та Go. Також детально розібрано стратегії **Write-Around** та **Refresh-Ahead**, шардування пам'яті для усунення блокувань, математику ефективності пакетування, регулювання зворотного тиску (backpressure) та обробку часткових відмов у розподіленому середовищі.

## Архітектурний задум і розподіл обов'язків

Щоб поведінку різних стратегій можна було коректно зіставити та протестувати, виділимо два базові компоненти системи:
1. **Первинне сховище (Database):** Абстракція надійного персистентного сховища (наприклад, кластера PostgreSQL, MySQL або дискового Key-Value). Операції з цим сховищем пов'язані з мережевими затримками, дисковим вводом-виводом і транзакційними витратами (у нашій моделі затримка читання становить 10 мс, запису — 15 мс, а пакетного запису — 25 мс).
2. **Кеш-сховище (CacheStore):** Швидке сховище в оперативній пам'яті (локальна пам'ять процесу або інстанс Redis/Memcached), доступ до якого відбувається за частки мілісекунди через атомарні потокобезпечні операції.

Кожен із менеджерів кешування реалізує власну модель взаємодії між цими компонентами:

```
1. Cache-Aside:
   Читання: Застосунок ──> Кеш (промах) ──> База Даних ──> Запис у Кеш
   Запис:    Застосунок ──> База Даних ──> Видалення (DEL) із Кешу

2. Read-Through:
   Читання: Застосунок ──> Кеш-Проксі (промах) ──[ Singleflight ]──> База Даних ──> Повернення

3. Write-Through:
   Запис:    Застосунок ──> Менеджер ──[ Синхронно ]──> База Даних + Кеш

4. Write-Behind:
   Запис:    Застосунок ──> Кеш (миттєво) + Буфер ──[ Асинхронно ]──> База Даних

5. Write-Around:
   Запис:    Застосунок ──> База Даних (минаючи кеш) ──> Видалення з Кешу
```

У патерні **Cache-Aside** застосунок самостійно вирішує, коли звертатися до бази. При записі він обов'язково виконує операцію **інвалідації (видалення ключа)**, а не перезапису значення в кеші, що запобігає гонці неузгодженості між двома паралельними модифікаціями.

У патерні **Read-Through** клієнтський код взаємодіє виключно з інтерфейсом кешу. Кеш інкапсулює функцію зворотного виклику (Loader) і самостійно завантажує відсутні дані. Щоб запобігти лавинній навалі (Cache Stampede), реалізовано механізм **Singleflight (коалесценція запитів на читання)**: якщо сотня потоків одночасно запитує один і той самий холодний ключ, до бази виконується рівно один запит, а результат роздається всім очікуючим потокам.

У патерні **Write-Through** менеджер бере на себе синхронізацію: запис у базу та оновлення пам'яті відбуваються в межах єдиного синхронного виклику, гарантуючи негайну строгу узгодженість для наступних читань.

У патерні **Write-Behind (Write-Back)** клієнт отримує підтвердження успіху негайно після запису в оперативну пам'ять та постановки операції в чергу. Фоновий воркер періодично прокидається, забирає накопичені оновлення, виконує **коалесценцію (coalescing)** — об'єднує багаторазові зміни того самого ключа в одне фінальне значення — і записує результат у базу єдиною пакетною транзакцією.

## Повний робочий код реалізації

:::tabs
```cpp
#include <iostream>
#include <string>
#include <unordered_map>
#include <optional>
#include <mutex>
#include <shared_mutex>
#include <chrono>
#include <thread>
#include <condition_variable>
#include <vector>
#include <memory>
#include <functional>
#include <future>

// ── Інтерфейс первинного надійного сховища ──────────────────────────────────
class Database {
public:
    virtual ~Database() = default;
    virtual std::optional<std::string> get(const std::string& key) = 0;
    virtual void set(const std::string& key, const std::string& value) = 0;
    virtual void batch_set(const std::vector<std::pair<std::string, std::string>>& items) = 0;
};

// Імітація бази даних із затримками дискового вводу-виводу
class MockDatabase : public Database {
    mutable std::shared_mutex mtx_;
    std::unordered_map<std::string, std::string> storage_;
public:
    std::optional<std::string> get(const std::string& key) override {
        std::this_thread::sleep_for(std::chrono::milliseconds(10)); // імітація IO
        std::shared_lock lock(mtx_);
        auto it = storage_.find(key);
        if (it != storage_.end()) return it->second;
        return std::nullopt;
    }

    void set(const std::string& key, const std::string& value) override {
        std::this_thread::sleep_for(std::chrono::milliseconds(15)); // імітація fsync
        std::unique_lock lock(mtx_);
        storage_[key] = value;
    }

    void batch_set(const std::vector<std::pair<std::string, std::string>>& items) override {
        std::this_thread::sleep_for(std::chrono::milliseconds(25)); // груповий запис
        std::unique_lock lock(mtx_);
        for (const auto& [k, v] : items) {
            storage_[k] = v;
        }
    }
};

// ── Швидкий потокобезпечний кеш у пам'яті ──────────────────────────────────
class CacheStore {
    mutable std::shared_mutex mtx_;
    std::unordered_map<std::string, std::string> map_;
public:
    std::optional<std::string> get(const std::string& key) const {
        std::shared_lock lock(mtx_);
        auto it = map_.find(key);
        if (it != map_.end()) return it->second;
        return std::nullopt;
    }

    void set(const std::string& key, const std::string& value) {
        std::unique_lock lock(mtx_);
        map_[key] = value;
    }

    void del(const std::string& key) {
        std::unique_lock lock(mtx_);
        map_.erase(key);
    }
};

// ── Допоміжний механізм Singleflight (придушення дублікатів запитів) ───────
class SingleflightGroup {
    struct Call {
        std::shared_future<std::optional<std::string>> future;
    };
    std::mutex mtx_;
    std::unordered_map<std::string, std::shared_ptr<Call>> calls_;
public:
    template<typename Fn>
    std::optional<std::string> execute(const std::string& key, Fn&& fn) {
        std::shared_ptr<Call> call;
        {
            std::lock_guard lock(mtx_);
            auto it = calls_.find(key);
            if (it != calls_.end()) {
                call = it->second;
            } else {
                call = std::make_shared<Call>();
                auto task = std::make_shared<std::packaged_task<std::optional<std::string>()>>(std::forward<Fn>(fn));
                call->future = task->get_future().share();
                calls_[key] = call;
                std::thread([task]() { (*task)(); }).detach();
            }
        }

        auto result = call->future.get();

        {
            std::lock_guard lock(mtx_);
            calls_.erase(key);
        }

        return result;
    }
};

// ── 1. Патерн Cache-Aside (Оркестрація застосунком) ─────────────────────────
class CacheAsideManager {
    std::shared_ptr<Database> db_;
    std::shared_ptr<CacheStore> cache_;
public:
    CacheAsideManager(std::shared_ptr<Database> db, std::shared_ptr<CacheStore> cache)
        : db_(std::move(db)), cache_(std::move(cache)) {}

    std::optional<std::string> get(const std::string& key) {
        // 1. Спроба читання з кешу
        if (auto cached = cache_->get(key); cached.has_value()) {
            return cached; // влучання (hit)
        }

        // 2. Промах (miss) — звернення до джерела правди
        auto from_db = db_->get(key);
        if (from_db.has_value()) {
            // 3. Ліниве наповнення кешу отриманим значенням
            cache_->set(key, *from_db);
        }
        return from_db;
    }

    void update(const std::string& key, const std::string& value) {
        // 1. Спершу фіксуємо зміну в базі даних
        db_->set(key, value);
        // 2. Інвалідуємо кеш (видалення, а не перезапис, захищає від гонок запису)
        cache_->del(key);
    }
};

// ── 2. Патерн Read-Through з підтримкою Singleflight ────────────────────────
class ReadThroughManager {
    std::shared_ptr<Database> db_;
    std::shared_ptr<CacheStore> cache_;
    SingleflightGroup sf_;
public:
    ReadThroughManager(std::shared_ptr<Database> db, std::shared_ptr<CacheStore> cache)
        : db_(std::move(db)), cache_(std::move(cache)) {}

    std::optional<std::string> get(const std::string& key) {
        if (auto cached = cache_->get(key); cached.has_value()) {
            return cached;
        }

        // При промаху дедуплікуємо паралельні звернення до одного ключа
        return sf_.execute(key, [this, key]() -> std::optional<std::string> {
            // Подвійна перевірка (Double-checked locking pattern)
            if (auto cached = cache_->get(key); cached.has_value()) {
                return cached;
            }
            auto val = db_->get(key);
            if (val.has_value()) {
                cache_->set(key, *val);
            }
            return val;
        });
    }
};

// ── 3. Патерн Write-Through (Синхронний наскрізний запис) ───────────────────
class WriteThroughManager {
    std::shared_ptr<Database> db_;
    std::shared_ptr<CacheStore> cache_;
public:
    WriteThroughManager(std::shared_ptr<Database> db, std::shared_ptr<CacheStore> cache)
        : db_(std::move(db)), cache_(std::move(cache)) {}

    std::optional<std::string> get(const std::string& key) {
        if (auto cached = cache_->get(key); cached.has_value()) {
            return cached;
        }
        auto from_db = db_->get(key);
        if (from_db.has_value()) {
            cache_->set(key, *from_db);
        }
        return from_db;
    }

    void set(const std::string& key, const std::string& value) {
        // Синхронний наскрізний запис: спершу база, потім оновлення кешу
        db_->set(key, value);
        cache_->set(key, value);
    }
};

// ── 4. Патерн Write-Behind (Асинхронний запис із коалесценцією) ─────────────
class WriteBehindManager {
    std::shared_ptr<Database> db_;
    std::shared_ptr<CacheStore> cache_;

    std::mutex queue_mtx_;
    std::condition_variable cv_;
    std::unordered_map<std::string, std::string> write_buffer_; // мапа для коалесценції
    size_t max_buffer_size_{10000};
    bool stop_{false};
    std::jthread worker_;

    void worker_loop() {
        while (true) {
            std::unordered_map<std::string, std::string> batch;
            {
                std::unique_lock lock(queue_mtx_);
                // Чекаємо тайм-ауту скидання (50 мс) або сигналу зупинки/переповнення
                cv_.wait_for(lock, std::chrono::milliseconds(50), [this] {
                    return stop_ || write_buffer_.size() >= 50;
                });

                if (stop_ && write_buffer_.empty()) {
                    break;
                }

                batch.swap(write_buffer_); // атомарне вилучення накопиченої пачки
            }

            if (!batch.empty()) {
                std::vector<std::pair<std::string, std::string>> items(batch.begin(), batch.end());
                db_->batch_set(items); // груповий запис у базу
            }
        }
    }

public:
    WriteBehindManager(std::shared_ptr<Database> db, std::shared_ptr<CacheStore> cache)
        : db_(std::move(db)), cache_(std::move(cache)) {
        worker_ = std::jthread([this] { worker_loop(); });
    }

    ~WriteBehindManager() {
        {
            std::unique_lock lock(queue_mtx_);
            stop_ = true;
        }
        cv_.notify_all();
        // std::jthread автоматично виконає join() у своєму деструкторі
    }

    std::optional<std::string> get(const std::string& key) {
        if (auto cached = cache_->get(key); cached.has_value()) {
            return cached;
        }
        auto from_db = db_->get(key);
        if (from_db.has_value()) {
            cache_->set(key, *from_db);
        }
        return from_db;
    }

    bool set(const std::string& key, const std::string& value) {
        // Миттєвий запис у кеш для забезпечення читання щойно записаного (Read-Your-Writes)
        cache_->set(key, value);

        // Буферизація з контролем переповнення (Backpressure)
        std::unique_lock lock(queue_mtx_);
        if (write_buffer_.size() >= max_buffer_size_) {
            return false; // захист від вичерпання пам'яті
        }
        write_buffer_[key] = value; // коалесценція: повторний запис замінює старе значення
        if (write_buffer_.size() >= 50) {
            cv_.notify_one();
        }
        return true;
    }
};
```
```go
package main

import (
	"context"
	"errors"
	"sync"
	"time"
)

// Database визначає інтерфейс первинного сховища
type Database interface {
	Get(key string) (string, bool)
	Set(key, value string)
	BatchSet(items map[string]string)
}

// MockDatabase імітує мережеві та дискові затримки
type MockDatabase struct {
	mu      sync.RWMutex
	storage map[string]string
}

func NewMockDatabase() *MockDatabase {
	return &MockDatabase{storage: make(map[string]string)}
}

func (db *MockDatabase) Get(key string) (string, bool) {
	time.Sleep(10 * time.Millisecond) // імітація IO
	db.mu.RLock()
	defer db.mu.RUnlock()
	val, ok := db.storage[key]
	return val, ok
}

func (db *MockDatabase) Set(key, value string) {
	time.Sleep(15 * time.Millisecond)
	db.mu.Lock()
	defer db.mu.Unlock()
	db.storage[key] = value
}

func (db *MockDatabase) BatchSet(items map[string]string) {
	time.Sleep(25 * time.Millisecond)
	db.mu.Lock()
	defer db.mu.Unlock()
	for k, v := range items {
		db.storage[k] = v
	}
}

// CacheStore — швидкий кеш у пам'яті
type CacheStore struct {
	mu  sync.RWMutex
	mem map[string]string
}

func NewCacheStore() *CacheStore {
	return &CacheStore{mem: make(map[string]string)}
}

func (c *CacheStore) Get(key string) (string, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	val, ok := c.mem[key]
	return val, ok
}

func (c *CacheStore) Set(key, value string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.mem[key] = value
}

func (c *CacheStore) Del(key string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	delete(c.mem, key)
}

// ── Singleflight Group для Read-Through ─────────────────────────────────────
type call struct {
	wg  sync.WaitGroup
	val string
	ok  bool
	err error
}

type SingleflightGroup struct {
	mu sync.Mutex
	m  map[string]*call
}

func NewSingleflightGroup() *SingleflightGroup {
	return &SingleflightGroup{m: make(map[string]*call)}
}

func (g *SingleflightGroup) Do(key string, fn func() (string, bool)) (string, bool) {
	g.mu.Lock()
	if c, ok := g.m[key]; ok {
		g.mu.Unlock()
		c.wg.Wait()
		return c.val, c.ok
	}
	c := new(call)
	c.wg.Add(1)
	g.m[key] = c
	g.mu.Unlock()

	c.val, c.ok = fn()
	c.wg.Done()

	g.mu.Lock()
	delete(g.m, key)
	g.mu.Unlock()

	return c.val, c.ok
}

// ── 1. Cache-Aside Manager ──────────────────────────────────────────────────
type CacheAsideManager struct {
	db    Database
	cache *CacheStore
}

func NewCacheAsideManager(db Database, cache *CacheStore) *CacheAsideManager {
	return &CacheAsideManager{db: db, cache: cache}
}

func (m *CacheAsideManager) Get(key string) (string, bool) {
	if val, ok := m.cache.Get(key); ok {
		return val, true // влучання
	}
	val, ok := m.db.Get(key)
	if ok {
		m.cache.Set(key, val) // наповнення на промах
	}
	return val, ok
}

func (m *CacheAsideManager) Update(key, value string) {
	m.db.Set(key, value) // спершу сховище правди
	m.cache.Del(key)    // інвалідація кешу (delete замість set)
}

// ── 2. Read-Through Manager ────────────────────────────────────────────────
type ReadThroughManager struct {
	db    Database
	cache *CacheStore
	sf    *SingleflightGroup
}

func NewReadThroughManager(db Database, cache *CacheStore) *ReadThroughManager {
	return &ReadThroughManager{
		db:    db,
		cache: cache,
		sf:    NewSingleflightGroup(),
	}
}

func (m *ReadThroughManager) Get(key string) (string, bool) {
	if val, ok := m.cache.Get(key); ok {
		return val, true
	}
	return m.sf.Do(key, func() (string, bool) {
		if val, ok := m.cache.Get(key); ok {
			return val, true
		}
		val, ok := m.db.Get(key)
		if ok {
			m.cache.Set(key, val)
		}
		return val, ok
	})
}

// ── 3. Write-Through Manager ────────────────────────────────────────────────
type WriteThroughManager struct {
	db    Database
	cache *CacheStore
}

func NewWriteThroughManager(db Database, cache *CacheStore) *WriteThroughManager {
	return &WriteThroughManager{db: db, cache: cache}
}

func (m *WriteThroughManager) Get(key string) (string, bool) {
	if val, ok := m.cache.Get(key); ok {
		return val, true
	}
	val, ok := m.db.Get(key)
	if ok {
		m.cache.Set(key, val)
	}
	return val, ok
}

func (m *WriteThroughManager) Set(key, value string) {
	m.db.Set(key, value)
	m.cache.Set(key, value)
}

// ── 4. Write-Behind Manager ─────────────────────────────────────────────────
var ErrBufferFull = errors.New("write buffer overflow: backpressure triggered")

type WriteBehindManager struct {
	db        Database
	cache     *CacheStore
	mu        sync.Mutex
	buffer    map[string]string
	maxBuffer int
	ctx       context.Context
	cancel    context.CancelFunc
	wg        sync.WaitGroup
}

func NewWriteBehindManager(db Database, cache *CacheStore, flushInterval time.Duration, maxBuffer int) *WriteBehindManager {
	ctx, cancel := context.WithCancel(context.Background())
	mgr := &WriteBehindManager{
		db:        db,
		cache:     cache,
		buffer:    make(map[string]string),
		maxBuffer: maxBuffer,
		ctx:       ctx,
		cancel:    cancel,
	}

	mgr.wg.Add(1)
	go mgr.worker(flushInterval)
	return mgr
}

func (m *WriteBehindManager) Set(key, value string) error {
	m.cache.Set(key, value) // миттєва доступність у кеші

	m.mu.Lock()
	defer m.mu.Unlock()

	if len(m.buffer) >= m.maxBuffer {
		return ErrBufferFull // захист оперативної пам'яті
	}

	m.buffer[key] = value // злиття мутацій в один запис
	return nil
}

func (m *WriteBehindManager) worker(interval time.Duration) {
	defer m.wg.Done()
	ticker := time.NewTicker(interval)
	defer ticker.Stop()

	for {
		select {
		case <-m.ctx.Done():
			m.flush()
			return
		case <-ticker.C:
			m.flush()
		}
	}
}

func (m *WriteBehindManager) flush() {
	m.mu.Lock()
	if len(m.buffer) == 0 {
		m.mu.Unlock()
		return
	}
	batch := m.buffer
	m.buffer = make(map[string]string)
	m.mu.Unlock()

	m.db.BatchSet(batch)
}

func (m *WriteBehindManager) Close() {
	m.cancel()
	m.wg.Wait() // гарантований злив буфера перед завершенням
}
```
:::

## Покроковий розбір механізмів і протоколів

### 1. Анатомія життєвого циклу Cache-Aside
У реалізації `CacheAsideManager` читання й запис навмисно розділені на прості незв'язані кроки:
- Під час читання операція `get()` робить швидку спробу пошуку в хеш-таблиці `CacheStore`. Якщо ключ знайдено, затримка становить менше 1 мкс. Якщо ключа немає, потік іде в базу (затримка 10 мс) і після отримання результату викликає `cache->set()`. Це означає, що кеш зберігає лише ті об'єкти, які **фактично запитуються клієнтами** (лінива ініціалізація), не витрачаючи пам'ять на холодні дані.
- Під час запису `update()` критично важливий порядок дій: спочатку запис у базу, потім `cache->del()`. Чому саме видалення, а не пряме оновлення `cache->set()`? Якщо два клієнти одночасно оновлюють один і той самий запис, мережева затримка може змінити порядок їхніх викликів до кешу. Прямий перезапис створить перманентну розсинхронізацію (у базі лишиться нове значення другого клієнта, а в кеші — старе значення першого). Видалення ж гарантує, що наступний читач примусово звернеться до бази даних і отримає канонічний стан.

### 2. Захист від лавинних навал через Singleflight у Read-Through
У високонавантажених системах промах на гарячому ключі може спричинити так звану «лавинну навалу» (Cache Stampede). Якщо термін дії ключа закінчився або кеш перезавантажився, тисячі паралельних потоків одночасно виявлять відсутність даних у пам'яті й одночасно надішлють тисячу ідентичних запитів до бази даних, паралізуючи дискову підсистему.

Клас `SingleflightGroup` повністю усуває цю проблему. Він відстежує активні запити в хеш-таблиці:
1. Перший потік, який звертається за ключем `K`, створює запис у мапі викликів `calls_` і запускає виконання важкого запиту до бази даних.
2. Усі наступні потоки, які приходять протягом тих 10 мілісекунд, поки база виконує вибірку, бачать наявність активного виклику й просто блокуються на `std::shared_future::get()` (або `sync.WaitGroup` у Go).
3. Коли перший потік отримує результат і зберігає його в кеш, результат автоматично розсилається всім очікуючим потокам. До бази вирушив рівно один запит замість сотень.

### 3. Коалесценція та математика ефективності у Write-Behind
Найбільша перевага патерну `WriteBehindManager` полягає в оптимізації дискового вводу-виводу шляхом злиття мутацій.

Погляньмо на математику навантаження. Припустімо, що потік оновлень популярного лічильника надходить із середньою інтенсивністю `R = 2000` записів на секунду. Якщо інтервал скидання буфера становить `T = 50` мс (0.05 с), кількість оновлень між двома скиданнями дорівнює:

```
N = R · T = 2000 · 0.05 = 100 записів
```

Якщо всі ці 100 записів стосуються 5 гарячих ключів (наприклад, лічильників переглядів топових статей):
- Без коалесценції база даних мусила б виконати 100 окремих `UPDATE`-запитів (100 дискових операцій).
- З коалесценцією хеш-таблиця `write_buffer_` перезаписує значення для кожного з 5 ключів локально в оперативній пам'яті.
- Фоновий воркер надсилає до бази рівно 5 оновлень у єдиній транзакції `batch_set()`.
- Дискове навантаження на базу скорочується у `100 / 5 = 20` разів, а затримка відповіді клієнту падає з 15 мс до менш ніж 0.1 мс.

### 4. Стратегія Write-Around: захист пам'яті від одноразових записів
Патерн Write-Around є важливою варіацією для сценаріїв із вираженою асиметрією трафіку. При звичайному Write-Through кожен збережений запис примусово дублюється в кеш. Якщо система виконує масовий імпорт мільйона записів або оновлення архівних логів, які не будуть запитуватися найближчим часом, прямий запис у кеш витіснить із пам'яті гарячі активні ключі користувачів (явище кеш-забруднення, англ. *cache pollution*).

У схемі Write-Around клієнт пише дані безпосередньо в базу даних, оминаючи кеш, і одночасно надсилає команду `DEL key` до кешу (якщо там був старий запис). Якщо ці дані згодом знадобляться для читання, перший запит через Cache-Aside або Read-Through ліниво підніме їх у пам'ять. Якщо ж до них більше ніхто не звернеться, оперативна пам'ять залишиться доступною для дійсно гарячого набору даних.

### 5. Стратегія Refresh-Ahead: передбачення закінчення TTL
Для критично важливих ключів із високим навантаженням навіть одиничний промах затримкою в 10 мс може викликати стрибок хвостової латентності (p99/p99.9). Стратегія Refresh-Ahead автоматизує оновлення даних до того, як закінчиться термін їхньої придатності.

Кеш відстежує історію звернень до кожного ключа. Якщо ключ має TTL 60 секунд, а звернення до нього фіксуються частіше ніж раз на 5 секунд, то при зверненні на 55-й секунді кеш негайно повертає клієнту поточне (ще дійсне) значення з пам'яті, а у фоновому потоці асинхронно відправляє виклик до бази даних на перезавантаження значення і скидання таймера TTL на наступні 60 секунд. Користувачі взагалі ніколи не стикаються з промахами та затримками дискового читання.

## Боротьба з конкуренцією блокувань: шардування кешу

У високонавантажених серверах, де кількість одночасних запитів сягає сотень тисяч на секунду, єдиний м'ютекс `std::shared_mutex` або `sync.RWMutex` навколо всієї хеш-таблиці кешу стає точкою жорсткої конкуренції (lock contention). Навіть операції читання зі спільним блокуванням призводять до постійної інвалідації кеш-ліній процесора через атомарні лічильники блокування (cache line bouncing між ядрами CPU).

Стандартним вирішенням цієї проблеми є **шардування кешу в пам'яті (Striped / Sharded Cache)**:
- Створюється масив із `N` незалежних слотів (секцій), де `N` зазвичай обирають як степінь двійки (наприклад, 64 або 256).
- Кожна секція має власну хеш-таблицю та власний незалежний м'ютекс.
- При кожному зверненні за ключем обчислюється хеш `H = hash(key)`, а номер цільової секції визначається швидкою бітовою маскою `shard_idx = H & (N - 1)`.

Завдяки цьому паралельні запити до різних ключів потрапляють у різні секції й виконуються на різних ядрах процесора повністю паралельно, без взаємного очікування на блокуваннях. Імовірність зіткнення двох запитів за одним м'ютексом зменшується рівно в `N` разів.

## Метрики моніторингу та телеметрія

Впровадження кешувальних стратегій у виробниче середовище вимагає постійного відстеження ключових показників продуктивності. Відсутність спостережливості перетворює кеш на чорну скриньку, де непомітна деградація може раптово покласти первинну базу даних.

Обов'язковий набір метрик включає:
1. **Частка влучань (Hit Ratio):** Відношення кількості влучань до загальної кількості запитів `hits / (hits + misses)`. Падіння цього показника нижче 90 % є першим сигналом про некоректний TTL, недостатній обсяг оперативної пам'яті або шкідливий наскрізний прохід (scan), що вимиває гарячі дані.
2. **Розмір черги та вік найстарішого запису у Write-Behind:** Лічильник незбережених об'єктів у буфері та час, протягом якого найстаріший запис очікує на скидання. Зростання цих величин свідчить про перевантаження бази даних або деградацію мережі.
3. **Хвостова затримка (p95 / p99 Latency):** Час відповіді на читання з кешу та час виконання операцій `db->get()` на промахах. Дозволяє виявити лавинні навали на базу та блокування окремих ключів.
4. **Кількість відхилених оновлень (Shedded Writes / Backpressure Events):** Лічильник помилок `ErrBufferFull`, що сигналізує про необхідність термінового масштабування первинного сховища або коригування лімітів буферизації.

## Підводні камені та пастки в продакшені

### Пастка 1: Неузгодженість при збої інвалідації (Dual-Write Failure)
У патерні Cache-Aside можлива ситуація, коли транзакція в базі даних успішно зафіксована, але по дорозі до кешу стається обрив мережевого з'єднання, вичерпання пулу підключень або аварійна зупинка процесу. У результаті старий ключ залишається в кеші.

**Як захиститися:**
- Кожен запис у кеш обов'язково повинен мати скінченний час життя (**TTL** — Time-To-Live, наприклад, 60 секунд). Навіть якщо подія інвалідації загубилася, неузгодженість буде автоматично виправлена після закінчення TTL.
- У критичних доменах (фінанси, білінг) інвалідацію переносять на рівень **Change Data Capture (CDC)**: демон вичитує журнал бінарних логів бази даних (WAL / binlog) і гарантовано публікує події видалення ключів у кеш через ідемпотентну чергу повідомлень.

### Пастка 2: Переповнення буфера та регулювання тиску (Backpressure)
Якщо первинна база даних тимчасово уповільнює обробку запитів або зазнає деградації, а клієнти продовжують інтенсивно писати у Write-Behind, буфер оновлень починає неконтрольовано зростати. Якщо черга необмежена, процес завершиться аварійно через брак пам'яті (OOM Killer).

**Як захиститися:**
- Завжди встановлювати ліміт розміру буфера `max_buffer_size`.
- При досягненні 80 % місткості застосовувати зворотний тиск: пригальмовувати вхідні клієнтські виклики (`sleep` або блокування на умовній змінній).
- При досягненні 100 % відхиляти нові операції з явною помилкою перевантаження (`ErrBufferFull`), змушуючи клієнтів застосовувати повторні спроби з експоненційним відкатом (Exponential Backoff).

### Пастка 3: Втрата даних при збої процесу у Write-Behind
Оскільки Write-Behind повертає клієнту успішну відповідь до того, як дані фізично збережено на диску бази даних, раптове знеструмлення сервера або аварійне завершення процесу призведе до безповоротної втрати всіх змін, які перебували в буфері пам'яті.

**Як захиститися:**
- Якщо втрата даних є неприпустимою, Write-Behind комбінують із попереднім записом у локальний append-only файл на NVMe-накопичувачі (Write-Ahead Log) або в реплікований брокер повідомлень (Apache Kafka) з підтвердженням від кворуму реплік перед поверненням `OK` клієнту.

### Пастка 4: Гонка застарілого запису на промаху (Stale Set Race)
Класична гонка виникає за такого збігу обставин:
1. Потік А читає ключ `K`, отримує промах у кеші й виконує `SELECT` із бази даних, отримуючи значення `v1`.
2. Потік Б оновлює ключ `K` у базі даних до значення `v2` і надсилає інвалідацію `DEL K` у кеш.
3. Потік А через високу затримку процесора чи мережі нарешті отримує керування й записує своє застаріле значення `cache->set(K, v1)`.

У результаті кеш містить старе значення `v1`, тоді як база даних містить `v2`.

**Як захиститися:**
- Використовувати **орендні токени (Lease Tokens)** або версіонування: кеш видає токен на завантаження; під час інвалідації всі раніше видані токени анулюються, і спроба запису застарілого токена відхиляється кеш-сервером.
- Використовувати короткий TTL для записів, створених на промаху.

### Пастка 5: Обробка часткових збоїв пакетного запису (Partial Batch Failure)
Під час скидання накопиченого буфера у Write-Behind база даних може повернути помилку для окремого запису (наприклад, порушення обмеження унікальності або зовнішнього ключа). Якщо вся пачка відхиляється, виникає дилема: відкинути всі 50 записів чи повторити спробу?

**Як захиститися:**
- Якщо пакетна транзакція зазнає невдачі, менеджер повинен переключитися на розгортання пачки в окремі одиничні запити, щоб ізолювати дефектний рядок, зафіксувати решту 49 успішних оновлень, а збійний запис відправити в спеціальну «мертву чергу» (Dead Letter Queue, DLQ) для ручного або автоматизованого розбору.

### 6. Інтеграція із запобіжниками (Circuit Breaker)
У разі повної недосяжності кешу (наприклад, аварія мережевого шлюзу або падіння вузла Redis) спроба надіслати тисячі запитів у зламаний сокет призведе до вичерпання пулу з'єднань і зависання клієнтських потоків на мережевих тайм-аутах.

Менеджери кешування на промисловому рівні обов'язково загортають у патерн **Circuit Breaker (запобіжник)**:
- Якщо протягом 5 секунд фіксується 10 помилок підключення до кешу поспіль, запобіжник переходить у стан «розімкнено» (*open*).
- Усі наступні операції читання та запису тимчасово оминають шар кешування, спрямовуючи запити безпосередньо в базу даних без спроб відкриття сокетів до кешу.
- Через 30 секунд запобіжник переходить у стан «напіврозімкнено» (*half-open*), пропускаючи один тестовий запит для перевірки відновлення вузла пам'яті. Це гарантує м'яку деградацію системи замість каскадного колапсу всього сервісу.

