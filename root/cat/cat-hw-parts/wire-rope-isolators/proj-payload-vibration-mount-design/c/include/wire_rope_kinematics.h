#ifndef WIRE_ROPE_KINEMATICS_H
#define WIRE_ROPE_KINEMATICS_H

#include <stdbool.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Статус безпеки динамічного ходу віброізолятора.
 */
typedef enum {
    MOUNT_STATUS_SAFE,          /**< Робочий хід у межах норми */
    MOUNT_STATUS_WARNING_STROKE,/**< Хід перевищує 80% допустимого запасу */
    MOUNT_STATUS_BOTTOMING_OUT  /**< Пробивання демпфера (жорсткий удар в упор) */
} mount_safety_status_t;

/**
 * @brief Параметри одиничного комбінованого ізолятора (трос + силікон).
 */
typedef struct {
    double k_compression_n_m;   /**< Жорсткість на стиск вздовж осі опори (Н/м) */
    double k_shear_n_m;         /**< Жорсткість на зсув перпендикулярно до осі (Н/м) */
    double max_stroke_mm;       /**< Гранично допустимий хід до жорсткого упору (мм) */
    double tilt_angle_deg;      /**< Кут просторового нахилу до горизонту (градуси) */
} isolator_spec_t;

/**
 * @brief Розрахункова модель просторової системи підвісу корисного навантаження.
 */
typedef struct {
    isolator_spec_t spec;       /**< Характеристики використовуваних демпферів */
    uint8_t isolator_count;     /**< Кількість ізоляторів (зазвичай 4 симетричні опори) */
    double payload_mass_kg;     /**< Маса підвішеного приладового блоку (кг) */
    double k_total_z_n_m;       /**< Сумарна еквівалентна вертикальна жорсткість (Н/м) */
    double k_total_xy_n_m;      /**< Сумарна горизонтальна жорсткість у площині (Н/м) */
    double f0_z_hz;             /**< Власна вертикальна резонансна частота (Гц) */
    double f0_xy_hz;            /**< Власна горизонтальна резонансна частота (Гц) */
} spatial_mount_t;

/**
 * @brief Ініціалізує параметри просторового підвісу та виконує розрахунок тривісної жорсткості.
 * @param mount Вказівник на структуру підвісу.
 * @param spec Характеристики ізоляторів.
 * @param isolator_count Кількість опор.
 * @param mass_kg Маса корисного навантаження.
 */
void spatial_mount_init(spatial_mount_t *mount, isolator_spec_t spec, uint8_t isolator_count, double mass_kg);

/**
 * @brief Розраховує динамічний хід ізоляторів під час ударного перевантаження.
 * @param mount Вказівник на підвіс.
 * @param accel_g Величина прискорення у одиницях G (1 G = 9.81 м/с²).
 * @param is_vertical Напрямок удару: true - вертикальний, false - бічний.
 * @return Розрахований динамічний хід демпфера вздовж осі навантаження (мм).
 */
double spatial_mount_calculate_dynamic_stroke(const spatial_mount_t *mount, double accel_g, bool is_vertical);

/**
 * @brief Оцінює небезпеку пробивання ізолятора (bottoming out) за поточним динамічним ходом.
 * @param mount Вказівник на підвіс.
 * @param stroke_mm Розрахований динамічний хід (мм).
 * @return Статус безпеки деформації демпфера.
 */
mount_safety_status_t spatial_mount_check_bottoming(const spatial_mount_t *mount, double stroke_mm);

/**
 * @brief Повертає текстовий опис статусу безпеки українською мовою.
 */
const char* spatial_mount_get_status_name(mount_safety_status_t status);

#ifdef __cplusplus
}
#endif

#endif /* WIRE_ROPE_KINEMATICS_H */
