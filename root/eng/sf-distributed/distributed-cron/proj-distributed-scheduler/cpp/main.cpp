#include <iostream>
#include <vector>
#include <memory>
#include <string>
#include <string_view>
#include <chrono>
#include <cstdint>
#include <expected>

namespace cron {

using Seconds = std::chrono::seconds;
using SystemTime = std::chrono::system_clock::time_point;

struct CronTask {
    uint64_t job_id;
    std::string name;
    Seconds interval;
    SystemTime next_run;
    uint32_t remaining_rounds{0};
};

struct TriggerEvent {
    uint64_t job_id;
    std::string name;
    SystemTime scheduled_time;
    uint64_t fencing_epoch;
};

enum class DispatchError {
    LeaseExpired,
    StaleFencingToken
};

/* Стан воркера з підтримкою огорожі */
class WorkerFencingGuard {
public:
    std::expected<void, DispatchError> validate_and_record(uint64_t epoch) noexcept {
        if (epoch < highest_seen_epoch_) {
            return std::unexpected(DispatchError::StaleFencingToken);
        }
        highest_seen_epoch_ = epoch;
        return {};
    }

    [[nodiscard]] uint64_t highest_seen_epoch() const noexcept {
        return highest_seen_epoch_;
    }

private:
    uint64_t highest_seen_epoch_{0};
};

/* Обгортка лізи шарду з перевіркою часу (RAII) */
class ShardLease {
public:
    ShardLease(uint32_t shard_id, uint64_t epoch, SystemTime deadline) noexcept
        : shard_id_(shard_id), epoch_(epoch), deadline_(deadline), active_(true) {}

    [[nodiscard]] bool is_valid(SystemTime current_time) const noexcept {
        return active_ && (current_time <= deadline_);
    }

    [[nodiscard]] uint64_t epoch() const noexcept { return epoch_; }
    [[nodiscard]] uint32_t shard_id() const noexcept { return shard_id_; }

    void invalidate() noexcept { active_ = false; }

private:
    uint32_t shard_id_;
    uint64_t epoch_;
    SystemTime deadline_;
    bool active_;
};

/* Ієрархічне часове колесо */
class TimingWheel {
public:
    static constexpr size_t SlotsCount = 60;
    static constexpr Seconds TickDuration{1};

    explicit TimingWheel(SystemTime start_time)
        : current_time_(start_time), current_slot_(0), slots_(SlotsCount) {}

    void add_task(std::unique_ptr<CronTask> task) {
        auto delay = std::chrono::duration_cast<Seconds>(task->next_run - current_time_).count();
        if (delay < 0) delay = 0;

        auto ticks = static_cast<uint64_t>(delay) / TickDuration.count();
        task->remaining_rounds = static_cast<uint32_t>(ticks / SlotsCount);
        size_t target_slot = (current_slot_ + ticks) % SlotsCount;

        slots_[target_slot].push_back(std::move(task));
    }

    void tick(const ShardLease& lease, WorkerFencingGuard& worker) {
        current_time_ += TickDuration;
        current_slot_ = (current_slot_ + 1) % SlotsCount;

        if (!lease.is_valid(current_time_)) {
            std::cout << "[WARN] Ліза шарду " << lease.shard_id() << " недійсна! Пропуск диспатчу.\n";
            return;
        }

        auto& bucket = slots_[current_slot_];
        std::vector<std::unique_ptr<CronTask>> rearm_list;

        for (auto it = bucket.begin(); it != bucket.end();) {
            if ((*it)->remaining_rounds > 0) {
                (*it)->remaining_rounds--;
                ++it;
            } else {
                auto task = std::move(*it);
                it = bucket.erase(it);

                // Відправляємо тригер
                dispatch(TriggerEvent{
                    .job_id = task->job_id,
                    .name = task->name,
                    .scheduled_time = current_time_,
                    .fencing_epoch = lease.epoch()
                }, worker);

                // Оновлюємо розклад для наступного спрацьовування
                task->next_run = current_time_ + task->interval;
                rearm_list.push_back(std::move(task));
            }
        }

        for (auto& task : rearm_list) {
            add_task(std::move(task));
        }
    }

private:
    void dispatch(const TriggerEvent& ev, WorkerFencingGuard& worker) {
        std::cout << "[DISPATCH C++] Задача ID=" << ev.job_id << " ('" << ev.name
                  << "'), Епоха=" << ev.fencing_epoch << "\n";

        auto res = worker.validate_and_record(ev.fencing_epoch);
        if (!res.has_value()) {
            std::cout << "  [ВОРКЕР: ВІДХИЛЕНО] Токен огорожі застарів! ("
                      << ev.fencing_epoch << " < " << worker.highest_seen_epoch() << ")\n";
        } else {
            std::cout << "  [ВОРКЕР: ПРИЙНЯТО] Успішна обробка задачі.\n";
        }
    }

    SystemTime current_time_;
    size_t current_slot_;
    std::vector<std::vector<std::unique_ptr<CronTask>>> slots_;
};

} // namespace cron

int main() {
    using namespace std::chrono_literals;
    auto now = std::chrono::system_clock::now();

    cron::TimingWheel wheel(now);
    cron::ShardLease lease(1, 200, now + 10s);
    cron::WorkerFencingGuard worker;

    auto t1 = std::make_unique<cron::CronTask>();
    t1->job_id = 501;
    t1->name = "Analytics Aggregation";
    t1->interval = 2s;
    t1->next_run = now + 2s;

    auto t2 = std::make_unique<cron::CronTask>();
    t2->job_id = 502;
    t2->name = "Cache Invalidation";
    t2->interval = 4s;
    t2->next_run = now + 4s;

    wheel.add_task(std::move(t1));
    wheel.add_task(std::move(t2));

    std::cout << "=== СТАРТ СИМУЛЯЦІЇ C++ ПЛАНУВАЛЬНИКА ===\n";
    for (int i = 1; i <= 5; ++i) {
        std::cout << "\n--- Тік " << i << " с ---\n";
        wheel.tick(lease, worker);
    }

    std::cout << "\n=== ТЕСТ ЗОМБІ-СИГНАЛУ ЗІ СТАРОЮ ЕПОХОЮ ===\n";
    // Імітуємо оновлення епохи іншим планувальником
    static_cast<void>(worker.validate_and_record(201));

    // Спроба відправити подію зі старою епохою 200
    cron::TriggerEvent stale_event{
        .job_id = 501,
        .name = "Analytics Aggregation",
        .scheduled_time = now + 6s,
        .fencing_epoch = 200
    };
    auto check = worker.validate_and_record(stale_event.fencing_epoch);
    if (!check.has_value()) {
        std::cout << "Токен 200 відкинуто успішно: безпеку даних збережено.\n";
    }

    return 0;
}
