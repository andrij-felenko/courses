/* Інтерфейс Disjoint Sparse Table мовою C */
typedef int32_t (*st_semigroup_op_t)(int32_t a, int32_t b);

typedef struct {
    size_t n;
    size_t padded_n;
    size_t levels;
    st_semigroup_op_t op;
    int32_t *table;
} disjoint_sparse_table_t;

disjoint_sparse_table_t *dst_create(const int32_t *arr, size_t n, st_semigroup_op_t op);
bool dst_query(const disjoint_sparse_table_t *dst, size_t l, size_t r, int32_t *result);
void dst_destroy(disjoint_sparse_table_t *dst);
