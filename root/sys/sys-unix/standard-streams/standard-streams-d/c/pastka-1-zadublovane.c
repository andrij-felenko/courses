#include <stdio.h>
#include <unistd.h>

int main(void) {
    printf("Початок обчислень..."); // Символу \n немає!
    
    fork();

    printf(" Завершено.\n");
    return 0;
}
