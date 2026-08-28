#include <vector>
#include <queue>
#include <string>

struct Point { int r, c; };

int bfs_grid_cpp(const std::vector<std::string>& grid, Point start, Point target) {
    int rows = grid.size();
    int cols = grid[0].size();
    if (grid[start.r][start.c] == '#' || grid[target.r][target.c] == '#') return -1;

    std::vector<std::vector<int>> dist(rows, std::vector<int>(cols, -1));
    std::queue<Point> q;

    dist[start.r][start.c] = 0;
    q.push(start);

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    while (!q.empty()) {
        Point curr = q.front();
        q.pop();

        if (curr.r == target.r && curr.c == target.c) {
            return dist[curr.r][curr.c];
        }

        for (int i = 0; i < 4; ++i) {
            int nr = curr.r + dr[i];
            int nc = curr.c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                grid[nr][nc] != '#' && dist[nr][nc] == -1) {
                dist[nr][nc] = dist[curr.r][curr.c] + 1;
                q.push({nr, nc});
            }
        }
    }
    return -1;
}
