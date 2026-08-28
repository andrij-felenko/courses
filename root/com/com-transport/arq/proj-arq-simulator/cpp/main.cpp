#include <iostream>
#include <vector>
#include <queue>
#include <random>
#include <memory>
#include <string_view>
#include <iomanip>

enum class ArqProtocol {
    StopAndWait,
    GoBackN,
    SelectiveRepeat
};

enum class EventType {
    FrameRx,
    AckRx,
    Timeout
};

struct SimEvent {
    double time_us;
    EventType type;
    uint32_t seq_num;
    bool is_corrupted;

    bool operator>(const SimEvent& other) const noexcept {
        return time_us > other.time_us;
    }
};

class ArqSimulator {
public:
    struct Config {
        ArqProtocol proto;
        uint32_t window_size;
        double t_frame_us = 100.0;
        double t_prop_us = 500.0;
        double p_loss = 0.05;
        uint32_t total_packets = 1000;
    };

    struct Metrics {
        double efficiency;
        double avg_delay_ms;
        uint32_t total_transmissions;
    };

    explicit ArqSimulator(Config cfg)
        : cfg_(cfg),
          rto_us_(cfg.t_frame_us + 2.0 * cfg.t_prop_us + 50.0),
          rng_(42),
          loss_dist_(0.0, 1.0),
          tx_acked_(cfg.total_packets, false),
          rx_buffered_(cfg.total_packets, false),
          packet_start_time_(cfg.total_packets, -1.0) {}

    Metrics run() {
        double now = 0.0;

        // Стартове заповнення передавального вікна
        while (tx_next_seq_ < tx_base_ + cfg_.window_size && tx_next_seq_ < cfg_.total_packets) {
            schedule_tx(now, tx_next_seq_++);
        }

        while (!event_queue_.empty() && successful_packets_ < cfg_.total_packets) {
            SimEvent ev = event_queue_.top();
            event_queue_.pop();
            now = ev.time_us;

            switch (ev.type) {
            case EventType::FrameRx:
                handle_frame_rx(now, ev);
                break;
            case EventType::AckRx:
                handle_ack_rx(now, ev);
                break;
            case EventType::Timeout:
                handle_timeout(now, ev);
                break;
            }
        }

        return Metrics{
            .efficiency = static_cast<double>(cfg_.total_packets) / total_transmissions_,
            .avg_delay_ms = (total_delay_us_ / cfg_.total_packets) / 1000.0,
            .total_transmissions = total_transmissions_
        };
    }

private:
    void schedule_tx(double current_time, uint32_t seq) {
        total_transmissions_++;
        if (packet_start_time_[seq] < 0.0) {
            packet_start_time_[seq] = current_time;
        }

        bool lost = (loss_dist_(rng_) < cfg_.p_loss);
        event_queue_.push(SimEvent{
            .time_us = current_time + cfg_.t_frame_us + cfg_.t_prop_us,
            .type = EventType::FrameRx,
            .seq_num = seq,
            .is_corrupted = lost
        });

        event_queue_.push(SimEvent{
            .time_us = current_time + rto_us_,
            .type = EventType::Timeout,
            .seq_num = seq,
            .is_corrupted = false
        });
    }

    void handle_frame_rx(double now, const SimEvent& ev) {
        if (ev.is_corrupted) return;

        if (cfg_.proto == ArqProtocol::StopAndWait || cfg_.proto == ArqProtocol::GoBackN) {
            if (ev.seq_num == rx_expected_) {
                rx_expected_++;
                event_queue_.push(SimEvent{
                    .time_us = now + cfg_.t_prop_us,
                    .type = EventType::AckRx,
                    .seq_num = ev.seq_num,
                    .is_corrupted = false
                });
            } else if (rx_expected_ > 0) {
                event_queue_.push(SimEvent{
                    .time_us = now + cfg_.t_prop_us,
                    .type = EventType::AckRx,
                    .seq_num = rx_expected_ - 1,
                    .is_corrupted = false
                });
            }
        } else if (cfg_.proto == ArqProtocol::SelectiveRepeat) {
            if (ev.seq_num < cfg_.total_packets) {
                rx_buffered_[ev.seq_num] = true;
                event_queue_.push(SimEvent{
                    .time_us = now + cfg_.t_prop_us,
                    .type = EventType::AckRx,
                    .seq_num = ev.seq_num,
                    .is_corrupted = false
                });
                while (rx_expected_ < cfg_.total_packets && rx_buffered_[rx_expected_]) {
                    rx_expected_++;
                }
            }
        }
    }

    void handle_ack_rx(double now, const SimEvent& ev) {
        if (cfg_.proto == ArqProtocol::StopAndWait) {
            if (ev.seq_num == tx_base_) {
                mark_packet_acked(now, ev.seq_num);
                tx_base_++;
                if (tx_next_seq_ < cfg_.total_packets) {
                    schedule_tx(now, tx_next_seq_++);
                }
            }
        } else if (cfg_.proto == ArqProtocol::GoBackN) {
            if (ev.seq_num >= tx_base_) {
                while (tx_base_ <= ev.seq_num && tx_base_ < cfg_.total_packets) {
                    if (!tx_acked_[tx_base_]) {
                        mark_packet_acked(now, tx_base_);
                    }
                    tx_base_++;
                }
                while (tx_next_seq_ < tx_base_ + cfg_.window_size && tx_next_seq_ < cfg_.total_packets) {
                    schedule_tx(now, tx_next_seq_++);
                }
            }
        } else if (cfg_.proto == ArqProtocol::SelectiveRepeat) {
            if (ev.seq_num < cfg_.total_packets && !tx_acked_[ev.seq_num]) {
                mark_packet_acked(now, ev.seq_num);
                while (tx_base_ < cfg_.total_packets && tx_acked_[tx_base_]) {
                    tx_base_++;
                }
                while (tx_next_seq_ < tx_base_ + cfg_.window_size && tx_next_seq_ < cfg_.total_packets) {
                    schedule_tx(now, tx_next_seq_++);
                }
            }
        }
    }

    void handle_timeout(double now, const SimEvent& ev) {
        if (ev.seq_num < cfg_.total_packets && !tx_acked_[ev.seq_num]) {
            if (cfg_.proto == ArqProtocol::StopAndWait || cfg_.proto == ArqProtocol::SelectiveRepeat) {
                schedule_tx(now, ev.seq_num);
            } else if (cfg_.proto == ArqProtocol::GoBackN && ev.seq_num == tx_base_) {
                for (uint32_t s = tx_base_; s < tx_next_seq_; s++) {
                    schedule_tx(now, s);
                }
            }
        }
    }

    void mark_packet_acked(double now, uint32_t seq) {
        tx_acked_[seq] = true;
        total_delay_us_ += (now - packet_start_time_[seq]);
        successful_packets_++;
    }

    Config cfg_;
    double rto_us_;
    std::mt19937 rng_;
    std::uniform_real_distribution<double> loss_dist_;

    std::priority_queue<SimEvent, std::vector<SimEvent>, std::greater<SimEvent>> event_queue_;
    uint32_t tx_base_ = 0;
    uint32_t tx_next_seq_ = 0;
    uint32_t rx_expected_ = 0;

    std::vector<bool> tx_acked_;
    std::vector<bool> rx_buffered_;
    std::vector<double> packet_start_time_;

    uint32_t total_transmissions_ = 0;
    uint32_t successful_packets_ = 0;
    double total_delay_us_ = 0.0;
};

void print_result(std::string_view name, ArqSimulator::Config cfg, ArqSimulator::Metrics m) {
    std::cout << "[" << name << "] Win=" << cfg.window_size 
              << ", Pf=" << cfg.p_loss << ", a=" << (cfg.t_prop_us / cfg.t_frame_us)
              << " -> Ефективність: " << std::fixed << std::setprecision(3) << m.efficiency
              << ", Середня затримка: " << std::setprecision(2) << m.avg_delay_ms << " мс"
              << " (Передач: " << m.total_transmissions << ")\n";
}

int main() {
    std::cout << "=== Результати імітаційного моделювання ARQ (1000 пакетів) ===\n";

    ArqSimulator sim_sw({.proto = ArqProtocol::StopAndWait, .window_size = 1, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05});
    print_result("Stop-and-Wait", {.proto = ArqProtocol::StopAndWait, .window_size = 1, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05}, sim_sw.run());

    ArqSimulator sim_gbn({.proto = ArqProtocol::GoBackN, .window_size = 16, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05});
    print_result("Go-Back-N", {.proto = ArqProtocol::GoBackN, .window_size = 16, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05}, sim_gbn.run());

    ArqSimulator sim_sr({.proto = ArqProtocol::SelectiveRepeat, .window_size = 16, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05});
    print_result("Selective Repeat", {.proto = ArqProtocol::SelectiveRepeat, .window_size = 16, .t_frame_us = 100.0, .t_prop_us = 500.0, .p_loss = 0.05}, sim_sr.run());

    return 0;
}
