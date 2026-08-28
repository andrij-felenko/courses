// comeasure.c — той самий алгоритм, але кожен доступ проходить крізь модель
// кеша, яка рахує промахи.  Збірка:  cc -O2 -o comeasure comeasure.c
#include <stdio.h>
#include <stdint.h>
#include <string.h>

#define N     128                  // матриці N×N
#define DPL   8                    // double на лінію: 64 Б / 8 Б = 8
#define NBLK  (3*N*N/DPL)          // усього блоків у спільному масиві
#define NL    64                   // ліній у кеші: 64 × 64 Б = 4 КБ

static double arena[3*N*N];        // A, B, C підряд — щоб адреса = індекс
#define A_OFF 0
#define B_OFF (N*N)
#define C_OFF (2*N*N)

static int32_t  where_[NBLK];      // блок → лінія, або -1
static int32_t  tagof[NL];         // лінія → блок, або -1
static uint64_t used[NL], clk, misses;

static void cache_reset(void)
{
    memset(where_, -1, sizeof where_);     // 0xFF у кожен байт = -1 у int32
    memset(tagof,  -1, sizeof tagof);
    memset(used,    0, sizeof used);
    clk = 0; misses = 0;
}

// єдина точка, крізь яку проходить УСЕ читання й писання
static void touch(size_t idx)
{
    int32_t blk = (int32_t)(idx / DPL);
    int32_t ln  = where_[blk];
    if (ln >= 0) { used[ln] = ++clk; return; }      // влучання
    misses++;
    int32_t v = 0;                                  // жертва — найдавніше вживана
    for (int32_t i = 1; i < NL; i++)                // (скан лише на промаху)
        if (used[i] < used[v]) v = i;
    if (tagof[v] >= 0) where_[tagof[v]] = -1;       // виселяємо стару
    tagof[v] = blk; where_[blk] = v; used[v] = ++clk;
}

static double rd(size_t i) { touch(i); return arena[i]; }
static void   wr(size_t i, double v) { touch(i); arena[i] = v; }
