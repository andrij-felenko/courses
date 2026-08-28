#include <cstdint>
#include <string>
#include <map>
#include <set>
#include <iostream>

// Лічильник, що лише зростає (G-Counter).
struct GCounter {
    std::map<uint32_t, uint64_t> cell;   // id репліки -> скільки нарахувала САМЕ вона

    void inc(uint32_t self, uint64_t by = 1) { cell[self] += by; }   // росте лише СВОЯ комірка

    uint64_t value() const {
        uint64_t s = 0;
        for (const auto& [id, c] : cell) s += c;   // значення = сума всіх комірок
        return s;
    }

    void merge(const GCounter& other) {
        for (const auto& [id, c] : other.cell)
            if (c > cell[id]) cell[id] = c;         // злиття = поелементний максимум
    }
};
