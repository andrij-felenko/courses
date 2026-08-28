void enter_deep_sleep_cycle(void)
{
    /* 1. Підготовка виводів та апаратури */
    low_power_pins_enter_sleep();

    /* 2. Вхід у режим Stop/Standby */
    __asm volatile("wfi");

    /* 3. Відновлення після пробудження перериванням від RTC або EXTI */
    low_power_pins_restore();
}
