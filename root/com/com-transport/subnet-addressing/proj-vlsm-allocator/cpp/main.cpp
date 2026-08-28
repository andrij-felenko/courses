#include <iostream>
#include <vector>
#include <string>
#include <string_view>
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <cstdint>
#include <bit>
#include <expected>

struct IPv4Address {
    uint32_t val{0};

    constexpr IPv4Address() = default;
    constexpr explicit IPv4Address(uint32_t v) : val(v) {}

    static std::expected<IPv4Address, std::string> from_string(std::string_view str) {
        unsigned int b3, b2, b1, b0;
        char dot1, dot2, dot3;
        std::istringstream iss{std::string(str)};
        if (!(iss >> b3 >> dot1 >> b2 >> dot2 >> b1 >> dot3 >> b0) ||
            dot1 != '.' || dot2 != '.' || dot3 != '.' ||
            b3 > 255 || b2 > 255 || b1 > 255 || b0 > 255) {
            return std::unexpected("Некоректний формат IP-адреси");
        }
        uint32_t num = (static_cast<uint32_t>(b3) << 24) |
                       (static_cast<uint32_t>(b2) << 16) |
                       (static_cast<uint32_t>(b1) << 8)  |
                       static_cast<uint32_t>(b0);
        return IPv4Address(num);
    }

    [[nodiscard]] std::string to_string() const {
        std::ostringstream oss;
        oss << ((val >> 24) & 0xFF) << '.'
            << ((val >> 16) & 0xFF) << '.'
            << ((val >> 8)  & 0xFF) << '.'
            << (val & 0xFF);
        return oss.str();
    }
};

struct SubnetRequest {
    std::string name;
    uint32_t required_hosts{0};
    bool is_p2p_31{false};
};

struct AllocatedSubnet {
    std::string name;
    uint8_t prefix_len{0};
    uint32_t allocated_size{0};
    IPv4Address network;
    IPv4Address mask;
    IPv4Address first_host;
    IPv4Address last_host;
    IPv4Address broadcast;
    bool is_rfc3021{false};
};

class VLSMPlanner {
public:
    static std::expected<std::vector<AllocatedSubnet>, std::string>
    calculate(IPv4Address root_ip, uint8_t root_prefix, std::vector<SubnetRequest> requests) {
        if (root_prefix > 32) {
            return std::unexpected("Довжина префікса не може перевищувати 32");
        }

        uint32_t root_size = (root_prefix == 0) ? 0xFFFFFFFF : (1U << (32 - root_prefix));
        uint32_t pool_start = root_ip.val & ~((root_prefix == 32) ? 0 : (root_size - 1));
        uint64_t pool_end = static_cast<uint64_t>(pool_start) + root_size - 1;

        struct SizingItem {
            SubnetRequest req;
            uint8_t prefix;
            uint32_t size;
        };

        std::vector<SizingItem> items;
        items.reserve(requests.size());

        for (const auto &r : requests) {
            if (r.is_p2p_31 && r.required_hosts == 2) {
                items.push_back({r, 31, 2});
            } else {
                uint32_t needed = r.required_hosts + 2;
                // std::bit_width обчислює мінімальну кількість бітів для представлення числа
                uint8_t h = (needed <= 1) ? 1 : static_cast<uint8_t>(std::bit_width(needed - 1));
                uint8_t p = 32 - h;
                items.push_back({r, p, 1U << h});
            }
        }

        // Сортування за спаданням розміру блоку
        std::ranges::sort(items, [](const SizingItem &a, const SizingItem &b) {
            return a.size > b.size;
        });

        std::vector<AllocatedSubnet> result;
        result.reserve(items.size());

        uint64_t current_ip = pool_start;

        for (const auto &item : items) {
            uint64_t sz = item.size;
            // Вирівнювання адреси за межею блоку степеня двійки
            current_ip = (current_ip + sz - 1) & ~(sz - 1);

            if (current_ip + sz - 1 > pool_end) {
                return std::unexpected("Адресний пул вичерпано для підмережі: " + item.req.name);
            }

            uint32_t net_val = static_cast<uint32_t>(current_ip);
            uint32_t mask_val = (item.prefix == 0) ? 0 : (~0U << (32 - item.prefix));

            AllocatedSubnet sub;
            sub.name = item.req.name;
            sub.prefix_len = item.prefix;
            sub.allocated_size = item.size;
            sub.network = IPv4Address(net_val);
            sub.mask = IPv4Address(mask_val);

            if (item.prefix == 31) {
                sub.is_rfc3021 = true;
                sub.first_host = IPv4Address(net_val);
                sub.last_host = IPv4Address(net_val + 1);
                sub.broadcast = IPv4Address(0);
            } else {
                sub.is_rfc3021 = false;
                sub.first_host = IPv4Address(net_val + 1);
                sub.last_host = IPv4Address(net_val + item.size - 2);
                sub.broadcast = IPv4Address(net_val + item.size - 1);
            }

            result.push_back(sub);
            current_ip += sz;
        }

        return result;
    }
};

int main() {
    auto root_ip = IPv4Address::from_string("10.100.0.0");
    if (!root_ip) {
        std::cerr << root_ip.error() << std::endl;
        return 1;
    }

    std::vector<SubnetRequest> requests = {
        { "Server Farm",      500,  false },
        { "Engineering Dept", 220,  false },
        { "Sales Dept",       120,  false },
        { "Guest Wi-Fi",      1000, false },
        { "Core Link A-B",    2,    true  },
        { "Core Link B-C",    2,    true  }
    };

    auto plan = VLSMPlanner::calculate(*root_ip, 18, std::move(requests));
    if (!plan) {
        std::cerr << "Помилка планування: " << plan.error() << std::endl;
        return 1;
    }

    std::cout << "Результати планування VLSM для пулу 10.100.0.0/18 (C++20):\n";
    std::cout << std::left << std::setw(18) << "Підмережа"
              << std::setw(8)  << "Префікс"
              << std::setw(16) << "Мережа"
              << std::setw(16) << "Маска"
              << std::setw(33) << "Діапазон хостів"
              << std::setw(16) << "Broadcast" << "\n";
    std::cout << std::string(107, '-') << "\n";

    for (const auto &sub : *plan) {
        std::string range = sub.first_host.to_string() + " - " + sub.last_host.to_string();
        std::string brd = sub.is_rfc3021 ? "N/A (RFC 3021)" : sub.broadcast.to_string();

        std::cout << std::left << std::setw(18) << sub.name
                  << "/" << std::setw(7) << static_cast<int>(sub.prefix_len)
                  << std::setw(16) << sub.network.to_string()
                  << std::setw(16) << sub.mask.to_string()
                  << std::setw(33) << range
                  << std::setw(16) << brd << "\n";
    }
    return 0;
}
