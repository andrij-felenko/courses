// Сусіди у 8-зв'язності: 4 ортогональні + 4 діагональні.
struct Step { int dx, dy; float cost; };
static const Step NEIGH[8] = {
    {+1, 0, 1.0f}, {-1, 0, 1.0f}, {0, +1, 1.0f}, {0, -1, 1.0f},   // прямі: ціна 1
    {+1, +1, 1.41421f}, {+1, -1, 1.41421f},                         // діагоналі: √2
    {-1, +1, 1.41421f}, {-1, -1, 1.41421f},
};

// Чебишева евристика для 8-зв'язності: min(|dx|,|dy|) діагоналей + решта прямо.
// (діагональ коштує √2, тож рахуємо чесно, а не просто max)
float heuristic(int cx, int cy, int gx, int gy) {
    int dx = abs(gx - cx), dy = abs(gy - cy);
    int diag = dx < dy ? dx : dy;          // скільки ходів можна зробити навскіс
    int straight = abs(dx - dy);           // решта — прямими кроками
    return diag * 1.41421f + straight * 1.0f;
}

// Розкриття поточної клітини (cur) у головному циклі A*:
for (const Step& s : NEIGH) {
    int nx = cur.x + s.dx, ny = cur.y + s.dy;

    if (!in_bounds(nx, ny) || grid[ny][nx] == OCCUPIED)
        continue;                          // за межами або в стіні — пропускаємо

    float new_g = g[cur.y][cur.x] + s.cost;
    if (new_g < g[ny][nx]) {               // знайшли дешевший шлях до сусіда
        g[ny][nx]        = new_g;
        float f          = new_g + heuristic(nx, ny, goal_x, goal_y);
        came_from[ny][nx] = cur;           // хлібна крихта: звідки прийшли
        open.push({f, nx, ny});            // у чергу з пріоритетом за f
    }
}
