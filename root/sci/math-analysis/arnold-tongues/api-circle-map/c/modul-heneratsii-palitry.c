typedef struct {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} circle_map_color_rgb_t;

/**
 * @brief Перетворює число обертання W у RGB колір за вибраною палітрою.
 */
circle_map_color_rgb_t circle_map_rotation_to_rgb(double w, bool is_locked);
