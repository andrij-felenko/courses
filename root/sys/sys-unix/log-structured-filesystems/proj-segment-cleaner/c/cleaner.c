/* cleaner.c — імітований лог-структурований том і його прибирач на C.
 * Збірка: cc -O2 -o cleaner cleaner.c
 */
#include <stdio.h>
#include <stdint.h>

#define SEG_BLOCKS   64      /* слотів у сегменті                       */
#define NSEGS       512      /* сегментів на томі                       */
#define FILE_BLOCKS  64      /* блоків у файлі                          */
#define WARMUP   100000L     /* перезаписів на розігрів                 */
#define MEASURE  200000L     /* перезаписів під вимірюванням            */

#ifndef LOW_FREE
#define LOW_FREE      8      /* нижче — вмикаємо прибирача              */
#endif
#ifndef RESERVE
#define RESERVE       4      /* сегменти, які бере лише прибирач        */
#endif

enum { GREEDY, COSTBEN };

typedef struct { int32_t ino, off; } Sum;     /* рядок підсумкового блока */

typedef struct {
    Sum      sum[SEG_BLOCKS];   /* чий кожен слот: файл і зсув у ньому   */
    int32_t  written;           /* скільки слотів уже зайнято            */
    int32_t  live;              /* кеш живих: таблиця стану сегментів    */
    uint64_t sealed;            /* час останнього запису в цей сегмент   */
    int32_t  is_free;
} Segment;

static Segment  seg[NSEGS];
static int32_t  inode[NSEGS][FILE_BLOCKS];    /* файл × зсув → адреса    */
static int32_t  nfiles, nhot, free_segs;
static int32_t  head[2];            /* 0 — голова програми, 1 — прибирача */
static uint64_t now_;               /* лічильник записаних блоків = час   */
static int      policy, sep_head;

static long long user_writes, clean_writes, clean_reads, victims, stalls;
static double    u_sum;
