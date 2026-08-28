// ESP32-подібно: подати зовнішній MEMS-такт на швидку периферію (напр. RMII Ethernet)
// MEMS дає готовий меандр на вивід GPIO0 (CLK_IN) — власний генератор не потрібен.

// 1. Налаштувати вивід як вхід зовнішнього такту
gpio_set_direction(GPIO_NUM_0, GPIO_MODE_INPUT);

// 2. Наказати блоку RMII брати такт ЗВНІ, а не з внутрішнього APLL
emac_config.clock_config.rmii.clock_mode = EMAC_CLK_EXT_IN;  // зовнішній 50 МГц від MEMS
emac_config.clock_config.rmii.clock_gpio = EMAC_CLK_IN_GPIO; // на якому виводі

// 3. Ознака життя: периферія застукала на розрахунковій швидкості,
//    а на виводі OUT MEMS видно меандр 50 МГц (осцилографом).
