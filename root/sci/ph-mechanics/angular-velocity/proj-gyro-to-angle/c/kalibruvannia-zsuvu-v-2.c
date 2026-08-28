typedef struct {
    float theta;   /* поточний кут, рад (стан, живе між тактами) */
    float bias;    /* оцінений зсув, рад/с                       */
} GyroAngle;

static void gyro_angle_init(GyroAngle *g, float bias)
{
    g->theta = 0.0f;
    g->bias  = bias;
}

/* Один такт: сира швидкість осі та реальний крок часу. */
static void gyro_angle_step(GyroAngle *g, int16_t raw, float dt)
{
    float w = gyro_rate_rad(raw) - g->bias;   /* прибрати зсув */
    g->theta += w * dt;                        /* проінтегрувати */
}
