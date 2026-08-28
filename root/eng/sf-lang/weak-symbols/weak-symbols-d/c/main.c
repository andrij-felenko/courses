// оголошуємо чужу функцію слабким посиланням: її може й не бути в цій збірці
__attribute__((weak)) void optional_logger_init(void);

void system_boot(void)
{
    // ... базове піднімання системи ...

    if (optional_logger_init) {          // символ ненульовий ⇔ модуль присутній
        optional_logger_init();          // є — гукаємо
    }
    // нема — просто пропускаємо, без жодної помилки лінкування
}
