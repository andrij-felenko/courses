// hal_hazard.c (C99)
__attribute__((weak)) void hal_tick_hook(void)
{
    // порожньо
}

void hal_process(void)
{
    hal_tick_hook(); // Компілятор може вбудувати (inline) це порожнє тіло!
}
