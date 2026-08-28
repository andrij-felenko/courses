/* wq.c — черга задач у спільному сегменті на два незалежні процеси.
   збірка: cc -std=c11 -O2 -Wall -pthread -o wq wq.c -lrt             */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <pthread.h>
#include <signal.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <time.h>
#include <unistd.h>

#define SHM_NAME   "/wq-demo"
#define WQ_MAGIC   0x51574B31u   /* довільне, але СВОЄ: чужий сегмент не сплутаємо */
#define WQ_ABI     1u
#define WQ_SLOTS   64u           /* степінь двійки: індекс — маскою, без ділення */
#define WQ_PAYLOAD 96u

enum { OP_NONE = 0, OP_PUSH = 1, OP_POP = 2 };

struct slot {
    _Atomic uint64_t gen;         /* парне — запис цілий; непарне — його зараз пишуть */
    uint32_t len;
    uint8_t  data[WQ_PAYLOAD];
};

struct wq {
    uint32_t magic, abi;
    uint32_t hdr_size, slot_size; /* розкладка: сусід іншої розрядности не пройде */
    uint32_t slots;
    _Atomic uint32_t ready;       /* 0 → 1 після ПОВНОЇ ініціалізації */

    pthread_mutex_t lock;
    pthread_cond_t  not_empty, not_full;

    _Atomic uint64_t head, tail;  /* монотонні; індекс = значення & (slots − 1) */

    _Atomic uint32_t op;          /* намір, записаний ДО дотику до кільця */
    _Atomic uint64_t op_index;    /* номер запису, який укладають або забирають */
    _Atomic uint64_t op_gen;      /* яким було покоління слота ПЕРЕД зміною */

    struct slot ring[WQ_SLOTS];
};

_Static_assert(ATOMIC_LLONG_LOCK_FREE == 2,
    "64-бітні атоміки мусять бути неблокувальні: інакше компілятор підставить "
    "замок із таблиці власного процесу — сусідові він невидимий");

#define CK(x) do { if (!(x)) { fprintf(stderr, "%s:%d %s (%s)\n", __FILE__, __LINE__, \
                   #x, strerror(errno)); _exit(1); } } while (0)
