// Варіант 1: Програмне перемикання виводу в ISR (піддається джитеру ISR)
static void IRAM_ATTR dda_timer_isr_handler(void* arg) {
    // Вхід у переривання зазнає варіації затримки τ_lat
    gpio_set_level(CONFIG_STEP_GPIO, 1);
    
    uint32_t next_period = calculate_next_dda_step();
    timer_set_alarm_value(TIMER_GROUP_0, TIMER_0, next_period);
    
    gpio_set_level(CONFIG_STEP_GPIO, 0);
}

// Варіант 2: Подвійне апаратне буферування періодів (J_ISR = 0)
void setup_hardware_output_compare(void) {
    // Налаштування апаратного виводу на автоматичний переключатель за подією таймера
    mcpwm_config_t pwm_config = {
        .frequency = 100000, // Частота таймера f_timer = 100 кГц
        .cmpr_a = 0,          // Початкове значення порівняння
        .counter_mode = MCPWM_UP_COUNTER,
        .duty_mode = MCPWM_DUTY_MODE_0
    };
    mcpwm_init(MCPWM_UNIT_0, MCPWM_TIMER_0, &pwm_config);
    // Апаратне перемикання виводу відбувається без участі ядра процесора
}
