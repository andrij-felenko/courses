// Скільки звернень до пам'яті коштує один промах TLB при вкладеному
// обході: g рівнів у гостя, h — у хоста.
static inline int nested_walk_accesses(int g, int h) {
    return (g + 1) * (h + 1) - 1;          // = g*h + g + h
}

// Середня ціна перекладу з урахуванням TLB.
// p — частка промахів, c_dram — такти на одне звернення в RAM.
double avg_translate_cycles(int g, int h, double p, double c_dram) {
    double c_hit  = 1.0;                              // влучання ≈ безкоштовне
    double c_miss = nested_walk_accesses(g, h) * c_dram;
    return (1.0 - p) * c_hit + p * c_miss;
}
