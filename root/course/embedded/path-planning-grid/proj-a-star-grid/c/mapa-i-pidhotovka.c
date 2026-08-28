// Скинути робочі масиви перед новим пошуком. Мапу (grid) не чіпаємо.
static void astar_reset(void) {
    for (int i = 0; i < N_CELLS; i++) {
        g_cost[i]    = INF;
        came_from[i] = -1;
    }
    heap_len = 0;
}

// Чи в межах сітки і чи вільна клітина.
static inline bool cell_free(int x, int y) {
    if (x < 0 || x >= GRID_W || y < 0 || y >= GRID_H) return false;
    return grid[idx_of(x, y)] == 0;
}
