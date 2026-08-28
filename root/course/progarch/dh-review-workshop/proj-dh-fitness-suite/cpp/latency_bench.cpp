// fitness/latency_bench.cpp — бюджет ЛОКАЛЬНОГО обробітку на хабі
#include <algorithm>
#include <chrono>
#include <cstdio>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using Clock = std::chrono::steady_clock;   // монотонний годинник для інтервалів

struct Command {
    std::string id;
    std::string target;
    std::string action;
};

// Двійник хаба: той самий обробіток, що й у першого вартового, — дедуп за command-id.
class Hub {
    std::unordered_map<std::string, int> actuations_;   // ціль → скільки разів смикнули
    std::unordered_set<std::string> seen_;              // застосовані command-id
public:
    void handle(const Command& cmd) {
        if (seen_.count(cmd.id)) return;                // дубль: стан не рухаємо
        seen_.insert(cmd.id);
        if (cmd.action == "open") actuations_[cmd.target] += 1;
    }
    int actuations(const std::string& target) const {
        auto it = actuations_.find(target);
        return it == actuations_.end() ? 0 : it->second;
    }
};

int main() {
    Hub h;

    for (int i = 0; i < 200; ++i)          // прогрів: кеші, гілки, алокатор
        h.handle({"w-" + std::to_string(i), "front-door", "open"});

    constexpr int n = 5000;
    std::vector<long long> lat(n);          // наносекунди на один обробіток
    for (int i = 0; i < n; ++i) {
        Command cmd{"c-" + std::to_string(i), "front-door", "open"};
        auto start = Clock::now();
        h.handle(cmd);                      // свіжий id щоразу: міряємо РОБОТУ, не дедуп
        lat[i] = std::chrono::duration_cast<std::chrono::nanoseconds>(
                     Clock::now() - start).count();
    }

    // хаб мусив відпрацювати всі 5200 команд — інакше вимір недійсний
    if (h.actuations("front-door") != 200 + n) {
        std::fprintf(stderr, "обробіток не відбувся — вимір порожній\n");
        return 2;
    }

    std::sort(lat.begin(), lat.end());
    long long p95 = lat[static_cast<int>(0.95 * n)];    // ⌊0.95·n⌋ = lat[4750]

    constexpr long long budget_ns = 2 * 1000 * 1000;    // стеля 2 мс на сам обробіток
    if (p95 > budget_ns) {                              // ненульовий вихід → червоне складання
        std::fprintf(stderr, "p95 обробітку %lld нс перевищив бюджет %lld нс\n", p95, budget_ns);
        return 1;
    }
    return 0;
}
