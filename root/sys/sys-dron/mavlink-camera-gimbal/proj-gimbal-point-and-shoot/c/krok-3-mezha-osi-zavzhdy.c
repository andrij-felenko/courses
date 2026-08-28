static float wrap_pi(float x)
{
    while (x >  (float)M_PI) x -= 2.0f * (float)M_PI;
    while (x < -(float)M_PI) x += 2.0f * (float)M_PI;
    return x;
}

/* Порівнюємо ЗАВЖДИ кут у рамці корпусу. NaN у межі означає «невідомо». */
static bool within_limits(const mavlink_gimbal_device_information_t *i,
                          float pitch, float yaw_body)
{
    if (isfinite(i->pitch_min) && pitch    < i->pitch_min) return false;
    if (isfinite(i->pitch_max) && pitch    > i->pitch_max) return false;
    if (isfinite(i->yaw_min)   && yaw_body < i->yaw_min)   return false;
    if (isfinite(i->yaw_max)   && yaw_body > i->yaw_max)   return false;
    return true;
}
