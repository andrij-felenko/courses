#include <stdio.h>
#include <inttypes.h>
#include "alarm_rationalizer.h"
#include "plausibility_checker.h"

int main(void) {
    printf("=== Диспетчер та раціоналізатор тривог ISA-18.2 (C99) ===\n\n");

    AlarmRationalizer_t ar;
    alarm_rationalizer_init(&ar);

    /* 1. Реєстрація первинної тривоги: Втрата головної шини живлення 28V (Parent Alarm) */
    AlarmConfig_t power_loss_cfg = {
        .id = 0,
        .tag = "PWR_MAIN_BUS_UV",
        .action_text = "Увімкнути резервний акумулятор, перевірити інвертор",
        .consequence = "Повна втрата живлення корисного навантаження та зв'язку",
        .priority = ALARM_PRIO_CRITICAL,
        .category = ALARM_CAT_SAFETY,
        .response_time_limit_ms = 10000,
        .trip_threshold = 22.0f,
        .clear_threshold = 24.5f,
        .is_high_alarm = false,
        .on_delay_ms = 100,
        .off_delay_ms = 500,
        .chatter_limit = 3,
        .chatter_window_ms = 5000,
        .suppression_state_mask = SYS_STATE_COLD_BOOT | SYS_STATE_MAINTENANCE,
        .parent_alarm_id = -1
    };
    alarm_rationalizer_register(&ar, &power_loss_cfg);

    /* 2. Реєстрація вторинної тривоги: Втрата телеметрії лідара (Child Alarm, пригнічується при PWR_MAIN_BUS_UV) */
    AlarmConfig_t lidar_comm_cfg = {
        .id = 1,
        .tag = "LIDAR_COMM_LOST",
        .action_text = "Перевірити живлення та кабель RS-485 лідара",
        .consequence = "Неможливість побудови карти перешкод на малій висоті",
        .priority = ALARM_PRIO_MEDIUM,
        .category = ALARM_CAT_COMMUNICATION,
        .response_time_limit_ms = 60000,
        .trip_threshold = 0.5f,
        .clear_threshold = 0.5f,
        .is_high_alarm = false,
        .on_delay_ms = 500,
        .off_delay_ms = 1000,
        .chatter_limit = 4,
        .chatter_window_ms = 10000,
        .suppression_state_mask = SYS_STATE_COLD_BOOT | SYS_STATE_STANDBY,
        .parent_alarm_id = 0 /* Батьківська тривога - PWR_MAIN_BUS_UV */
    };
    alarm_rationalizer_register(&ar, &lidar_comm_cfg);

    /* 3. Реєстрація діагностичної тривоги достовірності сенсорів (Sensor Plausibility) */
    AlarmConfig_t plausibility_cfg = {
        .id = 2,
        .tag = "SENSOR_PLAUSIBILITY_WARN",
        .action_text = "Звірити первинні прилади, перейти на ручне керування",
        .consequence = "Сліпа довіра до здеградованого фільтра EKF спричинить зіткнення",
        .priority = ALARM_PRIO_HIGH,
        .category = ALARM_CAT_SENSOR_HEALTH,
        .response_time_limit_ms = 15000,
        .trip_threshold = 0.50f, /* Тривога якщо confidence_score < 0.50 */
        .clear_threshold = 0.75f,
        .is_high_alarm = false,
        .on_delay_ms = 200,
        .off_delay_ms = 1000,
        .chatter_limit = 3,
        .chatter_window_ms = 5000,
        .suppression_state_mask = SYS_STATE_COLD_BOOT,
        .parent_alarm_id = -1
    };
    alarm_rationalizer_register(&ar, &plausibility_cfg);

    /* Ініціалізація перевірки достовірності */
    PlausibilityCheckerConfig_t pc_cfg = {
        .max_allowed_accel_jerk = 15.0f,
        .max_kinematic_residual = 3.5f,
        .max_power_residual_w = 45.0f,
        .min_confidence_alarm_threshold = 0.50f,
        .diagnostic_alarm_id = 2
    };
    PlausibilityChecker_t pc;
    plausibility_checker_init(&pc, &pc_cfg);

    printf("[1] Перехід системи у робочий стан SYS_STATE_MISSION (now = 1000 ms)\n");
    alarm_rationalizer_set_system_state(&ar, SYS_STATE_MISSION, 1000);

    /* Тест 1: Номінальна робота (все в нормі) */
    alarm_rationalizer_update_value(&ar, 0, 27.8f, 1000);
    alarm_rationalizer_update_value(&ar, 1, 1.0f, 1000);
    plausibility_check_battery_power(&pc, 27.8f, 12.0f, 330.0f, 1000);
    plausibility_check_kinematics(&pc, 0.2f, 15.0f, 1000);
    plausibility_sync_to_rationalizer(&pc, &ar, 1000);
    alarm_rationalizer_process(&ar, 1000);

    uint16_t active[MAX_ALARMS];
    size_t active_cnt = alarm_rationalizer_get_active_hmi_alarms(&ar, active, MAX_ALARMS);
    printf("   Активних тривог на HMI: %zu\n", active_cnt);

    /* Тест 2: Аварія живлення (PWR_MAIN_BUS_UV спадає до 19.5V, лідар також падає) */
    printf("\n[2] Аварія шини живлення 28V (падає до 19.5V, now = 2000 ms)\n");
    alarm_rationalizer_update_value(&ar, 0, 19.5f, 2000);
    alarm_rationalizer_update_value(&ar, 1, 0.0f, 2000); /* Вторинний збій лідара */
    
    /* Прогін часу 200 ms для спрацювання On-Delay (100 ms) */
    alarm_rationalizer_process(&ar, 2200);

    active_cnt = alarm_rationalizer_get_active_hmi_alarms(&ar, active, MAX_ALARMS);
    printf("   Активних тривог на HMI: %zu\n", active_cnt);
    for (size_t i = 0; i < active_cnt; ++i) {
        uint16_t id = active[i];
        printf("   -> [%s] Стан=%d, Пріоритет=%d, Дія=\"%s\"\n",
               ar.configs[id].tag, ar.runtimes[id].state,
               ar.configs[id].priority, ar.configs[id].action_text);
    }
    printf("   Стан вторинної тривоги LIDAR_COMM_LOST (ID 1): Стан=%d (SuppressedByParent=%s)\n",
           ar.runtimes[1].state, ar.runtimes[1].is_suppressed_by_parent ? "ТАК" : "НІ");

    /* Тест 3: Квитування первинної тривоги оператором */
    printf("\n[3] Оператор натискає ACK для тривоги PWR_MAIN_BUS_UV (now = 3000 ms)\n");
    alarm_rationalizer_ack(&ar, 0, 3000);
    alarm_rationalizer_process(&ar, 3000);
    printf("   Стан PWR_MAIN_BUS_UV після ACK: %d (ACK_ALARM)\n", ar.runtimes[0].state);

    /* Тест 4: Перевірка розбіжності сенсорів (GPS спуфінг / дрейф IMU) */
    printf("\n[4] Симуляція спуфінгу GNSS: розбіжність прискорення IMU (0.1 м/с2) та стрибка швидкості GNSS (now = 4000 ms)\n");
    plausibility_check_kinematics(&pc, 0.1f, 35.0f, 4000); /* Стрибок з 15 до 35 м/с за 3 сек */
    plausibility_sync_to_rationalizer(&pc, &ar, 4000);
    alarm_rationalizer_process(&ar, 4500);

    printf("   Оцінка швидкості: %.1f м/с, Довірчий інтервал 95%%: +/-%.2f м/с, Достовірність=%.2f (Статус=%d)\n",
           pc.nav_velocity_confidence.estimated_value,
           pc.nav_velocity_confidence.confidence_bound_95,
           pc.nav_velocity_confidence.confidence_score,
           pc.nav_velocity_confidence.status);

    active_cnt = alarm_rationalizer_get_active_hmi_alarms(&ar, active, MAX_ALARMS);
    printf("   Активних тривог на HMI після збою достовірності: %zu\n", active_cnt);
    for (size_t i = 0; i < active_cnt; ++i) {
        uint16_t id = active[i];
        printf("   -> [%s] Стан=%d, Пріоритет=%d, Дія=\"%s\"\n",
               ar.configs[id].tag, ar.runtimes[id].state,
               ar.configs[id].priority, ar.configs[id].action_text);
    }

    printf("\nПідсумок: Лавина тривог ліквідована, вторинні тривоги пригнічені, довірчі інтервали розраховані.\n");
    return 0;
}
