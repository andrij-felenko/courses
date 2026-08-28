#include <stdio.h>
#include <stdlib.h>

/* У мові C винятків немає, але аналогічний витік виникає при
   використанні setjmp/longjmp для обробки помилок */
#include <setjmp.h>

static jmp_buf error_recovery;

void worker(void) {
    char *temp_buffer = (char *)malloc(8192);
    /* Імітація виявлення фатальної помилки протоколу */
    longjmp(error_recovery, 1);
    
    /* До цього рядка потік керування ніколи не доходить */
    free(temp_buffer);
}

int main(void) {
    if (setjmp(error_recovery) == 0) {
        worker();
    } else {
        printf("[C] Помилку перехоплено, але temp_buffer 8 KB витік назавжди!\n");
    }
    return 0;
}
