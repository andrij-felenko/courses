#include <stdio.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void)
{
    printf("рахунок: %d\n", 42);
    if (fork() == 0)
        return 0;            /* дитина завершується звичайно — і зливає СВОЮ копію буфера */
    wait(NULL);
    return 0;                /* батько зливає свою */
}
