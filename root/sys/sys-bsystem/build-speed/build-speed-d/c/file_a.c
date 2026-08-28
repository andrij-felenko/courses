/* Проблема: static змінні та макроси з однаковими іменами у двох .c файлах */

/* file_a.c */
#define BUFFER_SIZE 1024
static int internal_counter = 0;

void process_a(void) {
    internal_counter += BUFFER_SIZE;
}

/* file_b.c */
#define BUFFER_SIZE 4096   /* Помилка: перевизначення макросу під час Unity збірки */
static int internal_counter = 0; /* Помилка: колізія імені з file_a.c */

void process_b(void) {
    internal_counter += BUFFER_SIZE;
}

/* Рішення для C: скасування макросів (#undef) та унікальні імена для static символів */
/* file_a.c (виправлено) */
#define BUFFER_SIZE_A 1024
static int counter_a = 0;

void process_a(void) {
    counter_a += BUFFER_SIZE_A;
}
#undef BUFFER_SIZE_A
