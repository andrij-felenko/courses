/* ============================================================================
 * Метричний рушій на сучасному C++20
 * Потокобезпечний, lock-free операції інструментації, захист кардинальності
 * та форматування у стандарт OpenMetrics через std::string_view та std::span.
 * ============================================================================ */
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <array>
#include <span>
#include <atomic>
#include <shared_mutex>
#include <memory>
#include <sstream>
#include <format>
#include <algorithm>
#include <chrono>

namespace telemetry {

enum class MetricType {
    Counter,
    Gauge,
    Histogram
};

/* Атомарне додавання дійсного числа через compare-and-swap */
inline void atomic_add(std::atomic<double>& target, double delta) noexcept {
    double current = target.load(std::memory_order_relaxed);
    while (!target.compare_exchange_weak(current, current + delta,
                                         std::memory_order_relaxed,
                                         std::memory_order_relaxed)) {}
}

class Counter {
public:
    void inc(uint64_t delta = 1) noexcept {
        value_.fetch_add(delta, std::memory_order_relaxed);
    }
    [[nodiscard]] uint64_t get() const noexcept {
        return value_.load(std::memory_order_relaxed);
    }
private:
    alignas(64) std::atomic<uint64_t> value_{0};
};

class Gauge {
public:
    void set(double val) noexcept {
        value_.store(val, std::memory_order_relaxed);
    }
    void add(double delta) noexcept {
        atomic_add(value_, delta);
    }
    [[nodiscard]] double get() const noexcept {
        return value_.load(std::memory_order_relaxed);
    }
private:
    alignas(64) std::atomic<double> value_{0.0};
};

class Histogram {
public:
    explicit Histogram(std::span<const double> bounds)
        : boundaries_(bounds.begin(), bounds.end()),
          bucket_counts_(bounds.size()) {
        for (auto& c : bucket_counts_) {
            c.store(0, std::memory_order_relaxed);
        }
    }

    void observe(double value) noexcept {
        for (size_t i = 0; i < boundaries_.size(); ++i) {
            if (value <= boundaries_[i]) {
                bucket_counts_[i].fetch_add(1, std::memory_order_relaxed);
            }
        }
        count_.fetch_add(1, std::memory_order_relaxed);
        atomic_add(sum_, value);
    }

    [[nodiscard]] std::span<const double> boundaries() const noexcept { return boundaries_; }
    [[nodiscard]] uint64_t bucket_count(size_t idx) const noexcept {
        return bucket_counts_[idx].load(std::memory_order_relaxed);
    }
    [[nodiscard]] uint64_t count() const noexcept { return count_.load(std::memory_order_relaxed); }
    [[nodiscard]] double sum() const noexcept { return sum_.load(std::memory_order_relaxed); }

private:
    std::vector<double> boundaries_;
    std::vector<std::atomic<uint64_t>> bucket_counts_;
    alignas(64) std::atomic<uint64_t> count_{0};
    alignas(64) std::atomic<double> sum_{0.0};
};

/* Дескриптор метричного ряду */
struct MetricEntry {
    std::string name;
    std::string labels;
    MetricType type;
    std::variant<Counter, Gauge, Histogram> storage;
};

class Registry {
public:
    static constexpr size_t kMaxSeriesLimit = 512;

    Counter* get_counter(std::string_view name, std::string_view labels) {
        return get_or_create<Counter>(name, labels, MetricType::Counter,
                                      []() { return Counter{}; });
    }

    Gauge* get_gauge(std::string_view name, std::string_view labels) {
        return get_or_create<Gauge>(name, labels, MetricType::Gauge,
                                    []() { return Gauge{}; });
    }

    Histogram* get_histogram(std::string_view name, std::string_view labels,
                             std::span<const double> buckets) {
        return get_or_create<Histogram>(name, labels, MetricType::Histogram,
                                        [buckets]() { return Histogram(buckets); });
    }

    [[nodiscard]] std::string render_openmetrics() const {
        std::shared_lock lock(mutex_);
        std::string out;
        out.reserve(32768);

        for (const auto& entry : entries_) {
            if (entry.type == MetricType::Counter) {
                const auto& c = std::get<Counter>(entry.storage);
                out += std::format("# TYPE {} counter\n{}{{{}}} {}\n",
                                   entry.name, entry.name, entry.labels, c.get());
            } else if (entry.type == MetricType::Gauge) {
                const auto& g = std::get<Gauge>(entry.storage);
                out += std::format("# TYPE {} gauge\n{}{{{}}} {:.6f}\n",
                                   entry.name, entry.name, entry.labels, g.get());
            } else if (entry.type == MetricType::Histogram) {
                const auto& h = std::get<Histogram>(entry.storage);
                out += std::format("# TYPE {} histogram\n", entry.name);
                auto bounds = h.boundaries();
                for (size_t b = 0; b < bounds.size(); ++b) {
                    out += std::format("{}_bucket{{{},le=\"{:.4f}\"}} {}\n",
                                       entry.name, entry.labels, bounds[b], h.bucket_count(b));
                }
                out += std::format("{}_bucket{{{},le=\"+Inf\"}} {}\n",
                                   entry.name, entry.labels, h.count());
                out += std::format("{}_sum{{{{{}}}}} {:.6f}\n", entry.name, entry.labels, h.sum());
                out += std::format("{}_count{{{{{}}}}} {}\n", entry.name, entry.labels, h.count());
            }
        }

        out += std::format("# TYPE metrics_overflow_total counter\nmetrics_overflow_total {}\n# EOF\n",
                           overflow_count_.load(std::memory_order_relaxed));
        return out;
    }

private:
    template <typename T, typename Factory>
    T* get_or_create(std::string_view name, std::string_view labels, MetricType type, Factory&& factory) {
        {
            std::shared_lock lock(mutex_);
            for (auto& entry : entries_) {
                if (entry.name == name && entry.labels == labels) {
                    return &std::get<T>(entry.storage);
                }
            }
        }

        std::unique_lock lock(mutex_);
        for (auto& entry : entries_) {
            if (entry.name == name && entry.labels == labels) {
                return &std::get<T>(entry.storage);
            }
        }

        if (entries_.size() >= kMaxSeriesLimit) {
            overflow_count_.fetch_add(1, std::memory_order_relaxed);
            return nullptr;
        }

        entries_.push_back(MetricEntry{
            .name = std::string(name),
            .labels = std::string(labels),
            .type = type,
            .storage = factory()
        });

        return &std::get<T>(entries_.back().storage);
    }

    mutable std::shared_mutex mutex_;
    std::vector<MetricEntry> entries_;
    std::atomic<uint64_t> overflow_count_{0};
};

} // namespace telemetry
