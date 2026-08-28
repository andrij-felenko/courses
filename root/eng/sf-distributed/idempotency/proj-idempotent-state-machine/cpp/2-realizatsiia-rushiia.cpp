#include <iostream>
#include <string>
#include <string_view>
#include <unordered_map>
#include <chrono>
#include <mutex>
#include <optional>
#include <memory>
#include <expected>
#include <cstdint>

enum class IdemState {
    InProgress,
    Committed,
    Failed
};

enum class IdemError {
    InFlightConflict,
    PayloadMismatch,
    InternalError
};

struct CachedResponse {
    int statusCode;
    std::string body;
};

class IdempotencyEngine {
public:
    using Clock = std::chrono::steady_clock;
    using TimePoint = Clock::time_point;

    explicit IdempotencyEngine(
        std::chrono::seconds leaseTimeout = std::chrono::seconds(30),
        std::chrono::seconds retentionPeriod = std::chrono::seconds(86400))
        : leaseDuration_(leaseTimeout), retentionDuration_(retentionPeriod) {}

    // Спроба отримати або перевірити стан операції
    // Повертає:
    // - nullopt: запис успішно взято в обробку (викликач виконує бізнес-дію)
    // - CachedResponse: дія вже була успішно зафіксована раніше
    // - IdemError: конфлікт виконання або розбіжність параметрів
    std::expected<std::optional<CachedResponse>, IdemError> acquireOrCheck(
        std::string_view key, std::string_view payload) {
        
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = Clock::now();
        uint64_t pHash = computeHash(payload);

        auto it = store_.find(std::string(key));
        if (it != store_.end()) {
            auto& record = it->second;

            if (record.state == IdemState::Committed) {
                if (record.payloadHash != pHash) {
                    return std::unexpected(IdemError::PayloadMismatch);
                }
                return std::make_optional(record.cachedResult);
            }

            if (record.state == IdemState::InProgress) {
                if (now < record.expiresAt) {
                    return std::unexpected(IdemError::InFlightConflict);
                }
                // Оренда застаріла — перехоплюємо виконання
                record.payloadHash = pHash;
                record.expiresAt = now + leaseDuration_;
                return std::nullopt;
            }

            if (record.state == IdemState::Failed) {
                record.state = IdemState::InProgress;
                record.payloadHash = pHash;
                record.expiresAt = now + leaseDuration_;
                return std::nullopt;
            }
        }

        // Новий запис
        Record newRecord{
            .payloadHash = pHash,
            .state = IdemState::InProgress,
            .cachedResult = {},
            .expiresAt = now + leaseDuration_
        };
        store_.emplace(std::string(key), std::move(newRecord));
        return std::nullopt;
    }

    // Фіксація успішного результату
    bool commit(std::string_view key, int statusCode, std::string body) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = store_.find(std::string(key));
        if (it != store_.end() && it->second.state == IdemState::InProgress) {
            it->second.state = IdemState::Committed;
            it->second.cachedResult = CachedResponse{statusCode, std::move(body)};
            it->second.expiresAt = Clock::now() + retentionDuration_;
            return true;
        }
        return false;
    }

    // Фіксація збою (дозволяє наступні retry)
    bool fail(std::string_view key) {
        std::lock_guard<std::mutex> lock(mutex_);
        auto it = store_.find(std::string(key));
        if (it != store_.end() && it->second.state == IdemState::InProgress) {
            it->second.state = IdemState::Failed;
            return true;
        }
        return false;
    }

    // Фонове очищення застарілих записів після TTL
    size_t evictExpired() {
        std::lock_guard<std::mutex> lock(mutex_);
        auto now = Clock::now();
        size_t initialSize = store_.size();
        std::erase_if(store_, [now](const auto& item) {
            return now >= item.second.expiresAt;
        });
        return initialSize - store_.size();
    }

private:
    struct Record {
        uint64_t payloadHash;
        IdemState state;
        CachedResponse cachedResult;
        TimePoint expiresAt;
    };

    static uint64_t computeHash(std::string_view s) {
        uint64_t h = 0xcbf29ce484222325ULL;
        for (char c : s) {
            h ^= static_cast<uint8_t>(c);
            h *= 0x100000001b3ULL;
        }
        return h;
    }

    std::chrono::seconds leaseDuration_;
    std::chrono::seconds retentionDuration_;
    std::mutex mutex_;
    std::unordered_map<std::string, Record> store_;
};
