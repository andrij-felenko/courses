// Закритий набір — по біту на клітину. Компактно і швидко.
static uint8_t closed[(N_CELLS + 7) / 8];
static inline void closed_set(int idx)  { closed[idx >> 3] |=  (1u << (idx & 7)); }
static inline bool closed_get(int idx)  { return closed[idx >> 3] & (1u << (idx & 7)); }
static inline void closed_clear_all(void) {
    for (unsigned i = 0; i < sizeof closed; i++) closed[i] = 0;
}

// Пошук шляху від (sx,sy) до (gx,gy). Повертає true, якщо шлях є;
// came_from[] тоді містить крихти для відновлення.
static bool astar_search(int sx, int sy, int gx, int gy) {
    astar_reset();
    closed_clear_all();

    if (!cell_free(sx, sy) || !cell_free(gx, gy)) return false;  // старт/ціль у стіні

    int start = idx_of(sx, sy);
    g_cost[start] = 0.0f;
    heap_push(start, heuristic(sx, sy, gx, gy));   // f старту = 0 + h

    while (!heap_empty()) {
        int32_t cur = heap_pop_min();              // найдешевша за f

        if (closed_get(cur)) continue;             // застарілий дублікат — викинути
        if (cur == idx_of(gx, gy)) return true;    // дійшли до цілі

        closed_set(cur);                           // розкриваємо остаточно
        int cx = x_of(cur), cy = y_of(cur);

        for (int k = 0; k < 8; k++) {
            int nx = cx + NEIGH[k].dx;
            int ny = cy + NEIGH[k].dy;

            if (!cell_free(nx, ny)) continue;      // за межами або в стіні

            // ── зріз кута: діагональ дозволена, лише якщо ОБИДВА
            //    ортогональні сусіди по дорозі вільні (див. пастку 2) ──
            if (NEIGH[k].dx != 0 && NEIGH[k].dy != 0) {
                if (!cell_free(cx + NEIGH[k].dx, cy) ||
                    !cell_free(cx, cy + NEIGH[k].dy))
                    continue;                       // кут стіни — не зрізаємо
            }

            int nidx = idx_of(nx, ny);
            if (closed_get(nidx)) continue;        // вже остаточно розкрито

            float new_g = g_cost[cur] + NEIGH[k].cost;
            if (new_g < g_cost[nidx]) {            // знайшли дешевший шлях
                g_cost[nidx]    = new_g;
                came_from[nidx] = cur;             // хлібна крихта
                float f = new_g + heuristic(nx, ny, gx, gy);
                heap_push(nidx, f);                // (можливий дублікат — не страшно)
            }
        }
    }
    return false;   // фронт вичерпано, цілі не досягли — шляху не існує
}
