// ftlsim.c — навчальний посторінковий FTL: карта, запис не на місце,
// жадібне збирання сміття, лічильник підсилення запису.
// Збірка:  cc -O2 -o ftlsim ftlsim.c
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>

#define PPB    64                  // сторінок у блоці
#define NBLK   256                 // блоків у кристалі
#define NPHYS  (PPB * NBLK)        // 16384 фізичні сторінки
#define GC_LOW 2                   // поріг пулу: нижче — будимо збирача
#define NONE   0xFFFFFFFFu

enum { P_FREE, P_VALID, P_INVALID };   // стан фізичної сторінки

static uint8_t  pstate[NPHYS];         // стан кожної фізичної сторінки
static uint32_t powner[NPHYS];         // OOB: чий LPN тут лежить
static uint16_t invalid_cnt[NBLK];     // недійсних сторінок у блоці
static uint32_t erase_cnt[NBLK];       // скільки разів блок стирали

static uint32_t map[NPHYS];            // карта: map[LPN] = PPN
static uint32_t nlog;                  // скільки LPN бачить хост

static uint32_t freelist[NBLK];        // пул стертих блоків (стек)
static uint32_t freetop;               // скільки їх у пулі
static uint32_t wblk, wpage;           // фронт запису: блок і зсув у ньому

static uint64_t host_w, flash_w, erases, gc_copies;   // лічильники

static void gc_run(void);              // наперед: ftl_write кличе збирача
