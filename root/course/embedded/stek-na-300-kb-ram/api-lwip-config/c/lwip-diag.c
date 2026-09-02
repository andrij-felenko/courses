#include "lwip-diag.h"

#include <stdio.h>
#include <string.h>

#include "lwip/memp.h"

#if !NO_SYS
#include "lwip/tcpip.h"
#endif

/* lwip_stats оновлює потік tcpip_thread. Читати його з задачі застосунку
 * без блокування ядра — гарантований рваний знімок: половина полів зі
 * старого стану, половина з нового. */
#if !NO_SYS && LWIP_TCPIP_CORE_LOCKING
#define DIAG_LOCK()   LOCK_TCPIP_CORE()
#define DIAG_UNLOCK() UNLOCK_TCPIP_CORE()
#else
#define DIAG_LOCK()   do { } while (0)
#define DIAG_UNLOCK() do { } while (0)
#endif

#if LWIP_STATS && MEMP_STATS && MEM_STATS

static void diag_sample(lwip_diag_pool_t *slot,
                        lwip_diag_pool_id_t id,
                        const char *name,
                        memp_t pool)
{
  const struct stats_mem *s = lwip_stats.memp[pool];

  slot->id = id;
  slot->name = name;
  slot->avail = (u32_t)s->avail;
  slot->used = (u32_t)s->used;
  slot->peak = (u32_t)s->max;
  slot->failures = (u32_t)s->err;
}

static const lwip_diag_pool_t *diag_find(const lwip_diag_report_t *r,
                                         lwip_diag_pool_id_t id)
{
  u8_t i;

  for (i = 0; i < r->pool_count; i++) {
    if (r->pools[i].id == id) {
      return &r->pools[i];
    }
  }
  return NULL; /* пул вимкнений у lwipopts.h — це не помилка */
}

static int diag_at_ceiling(const lwip_diag_pool_t *p)
{
  return (p != NULL) && (p->failures > 0u || (p->avail > 0u && p->peak >= p->avail));
}

/* Порядок питань навмисний: спершу те, що вже втратило дані, потім те,
 * що лише вперлося в стелю. Перша відповідь і є вузьке місце. */
static lwip_diag_verdict_t diag_classify(const lwip_diag_report_t *r)
{
  const lwip_diag_pool_t *rx = diag_find(r, LWIP_DIAG_POOL_PBUF_POOL);

  if (rx != NULL && rx->failures > 0u) {
    return LWIP_DIAG_RX_POOL_STARVED;
  }
  if (r->heap.failures > 0u) {
    return LWIP_DIAG_HEAP_EXHAUSTED;
  }
  if (diag_at_ceiling(diag_find(r, LWIP_DIAG_POOL_TCP_SEG))) {
    return LWIP_DIAG_SEGS_EXHAUSTED;
  }
  if (diag_at_ceiling(diag_find(r, LWIP_DIAG_POOL_TCP_PCB))) {
    return LWIP_DIAG_SOCKETS_EXHAUSTED;
  }
  return LWIP_DIAG_HEALTHY;
}

#endif /* LWIP_STATS && MEMP_STATS && MEM_STATS */

int lwip_diag_collect(lwip_diag_report_t *report)
{
  if (report == NULL) {
    return -1;
  }
  memset(report, 0, sizeof(*report));

#if LWIP_STATS && MEMP_STATS && MEM_STATS
  {
    u8_t n = 0;

    DIAG_LOCK();
    diag_sample(&report->pools[n++], LWIP_DIAG_POOL_PBUF_POOL, "PBUF_POOL", MEMP_PBUF_POOL);
    diag_sample(&report->pools[n++], LWIP_DIAG_POOL_PBUF, "PBUF_REF", MEMP_PBUF);
#if LWIP_TCP
    diag_sample(&report->pools[n++], LWIP_DIAG_POOL_TCP_PCB, "TCP_PCB", MEMP_TCP_PCB);
    diag_sample(&report->pools[n++], LWIP_DIAG_POOL_TCP_LISTEN, "TCP_LISTEN", MEMP_TCP_PCB_LISTEN);
    diag_sample(&report->pools[n++], LWIP_DIAG_POOL_TCP_SEG, "TCP_SEG", MEMP_TCP_SEG);
#endif
#if LWIP_UDP
    diag_sample(&report->pools[n++], LWIP_DIAG_POOL_UDP_PCB, "UDP_PCB", MEMP_UDP_PCB);
#endif
#if LWIP_NETCONN
    diag_sample(&report->pools[n++], LWIP_DIAG_POOL_NETCONN, "NETCONN", MEMP_NETCONN);
#endif

    report->heap.id = LWIP_DIAG_POOL_PBUF_POOL; /* поле не використовується для купи */
    report->heap.name = "HEAP(mem)";
    report->heap.avail = (u32_t)lwip_stats.mem.avail;
    report->heap.used = (u32_t)lwip_stats.mem.used;
    report->heap.peak = (u32_t)lwip_stats.mem.max;
    report->heap.failures = (u32_t)lwip_stats.mem.err;
    DIAG_UNLOCK();

    report->pool_count = n;
    report->verdict = diag_classify(report);
    return 0;
  }
#else
  /* Статистику вимкнено в lwipopts.h: рахувати нема чого. */
  return -1;
#endif
}

const char *lwip_diag_verdict_str(lwip_diag_verdict_t verdict)
{
  switch (verdict) {
    case LWIP_DIAG_HEALTHY:
      return "запас є";
    case LWIP_DIAG_RX_POOL_STARVED:
      return "вичерпано PBUF_POOL: збільшити PBUF_POOL_SIZE або пришвидшити обробку";
    case LWIP_DIAG_HEAP_EXHAUSTED:
      return "вичерпано купу MEM_SIZE: збільшити MEM_SIZE або зменшити TCP_SND_BUF";
    case LWIP_DIAG_SEGS_EXHAUSTED:
      return "вичерпано TCP_SEG: підняти MEMP_NUM_TCP_SEG під TCP_SND_QUEUELEN";
    case LWIP_DIAG_SOCKETS_EXHAUSTED:
      return "вичерпано TCP_PCB: підняти MEMP_NUM_TCP_PCB або закривати з'єднання";
    default:
      return "невідомий стан";
  }
}

static unsigned diag_percent(u32_t part, u32_t whole)
{
  if (whole == 0u) {
    return 0u;
  }
  return (unsigned)((part * 100u) / whole);
}

void lwip_diag_print(const lwip_diag_report_t *report)
{
  u8_t i;

  if (report == NULL) {
    return;
  }

  printf("lwIP: пам'ять і пули\n");
  printf("%-12s %6s %6s %6s %6s %8s\n", "пул", "усього", "зайн", "пік", "пік%", "відмов");

  for (i = 0; i < report->pool_count; i++) {
    const lwip_diag_pool_t *p = &report->pools[i];

    printf("%-12s %6lu %6lu %6lu %5u%% %8lu%s\n",
           p->name,
           (unsigned long)p->avail,
           (unsigned long)p->used,
           (unsigned long)p->peak,
           diag_percent(p->peak, p->avail),
           (unsigned long)p->failures,
           (p->failures > 0u) ? "  <-- відмови" : "");
  }

  printf("%-12s %6lu %6lu %6lu %5u%% %8lu   (байтів)\n",
         report->heap.name,
         (unsigned long)report->heap.avail,
         (unsigned long)report->heap.used,
         (unsigned long)report->heap.peak,
         diag_percent(report->heap.peak, report->heap.avail),
         (unsigned long)report->heap.failures);

  printf("присуд: %s\n", lwip_diag_verdict_str(report->verdict));
}

void lwip_diag_dump(void)
{
  lwip_diag_report_t report;

  if (lwip_diag_collect(&report) != 0) {
    printf("lwIP: статистику вимкнено (LWIP_STATS/MEMP_STATS/MEM_STATS у lwipopts.h)\n");
    return;
  }

  lwip_diag_print(&report);

#if LWIP_STATS_DISPLAY
  stats_display(); /* повна рідна карта: протоколи, лічильники помилок, netif */
#endif
}
