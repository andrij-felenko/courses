void enter_audited_deep_sleep(void)
{
    apply_sleep_profile();          // 1) усі ніжки → безпечний рівень (один прохід)
    sensor_power_down();            // 2) правильний порядок: сигнали → потім VDD
    display_power_down();           //    (так само для решти вузлів за load switch)
    radio_power_down();

    freeze_pins_for_deep_sleep();   // 3) заморозити цифрові ніжки на deep-sleep
    isolate_rtc_pins();             //    + ізолювати конфліктні RTC-ніжки

    esp_deep_sleep_start();         // тепер кран закритий з усіх боків
}
