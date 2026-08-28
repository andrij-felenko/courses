// client_failover_driver.hpp — Ідіоматичний C++20 клієнт із підтримкою failover
#pragma once
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <random>
#include <chrono>
#include <thread>
#include <expected>
#include <memory>
#include <optional>

namespace db::ha {

enum class ClusterState {
    Disconnected,
    ProbingHosts,
    ConnectedPrimary,
    BackoffWait,
    FatalFailure
};

enum class ClientError {
    ClusterUnavailable,
    QueryExecutionFailed,
    Timeout
};

struct Endpoint {
    std::string host;
    uint16_t port{5432};
};

class FailoverClient {
public:
    explicit FailoverClient(std::vector<Endpoint> endpoints)
        : endpoints_(std::move(endpoints)), rng_(std::random_device{}()) {}

    [[nodiscard]] std::expected<void, ClientError> execute_write(std::string_view query) {
        ClusterState state = ClusterState::ProbingHosts;
        uint32_t attempt = 0;

        while (state != ClusterState::FatalFailure) {
            switch (state) {
                case ClusterState::ProbingHosts: {
                    if (auto primary_idx = probe_endpoints(); primary_idx.has_value()) {
                        active_index_ = *primary_idx;
                        state = ClusterState::ConnectedPrimary;
                        attempt = 0;
                    } else {
                        state = ClusterState::BackoffWait;
                    }
                    break;
                }

                case ClusterState::ConnectedPrimary: {
                    std::cout << "[CLIENT-CXX] Успішний запис на "
                              << endpoints_[active_index_].host << ":"
                              << endpoints_[active_index_].port << " | SQL: " << query << '\n';
                    return {};
                }

                case ClusterState::BackoffWait: {
                    ++attempt;
                    if (attempt >= max_attempts_) {
                        std::cerr << "[CLIENT-CXX] Вичерпано ліміт спроб підключення до Primary.\n";
                        return std::unexpected(ClientError::ClusterUnavailable);
                    }
                    const auto wait_dur = compute_backoff(attempt);
                    std::cerr << "[CLIENT-CXX] Очікування нового Primary: "
                              << wait_dur.count() << " мс (спроба " << attempt << ")\n";
                    std::this_thread::sleep_for(wait_dur);
                    state = ClusterState::ProbingHosts;
                    break;
                }

                default:
                    return std::unexpected(ClientError::ClusterUnavailable);
            }
        }
        return std::unexpected(ClientError::ClusterUnavailable);
    }

private:
    [[nodiscard]] std::optional<size_t> probe_endpoints() const {
        for (size_t i = 0; i < endpoints_.size(); ++i) {
            size_t idx = (active_index_ + i) % endpoints_.size();
            if (mock_is_primary(endpoints_[idx])) {
                return idx;
            }
        }
        return std::nullopt;
    }

    [[nodiscard]] static bool mock_is_primary(const Endpoint& ep) noexcept {
        return ep.host == "10.0.1.12"; // Симуляція виявлення нового промоутеного лідера
    }

    [[nodiscard]] std::chrono::milliseconds compute_backoff(uint32_t attempt) {
        const uint32_t shift = (attempt > 6) ? 6 : attempt;
        const uint32_t max_ms = std::min(max_backoff_ms_, base_backoff_ms_ * (1U << shift));
        std::uniform_int_distribution<uint32_t> dist(0, max_ms);
        return std::chrono::milliseconds(dist(rng_));
    }

    std::vector<Endpoint> endpoints_;
    size_t active_index_{0};
    uint32_t base_backoff_ms_{100};
    uint32_t max_backoff_ms_{3000};
    uint32_t max_attempts_{10};
    mutable std::mt19937 rng_;
};

} // namespace db::ha
