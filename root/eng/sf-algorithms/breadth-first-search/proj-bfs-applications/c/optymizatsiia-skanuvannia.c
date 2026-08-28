#include <stdbool.h>
#include <stdlib.h>

typedef struct { int r, c; } PixelC;

void flood_fill_c(int** image, int rows, int cols, int start_r, int start_c, int new_color) {
    int target_color = image[start_r][start_c];
    if (target_color == new_color) return;

    PixelC* queue = (PixelC*)malloc(sizeof(PixelC) * rows * cols);
    int head = 0, tail = 0;

    image[start_r][start_c] = new_color;
    queue[tail++] = (PixelC){start_r, start_c};

    int dr[] = {-1, 1, 0, 0};
    int dc[] = {0, 0, -1, 1};

    while (head < tail) {
        PixelC curr = queue[head++];
        for (int i = 0; i < 4; ++i) {
            int nr = curr.r + dr[i];
            int nc = curr.c + dc[i];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && image[nr][nc] == target_color) {
                image[nr][nc] = new_color;
                queue[tail++] = (PixelC){nr, nc};
            }
        }
    }
    free(queue);
}
