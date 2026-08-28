/* pid.c */
#include "pid.h"

void pid_init(pid_t *c)
{
    c->I_term = 0.0;
    c->D_term = 0.0f;
    c->y_prev = 0.0f;
    c->manual = false;
    c->man_out = 0.0f;
    c->initialized = false;   /* перший крок лише «зарядить» стан, без ривка */
}
