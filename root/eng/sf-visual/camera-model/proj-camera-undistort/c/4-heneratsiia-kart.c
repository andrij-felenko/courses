// Таблиця попередньо обчислених координат
typedef struct {
    int width;
    int height;
    float *map_x; // розмір width * height
    float *map_y; // розмір width * height
} UndistortMap;

UndistortMap* create_undistort_map(int width, int height,
                                   const CameraIntrinsics *K_src,
                                   const DistortionCoeffs *D,
                                   const CameraIntrinsics *K_dst) {
    UndistortMap *map = (UndistortMap*)malloc(sizeof(UndistortMap));
    if (!map) return NULL;

    map->width = width;
    map->height = height;
    map->map_x = (float*)malloc(sizeof(float) * width * height);
    map->map_y = (float*)malloc(sizeof(float) * width * height);

    if (!map->map_x || !map->map_y) {
        free(map->map_x);
        free(map->map_y);
        free(map);
        return NULL;
    }

    // Для кожного вихідного пікселя (u_dst, v_dst) рахуємо, де він лежить у сирому кадрі
    for (int v_dst = 0; v_dst < height; ++v_dst) {
        for (int u_dst = 0; u_dst < width; ++u_dst) {
            // 1. Нормовані координати в новому зображенні
            double x = (u_dst - K_dst->cx) / K_dst->fx;
            double y = (v_dst - K_dst->cy) / K_dst->fy;

            // 2. Пряме застосування моделі дисторсії Брауна
            double r2 = x * x + y * y;
            double r4 = r2 * r2;
            double r6 = r4 * r2;

            double radial = 1.0 + D->k1 * r2 + D->k2 * r4 + D->k3 * r6;
            double dx_tan = 2.0 * D->p1 * x * y + D->p2 * (r2 + 2.0 * x * x);
            double dy_tan = D->p1 * (r2 + 2.0 * y * y) + 2.0 * D->p2 * x * y;

            double x_d = x * radial + dx_tan;
            double y_d = y * radial + dy_tan;

            // 3. Переведення у пікселі вихідного сирого кадру
            float u_src = (float)(K_src->fx * x_d + K_src->cx);
            float v_src = (float)(K_src->fy * y_d + K_src->cy);

            int idx = v_dst * width + u_dst;
            map->map_x[idx] = u_src;
            map->map_y[idx] = v_src;
        }
    }
    return map;
}

void free_undistort_map(UndistortMap *map) {
    if (map) {
        free(map->map_x);
        free(map->map_y);
        free(map);
    }
}
