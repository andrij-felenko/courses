#include <stdint.h>
#include <stdbool.h>

// Перелічуваний тип статусів вимірювання відстані
typedef enum {
    GP2Y0A21_STATUS_OK = 0,         // Дані валідні, об'єкт у діапазоні 10-80 см
    GP2Y0A21_STATUS_BLIND_ZONE,     // Об'єкт у сліпій зоні (< 10 см)
    GP2Y0A21_STATUS_TOO_FAR,        // Об'єкт за межею вимірювання (> 80 см)
    GP2Y0A21_STATUS_HW_FAULT        // Апаратний збій (обрив лінії або коротке замикання)
} gp2y0a21_status_t;

// Структурний тип стану діагностики з гістерезисом
typedef struct {
    uint16_t u_high_mv;             // Верхній поріг входження в сліпу зону (наприклад, 2850 мВ)
    uint16_t u_low_mv;              // Нижній поріг виходу зі сліпої зони (наприклад, 2650 мВ)
    uint16_t u_min_far_mv;          // Поріг дальньої межі (наприклад, 400 мВ)
    bool in_blind_zone;             // Прапорець перебування у сліпій зоні
} gp2y0a21_diag_t;

void gp2y0a21_diag_init(gp2y0a21_diag_t *diag) {
    diag->u_high_mv = 2850;
    diag->u_low_mv = 2650;
    diag->u_min_far_mv = 400;
    diag->in_blind_zone = false;
}

gp2y0a21_status_t gp2y0a21_diagnose_voltage(gp2y0a21_diag_t *diag, uint16_t raw_mv) {
    // 1. Апаратна діагностика обриву лінії (0 мВ) або короткого замикання / насичення ADC (> 3250 мВ)
    if (raw_mv < 50 || raw_mv > 3250) {
        return GP2Y0A21_STATUS_HW_FAULT;
    }

    // 2. Оновлення стану гістерезису для сліпої зони
    if (!diag->in_blind_zone) {
        if (raw_mv >= diag->u_high_mv) {
            diag->in_blind_zone = true;
        }
    } else {
        if (raw_mv < diag->u_low_mv) {
            diag->in_blind_zone = false;
        }
    }

    // 3. Формування підсумкового статусу
    if (diag->in_blind_zone) {
        return GP2Y0A21_STATUS_BLIND_ZONE;
    }

    if (raw_mv < diag->u_min_far_mv) {
        return GP2Y0A21_STATUS_TOO_FAR;
    }

    return GP2Y0A21_STATUS_OK;
}
