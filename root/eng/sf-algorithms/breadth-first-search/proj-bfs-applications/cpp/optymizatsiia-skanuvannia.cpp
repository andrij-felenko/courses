#include <vector>
#include <queue>

void flood_fill_cpp(std::vector<std::vector<int>>& image, int start_r, int start_c, int new_color) {
    int rows = image.size();
    int cols = image[0].size();
    int target_color = image[start_r][start_c];
    if (target_color == new_color) return;

    std::queue<std::pair<int, int>> q;
    image[start_r][start_c] = new_color;
    q.push({start_r, start_c});

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    while (!q.empty()) {
        auto [r, c] = q.front();
        q.pop();

        for (int i = 0; i < 4; ++i) {
            int nr = r + dr[i];
            int nc = c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && image[nr][nc] == target_color) {
                image[nr][nc] = new_color;
                q.push({nr, nc});
            }
        }
    }
}
