#include "bus/dispatcher.hpp"

namespace bus {
namespace {

constexpr std::size_t kMaxDispatchers = 4;
Dispatcher* g_registry[kMaxDispatchers]{};

void register_dispatcher(Dispatcher* dispatcher)
{
    for (auto& slot : g_registry) {
        if (slot == nullptr) {
            slot = dispatcher;
            return;
        }
    }
}

void unregister_dispatcher(Dispatcher* dispatcher)
{
    for (auto& slot : g_registry) {
        if (slot == dispatcher) {
            slot = nullptr;
        }
    }
}

// На Cortex-M7 DMA не бачить кеша ядра: перед передачею буфер виштовхуємо,
// після прийому оголошуємо недійсним. Межі округлюємо до рядка кешу.
void clean_cache(std::span<const std::uint8_t> buffer) noexcept
{
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
    if (buffer.empty()) {
        return;
    }
    const auto begin = reinterpret_cast<std::uintptr_t>(buffer.data()) & ~std::uintptr_t{0x1F};
    const auto end = (reinterpret_cast<std::uintptr_t>(buffer.data()) + buffer.size() + 31U) &
                     ~std::uintptr_t{0x1F};
    SCB_CleanDCache_by_Addr(reinterpret_cast<std::uint32_t*>(begin),
                            static_cast<std::int32_t>(end - begin));
#else
    (void)buffer;
#endif
}

void invalidate_cache(std::span<const std::uint8_t> buffer) noexcept
{
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)
    if (buffer.empty()) {
        return;
    }
    const auto begin = reinterpret_cast<std::uintptr_t>(buffer.data()) & ~std::uintptr_t{0x1F};
    const auto end = (reinterpret_cast<std::uintptr_t>(buffer.data()) + buffer.size() + 31U) &
                     ~std::uintptr_t{0x1F};
    SCB_InvalidateDCache_by_Addr(reinterpret_cast<std::uint32_t*>(begin),
                                 static_cast<std::int32_t>(end - begin));
#else
    (void)buffer;
#endif
}

// HAL не const-correct: навіть на передачу вимагає uint8_t*.
std::uint8_t* writable(std::span<const std::uint8_t> buffer) noexcept
{
    return const_cast<std::uint8_t*>(buffer.data());
}

}  // namespace

Dispatcher::Dispatcher(I2C_HandleTypeDef& i2c, const I2cLines& lines) noexcept
    : kind_{Kind::I2c}, handle_{&i2c}, lines_{lines}
{
    register_dispatcher(this);
}

Dispatcher::Dispatcher(SPI_HandleTypeDef& spi) noexcept : kind_{Kind::Spi}, handle_{&spi}
{
    register_dispatcher(this);
}

Dispatcher::~Dispatcher()
{
    unregister_dispatcher(this);
}

Dispatcher* Dispatcher::from_handle(const void* hal_handle) noexcept
{
    for (Dispatcher* dispatcher : g_registry) {
        if (dispatcher != nullptr && dispatcher->handle_ == hal_handle) {
            return dispatcher;
        }
    }
    return nullptr;
}

// Пастка CPOL/CPHA: на одній шині можуть висіти чипи з різними режимами, тож
// конфігурацію міняємо перед кожним опусканням CS — і тільки коли вона інша.
void Dispatcher::apply_spi_mode(const Device& device) noexcept
{
    auto* spi = static_cast<SPI_HandleTypeDef*>(handle_);
    const std::uint32_t polarity = clock_polarity(device.spi_mode);
    const std::uint32_t phase = clock_phase(device.spi_mode);

    if (spi->Init.CLKPolarity == polarity && spi->Init.CLKPhase == phase &&
        spi->Init.BaudRatePrescaler == device.spi_prescaler) {
        return;
    }

    static_cast<void>(HAL_SPI_DeInit(spi));
    spi->Init.CLKPolarity = polarity;
    spi->Init.CLKPhase = phase;
    spi->Init.BaudRatePrescaler = device.spi_prescaler;
    static_cast<void>(HAL_SPI_Init(spi));
}

HAL_StatusTypeDef Dispatcher::start_i2c(Transaction& txn) noexcept
{
    auto* i2c = static_cast<I2C_HandleTypeDef*>(handle_);
    const auto address = static_cast<std::uint16_t>(txn.device->i2c_address << 1);

    phase_ = Phase::Data;

    if (txn.command.empty()) {
        if (txn.op == Op::Read) {
            return HAL_I2C_Master_Receive_DMA(i2c, address, txn.rx.data(),
                                              static_cast<std::uint16_t>(txn.rx.size()));
        }
        clean_cache(txn.tx);
        return HAL_I2C_Master_Transmit_DMA(i2c, address, writable(txn.tx),
                                           static_cast<std::uint16_t>(txn.tx.size()));
    }

    const auto memory = txn.command.memory_address();
    if (!memory.has_value()) {
        return HAL_ERROR;   // довшої за 2 байти адреси регістра в I2C не буває
    }

    if (txn.op == Op::Read) {
        return HAL_I2C_Mem_Read_DMA(i2c, address, *memory, txn.command.memory_address_size(),
                                    txn.rx.data(), static_cast<std::uint16_t>(txn.rx.size()));
    }
    clean_cache(txn.tx);
    return HAL_I2C_Mem_Write_DMA(i2c, address, *memory, txn.command.memory_address_size(),
                                 writable(txn.tx), static_cast<std::uint16_t>(txn.tx.size()));
}

HAL_StatusTypeDef Dispatcher::start_spi_data(Transaction& txn) noexcept
{
    auto* spi = static_cast<SPI_HandleTypeDef*>(handle_);

    switch (txn.op) {
    case Op::Read:
        return HAL_SPI_Receive_DMA(spi, txn.rx.data(), static_cast<std::uint16_t>(txn.rx.size()));
    case Op::Write:
        clean_cache(txn.tx);
        return HAL_SPI_Transmit_DMA(spi, writable(txn.tx),
                                    static_cast<std::uint16_t>(txn.tx.size()));
    case Op::Transfer:
        clean_cache(txn.tx);
        return HAL_SPI_TransmitReceive_DMA(spi, writable(txn.tx), txn.rx.data(),
                                           static_cast<std::uint16_t>(txn.tx.size()));
    }
    return HAL_ERROR;
}

Result Dispatcher::start_current() noexcept
{
    Transaction& txn = queue_[tail_];
    started_ms_ = HAL_GetTick();

    HAL_StatusTypeDef status = HAL_ERROR;

    if (kind_ == Kind::I2c) {
        status = start_i2c(txn);
    } else {
        apply_spi_mode(*txn.device);
        chip_select_.emplace(*txn.device);   // CS упаде тут і підніметься в complete()

        if (!txn.command.empty()) {
            phase_ = Phase::CommandBytes;
            clean_cache({txn.command.data(), txn.command.size()});
            status = HAL_SPI_Transmit_DMA(static_cast<SPI_HandleTypeDef*>(handle_),
                                          txn.command.data(),
                                          static_cast<std::uint16_t>(txn.command.size()));
        } else {
            phase_ = Phase::Data;
            status = start_spi_data(txn);
        }
    }

    return (status == HAL_OK) ? Result::Ok : Result::HardwareError;
}

// Завершує поточну транзакцію й тягне наступні. Саме цикл, а не рекурсія: коли
// чипа на платі немає, HAL відмовляє одразу на старті, і вся черга склалася б
// у глибокий стек викликів усередині переривання.
void Dispatcher::complete(Result result) noexcept
{
    for (;;) {
        Transaction& txn = queue_[tail_];

        chip_select_.reset();   // деструктор ChipSelect піднімає лінію

        if (result == Result::Ok && txn.op != Op::Write) {
            invalidate_cache(txn.rx);
        }

        const Completion done = txn.done;

        {
            IrqLock lock;
            tail_ = (tail_ + 1) % kQueueCapacity;
        }
        phase_ = Phase::Idle;

        if (result == Result::Ok) {
            ++stats_.done;
        } else {
            ++stats_.failed;
        }

        // busy_ лишається виставленим: якщо колбек покладе нову транзакцію,
        // вона не стартує сама — її підбере цей самий цикл.
        done(result);

        bool has_next = false;
        {
            IrqLock lock;
            has_next = head_ != tail_;
            busy_ = has_next;
        }

        if (!has_next) {
            return;
        }
        result = start_current();
        if (result == Result::Ok) {
            return;   // далі веде DMA
        }
    }
}

std::expected<void, SubmitError> Dispatcher::submit(const Transaction& txn) noexcept
{
    if (txn.device == nullptr) {
        return std::unexpected{SubmitError::NoDevice};
    }
    if (txn.command.empty() && txn.tx.empty() && txn.rx.empty()) {
        return std::unexpected{SubmitError::EmptyTransaction};
    }
    if (kind_ == Kind::I2c && !txn.command.empty() && !txn.command.memory_address().has_value()) {
        return std::unexpected{SubmitError::CommandTooLong};
    }

    bool take_bus = false;
    {
        IrqLock lock;
        const std::size_t next_head = (head_ + 1) % kQueueCapacity;
        if (next_head == tail_) {
            ++stats_.dropped;
            return std::unexpected{SubmitError::QueueFull};
        }
        queue_[head_] = txn;
        head_ = next_head;

        take_bus = !busy_;
        if (take_bus) {
            busy_ = true;   // займаємо шину ще під маскою, щоб ISR не стартував удруге
        }
    }

    if (take_bus) {
        const Result result = start_current();
        if (result != Result::Ok) {
            complete(result);
        }
    }
    return {};
}

void Dispatcher::poll() noexcept
{
    if (needs_recovery_) {
        needs_recovery_ = false;
        const auto outcome = recover_i2c_bus(*static_cast<I2C_HandleTypeDef*>(handle_), lines_);
        if (outcome == RecoveryOutcome::Released) {
            ++stats_.recovered;
        }
    }

    if (!busy_) {
        return;
    }

    const std::uint32_t limit = queue_[tail_].timeout_ms;
    if (HAL_GetTick() - started_ms_ < limit) {
        return;
    }

    // Мовчання DMA довше за дозволене — це застряглий обмін. Обриваємо його й
    // віддаємо клієнтові чесний Timeout, а не тихе зависання назавжди.
    if (kind_ == Kind::Spi) {
        static_cast<void>(HAL_SPI_Abort(static_cast<SPI_HandleTypeDef*>(handle_)));
    } else {
        static_cast<void>(HAL_I2C_Master_Abort_IT(
            static_cast<I2C_HandleTypeDef*>(handle_),
            static_cast<std::uint16_t>(queue_[tail_].device->i2c_address << 1)));
        needs_recovery_ = true;
    }

    bool still_busy = false;
    {
        IrqLock lock;
        still_busy = busy_;   // переривання могло встигнути завершити обмін
    }
    if (still_busy) {
        complete(Result::Timeout);
    }
}

void Dispatcher::on_transfer_complete() noexcept
{
    if (!busy_) {
        return;
    }

    Transaction& txn = queue_[tail_];

    if (kind_ == Kind::Spi && phase_ == Phase::CommandBytes) {
        phase_ = Phase::Data;
        if (txn.tx.empty() && txn.rx.empty()) {
            complete(Result::Ok);   // команда без даних, як WREN у FRAM
            return;
        }
        if (start_spi_data(txn) != HAL_OK) {
            complete(Result::HardwareError);
        }
        return;
    }

    complete(Result::Ok);
}

void Dispatcher::on_error() noexcept
{
    if (!busy_) {
        return;
    }
    if (kind_ == Kind::I2c) {
        // Лікуємо не тут: розблокування смикає піни й спить мікросекунди,
        // а ми в перериванні. Позначаємо й повертаємося до цього в poll().
        needs_recovery_ = true;
    }
    complete(Result::HardwareError);
}

}  // namespace bus

// ---- слабкі колбеки HAL ----------------------------------------------------

namespace {

void forward_complete(const void* handle)
{
    if (auto* dispatcher = bus::Dispatcher::from_handle(handle); dispatcher != nullptr) {
        dispatcher->on_transfer_complete();
    }
}

void forward_error(const void* handle)
{
    if (auto* dispatcher = bus::Dispatcher::from_handle(handle); dispatcher != nullptr) {
        dispatcher->on_error();
    }
}

}  // namespace

extern "C" {

void HAL_I2C_MemRxCpltCallback(I2C_HandleTypeDef* hi2c) { forward_complete(hi2c); }
void HAL_I2C_MemTxCpltCallback(I2C_HandleTypeDef* hi2c) { forward_complete(hi2c); }
void HAL_I2C_MasterRxCpltCallback(I2C_HandleTypeDef* hi2c) { forward_complete(hi2c); }
void HAL_I2C_MasterTxCpltCallback(I2C_HandleTypeDef* hi2c) { forward_complete(hi2c); }
void HAL_I2C_ErrorCallback(I2C_HandleTypeDef* hi2c) { forward_error(hi2c); }
void HAL_I2C_AbortCpltCallback(I2C_HandleTypeDef* hi2c) { forward_error(hi2c); }

void HAL_SPI_TxCpltCallback(SPI_HandleTypeDef* hspi) { forward_complete(hspi); }
void HAL_SPI_RxCpltCallback(SPI_HandleTypeDef* hspi) { forward_complete(hspi); }
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef* hspi) { forward_complete(hspi); }
void HAL_SPI_ErrorCallback(SPI_HandleTypeDef* hspi) { forward_error(hspi); }

}  // extern "C"
