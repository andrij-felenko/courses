#include <stdio.h>
#include <stdbool.h>
#include <unistd.h>

/* Параметри кваліфікаційного тесту за стандартом JEDEC JESD78 */
#define JESD78_TRIG_CURRENT_MA    100.0   /* Струм інжекції ±100 мА */
#define JESD78_PULSE_DURATION_US  10000   /* Тривалість імпульсу 10 мс */
#define JESD78_MAX_IDD_DELTA_MA   10.0    /* Поріг фіксації засувки 10 мА */

typedef struct {
    double vdd_volts;
    double quiescent_idd_ma;
    bool latchup_detected;
} jesd78_test_result_t;

/* Емуляція вимірювального циклу JESD78 для тестового піна */
jesd78_test_result_t run_jesd78_pin_test(int pin_id, double inject_current_ma) {
    jesd78_test_result_t res = { .vdd_volts = 3.3, .quiescent_idd_ma = 0.015, .latchup_detected = false };
    
    /* 1. Вимірювання початкового струму спокою */
    double idd_baseline = res.quiescent_idd_ma;
    
    /* 2. Подача тригерного струму в пін I/O */
    printf("[JESD78] Тестування піна %d: інжекція %.1f мА...\n", pin_id, inject_current_ma);
    usleep(JESD78_PULSE_DURATION_US);
    
    /* 3. Зняття тригерного струму та стабілізація */
    usleep(5000); /* Пауза 5 мс після завершення інжекції */
    
    /* 4. Фіксація залишкового струму шини живлення */
    double idd_post = idd_baseline; /* У разі відсутності latchup */
    
    double delta_idd = idd_post - idd_baseline;
    if (delta_idd > JESD78_MAX_IDD_DELTA_MA) {
        res.latchup_detected = true;
        printf("[FAIL] Виявлено Latch-up на піні %d! Струм ΔIdd = %.2f мА\n", pin_id, delta_idd);
    } else {
        printf("[PASS] Пін %d витримав тест. ΔIdd = %.4f мА\n", pin_id, delta_idd);
    }
    
    return res;
}
