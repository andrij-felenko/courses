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
