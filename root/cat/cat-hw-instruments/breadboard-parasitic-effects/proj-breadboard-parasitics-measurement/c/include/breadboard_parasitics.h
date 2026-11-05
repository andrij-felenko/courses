#ifndef BREADBOARD_PARASITICS_H
#define BREADBOARD_PARASITICS_H

#include "oscilloscope_trace.h"
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * @brief Оцінка технічного стану контактних затискачів макетної плати.
 */
typedef enum {
    CONTACT_HEALTH_NEW = 0,        /* Новий контакт (відмінний стан, R_cont < 50 мОм) */
    CONTACT_HEALTH_ACCEPTABLE = 1, /* Задовільний робочий стан (50 мОм <= R_cont <= 200 мОм) */
    CONTACT_HEALTH_DEGRADED = 2    /* Зношений або окислений контакт (R_cont > 200 мОм) */
} contact_health_t;

/**
 * @brief Параметри конфігурації вимірювального стенда.
 */
typedef struct {
    double test_resistance_ohm;  /* Опір тестового резистора R_test, Ом (типово 10 кОм) */
    double probe_capacitance_f;  /* Власна вхідна ємність щупа осцилографа C_probe, Ф (типово 12 пФ для 10X) */
    double test_load_current_a;  /* Тестовий струм навантаження I_test, А (типово 0.5 А) */
} test_bench_config_t;

/**
 * @brief Зведений метрологічний та діагностичний звіт параметрів контакту.
 */
typedef struct {
    double rise_time_ns;            /* Тривалість наростання фронту t_r (10%-90%), нс */
    double total_capacitance_pf;     /* Повна виміряна ємність вимірювального вузла C_total, пФ */
    double parasitic_capacitance_pf; /* Власна міжрейкова паразитна ємність плати C_par, пФ */
    double cutoff_frequency_mhz;     /* Гранична частота зрізу RC-кола f_-3dB на тестовому опорі, МГц */
    double voltage_drop_mv;          /* Резистивне падіння напруги під струмовим навантаженням, мВ */
    double contact_resistance_mohm;  /* Розрахований контактний опір R_cont, мОм */
    contact_health_t health;         /* Класифікація зносу контактної групи */
    char notes[384];                 /* Інженерний висновок та експлуатаційні рекомендації */
} parasitic_report_t;

/**
 * @brief Переведення технічного стану контакту в текстовий вигляд.
 * @param health Стан контакту.
 * @return Рядковий літерал українською мовою.
 */
const char *contact_health_to_string(contact_health_t health);

/**
 * @brief Розрахунок повної ємності вузла за тривалістю наростання фронту: C_total = t_r / (ln(9) * R_test).
 * @param config Конфігурація вимірювального стенда.
 * @param rise_time_s Час наростання 10%-90% у секундах.
 * @return Повна ємність у фарадах.
 */
double calculate_total_capacitance(const test_bench_config_t *config, double rise_time_s);

/**
 * @brief Розрахунок паразитної ємності контактів плати з компенсацією ємності щупа: C_par = max(0, C_total - C_probe).
 * @param config Конфігурація вимірювального стенда.
 * @param rise_time_s Час наростання 10%-90% у секундах.
 * @return Паразитна ємність плати у фарадах.
 */
double calculate_parasitic_capacitance(const test_bench_config_t *config, double rise_time_s);

/**
 * @brief Розрахунок контактного опору за падінням напруги під навантаженням: R_cont = Delta_V / I_load.
 * @param config Конфігурація вимірювального стенда.
 * @param voltage_drop_v Падіння напруги на контакті у вольтах.
 * @return Контактний опір в омах.
 */
double calculate_contact_resistance(const test_bench_config_t *config, double voltage_drop_v);

/**
 * @brief Розрахунок частоти зрізу f_-3dB еквівалентного RC-ланцюга для паразитної ємності плати.
 * @param config Конфігурація вимірювального стенда.
 * @param capacitance_f Ємність у фарадах.
 * @return Гранична частота зрізу в герцах.
 */
double calculate_cutoff_frequency(const test_bench_config_t *config, double capacitance_f);

/**
 * @brief Автоматична класифікація технічного стану контактного затискача за величиною опору.
 * @param contact_resistance_ohm Контактний опір в омах.
 * @return Категорія технічного стану (новий, задовільний, деградований).
 */
contact_health_t assess_contact_health(double contact_resistance_ohm);

/**
 * @brief Виділення величини падіння напруги з осцилограми імпульсного навантаження.
 * @param load_trace Осцилограма перехідного процесу під навантаженням.
 * @return Резистивне падіння напруги у вольтах (Delta_V).
 */
double extract_contact_voltage_drop(const oscilloscope_trace_t *load_trace);

/**
 * @brief Комплексний аналіз на основі осцилограми перехідного фронту та числового значення падіння напруги.
 * @param config Конфігурація вимірювального стенда.
 * @param step_trace Осцилограма заряджання RC-кола.
 * @param voltage_drop_v Величина спаду напруги у вольтах.
 * @param out_report Вихідна структура для запису діагностичного звіту.
 * @return true у разі успішного аналізу, false при некоректних даних.
 */
bool analyze_breadboard_parasitics(const test_bench_config_t *config,
                                   const oscilloscope_trace_t *step_trace,
                                   double voltage_drop_v,
                                   parasitic_report_t *out_report);

/**
 * @brief Комплексний аналіз на основі двох осцилограм (RC-фронту та імпульсу навантаження).
 * @param config Конфігурація вимірювального стенда.
 * @param step_trace Осцилограма наростання напруги вхідного фронту.
 * @param load_trace Осцилограма просідання напруги під імпульсом струму.
 * @param out_report Вихідна структура для запису діагностичного звіту.
 * @return true у разі успіху, false при помилці.
 */
bool analyze_breadboard_parasitics_traces(const test_bench_config_t *config,
                                          const oscilloscope_trace_t *step_trace,
                                          const oscilloscope_trace_t *load_trace,
                                          parasitic_report_t *out_report);

#ifdef __cplusplus
}
#endif

#endif /* BREADBOARD_PARASITICS_H */
