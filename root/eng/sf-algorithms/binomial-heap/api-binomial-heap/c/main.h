// Створення та звільнення пам'яті
BinomialNode* binomial_heap_create(void);
void binomial_heap_free(BinomialNode* heap);

// Основні операції над купою
BinomialNode* binomial_heap_insert(BinomialNode* heap, int key);
BinomialNode* binomial_heap_union(BinomialNode* h1, BinomialNode* h2);
BinomialNode* binomial_heap_find_min(BinomialNode* heap);
BinomialNode* binomial_heap_extract_min(BinomialNode* heap, int* out_min_key);
void binomial_heap_decrease_key(BinomialNode* node, int new_key);
BinomialNode* binomial_heap_delete(BinomialNode* heap, BinomialNode* node);
