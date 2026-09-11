/**
 * @file gauge_renderer.h
 * @brief Архітектура попіксельного сканлайн-рендерингу кругової шкали з подвійною рядковою буферизацією.
 *
 * Модуль реалізує генерацію рядків графічного інтерфейсу на льоту (без важкого фреймбуфера),
 * цілочисельний розрахунок геометрії стрілки й поділок, а також експоненційне демпфування коливань.
 */

#ifndef GAUGE_RENDERER_H
#define GAUGE_RENDERER_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/* --- Розміри екрана та геометричні параметри приладу --- */
#define GAUGE_DISPLAY_WIDTH        240U
#define GAUGE_DISPLAY_HEIGHT       240U

#define GAUGE_CENTER_X             120
#define GAUGE_CENTER_Y             120

/* Радіуси кругових елементів циферблата (у пікселях) */
#define GAUGE_RADIUS_BEZEL_OUT     119
#define GAUGE_RADIUS_BEZEL_IN      113
#define GAUGE_RADIUS_DIAL          112
#define GAUGE_RADIUS_ARC_OUT        98
#define GAUGE_RADIUS_ARC_IN         88
#define GAUGE_RADIUS_HUB            10
#define GAUGE_RADIUS_HUB_CORE        3

/* Довжина стрілки та її противаги */
#define GAUGE_NEEDLE_LENGTH         84
#define GAUGE_NEEDLE_TAIL_LENGTH    16

/* Діапазон кутів переміщення стрілки (градуси відносно вертикалі) */
#define GAUGE_MIN_ANGLE_DEG       -135
#define GAUGE_MAX_ANGLE_DEG       +135
#define GAUGE_TOTAL_SWEEP_DEG      270

/* Зсув для формату з фіксованою комою Q8 (1 градус = 256 квантів) */
#define GAUGE_FP_SHIFT             8U

/**
 * @brief Структура подвійного рядкового буфера ping-pong.
 * Дозволяє процесору малювати наступний рядок у буфер B,
 * поки контролер DMA транслює буфер A на дисплей.
 * Загальний обсяг пам'яті: 2 * 240 * 2 = 960 байтів RAM.
 */
typedef struct {
    uint16_t buffer[2][GAUGE_DISPLAY_WIDTH]; /**< Два чергові рядкові буфери RGB565 */
    uint8_t write_index;                     /**< Індекс буфера, в який зараз рендерить CPU (0 або 1) */
} ping_pong_buffer_t;

/**
 * @brief Стан приладу та параметри демпфування стрілки.
 */
typedef struct {
    int16_t target_value;       /**< Цільове вимірюване значення (наприклад, 0..1000) */
    int16_t min_value;          /**< Нижня межа шкали */
    int16_t max_value;          /**< Верхня межа шкали */
    int32_t current_angle_fp;   /**< Поточний згладжений кут у форматі Q8 (кути з високою роздільністю) */
    int16_t current_angle_deg;  /**< Поточний кут у цілих градусах для тригонометрії */
    uint8_t damping_shift;      /**< Коефіцієнт згладжування фільтра (ділення зсувом вправо) */
} gauge_state_t;

/**
 * @brief Ініціалізація математичної моделі шкали та початкового стану стрілки.
 * @param gauge Вказівник на структуру стану приладу.
 * @param min_val Мінімальне значення вимірюваної величини.
 * @param max_val Максимальне значення вимірюваної величини.
 * @param damping_shift Коефіцієнт експоненційного демпфування (типово 3 або 4).
 */
void gauge_renderer_init(gauge_state_t *gauge, int16_t min_val, int16_t max_val, uint8_t damping_shift);

/**
 * @brief Оновлення цільового значення та один крок експоненційного згладжування положення стрілки.
 * @param gauge Вказівник на структуру стану приладу.
 * @param target_value Нове значення вимірюваної величини.
 */
void gauge_update_needle(gauge_state_t *gauge, int16_t target_value);

/**
 * @brief Генерація одного сканлайну графіки безпосередньо у наданий рядковий буфер.
 * Алгоритм розраховує перетин рядка Y з безелем, фоном циферблата, кольоровою шкалою,
 * поділками, стрілкою та центральною заглушкою виключно цілочисельними операціями.
 * @param gauge Вказівник на структуру стану приладу.
 * @param y Номер рядка на екрані (0..GAUGE_DISPLAY_HEIGHT-1).
 * @param line_buffer Вказівник на вихідний масив із 240 пікселів uint16_t.
 */
void gauge_render_scanline(const gauge_state_t *gauge, uint16_t y, uint16_t *line_buffer);

#ifdef __cplusplus
}
#endif

#endif /* GAUGE_RENDERER_H */
