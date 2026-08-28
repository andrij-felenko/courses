#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct {
    int *parent_or_size;
    size_t capacity;
    size_t num_sets;
} CompactDSU;

CompactDSU *compact_dsu_create(size_t n) {
    CompactDSU *dsu = (CompactDSU *)malloc(sizeof(CompactDSU));
    if (!dsu) return NULL;

    dsu->parent_or_size = (int *)malloc(n * sizeof(int));
    if (!dsu->parent_or_size) {
        free(dsu);
        return NULL;
    }

    dsu->capacity = n;
    dsu->num_sets = n;
    // Значення -1 означає, що вузол є коренем, а розмір множини дорівнює 1
    for (size_t i = 0; i < n; i++) {
        dsu->parent_or_size[i] = -1;
    }
    return dsu;
}

void compact_dsu_destroy(CompactDSU *dsu) {
    if (!dsu) return;
    free(dsu->parent_or_size);
    free(dsu);
}

// Однопрохідне уполовинення шляху (Path Halving)
int compact_dsu_find(CompactDSU *dsu, int x) {
    while (dsu->parent_or_size[x] >= 0) {
        if (dsu->parent_or_size[dsu->parent_or_size[x]] >= 0) {
            dsu->parent_or_size[x] = dsu->parent_or_size[dsu->parent_or_size[x]];
        }
        x = dsu->parent_or_size[x];
    }
    return x;
}

bool compact_dsu_union(CompactDSU *dsu, int x, int y) {
    int root_x = compact_dsu_find(dsu, x);
    int root_y = compact_dsu_find(dsu, y);

    if (root_x == root_y) return false;

    // Менша множина підпорядковується більшій
    if (dsu->parent_or_size[root_x] < dsu->parent_or_size[root_y]) {
        dsu->parent_or_size[root_x] += dsu->parent_or_size[root_y];
        dsu->parent_or_size[root_y] = root_x;
    } else {
        dsu->parent_or_size[root_y] += dsu->parent_or_size[root_x];
        dsu->parent_or_size[root_x] = root_y;
    }

    dsu->num_sets--;
    return true;
}

int compact_dsu_set_size(CompactDSU *dsu, int x) {
    int root = compact_dsu_find(dsu, x);
    return -dsu->parent_or_size[root];
}
