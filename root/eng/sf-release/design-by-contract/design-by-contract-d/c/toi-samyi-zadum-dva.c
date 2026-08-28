#include <assert.h>
#include <stdint.h>

#define CAP 64

typedef struct {
    int32_t  data[CAP];
    uint16_t count;
} stack_t;

// ІНВАРІАНТ класу → окрема функція, бо мова не покличе її сама.
static inline bool stk_invariant(const stack_t *s) {
    return s->count <= CAP;          // count_in_range
}

void stk_push(stack_t *s, int32_t item) {
    uint16_t count_before = s->count;     // ← знімок «до» руками: тут немає `old`
    assert(stk_invariant(s));             // інваріант на вході
    assert(s->count < CAP);               // ПЕРЕДУМОВА: not_full

    s->data[s->count] = item;
    s->count++;

    assert(s->count == count_before + 1); // ПОСТУМОВА: one_more (через знімок)
    assert(s->data[s->count - 1] == item);// ПОСТУМОВА: item_added
    assert(stk_invariant(s));             // інваріант на виході
}
