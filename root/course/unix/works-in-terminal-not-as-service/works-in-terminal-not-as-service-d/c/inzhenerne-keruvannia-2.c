#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void setup_service_stdio(void) {
    /* Перевіряємо, чи ми працюємо не в інтерактивному терміналі */
    if (!isatty(fileno(stdout))) {
        /* Примусово вмикаємо рядкову буферизацію для stdout */
        setvbuf(stdout, NULL, _IOLBF, 0);
    }
    
    /* stderr завжди має бути небуферизованим */
    setvbuf(stderr, NULL, _IONBF, 0);

    /* Закриваємо або перенаправляємо stdin у разі потреби */
    if (!isatty(fileno(stdin))) {
        freopen("/dev/null", "r", stdin);
    }
}
