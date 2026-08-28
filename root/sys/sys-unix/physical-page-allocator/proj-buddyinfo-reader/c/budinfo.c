/* budinfo.c — форма вільної пам'яті: зони, найбільший блок, avail(k).
   Збірка: cc -O2 -std=gnu11 -o budinfo budinfo.c
   Запуск: ./budinfo [--zone НАЗВА] [--need БАЙТІВ] [--hidden]

   без ключів  один підсумковий рядок на зону
   --zone      лише ця зона, але з повною таблицею за порядками
   --need      відповісти, чи є суцільний шматок такого розміру і в якій зоні
   --hidden    додати кадри з посторінкових запасів ядер (з /proc/zoneinfo)  */
#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAX_ORDERS 32
#define MAX_ZONES  64
#define BUFSZ      (1 << 17)      /* 128 КіБ — стане на будь-яку кількість вузлів */

static long pgsz;                 /* байтів у кадрі ЦІЄЇ машини */

struct zonerow {
    int  node;
    char name[16];
    int  norders;                 /* скільки стовпців дало ядро, а не скільки ми чекали */
    unsigned long nr_free[MAX_ORDERS];
    unsigned long avail[MAX_ORDERS];
    unsigned long free_pages;
    int  top;                     /* найбільший порядок із блоками; −1 — жодного */
};

/* Один read(): текст складається в мить читання, і дрібними порціями
   ви змішуєте кілька різних станів машини в одному «знімку». */
static ssize_t slurp(const char *path, char *buf, size_t cap)
{
    int fd = open(path, O_RDONLY | O_CLOEXEC);
    if (fd < 0) return -1;
    ssize_t n = read(fd, buf, cap - 1);
    close(fd);
    if (n < 0) return -1;
    buf[n] = '\0';
    return n;
}
