static void print_pixel_c(int32_t x, int32_t y, void* user_data) {
    (void)user_data;
    printf("(%d, %d) ", x, y);
}

int main(void) {
    printf("Line (0,0) -> (7,3):\n");
    bresenham_draw_line_c(0, 0, 7, 3, print_pixel_c, NULL);
    printf("\n\nCircle R=6 at (0,0):\n");
    bresenham_draw_circle_c(0, 0, 6, print_pixel_c, NULL);
    printf("\n");
    return 0;
}
