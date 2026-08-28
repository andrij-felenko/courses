#include <vector>
#include <numeric>

struct Run { bool halted; uint64_t steps; uint64_t ones; };

// Женемо `table` з чистої стрічки, не більш як `cap` кроків.
// Повертає (зупинилась?, кроків, одиниць).
Run simulate(const std::vector<uint32_t>& table, uint32_t n, uint64_t cap) {
    size_t width = 2 * cap + 3;
    std::vector<uint8_t> tape(width, 0);   // стрічка — щільний масив
    size_t h = cap + 1;                    // голівка стартує в центрі
    uint32_t st = 0;                       // стан A
    uint64_t steps = 0;
    for (;;) {
        uint32_t a = table[st * 2 + tape[h]];
        tape[h] = write(a);
        ++steps;
        if (target(a) == n) {              // перейшли в стан зупинки
            uint64_t ones = std::accumulate(tape.begin(), tape.end(), uint64_t{0});
            return {true, steps, ones};
        }
        h = (size_t)((int64_t)h + dir(a)); // зсув на одну клітинку
        st = target(a);
        if (steps >= cap) {                // СТЕЛЯ — далі не женемо
            uint64_t ones = std::accumulate(tape.begin(), tape.end(), uint64_t{0});
            return {false, steps, ones};
        }
    }
}
