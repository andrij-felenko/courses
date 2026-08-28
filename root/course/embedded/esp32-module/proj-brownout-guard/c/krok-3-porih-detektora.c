// Перевести номер рівня класичного ESP32 у напругу (мВ) за офіційною таблицею.
static int brownout_threshold_mv(void)
{
#if   CONFIG_ESP_BROWNOUT_DET_LVL_SEL_0
    return 2430;
#elif CONFIG_ESP_BROWNOUT_DET_LVL_SEL_1
    return 2480;
#elif CONFIG_ESP_BROWNOUT_DET_LVL_SEL_2
    return 2580;
#elif CONFIG_ESP_BROWNOUT_DET_LVL_SEL_3
    return 2620;
#elif CONFIG_ESP_BROWNOUT_DET_LVL_SEL_4
    return 2670;
#elif CONFIG_ESP_BROWNOUT_DET_LVL_SEL_5
    return 2700;
#elif CONFIG_ESP_BROWNOUT_DET_LVL_SEL_6
    return 2770;
#elif CONFIG_ESP_BROWNOUT_DET_LVL_SEL_7
    return 2800;
#else
    return -1;   // детектор вимкнено
#endif
}
