// ПРАВИЛЬНО: спершу зняти сигнали, потім гасити живлення вузла
static void sensor_power_down(void)
{
    // 1) Знімаємо потенціал із усіх ліній, що дивляться в давач.
    gpio_set_level(SENSOR_DATA_PIN, 0);
    gpio_set_level(SENSOR_CLK_PIN,  0);
    gpio_set_level(SENSOR_CS_PIN,   0);

    // 2) Лише тепер гасимо VDD вузла через його load switch.
    //    На момент зняття живлення на жодній ніжці немає 3.3 В →
    //    діод давача замкнений → зворотного струму немає.
    gpio_set_level(SENSOR_LOADSW_EN, 0);
}
