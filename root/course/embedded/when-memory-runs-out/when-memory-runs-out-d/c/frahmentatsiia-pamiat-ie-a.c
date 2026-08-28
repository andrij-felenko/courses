// Пул фіксованих блоків: виділення/звільнення без фрагментації і без пошуку
#define POOL_N     32
#define BLOCK_SZ   64
static uint8_t  pool[POOL_N][BLOCK_SZ];
static uint8_t *free_list[POOL_N];
static int      free_top;

void pool_init(void) {
    for (int i = 0; i < POOL_N; i++) free_list[i] = pool[i];
    free_top = POOL_N;
}
void *pool_alloc(void) {              // миттєво: зняти з вершини списку вільних
    return free_top ? free_list[--free_top] : NULL;
}
void pool_free(void *p) {             // миттєво: повернути у список
    if (free_top < POOL_N) free_list[free_top++] = p;
}
