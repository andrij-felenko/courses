# ⚙️ Проєкт драйвера Ethernet MAC Zero-Copy: прив'язка DMA до буферів pbuf

Під час передавання трафіку на швидкості 100 Мбіт/с мережевий контролер обробляє до 148 800 кадрів за секунду. Якщо драйвер використовує проміжне копіювання (`memcpy`) для перенесення кожного байта з апаратних буферів DMA у структури `pbuf` стека lwIP, процесор Cortex-M4 або Cortex-M7 витрачає до 60–80% тактової частоти лише на пересилку пам'яті. Механізм Zero-Copy (нульового копіювання) усуває цей наклад: дескриптори DMA зв'язуються безпосередньо з вказівниками на корисні дані у пулі `PBUF_POOL`.

---

## 1. Архітектура апаратних дескрипторів DMA

Вбудований Ethernet MAC контролер (наприклад, у сімействах STM32F4, STM32F7, STM32H7 або NXP i.MX RT) керує прийомом та передачею даних через кільцеві списки апаратних дескрипторів DMA (*Descriptor Ring*). Контролер працює як незалежний майстер шини (Bus Master), автономно вичитуючи кадри з внутрішнього FIFO трансивера та записуючи їх безпосередньо в системну пам'ять SRAM без участі процесорного ядра.

```
+-------------------------------------------------------------------------------+
|                 Кільцевий список дескрипторів DMA (RX Ring)                   |
|                                                                               |
|  +--------------------+      +--------------------+      +-----------------+  |
|  | RX Descriptor #0   | ───► | RX Descriptor #1   | ───► | RX Desc #2 (RER)|  |
|  | • Status: OWN_DMA  |      | • Status: OWN_CPU  |      | • Status: ...   |  |
|  | • Buffer: pbuf0-›  |      | • Buffer: pbuf1-›  |      | • Buffer: ...   |  |
|  +--------------------+      +--------------------+      +-----------------+  |
|            ▲                                                      │           |
|            └──────────────────────────────────────────────────────┘           |
+-------------------------------------------------------------------------------+
```

### Структура дескриптора DMA (`ETH_DMADescTypeDef`)

Кожен дескриптор складається з чотирьох 32-бітних слів (16 байтів у стандартному режимі або 32 байти в режимі з апаратними мітками часу IEEE 1588):
1. `DESC0` (Регістр стану `Status`):
   * Біт 31 (`OWN`): Прапорець володіння. Якщо біт встановлено в `1`, дескриптор належить контролеру DMA і процесор не має права змінювати його поля. Якщо біт скинуто в `0`, обробку завершено і буфер передано процесору.
   * Біти 29–28 (`FS` / `LS`): Перший та останній сегмент кадру (*First / Last Segment*). Для нефрагментованих кадрів обидва біти встановлені в `1`.
   * Біти 16–29 (`FL`): Довжина прийнятого кадру в байтах (*Frame Length*), включаючи 4 байти контрольної суми FCS (CRC32).
2. `DESC1` (Регістр керування `ControlBufferSize`):
   * Біт 15 (`RER` / `TER`): Кінець кільця (*Receive/Transmit End of Ring*). Вказує контролеру DMA повернутися до початку масиву дескрипторів.
   * Біти 0–12 (`RBS1`): Розмір виділеного буфера прийому в байтах (повинен точно відповідати розміру `PBUF_POOL_BUFSIZE`, тобто 1536 байтів).
3. `DESC2` (Адреса буфера `Buffer1Addr`):
   * Фізична 32-бітна адреса в пам'яті SRAM, куди DMA записуватиме байти кадру (встановлюється рівною `(uint32_t)pbuf->payload`).
4. `DESC3` (Адреса зв'язку `Buffer2NextDescAddr`):
   * Вказівник на наступний дескриптор у кільцевому ланцюжку.

---

## 2. Когерентність кеша даних (ARM Cortex-M7 D-Cache)

У мікроконтролерах із процесорним ядром Cortex-M7 (STM32F7, STM32H7, Microchip SAM E70, NXP i.MX RT) увімкнено гарвардський кеш даних першого рівня (L1 D-Cache) з рядками по 32 байти. Оскільки контролер Ethernet DMA є зовнішнім майстром шини AXI/AHB, він звертається безпосередньо до фізичної пам'яті SRAM в обхід кеша процесора. Без спеціальних операцій синхронізації це призводить до фатального пошкодження даних:

```
+-------------------------------------------------------------------------------+
|                      Проблема та лікування D-Cache                            |
|                                                                               |
|   RX Операція:                                                                |
|   1. DMA записує новий Ethernet-кадр у фізичну SRAM.                          |
|   2. Процесор викликає SCB_InvalidateDCache_by_Addr(): кеш-лінії скидаються.  |
|   3. Процесор читає свіжі байти безпосередньо з фізичної пам'яті.             |
|                                                                               |
|   TX Операція:                                                                |
|   1. Процесор формує вихідний пакет TCP/IP у своєму D-Cache.                  |
|   2. Процесор викликає SCB_CleanDCache_by_Addr(): брудні дані скидаються в RAM.|
|   3. DMA зчитує актуальні байти з RAM і передає в кабель.                     |
+-------------------------------------------------------------------------------+
```

### Суворі вимоги до вирівнювання пам'яті (Cache-Line Alignment)

Якщо буфер дескриптора або пакета не вирівняний по межі 32 байтів, виникає явище паразитного перезапису (*False Sharing*):
* Припустимо, буфер `pbuf->payload` починається за адресою `0x20000010` (зсув 16 байтів всередині кеш-лінії `0x20000000–0x2000001F`).
* Перші 16 байтів цієї кеш-лінії займає системна змінна лічильника операційної системи.
* Коли процесор виконує інвалідацію кеш-лінії для читання пакета (`SCB_InvalidateDCache_by_Addr`), рядок кеша анулюється, і незбережені зміни лічильника в перших 16 байтах безповоротно втрачаються.

> **Правило вирівнювання:** Усі масиви дескрипторів `ETH_DMADescTypeDef` та область корисного навантаження кожного буфера `PBUF_POOL` повинні бути вирівняні за атрибутом `__attribute__((aligned(32)))`, а їхні розміри мають бути строго кратними 32 байтам.

---

## 3. Реалізація драйвера Zero-Copy

Нижче наведено робочу реалізацію функцій ініціалізації кільця RX дескрипторів, обробки вхідного переривання та безпечної передачі пакетів без проміжного копіювання.

:::tabs

@tab C (Реалізація lwIP Ethernetif)
```c
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
```

@tab C++ (Ідіоматичний драйвер Zero-Copy)
```cpp
#include <span>
#include <array>
#include <cstdint>
#include <optional>
#include <concepts>

extern "C" {
#include "lwip/opt.h"
#include "lwip/pbuf.h"
}

namespace embedded::net {

inline constexpr size_t kRxDescCount = 4;
inline constexpr size_t kTxDescCount = 4;
inline constexpr size_t kFrameBufSize = 1536;
inline constexpr size_t kCacheLineSize = 32;

enum class DmaStatus : uint32_t {
    OwnByDma  = 0x80000000U,
    FirstSeg  = 0x20000000U,
    LastSeg   = 0x10000000U,
    IntOnComp = 0x40000000U,
    RxEndOfRing = 0x00008000U,
};

struct alignas(kCacheLineSize) DmaDescriptor {
    volatile uint32_t status{0};
    volatile uint32_t controlBufferSize{0};
    volatile uint32_t buffer1Addr{0};
    volatile uint32_t buffer2NextDescAddr{0};
};

class PbufScopedRef {
public:
    explicit PbufScopedRef(struct pbuf* p) noexcept : pbuf_(p) {
        if (pbuf_ != nullptr) {
            pbuf_ref(pbuf_);
        }
    }

    ~PbufScopedRef() noexcept {
        if (pbuf_ != nullptr) {
            pbuf_free(pbuf_);
        }
    }

    PbufScopedRef(const PbufScopedRef&) = delete;
    PbufScopedRef& operator=(const PbufScopedRef&) = delete;

    PbufScopedRef(PbufScopedRef&& other) noexcept : pbuf_(other.pbuf_) {
        other.pbuf_ = nullptr;
    }

    [[nodiscard]] struct pbuf* get() const noexcept { return pbuf_; }
    [[nodiscard]] struct pbuf* release() noexcept {
        struct pbuf* tmp = pbuf_;
        pbuf_ = nullptr;
        return tmp;
    }

private:
    struct pbuf* pbuf_{nullptr};
};

class EthernetZeroCopyDriver {
public:
    EthernetZeroCopyDriver() noexcept = default;

    [[nodiscard]] bool init() noexcept {
        for (size_t i = 0; i < kRxDescCount; ++i) {
            struct pbuf* p = pbuf_alloc(PBUF_RAW, kFrameBufSize, PBUF_POOL);
            if (p == nullptr) {
                return false;
            }

            rxPbufs_[i] = p;
            rxRing_[i].buffer1Addr = reinterpret_cast<uint32_t>(p->payload);
            rxRing_[i].controlBufferSize = kFrameBufSize;
            rxRing_[i].buffer2NextDescAddr = reinterpret_cast<uint32_t>(&rxRing_[(i + 1) % kRxDescCount]);

            if (i == kRxDescCount - 1) {
                rxRing_[i].controlBufferSize |= static_cast<uint32_t>(DmaStatus::RxEndOfRing);
            }

            invalidateCache(p->payload, kFrameBufSize);
            rxRing_[i].status = static_cast<uint32_t>(DmaStatus::OwnByDma);
        }

        cleanCache(rxRing_.data(), sizeof(rxRing_));
        rxHead_ = 0;
        return true;
    }

    [[nodiscard]] std::optional<struct pbuf*> receivePacket() noexcept {
        auto& desc = rxRing_[rxHead_];
        invalidateCache(&desc, sizeof(DmaDescriptor));

        if ((desc.status & static_cast<uint32_t>(DmaStatus::OwnByDma)) != 0) {
            return std::nullopt; /* Кадр ще не надійшов */
        }

        const uint32_t frameLen = (desc.status >> 16) & 0x3FFFU;
        struct pbuf* received = rxPbufs_[rxHead_];

        /* Виділяємо свіжий pbuf під наступний прийом */
        struct pbuf* freshPbuf = pbuf_alloc(PBUF_RAW, kFrameBufSize, PBUF_POOL);
        if (freshPbuf != nullptr) {
            received->len = static_cast<u16_t>(frameLen);
            received->tot_len = static_cast<u16_t>(frameLen);
            invalidateCache(received->payload, frameLen);

            rxPbufs_[rxHead_] = freshPbuf;
            desc.buffer1Addr = reinterpret_cast<uint32_t>(freshPbuf->payload);
            invalidateCache(freshPbuf->payload, kFrameBufSize);
        } else {
            /* При вичерпанні пулу скидаємо пакет та перевикористовуємо буфер */
            received = nullptr;
        }

        desc.status = static_cast<uint32_t>(DmaStatus::OwnByDma);
        cleanCache(&desc, sizeof(DmaDescriptor));

        rxHead_ = (rxHead_ + 1) % kRxDescCount;
        return received != nullptr ? std::make_optional(received) : std::nullopt;
    }

    [[nodiscard]] bool sendPacket(struct pbuf* p) noexcept {
        if (p == nullptr) {
            return false;
        }

        auto& desc = txRing_[txHead_];
        invalidateCache(&desc, sizeof(DmaDescriptor));

        if ((desc.status & static_cast<uint32_t>(DmaStatus::OwnByDma)) != 0) {
            return false; /* Кільце передачі заповнене */
        }

        /* Звільняємо старий pbuf після підтвердження DMA */
        if (txPbufs_[txHead_] != nullptr) {
            pbuf_free(txPbufs_[txHead_]);
            txPbufs_[txHead_] = nullptr;
        }

        pbuf_ref(p);
        txPbufs_[txHead_] = p;

        cleanCache(p->payload, p->len);

        desc.buffer1Addr = reinterpret_cast<uint32_t>(p->payload);
        desc.controlBufferSize = p->len;
        desc.status = static_cast<uint32_t>(DmaStatus::OwnByDma) |
                      static_cast<uint32_t>(DmaStatus::FirstSeg) |
                      static_cast<uint32_t>(DmaStatus::LastSeg)  |
                      static_cast<uint32_t>(DmaStatus::IntOnComp);

        cleanCache(&desc, sizeof(DmaDescriptor));
        txHead_ = (txHead_ + 1) % kTxDescCount;
        return true;
    }

private:
    static void invalidateCache(const void* addr, size_t size) noexcept {
        const auto a = reinterpret_cast<uintptr_t>(addr) & ~(kCacheLineSize - 1);
        const auto s = size + (reinterpret_cast<uintptr_t>(addr) - a);
        /* SCB_InvalidateDCache_by_Addr(reinterpret_cast<uint32_t*>(a), static_cast<int32_t>(s)); */
        (void)a; (void)s;
    }

    static void cleanCache(const void* addr, size_t size) noexcept {
        const auto a = reinterpret_cast<uintptr_t>(addr) & ~(kCacheLineSize - 1);
        const auto s = size + (reinterpret_cast<uintptr_t>(addr) - a);
        /* SCB_CleanDCache_by_Addr(reinterpret_cast<uint32_t*>(a), static_cast<int32_t>(s)); */
        (void)a; (void)s;
    }

    alignas(kCacheLineSize) std::array<DmaDescriptor, kRxDescCount> rxRing_{};
    alignas(kCacheLineSize) std::array<DmaDescriptor, kTxDescCount> txRing_{};
    std::array<struct pbuf*, kRxDescCount> rxPbufs_{};
    std::array<struct pbuf*, kTxDescCount> txPbufs_{};

    size_t rxHead_{0};
    size_t txHead_{0};
};

} // namespace embedded::net
```

:::

---

## 4. Вивільнення пам'яті та захист від стану гонитви (Race Conditions)

Під час розробки асинхронних драйверів мережі виникає кілька типових крайових випадків, які можуть зруйнувати цілісність пам'яті або заблокувати прийом пакетів:

### 1. Відкладене звільнення буферів передачі (Deferred TX Free)
Класична помилка початківців — викликати `pbuf_free()` безпосередньо з обробника переривання закінчення передачі DMA (`ETH_IRQHandler`). Це небезпечно, оскільки:
* Функція `pbuf_free()` може викликати звільнення ланцюжка дескрипторів або повернення пам'яті в купу `mem_malloc`, яка не є реентрабельною без глобального блокування планувальника RTOS.
* Виклик динамічної алокації з переривання збільшує джитер системного таймера.

Правильне інженерне рішення полягає у відкладеному вивільненні: дескриптор передачі запам'ятовує вказівник на надісланий `pbuf`. Коли при наступній передачі через `eth_dma_tx_send()` кільцевий індекс знову доходить до цього дескриптора, драйвер перевіряє скидання біта `OWN` і безпечно звільняє старий `pbuf` вже в контексті викликаючої задачі.

### 2. Поведінка драйвера при вичерпанні пулу прийому (RX Starvation)
Якщо мережевий трафік перевищує швидкість обробки задач, виклик `pbuf_alloc(..., PBUF_POOL)` повертає `NULL`. Якщо драйвер у цей момент вилучить заповнений `pbuf` з дескриптора і не зможе вставити новий, апаратний дескриптор залишиться з нульовою адресою, що призведе до апаратної зупинки шини DMA (*DMA Bus Fault / Fatal Rx Overflow*).

У наведеній реалізації застосовано безпечну стратегію захисту:
* Якщо `p_new == NULL`, драйвер просто відкидає щойно прийнятий пакет.
* Вказівник `p_received` не передається в стек lwIP, а залишається підключеним до того самого дескриптора DMA.
* Дескриптору повертається біт `OWN_DMA`. Кадр втрачається на апаратному рівні, але апаратний ланцюжок залишається цілісним і контролер продовжує функціонувати.
