typedef struct {
    long long* tree;    /* Динамічний масив вузлів дерева розмірності 4N */
    size_t n;           /* Кількість елементів у вичатковому масиві */
} segment_tree_t;

typedef struct {
    long long* tree;    /* Динамічний масив агрегованих значень (4N) */
    long long* lazy;    /* Динамічний масив відкладених поміток (4N) */
    size_t n;           /* Кількість елементів у вичатковому масиві */
} lazy_seg_tree_t;
