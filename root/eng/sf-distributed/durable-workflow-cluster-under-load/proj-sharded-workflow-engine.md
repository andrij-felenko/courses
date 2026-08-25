# ⚙️ Шардований рушій довговічного виконання з Continue-As-New та ієрархічними таймерами

Практична реалізація ядра шардованого рушія довговічного виконання (Durable Execution Engine), що демонструє горизонтальний розподіл процесів за стабільним хешуванням, атомарне відсікання історії через `Continue-As-New` та квантування розподілених таймерів через двоповерхове колесо таймерів (Timer Wheel).

## Архітектурна задача та механізм роботи

Розробка промислового рушія довговічного виконання на масштабі вимагає вирішення трьох фундаментальних проблем розподілених обчислень:

### 1. Горизонтальний шардинг без спільних блокувань

У системі з десятками мільйонів активних процесів утримання єдиної глобальної черги або глобального блокування призводить до миттєвого колапсу пропускної здатності. Рушій розділяє простір ідентифікаторів `WorkflowID` на фіксовану кількість логічних шардів (наприклад, 4096 шардів у промислових кластерах).

Кожен шард є повністю автономною одиницею обчислення, що володіє:
* Власним потоком обробки та м'ютексом синхронізації.
* Локальним кешем детермінованих станів процесів (LRU Cache).
* Власним екземпляром ієрархічного колеса таймерів.

Маршрутизація вхідних запитів (`StartWorkflow`, `Signal`, `Query`) здійснюється детерміновано за формулою `ShardID = Hash(WorkflowID) % TotalShards`. Це гарантує, що всі операції над одним процесом завжди потрапляють на той самий шард і виконуються строго послідовно без потреби у розподілених блокуваннях (Distributed Locks).

### 2. Запобігання вибуху історії (Continue-As-New)

Якщо робочий процес працює місяцями (наприклад, сутність банківського рахунку чи IoT-пристрою), журнал подій безперервно зростає. При досягненні системного порогу подій (Compaction Threshold) шард ініціює команду `Continue-As-New`.

Механізм переходу складається з чотирьох кроків:
1. Поточний запуск процесу (`RunID`) фіксує фінальну подію `ContinuedAsNew` та позначається як закритий.
2. Поточні значення бізнес-змінних (наприклад, баланс рахунку) упаковуються в компактний JSON-знімок.
3. Створюється новий запуск процесу з новим `RunID`, але тим самим `WorkflowID`.
4. Новий запуск отримує чистий журнал, де першою подією є `WorkflowStarted` із переданим знімком стану. Усі нерозглянуті вхідні сигнали атомарно переносяться в новий журнал.

### 3. Ієрархічне квантування таймерів (Timer Wheel)

Замість важких SQL-запитів виду `SELECT ... WHERE fire_time <= NOW()` шард організовує таймери у вигляді ієрархічного колеса. Колесо має два рівні дискретизації:
* **Секундне колесо:** 60 слотів (0..59 сек). Кожен тік таймера просуває вказівник на один слот і миттєво витягує всі готові задачі.
* **Хвилинне колесо:** 60 слотів (0..59 хв). Коли секундне колесо завершує повний оберт (секунда 0), задачі з поточного хвилинного слота каскадно пересипаються у відповідні слоти секундного колеса.

Це забезпечує константну часову складність `O(1)` для операцій планування та перевірки таймерів незалежно від кількості запланованих подій.

## Реалізація шардованого рушія

:::tabs
```cpp
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <memory>
#include <mutex>
#include <chrono>
#include <functional>
#include <optional>
#include <cstdint>

// ── Типи подій журналу ──────────────────────────────────────────────────
enum class EventType {
    WorkflowStarted,
    ActivityScheduled,
    ActivityCompleted,
    TimerStarted,
    TimerFired,
    WorkflowSignaled,
    ContinuedAsNew
};

struct HistoryEvent {
    int64_t event_id;
    EventType type;
    std::string name;
    std::string payload;
};

// ── Стан довговічного процесу ───────────────────────────────────────────
struct WorkflowExecution {
    std::string workflow_id;
    std::string run_id;
    int64_t current_balance{0};
    int64_t processed_events_count{0};
    std::vector<HistoryEvent> history;
    bool is_closed{false};
};

// ── Дворівневе ієрархічне колесо таймерів (Timer Wheel) ────────────────
struct TimerEntry {
    std::string workflow_id;
    int64_t delay_seconds;
    std::function<void()> callback;
};

class HierarchicalTimerWheel {
public:
    static constexpr size_t SECONDS_SLOTS = 60;
    static constexpr size_t MINUTES_SLOTS = 60;

    HierarchicalTimerWheel() 
        : current_second_(0), current_minute_(0),
          second_wheel_(SECONDS_SLOTS), minute_wheel_(MINUTES_SLOTS) {}

    void schedule_timer(const std::string& workflow_id, int64_t seconds_from_now, std::function<void()> cb) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (seconds_from_now < static_cast<int64_t>(SECONDS_SLOTS)) {
            size_t target_slot = (current_second_ + seconds_from_now) % SECONDS_SLOTS;
            second_wheel_[target_slot].push_back({workflow_id, seconds_from_now, std::move(cb)});
        } else {
            int64_t minutes = seconds_from_now / 60;
            size_t target_slot = (current_minute_ + minutes) % MINUTES_SLOTS;
            minute_wheel_[target_slot].push_back({workflow_id, seconds_from_now, std::move(cb)});
        }
    }

    void advance_second(std::vector<std::function<void()>>& ready_callbacks) {
        std::lock_guard<std::mutex> lock(mutex_);
        current_second_ = (current_second_ + 1) % SECONDS_SLOTS;

        // Виконання готових таймерів із секундного колеса
        auto& active_bucket = second_wheel_[current_second_];
        for (auto& entry : active_bucket) {
            ready_callbacks.push_back(std::move(entry.callback));
        }
        active_bucket.clear();

        // На кожній секунді 0 каскадуємо з хвилинного колеса
        if (current_second_ == 0) {
            current_minute_ = (current_minute_ + 1) % MINUTES_SLOTS;
            auto& minute_bucket = minute_wheel_[current_minute_];
            for (auto& entry : minute_bucket) {
                int64_t remaining_sec = entry.delay_seconds % 60;
                second_wheel_[remaining_sec].push_back(std::move(entry));
            }
            minute_bucket.clear();
        }
    }

private:
    std::mutex mutex_;
    size_t current_second_;
    size_t current_minute_;
    std::vector<std::vector<TimerEntry>> second_wheel_;
    std::vector<std::vector<TimerEntry>> minute_wheel_;
};

// ── Логічний шард сервісу історії ───────────────────────────────────────
class HistoryShard {
public:
    explicit HistoryShard(uint32_t shard_id, size_t history_compaction_threshold = 10)
        : shard_id_(shard_id), compaction_threshold_(history_compaction_threshold) {}

    void execute_signal(const std::string& workflow_id, int64_t amount) {
        std::lock_guard<std::mutex> lock(shard_mutex_);
        auto& wf = get_or_create_execution(workflow_id);

        if (wf.is_closed) {
            std::cout << "[Шард #" << shard_id_ << "] Процес " << workflow_id << " завершено.\n";
            return;
        }

        // Запис події сигналу в журнал історії
        int64_t next_id = static_cast<int64_t>(wf.history.size()) + 1;
        wf.history.push_back({next_id, EventType::WorkflowSignaled, "DepositSignal", std::to_string(amount)});
        wf.current_balance += amount;
        wf.processed_events_count++;

        std::cout << "[Шард #" << shard_id_ << "] Процес " << workflow_id 
                  << " (Run: " << wf.run_id << "): поповнення на " << amount 
                  << " грн. Баланс: " << wf.current_balance 
                  << " | Подій в історії: " << wf.history.size() << "\n";

        // Перевірка необхідності Continue-As-New
        if (wf.history.size() >= compaction_threshold_) {
            trigger_continue_as_new(wf);
        }
    }

    HierarchicalTimerWheel& timer_wheel() { return timer_wheel_; }

private:
    WorkflowExecution& get_or_create_execution(const std::string& workflow_id) {
        auto it = executions_.find(workflow_id);
        if (it == executions_.end()) {
            WorkflowExecution new_wf;
            new_wf.workflow_id = workflow_id;
            new_wf.run_id = "run_001";
            new_wf.history.push_back({1, EventType::WorkflowStarted, "Onboarding", "{}"});
            auto [inserted, _] = executions_.emplace(workflow_id, std::move(new_wf));
            return inserted->second;
        }
        return it->second;
    }

    void trigger_continue_as_new(WorkflowExecution& old_wf) {
        std::cout << ">>> [Шард #" << shard_id_ << "] Відсікання історії для " 
                  << old_wf.workflow_id << " (досягнуто ліміт " << compaction_threshold_ << " подій) <<<\n";

        // Фіксуємо подію в старому запуску
        old_wf.history.push_back({static_cast<int64_t>(old_wf.history.size()) + 1, 
                                  EventType::ContinuedAsNew, "ContinueAsNew", ""});
        old_wf.is_closed = true;

        // Створюємо новий запуск із перенесенням накопиченого балансу (знімок стану)
        WorkflowExecution new_wf;
        new_wf.workflow_id = old_wf.workflow_id;
        static int run_counter = 2;
        new_wf.run_id = "run_00" + std::to_string(run_counter++);
        new_wf.current_balance = old_wf.current_balance;
        new_wf.processed_events_count = 0;

        // Нова історія починається з чистого аркуша зі знімком
        new_wf.history.push_back({1, EventType::WorkflowStarted, "Onboarding", 
                                  "{\"snapshot_balance\":" + std::to_string(old_wf.current_balance) + "}"});

        executions_[old_wf.workflow_id] = std::move(new_wf);
        std::cout << "[Шард #" << shard_id_ << "] Новий запуск " << executions_[old_wf.workflow_id].run_id 
                  << " стартував із чистим журналом (1 подія).\n";
    }

    uint32_t shard_id_;
    size_t compaction_threshold_;
    std::mutex shard_mutex_;
    std::unordered_map<std::string, WorkflowExecution> executions_;
    HierarchicalTimerWheel timer_wheel_;
};

// ── Кластер оркестратора зі стабільним хешуванням ──────────────────────
class DurableCluster {
public:
    explicit DurableCluster(size_t num_shards = 4) : num_shards_(num_shards) {
        for (size_t i = 0; i < num_shards_; ++i) {
            shards_.push_back(std::make_unique<HistoryShard>(static_cast<uint32_t>(i)));
        }
    }

    void send_signal(const std::string& workflow_id, int64_t amount) {
        size_t shard_index = hash_workflow_id(workflow_id) % num_shards_;
        shards_[shard_index]->execute_signal(workflow_id, amount);
    }

    void schedule_timer(const std::string& workflow_id, int64_t delay_seconds, std::function<void()> cb) {
        size_t shard_index = hash_workflow_id(workflow_id) % num_shards_;
        shards_[shard_index]->timer_wheel().schedule_timer(workflow_id, delay_seconds, std::move(cb));
    }

    void tick_all_shards() {
        std::vector<std::function<void()>> callbacks;
        for (auto& shard : shards_) {
            shard->timer_wheel().advance_second(callbacks);
        }
        for (auto& cb : callbacks) {
            cb();
        }
    }

private:
    static size_t hash_workflow_id(const std::string& id) {
        // Простий хеш FNV-1a для детермінованої маршрутизації
        size_t hash = 14695981039346656037ULL;
        for (char c : id) {
            hash ^= static_cast<size_t>(c);
            hash *= 1099511628211ULL;
        }
        return hash;
    }

    size_t num_shards_;
    std::vector<std::unique_ptr<HistoryShard>> shards_;
};

int main() {
    DurableCluster cluster(4);

    std::cout << "=== Симуляція довговічного процесу з 12 сигналами ===\n";
    // Процес user_101 отримує 12 сигналів (поріг відсікання = 10 подій)
    for (int i = 1; i <= 12; ++i) {
        cluster.send_signal("user_101", 100);
    }

    std::cout << "\n=== Реєстрація таймера через ієрархічне колесо ===\n";
    cluster.schedule_timer("user_101", 3, []() {
        std::cout << "[Таймер] Спрацював трисекундний таймер нарахування бонусів!\n";
    });

    // Емуляція 4 секундних тіків
    for (int s = 1; s <= 4; ++s) {
        std::cout << "Тік годинника: " << s << " сек...\n";
        cluster.tick_all_shards();
    }

    return 0;
}
```
```go
package main

import (
	"fmt"
	"hash/fnv"
	"sync"
)

type EventType int

const (
	WorkflowStarted EventType = iota
	WorkflowSignaled
	ContinuedAsNew
)

type HistoryEvent struct {
	EventID int64
	Type    EventType
	Name    string
	Payload string
}

type WorkflowExecution struct {
	WorkflowID     string
	RunID          string
	CurrentBalance int64
	History        []HistoryEvent
	IsClosed       bool
}

type HistoryShard struct {
	ShardID             uint32
	CompactionThreshold int
	Mu                  sync.Mutex
	Executions          map[string]*WorkflowExecution
}

func NewHistoryShard(id uint32, threshold int) *HistoryShard {
	return &HistoryShard{
		ShardID:             id,
		CompactionThreshold: threshold,
		Executions:          make(map[string]*WorkflowExecution),
	}
}

func (s *HistoryShard) ExecuteSignal(workflowID string, amount int64) {
	s.Mu.Lock()
	defer s.Mu.Unlock()

	wf, exists := s.Executions[workflowID]
	if !exists {
		wf = &WorkflowExecution{
			WorkflowID:     workflowID,
			RunID:          "run_001",
			CurrentBalance: 0,
			History: []HistoryEvent{
				{EventID: 1, Type: WorkflowStarted, Name: "Onboarding", Payload: "{}"},
			},
		}
		s.Executions[workflowID] = wf
	}

	if wf.IsClosed {
		return
	}

	wf.History = append(wf.History, HistoryEvent{
		EventID: int64(len(wf.History) + 1),
		Type:    WorkflowSignaled,
		Name:    "DepositSignal",
		Payload: fmt.Sprintf("%d", amount),
	})
	wf.CurrentBalance += amount

	fmt.Printf("[Шард #%d] %s (Run: %s): +%d грн. Баланс: %d | Історія: %d подій\n",
		s.ShardID, wf.WorkflowID, wf.RunID, amount, wf.CurrentBalance, len(wf.History))

	if len(wf.History) >= s.CompactionThreshold {
		fmt.Printf(">>> [Шард #%d] Відсікання Continue-As-New для %s <<<\n", s.ShardID, wf.WorkflowID)
		wf.IsClosed = true

		newWf := &WorkflowExecution{
			WorkflowID:     wf.WorkflowID,
			RunID:          "run_002",
			CurrentBalance: wf.CurrentBalance,
			History: []HistoryEvent{
				{EventID: 1, Type: WorkflowStarted, Name: "Onboarding", Payload: fmt.Sprintf("{\"balance\":%d}", wf.CurrentBalance)},
			},
		}
		s.Executions[workflowID] = newWf
	}
}

type DurableCluster struct {
	NumShards uint32
	Shards    []*HistoryShard
}

func NewDurableCluster(numShards uint32) *DurableCluster {
	shards := make([]*HistoryShard, numShards)
	for i := uint32(0); i < numShards; i++ {
		shards[i] = NewHistoryShard(i, 10)
	}
	return &DurableCluster{NumShards: numShards, Shards: shards}
}

func (c *DurableCluster) SendSignal(workflowID string, amount int64) {
	h := fnv.New32a()
	h.Write([]byte(workflowID))
	shardIdx := h.Sum32() % c.NumShards
	c.Shards[shardIdx].ExecuteSignal(workflowID, amount)
}

func main() {
	cluster := NewDurableCluster(4)
	for i := 1; i <= 12; i++ {
		cluster.SendSignal("user_101", 100)
	}
}
```
:::

## Покроковий розбір виконання

Під час запуску програми відбувається наступна послідовність дій:

1. **Ініціалізація кластера:** Створюється екземпляр `DurableCluster` із 4 логічними шардами.
2. **Маршрутизація сигналів:** Процес `user_101` через хеш FNV-1a однозначно закріплюється за одним конкретним шардом (наприклад, Шард #2). Усі наступні сигнали надсилаються виключно в цей шард.
3. **Накопичення історії:** Перші 9 сигналів збільшують баланс та додають події до `run_001`.
4. **Спрацювання Continue-As-New:** На 10-й події розмір журналу досягає `compaction_threshold = 10`. Шард маркує `run_001` закритим, серіалізує накопичений баланс (900 грн) і створює `run_002` із чистим журналом з однієї події.
5. **Продовження роботи:** Наступні сигнали 11 та 12 потрапляють уже в новий журнал `run_002`, зберігаючи загальний баланс без втрати даних та без навантаження на Replay.
6. **Робота таймера:** Запланований на 3 секунди таймер потрапляє у 3-й слот секундного колеса і точно на 3-му тіку викликає зареєстрований колбек.

## Аналіз крайових випадків та пасток реалізації

При перенесенні наведеного прототипу у високопродуктивне виробниче середовище виникають чотири критичні інженерні виклики:

### 1. Гонка сигналів під час переходу Continue-As-New

Якщо зовнішній сигнал надходить у проміжку між викликом `ContinueAsNew` та завершенням транзакції запису нового запуску в базу даних:
* **Небезпека:** сигнал може бути відкинутий як такий, що надісланий у закритий `run_001`, або загублений.
* **Рішення:** шард утримує блокування на рівні `WorkflowID` протягом усього циклу створення нового запуску. Усі вхідні сигнали буферизуються в тимчасовій черзі шарду й атомарно записуються у журнал `run_002` безпосередньо після події `WorkflowStarted`.

### 2. Втрата таймерів при зміні лідера шарду (Failover)

Якщо вузол кластера зазнає аварійного перезавантаження, інший сервер підхоплює управління шардом:
* **Небезпека:** стан коліс таймерів в оперативній пам'яті втрачається.
* **Рішення:** таймери завжди зберігаються у персистентній таблиці `timer_tasks` із діапазонним індексом за часом. При старті новий вузол вичитує діапазон `[NOW, NOW + 1 hour]` і відновлює секундні та хвилинні бакети в пам'яті.

### 3. Дрейф системного годинника (NTP Clock Drift)

При коригуванні часу сервером через протокол NTP системний годинник може стрибнути назад або вперед:
* **Небезпека:** таймери спрацюють передчасно або пропустять свій слот.
* **Рішення:** просування коліс таймерів прив'язується виключно до монотонного годинника операційної системи (`std::chrono::steady_clock` або `CLOCK_MONOTONIC_RAW`), який гарантує неперервний рух уперед без стрибків.

### 4. Вимивання пам'яті при мільйонах сплячих процесів (OOM)

Якщо в пам'яті шарду зберігати всі процеси, система вичерпає оперативну пам'ять:
* **Рішення:** структура `executions_` перетворюється на фіксований LRU-кеш (наприклад, 10 000 найбільш активних процесів). Неактивні сплячі процеси вивантажуються з пам'яті і підвантажуються з диска лише при надходженні нового сигналу чи спрацюванні таймера.
