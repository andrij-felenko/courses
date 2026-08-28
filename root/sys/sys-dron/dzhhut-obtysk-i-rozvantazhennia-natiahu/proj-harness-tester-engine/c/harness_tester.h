/**
 * @file harness_tester.h
 * @brief Драйвер та аналітичний рушій матричного тестування кабельних джгутів (C99).
 */

#ifndef HARNESS_TESTER_H
#define HARNESS_TESTER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

#define HARNESS_MAX_PINS 64U
#define HARNESS_MATRIX_WORDS ((HARNESS_MAX_PINS + 63U) / 64U)

/**
 * @brief Типи топологічних дефектів кабельного джгута.
 */
typedef enum {
    HARNESS_DEFECT_NONE = 0,
    HARNESS_DEFECT_OPEN_CIRCUIT,       /**< Обрив провідника */
    HARNESS_DEFECT_SHORT_CIRCUIT,      /**< Закорочення між незалежними лініями */
    HARNESS_DEFECT_MISWIRED_PIN,       /**< Переплутаний пін (крос-з'єднання) */
    HARNESS_DEFECT_INTERMITTENT_GLITCH /**< Плаваючий контакт під вібрацією */
} harness_defect_type_t;

/**
 * @brief Запис про одиничний виявлений дефект.
 */
typedef struct {
    harness_defect_type_t type;
    uint8_t pin_a;                     /**< Номер ведучого піна (0..N-1) */
    uint8_t pin_b;                     /**< Номер веденого піна (0..N-1) */
    uint32_t glitch_duration_us;       /**< Тривалість мікрообриву в мікросекундах */
} harness_defect_entry_t;

/**
 * @brief Матриця провідності джгута (бітове представлення N x N).
 */
typedef struct {
    uint8_t pin_count;
    uint64_t rows[HARNESS_MAX_PINS];   /**< Бітова маска: біт j у rows[i] = 1, якщо i з'єднано з j */
} harness_matrix_t;

/**
 * @brief Апаратний інтерфейс низькорівневого доступу до пінів тестера.
 */
typedef struct {
    void (*set_pin_mode_drive)(uint8_t pin, bool level_high);
    void (*set_pin_mode_sense)(uint8_t pin);
    bool (*read_pin_level)(uint8_t pin);
    void (*delay_us)(uint32_t us);
    uint32_t (*get_time_us)(void);
} harness_hw_interface_t;

/**
 * @brief Результати повного тестування джгута.
 */
typedef struct {
    bool is_passed;
    uint32_t total_errors;
    uint32_t open_circuits;
    uint32_t short_circuits;
    uint32_t miswires;
    uint32_t intermittent_glitches;
    uint32_t test_duration_us;
} harness_test_summary_t;

/**
 * @brief Дескриптор стану сесії тестування джгута.
 */
typedef struct {
    uint8_t pin_count;
    harness_matrix_t ref_matrix;       /**< Еталонна матриця з'єднань */
    harness_matrix_t measured_matrix;  /**< Фактично виміряна матриця */
    harness_hw_interface_t hw;
    harness_defect_entry_t defect_log[128];
    uint32_t defect_count;
    uint32_t max_defects;
} harness_session_t;

/**
 * @brief Ініціалізація сесії тестування.
 */
void harness_session_init(harness_session_t *session, uint8_t pin_count, const harness_hw_interface_t *hw);

/**
 * @brief Очищення матриці з'єднань.
 */
void harness_matrix_clear(harness_matrix_t *mat, uint8_t pin_count);

/**
 * @brief Додавання зв'язку в матрицю (двосторонній симетричний зв'язок).
 */
bool harness_matrix_add_wire(harness_matrix_t *mat, uint8_t pin_a, uint8_t pin_b);

/**
 * @brief Режим навчання: зняття еталонної матриці з перевіреного зразка джгута.
 */
bool harness_learn_golden_sample(harness_session_t *session);

/**
 * @brief Виконання повного статичного сканування топології джгута.
 */
bool harness_scan_network(harness_session_t *session);

/**
 * @brief Порівняння виміряної матриці з еталонною та формування діагностичного звіту.
 */
void harness_analyze_defects(harness_session_t *session, harness_test_summary_t *summary);

/**
 * @brief Режим вібраційного моніторингу: швидкісне детектування мікрообривів.
 */
uint32_t harness_monitor_vibration_glitches(harness_session_t *session, uint32_t duration_ms);

#ifdef __cplusplus
}
#endif

#endif /* HARNESS_TESTER_H */
