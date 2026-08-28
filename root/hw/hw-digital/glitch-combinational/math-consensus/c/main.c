#include <stdio.h>
#include <stdbool.h>

// Один добуток-член; C та notC подаємо ОКРЕМО, щоб змоделювати
// момент, коли C вже впав (0), а notC ще не піднявся (0) — це і є "шов".
static inline bool f_plain(bool A, bool B, bool C, bool notC) {
    bool p1 = B && C;        // член B·C
    bool p2 = A && notC;     // член A·C̄
    return p1 || p2;         // OR без накривного члена
}

static inline bool f_fixed(bool A, bool B, bool C, bool notC) {
    bool p1 = B && C;        // B·C
    bool p2 = A && notC;     // A·C̄
    bool pc = A && B;        // накривний член A·B — НЕ залежить від C
    return p1 || p2 || pc;   // OR із накривним членом
}

int main(void) {
    bool A = true, B = true;

    // Три моменти переходу C: 1 -> 0. У "шві" C=0, а notC ще=0 (інвертор не встиг).
    struct { const char *when; bool C, notC; } t[] = {
        { "до    (C=1)", true,  false },  // усталено: C=1, notC=0
        { "шов   (C впав, C̄ ще ні)", false, false },  // небезпечна мить
        { "після (C=0)", false, true  },  // усталено: C=0, notC=1
    };

    for (int i = 0; i < 3; i++) {
        bool plain = f_plain(A, B, t[i].C, t[i].notC);
        bool fixed = f_fixed(A, B, t[i].C, t[i].notC);
        printf("%-28s  без члена=%d   з членом=%d\n",
               t[i].when, plain, fixed);
    }
    return 0;
}
