#define SCRAM_MAX_ITERATIONS 65536

int scram_check_iteration_count(long i) {
    /* Нижня межа — вимога RFC 5802 (не менше 4096);
       верхня — захист самого клієнта від навмисного вичерпання CPU. */
    if (i < 4096 || i > SCRAM_MAX_ITERATIONS) {
        return 0;   /* обмін припиняється до будь-яких обчислень */
    }
    return 1;
}
