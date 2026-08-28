#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <memory>
#include <chrono>
#include <future>
#include <functional>
#include <unordered_map>
#include <mutex>
#include <sstream>
#include <iomanip>
#include <expected>
#include <optional>

// ── 1. Моделі даних та діагностичний конверт карантину ───────────────────────

enum class MessageStatus {
    Quarantined,
    UnderReview,
    Mutated,
    Replayed,
    Discarded
};

enum class FailureCategory {
    Transient,           // Мережевий таймаут, блокування БД -> Повтор (Retry)
    DeterministicPoison, // Зламана схема, бізнес-інваріант -> Миттєвий карантин
    ResourceExhaustion,  // Таймаут CPU, ReDoS, зависання -> Карантин
    PanicOrCrash         // Необроблений виняток / паніка -> Карантин
};

struct IngressMessage {
    std::string id;
    std::string partition_key;
    std::string payload;
    int delivery_count{1};
    int64_t timestamp_ms{0};
};

struct QuarantineEnvelope {
    std::string quarantine_id;
    std::string original_message_id;
    std::string partition_key;
    std::string original_payload;
    std::string mutated_payload;
    std::string failure_reason;
    std::string exception_details;
    FailureCategory category;
    MessageStatus status;
    int delivery_attempts;
    int64_t quarantined_at_ms;
    std::string host_identity;
};

// ── 2. Сховище карантину (Quarantine Repository) ────────────────────────────

class QuarantineRepository {
public:
    void save(const QuarantineEnvelope& env) {
        std::lock_guard<std::mutex> lock(mutex_);
        store_[env.quarantine_id] = env;
        std::cout << "[QUARANTINE-STORE] Збережено в карантин ID=" << env.quarantine_id 
                  << " для MessageID=" << env.original_message_id 
                  << " (Причина: " << env.failure_reason << ")\n";
    }

    std::optional<QuarantineEnvelope> get(const std::string& qid) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = store_.find(qid);
        if (it != store_.end()) return it->second;
        return std::nullopt;
    }

    void update(const QuarantineEnvelope& env) {
        std::lock_guard<std::mutex> lock(mutex_);
        store_[env.quarantine_id] = env;
    }

    std::vector<QuarantineEnvelope> list_active() {
        std::lock_guard<std::mutex> lock(mutex_);
        std::vector<QuarantineEnvelope> res;
        for (const auto& [_, env] : store_) {
            if (env.status == MessageStatus::Quarantined || env.status == MessageStatus::UnderReview) {
                res.push_back(env);
            }
        }
        return res;
    }

private:
    std::unordered_map<std::string, QuarantineEnvelope> store_;
    std::mutex mutex_;
};

// ── 3. Сторожовий супервізор виконання (Execution Supervisor) ───────────────

class ExecutionSupervisor {
public:
    using Handler = std::function<std::expected<void, std::string>(const IngressMessage&)>;

    static std::expected<void, std::pair<FailureCategory, std::string>>
    execute_with_watchdog(const IngressMessage& msg, Handler handler, std::chrono::milliseconds timeout) {
        auto task = std::packaged_task<std::expected<void, std::string>()>([&]() {
            try {
                return handler(msg);
            } catch (const std::exception& ex) {
                return std::unexpected(std::string("Unhandled exception: ") + ex.what());
            } catch (...) {
                return std::unexpected(std::string("Fatal unknown crash/panic caught"));
            }
        });

        auto future = task.get_future();
        std::thread worker_thread(std::move(task));

        if (future.wait_for(timeout) == std::future_status::timeout) {
            // Таймаут обробки: отруйне повідомлення викликало зависання або DoS
            worker_thread.detach(); // Від'єднуємо завислий потік
            return std::unexpected(std::make_pair(
                FailureCategory::ResourceExhaustion,
                "Watchdog deadline exceeded: CPU lockup or infinite loop detected"
            ));
        }

        worker_thread.join();
        auto result = future.get();

        if (result.has_value()) {
            return {};
        }

        std::string err = result.error();
        if (err.find("Schema") != std::string::npos || err.find("Invariant") != std::string::npos) {
            return std::unexpected(std::make_pair(FailureCategory::DeterministicPoison, err));
        }
        if (err.find("crash") != std::string::npos || err.find("exception") != std::string::npos) {
            return std::unexpected(std::make_pair(FailureCategory::PanicOrCrash, err));
        }

        return std::unexpected(std::make_pair(FailureCategory::Transient, err));
    }
};

// ── 4. Головний процесор черги з карантинним контуром ────────────────────────

class ResilientConsumer {
public:
    ResilientConsumer(std::shared_ptr<QuarantineRepository> repo, int max_retries = 3)
        : repo_(std::move(repo)), max_retries_(max_retries) {}

    bool process_message(const IngressMessage& msg, ExecutionSupervisor::Handler handler) {
        constexpr auto WATCHDOG_TIMEOUT = std::chrono::milliseconds(500);

        auto exec_res = ExecutionSupervisor::execute_with_watchdog(msg, handler, WATCHDOG_TIMEOUT);

        if (exec_res.has_value()) {
            std::cout << "[CONSUMER] Повідомлення ID=" << msg.id << " успішно оброблено. Commit ACK.\n";
            return true;
        }

        auto [category, details] = exec_res.error();
        std::cerr << "[CONSUMER-ALERT] Збій повідомлення ID=" << msg.id 
                  << ", Категорія=" << static_cast<int>(category) << ", Деталі: " << details << "\n";

        bool should_quarantine = (category == FailureCategory::DeterministicPoison) ||
                                 (category == FailureCategory::ResourceExhaustion)  ||
                                 (category == FailureCategory::PanicOrCrash)        ||
                                 (msg.delivery_count >= max_retries_);

        if (should_quarantine) {
            QuarantineEnvelope env{
                .quarantine_id = "Q-" + msg.id + "-" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count()),
                .original_message_id = msg.id,
                .partition_key = msg.partition_key,
                .original_payload = msg.payload,
                .mutated_payload = "",
                .failure_reason = (category == FailureCategory::DeterministicPoison) ? "DETERMINISTIC_POISON" :
                                  (category == FailureCategory::ResourceExhaustion)  ? "RESOURCE_EXHAUSTION" :
                                  (category == FailureCategory::PanicOrCrash)        ? "FATAL_PANIC" : "MAX_RETRIES_EXCEEDED",
                .exception_details = details,
                .category = category,
                .status = MessageStatus::Quarantined,
                .delivery_attempts = msg.delivery_count,
                .quarantined_at_ms = std::chrono::duration_cast<std::chrono::milliseconds>(
                                         std::chrono::system_clock::now().time_since_epoch()).count(),
                .host_identity = "worker-node-01"
            };

            repo_->save(env);
            // ФІКСУЄМО ЗМІЩЕННЯ: потік не блокується, черга рухається далі
            std::cout << "[CONSUMER] Отруту ізольовано в карантин. Commit Offset для звільнення партиції.\n";
            return true;
        }

        // Перехідний збій: відправляємо на повтор із затримкою
        std::cout << "[CONSUMER] Перехідний збій. Спроба " << msg.delivery_count << "/" << max_retries_ 
                  << ". Requeue with Backoff.\n";
        return false;
    }

private:
    std::shared_ptr<QuarantineRepository> repo_;
    int max_retries_;
};

// ── 5. Служба тріажу та безпечного спуску (Triage & Redrive Engine) ───────────

class TriageEngine {
public:
    explicit TriageEngine(std::shared_ptr<QuarantineRepository> repo) : repo_(std::move(repo)) {}

    bool mutate_payload(const std::string& qid, const std::string& new_payload) {
        auto env = repo_->get(qid);
        if (!env) return false;
        env->mutated_payload = new_payload;
        env->status = MessageStatus::Mutated;
        repo_->update(*env);
        std::cout << "[TRIAGE] Повідомлення " << qid << " успішно виправлено (Payload Mutated).\n";
        return true;
    }

    bool canary_replay(const std::string& qid, ExecutionSupervisor::Handler handler) {
        auto env = repo_->get(qid);
        if (!env) return false;

        std::string payload_to_test = env->mutated_payload.empty() ? env->original_payload : env->mutated_payload;
        IngressMessage test_msg{
            .id = env->original_message_id + "-canary",
            .partition_key = env->partition_key,
            .payload = payload_to_test,
            .delivery_count = 1,
            .timestamp_ms = 0
        };

        std::cout << "[TRIAGE-CANARY] Тестування повідомлення " << qid << " у безпечному сендбоксі...\n";
        auto res = ExecutionSupervisor::execute_with_watchdog(test_msg, handler, std::chrono::milliseconds(500));

        if (res.has_value()) {
            std::cout << "[TRIAGE-CANARY] УСПІХ: Повідомлення успішно проходить обробку!\n";
            env->status = MessageStatus::Replayed;
            repo_->update(*env);
            return true;
        }

        std::cerr << "[TRIAGE-CANARY] НЕВДАЧА: Повідомлення все ще викликає збій: " << res.error().second << "\n";
        return false;
    }

private:
    std::shared_ptr<QuarantineRepository> repo_;
};
