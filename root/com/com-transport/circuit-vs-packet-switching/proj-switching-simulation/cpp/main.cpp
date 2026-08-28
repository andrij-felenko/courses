#include <iostream>
#include <vector>
#include <queue>
#include <random>
#include <cmath>
#include <iomanip>

struct Packet {
    double arrival_time;
    int source_id;
};

struct Source {
    double time_on_mean;
    double time_off_mean;
    double peak_rate_bps;
    bool is_on{false};
    double next_state_change{0.0};
    int channel_id{-1};
    double last_packet_time{0.0};
};

class SwitchingSimulator {
public:
    SwitchingSimulator(int num_sources, double link_bps, double peak_bps, double sim_time)
        : num_sources_(num_sources),
          link_capacity_bps_(link_bps),
          peak_rate_bps_(peak_bps),
          sim_duration_(sim_time),
          num_circuits_(static_cast<int>(link_bps / peak_bps)),
          circuit_busy_(num_circuits_, false),
          gen_(42) {}

    void run() {
        std::exponential_distribution<double> dist_on(1.0 / 0.2);
        std::exponential_distribution<double> dist_off(1.0 / 1.8);

        std::vector<Source> sources(num_sources_);
        for (auto &s : sources) {
            s.time_on_mean = 0.2;
            s.time_off_mean = 1.8;
            s.peak_rate_bps = peak_rate_bps_;
            s.is_on = false;
            s.next_state_change = dist_off(gen_);
        }

        const double dt = 0.0001; // 100 мкс
        const int packet_size_bits = 8000;
        const double packet_interval = static_cast<double>(packet_size_bits) / peak_rate_bps_;
        const double packet_tx_time = static_cast<double>(packet_size_bits) / link_capacity_bps_;

        std::queue<Packet> pkt_queue;
        const size_t queue_capacity = 50;

        for (double t = 0.0; t < sim_duration_; t += dt) {
            // Оновлення джерел
            for (int i = 0; i < num_sources_; ++i) {
                auto &s = sources[i];
                if (t >= s.next_state_change) {
                    if (!s.is_on) {
                        s.is_on = true;
                        s.next_state_change = t + dist_on(gen_);
                        s.last_packet_time = t;

                        // Circuit: запит на таймслот
                        circuit_requests_total_++;
                        int free_ch = -1;
                        for (int ch = 0; ch < num_circuits_; ++ch) {
                            if (!circuit_busy_[ch]) {
                                free_ch = ch;
                                break;
                            }
                        }
                        if (free_ch != -1) {
                            circuit_busy_[free_ch] = true;
                            s.channel_id = free_ch;
                        } else {
                            s.channel_id = -1;
                            circuit_requests_blocked_++;
                        }
                    } else {
                        s.is_on = false;
                        s.next_state_change = t + dist_off(gen_);
                        if (s.channel_id != -1) {
                            circuit_busy_[s.channel_id] = false;
                            s.channel_id = -1;
                        }
                    }
                }

                if (s.is_on) {
                    if (s.channel_id != -1) {
                        circuit_bits_transferred_ += peak_rate_bps_ * dt;
                    }
                    if (t - s.last_packet_time >= packet_interval) {
                        s.last_packet_time = t;
                        packets_generated_++;
                        if (pkt_queue.size() < queue_capacity) {
                            pkt_queue.push(Packet{t, i});
                        } else {
                            packets_dropped_++;
                        }
                    }
                }
            }

            // Обробка черги вихідного порту
            if (t >= packet_server_busy_until_ && !pkt_queue.empty()) {
                Packet p = pkt_queue.front();
                pkt_queue.pop();
                packet_server_busy_until_ = t + packet_tx_time;
                double delay = (t + packet_tx_time) - p.arrival_time;
                total_packet_delay_ += delay;
                total_packet_delay_sq_ += delay * delay;
                packets_served_++;
                packet_bits_transferred_ += packet_size_bits;
            }
        }
    }

    void print_report() const {
        double circuit_util = (circuit_bits_transferred_ / (link_capacity_bps_ * sim_duration_)) * 100.0;
        double circuit_block = (static_cast<double>(circuit_requests_blocked_) / circuit_requests_total_) * 100.0;

        double packet_util = (packet_bits_transferred_ / (link_capacity_bps_ * sim_duration_)) * 100.0;
        double packet_loss = (static_cast<double>(packets_dropped_) / packets_generated_) * 100.0;
        double avg_delay = (total_packet_delay_ / packets_served_) * 1000.0;
        double var_delay = (total_packet_delay_sq_ / packets_served_) - std::pow(total_packet_delay_ / packets_served_, 2);
        double jitter = std::sqrt(std::max(0.0, var_delay)) * 1000.0;

        std::cout << std::fixed << std::setprecision(2);
        std::cout << "================ РЕЗУЛЬТАТИ СИМУЛЯЦІЇ (100 с) ================\n";
        std::cout << "Кількість підключених джерел: " << num_sources_ << " | Смуга: " << (link_capacity_bps_ / 1e6) << " Мбіт/с\n\n";
        std::cout << "1. КОМУТАЦІЯ КАНАЛІВ (CIRCUIT SWITCHING):\n";
        std::cout << "   • Утилізація вихідного лінка:  " << circuit_util << " %\n";
        std::cout << "   • Загальна кількість викликів: " << circuit_requests_total_ << "\n";
        std::cout << "   • Блокування нових викликів:   " << circuit_block << " % (" << circuit_requests_blocked_ << " відхилено)\n";
        std::cout << "   • Джитер та варіація затримки: 0.00 мс\n\n";
        std::cout << "2. КОМУТАЦІЯ ПАКЕТІВ (PACKET SWITCHING):\n";
        std::cout << "   • Утилізація вихідного лінка:  " << packet_util << " %\n";
        std::cout << "   • Згенеровано пакетів:         " << packets_generated_ << "\n";
        std::cout << "   • Втрати через буфер:          " << packet_loss << " % (" << packets_dropped_ << " втрачено)\n";
        std::cout << "   • Середня затримка пакета:     " << avg_delay << " мс\n";
        std::cout << "   • Джитер (std dev затримки):   " << jitter << " мс\n";
        std::cout << "===============================================================\n";
    }

private:
    int num_sources_;
    double link_capacity_bps_;
    double peak_rate_bps_;
    double sim_duration_;
    int num_circuits_;
    std::vector<bool> circuit_busy_;

    long circuit_requests_total_{0};
    long circuit_requests_blocked_{0};
    double circuit_bits_transferred_{0.0};

    long packets_generated_{0};
    long packets_dropped_{0};
    long packets_served_{0};
    double total_packet_delay_{0.0};
    double total_packet_delay_sq_{0.0};
    double packet_server_busy_until_{0.0};
    double packet_bits_transferred_{0.0};

    std::mt19937 gen_;
};

int main() {
    SwitchingSimulator sim(35, 10000000.0, 1000000.0, 100.0);
    sim.run();
    sim.print_report();
    return 0;
}
