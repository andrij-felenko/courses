#include <stdint.h>
#include <stdlib.h>

enum Kind { ZERO, SUCC };          // мітка різновиду — сума типів руками

typedef struct Nat {
    enum Kind kind;
    struct Nat *pred;              // для SUCC — попередник; для ZERO — NULL
} Nat;

Nat *zero(void) {                  // нуль — комірка без попередника
    Nat *n = malloc(sizeof(Nat));
    n->kind = ZERO;
    n->pred = NULL;
    return n;
}

Nat *succ(Nat *n) {                // наступник — нова комірка, що вказує на n
    Nat *s = malloc(sizeof(Nat));
    s->kind = SUCC;
    s->pred = n;
    return s;
}

uint64_t to_int(const Nat *n) {                     // нуль → 0, інакше 1 + решта
    return n->kind == ZERO ? 0 : 1 + to_int(n->pred);
}

Nat *from_int(uint64_t n) {                         // накрутити Succ n разів
    return n == 0 ? zero() : succ(from_int(n - 1));
}

Nat *copy(const Nat *n) {                            // глибока копія ланцюга
    return n->kind == ZERO ? zero() : succ(copy(n->pred));
}

Nat *add(const Nat *a, const Nat *b) {
    return b->kind == ZERO
        ? copy(a)                    // a + 0 = a (копія: власники різні)
        : succ(add(a, b->pred));     // a + S(b) = S(a + b)
}

Nat *mul(const Nat *a, const Nat *b) {
    return b->kind == ZERO
        ? zero()                     // a · 0 = 0
        : add(mul(a, b->pred), a);   // a·S(b) = a·b + a
}
