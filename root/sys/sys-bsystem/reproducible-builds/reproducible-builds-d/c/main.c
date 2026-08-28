/* Детерміністичний підхід: використання канонічних констант версії */
#include <stdio.h>

#ifndef PROJECT_VERSION_STRING
#define PROJECT_VERSION_STRING "1.0.0-release"
#endif

#ifndef MODULE_NAME
#define MODULE_NAME "core_engine"
#endif

void log_module_info(void) {
    /* Детерміністично: версія фіксується системою контролю версій */
    printf("Software Version: %s\n", PROJECT_VERSION_STRING);
    /* Детерміністично: використовується логічне ім'я модуля замість шляху файлу */
    printf("Module: %s\n", MODULE_NAME);
}
