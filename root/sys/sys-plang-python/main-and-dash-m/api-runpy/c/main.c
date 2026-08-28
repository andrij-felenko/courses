typedef struct {
    int parse_argv;            /* 1 = парсити аргументи командного рядка CLI */
    wchar_t *run_command;      /* Команда для запуску (аналог прапорця -c) */
    wchar_t *run_module;       /* Модуль для запуску через runpy (аналог -m) */
    wchar_t *run_filename;     /* Шлях до файлу, каталогу або zipapp */
    
    PyConfig_Argv argv;        /* Список аргументів для заповнення sys.argv */
    PyConfig_Argv orig_argv;   /* Оригінальні аргументи операційної системи */
    /* ... додаткові поля шляхів та алокаторів пам'яті ... */
} PyConfig;
