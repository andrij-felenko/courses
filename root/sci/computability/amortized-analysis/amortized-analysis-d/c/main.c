typedef struct {
    int *data;      // блок пам'яті під елементи
    int  len;       // скільки зайнято
    int  cap;       // скільки вміщає
} Vec;

void push(Vec *v, int x) {
    if (v->len == v->cap) {                 // місця немає — треба рости
        int newcap = v->cap ? v->cap * 2 : 1;
        int *bigger = malloc(newcap * sizeof(int));
        for (int i = 0; i < v->len; i++)    // ← копіюємо ВСЕ: це O(len)
            bigger[i] = v->data[i];
        free(v->data);
        v->data = bigger;
        v->cap  = newcap;
    }
    v->data[v->len++] = x;                   // дешевий запис: O(1)
}
