/* layout.c — що ця збірка думає про ширину чисел і розкладку структур */
#include <stdio.h>
#include <stddef.h>
#include <sys/types.h>
#include <time.h>

struct sample {
    int       code;    /* 4 байти в обох домовленостях */
    long long stamp;   /* 8 байтів в обох домовленостях */
};

int main(void)
{
    printf("ширини        : int=%zu long=%zu покажчик=%zu\n",
           sizeof(int), sizeof(long), sizeof(void *));
    printf("типи межі     : size_t=%zu off_t=%zu time_t=%zu\n",
           sizeof(size_t), sizeof(off_t), sizeof(time_t));
    printf("struct sample : розмір=%zu зсув(code)=%zu зсув(stamp)=%zu\n",
           sizeof(struct sample),
           offsetof(struct sample, code),
           offsetof(struct sample, stamp));
    return 0;
}
