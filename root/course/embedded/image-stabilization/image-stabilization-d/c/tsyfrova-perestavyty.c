const float FOV_DEG   = 90.0f;
const int   FRAME_W   = 1920;
const float PX_PER_DEG = FRAME_W / FOV_DEG;   /* ≈ 21.3 пікселя на градус */

/* gyro_yaw — кутова швидкість рискання (°/с), dt — тривалість кадру (с) */
int eis_shift_px(float gyro_yaw, float dt)
{
    float angle_deg = gyro_yaw * dt;          /* поворот за цей кадр (градуси) */
    float shift     = angle_deg * PX_PER_DEG; /* у пікселях */
    return (int)(-shift);                     /* зсуваємо кадр ПРОТИ повороту */
}
