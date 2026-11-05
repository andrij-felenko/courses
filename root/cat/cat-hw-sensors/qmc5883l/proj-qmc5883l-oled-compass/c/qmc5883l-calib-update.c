void qmc5883l_calib_update(qmc5883l_calib_t *calib, const qmc5883l_raw_t *raw) {
    if (raw->x == 0 && raw->y == 0 && raw->z == 0) return;

    if (raw->x < calib->x_min) calib->x_min = raw->x;
    if (raw->x > calib->x_max) calib->x_max = raw->x;
    if (raw->y < calib->y_min) calib->y_min = raw->y;
    if (raw->y > calib->y_max) calib->y_max = raw->y;

    calib->x_offset = (float)(calib->x_min + calib->x_max) / 2.0f;
    calib->y_offset = (float)(calib->y_min + calib->y_max) / 2.0f;

    float x_delta = (float)(calib->x_max - calib->x_min) / 2.0f;
    float y_delta = (float)(calib->y_max - calib->y_min) / 2.0f;
    float avg_delta = (x_delta + y_delta) / 2.0f;

    if (x_delta > 0.0f) calib->x_scale = avg_delta / x_delta;
    if (y_delta > 0.0f) calib->y_scale = avg_delta / y_delta;

    calib->is_calibrated = true;
}
