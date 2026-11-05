#include "slip_ring_monitor.hpp"
#include <cmath>
#include <algorithm>
#include <numeric>

SlipRingMonitor::SlipRingMonitor(size_t window_size, double micro_break_threshold_ms)
    : window_size_(window_size),
      micro_break_threshold_ms_(micro_break_threshold_ms),
      total_sent_(0),
      total_received_(0),
      total_lost_(0),
      micro_breaks_detected_(0) {}

void SlipRingMonitor::recordSentPacket(uint64_t /*sequence_number*/) {
    total_sent_++;
}

void SlipRingMonitor::recordReceivedPacket(uint64_t /*sequence_number*/,
                                           std::chrono::steady_clock::time_point send_time,
                                           std::chrono::steady_clock::time_point receive_time) {
    total_received_++;

    auto duration_ns = std::chrono::duration_cast<std::chrono::nanoseconds>(receive_time - send_time).count();
    double latency_ms = static_cast<double>(duration_ns) / 1'000'000.0;

    // Перевірка на аномалію (мікророзрив контакту щіток)
    if (latency_ms > micro_break_threshold_ms_) {
        micro_breaks_detected_++;
    }

    // Оновлення вікна затримок
    latency_window_.push_back({receive_time, latency_ms});
    if (latency_window_.size() > window_size_) {
        latency_window_.pop_front();
    }

    // Оновлення вікна для розрахунку джитеру
    jitter_window_.push_back(latency_ms);
    if (jitter_window_.size() > window_size_) {
        jitter_window_.pop_front();
    }
}

void SlipRingMonitor::recordLostPacket(uint64_t /*sequence_number*/) {
    total_lost_++;
    micro_breaks_detected_++;
}

SlipRingStatistics SlipRingMonitor::getStatistics() const {
    SlipRingStatistics stats;
    stats.total_sent = total_sent_;
    stats.total_received = total_received_;
    stats.total_lost = total_lost_;
    stats.micro_breaks_detected = micro_breaks_detected_;

    if (total_sent_ > 0) {
        stats.packet_loss_percent = (static_cast<double>(total_lost_) / static_cast<double>(total_sent_)) * 100.0;
    } else {
        stats.packet_loss_percent = 0.0;
    }

    if (!latency_window_.empty()) {
        double sum_latency = 0.0;
        for (const auto& rec : latency_window_) {
            sum_latency += rec.latency_ms;
        }
        stats.average_latency_ms = sum_latency / latency_window_.size();
    } else {
        stats.average_latency_ms = 0.0;
    }

    // Розрахунок ковзного джитеру (середнє абсолютне відхилення послідовних затримок)
    if (jitter_window_.size() > 1) {
        double sum_diff = 0.0;
        for (size_t i = 1; i < jitter_window_.size(); ++i) {
            sum_diff += std::abs(jitter_window_[i] - jitter_window_[i - 1]);
        }
        stats.jitter_ms = sum_diff / (jitter_window_.size() - 1);
    } else {
        stats.jitter_ms = 0.0;
    }

    return stats;
}

void SlipRingMonitor::reset() {
    total_sent_ = 0;
    total_received_ = 0;
    total_lost_ = 0;
    micro_breaks_detected_ = 0;
    latency_window_.clear();
    jitter_window_.clear();
}
