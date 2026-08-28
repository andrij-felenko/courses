#include <stdint.h>
#include <string.h>
#include <stdio.h>

#define PAGE_SZ        512        /* байтів у сторінці */
#define PAGES_PER_BLK  4          /* сторінок у блоці  */
#define NUM_BLOCKS     8          /* блоків у «чипі»   */
#define NUM_LBA        16         /* логічних секторів (< 32 фіз. сторінок → надлишковий резерв) */

enum { PAGE_FREE, PAGE_VALID, PAGE_STALE };      /* стан фізичної сторінки */
typedef struct { int blk, page; } phys_t;        /* фізичне місце: блок + сторінка */

static uint8_t data  [NUM_BLOCKS][PAGES_PER_BLK][PAGE_SZ]; /* власне NAND          */
static uint8_t pstate[NUM_BLOCKS][PAGES_PER_BLK];          /* FREE / VALID / STALE  */
static int     powner[NUM_BLOCKS][PAGES_PER_BLK];          /* чий LBA тут лежить (службове поле) */
static phys_t  map[NUM_LBA];                               /* таблиця: LBA → фізична сторінка */
static int     wblk, wpage;                                /* фронт запису: куди кладемо наступне */

static void ftl_init(void) {
    for (int b = 0; b < NUM_BLOCKS; b++)
        for (int p = 0; p < PAGES_PER_BLK; p++) { pstate[b][p] = PAGE_FREE; powner[b][p] = -1; }
    for (int l = 0; l < NUM_LBA; l++) { map[l].blk = -1; map[l].page = -1; }  /* -1 = ще не писали */
    wblk = 0; wpage = 0;
}

static void nand_erase(int b) {                  /* стерти цілий блок начисто */
    for (int p = 0; p < PAGES_PER_BLK; p++) { pstate[b][p] = PAGE_FREE; powner[b][p] = -1; }
}

static int find_free_block(void) {               /* перший повністю стертий блок */
    for (int b = 0; b < NUM_BLOCKS; b++) {
        int all_free = 1;
        for (int p = 0; p < PAGES_PER_BLK; p++)
            if (pstate[b][p] != PAGE_FREE) { all_free = 0; break; }
        if (all_free) return b;
    }
    return -1;
}

static int free_pages(void) {                    /* скільки стертих сторінок лишилось усього */
    int n = 0;
    for (int b = 0; b < NUM_BLOCKS; b++)
        for (int p = 0; p < PAGES_PER_BLK; p++)
            if (pstate[b][p] == PAGE_FREE) n++;
    return n;
}

static phys_t alloc_page(void) {                 /* наступна вільна СТЕРТА сторінка */
    if (wpage >= PAGES_PER_BLK) { wblk = find_free_block(); wpage = 0; }  /* блок повний — беремо свіжий */
    phys_t pp = { wblk, wpage };
    wpage++;
    return pp;
}

static int pick_victim(void) {                   /* блок із найбільшою часткою застарілих */
    int best = -1, best_stale = 0;               /* жертва мусить мати хоч одну застарілу — інакше прибирати нічого */
    for (int b = 0; b < NUM_BLOCKS; b++) {
        if (b == wblk) continue;                 /* фронт запису не чіпаємо */
        int stale = 0, used = 0;
        for (int p = 0; p < PAGES_PER_BLK; p++) {
            if (pstate[b][p] == PAGE_STALE) stale++;
            if (pstate[b][p] != PAGE_FREE)  used++;
        }
        if (used && stale > best_stale) { best_stale = stale; best = b; }
    }
    return best;
}

static void garbage_collect(void) {
    int v = pick_victim();
    if (v < 0) return;                           /* нема що прибирати */
    for (int p = 0; p < PAGES_PER_BLK; p++) {    /* чинні сторінки жертви — в інше місце */
        if (pstate[v][p] != PAGE_VALID) continue;
        int lba = powner[v][p];
        phys_t np = alloc_page();                /* завжди у стерту сторінку */
        memcpy(data[np.blk][np.page], data[v][p], PAGE_SZ);
        pstate[np.blk][np.page] = PAGE_VALID;
        powner[np.blk][np.page] = lba;
        map[lba] = np;                           /* таблиця → на копію (негайно!) */
    }
    nand_erase(v);                               /* спорожнілу жертву — назад у запас */
}

void ftl_read(int lba, uint8_t *buf) {
    phys_t pp = map[lba];                         /* один погляд у таблицю */
    if (pp.blk < 0) { memset(buf, 0, PAGE_SZ); return; }   /* сюди ще не писали */
    memcpy(buf, data[pp.blk][pp.page], PAGE_SZ);
}

void ftl_write(int lba, const uint8_t *buf) {
    if (free_pages() < 2 * PAGES_PER_BLK)         /* запас тане — прибрати завчасно */
        garbage_collect();
    phys_t pp = alloc_page();                     /* нове місце → запис «не на місці» */
    memcpy(data[pp.blk][pp.page], buf, PAGE_SZ);
    pstate[pp.blk][pp.page] = PAGE_VALID;
    powner[pp.blk][pp.page] = lba;
    phys_t old = map[lba];
    if (old.blk >= 0)                             /* була попередня версія — це сміття */
        pstate[old.blk][old.page] = PAGE_STALE;
    map[lba] = pp;                                /* перевести LBA на нове місце */
}

int main(void) {
    ftl_init();
    uint8_t buf[PAGE_SZ];
    for (int round = 0; round < 12; round++)      /* переписуємо кілька секторів багато разів → */
        for (int lba = 0; lba < 6; lba++) {       /* плодимо застарілі сторінки й провокуємо GC   */
            memset(buf, (uint8_t)(round * 10 + lba), PAGE_SZ);
            ftl_write(lba, buf);
        }
    for (int lba = 0; lba < 6; lba++) {           /* читаємо назад — маємо ОСТАННЮ версію кожного */
        ftl_read(lba, buf);
        printf("LBA %2d -> 0x%02X, лежить у блоці %d\n", lba, buf[0], map[lba].blk);
    }
    printf("вільних сторінок наприкінці: %d\n", free_pages());
    return 0;
}
