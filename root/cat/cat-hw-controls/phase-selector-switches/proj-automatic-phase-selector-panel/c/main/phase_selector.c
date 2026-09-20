#include "phase_selector.h"
#include <math.h>
#include <string.h>
#include "esp_log.h"
#include "esp_timer.h"

static const char *TAG = "PHASE_SELECTOR";

static phase_selector_config_t s_config;
static phase_selector_status_t s_status = {0};
static bool s_initialized = false;
static int64_t s_state_entry_time = 0;

/// Апаратне відключення всіх силових реле (гарантія безпеки)
static void force_all_relays_off(void)
{
    gpio_set_level(s_config.relay_gpio_l1, 0);
    gpio_set_level(s_config.relay_gpio_l2, 0);
    gpio_set_level(s_config.relay_gpio_l3, 0);
}

/// Апаратне включення силового реле вибраної фази
static void set_active_relay(phase_id_t phase)
{
    force_all_relays_off();
    switch (phase) {
        case PHASE_L1:
            gpio_set_level(s_config.relay_gpio_l1, 1);
            break;
        case PHASE_L2:
            gpio_set_level(s_config.relay_gpio_l2, 1);
            break;
        case PHASE_L3:
            gpio_set_level(s_config.relay_gpio_l3, 1);
            break;
        default:
            break;
    }
}

/// Оцінка допустимості напруги фази із застосуванням гістерезису
static bool is_voltage_valid(float v_rms, bool currently_valid, float v_min, float v_max, float hyst)
{
    if (currently_valid) {
        // Розширений діапазон утримання стабільного стану
        return (v_rms >= (v_min - hyst)) && (v_rms <= (v_max + hyst));
    } else {
        // Звужений діапазон первинного входу в норму
        return (v_rms >= (v_min + hyst)) && (v_rms <= (v_max - hyst));
    }
}

/// Вибір найкращої доступної фази з урахуванням пріоритету
static phase_id_t select_best_phase(void)
{
    if (s_status.is_valid_l1) return PHASE_L1;
    if (s_status.is_valid_l2) return PHASE_L2;
    if (s_status.is_valid_l3) return PHASE_L3;
    return PHASE_NONE;
}

esp_err_t phase_selector_init(const phase_selector_config_t *config)
{
    if (config == NULL) {
        ESP_LOGE(TAG, "Помилка: нульовий вказівник конфігурації");
        return ESP_ERR_INVALID_ARG;
    }

    memcpy(&s_config, config, sizeof(phase_selector_config_t));

    // Налаштування GPIO виводів керування реле
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << config->relay_gpio_l1) | 
                        (1ULL << config->relay_gpio_l2) | 
                        (1ULL << config->relay_gpio_l3),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    esp_err_t err = gpio_config(&io_conf);
    if (err != ESP_OK) {
        ESP_LOGE(TAG, "Помилка налаштування GPIO реле");
        return err;
    }

    force_all_relays_off();

    s_status.active_phase = PHASE_NONE;
    s_status.target_phase = PHASE_NONE;
    s_status.fsm_state = FSM_STATE_INIT;
    s_state_entry_time = esp_timer_get_time() / 1000;
    s_initialized = true;

    ESP_LOGI(TAG, "Драйвер перемикача фаз успішно ініціалізовано");
    return ESP_OK;
}

esp_err_t phase_selector_process_samples(const float samples_l1[], 
                                         const float samples_l2[], 
                                         const float samples_l3[], 
                                         uint32_t num_samples)
{
    if (!s_initialized || num_samples == 0) {
        return ESP_ERR_INVALID_STATE;
    }

    // Обчислення True-RMS значення: корінь із середнього квадрату мгновенних напруг
    float sum_sq_l1 = 0.0f, sum_sq_l2 = 0.0f, sum_sq_l3 = 0.0f;

    for (uint32_t i = 0; i < num_samples; i++) {
        sum_sq_l1 += samples_l1[i] * samples_l1[i];
        sum_sq_l2 += samples_l2[i] * samples_l2[i];
        sum_sq_l3 += samples_l3[i] * samples_l3[i];
    }

    s_status.v_rms_l1 = sqrtf(sum_sq_l1 / (float)num_samples);
    s_status.v_rms_l2 = sqrtf(sum_sq_l2 / (float)num_samples);
    s_status.v_rms_l3 = sqrtf(sum_sq_l3 / (float)num_samples);

    // Перевірка відповідності напруг нормованим межам з гістерезисом
    s_status.is_valid_l1 = is_voltage_valid(s_status.v_rms_l1, s_status.is_valid_l1, 
                                            s_config.v_min_threshold, s_config.v_max_threshold, 
                                            s_config.v_hysteresis);
    s_status.is_valid_l2 = is_voltage_valid(s_status.v_rms_l2, s_status.is_valid_l2, 
                                            s_config.v_min_threshold, s_config.v_max_threshold, 
                                            s_config.v_hysteresis);
    s_status.is_valid_l3 = is_voltage_valid(s_status.v_rms_l3, s_status.is_valid_l3, 
                                            s_config.v_min_threshold, s_config.v_max_threshold, 
                                            s_config.v_hysteresis);

    return ESP_OK;
}

esp_err_t phase_selector_update(phase_selector_status_t *out_status)
{
    if (!s_initialized || out_status == NULL) {
        return ESP_ERR_INVALID_STATE;
    }

    int64_t now_ms = esp_timer_get_time() / 1000;
    uint32_t elapsed_ms = (uint32_t)(now_ms - s_state_entry_time);

    phase_id_t best_phase = select_best_phase();

    switch (s_status.fsm_state) {
        case FSM_STATE_INIT:
            if (best_phase != PHASE_NONE) {
                s_status.target_phase = best_phase;
                s_status.fsm_state = FSM_STATE_DEAD_TIME;
                s_state_entry_time = now_ms;
                force_all_relays_off();
                ESP_LOGI(TAG, "Ініціалізація: вибір фази %d, перехід у dead-time", best_phase);
            } else {
                s_status.fsm_state = FSM_STATE_FAULT;
            }
            break;

        case FSM_STATE_MONITOR:
            // Перевірка втрати або деградації поточної фази
            bool current_is_valid = false;
            if (s_status.active_phase == PHASE_L1) current_is_valid = s_status.is_valid_l1;
            else if (s_status.active_phase == PHASE_L2) current_is_valid = s_status.is_valid_l2;
            else if (s_status.active_phase == PHASE_L3) current_is_valid = s_status.is_valid_l3;

            if (!current_is_valid) {
                // Поточна фаза вийшла за межі норми, необхідне аварійне перемикання
                if (best_phase != PHASE_NONE) {
                    ESP_LOGW(TAG, "Втрата активної фази %d! Перехід на резерв %d", 
                             s_status.active_phase, best_phase);
                    s_status.target_phase = best_phase;
                    s_status.fsm_state = FSM_STATE_DEAD_TIME;
                    s_state_entry_time = now_ms;
                    force_all_relays_off();
                } else {
                    ESP_LOGE(TAG, "Аварія: усе три фази вийшли за припустимі межі!");
                    s_status.active_phase = PHASE_NONE;
                    s_status.target_phase = PHASE_NONE;
                    s_status.fsm_state = FSM_STATE_FAULT;
                    force_all_relays_off();
                }
            } else if (s_status.active_phase != PHASE_L1 && s_status.is_valid_l1) {
                // Пріоритетна фаза L1 відновилася, починаємо витримку затримки повернення
                ESP_LOGI(TAG, "Відновлення пріоритетної фази L1, запуск таймера повернення");
                s_status.target_phase = PHASE_L1;
                s_status.fsm_state = FSM_STATE_RETURN_DELAY;
                s_state_entry_time = now_ms;
            }
            break;

        case FSM_STATE_DEAD_TIME:
            // Очікування часу гасіння дуги для запобігання міжфазному замиканню
            if (elapsed_ms >= s_config.t_transfer_ms) {
                set_active_relay(s_status.target_phase);
                s_status.active_phase = s_status.target_phase;
                s_status.fsm_state = FSM_STATE_MONITOR;
                s_state_entry_time = now_ms;
                ESP_LOGI(TAG, "Dead-time завершено. Увімкнено фазу %d", s_status.active_phase);
            }
            break;

        case FSM_STATE_RETURN_DELAY:
            // Перевірка стійкості пріоритетної фази L1 під час витримки
            if (!s_status.is_valid_l1) {
                // L1 знову вийшла з ладу, скасовуємо повернення
                ESP_LOGW(TAG, "Сплеск на L1 під час витримки, повернення скасовано");
                s_status.target_phase = s_status.active_phase;
                s_status.fsm_state = FSM_STATE_MONITOR;
                s_state_entry_time = now_ms;
            } else if (elapsed_ms >= s_config.t_return_ms) {
                // Витримка завершена, виконуємо безпечний перехід на L1
                ESP_LOGI(TAG, "Затримка повернення витримана. Перемикання на L1");
                s_status.target_phase = PHASE_L1;
                s_status.fsm_state = FSM_STATE_DEAD_TIME;
                s_state_entry_time = now_ms;
                force_all_relays_off();
            }
            break;

        case FSM_STATE_FAULT:
            force_all_relays_off();
            s_status.active_phase = PHASE_NONE;
            if (best_phase != PHASE_NONE) {
                ESP_LOGI(TAG, "Відновлення мережі у стані FAULT, вибір фази %d", best_phase);
                s_status.target_phase = best_phase;
                s_status.fsm_state = FSM_STATE_DEAD_TIME;
                s_state_entry_time = now_ms;
            }
            break;
    }

    memcpy(out_status, &s_status, sizeof(phase_selector_status_t));
    return ESP_OK;
}
