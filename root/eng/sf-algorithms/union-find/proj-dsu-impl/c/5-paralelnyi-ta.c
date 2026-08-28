#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdatomic.h>

typedef struct {
    _Atomic int *parent;
    size_t capacity;
} LockFreeDSU;

LockFreeDSU *lockfree_dsu_create(size_t n) {
    LockFreeDSU *dsu = (LockFreeDSU *)malloc(sizeof(LockFreeDSU));
    if (!dsu) return NULL;

    dsu->parent = (_Atomic int *)malloc(n * sizeof(_Atomic int));
    if (!dsu->parent) {
        free(dsu);
        return NULL;
    }

    dsu->capacity = n;
    for (size_t i = 0; i < n; i++) {
        atomic_init(&dsu->parent[i], (int)i);
    }
    return dsu;
}

void lockfree_dsu_destroy(LockFreeDSU *dsu) {
    if (!dsu) return;
    free(dsu->parent);
    free(dsu);
}

// Атомарне уполовинення шляху
int lockfree_dsu_find(LockFreeDSU *dsu, int x) {
    while (true) {
        int p = atomic_load(&dsu->parent[x]);
        if (p == x) return x;

        int grand_p = atomic_load(&dsu->parent[p]);
        // Спроба атомарно оновити покажчик батька на діда
        atomic_compare_exchange_weak(&dsu->parent[x], &p, grand_p);
        x = atomic_load(&dsu->parent[x]);
    }
}

bool lockfree_dsu_union(LockFreeDSU *dsu, int x, int y) {
    while (true) {
        int root_x = lockfree_dsu_find(dsu, x);
        int root_y = lockfree_dsu_find(dsu, y);

        if (root_x == root_y) return false;

        // Приєднуємо корінь з меншим індексом до кореня з більшим для уникнення циклів
        if (root_x > root_y) {
            int temp = root_x;
            root_x = root_y;
            root_y = temp;
        }

        // Атомарна спроба зробити root_x батьком root_y
        int expected = root_y;
        if (atomic_compare_exchange_strong(&dsu->parent[root_y], &expected, root_x)) {
            return true;
        }
    }
}
