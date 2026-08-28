void reserve(Vec *v, size_t want) {
    if (want <= v->cap) return;
    int *bigger = malloc(want * sizeof(int));
    for (size_t i = 0; i < v->len; i++)
        bigger[i] = v->data[i];
    v->copies += v->len;
    free(v->data);
    v->data = bigger;
    v->cap  = want;
}

// далі — мільйон додатків БЕЗ жодного росту:
Vec v = {0}; v.factor = 2.0;
reserve(&v, 1000000);         // одне-єдине виділення наперед
for (int i = 0; i < 1000000; i++)
    push(&v, i);              // v->len ніколи не дорівнює v->cap → гілка росту мовчить
