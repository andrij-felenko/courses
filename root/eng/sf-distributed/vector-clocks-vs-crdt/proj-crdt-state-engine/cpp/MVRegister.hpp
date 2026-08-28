// MVRegister.hpp
#pragma once
#include "VectorClock.hpp"
#include <vector>
#include <string>
#include <ranges>

template <typename T>
class MVRegister {
public:
    struct VersionedValue {
        T value;
        VectorClock clock;
    };

    // Запис нового значення із причинним контекстом клієнта
    void write(T value, const std::string& actor_id, VectorClock context) {
        context.increment(actor_id);
        
        std::vector<VersionedValue> next_versions;
        next_versions.push_back(VersionedValue{
            .value = std::move(value),
            .clock = context
        });

        // Залишаємо лише ті старі версії, які НЕ є предками нового запису
        for (auto& entry : versions_) {
            auto rel = entry.clock.compare(context);
            if (rel == ClockRelation::Concurrent || rel == ClockRelation::After) {
                next_versions.push_back(std::move(entry));
            }
        }
        versions_ = std::move(next_versions);
    }

    // Злиття станів двох MV-регістрів
    void merge(const MVRegister<T>& other) {
        std::vector<VersionedValue> merged;

        // Перевіряємо кожну версію з поточного регістра
        for (const auto& local : versions_) {
            bool overwritten = false;
            for (const auto& remote : other.versions_) {
                if (local.clock.compare(remote.clock) == ClockRelation::Before) {
                    overwritten = true;
                    break;
                }
            }
            if (!overwritten) {
                merged.push_back(local);
            }
        }

        // Додаємо віддалені версії, якщо вони не перезаписані локальними
        for (const auto& remote : other.versions_) {
            bool overwritten = false;
            for (const auto& local : versions_) {
                auto rel = remote.clock.compare(local.clock);
                if (rel == ClockRelation::Before || rel == ClockRelation::Equal) {
                    overwritten = true;
                    break;
                }
            }
            if (!overwritten) {
                merged.push_back(remote);
            }
        }

        versions_ = std::move(merged);
    }

    [[nodiscard]] std::vector<T> read() const {
        std::vector<T> result;
        result.reserve(versions_.size());
        for (const auto& v : versions_) {
            result.push_back(v.value);
        }
        return result;
    }

    [[nodiscard]] bool has_conflict() const noexcept {
        return versions_.size() > 1;
    }

private:
    std::vector<VersionedValue> versions_;
};
