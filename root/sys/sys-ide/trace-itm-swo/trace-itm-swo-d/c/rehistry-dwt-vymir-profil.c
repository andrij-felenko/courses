// Частку часу, проведену в задачі простою, рахуємо лічильником тактів
static uint32_t idle_cycles, last_window;

void idle_hook(void) {              // викликається, коли робити нічого
    uint32_t t0 = DWT->CYCCNT;
    __WFI();                        // ядро спить до переривання
    idle_cycles += DWT->CYCCNT - t0;   // накопичуємо такти простою
}

// Раз на секунду рахуємо завантаження (частку часу поза простоєм)
float cpu_load_percent(void) {
    uint32_t now = DWT->CYCCNT;
    uint32_t window = now - last_window;        // тактів за вікно
    float load = 100.0f * (1.0f - (float)idle_cycles / (float)window);
    last_window = now;
    idle_cycles = 0;
    return load;                                 // % часу, коли ядро НЕ простоювало
}
