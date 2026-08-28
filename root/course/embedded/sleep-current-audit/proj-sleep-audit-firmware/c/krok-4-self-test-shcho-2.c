// Самотест ділення навпіл: лишає по одній гілці й чекає зняття струму.
// Запускати з пристроєм у розриві живлення під лічильником/профілювальником.
void sleep_self_test(void)
{
    const TickType_t SETTLE = pdMS_TO_TICKS(3000);  // час зняти усталене число

    apply_sleep_profile();   // ніжки — у безпечний стан, як перед справжнім сном
    all_branches_off();
    ESP_LOGI("AUDIT", "усі гілки OFF — зніми струм (це ПІДЛОГА: сам чип)");
    vTaskDelay(SETTLE);

    for (size_t i = 0; i < BRANCH_LEN; i++) {
        all_branches_off();
        gpio_set_level(BRANCHES[i].en_pin, 1);       // лишаємо рівно одну гілку
        ESP_LOGI("AUDIT", "увімкнено ТІЛЬКИ '%s' — зніми струм; "
                          "внесок гілки = показ − підлога", BRANCHES[i].name);
        vTaskDelay(SETTLE);
    }

    all_branches_off();
    ESP_LOGI("AUDIT", "self-test завершено — усі гілки OFF");
}
