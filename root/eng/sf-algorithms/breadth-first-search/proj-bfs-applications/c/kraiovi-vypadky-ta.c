#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

typedef struct { int r, c; } PointC;

int bfs_grid_c(const char* const* grid, int rows, int cols, PointC start, PointC target) {
    if (grid[start.r][start.c] == '#' || grid[target.r][target.c] == '#') return -1;

    bool** visited = (bool**)malloc(sizeof(bool*) * rows);
    int** dist = (int**)malloc(sizeof(int*) * rows);
    for (int i = 0; i < rows; ++i) {
        visited[i] = (bool*)calloc(cols, sizeof(bool));
        dist[i] = (int*)malloc(sizeof(int) * cols);
        for (int j = 0; j < cols; ++j) dist[i][j] = -1;
    }

    PointC* queue = (PointC*)malloc(sizeof(PointC) * rows * cols);
    int head = 0, tail = 0;

    visited[start.r][start.c] = true;
    dist[start.r][start.c] = 0;
    queue[tail++] = start;

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};
    int result = -1;

    while (head < tail) {
        PointC curr = queue[head++];
        if (curr.r == target.r && curr.c == target.c) {
            result = dist[curr.r][curr.c];
            break;
        }

        for (int i = 0; i < 4; ++i) {
            int nr = curr.r + dr[i];
            int nc = curr.c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols &&
                grid[nr][nc] != '#' && !visited[nr][nc]) {
                visited[nr][nc] = true;
                dist[nr][nc] = dist[curr.r][curr.c] + 1;
                queue[tail++] = (PointC){nr, nc};
            }
        }
    }

    for (int i = 0; i < rows; ++i) {
        free(visited[i]);
        free(dist[i]);
    }
    free(visited); free(dist); free(queue);
    return result;
}
