#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#define MAX_VARS 64
#define MAX_BLOCKS 16
#define MAX_EDGES 8

typedef struct {
    uint64_t bits;
} BitSet;

static inline BitSet bitset_create(void) {
    BitSet s = {0};
    return s;
}

static inline void bitset_set(BitSet *s, int var_id) {
    s->bits |= (1ULL << var_id);
}

static inline bool bitset_get(BitSet s, int var_id) {
    return (s.bits & (1ULL << var_id)) != 0;
}

static inline BitSet bitset_union(BitSet a, BitSet b) {
    BitSet res = { a.bits | b.bits };
    return res;
}

static inline BitSet bitset_diff(BitSet a, BitSet b) {
    BitSet res = { a.bits & ~b.bits };
    return res;
}

static inline bool bitset_equal(BitSet a, BitSet b) {
    return a.bits == b.bits;
}

typedef struct {
    int id;
    BitSet use;
    BitSet def;
    BitSet in;
    BitSet out;

    int succ_count;
    int succ[MAX_EDGES];
    int pred_count;
    int pred[MAX_EDGES];
} Block;

typedef struct {
    int num_blocks;
    int num_vars;
    Block blocks[MAX_BLOCKS];
} CFG;

void cfg_init(CFG *cfg, int num_blocks, int num_vars) {
    cfg->num_blocks = num_blocks;
    cfg->num_vars = num_vars;
    for (int i = 0; i < num_blocks; ++i) {
        cfg->blocks[i].id = i;
        cfg->blocks[i].use = bitset_create();
        cfg->blocks[i].def = bitset_create();
        cfg->blocks[i].in  = bitset_create();
        cfg->blocks[i].out = bitset_create();
        cfg->blocks[i].succ_count = 0;
        cfg->blocks[i].pred_count = 0;
    }
}

void cfg_add_edge(CFG *cfg, int from, int to) {
    Block *src = &cfg->blocks[from];
    Block *dst = &cfg->blocks[to];
    src->succ[src->succ_count++] = to;
    dst->pred[dst->pred_count++] = from;
}

void solve_live_variables(CFG *cfg) {
    int worklist[MAX_BLOCKS * 4];
    bool in_worklist[MAX_BLOCKS] = {false};
    int head = 0, tail = 0;

    /* Додаємо всі блоки у робочий список */
    for (int i = 0; i < cfg->num_blocks; ++i) {
        worklist[tail++] = i;
        in_worklist[i] = true;
    }

    while (head < tail) {
        int b_id = worklist[head++];
        in_worklist[b_id] = false;
        Block *b = &cfg->blocks[b_id];

        /* OUT[B] = ∪ IN[Succ] */
        BitSet new_out = bitset_create();
        for (int i = 0; i < b->succ_count; ++i) {
            int s_id = b->succ[i];
            new_out = bitset_union(new_out, cfg->blocks[s_id].in);
        }
        b->out = new_out;

        /* IN[B] = USE[B] ∪ (OUT[B] \ DEF[B]) */
        BitSet new_in = bitset_union(b->use, bitset_diff(b->out, b->def));

        /* Якщо IN[B] змінився, додаємо всіх попередників до робочого списку */
        if (!bitset_equal(new_in, b->in)) {
            b->in = new_in;
            for (int i = 0; i < b->pred_count; ++i) {
                int p_id = b->pred[i];
                if (!in_worklist[p_id]) {
                    worklist[tail++] = p_id;
                    in_worklist[p_id] = true;
                }
            }
        }
    }
}

void print_results(const CFG *cfg) {
    printf("=== Результати аналізу Live Variables ===\n");
    for (int i = 0; i < cfg->num_blocks; ++i) {
        const Block *b = &cfg->blocks[i];
        printf("Блок B%d:\n", b->id);
        printf("  USE: { ");
        for (int v = 0; v < cfg->num_vars; ++v) {
            if (bitset_get(b->use, v)) printf("v%d ", v);
        }
        printf("}\n  DEF: { ");
        for (int v = 0; v < cfg->num_vars; ++v) {
            if (bitset_get(b->def, v)) printf("v%d ", v);
        }
        printf("}\n  IN : { ");
        for (int v = 0; v < cfg->num_vars; ++v) {
            if (bitset_get(b->in, v)) printf("v%d ", v);
        }
        printf("}\n  OUT: { ");
        for (int v = 0; v < cfg->num_vars; ++v) {
            if (bitset_get(b->out, v)) printf("v%d ", v);
        }
        printf("}\n\n");
    }
}

int main(void) {
    /* 4 блоки, 3 змінні: v0 (a), v1 (b), v2 (c) */
    CFG cfg;
    cfg_init(&cfg, 4, 3);

    /* B0 (Entry): def = {v0, v1} (a = 1; b = 2;) */
    bitset_set(&cfg.blocks[0].def, 0);
    bitset_set(&cfg.blocks[0].def, 1);

    /* B1 (Loop Header): use = {v0}, def = {v2} (c = a + 1; if ...) */
    bitset_set(&cfg.blocks[1].use, 0);
    bitset_set(&cfg.blocks[1].def, 2);

    /* B2 (Loop Body): use = {v1, v2}, def = {v0} (a = b + c;) */
    bitset_set(&cfg.blocks[2].use, 1);
    bitset_set(&cfg.blocks[2].use, 2);
    bitset_set(&cfg.blocks[2].def, 0);

    /* B3 (Exit): use = {v2} (return c;) */
    bitset_set(&cfg.blocks[3].use, 2);

    /* Ребра: B0 -> B1; B1 -> B2, B1 -> B3; B2 -> B1 */
    cfg_add_edge(&cfg, 0, 1);
    cfg_add_edge(&cfg, 1, 2);
    cfg_add_edge(&cfg, 1, 3);
    cfg_add_edge(&cfg, 2, 1);

    solve_live_variables(&cfg);
    print_results(&cfg);

    return 0;
}
