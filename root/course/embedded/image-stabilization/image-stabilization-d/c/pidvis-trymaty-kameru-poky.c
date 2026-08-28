const float KP_ROLL   = 6.0f;     /* підсилення: одиниць виходу на градус похибки */
const float OUT_LIMIT = 100.0f;   /* межа керування мотором (±) */

/* roll_now — оцінка кута камери з її IMU (градуси), roll_set — бажаний кут */
float gimbal_roll_step(float roll_now, float roll_set)
{
    float error  = roll_set - roll_now;       /* куди й наскільки камера збилася */
    float output = KP_ROLL * error;           /* тягнемо мотор назад, до цілі */

    if (output >  OUT_LIMIT) output =  OUT_LIMIT;   /* не виходимо за межу */
    if (output < -OUT_LIMIT) output = -OUT_LIMIT;
    return output;                            /* далі йде на драйвер мотора крену */
}
