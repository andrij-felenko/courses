/* ofdprobe.c — хто з ким ділить опис відкритого файлу.
 *
 *   cc -Wall -O2 -o ofdprobe ofdprobe.c && ./ofdprobe
 *
 * Потрібен Linux: /proc/<pid>/fdinfo і kcmp() є лише тут.
 */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/stat.h>
#include <sys/syscall.h>
#include <sys/uio.h>
#include <sys/wait.h>
#include <unistd.h>
#if __has_include(<linux/kcmp.h>)
#include <linux/kcmp.h>
#else
#define KCMP_FILE 0
#endif

#define PROBE "probe.txt"

int main(void)
{
    setvbuf(stdout, NULL, _IOLBF, 0);
    puts("A пише «AAAAA», B пише «BBBBB»: 10 Б — опис один, 5 Б — описів два\n");

    puts("── спільний опис ──");
    case_dup();
    case_fork();
    case_scm();

    puts("\n── окремі описи ──");
    case_two_opens();

    puts("\n── писати вдвох без спільної позиції ──");
    case_append();
    case_pwrite();

    puts("\n── пастка Linux ──");
    case_pwrite_append();

    unlink(PROBE);
    return 0;
}
