#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>

typedef struct {
    int32_t x;
    int32_t y;
} Point2D;

typedef void (*PixelCallbackC)(int32_t x, int32_t y, void* user_data);

void bresenham_draw_line_c(int32_t x1, int32_t y1, int32_t x2, int32_t y2, PixelCallbackC plot, void* user_data) {
    int32_t dx = abs(x2 - x1);
    int32_t dy = abs(y2 - y1);
    int32_t sx = (x1 < x2) ? 1 : -1;
    int32_t sy = (y1 < y2) ? 1 : -1;
    
    bool is_steep = dy > dx;
    if (is_steep) {
        int32_t tmp = dx;
        dx = dy;
        dy = tmp;
    }
    
    int32_t err = 2 * dy - dx;
    int32_t x = x1;
    int32_t y = y1;
    
    for (int32_t i = 0; i <= dx; i++) {
        plot(x, y, user_data);
        
        while (err >= 0) {
            if (is_steep) {
                x += sx;
            } else {
                y += sy;
            }
            err -= 2 * dx;
        }
        
        if (is_steep) {
            y += sy;
        } else {
            x += sx;
        }
        err += 2 * dy;
    }
}
