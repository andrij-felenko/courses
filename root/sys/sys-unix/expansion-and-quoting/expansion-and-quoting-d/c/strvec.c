#include "strvec.h"

#include <stdlib.h>
#include <string.h>

void strvec_init(strvec *v)
{
    v->item = NULL;
    v->count = 0;
    v->cap = 0;
}

void strvec_free(strvec *v)
{
    for (size_t i = 0; i < v->count; ++i) {
        free(v->item[i]);
    }
    free(v->item);
    strvec_init(v);
}

static int strvec_reserve(strvec *v, size_t need)
{
    if (need <= v->cap) {
        return 0;
    }
    size_t cap = (v->cap != 0) ? v->cap : 8;
    while (cap < need) {
        cap *= 2;
    }
    char **grown = realloc(v->item, cap * sizeof *grown);
    if (grown == NULL) {
        return -1;
    }
    v->item = grown;
    v->cap = cap;
    return 0;
}

int strvec_adopt(strvec *v, char *s)
{
    if (strvec_reserve(v, v->count + 1) != 0) {
        free(s);
        return -1;
    }
    v->item[v->count++] = s;
    return 0;
}

int strvec_push_n(strvec *v, const char *s, size_t n)
{
    char *copy = malloc(n + 1);
    if (copy == NULL) {
        return -1;
    }
    memcpy(copy, s, n);
    copy[n] = '\0';
    return strvec_adopt(v, copy);
}

int strvec_push(strvec *v, const char *s)
{
    return strvec_push_n(v, s, strlen(s));
}
