void refine_subpixel_peak(double r_c, double r_left, double r_right,
                          double r_top, double r_bottom,
                          float *delta_x, float *delta_y) {
    const double denom_x = 2.0 * (2.0 * r_c - r_left - r_right);
    if (fabs(denom_x) > 1e-7) {
        *delta_x = (float)((r_right - r_left) / denom_x);
        if (*delta_x > 1.0f) *delta_x = 1.0f;
        if (*delta_x < -1.0f) *delta_x = -1.0f;
    } else {
        *delta_x = 0.0f;
    }

    const double denom_y = 2.0 * (2.0 * r_c - r_top - r_bottom);
    if (fabs(denom_y) > 1e-7) {
        *delta_y = (float)((r_bottom - r_top) / denom_y);
        if (*delta_y > 1.0f) *delta_y = 1.0f;
        if (*delta_y < -1.0f) *delta_y = -1.0f;
    } else {
        *delta_y = 0.0f;
    }
}
