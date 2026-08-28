typedef struct {
    uint32_t id;         // Унікальний ідентифікатор об'єкта/документа
    size_t count;        // Кількість унікальних елементів у множині
    uint64_t *elements;  // Відсортований масив 64-бітних хешів елементів
} jaccard_set_t;

typedef struct {
    uint32_t id;         // Ідентифікатор об'єкта
    size_t k_len;        // Кількість хеш-значень (розмір масиву sig)
    uint64_t *sig;       // Динамічний масив мінімальних хешів (розміру k_len)
} jaccard_signature_t;

typedef struct {
    uint32_t id_a;       // Ідентифікатор першого об'єкта
    uint32_t id_b;       // Ідентифікатор другого об'єкта
    double similarity;   // Обчислений коефіцієнт схожості Жаккара J ∈ [0, 1]
} jaccard_match_t;
