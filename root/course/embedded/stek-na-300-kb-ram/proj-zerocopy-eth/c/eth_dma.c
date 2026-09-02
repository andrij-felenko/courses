#include "eth_dma.h"

#include "ethernetif.h"
#include "stm32f7xx.h"

/* --- Біти дескрипторів Ethernet MAC (RDES/TDES) --- */

#define RDES0_OWN        0x80000000U  /* дескриптор належить DMA */
#define RDES0_FL_MASK    0x3FFF0000U  /* довжина кадру, разом із 4 байтами FCS */
#define RDES0_FL_SHIFT   16U
#define RDES0_ES         0x00008000U  /* Error Summary: кадр битий */
#define RDES0_FS         0x00000200U  /* перший сегмент */
#define RDES0_LS         0x00000100U  /* останній сегмент */

#define RDES1_RCH        0x00004000U  /* друга адреса — вказівник на наступний дескриптор */
#define RDES1_RER        0x00008000U  /* кінець кільця */
#define RDES1_RBS1_MASK  0x00001FFFU  /* розмір буфера прийому, біти 12..0 */

#define TDES0_OWN        0x80000000U
#define TDES0_IC         0x40000000U  /* переривання по завершенні кадру */
#define TDES0_LS         0x20000000U
#define TDES0_FS         0x10000000U
#define TDES0_TCH        0x00100000U  /* режим ланцюжка */
#define TDES0_TER        0x00200000U  /* кінець кільця */
#define TDES1_TBS1_MASK  0x00001FFFU

/* Дескриптор — чотири 32-бітні слова, які пише апаратура, тому поля volatile.
   aligned(32) заразом робить sizeof рівним 32: один дескриптор = рівно одна
   кеш-лінія, і clean/invalidate над ним ніколи не зачепить сусіда. */
typedef struct {
    volatile uint32_t status;   /* RDES0 / TDES0 */
    volatile uint32_t control;  /* RDES1 / TDES1 */
    volatile uint32_t buffer;   /* RDES2 / TDES2 — адреса корисних даних */
    volatile uint32_t next;     /* RDES3 / TDES3 — наступний дескриптор */
} __attribute__((aligned(ETH_CACHE_LINE))) eth_desc_t;

static eth_desc_t rx_ring[ETH_RX_DESC_COUNT] __attribute__((aligned(ETH_CACHE_LINE)));
static eth_desc_t tx_ring[ETH_TX_DESC_COUNT] __attribute__((aligned(ETH_CACHE_LINE)));

/* Прив'язка «дескриптор → pbuf». Саме вона й робить драйвер zero-copy:
   апаратура пише прямо в payload буфера зі стека, а не в чужий масив. */
static struct pbuf *rx_pbufs[ETH_RX_DESC_COUNT];
static struct pbuf *tx_pbufs[ETH_TX_DESC_COUNT];

static uint32_t rx_head;  /* наступний дескриптор, який дивиться процесор */
static uint32_t tx_head;  /* наступний вільний дескриптор передачі */

/* --- Узгодження D-Cache (CMSIS) --- */

/* Обидві операції працюють кеш-лініями, тому адресу округлюємо ВНИЗ, а розмір
   доточуємо на той самий зсув. Інакше апаратура мовчки обробить не ту лінію. */
static void cache_invalidate(const void *addr, uint32_t size)
{
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
    uint32_t start = (uint32_t)addr & ~((uint32_t)ETH_CACHE_LINE - 1U);
    uint32_t bytes = size + ((uint32_t)addr - start);
    SCB_InvalidateDCache_by_Addr((uint32_t *)start, (int32_t)bytes);
#else
    (void)addr; (void)size;
    __DSB();
#endif
}

static void cache_clean(const void *addr, uint32_t size)
{
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
    uint32_t start = (uint32_t)addr & ~((uint32_t)ETH_CACHE_LINE - 1U);
    uint32_t bytes = size + ((uint32_t)addr - start);
    SCB_CleanDCache_by_Addr((uint32_t *)start, (int32_t)bytes);
#else
    (void)addr; (void)size;
    __DSB();
#endif
}

/* --- Буфери прийому --- */

/* Один буфер під дескриптор. Перевіряємо рівно те, що ламає zero-copy
   на живому залізі, і краще впасти тут, ніж псувати чужу пам'ять потім. */
static struct pbuf *rx_buffer_alloc(void)
{
    struct pbuf *p = pbuf_alloc(PBUF_RAW, ETH_RX_BUF_SIZE, PBUF_POOL);
    if (p == NULL) {
        return NULL; /* пул вичерпано */
    }
    if (p->next != NULL || p->len < ETH_RX_BUF_SIZE) {
        /* PBUF_POOL_BUFSIZE менший за кадр — пул віддав ланцюжок. */
        pbuf_free(p);
        return NULL;
    }
    if (((uintptr_t)p->payload & (ETH_CACHE_LINE - 1U)) != 0U) {
        /* MEM_ALIGNMENT у lwipopts.h менший за кеш-лінію: інвалідація зачепила б
           сусідні дані в тій самій лінії — те саме паразитне перезаписування. */
        pbuf_free(p);
        return NULL;
    }
    return p;
}

static void rx_buffers_release(void)
{
    for (uint32_t i = 0; i < ETH_RX_DESC_COUNT; i++) {
        if (rx_pbufs[i] != NULL) {
            pbuf_free(rx_pbufs[i]);
            rx_pbufs[i] = NULL;
        }
    }
}

/* --- Ініціалізація --- */

bool eth_dma_init(void)
{
    for (uint32_t i = 0; i < ETH_RX_DESC_COUNT; i++) {
        struct pbuf *p = rx_buffer_alloc();
        if (p == NULL) {
            rx_buffers_release();
            return false;
        }
        rx_pbufs[i] = p;

        rx_ring[i].buffer  = (uint32_t)p->payload;
        rx_ring[i].control = RDES1_RCH | (ETH_RX_BUF_SIZE & RDES1_RBS1_MASK);
        rx_ring[i].next    = (uint32_t)&rx_ring[(i + 1U) % ETH_RX_DESC_COUNT];
        if (i == ETH_RX_DESC_COUNT - 1U) {
            /* У режимі ланцюжка DMA і так іде за RDES3; біт лишаємо як явну
               позначку кінця кільця для того, хто читатиме дамп дескрипторів. */
            rx_ring[i].control |= RDES1_RER;
        }
        /* Буфер віддаємо апаратурі — усе, що процесор про нього «пам'ятає»
           в кеші, треба викинути, інакше стек прочитає стару копію. */
        cache_invalidate(p->payload, ETH_RX_BUF_SIZE);
        rx_ring[i].status = RDES0_OWN;
    }

    for (uint32_t i = 0; i < ETH_TX_DESC_COUNT; i++) {
        tx_pbufs[i]        = NULL;
        tx_ring[i].buffer  = 0U;
        tx_ring[i].control = 0U;
        tx_ring[i].next    = (uint32_t)&tx_ring[(i + 1U) % ETH_TX_DESC_COUNT];
        tx_ring[i].status  = TDES0_TCH;
        if (i == ETH_TX_DESC_COUNT - 1U) {
            tx_ring[i].status |= TDES0_TER;
        }
    }

    /* Дескриптори щойно писав процесор — виштовхуємо їх з кеша в SRAM,
       бо читати їх буде DMA повз кеш. */
    cache_clean(rx_ring, sizeof(rx_ring));
    cache_clean(tx_ring, sizeof(tx_ring));

    rx_head = 0;
    tx_head = 0;

    ETH->DMARDLAR = (uint32_t)rx_ring;
    ETH->DMATDLAR = (uint32_t)tx_ring;

    ETH->DMAIER |= ETH_DMAIER_NISE | ETH_DMAIER_RIE | ETH_DMAIER_TIE |
                   ETH_DMAIER_AISE | ETH_DMAIER_RBUIE;

    ETH->MACCR |= ETH_MACCR_TE | ETH_MACCR_RE;

    ETH->DMAOMR |= ETH_DMAOMR_FTF;  /* скидаємо FIFO передачі; біт самоочисний */
    for (uint32_t spin = 0; spin < 100000U; spin++) {
        if ((ETH->DMAOMR & ETH_DMAOMR_FTF) == 0U) {
            break;
        }
    }
    ETH->DMAOMR |= ETH_DMAOMR_ST | ETH_DMAOMR_SR;

    NVIC_SetPriority(ETH_IRQn, 5);  /* нижче за поріг RTOS-безпечних переривань */
    NVIC_EnableIRQ(ETH_IRQn);
    return true;
}

/* --- Прийом --- */

/* Повертає дескриптор апаратурі, не чіпаючи прив'язаного буфера. Саме це
   рятує кільце, коли пул порожній: адреса в RDES2 лишається справжньою. */
static void rx_descriptor_return(eth_desc_t *d)
{
    d->status = RDES0_OWN;
    cache_clean(d, sizeof(*d));
}

struct pbuf *eth_dma_rx_receive(void)
{
    for (uint32_t scanned = 0; scanned < ETH_RX_DESC_COUNT; scanned++) {
        eth_desc_t *d = &rx_ring[rx_head];

        /* Статус писав DMA — власна копія в кеші тут завжди застаріла. */
        cache_invalidate(d, sizeof(*d));
        if ((d->status & RDES0_OWN) != 0U) {
            return NULL; /* кільце дійшло до дескриптора, який ще в роботі DMA */
        }

        const uint32_t status = d->status;
        const uint32_t frame_len = (status & RDES0_FL_MASK) >> RDES0_FL_SHIFT;
        struct pbuf *received = rx_pbufs[rx_head];
        struct pbuf *out = NULL;

        const bool single = (status & (RDES0_FS | RDES0_LS)) == (RDES0_FS | RDES0_LS);
        const bool sane = single && ((status & RDES0_ES) == 0U) &&
                          (frame_len > 4U) && (frame_len <= ETH_RX_BUF_SIZE);

        if (sane) {
            /* Спершу дістаємо заміну — і лише якщо вона є, віддаємо кадр стеку. */
            struct pbuf *fresh = rx_buffer_alloc();
            if (fresh != NULL) {
                /* FL рахує ще й 4 байти FCS, які стеку не потрібні. */
                const uint16_t len = (uint16_t)(frame_len - 4U);

                cache_invalidate(received->payload, len);
                received->len = len;
                received->tot_len = len;

                rx_pbufs[rx_head] = fresh;
                d->buffer = (uint32_t)fresh->payload;
                cache_invalidate(fresh->payload, ETH_RX_BUF_SIZE);
                out = received;
            }
            /* Заміни немає — кадр просто гине, буфер лишається в дескрипторі. */
        }

        rx_descriptor_return(d);
        rx_head = (rx_head + 1U) % ETH_RX_DESC_COUNT;

        /* Поки кільце стояло порожнім, DMA міг заснути на Receive Buffer
           Unavailable. Прапорець знімається записом одиниці, будить — DMARPDR. */
        if ((ETH->DMASR & ETH_DMASR_RBUS) != 0U) {
            ETH->DMASR = ETH_DMASR_RBUS;
            ETH->DMARPDR = 0U;
        }

        if (out != NULL) {
            return out;
        }
        /* Кадр відкинуто — не виходимо, а дивимось наступний дескриптор. */
    }
    return NULL;
}

/* --- Передача --- */

void eth_dma_tx_reclaim(void)
{
    for (uint32_t i = 0; i < ETH_TX_DESC_COUNT; i++) {
        if (tx_pbufs[i] == NULL) {
            continue;
        }
        cache_invalidate(&tx_ring[i], sizeof(tx_ring[i]));
        if ((tx_ring[i].status & TDES0_OWN) != 0U) {
            continue; /* DMA ще читає цей буфер */
        }
        /* Контекст задачі, не переривання: pbuf_free тут має право
           повертати пам'ять у пул і чіпати блокування стека. */
        pbuf_free(tx_pbufs[i]);
        tx_pbufs[i] = NULL;
    }
}

bool eth_dma_tx_send(struct pbuf *p)
{
    if (p == NULL || p->tot_len == 0U) {
        return false;
    }

    eth_dma_tx_reclaim();

    /* Ланцюжок pbuf розкладаємо по дескрипторах один в один: копіювати
       ланки в суцільний буфер означало б викинути весь zero-copy. */
    uint32_t need = 0;
    for (struct pbuf *q = p; q != NULL; q = q->next) {
        if (q->len == 0U) {
            continue;
        }
        if (q->len > TDES1_TBS1_MASK) {
            return false; /* ланка довша за те, що вміщує TBS1 */
        }
        need++;
    }
    if (need == 0U || need > ETH_TX_DESC_COUNT) {
        return false;
    }

    for (uint32_t k = 0; k < need; k++) {
        eth_desc_t *d = &tx_ring[(tx_head + k) % ETH_TX_DESC_COUNT];
        cache_invalidate(d, sizeof(*d));
        if ((d->status & TDES0_OWN) != 0U) {
            return false; /* кільце передачі заповнене */
        }
    }

    const uint32_t first = tx_head;
    uint32_t k = 0;
    for (struct pbuf *q = p; q != NULL; q = q->next) {
        if (q->len == 0U) {
            continue;
        }
        eth_desc_t *d = &tx_ring[(first + k) % ETH_TX_DESC_COUNT];

        /* Пакет процесор щойно склав у своєму кеші — до старту DMA
           байти мусять опинитися у фізичній SRAM. */
        cache_clean(q->payload, q->len);

        d->buffer  = (uint32_t)q->payload;
        d->control = q->len & TDES1_TBS1_MASK;

        uint32_t st = TDES0_TCH;
        if ((first + k) % ETH_TX_DESC_COUNT == ETH_TX_DESC_COUNT - 1U) {
            st |= TDES0_TER;
        }
        if (k == 0U) {
            st |= TDES0_FS;
        }
        if (k == need - 1U) {
            st |= TDES0_LS | TDES0_IC;
        }
        d->status = st;  /* поки БЕЗ OWN */
        k++;
    }

    /* Одне посилання на весь кадр, і висить воно на ОСТАННЬОМУ дескрипторі:
       поки DMA не дійшов до кінця, звільняти ланцюжок не можна. */
    pbuf_ref(p);
    tx_pbufs[(first + need - 1U) % ETH_TX_DESC_COUNT] = p;

    /* Володіння віддаємо задом наперед: якби перший дескриптор дістав OWN
       раніше за останній, DMA почав би передавати недобудований кадр. */
    for (uint32_t back = need; back-- > 0U;) {
        eth_desc_t *d = &tx_ring[(first + back) % ETH_TX_DESC_COUNT];
        d->status |= TDES0_OWN;
        cache_clean(d, sizeof(*d));
    }
    __DSB();

    tx_head = (first + need) % ETH_TX_DESC_COUNT;

    if ((ETH->DMASR & ETH_DMASR_TBUS) != 0U) {
        ETH->DMASR = ETH_DMASR_TBUS;
    }
    ETH->DMATPDR = 0U;  /* Transmit Poll Demand: «подивись у кільце ще раз» */
    return true;
}

/* --- Переривання --- */

void ETH_IRQHandler(void)
{
    const uint32_t sr = ETH->DMASR;

    if ((sr & ETH_DMASR_RS) != 0U) {
        ETH->DMASR = ETH_DMASR_RS;
        /* Тільки сигнал задачі. Ні pbuf_alloc, ні pbuf_free тут не можна:
           пул захищений блокуванням стека, а не забороною переривань. */
        ethernetif_notify_from_isr();
    }

    if ((sr & ETH_DMASR_TS) != 0U) {
        ETH->DMASR = ETH_DMASR_TS;
        /* Буфери передачі звільнить eth_dma_tx_reclaim() у задачі. */
    }

    if ((sr & ETH_DMASR_RBUS) != 0U) {
        /* Пул був порожній, DMA спинився. Знімаємо прапорець, штовхаємо
           приймач і будимо задачу — вона розгребе кільце. */
        ETH->DMASR = ETH_DMASR_RBUS;
        ETH->DMARPDR = 0U;
        ethernetif_notify_from_isr();
    }

    ETH->DMASR = sr & (ETH_DMASR_NIS | ETH_DMASR_AIS);
}
