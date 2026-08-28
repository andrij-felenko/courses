// Розкласти пораховані коефіцієнти в параметри автопілота.
static void accel_cal_to_params(const accel_cal_t *cal)
{
    param_set_float("INS_ACCOFFS_X", cal->offset.x);
    param_set_float("INS_ACCOFFS_Y", cal->offset.y);
    param_set_float("INS_ACCOFFS_Z", cal->offset.z);
    param_set_float("INS_ACCSCAL_X", cal->scale.x);
    param_set_float("INS_ACCSCAL_Y", cal->scale.y);
    param_set_float("INS_ACCSCAL_Z", cal->scale.z);
}

// А в робочому циклі кожен сирий вектор проганяється крізь ці числа:
static vec3_t accel_apply(vec3_t raw, const accel_cal_t *cal)
{
    return (vec3_t){
        (raw.x - cal->offset.x) * cal->scale.x,
        (raw.y - cal->offset.y) * cal->scale.y,
        (raw.z - cal->offset.z) * cal->scale.z,
    };
}
