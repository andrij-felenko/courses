#include <math.h>
#include <unistd.h>
#include <stdlib.h>

/* Обчислення затримки експоненційного відкату з випадковим джитером */
unsigned int calculate_retry_delay_ms(int attempt, unsigned int base_ms, unsigned int max_ms) {
    if (attempt < 0) attempt = 0;
    if (attempt > 10) attempt = 10;
    
    unsigned int exp_delay = base_ms * (1U << attempt);
    if (exp_delay > max_ms) exp_delay = max_ms;
    
    /* Додаємо джитер до 25% від затримки для усунення синхронних сплесків */
    unsigned int jitter = (unsigned int)(rand() % (exp_delay / 4 + 1));
    return exp_delay + jitter;
}
