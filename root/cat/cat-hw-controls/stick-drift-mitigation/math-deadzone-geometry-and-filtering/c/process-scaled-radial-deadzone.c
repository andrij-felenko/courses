#include <math.h>

typedef struct {
    float x;
    float y;
} vector2d_t;

vector2d_t process_scaled_radial_deadzone(float x_in, float y_in, float d_min, float d_max, float gamma) {
    vector2d_t out = {0.0f, 0.0f};
    float r = sqrtf(x_in * x_in + y_in * y_in);
    
    if (r <= d_min || r < 1e-6f) {
        return out;
    }
    
    float r_norm = (r - d_min) / (d_max - d_min);
    if (r_norm > 1.0f) {
        r_norm = 1.0f;
    }
    
    float r_scaled = powf(r_norm, gamma);
    out.x = (x_in / r) * r_scaled;
    out.y = (y_in / r) * r_scaled;
    return out;
}
