/* Формати двійкової серіалізації точок */
typedef enum {
    MSM_FORMAT_UNCOMPRESSED = 0,  /* Повний двійковий формат (x || y) */
    MSM_FORMAT_COMPRESSED   = 1   /* Стиснений формат (x + bit flags) */
} msm_serialization_format_t;

/**
 * Серіалізація точки еліптичної кривої у двійковий буфер.
 * @param out_bytes Буфер вихідних байтів (мінімум 64 або 32 байти для BN254).
 * @param point     Вхідна афінна точка.
 * @param format    Обраний формат серіалізації.
 * @param curve     Ідентифікатор кривої.
 */
msm_status_t msm_point_serialize(
    uint8_t *out_bytes,
    const msm_point_affine_t *point,
    msm_serialization_format_t format,
    msm_curve_id_t curve
);

/**
 * Десеріалізація та валідація точки з перевіркою належності підгрупі.
 */
msm_status_t msm_point_deserialize(
    msm_point_affine_t *point,
    const uint8_t *in_bytes,
    msm_serialization_format_t format,
    msm_curve_id_t curve
);
