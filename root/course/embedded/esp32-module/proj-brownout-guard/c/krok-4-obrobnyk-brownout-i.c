IRAM_ATTR static void rtc_brownout_isr_handler(void *arg)
{
    brownout_ll_intr_clear();               // 1. зняти прапорець переривання

    esp_cpu_stall(other_core_id);           // 2. зупинити друге ядро

    esp_reset_reason_set_hint(ESP_RST_BROWNOUT);  // 3. лишити підказку в RTC

    ESP_DRAM_LOGI(TAG, "Brownout detector was triggered\r\n\r\n");  // 4. друк із DRAM

    esp_restart_noos();                     // 5. негайний перезапуск
}
