#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <optional>
#include <random>
#include <format>
#include <memory>

enum class IncidentState {
    Triggered,
    Acknowledged,
    Escalated,
    Mitigated,
    Resolved
};

enum class Severity {
    Sev1 = 1,
    Sev2 = 2,
    Sev3 = 3,
    Sev4 = 4
};

struct OnCallEngineer {
    std::string name;
    std::string phone;
    std::string slack_handle;
};

struct TimelineEvent {
    std::chrono::system_clock::time_point timestamp;
    IncidentState state_snapshot;
    std::string message;
};

struct EscalationPolicy {
    std::vector<OnCallEngineer> tiers;
    std::chrono::seconds ack_timeout;
};

class IncidentOrchestrator {
public:
    IncidentOrchestrator(uint64_t id, std::string title, Severity sev, EscalationPolicy policy)
        : id_(id), title_(std::move(title)), severity_(sev), policy_(std::move(policy)),
          state_(IncidentState::Triggered), current_tier_(0), is_running_(true) {
        
        generate_new_token();
        
        append_timeline(std::format("Інцидент відкрито із критичністю SEV-{}. Призначено на Tier-1: {}",
                                    static_cast<int>(severity_), policy_.tiers.at(0).name));
        
        dispatch_pager(policy_.tiers.at(0));
        
        // Запуск потоку таймера ескалації
        timer_thread_ = std::jthread([this](std::stop_token st) {
            timer_worker(st);
        });
    }

    ~IncidentOrchestrator() {
        resolve("Знищення екземпляра оркестратора (автоматичне закриття)");
    }

    // Заборона копіювання, дозволено переміщення
    IncidentOrchestrator(const IncidentOrchestrator&) = delete;
    IncidentOrchestrator& operator=(const IncidentOrchestrator&) = delete;
    IncidentOrchestrator(IncidentOrchestrator&&) = delete;
    IncidentOrchestrator& operator=(IncidentOrchestrator&&) = delete;

    bool acknowledge(uint32_t token, const std::string& responder_name) {
        std::unique_lock lock(mutex_);
        
        if (state_ != IncidentState::Triggered && state_ != IncidentState::Escalated) {
            return false;
        }

        if (token != current_token_) {
            append_timeline_locked(std::format("Відхилено ACK від {}: недійсний токен {}", responder_name, token));
            return false;
        }

        state_ = IncidentState::Acknowledged;
        append_timeline_locked(std::format("Інцидент підтверджено черговим {} (рівень Tier-{}). Таймер зупинено.",
                                           responder_name, current_tier_ + 1));
        
        cv_.notify_all();
        return true;
    }

    bool mitigate(const std::string& action_taken) {
        std::unique_lock lock(mutex_);
        
        if (state_ != IncidentState::Acknowledged) {
            return false;
        }

        state_ = IncidentState::Mitigated;
        append_timeline_locked(std::format("Вплив на користувачів усунуто: {}. Початок стабілізаційного періоду.", action_taken));
        
        cv_.notify_all();
        return true;
    }

    void resolve(const std::string& resolution_summary) {
        {
            std::unique_lock lock(mutex_);
            if (state_ == IncidentState::Resolved) {
                return;
            }
            state_ = IncidentState::Resolved;
            is_running_ = false;
            append_timeline_locked(std::format("Інцидент успішно закрито: {}. Матеріали передано на постмортем.", resolution_summary));
        }
        
        cv_.notify_all();
        if (timer_thread_.joinable()) {
            timer_thread_.request_stop();
        }
    }

    [[nodiscard]] IncidentState get_state() const {
        std::lock_guard lock(mutex_);
        return state_;
    }

private:
    void generate_new_token() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_int_distribution<uint32_t> dist(100000, 999999);
        current_token_ = dist(gen);
    }

    void dispatch_pager(const OnCallEngineer& eng) {
        std::cout << std::format(">>> PAGER ALERT >>> Дзвінок/SMS на {} ({}): [SEV-{}] {}. Введіть токен {} для ACK.\n",
                                 eng.phone, eng.name, static_cast<int>(severity_), title_, current_token_);
    }

    void append_timeline(const std::string& msg) {
        std::lock_guard lock(mutex_);
        append_timeline_locked(msg);
    }

    void append_timeline_locked(const std::string& msg) {
        auto now = std::chrono::system_clock::now();
        timeline_.push_back({now, state_, msg});
        
        auto epoch_ms = std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count();
        std::cout << std::format("[{} ms] [INC-{}] [{}] {}\n",
                                 epoch_ms, id_, state_to_string(state_), msg);
    }

    static std::string state_to_string(IncidentState s) {
        switch (s) {
            case IncidentState::Triggered:    return "TRIGGERED";
            case IncidentState::Acknowledged: return "ACKNOWLEDGED";
            case IncidentState::Escalated:    return "ESCALATED";
            case IncidentState::Mitigated:    return "MITIGATED";
            case IncidentState::Resolved:     return "RESOLVED";
            default:                          return "UNKNOWN";
        }
    }

    void timer_worker(std::stop_token st) {
        while (!st.stop_requested()) {
            std::unique_lock lock(mutex_);

            cv_.wait(lock, [this, &st] {
                return st.stop_requested() || !is_running_ || 
                       state_ == IncidentState::Triggered || 
                       state_ == IncidentState::Escalated;
            });

            if (st.stop_requested() || !is_running_ || 
                (state_ != IncidentState::Triggered && state_ != IncidentState::Escalated)) {
                continue;
            }

            // Очікування тайм-ауту дедлайну або сигналу зміни стану
            bool acknowledged_in_time = cv_.wait_for(lock, policy_.ack_timeout, [this, &st] {
                return st.stop_requested() || !is_running_ || 
                       state_ != IncidentState::Triggered && state_ != IncidentState::Escalated;
            });

            if (st.stop_requested() || !is_running_) {
                break;
            }

            if (!acknowledged_in_time) {
                // Тайм-аут вичерпано — проводимо ескалацію
                append_timeline_locked(std::format("Дедлайн підтвердження ({} сек) вичерпано на рівні Tier-{} ({})",
                                                   policy_.ack_timeout.count(), current_tier_ + 1,
                                                   policy_.tiers.at(current_tier_).name));

                if (current_tier_ + 1 < policy_.tiers.size()) {
                    current_tier_++;
                    state_ = IncidentState::Escalated;
                    generate_new_token();

                    append_timeline_locked(std::format("Ескалація на рівень Tier-{}: черговий {}",
                                                       current_tier_ + 1, policy_.tiers.at(current_tier_).name));
                    dispatch_pager(policy_.tiers.at(current_tier_));
                } else {
                    append_timeline_locked("КРИТИЧНО: Усі рівні ескалації вичерпані! Аварійний broadcast на Incident Commander.");
                    is_running_ = false;
                    break;
                }
            }
        }
    }

    const uint64_t id_;
    const std::string title_;
    const Severity severity_;
    const EscalationPolicy policy_;

    IncidentState state_;
    size_t current_tier_;
    uint32_t current_token_{0};
    bool is_running_;

    std::vector<TimelineEvent> timeline_;
    mutable std::mutex mutex_;
    std::condition_variable cv_;
    std::jthread timer_thread_;
};
