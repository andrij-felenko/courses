// Пороги в 12-бітних одиницях — уперед-калібровані під 0..4095, а не 0..1023.
#define SEE_FIRE   800.0f      // сума жару, з якої робот починає їхати на вогонь
#define BURN_NEAR 2800.0f      // сума, з якої вважаємо, що впритул → гасити
#define BASE_SPD   140         // базова швидкість руху вперед
#define TURN_GAIN  0.6f        // наскільки різко кермувати за різницею

void app_main(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &adc));
    adc_oneshot_chan_cfg_t cfg = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc, AO_L_CH, &cfg));
    ESP_ERROR_CHECK(adc_oneshot_config_channel(adc, AO_R_CH, &cfg));
    motors_init();
    gpio_set_level(FAN, 0);

    int l = 0, r = 0;                          // старт середніх — з поточних значень
    adc_oneshot_read(adc, AO_L_CH, &l); ir_l = l;
    adc_oneshot_read(adc, AO_R_CH, &r); ir_r = r;

    for (;;) {
        read_sensors();
        float sum  = ir_l + ir_r;              // загальна близькість вогню
        float diff = ir_l - ir_r;              // >0 → жар зліва, <0 → справа

        if (sum < SEE_FIRE) {                  // вогню не видно — стій
            gpio_set_level(FAN, 0);
            drive(0, 0);
        } else if (sum >= BURN_NEAR) {         // впритул — стоп і дми
            drive(0, 0);
            gpio_set_level(FAN, 1);
        } else {                               // бачимо вогонь — їдемо, підрулюючи
            gpio_set_level(FAN, 0);
            int turn = (int)(TURN_GAIN * diff);
            drive(BASE_SPD - turn, BASE_SPD + turn);
        }
        vTaskDelay(pdMS_TO_TICKS(20));         // ~50 Гц — досить для керма
    }
}
