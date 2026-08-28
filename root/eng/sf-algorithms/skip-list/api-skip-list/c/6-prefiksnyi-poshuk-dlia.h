/* Структура зрізу пам'яті для довільних байтових послідовностей */
typedef struct SkipSlice {
    const char* data;
    size_t size;
} SkipSlice;

/* Сигнатура користувацького компаратора */
typedef int (*SkipSliceComparator)(SkipSlice a, SkipSlice b);

/* Пошук першого ключа з заданим префіксом */
bool skiplist_seek_prefix(const SkipList* list, SkipSlice prefix,
                          SkipSliceComparator cmp, int* out_val);
