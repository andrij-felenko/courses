void startup_check(void) {
    esp_reset_reason_t reason = esp_reset_reason();

    // 1. Структура зіпсута (System Reset / нова плата / збій біта)? Почати з нуля.
    if (!bs_valid(&s_bs) || reason == ESP_RST_POWERON) {
        s_bs.fail_cnt = 0;
        s_bs.last_uptime = 0;
        bs_commit(&s_bs);
    }

    bool pathological = (reason == ESP_RST_TASK_WDT ||
                         reason == ESP_RST_INT_WDT  ||
                         reason == ESP_RST_PANIC);

    if (pathological) {
        // 2. Щільність: попередній збій стався після короткого життя?
        //    last_uptime малий → пристрій ледь піднявся й упав → щільна серія.
        if (s_bs.last_uptime <= BURST_WINDOW_S) {
            s_bs.fail_cnt++;                 // та сама серія росте
        } else {
            s_bs.fail_cnt = 1;              // попереднє застаріло — нова серія
        }
        ESP_LOGW(TAG, "fault (%d), burst_cnt=%u", reason, s_bs.fail_cnt);
        bs_commit(&s_bs);
    }

    // 3. Поріг щільної серії перейдено — лізти драбиною, спираючись на NVS-журнал.
    if (s_bs.fail_cnt >= FAULT_THRESHOLD) {
        esc_level_t level = esc_load();      // що ми вже пробували?
        switch (level) {
            case ESC_NORMAL:
                esc_store(ESC_CONFIG_ROLLED);
                config_rollback();           // спершу відкотити конфіг
                break;
            case ESC_CONFIG_ROLLED:
                esc_store(ESC_FW_ROLLED);
                esp_ota_mark_app_invalid_rollback_and_reboot();  // тоді прошивку
                break;
            default:
                break;                       // усе вичерпано — лишаємось у safe mode
        }
        enter_safe_mode();
        return;
    }

    // 4. Нормальний старт: завести таймер стабільності.
    start_stability_timer();
    // ... звичайна ініціалізація
}
