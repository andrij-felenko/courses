int main(void) {
    Point pts[] = {
        {{50.0, 45.0}, 1},
        {{25.0, 65.0}, 2},
        {{75.0, 25.0}, 3},
        {{12.0, 30.0}, 4},
        {{38.0, 85.0}, 5},
        {{62.0, 75.0}, 6},
        {{88.0, 12.0}, 7}
    };
    size_t n = sizeof(pts) / sizeof(pts[0]);

    KDTree* tree = kdtree_create(pts, n);
    if (!tree) {
        fprintf(stderr, "Помилка виділення пам'яті для K-d дерева\n");
        return 1;
    }

    /* 1. Пошук найближчого сусіда для Q(48, 42) */
    Point query = {{48.0, 42.0}, 0};
    double dist_sq = 0.0;
    const Point* nn = kdtree_nearest_neighbor(tree, &query, &dist_sq);

    if (nn) {
        printf("Найближчий сусід: ID=%d (%.1f, %.1f), dist_sq=%.2f\n",
               nn->id, nn->coords[0], nn->coords[1], dist_sq);
    }

    /* 2. Діапазонний пошук у вікні [20, 70] x [20, 70] */
    Point min_box = {{20.0, 20.0}, 0};
    Point max_box = {{70.0, 70.0}, 0};
    Point range_results[10];
    size_t found = kdtree_range_query(tree, &min_box, &max_box, range_results, 10);

    printf("Знайдено точок у діапазоні: %zu\n", found);
    for (size_t i = 0; i < found; ++i) {
        printf("  - ID=%d (%.1f, %.1f)\n",
               range_results[i].id, range_results[i].coords[0], range_results[i].coords[1]);
    }

    kdtree_free(tree);
    return 0;
}
