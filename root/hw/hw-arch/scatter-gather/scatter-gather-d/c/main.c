struct sg_seg { uintptr_t addr; size_t len; };   // сегмент: адреса + довжина

size_t sg_total(const struct sg_seg *v, int n) {  // сумарна довжина
    size_t s = 0;
    for (int i = 0; i < n; i++) s += v[i].len;     // O(n)
    return s;
}

// «зʼїсти» переслані bytes: повернути індекс першого несплаченого сегмента
int sg_advance(struct sg_seg *v, int n, size_t bytes) {
    int i = 0;
    while (i < n && bytes >= v[i].len) {            // цілі сегменти — геть
        bytes -= v[i].len;
        i++;
    }
    if (i < n && bytes > 0) {                       // влучений — обрізати
        v[i].addr += bytes;                         // база вперед
        v[i].len  -= bytes;                         // довжина менша
    }
    return i;                                       // звідси продовжити
}
