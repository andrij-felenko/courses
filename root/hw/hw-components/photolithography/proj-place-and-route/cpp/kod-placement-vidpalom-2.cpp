#include <vector>
#include <queue>
#include <cstdint>

struct Point { int r, c; };

// Хвильовий пошук Лі: BFS від джерела сіткою, доки хвиля не дійде
// до цілі, оминаючи зайняті клітини (grid: 0 — вільно, 1 — зайнято).
// Повертає доріжку або порожньо, якщо дороги не лишилося.
std::vector<Point> mazeRoute(std::vector<std::vector<uint8_t>>& grid,
                             Point src, Point dst) {
    int H = grid.size(), W = grid[0].size();
    std::vector<std::vector<int>> dist(H, std::vector<int>(W, -1));
    const int dr[] = {-1, 1, 0, 0}, dc[] = {0, 0, -1, 1};

    std::queue<Point> wave;
    wave.push(src);  dist[src.r][src.c] = 0;
    while (!wave.empty()) {
        Point p = wave.front();  wave.pop();
        if (p.r == dst.r && p.c == dst.c) break;       // хвиля дійшла до цілі
        for (int k = 0; k < 4; ++k) {
            int nr = p.r + dr[k], nc = p.c + dc[k];
            if (nr < 0 || nr >= H || nc < 0 || nc >= W) continue;
            if (grid[nr][nc] || dist[nr][nc] != -1) continue;   // зайнято / вже пройдено
            dist[nr][nc] = dist[p.r][p.c] + 1;
            wave.push({nr, nc});
        }
    }
    if (dist[dst.r][dst.c] < 0) return {};             // дороги немає → rip-up & reroute

    std::vector<Point> path;                           // зворотний хід по спадній відстані
    for (Point p = dst; ; ) {
        path.push_back(p);
        grid[p.r][p.c] = 1;                            // клітину доріжки робимо зайнятою
        if (p.r == src.r && p.c == src.c) break;
        for (int k = 0; k < 4; ++k) {
            int nr = p.r + dr[k], nc = p.c + dc[k];
            if (nr >= 0 && nr < H && nc >= 0 && nc < W &&
                dist[nr][nc] == dist[p.r][p.c] - 1) { p = {nr, nc}; break; }
        }
    }
    return path;
}
