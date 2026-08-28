typedef struct {
    size_t total;       // увесь розмір ділянки, байтів
    size_t free_min;    // найменше непочате (недоторканий 0xA5 від дна)
    size_t used_peak;   // пік ужитого = total − free_min
} stack_usage_t;

stack_usage_t stack_measure(void) {
    stack_usage_t r;
    r.total = (size_t)(stack_hi - stack_lo);

    // йдемо від дна вгору, рахуючи цілий візерунок
    size_t intact = 0;
    for (uint8_t *p = stack_lo; p < stack_hi; ++p) {
        if (*p != STACK_PATTERN) break;   // перший НЕ-0xA5 — найглибша межа
        ++intact;
    }
    r.free_min = intact;
    r.used_peak = r.total - intact;
    return r;
}
