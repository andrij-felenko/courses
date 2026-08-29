#pragma once

// Лічильники й гістограма конвеєра у форматі, який забирає Prometheus.
// Усе — атоміки з relaxed-порядком: точний порядок інкрементів нікому не потрібен,
// а зайвий бар'єр на гарячому шляху коштує тактів.

#include "wire_format.hpp"

#include <array>
#include <atomic>
#include <chrono>
#include <cstddef>
#include <cstdint>
#include <iomanip>
#include <sstream>
#include <string>

namespace ingest {

// Смуги гістограми в секундах: від сотні мікросекунд до чверті секунди.
inline constexpr std::array<double, 11> kLatencyBuckets{
    0.0001, 0.00025, 0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25};

class Metrics {
public:
    void on_ingested() noexcept { ingested_.fetch_add(1, std::memory_order_relaxed); }
    void on_dropped() noexcept { dropped_.fetch_add(1, std::memory_order_relaxed); }
    void on_out_of_range() noexcept { out_of_range_.fetch_add(1, std::memory_order_relaxed); }

    void on_rejected(FrameError error) noexcept {
        rejected_[static_cast<std::size_t>(error)].fetch_add(1, std::memory_order_relaxed);
    }

    void on_stored(std::size_t rows) noexcept {
        stored_.fetch_add(rows, std::memory_order_relaxed);
        batches_.fetch_add(1, std::memory_order_relaxed);
    }

    template <class Rep, class Period>
    void observe_latency(std::chrono::duration<Rep, Period> value) noexcept {
        auto micros = std::chrono::duration_cast<std::chrono::microseconds>(value).count();
        if (micros < 0) {
            micros = 0;  // годинник назад не йде, але захист дешевший за від'ємну суму
        }
        const double seconds = static_cast<double>(micros) * 1e-6;

        std::size_t index = 0;
        while (index < kLatencyBuckets.size() && seconds > kLatencyBuckets[index]) {
            ++index;
        }
        buckets_[index].fetch_add(1, std::memory_order_relaxed);
        latency_sum_us_.fetch_add(static_cast<std::uint64_t>(micros), std::memory_order_relaxed);
        latency_count_.fetch_add(1, std::memory_order_relaxed);
    }

    std::uint64_t ingested_total() const noexcept { return ingested_.load(std::memory_order_relaxed); }
    std::uint64_t dropped_total() const noexcept { return dropped_.load(std::memory_order_relaxed); }
    std::uint64_t stored_total() const noexcept { return stored_.load(std::memory_order_relaxed); }
    std::uint64_t batches_total() const noexcept { return batches_.load(std::memory_order_relaxed); }
    std::uint64_t out_of_range_total() const noexcept {
        return out_of_range_.load(std::memory_order_relaxed);
    }
    std::uint64_t rejected_total(FrameError error) const noexcept {
        return rejected_[static_cast<std::size_t>(error)].load(std::memory_order_relaxed);
    }

    // Текстовий формат експозиції Prometheus: смуги гістограми — накопичувальні.
    std::string render() const {
        std::ostringstream out;
        out << "# HELP telemetry_ingested_total Кадрів, узятих приймачем у чергу.\n"
               "# TYPE telemetry_ingested_total counter\n"
            << "telemetry_ingested_total " << ingested_total() << "\n"
            << "# HELP telemetry_dropped_total Кадрів, утрачених через переповнення черги.\n"
               "# TYPE telemetry_dropped_total counter\n"
            << "telemetry_dropped_total " << dropped_total() << "\n"
            << "# HELP telemetry_rejected_total Кадрів, відкинутих розбором.\n"
               "# TYPE telemetry_rejected_total counter\n";

        for (std::size_t i = 1; i < kFrameErrorCount; ++i) {
            const auto error = static_cast<FrameError>(i);
            out << "telemetry_rejected_total{reason=\"" << to_string(error) << "\"} "
                << rejected_total(error) << "\n";
        }

        out << "# HELP telemetry_out_of_range_total Подій поза фізичним діапазоном давача.\n"
               "# TYPE telemetry_out_of_range_total counter\n"
            << "telemetry_out_of_range_total " << out_of_range_total() << "\n"
            << "# HELP telemetry_stored_total Рядків, записаних у сховище.\n"
               "# TYPE telemetry_stored_total counter\n"
            << "telemetry_stored_total " << stored_total() << "\n"
            << "# HELP telemetry_processing_latency_seconds Час від прийому до розбору.\n"
               "# TYPE telemetry_processing_latency_seconds histogram\n";

        std::uint64_t cumulative = 0;
        out << std::fixed;
        for (std::size_t i = 0; i < kLatencyBuckets.size(); ++i) {
            cumulative += buckets_[i].load(std::memory_order_relaxed);
            out << "telemetry_processing_latency_seconds_bucket{le=\"" << std::setprecision(5)
                << kLatencyBuckets[i] << "\"} " << cumulative << "\n";
        }
        cumulative += buckets_[kLatencyBuckets.size()].load(std::memory_order_relaxed);
        out << "telemetry_processing_latency_seconds_bucket{le=\"+Inf\"} " << cumulative << "\n"
            << "telemetry_processing_latency_seconds_sum " << std::setprecision(6)
            << static_cast<double>(latency_sum_us_.load(std::memory_order_relaxed)) * 1e-6 << "\n"
            << "telemetry_processing_latency_seconds_count "
            << latency_count_.load(std::memory_order_relaxed) << "\n";
        return out.str();
    }

private:
    alignas(64) std::atomic<std::uint64_t> ingested_{0};
    alignas(64) std::atomic<std::uint64_t> dropped_{0};
    alignas(64) std::atomic<std::uint64_t> stored_{0};
    alignas(64) std::atomic<std::uint64_t> batches_{0};
    alignas(64) std::atomic<std::uint64_t> out_of_range_{0};
    alignas(64) std::atomic<std::uint64_t> latency_sum_us_{0};
    alignas(64) std::atomic<std::uint64_t> latency_count_{0};
    std::array<std::atomic<std::uint64_t>, kFrameErrorCount> rejected_{};
    std::array<std::atomic<std::uint64_t>, kLatencyBuckets.size() + 1> buckets_{};
};

}  // namespace ingest
