#ifndef T8_MAINTENANCE_H
#define T8_MAINTENANCE_H

#include <stdbool.h>
#include <stdint.h>

/**
 * @brief Матеріал гайки ходового гвинта T8.
 */
typedef enum {
    NUT_MATERIAL_POM,   ///< Поліацеталь (POM / Delrin) - низький коефіцієнт тертя
    NUT_MATERIAL_BRASS  ///< Латунь (CW614N) - висока несуча здатність
} nut_material_t;

/**
 * @brief Поточний стан мастильної плівки силіконової змазки SI-180.
 */
typedef struct {
    double film_thickness_um;       ///< Поточна товщина трибологічної плівки (мкм)
    double initial_film_thickness;  ///< Початкова товщина після нанесення (номінал 10.0 мкм)
    double contamination_index;     ///< Індекс забруднення пилом (0.0 - чисте мастило, 1.0 - абразивна паста)
    double dynamic_viscosity_cst;   ///< Ефективна кінематична в'язкість (номінал 1000 cSt)
} grease_state_t;

/**
 * @brief Контекст обліку напрацювання кінематичної пари осі Z.
 */
typedef struct {
    nut_material_t nut_material;    ///< Матеріал використовуваної гайки
    grease_state_t grease;          ///< Стан силіконового змащення
    double total_distance_m;        ///< Сумарний пробіг каретки вздовж осі Z (метри)
    double print_hours;             ///< Загальний час друку (години)
    uint32_t z_hop_count;           ///< Кількість коротких реверсивних переміщень (Z-hop)
    double accumulated_wear_um;     ///< Розрахунковий знос профілю нарізі гайки (мкм)
    double service_limit_distance_m;///< Рекомендований граничний пробіг до регламентного ТО (метри)
} t8_tracker_t;

/**
 * @brief Ініціалізує модуль обліку напрацювання ходового гвинта T8.
 * @param tracker Вказівник на екземпляр трекера.
 * @param nut_material Матеріал гайки (POM або латунь).
 * @param initial_film_um Початкова товщина мастильної плівки SI-180 (мкм).
 */
void t8_tracker_init(t8_tracker_t *tracker, nut_material_t nut_material, double initial_film_um);

/**
 * @brief Реєструє переміщення каретки за віссю Z під час друку шару або Z-hop.
 * @param tracker Вказівник на трекер.
 * @param distance_mm Довжина переміщення у міліметрах.
 * @param speed_mm_s Швидкість переміщення (мм/с).
 * @param is_z_hop Ознака швидкого відскоку сопла.
 * @param dust_exposure_factor Коефіцієнт пилового навантаження середовища (1.0 - чиста кімната, 2.5 - відкритий цех).
 */
void t8_tracker_log_movement(t8_tracker_t *tracker, double distance_mm, double speed_mm_s, bool is_z_hop, double dust_exposure_factor);

/**
 * @brief Оцінює поточний залишковий ресурс мастила у відсотках.
 * @param tracker Вказівник на трекер.
 * @return Відсоток ресурсу мастильної плівки (від 100.0% до 0.0%).
 */
double t8_tracker_get_grease_health(const t8_tracker_t *tracker);

/**
 * @brief Перевіряє, чи вичерпано ресурс мастила та чи потрібне планове сервісне ТО.
 * @param tracker Вказівник на трекер.
 * @return true, якщо товщина плівки менша 3 мкм або забруднення перевищує 80%.
 */
bool t8_tracker_needs_maintenance(const t8_tracker_t *tracker);

/**
 * @brief Скидає лічильники після проведення очищення спиртом IPA та нанесення нової порції SI-180.
 * @param tracker Вказівник на трекер.
 * @param new_film_um Товщина нанесеної нової плівки (мкм).
 */
void t8_tracker_perform_service(t8_tracker_t *tracker, double new_film_um);

/**
 * @brief Виводить у термінал діагностичний звіт кінематичного стану вузла T8.
 * @param tracker Вказівник на трекер.
 */
void t8_tracker_print_report(const t8_tracker_t *tracker);

#endif /* T8_MAINTENANCE_H */
