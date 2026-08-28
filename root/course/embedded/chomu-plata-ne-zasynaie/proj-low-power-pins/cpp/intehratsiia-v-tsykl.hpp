void enter_deep_sleep_cycle(LowPower::SleepManager& sleep_manager) noexcept
{
    {
        /* RAII-об'єкт ізолює піни при створенні та автоматично відновлює при виході з блоку */
        auto sleep_guard = sleep_manager.guard();

        /* Ядро засинає */
        asm volatile("wfi");
    }
    /* Тут усі піни вже гарантовано відновлені у вихідний робочий стан */
}
