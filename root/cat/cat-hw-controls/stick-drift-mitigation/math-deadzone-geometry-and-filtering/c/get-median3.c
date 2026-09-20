#include <math.h>

typedef struct {
    float x;
    float y;
} vector2d_t;

typedef struct {
    float x_buf[3];
    float y_buf[3];
    float x_ema;
    float y_ema;
    float alpha;
    float d_min;
    float d_max;
    float gamma;
} stick_pipeline_t;

static float get_median3(float a, float b, float c) {
    if ((a <= b && b <= c) || (c <= b && b <= a)) return b;
    if ((b <= a && a <= c) || (c <= a && a <= b)) return a;
    return c;
}

vector2d_t process_stick_pipeline(stick_pipeline_t *pipe, float raw_x, float raw_y) {
    pipe->x_buf[0] = pipe->x_buf[1]; pipe->x_buf[1] = pipe->x_buf[2]; pipe->x_buf[2] = raw_x;
    pipe->y_buf[0] = pipe->y_buf[1]; pipe->y_buf[1] = pipe->y_buf[2]; pipe->y_buf[2] = raw_y;
    
    float med_x = get_median3(pipe->x_buf[0], pipe->x_buf[1], pipe->x_buf[2]);
    float med_y = get_median3(pipe->y_buf[0], pipe->y_buf[1], pipe->y_buf[2]);
    
    float r = sqrtf(med_x * med_x + med_y * med_y);
    vector2d_t scaled = {0.0f, 0.0f};
    
    if (r > pipe->d_min && r > 1e-6f) {
        float r_norm = (r - pipe->d_min) / (pipe->d_max - pipe->d_min);
        if (r_norm > 1.0f) r_norm = 1.0f;
        float r_scaled = powf(r_norm, pipe->gamma);
        scaled.x = (med_x / r) * r_scaled;
        scaled.y = (med_y / r) * r_scaled;
    }
    
    pipe->x_ema = pipe->x_ema + pipe->alpha * (scaled.x - pipe->x_ema);
    pipe->y_ema = pipe->y_ema + pipe->alpha * (scaled.y - pipe->y_ema);
    
    vector2d_t result = {pipe->x_ema, pipe->y_ema};
    return result;
}
