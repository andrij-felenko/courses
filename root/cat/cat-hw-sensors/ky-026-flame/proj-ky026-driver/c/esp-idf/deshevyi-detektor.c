#define MIN_LEVEL 480         // мінімум середнього ІЧ у 12-бітних одиницях

static flicker_t flick = { .ch = ADC_CHANNEL_6, .lo = 2.0f, .hi = 20.0f };

// Окрема задача семплює рівним кроком — це надійніше за лічильник у loop().
static void flame_task(void *arg) {
    flicker_begin(&flick);
    TickType_t next = xTaskGetTickCount();
    int n = 0;
    for (;;) {
        flicker_sample(&flick);                       // семплюй якомога рівніше

        if (++n >= 40) {                              // друкуй нечасто, семплюй часто
            n = 0;
            bool bright   = flicker_level(&flick) > MIN_LEVEL;  // є помітний ІЧ
            bool flickers = flicker_flame(&flick);              // і він пульсує 2..20 Гц
            ESP_LOGI(TAG, "рівень=%d  f=%.1f Гц  →  %s",
                     flicker_level(&flick), flick.last_freq,
                     (bright && flickers) ? "ВОГОНЬ" : "спокій");
        }
        vTaskDelayUntil(&next, pdMS_TO_TICKS(5));     // рівні 5 мс = 200 Гц вибірки
    }
}

void app_main(void) {
    adc_oneshot_unit_init_cfg_t unit = { .unit_id = ADC_UNIT_1 };
    ESP_ERROR_CHECK(adc_oneshot_new_unit(&unit, &flick.adc));
    adc_oneshot_chan_cfg_t ch = { .atten = ADC_ATTEN_DB_12, .bitwidth = ADC_BITWIDTH_DEFAULT };
    ESP_ERROR_CHECK(adc_oneshot_config_channel(flick.adc, flick.ch, &ch));
    xTaskCreate(flame_task, "flame", 4096, NULL, 5, NULL);
}
