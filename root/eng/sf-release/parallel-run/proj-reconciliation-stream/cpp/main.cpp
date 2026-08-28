#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <chrono>
#include <mutex>
#include <memory>
#include <vector>
#include <sstream>
#include <cmath>
#include <functional>

using namespace std::chrono_literals;

// Тип джерела події
enum class SourceBranch { Control, Candidate };

// Структура нормалізованого платіжного результату
struct TransactionResult {
    std::string correlation_id;
    std::string account_id;
    int64_t amount_cents;
    std::string currency;
    std::string status_code;
    std::chrono::system_clock::time_point emitted_at;
};

// Результат порівняння двох гілок
enum class DiffVerdict {
    ExactMatch,
    ToleratedVariance,
    SemanticMismatch,
    StructuralMissing
};

struct DiffReport {
    std::string correlation_id;
    DiffVerdict verdict;
    std::string details;
    std::chrono::milliseconds processing_skew;
};

// Нормалізатор: вилучає недетермінізм і перевіряє строгі бізнес-інваріанти
class LedgerNormalizer {
public:
    static DiffReport compare(const TransactionResult& ctrl, const TransactionResult& cand) {
        DiffReport report;
        report.correlation_id = ctrl.correlation_id;
        
        auto skew = std::chrono::duration_cast<std::chrono::milliseconds>(
            cand.emitted_at > ctrl.emitted_at ? (cand.emitted_at - ctrl.emitted_at) 
                                              : (ctrl.emitted_at - cand.emitted_at));
        report.processing_skew = skew;

        // 1. Перевірка базових контрактних полів
        if (ctrl.account_id != cand.account_id) {
            report.verdict = DiffVerdict::SemanticMismatch;
            report.details = "Account mismatch: ctrl=" + ctrl.account_id + ", cand=" + cand.account_id;
            return report;
        }

        if (ctrl.currency != cand.currency) {
            report.verdict = DiffVerdict::SemanticMismatch;
            report.details = "Currency mismatch: ctrl=" + ctrl.currency + ", cand=" + cand.currency;
            return report;
        }

        if (ctrl.status_code != cand.status_code) {
            report.verdict = DiffVerdict::SemanticMismatch;
            report.details = "Status mismatch: ctrl=" + ctrl.status_code + ", cand=" + cand.status_code;
            return report;
        }

        // 2. Перевірка балансу / суми операції
        if (ctrl.amount_cents != cand.amount_cents) {
            report.verdict = DiffVerdict::SemanticMismatch;
            report.details = "Amount mismatch: ctrl=" + std::to_string(ctrl.amount_cents) +
                             " != cand=" + std::to_string(cand.amount_cents);
            return report;
        }

        report.verdict = DiffVerdict::ExactMatch;
        report.details = "OK";
        return report;
    }
};

// Буфер ковзного вікна звірки
class SlidingReconciliationWindow {
private:
    struct PendingSlot {
        std::unique_ptr<TransactionResult> control_payload;
        std::unique_ptr<TransactionResult> candidate_payload;
        std::chrono::steady_clock::time_point first_seen;
    };

    mutable std::mutex mutex_;
    std::unordered_map<std::string, PendingSlot> slots_;
    std::chrono::milliseconds window_ttl_;

public:
    explicit SlidingReconciliationWindow(std::chrono::milliseconds ttl = 5000ms)
        : window_ttl_(ttl) {}

    // Додати подію з однієї з гілок
    void ingest(SourceBranch branch, TransactionResult result, 
                const std::function<void(const DiffReport&)>& on_diff) {
        std::unique_ptr<TransactionResult> pair_to_compare_ctrl;
        std::unique_ptr<TransactionResult> pair_to_compare_cand;
        std::string cid = result.correlation_id;

        {
            std::lock_guard<std::mutex> lock(mutex_);
            auto now = std::chrono::steady_clock::now();
            auto& slot = slots_[cid];

            if (!slot.control_payload && !slot.candidate_payload) {
                slot.first_seen = now;
            }

            if (branch == SourceBranch::Control) {
                slot.control_payload = std::make_unique<TransactionResult>(std::move(result));
            } else {
                slot.candidate_payload = std::make_unique<TransactionResult>(std::move(result));
            }

            // Якщо обидві половинки надійшли — забираємо на порівняння
            if (slot.control_payload && slot.candidate_payload) {
                pair_to_compare_ctrl = std::move(slot.control_payload);
                pair_to_compare_cand = std::move(slot.candidate_payload);
                slots_.erase(cid);
            }
        }

        // Порівняння робиться ПОЗА локом, щоб не гальмувати паралельні потоки
        if (pair_to_compare_ctrl && pair_to_compare_cand) {
            DiffReport report = LedgerNormalizer::compare(*pair_to_compare_ctrl, *pair_to_compare_cand);
            on_diff(report);
        }
    }

    // Фонова очистка прострочених слотів (події, для яких пара не прийшла)
    void sweep_expired(const std::function<void(const std::string&, SourceBranch)>& on_timeout) {
        std::vector<std::pair<std::string, SourceBranch>> timed_out;
        auto now = std::chrono::steady_clock::now();

        {
            std::lock_guard<std::mutex> lock(mutex_);
            for (auto it = slots_.begin(); it != slots_.end(); ) {
                if (now - it->second.first_seen > window_ttl_) {
                    SourceBranch missing = it->second.control_payload ? SourceBranch::Candidate 
                                                                       : SourceBranch::Control;
                    timed_out.emplace_back(it->first, missing);
                    it = slots_.erase(it);
                } else {
                    ++it;
                }
            }
        }

        for (const auto& [cid, missing_branch] : timed_out) {
            on_timeout(cid, missing_branch);
        }
    }

    size_t pending_count() const {
        std::lock_guard<std::mutex> lock(mutex_);
        return slots_.size();
    }
};
