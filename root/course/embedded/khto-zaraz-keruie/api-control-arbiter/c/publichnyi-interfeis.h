#ifndef CONTROL_ARBITER_H
#define CONTROL_ARBITER_H

#include "control_arbiter_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    control_setpoint_t raw_setpoint;
    uint64_t last_heartbeat_us;
    uint64_t last_packet_us;
    source_config_t config;
    uint8_t state_flags;
    bool registered;
} source_slot_t;

typedef struct {
    source_slot_t sources[SOURCE_COUNT];
    control_source_id_t active_source;
    control_source_id_t previous_source;
    control_setpoint_t smoothed_output;
    uint64_t last_eval_time_us;
    uint32_t transition_counter;
} arbiter_instance_t;

/**
 * @brief Ініціалізація структури арбітра значеннями за замовчуванням.
 * @param arb Вказівник на структуру екземпляра арбітра.
 */
void arbiter_init(arbiter_instance_t *arb);

/**
 * @brief Конфігурація порогів таймауту та лімітів наростання для слота.
 * @param arb Вказівник на екземпляр арбітра.
 * @param id Ідентифікатор джерела (0..SOURCE_COUNT-1).
 * @param cfg Вказівник на структуру конфігурації.
 * @return true, якщо слот успішно сконфігуровано.
 */
bool arbiter_configure_source(arbiter_instance_t *arb, 
                              control_source_id_t id, 
                              const source_config_t *cfg);

/**
 * @brief Оновлення мітки сторожового таймера (heartbeat feed).
 * @param arb Вказівник на екземпляр арбітра.
 * @param id Ідентифікатор джерела.
 * @param now_us Поточний монотонний системний час у мікросекундах.
 */
void arbiter_feed_heartbeat(arbiter_instance_t *arb, 
                            control_source_id_t id, 
                            uint64_t now_us);

/**
 * @brief Подання нового кадру уставки від комунікаційного драйвера.
 * @param arb Вказівник на екземпляр арбітра.
 * @param id Ідентифікатор джерела.
 * @param sp Вказівник на нову уставку.
 * @param now_us Поточний монотонний системний час у мікросекундах.
 */
void arbiter_submit_setpoint(arbiter_instance_t *arb, 
                             control_source_id_t id, 
                             const control_setpoint_t *sp, 
                             uint64_t now_us);

/**
 * @brief Основний крок оцінки пріоритетів та безударної фільтрації.
 * @param arb Вказівник на екземпляр арбітра.
 * @param now_us Поточний монотонний час системи у мікросекундах.
 * @param out_setpoint Буфер для запису згладженої уставки для регулятора.
 * @return Ідентифікатор джерела, яке зараз володіє авторитетом керування.
 */
control_source_id_t arbiter_evaluate(arbiter_instance_t *arb, 
                                     uint64_t now_us, 
                                     control_setpoint_t *out_setpoint);

/**
 * @brief Отримання поточного активного джерела авторитету.
 */
control_source_id_t arbiter_get_active_source(const arbiter_instance_t *arb);

/**
 * @brief Примусове захоплення виміряного стану апарата для безперервного рестарту.
 * @param arb Вказівник на екземпляр арбітра.
 * @param current_state Масив [Roll, Pitch, Yaw, Thrust] поточного стану EKF.
 * @param now_us Поточний час у мікросекундах.
 */
void arbiter_reset_state(arbiter_instance_t *arb, 
                         const float current_state[4], 
                         uint64_t now_us);

#ifdef __cplusplus
}
#endif

#endif /* CONTROL_ARBITER_H */
