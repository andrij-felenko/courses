#include <stddef.h>
#include <stdint.h>

typedef struct {
    int32_t candidate;
    size_t count;
} PartialMajority;

/* Асоціативний оператор злиття двох локальних результатів */
PartialMajority merge_majority_states(PartialMajority a, PartialMajority b) {
    if (a.count == 0) return b;
    if (b.count == 0) return a;

    if (a.candidate == b.candidate) {
        PartialMajority res = { a.candidate, a.count + b.count };
        return res;
    }

    if (a.count >= b.count) {
        PartialMajority res = { a.candidate, a.count - b.count };
        return res;
    } else {
        PartialMajority res = { b.candidate, b.count - a.count };
        return res;
    }
}
