#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
#include <string_view>
#include <numeric>
#include <format>

// Тривалість одного символу 802.11ax (12.8 мкс + 0.8 мкс GI) у секундах
constexpr double T_SYM_SEC = 13.6e-6;

struct ClientRequest {
    int client_id;
    size_t buffer_bytes;
    int mcs;
    bool latency_sensitive;
};

struct RUAllocation {
    int client_id;
    int ru_type;
    size_t allocated_bytes;
    double frame_duration_us;
};

class Wifi6RuScheduler {
public:
    explicit Wifi6RuScheduler(int bandwidth_mhz = 20) : bandwidth_mhz_(bandwidth_mhz) {}

    static constexpr int get_data_subcarriers(int ru_type) noexcept {
        switch (ru_type) {
            case 26:  return 24;
            case 52:  return 48;
            case 106: return 102;
            case 242: return 234;
            default:  return 24;
        }
    }

    static constexpr double get_bits_per_subcarrier(int mcs) noexcept {
        switch (mcs) {
            case 0:  return 0.5;   // BPSK 1/2
            case 3:  return 2.5;   // 16-QAM 1/2
            case 7:  return 4.5;   // 64-QAM 5/6
            case 9:  return 6.667; // 256-QAM 5/6
            case 11: return 8.333; // 1024-QAM 5/6
            default: return 1.0;
        }
    }

    double calculate_bits_per_symbol(int ru_type, int mcs) const noexcept {
        return get_data_subcarriers(ru_type) * get_bits_per_subcarrier(mcs);
    }

    std::pair<std::string, std::vector<RUAllocation>> schedule_20mhz(std::vector<ClientRequest> clients) const {
        if (clients.empty()) {
            return {"NO_CLIENTS", {}};
        }

        // Сортування за пріоритетом затримки та розміром буфера
        std::sort(clients.begin(), clients.end(), [](const ClientRequest& a, const ClientRequest& b) {
            if (a.latency_sensitive != b.latency_sensitive) {
                return a.latency_sensitive > b.latency_sensitive;
            }
            return a.buffer_bytes < b.buffer_bytes;
        });

        const size_t num_clients = clients.size();
        std::string pattern_name;
        int ru_type = 26;
        size_t max_slots = 1;

        if (num_clients >= 5) {
            pattern_name = "9xRU26";
            ru_type = 26;
            max_slots = 9;
        } else if (num_clients >= 3) {
            pattern_name = "4xRU52";
            ru_type = 52;
            max_slots = 4;
        } else if (num_clients == 2) {
            pattern_name = "2xRU106";
            ru_type = 106;
            max_slots = 2;
        } else {
            pattern_name = "1xRU242";
            ru_type = 242;
            max_slots = 1;
        }

        const size_t active_count = std::min(num_clients, max_slots);
        size_t max_symbols = 0;

        for (size_t i = 0; i < active_count; ++i) {
            const double bits_per_sym = calculate_bits_per_symbol(ru_type, clients[i].mcs);
            const double total_bits = static_cast<double>(clients[i].buffer_bytes * 8);
            const size_t needed_syms = static_cast<size_t>(std::ceil(total_bits / bits_per_sym));
            max_symbols = std::max(max_symbols, needed_syms);
        }

        const double frame_duration_us = max_symbols * T_SYM_SEC * 1e6;
        std::vector<RUAllocation> allocations;
        allocations.reserve(active_count);

        for (size_t i = 0; i < active_count; ++i) {
            const double bits_per_sym = calculate_bits_per_symbol(ru_type, clients[i].mcs);
            const size_t capacity_bytes = static_cast<size_t>((max_symbols * bits_per_sym) / 8.0);
            const size_t allocated_bytes = std::min(clients[i].buffer_bytes, capacity_bytes);

            allocations.push_back(RUAllocation{
                .client_id = clients[i].client_id,
                .ru_type = ru_type,
                .allocated_bytes = allocated_bytes,
                .frame_duration_us = frame_duration_us
            });
        }

        return {pattern_name, allocations};
    }

private:
    int bandwidth_mhz_;
};

int main() {
    std::vector<ClientRequest> clients = {
        {.client_id = 1, .buffer_bytes = 120, .mcs = 7,  .latency_sensitive = true},
        {.client_id = 2, .buffer_bytes = 80,  .mcs = 9,  .latency_sensitive = true},
        {.client_id = 3, .buffer_bytes = 500, .mcs = 11, .latency_sensitive = false},
        {.client_id = 4, .buffer_bytes = 300, .mcs = 7,  .latency_sensitive = false}
    };

    Wifi6RuScheduler scheduler(20);
    auto [pattern, allocations] = scheduler.schedule_20mhz(clients);

    std::cout << "--- Результат планування Wi-Fi 6 OFDMA (Конфігурація: " << pattern << ") ---
";
    for (const auto& alloc : allocations) {
        std::cout << "Клієнт #" << alloc.client_id
                  << ": RU" << alloc.ru_type
                  << " | Передано: " << alloc.allocated_bytes << " байт"
                  << " | Тривалість кадру: " << alloc.frame_duration_us << " мкс
";
    }

    return 0;
}
