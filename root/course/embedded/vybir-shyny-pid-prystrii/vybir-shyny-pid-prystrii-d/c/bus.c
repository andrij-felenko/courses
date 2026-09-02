/* Реалізація диспетчера: черга транзакцій, запуск DMA, розбір завершень.
 *
 * Черга — кільце на BUS_QUEUE_LEN елементів. Голову рухає клієнт (потенційно з
 * будь-якого пріоритету), хвіст — код завершення. Обидві операції короткі, тож
 * узгодження зроблено найдешевшим способом: маскуванням переривань на кілька
 * інструкцій, без м'ютексів і без черг ОС.
 */
#include "bus.h"

#include <stddef.h>

#define BUS_MAX_INSTANCES 4u

static bus_t *s_instances[BUS_MAX_INSTANCES];

/* ---- критична секція на кілька інструкцій ---------------------------------- */

static inline uint32_t crit_enter(void)
{
    uint32_t primask = __get_PRIMASK();
    __disable_irq();
    return primask;
}

static inline void crit_exit(uint32_t primask)
{
    if (primask == 0u) {
        __enable_irq();
    }
}

/* ---- узгодження кешу даних -------------------------------------------------
 * На Cortex-M7 DMA не бачить кеша ядра: перед передачею буфер треба виштовхнути
 * в пам'ять, після прийому — оголосити недійсним. Адреси округлюємо до межі
 * рядка кешу (32 байти), тому самі буфери мають бути вирівняні на 32.
 */
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
static void dcache_clean(const void *addr, uint16_t len)
{
    if ((addr == NULL) || (len == 0u)) {
        return;
    }
    uint32_t start = (uint32_t)addr & ~0x1Fu;
    uint32_t end   = ((uint32_t)addr + len + 31u) & ~0x1Fu;
    SCB_CleanDCache_by_Addr((uint32_t *)start, (int32_t)(end - start));
}

static void dcache_invalidate(const void *addr, uint16_t len)
{
    if ((addr == NULL) || (len == 0u)) {
        return;
    }
    uint32_t start = (uint32_t)addr & ~0x1Fu;
    uint32_t end   = ((uint32_t)addr + len + 31u) & ~0x1Fu;
    SCB_InvalidateDCache_by_Addr((uint32_t *)start, (int32_t)(end - start));
}
#else
static void dcache_clean(const void *addr, uint16_t len) { (void)addr; (void)len; }
static void dcache_invalidate(const void *addr, uint16_t len) { (void)addr; (void)len; }
#endif

/* ---- реєстр екземплярів ----------------------------------------------------
 * HAL віддає завершення слабкими колбеками, куди приходить лише вказівник на
 * дескриптор периферії. За ним і знаходимо свій диспетчер.
 */
static void bus_register(bus_t *bus)
{
    for (uint32_t i = 0u; i < BUS_MAX_INSTANCES; ++i) {
        if ((s_instances[i] == NULL) || (s_instances[i] == bus)) {
            s_instances[i] = bus;
            return;
        }
    }
}

static bus_t *bus_by_handle(const void *handle)
{
    for (uint32_t i = 0u; i < BUS_MAX_INSTANCES; ++i) {
        if ((s_instances[i] != NULL) && (s_instances[i]->handle == handle)) {
            return s_instances[i];
        }
    }
    return NULL;
}

/* ---- SPI: режим тактування й вибірка кристала ------------------------------ */

/* Пастка CPOL/CPHA: на одному контролері можуть висіти чипи з різними режимами,
 * тож конфігурацію міняємо перед КОЖНИМ опусканням CS — і лише коли вона справді
 * інша, бо HAL_SPI_Init коштує кількох сотень тактів. */
static void spi_apply_mode(SPI_HandleTypeDef *spi, const bus_device_t *dev)
{
    if ((spi->Init.CLKPolarity == dev->spi_polarity) &&
        (spi->Init.CLKPhase == dev->spi_phase) &&
        (spi->Init.BaudRatePrescaler == dev->spi_prescaler)) {
        return;
    }
    (void)HAL_SPI_DeInit(spi);
    spi->Init.CLKPolarity      = dev->spi_polarity;
    spi->Init.CLKPhase         = dev->spi_phase;
    spi->Init.BaudRatePrescaler = dev->spi_prescaler;
    (void)HAL_SPI_Init(spi);
}

static void cs_assert(const bus_device_t *dev)
{
    if (dev->cs_port != NULL) {
        HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_RESET);
    }
}

static void cs_release(const bus_device_t *dev)
{
    if (dev->cs_port != NULL) {
        HAL_GPIO_WritePin(dev->cs_port, dev->cs_pin, GPIO_PIN_SET);
    }
}

/* ---- запуск фаз ------------------------------------------------------------ */

static HAL_StatusTypeDef spi_start_data(SPI_HandleTypeDef *spi, bus_txn_t *txn)
{
    /* HAL не const-correct: віддає uint8_t* навіть на передачу, тому cast. */
    switch (txn->op) {
    case BUS_OP_READ:
        return HAL_SPI_Receive_DMA(spi, txn->rx, txn->len);
    case BUS_OP_WRITE:
        dcache_clean(txn->tx, txn->len);
        return HAL_SPI_Transmit_DMA(spi, (uint8_t *)txn->tx, txn->len);
    case BUS_OP_TRANSFER:
        dcache_clean(txn->tx, txn->len);
        return HAL_SPI_TransmitReceive_DMA(spi, (uint8_t *)txn->tx, txn->rx, txn->len);
    default:
        return HAL_ERROR;
    }
}

static bus_result_t bus_start_current(bus_t *bus)
{
    bus_txn_t *txn = &bus->queue[bus->tail];
    HAL_StatusTypeDef st;

    bus->started_ms = HAL_GetTick();

    if (bus->kind == BUS_KIND_I2C) {
        I2C_HandleTypeDef *i2c = (I2C_HandleTypeDef *)bus->handle;
        uint16_t addr = (uint16_t)(txn->dev->i2c_addr << 1);

        bus->phase = BUS_PHASE_DATA;
        if (txn->cmd_len == 0u) {
            if (txn->op == BUS_OP_READ) {
                st = HAL_I2C_Master_Receive_DMA(i2c, addr, txn->rx, txn->len);
            } else {
                dcache_clean(txn->tx, txn->len);
                st = HAL_I2C_Master_Transmit_DMA(i2c, addr, (uint8_t *)txn->tx, txn->len);
            }
        } else if (txn->cmd_len <= 2u) {
            /* Апаратний блок сам віддає адресу регістра й робить повторний старт. */
            uint16_t mem   = txn->cmd[0];
            uint16_t msize = I2C_MEMADD_SIZE_8BIT;
            if (txn->cmd_len == 2u) {
                mem   = (uint16_t)(((uint16_t)txn->cmd[0] << 8) | txn->cmd[1]);
                msize = I2C_MEMADD_SIZE_16BIT;
            }
            if (txn->op == BUS_OP_READ) {
                st = HAL_I2C_Mem_Read_DMA(i2c, addr, mem, msize, txn->rx, txn->len);
            } else {
                dcache_clean(txn->tx, txn->len);
                st = HAL_I2C_Mem_Write_DMA(i2c, addr, mem, msize, (uint8_t *)txn->tx, txn->len);
            }
        } else {
            /* Довша за 2 байти адреса регістра в I2C не буває — це помилка клієнта. */
            st = HAL_ERROR;
        }
    } else {
        SPI_HandleTypeDef *spi = (SPI_HandleTypeDef *)bus->handle;

        spi_apply_mode(spi, txn->dev);
        cs_assert(txn->dev);

        if (txn->cmd_len > 0u) {
            bus->phase = BUS_PHASE_CMD;
            dcache_clean(txn->cmd, txn->cmd_len);
            st = HAL_SPI_Transmit_DMA(spi, txn->cmd, txn->cmd_len);
        } else if (txn->len > 0u) {
            bus->phase = BUS_PHASE_DATA;
            st = spi_start_data(spi, txn);
        } else {
            st = HAL_ERROR;   /* порожня транзакція нікуди не поїде */
        }
    }

    return (st == HAL_OK) ? BUS_OK : BUS_ERR_HAL;
}

/* Завершує поточну транзакцію й тягне наступні. Цикл, а не рекурсія: коли чипа
 * на платі просто немає, HAL відмовляє на старті, і вся черга склалася б у
 * глибокий стек викликів. */
static void bus_complete(bus_t *bus, bus_result_t result)
{
    for (;;) {
        bus_txn_t *txn = &bus->queue[bus->tail];

        if (bus->kind == BUS_KIND_SPI) {
            cs_release(txn->dev);
        }
        if ((result == BUS_OK) && (txn->op != BUS_OP_WRITE)) {
            dcache_invalidate(txn->rx, txn->len);
        }

        bus_done_fn done = txn->done;
        void       *ctx  = txn->ctx;

        uint32_t primask = crit_enter();
        bus->tail = (uint8_t)((bus->tail + 1u) % BUS_QUEUE_LEN);
        crit_exit(primask);
        bus->phase = BUS_PHASE_IDLE;

        if (result == BUS_OK) {
            bus->stat_done++;
        } else {
            bus->stat_failed++;
        }

        /* busy лишається виставленим: якщо колбек покладе нову транзакцію,
         * вона не спробує стартувати сама — її підбере цей самий цикл. */
        if (done != NULL) {
            done(result, ctx);
        }

        primask = crit_enter();
        bool has_next = (bus->head != bus->tail);
        bus->busy = has_next;
        crit_exit(primask);

        if (!has_next) {
            return;
        }
        result = bus_start_current(bus);
        if (result == BUS_OK) {
            return;   /* далі веде DMA */
        }
    }
}

/* ---- публічний інтерфейс --------------------------------------------------- */

void bus_init_i2c(bus_t *bus, I2C_HandleTypeDef *i2c, const i2c_lines_t *lines)
{
    bus->kind   = BUS_KIND_I2C;
    bus->handle = i2c;
    bus->lines  = *lines;
    bus->head   = 0u;
    bus->tail   = 0u;
    bus->busy   = false;
    bus->phase  = BUS_PHASE_IDLE;
    bus->needs_recovery = false;
    bus->stat_done = 0u;
    bus->stat_failed = 0u;
    bus->stat_dropped = 0u;
    bus->stat_recovered = 0u;
    bus_register(bus);
}

void bus_init_spi(bus_t *bus, SPI_HandleTypeDef *spi)
{
    bus->kind   = BUS_KIND_SPI;
    bus->handle = spi;
    bus->head   = 0u;
    bus->tail   = 0u;
    bus->busy   = false;
    bus->phase  = BUS_PHASE_IDLE;
    bus->needs_recovery = false;
    bus->stat_done = 0u;
    bus->stat_failed = 0u;
    bus->stat_dropped = 0u;
    bus->stat_recovered = 0u;
    bus_register(bus);
}

bool bus_submit(bus_t *bus, const bus_txn_t *txn)
{
    if ((txn->dev == NULL) || (txn->cmd_len > BUS_MAX_CMD_BYTES)) {
        return false;
    }

    uint32_t primask = crit_enter();
    uint8_t next = (uint8_t)((bus->head + 1u) % BUS_QUEUE_LEN);
    if (next == bus->tail) {
        bus->stat_dropped++;
        crit_exit(primask);
        return false;
    }
    bus->queue[bus->head] = *txn;
    bus->head = next;

    bool take_bus = !bus->busy;
    if (take_bus) {
        bus->busy = true;   /* займаємо шину ще під маскою, щоб ISR не стартував удруге */
    }
    crit_exit(primask);

    if (take_bus) {
        bus_result_t res = bus_start_current(bus);
        if (res != BUS_OK) {
            bus_complete(bus, res);
        }
    }
    return true;
}

void bus_poll(bus_t *bus)
{
    if (bus->needs_recovery) {
        bus->needs_recovery = false;
        if (i2c_bus_recover((I2C_HandleTypeDef *)bus->handle, &bus->lines)) {
            bus->stat_recovered++;
        }
    }

    if (!bus->busy) {
        return;
    }

    uint16_t limit = bus->queue[bus->tail].timeout_ms;
    if (limit == 0u) {
        limit = BUS_DEFAULT_TIMEOUT_MS;
    }
    if ((uint32_t)(HAL_GetTick() - bus->started_ms) < (uint32_t)limit) {
        return;
    }

    /* Мовчання DMA довше за дозволене означає застряглий обмін: обриваємо його
     * й віддаємо клієнтові чесний BUS_ERR_TIMEOUT, а не тихе зависання. */
    if (bus->kind == BUS_KIND_SPI) {
        (void)HAL_SPI_Abort((SPI_HandleTypeDef *)bus->handle);
    } else {
        I2C_HandleTypeDef *i2c = (I2C_HandleTypeDef *)bus->handle;
        (void)HAL_I2C_Master_Abort_IT(i2c, (uint16_t)(bus->queue[bus->tail].dev->i2c_addr << 1));
        bus->needs_recovery = true;
    }

    uint32_t primask = crit_enter();
    bool still_busy = bus->busy;   /* переривання могло встигнути завершити обмін */
    crit_exit(primask);
    if (still_busy) {
        bus_complete(bus, BUS_ERR_TIMEOUT);
    }
}

/* ---- місток від колбеків HAL ----------------------------------------------- */

static void bus_on_transfer_done(bus_t *bus)
{
    if ((bus == NULL) || !bus->busy) {
        return;
    }

    bus_txn_t *txn = &bus->queue[bus->tail];

    if ((bus->kind == BUS_KIND_SPI) && (bus->phase == BUS_PHASE_CMD)) {
        bus->phase = BUS_PHASE_DATA;
        if (txn->len == 0u) {
            bus_complete(bus, BUS_OK);   /* команда без даних, як WREN у FRAM */
            return;
        }
        if (spi_start_data((SPI_HandleTypeDef *)bus->handle, txn) != HAL_OK) {
            bus_complete(bus, BUS_ERR_HAL);
        }
        return;
    }

    bus_complete(bus, BUS_OK);
}

static void bus_on_error(bus_t *bus)
{
    if ((bus == NULL) || !bus->busy) {
        return;
    }
    if (bus->kind == BUS_KIND_I2C) {
        /* Лікуємо не тут: розблокування смикає піни й спить мікросекунди,
         * а ми в перериванні. Позначаємо й повертаємося в bus_poll(). */
        bus->needs_recovery = true;
    }
    bus_complete(bus, BUS_ERR_HAL);
}

void HAL_I2C_MemRxCpltCallback(I2C_HandleTypeDef *hi2c)
{
    bus_on_transfer_done(bus_by_handle(hi2c));
}

void HAL_I2C_MemTxCpltCallback(I2C_HandleTypeDef *hi2c)
{
    bus_on_transfer_done(bus_by_handle(hi2c));
}

void HAL_I2C_MasterRxCpltCallback(I2C_HandleTypeDef *hi2c)
{
    bus_on_transfer_done(bus_by_handle(hi2c));
}

void HAL_I2C_MasterTxCpltCallback(I2C_HandleTypeDef *hi2c)
{
    bus_on_transfer_done(bus_by_handle(hi2c));
}

void HAL_I2C_ErrorCallback(I2C_HandleTypeDef *hi2c)
{
    bus_on_error(bus_by_handle(hi2c));
}

void HAL_I2C_AbortCpltCallback(I2C_HandleTypeDef *hi2c)
{
    bus_on_error(bus_by_handle(hi2c));
}

void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef *hspi)
{
    bus_on_transfer_done(bus_by_handle(hspi));
}

void HAL_SPI_RxCpltCallback(SPI_HandleTypeDef *hspi)
{
    bus_on_transfer_done(bus_by_handle(hspi));
}

void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi)
{
    bus_on_transfer_done(bus_by_handle(hspi));
}

void HAL_SPI_ErrorCallback(SPI_HandleTypeDef *hspi)
{
    bus_on_error(bus_by_handle(hspi));
}
