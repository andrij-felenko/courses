// netlist_audit.cpp - сучасна C++ верифікація парності сигналів
#include <iostream>
#include <string>
#include <string_view>
#include <vector>
#include <unordered_set>
#include <algorithm>

class NetlistAuditor {
public:
    void add_net(std::string_view net_name) {
        nets_.emplace(net_name);
    }

    [[nodiscard]] int verify_pairs() const {
        std::cout << "=== АУДИТ ПАРНОСТІ СИГНАЛІВ СХЕМИ (C++) ===\n";
        int issues = 0;

        for (const auto& net : nets_) {
            // Перевірка TX -> RX
            if (net.ends_with("_TX")) {
                std::string expected_rx = net.substr(0, net.size() - 3) + "_RX";
                if (!nets_.contains(expected_rx)) {
                    std::cout << "[ПОМИЛКА] Знайдено сигнал '" << net
                              << "', але відсутній парний '" << expected_rx << "'\n";
                    ++issues;
                }
            }

            // Перевірка диференційних пар _P -> _N
            if (net.ends_with("_P")) {
                std::string expected_n = net.substr(0, net.size() - 2) + "_N";
                if (!nets_.contains(expected_n)) {
                    std::cout << "[ПОМИЛКА] Диференційна лінія '" << net
                              << "' не має пари '" << expected_n << "'\n";
                    ++issues;
                }
            }
        }

        if (issues == 0) {
            std::cout << "[OK] Усі інтерфейсні та диференційні пари верифіковано.\n";
        } else {
            std::cout << "[УВАГА] Виявлено дефектів: " << issues
                      << ". Перевірте опечатки в назвах міток!\n";
        }
        return issues;
    }

private:
    std::unordered_set<std::string> nets_;
};

int main() {
    NetlistAuditor auditor;
    auditor.add_net("MCU_UART1_TX");
    auditor.add_net("MCU_UART1_RX");
    auditor.add_net("DEBUG_UART_TX"); // Відсутній RX
    auditor.add_net("USB_DP_P");
    auditor.add_net("USB_DP_N");
    auditor.add_net("CAN_P");         // Відсутній CAN_N

    auditor.verify_pairs();
    return 0;
}
