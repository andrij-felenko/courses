// eas_simulator.cpp — Ідіоматична реалізація мовою C++20
#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <numeric>
#include <cstdint>

constexpr std::uint32_t SCHED_CAPACITY_SCALE = 1024;

struct OppEntry {
    std::uint32_t frequency_khz;
    std::uint32_t power_mw;
    std::uint32_t performance;
};

class PerfDomain {
public:
    PerfDomain(std::string_view name, std::uint32_t capacity_orig, std::vector<OppEntry> opps)
        : name_(name), capacity_orig_(capacity_orig), opps_(std::move(opps)) {}

    [[nodiscard]] std::uint32_t calculate_power(std::uint32_t util_request) const {
        if (util_request == 0) {
            return 0;
        }
        const std::uint32_t req = std::min((util_request * 125) / 100, capacity_orig_);

        auto it = std::find_if(opps_.begin(), opps_.end(), [req](const OppEntry& opp) {
            return opp.performance >= req;
        });

        if (it != opps_.end()) {
            return it->power_mw;
        }
        return opps_.back().power_mw;
    }

    [[nodiscard]] std::string_view name() const noexcept { return name_; }

private:
    std::string name_;
    std::uint32_t capacity_orig_;
    std::vector<OppEntry> opps_;
};

int main(int argc, char* argv[]) {
    if (argc < 4) {
        std::cerr << "Використання: " << argv[0] << " <util_little> <util_big> <task_util>\n";
        return 1;
    }

    const std::uint32_t util_little = std::stoul(argv[1]);
    const std::uint32_t util_big = std::stoul(argv[2]);
    const std::uint32_t task_util = std::stoul(argv[3]);

    const PerfDomain little_domain{"LITTLE Cluster", 400, {
        { 300000,  45, 100 },
        { 600000,  95, 200 },
        { 1200000, 210, 400 }
    }};

    const PerfDomain big_domain{"big Cluster", 1024, {
        { 800000,  450, 500 },
        { 1500000, 900, 800 },
        { 2000000, 1500, 1024 }
    }};

    const std::uint32_t e_current = little_domain.calculate_power(util_little) + 
                                    big_domain.calculate_power(util_big);

    const std::uint32_t e_candA = little_domain.calculate_power(util_little + task_util) + 
                                  big_domain.calculate_power(util_big);
    const std::int64_t delta_A = static_cast<std::int64_t>(e_candA) - static_cast<std::int64_t>(e_current);

    const std::uint32_t e_candB = little_domain.calculate_power(util_little) + 
                                  big_domain.calculate_power(util_big + task_util);
    const std::int64_t delta_B = static_cast<std::int64_t>(e_candB) - static_cast<std::int64_t>(e_current);

    std::cout << "=== Симуляція рішень EAS (C++20) ===\n";
    std::cout << "Поточне споживання системи: " << e_current << " мВт\n";
    std::cout << "Варіант А (на LITTLE): Споживання = " << e_candA << " мВт, ΔE = " << delta_A << " мВт\n";
    std::cout << "Варіант Б (на big):    Споживання = " << e_candB << " мВт, ΔE = " << delta_B << " мВт\n";

    if (delta_A < delta_B) {
        std::cout << "Висновок: Призначити задачу на ядро LITTLE (заощадження " << (delta_B - delta_A) << " мВт)\n";
    } else {
        std::cout << "Висновок: Призначити задачу на ядро big (заощадження " << (delta_A - delta_B) << " мВт)\n";
    }

    return 0;
}
