#include "lwip/opt.h"
#include "lwip/pbuf.h"
#include "lwip/netif.h"
#include <stdint.h>
#include <stdbool.h>

#define ETH_RXBUFNB               4
#define ETH_TXBUFNB               4
#define ETH_RX_BUF_SIZE           1536
#define DCACHE_LINE_SIZE          32

/* Апаратні біти дескрипторів DMA */
#define ETH_DMARXDESC_OWN         0x80000000U
#define ETH_DMATXDESC_OWN         0x80000000U
#define ETH_DMATXDESC_FS          0x20000000U
#define ETH_DMATXDESC_LS          0x10000000U
#define ETH_DMATXDESC_IC          0x40000000U
#define ETH_DMARXDESC_RER         0x00008000U
#define ETH_DMATXDESC_TER         0x00200000U

typedef struct {
    volatile uint32_t Status;
    volatile uint32_t ControlBufferSize;
    volatile uint32_t Buffer1Addr;
    volatile uint32_t Buffer2NextDescAddr;
} __attribute__((aligned(32))) ETH_DMADescTypeDef;

/* Кільця дескрипторів та масиви прив'язки pbuf */
static ETH_DMADescTypeDef DMARxDscrTab[ETH_RXBUFNB] __attribute__((aligned(32)));
static ETH_DMADescTypeDef DMATxDscrTab[ETH_TXBUFNB] __attribute__((aligned(32)));
static struct pbuf *rx_pbufs[ETH_RXBUFNB];
static struct pbuf *tx_pbufs[ETH_TXBUFNB];

static uint32_t rx_desc_idx = 0;
static uint32_t tx_desc_idx = 0;

/* Функції узгодження кеша Cortex-M7 (CMSIS) */
static inline void cache_invalidate(void *addr, uint32_t size) {
    uint32_t a = (uint32_t)addr & ~(DCACHE_LINE_SIZE - 1);
    uint32_t s = size + ((uint32_t)addr - a);
    /* Виклик CMSIS: SCB_InvalidateDCache_by_Addr((uint32_t*)a, (int32_t)s); */
    (void)a; (void)s;
}

static inline void cache_clean(const void *addr, uint32_t size) {
    uint32_t a = (uint32_t)addr & ~(DCACHE_LINE_SIZE - 1);
    uint32_t s = size + ((uint32_t)addr - a);
    /* Виклик CMSIS: SCB_CleanDCache_by_Addr((uint32_t*)a, (int32_t)s); */
    (void)a; (void)s;
}

/**
 * @brief Ініціалізація кільця дескрипторів RX з прямим прив'язуванням PBUF_POOL
 */
bool eth_dma_rx_init(void) {
    for (uint32_t i = 0; i < ETH_RXBUFNB; i++) {
        struct pbuf *p = pbuf_alloc(PBUF_RAW, ETH_RX_BUF_SIZE, PBUF_POOL);
        if (p == NULL) {
            return false; /* Нестача пам'яті в PBUF_POOL */
        }

        rx_pbufs[i] = p;
        DMARxDscrTab[i].Buffer1Addr = (uint32_t)p->payload;
        DMARxDscrTab[i].ControlBufferSize = ETH_RX_BUF_SIZE;
        DMARxDscrTab[i].Buffer2NextDescAddr = (uint32_t)&DMARxDscrTab[(i + 1) % ETH_RXBUFNB];
        
        if (i == ETH_RXBUFNB - 1) {
            DMARxDscrTab[i].ControlBufferSize |= ETH_DMARXDESC_RER;
        }

        cache_invalidate(p->payload, ETH_RX_BUF_SIZE);
        DMARxDscrTab[i].Status = ETH_DMARXDESC_OWN;
    }
    
    cache_clean(DMARxDscrTab, sizeof(DMARxDscrTab));
    rx_desc_idx = 0;
    return true;
}

/**
 * @brief Обробник отримання кадру Zero-Copy (виклик з задачі/переривання)
 */
struct pbuf* eth_dma_rx_receive(void) {
    ETH_DMADescTypeDef *d = &DMARxDscrTab[rx_desc_idx];
    cache_invalidate(d, sizeof(ETH_DMADescTypeDef));

    /* Якщо DMA ще володіє дескриптором — нових пакетів немає */
    if (d->Status & ETH_DMARXDESC_OWN) {
        return NULL;
    }

    uint32_t frame_len = (d->Status >> 16) & 0x3FFF;
    struct pbuf *p_received = rx_pbufs[rx_desc_idx];

    /* Виділяємо новий порожній pbuf на заміну прийнятому */
    struct pbuf *p_new = pbuf_alloc(PBUF_RAW, ETH_RX_BUF_SIZE, PBUF_POOL);
    if (p_new != NULL) {
        p_received->len = (u16_t)frame_len;
        p_received->tot_len = (u16_t)frame_len;
        
        cache_invalidate(p_received->payload, frame_len);

        /* Підставляємо свіжий pbuf у дескриптор DMA */
        rx_pbufs[rx_desc_idx] = p_new;
        d->Buffer1Addr = (uint32_t)p_new->payload;
        cache_invalidate(p_new->payload, ETH_RX_BUF_SIZE);
    } else {
        /* При вичерпанні пулу дропаємо кадр і перевикористовуємо той самий pbuf */
        p_received = NULL;
    }

    /* Повертаємо дескриптор апаратному контролеру DMA */
    d->Status = ETH_DMARXDESC_OWN;
    cache_clean(d, sizeof(ETH_DMADescTypeDef));

    rx_desc_idx = (rx_desc_idx + 1) % ETH_RXBUFNB;
    return p_received;
}

/**
 * @brief Передача пакета Zero-Copy (TX)
 */
bool eth_dma_tx_send(struct pbuf *p) {
    ETH_DMADescTypeDef *d = &DMATxDscrTab[tx_desc_idx];
    cache_invalidate(d, sizeof(ETH_DMADescTypeDef));

    if (d->Status & ETH_DMATXDESC_OWN) {
        return false; /* Кільце передачі заповнене */
    }

    /* Звільняємо попередній pbuf, якщо передача вже завершилась */
    if (tx_pbufs[tx_desc_idx] != NULL) {
        pbuf_free(tx_pbufs[tx_desc_idx]);
        tx_pbufs[tx_desc_idx] = NULL;
    }

    /* Збільшуємо лічильник посилань pbuf на час роботи DMA */
    pbuf_ref(p);
    tx_pbufs[tx_desc_idx] = p;

    cache_clean(p->payload, p->len);

    d->Buffer1Addr = (uint32_t)p->payload;
    d->ControlBufferSize = p->len;
    d->Status = ETH_DMATXDESC_OWN | ETH_DMATXDESC_FS | ETH_DMATXDESC_LS | ETH_DMATXDESC_IC;

    cache_clean(d, sizeof(ETH_DMADescTypeDef));

    tx_desc_idx = (tx_desc_idx + 1) % ETH_TXBUFNB;
    return true;
}
