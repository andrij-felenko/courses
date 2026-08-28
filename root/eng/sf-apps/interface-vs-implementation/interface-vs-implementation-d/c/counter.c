// counter.c — тут, і лише тут, відома справжня будова.
#include "counter.h"
#include <stdlib.h>

struct Counter { int n; };        // приватне рішення: поки що просте int

Counter *counter_new(void)            { Counter *c = malloc(sizeof *c); c->n = 0; return c; }
void     counter_inc(Counter *c)      { c->n++; }
int      counter_value(const Counter *c) { return c->n; }
void     counter_free(Counter *c)     { free(c); }
