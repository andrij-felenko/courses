/* Стан фільтра — кут живе між викликами */
static float pitch = 0.0f;            /* поточна оцінка тангажа, градуси */
const  float ALPHA = 0.98f;           /* довіра гіроскопу (близько до 1) */

/* Один такт. gyro_y — кутова швидкість по осі тангажа (°/с);
   ax, az — осі акселерометра; dt — крок такту (с). */
float complementary_step(float gyro_y, float ax, float az, float dt)
{
    /* ПЕРЕДБАЧ: прокрутити кут уперед гіроскопом */
    float predicted = pitch + gyro_y * dt;

    /* ВИПРАВ: абсолютний тангаж із напрямку «низу» (вектор g) */
    float acc_pitch = atan2f(-ax, az) * 57.2958f;   /* рад → градуси */

    /* зважена суміш: майже все — передбачення, дрібка — корекція */
    pitch = ALPHA * predicted + (1.0f - ALPHA) * acc_pitch;
    return pitch;
}
