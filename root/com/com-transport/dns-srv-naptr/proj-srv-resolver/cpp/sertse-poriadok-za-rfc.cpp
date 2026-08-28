#include <algorithm>   // stable_sort, shuffle, stable_partition, lower_bound
#include <random>
#include <string>
#include <vector>

// Target — одна ціль SRV: куди йти, на який порт і з яким місцем у черзі.
struct Target {
    std::string       host;          // канонічне ім'я вузла, з крапкою на кінці
    uint16_t          port     = 0;
    uint16_t          priority = 0;
    uint16_t          weight   = 0;
    std::vector<Addr> addrs;         // заповнюється на третьому кроці ланцюга
};

// Один генератор на нитку. Сіяти сталою — це дати всім клієнтам світу
// однаковий жереб і зібрати весь потік на одному вузлі.
static std::mt19937& prng() {
    static thread_local std::mt19937 g{std::random_device{}()};
    return g;
}

// order_rfc2782 віддає повний порядок обходу: спершу за пріоритетом,
// а всередині кожного пріоритету — жеребкуванням за вагою.
std::vector<Target> order_rfc2782(std::vector<Target> rrs) {
    std::stable_sort(rrs.begin(), rrs.end(),
                     [](const Target& a, const Target& b) { return a.priority < b.priority; });

    std::vector<Target> out;
    out.reserve(rrs.size());

    for (auto it = rrs.begin(); it != rrs.end();) {
        const uint16_t p = it->priority;
        auto end = std::find_if(it, rrs.end(), [p](const Target& t) { return t.priority != p; });
        std::vector<Target> group(std::make_move_iterator(it), std::make_move_iterator(end));
        it = end;

        // «У будь-якому порядку» зі специфікації — не декорація: це єдине
        // джерело випадковості для групи, у якій усі ваги нульові.
        std::shuffle(group.begin(), group.end(), prng());

        // Нульові ваги — на початок: лише там їхня наростальна сума дорівнює нулю.
        std::stable_partition(group.begin(), group.end(),
                              [](const Target& t) { return t.weight == 0; });

        while (!group.empty()) {
            std::vector<unsigned> running(group.size());
            unsigned sum = 0;
            for (std::size_t k = 0; k < group.size(); ++k) {
                sum += group[k].weight;
                running[k] = sum;
            }

            std::uniform_int_distribution<unsigned> dice(0, sum);  // [0 … sum] ВКЛЮЧНО
            const unsigned r = dice(prng());
            const auto pick = std::lower_bound(running.begin(), running.end(), r) - running.begin();

            out.push_back(std::move(group[pick]));
            group.erase(group.begin() + pick);   // викинули — і рахуємо наново
        }
    }
    return out;
}
