// Приклад рішення на робочій частоті з тепловим бюджетом 0.2 Вт.
void decide_example(void)
{
    switch_dev_t bjt = { "BJT 2N2222", 0.30f, false, 0.3e-6f, 0.3e-6f };
    switch_dev_t mos = { "MOSFET лог.", 0.05f, true,  0.03e-6f, 0.03e-6f };

    // На 20 кГц обидва вкладаються в 0.2 Вт → обираємо простіший/дешевший (BJT).
    printf("20 кГц: %s\n", choose_switch(&bjt, &mos, 12, 0.5f, 0.5f, 20e3f, 0.2f));
    // На 100 кГц BJT (0.255 Вт) вилітає за бюджет 0.2 Вт → лишається MOSFET.
    printf("100 кГц: %s\n", choose_switch(&bjt, &mos, 12, 0.5f, 0.5f, 100e3f, 0.2f));
}
