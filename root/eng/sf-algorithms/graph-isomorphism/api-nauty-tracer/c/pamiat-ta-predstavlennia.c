// Спеціальні макроси Nauty для ефективного маніпулювання бітовими векторами:
#define SETWORDSNEEDED(n) (((n) + WORDSIZE - 1) / WORDSIZE)
#define GRAPHROW(g, v, m) ((g) + (size_t)(v) * (m))
#define ADDONEEDGE(g, u, v, m) \
    do { \
        GRAPHROW(g, u, m)[SETWORDINDEX(v)] |= SETBIT(SETBITINDEX(v)); \
        GRAPHROW(g, v, m)[SETWORDINDEX(u)] |= SETBIT(SETBITINDEX(u)); \
    } while(0)
#define DELONEEDGE(g, u, v, m) \
    do { \
        GRAPHROW(g, u, m)[SETWORDINDEX(v)] &= ~SETBIT(SETBITINDEX(v)); \
        GRAPHROW(g, v, m)[SETWORDINDEX(u)] &= ~SETBIT(SETBITINDEX(u)); \
    } while(0)
#define ISELEMENT(setptr, pos) \
    ((*(setptr + SETWORDINDEX(pos)) & SETBIT(SETBITINDEX(pos))) != 0)
