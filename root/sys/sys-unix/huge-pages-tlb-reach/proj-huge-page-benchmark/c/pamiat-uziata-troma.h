/* tlbwalk.c — ціна перекладу адрес на трьох видах сторінок.
   Збірка:  cc -O2 -std=gnu11 -o tlbwalk tlbwalk.c
   Запуск:  ./tlbwalk all 16 20        # режим · ГіБ · мільйонів кроків     */
#define _GNU_SOURCE
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/mman.h>

#define PAGE  4096UL
#define HUGE  (2UL << 20)
#define LINE  64UL

#ifndef MAP_HUGE_SHIFT
#define MAP_HUGE_SHIFT 26
#endif
#ifndef MADV_COLLAPSE
#define MADV_COLLAPSE 25                 /* з'явилося в Linux 6.1 */
#endif
